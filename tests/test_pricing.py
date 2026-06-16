from unittest.mock import patch

from shared_core.pricing import calculate_cost

from llm_monitor.pricing import PRICING_MAP, estimate_cost


def test_estimate_cost_known_model():
    cost = estimate_cost("gpt-4", 1000, 1000)
    assert cost == 0.09  # $0.03 + $0.06


def test_estimate_cost_gpt_4o_mini():
    cost = estimate_cost("gpt-4o-mini", 1000, 1000)
    assert cost == 0.00075  # $0.00015 + $0.0006


def test_estimate_cost_claude_haiku():
    cost = estimate_cost("claude-3-haiku", 2000, 500)
    assert cost == 0.001125  # (2000/1M)*0.25 + (500/1M)*1.25


def test_estimate_cost_unknown_model():
    cost = estimate_cost("unknown-model", 1000, 1000)
    assert cost == 0.02  # shared_core fallback: 5.0/1M input + 15.0/1M output


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


def test_estimate_cost_matches_shared_core():
    """estimate_cost must equal shared_core.calculate_cost (rounded)."""
    for model in ("gpt-4", "gpt-4o", "claude-3-haiku", "mystery-model"):
        expected = round(calculate_cost(model, 1234, 567), 8)
        assert estimate_cost(model, 1234, 567) == expected


def test_estimate_cost_delegates_to_shared_core():
    """The local wrapper must call shared_core.pricing.calculate_cost."""
    with patch("llm_monitor.pricing.calculate_cost", return_value=0.42) as mock_calc:
        result = estimate_cost("gpt-4", 10, 20)
    mock_calc.assert_called_once_with("gpt-4", 10, 20)
    assert result == 0.42


def test_pricing_map_derived_from_shared_registry():
    """PRICING_MAP per-1k rates derive from shared_core per-1M registry."""
    from shared_core.pricing import MODEL_PRICING

    entry = MODEL_PRICING["gpt-4"]
    assert PRICING_MAP["gpt-4"]["input_cost_per_1k"] == round(
        entry.input_per_1m / 1000.0, 8
    )
    assert PRICING_MAP["gpt-4"]["output_cost_per_1k"] == round(
        entry.output_per_1m / 1000.0, 8
    )
