from app.security import CSP, extract_html


def test_extracts_fenced_html_and_injects_csp():
    raw = """```html\n<!doctype html><html><head><title>X</title></head><body><script>console.log(1)</script></body></html>\n```"""
    out = extract_html(raw)
    assert "Content-Security-Policy" in out
    assert "console.log(1)" in out
    assert "```" not in out


def test_removes_iframe_and_external_link_tag():
    raw = "<html><head><link rel='stylesheet' href='https://x.test/x.css'></head><body><iframe src='https://x.test'></iframe><p>ok</p></body></html>"
    out = extract_html(raw).lower()
    assert "<iframe" not in out
    assert "<link" not in out
    assert "<p>ok</p>" in out
