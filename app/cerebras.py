from __future__ import annotations

from dataclasses import dataclass

import httpx

from .config import CEREBRAS_API_BASE, CEREBRAS_API_KEY, DEFAULT_MODEL, MODEL_PRICING, SUPPORTED_MODELS


@dataclass
class GenerationResult:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


def choose_model(requested: str | None, prompt: str) -> str:
    if requested and requested != "auto":
        if requested not in SUPPORTED_MODELS:
            raise ValueError(f"Modelo no soportado: {requested}")
        return requested
    return DEFAULT_MODEL if DEFAULT_MODEL in SUPPORTED_MODELS else "qwen-3.8-27b"


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
    return round(input_tokens * rates["input"] + output_tokens * rates["output"], 6)


async def generate_app(prompt: str, requested_model: str | None = None) -> GenerationResult:
    if not CEREBRAS_API_KEY:
        raise RuntimeError("Falta CEREBRAS_API_KEY. Copia .env.example a .env y agrega tu clave.")

    model = choose_model(requested_model, prompt)
    system_prompt = """You are an expert frontend engineer generating disposable, sandboxed micro-apps.
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

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt.strip()},
        ],
        "temperature": 0.2,
        "max_completion_tokens": 20000,
        "stream": False,
    }

    headers = {"Authorization": f"Bearer {CEREBRAS_API_KEY}", "Content-Type": "application/json"}
    timeout = httpx.Timeout(120.0, connect=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f"{CEREBRAS_API_BASE}/chat/completions", json=payload, headers=headers)
        if response.status_code >= 400:
            detail = response.text[:800]
            raise RuntimeError(f"Cerebras API respondió {response.status_code}: {detail}")
        data = response.json()

    content = data["choices"][0]["message"].get("content") or ""
    usage = data.get("usage") or {}
    input_tokens = int(usage.get("prompt_tokens") or 0)
    output_tokens = int(usage.get("completion_tokens") or 0)

    return GenerationResult(
        content=content,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimate_cost(model, input_tokens, output_tokens),
    )
