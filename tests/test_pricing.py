from llm_monitor.pricing import PRICING_MAP, estimate_cost


def test_estimate_cost_known_model():
    cost = estimate_cost("gpt-4", 1000, 1000)
    assert cost == 0.09  # $0.03 + $0.06


def test_estimate_cost_gpt_4o_mini():
    cost = estimate_cost("gpt-4o-mini", 1000, 1000)
    assert cost == 0.00075  # $0.00015 + $0.0006


def test_estimate_cost_claude_haiku():
    cost = estimate_cost("claude-3-haiku", 2000, 500)
    assert cost == 0.001125  # (2000/1000)*0.00025 + (500/1000)*0.00125


def test_estimate_cost_unknown_model():
    cost = estimate_cost("unknown-model", 1000, 1000)
    assert cost == 0.02  # fallback: $0.005/1k input + $0.015/1k output


def test_estimate_cost_zero_tokens():
    cost = estimate_cost("gpt-4", 0, 0)
    assert cost == 0.0


def test_pricing_map_has_models():
    assert "gpt-4" in PRICING_MAP
    assert "gpt-4o" in PRICING_MAP
    assert "gpt-4o-mini" in PRICING_MAP
    assert "claude-3-opus" in PRICING_MAP
    assert "claude-3-5-sonnet" in PRICING_MAP
    assert "claude-3-haiku" in PRICING_MAP
