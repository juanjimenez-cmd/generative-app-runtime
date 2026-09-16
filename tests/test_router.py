from app.cerebras import choose_model_decision


def test_auto_prefers_low_cost_model_for_simple_prompt():
    decision = choose_model_decision("auto", "Crea una calculadora básica de dos números")
    assert decision.model == "gpt-oss-120b"


def test_auto_prefers_qwen_for_complex_edit():
    decision = choose_model_decision(
        "auto",
        "Convierte este dashboard interactivo en un editor con drag and drop y export CSV",
        is_edit=True,
        current_html_chars=18000,
    )
    assert decision.model == "qwen-3.8-27b"
    assert decision.score >= 3


def test_manual_override_wins():
    decision = choose_model_decision("gpt-oss-120b", "dashboard canvas editor", is_edit=True)
    assert decision.model == "gpt-oss-120b"
    assert "manual" in decision.reason.lower()
