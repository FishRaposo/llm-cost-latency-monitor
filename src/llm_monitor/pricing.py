"""Thin cost wrapper that delegates to ``shared_core.pricing``.

``shared_core.pricing`` is the single source of truth for per-model token
pricing across the workspace. This module is a backwards-compatible shim so
existing callers (the SDK, dashboard, tests) keep importing ``estimate_cost``
and ``PRICING_MAP`` from ``llm_monitor.pricing`` while the actual rates live in
``shared_core``. ``PRICING_MAP`` is derived from the shared registry and
expressed in the project's legacy per-1k-token shape for display purposes only.
"""

from shared_core.pricing import (
    MODEL_PRICING,
    calculate_cost,
    register_pricing,  # noqa: F401  (re-exported for convenience)
)


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate the USD cost of a single LLM query.

    Delegates the math to :func:`shared_core.pricing.calculate_cost`, the
    canonical pricing source. Rounded to 8 decimals to match historical output.
    """
    return round(calculate_cost(model, input_tokens, output_tokens), 8)


def _build_pricing_map() -> dict:
    """Project the shared per-1M registry into a per-1k display table."""
    out: dict = {}
    for model, entry in MODEL_PRICING.items():
        out[model] = {
            "input_cost_per_1k": round(entry.input_per_1m / 1000.0, 8),
            "output_cost_per_1k": round(entry.output_per_1m / 1000.0, 8),
        }
    return out


# Derived view of shared_core pricing in per-1k-token units (display only).
# NOT the source of truth — cost math always flows through calculate_cost.
PRICING_MAP = _build_pricing_map()
