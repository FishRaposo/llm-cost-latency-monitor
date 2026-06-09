PRICING_MAP = {
    "gpt-4": {"input_cost_per_1k": 0.03, "output_cost_per_1k": 0.06},
    "gpt-4o": {"input_cost_per_1k": 0.005, "output_cost_per_1k": 0.015},
    "gpt-4o-mini": {"input_cost_per_1k": 0.00015, "output_cost_per_1k": 0.0006},
    "gpt-3.5-turbo": {"input_cost_per_1k": 0.0015, "output_cost_per_1k": 0.002},
    "claude-3-opus": {"input_cost_per_1k": 0.015, "output_cost_per_1k": 0.075},
    "claude-3-5-sonnet": {"input_cost_per_1k": 0.003, "output_cost_per_1k": 0.015},
    "claude-3-haiku": {"input_cost_per_1k": 0.00025, "output_cost_per_1k": 0.00125},
}

FALLBACK_RATES = {"input_cost_per_1k": 0.005, "output_cost_per_1k": 0.015}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimates the dollar cost of an LLM query."""
    rates = PRICING_MAP.get(model, FALLBACK_RATES)
    input_cost = (input_tokens / 1000.0) * rates["input_cost_per_1k"]
    output_cost = (output_tokens / 1000.0) * rates["output_cost_per_1k"]
    return round(input_cost + output_cost, 8)
