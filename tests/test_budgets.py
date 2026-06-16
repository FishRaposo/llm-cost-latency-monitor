"""Tests for USD budget-threshold alerting."""

from llm_monitor.budgets import evaluate_budget
from llm_monitor.storage import InMemoryTelemetryStore


def _seed(store, model="gpt-4", cost=0.01, n=1):
    for _ in range(n):
        store.log_request(
            {
                "model": model,
                "prompt_length": 10,
                "input_tokens": 10,
                "output_tokens": 5,
                "cost_usd": cost,
                "latency_ms": 50.0,
            }
        )


def test_no_alert_under_threshold():
    store = InMemoryTelemetryStore()
    _seed(store, cost=0.01)
    result = evaluate_budget(store, threshold_usd=1.0)
    assert result["flagged"] is False
    assert result["alerts"] == []
    assert result["total_alerts"] == 0


def test_alert_over_threshold():
    store = InMemoryTelemetryStore()
    _seed(store, cost=0.5, n=3)  # total 1.5
    result = evaluate_budget(store, threshold_usd=1.0)
    assert result["flagged"] is True
    assert result["total_alerts"] == 1
    assert result["alerts"][0]["type"] == "budget_overrun"
    assert result["alerts"][0]["severity"] == "critical"
    assert result["total_cost"] == 1.5


def test_per_model_alert():
    store = InMemoryTelemetryStore()
    _seed(store, model="gpt-4", cost=0.6)
    _seed(store, model="gpt-3.5-turbo", cost=0.05)
    result = evaluate_budget(store, threshold_usd=100.0, per_model_threshold_usd=0.5)
    # Total is under budget, but gpt-4 exceeds the per-model threshold.
    assert result["flagged"] is True
    model_alerts = [a for a in result["alerts"] if a["scope"] == "model"]
    assert len(model_alerts) == 1
    assert model_alerts[0]["model"] == "gpt-4"


def test_empty_store_no_alert():
    store = InMemoryTelemetryStore()
    result = evaluate_budget(store, threshold_usd=0.0)
    assert result["flagged"] is False
    assert result["total_cost"] == 0.0


def test_threshold_boundary_not_flagged():
    store = InMemoryTelemetryStore()
    _seed(store, cost=1.0)
    # Exactly at threshold is not over (strict greater-than).
    result = evaluate_budget(store, threshold_usd=1.0)
    assert result["flagged"] is False
