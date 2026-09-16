from __future__ import annotations

import json
from dataclasses import dataclass
from typing import AsyncIterator

import httpx

from .config import CEREBRAS_API_BASE, CEREBRAS_API_KEY, MODEL_PRICING, SUPPORTED_MODELS


SYSTEM_PROMPT = """You are an expert frontend engineer generating disposable, sandboxed micro-apps.
Return ONLY one complete HTML document. Requirements:
- Single-file HTML with inline CSS and JavaScript.
- No Markdown fences or commentary.
- No external URLs, CDNs, remote fonts, external images, fetch/XHR/WebSocket, iframes, object/embed, or form submissions.
- The app must work offline in a restrictive browser iframe.
- Use only browser-native APIs. FileReader is allowed for user-selected local CSV/text files.
- Do not attempt to access parent/top/opener, cookies, localStorage, service workers, clipboard, camera, microphone, geolocation, shell, Python, or the host filesystem.
- Make the UI polished, responsive and self-explanatory.
- Prefer deterministic calculations and graceful error messages.
"""

COMPLEXITY_TERMS = {
    "dashboard", "canvas", "editor", "paint", "drawing", "drag", "drop",
    "chart", "graph", "grafico", "gráfico", "spreadsheet", "excel", "csv",
    "timeline", "kanban", "multi-step", "wizard", "amortization", "amortización",
    "simulator", "simulador", "interactive", "interactivo", "export", "import",
}


@dataclass(frozen=True)
class RoutingDecision:
    model: str
    reason: str
    score: int


@dataclass
class GenerationResult:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    routing_reason: str


def choose_model_decision(
    requested: str | None,
    prompt: str,
    *,
    is_edit: bool = False,
    current_html_chars: int = 0,
) -> RoutingDecision:
    if requested and requested != "auto":
        if requested not in SUPPORTED_MODELS:
            raise ValueError(f"Modelo no soportado: {requested}")
        return RoutingDecision(requested, "Selección manual del usuario.", 0)

    normalized = prompt.lower()
    score = 0
    reasons: list[str] = []

    if is_edit:
        score += 3
        reasons.append("edición de una app existente")
    if current_html_chars > 12_000:
        score += 2
        reasons.append("HTML base extenso")
    if len(prompt) > 4_000:
        score += 3
        reasons.append("prompt muy extenso")
    elif len(prompt) > 1_200:
        score += 2
        reasons.append("prompt extenso")

    matches = sum(1 for term in COMPLEXITY_TERMS if term in normalized)
    if matches:
        added = min(4, matches)
        score += added
        reasons.append(f"{matches} señal(es) de UI/lógica compleja")

    if score >= 3:
        model = "qwen-3.8-27b"
        reason = "Qwen seleccionado por " + ", ".join(reasons or ["complejidad estimada"])
    else:
        model = "gpt-oss-120b"
        reason = "GPT-OSS seleccionado para una tarea corta/sencilla y priorizar costo."

    return RoutingDecision(model, reason, score)


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
    return round(input_tokens * rates["input"] + output_tokens * rates["output"], 6)


def rough_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def build_messages(prompt: str, current_html: str | None = None) -> list[dict[str, str]]:
    if current_html:
        user_content = (
            "Revise the existing app according to the change request. Return the COMPLETE revised HTML, "
            "not a patch or explanation.\n\n"
            f"CHANGE REQUEST:\n{prompt.strip()}\n\n"
            f"CURRENT APP HTML:\n{current_html}"
        )
    else:
        user_content = prompt.strip()
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def _payload(model: str, messages: list[dict[str, str]], *, stream: bool) -> dict:
    return {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_completion_tokens": 20_000,
        "stream": stream,
    }


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {CEREBRAS_API_KEY}", "Content-Type": "application/json"}


def _check_key() -> None:
    if not CEREBRAS_API_KEY:
        raise RuntimeError("Falta CEREBRAS_API_KEY. Copia .env.example a .env y agrega tu clave.")


async def generate_app(
    prompt: str,
    requested_model: str | None = None,
    *,
    current_html: str | None = None,
) -> GenerationResult:
    _check_key()
    decision = choose_model_decision(
        requested_model,
        prompt,
        is_edit=current_html is not None,
        current_html_chars=len(current_html or ""),
    )
    messages = build_messages(prompt, current_html)
    timeout = httpx.Timeout(120.0, connect=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{CEREBRAS_API_BASE}/chat/completions",
            json=_payload(decision.model, messages, stream=False),
            headers=_headers(),
        )
        if response.status_code >= 400:
            detail = response.text[:800]
            raise RuntimeError(f"Cerebras API respondió {response.status_code}: {detail}")
        data = response.json()

    content = data["choices"][0]["message"].get("content") or ""
    usage = data.get("usage") or {}
    input_tokens = int(usage.get("prompt_tokens") or rough_tokens("".join(m["content"] for m in messages)))
    output_tokens = int(usage.get("completion_tokens") or rough_tokens(content))

    return GenerationResult(
        content=content,
        model=decision.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimate_cost(decision.model, input_tokens, output_tokens),
        routing_reason=decision.reason,
    )


async def stream_app(
    prompt: str,
    requested_model: str | None = None,
    *,
    current_html: str | None = None,
) -> AsyncIterator[dict]:
    """Yield model deltas and a final usage/routing event from Cerebras streaming."""
    _check_key()
    decision = choose_model_decision(
        requested_model,
        prompt,
        is_edit=current_html is not None,
        current_html_chars=len(current_html or ""),
    )
    messages = build_messages(prompt, current_html)
    input_tokens = rough_tokens("".join(m["content"] for m in messages))
    output_parts: list[str] = []
    reported_input = 0
    reported_output = 0

    yield {"type": "routing", "model": decision.model, "reason": decision.reason, "score": decision.score}

    timeout = httpx.Timeout(180.0, connect=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream(
            "POST",
            f"{CEREBRAS_API_BASE}/chat/completions",
            json=_payload(decision.model, messages, stream=True),
            headers=_headers(),
        ) as response:
            if response.status_code >= 400:
                body = (await response.aread()).decode("utf-8", errors="replace")[:800]
                raise RuntimeError(f"Cerebras API respondió {response.status_code}: {body}")

            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                if raw == "[DONE]":
                    break
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                usage = data.get("usage") or {}
                reported_input = int(usage.get("prompt_tokens") or reported_input)
                reported_output = int(usage.get("completion_tokens") or reported_output)

                choices = data.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content") or ""
                if content:
                    output_parts.append(content)
                    yield {"type": "delta", "content": content}

    content = "".join(output_parts)
    input_tokens = reported_input or input_tokens
    output_tokens = reported_output or rough_tokens(content)
    yield {
        "type": "done",
        "content": content,
        "model": decision.model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimate_cost(decision.model, input_tokens, output_tokens),
        "routing_reason": decision.reason,
    }
