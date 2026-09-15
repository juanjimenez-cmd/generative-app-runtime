from __future__ import annotations

import html
import re

from .config import MAX_GENERATED_HTML_BYTES

CSP = (
    "default-src 'none'; "
    "script-src 'unsafe-inline'; "
    "style-src 'unsafe-inline'; "
    "img-src data: blob:; "
    "font-src data:; "
    "media-src data: blob:; "
    "connect-src 'none'; "
    "object-src 'none'; "
    "frame-src 'none'; "
    "child-src 'none'; "
    "form-action 'none'; "
    "base-uri 'none';"
)

FORBIDDEN_TAGS = ("iframe", "object", "embed", "base", "link")


def extract_html(model_output: str) -> str:
    """Extract one HTML document from a model response and inject restrictive CSP."""
    if not model_output or not model_output.strip():
        raise ValueError("El modelo devolvió una respuesta vacía.")

    text = model_output.strip()

    fenced = re.search(r"```(?:html)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    start_candidates = [i for i in (text.lower().find("<!doctype"), text.lower().find("<html")) if i >= 0]
    if start_candidates:
        text = text[min(start_candidates):]

    lower = text.lower()
    end = lower.rfind("</html>")
    if end >= 0:
        text = text[: end + len("</html>")]

    if "<html" not in text.lower():
        text = f"<!doctype html><html><head><meta charset='utf-8'></head><body>{text}</body></html>"

    for tag in FORBIDDEN_TAGS:
        text = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}\s*>",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        text = re.sub(rf"<{tag}\b[^>]*/?>", "", text, flags=re.IGNORECASE | re.DOTALL)

    text = re.sub(
        r'<meta\b[^>]*http-equiv\s*=\s*([\'\"]).*?\1[^>]*>',
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    csp_meta = f'<meta http-equiv="Content-Security-Policy" content="{html.escape(CSP, quote=True)}">'
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">'

    head_match = re.search(r"<head\b[^>]*>", text, flags=re.IGNORECASE)
    if head_match:
        insertion = head_match.end()
        text = text[:insertion] + csp_meta + viewport + text[insertion:]
    else:
        html_match = re.search(r"<html\b[^>]*>", text, flags=re.IGNORECASE)
        insertion = html_match.end() if html_match else 0
        text = text[:insertion] + "<head>" + csp_meta + viewport + "</head>" + text[insertion:]

    encoded = text.encode("utf-8")
    if len(encoded) > MAX_GENERATED_HTML_BYTES:
        raise ValueError(f"La app generada supera el límite de {MAX_GENERATED_HTML_BYTES:,} bytes.")

    return text


def response_security_headers() -> dict[str, str]:
    return {
        "Content-Security-Policy": CSP,
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        "Cache-Control": "no-store",
    }
