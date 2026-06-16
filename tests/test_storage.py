from llm_monitor.storage import InMemoryTelemetryStore


def _record(store, **overrides):
    base = {
        "model": "gpt-4",
        "prompt_length": 40,
        "input_tokens": 100,
        "output_tokens": 50,
        "cost_usd": 0.05,
        "latency_ms": 120.0,
        "prompt_version": "v1",
        "error": None,
    }
    base.update(overrides)
    store.log_request(base)


def test_log_and_get_aggregates():
    store = InMemoryTelemetryStore()
    _record(store, model="gpt-4", cost_usd=0.05, latency_ms=120.0)
    _record(store, model="gpt-3.5-turbo", cost_usd=0.01, latency_ms=80.0)

    agg = store.get_aggregates()
    assert agg["total_calls"] == 2
    assert agg["total_cost"] == 0.06
    assert agg["avg_latency"] == 100.0


def test_aggregates_empty():
    store = InMemoryTelemetryStore()
    agg = store.get_aggregates()
    assert agg["total_calls"] == 0
    assert agg["total_cost"] == 0.0
    assert agg["avg_latency"] == 0.0
    assert agg["error_rate"] == 0.0
    assert agg["by_model"] == {}


def test_aggregates_p50_p95_p99():
    store = InMemoryTelemetryStore()
    for i in range(100):
        _record(store, latency_ms=float(i + 1), cost_usd=0.01)

    agg = store.get_aggregates()
    assert agg["total_calls"] == 100
    assert agg["p50_latency_ms"] > 0
    assert agg["p95_latency_ms"] > agg["p50_latency_ms"]
    assert agg["p99_latency_ms"] >= agg["p95_latency_ms"]


def test_by_model_breakdown():
    store = InMemoryTelemetryStore()
    _record(store, model="gpt-4", input_tokens=10, output_tokens=20)
    _record(store, model="gpt-4", input_tokens=10, output_tokens=20)
    _record(store, model="claude-3-haiku", input_tokens=5, output_tokens=5)

    agg = store.get_aggregates()
    assert agg["by_model"]["gpt-4"]["calls"] == 2
    assert agg["by_model"]["gpt-4"]["total_tokens"] == 60
    assert agg["by_model"]["claude-3-haiku"]["calls"] == 1


def test_error_rate_tracking():
    store = InMemoryTelemetryStore()
    _record(store, error=None)
    _record(store, error="TimeoutError: boom")
    _record(store, error=None)
    _record(store, error=None)

    agg = store.get_aggregates()
    assert agg["error_rate"] == 0.25


def test_cost_by_prompt_version():
    store = InMemoryTelemetryStore()
    _record(store, prompt_version="v1", cost_usd=0.02)
    _record(store, prompt_version="v2", cost_usd=0.03)
    _record(store, prompt_version="v1", cost_usd=0.01)

    agg = store.get_aggregates()
    assert agg["cost_by_prompt_version"]["v1"] == 0.03
    assert agg["cost_by_prompt_version"]["v2"] == 0.03


def test_summary_passthrough():
    store = InMemoryTelemetryStore()
    _record(store)
    summary = store.summary()
    assert summary["total_requests"] == 1
    assert "p50_latency_ms" in summary
    assert "cost_by_model" in summary
