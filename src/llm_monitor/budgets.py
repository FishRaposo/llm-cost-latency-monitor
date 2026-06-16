"""Budget alerting.

Evaluates a store's aggregate spend against a USD threshold and flags overruns,
both in total and per-model. Returns structured alerts consumable by the
``/budgets/alerts`` endpoint or a dashboard. Pure-Python and offline-friendly.
"""

from typing import Any, Dict, List, Optional


def evaluate_budget(
    store,
    threshold_usd: float,
    per_model_threshold_usd: Optional[float] = None,
) -> Dict[str, Any]:
    """Compare spend against a budget and return alerts.

    Args:
        store: telemetry store exposing ``get_aggregates()``.
        threshold_usd: total-spend USD budget.
        per_model_threshold_usd: optional per-model USD budget; when set, each
            model exceeding it produces its own alert.

    Returns:
        ``{"threshold_usd", "total_cost", "flagged", "alerts": [...]}``.
    """
    aggregates = store.get_aggregates()
    total_cost = float(aggregates.get("total_cost", 0.0))
    alerts: List[Dict[str, Any]] = []

    flagged = total_cost > threshold_usd
    if flagged:
        alerts.append(
            {
                "type": "budget_overrun",
                "scope": "total",
                "severity": "critical",
                "message": (
                    f"Total spend ${total_cost:.6f} exceeds budget "
                    f"${threshold_usd:.6f}."
                ),
                "current_value": round(total_cost, 6),
                "threshold": threshold_usd,
            }
        )

    if per_model_threshold_usd is not None:
        for model, data in sorted(aggregates.get("by_model", {}).items()):
            model_cost = float(data.get("total_cost", 0.0))
            if model_cost > per_model_threshold_usd:
                alerts.append(
                    {
                        "type": "budget_overrun",
                        "scope": "model",
                        "model": model,
                        "severity": "warning",
                        "message": (
                            f"Model '{model}' spend ${model_cost:.6f} exceeds "
                            f"per-model budget ${per_model_threshold_usd:.6f}."
                        ),
                        "current_value": round(model_cost, 6),
                        "threshold": per_model_threshold_usd,
                    }
                )

    return {
        "threshold_usd": threshold_usd,
        "per_model_threshold_usd": per_model_threshold_usd,
        "total_cost": round(total_cost, 6),
        "flagged": flagged or any(a["scope"] == "model" for a in alerts),
        "alerts": alerts,
        "total_alerts": len(alerts),
    }
