from llm_monitor.storage import InMemoryTelemetryStore


def test_log_and_get_aggregates():
    store = InMemoryTelemetryStore()
    store.log_request({
        "model": "gpt-4",
        "cost_usd": 0.05,
        "latency_ms": 120.0,
        "input_tokens": 100,
        "output_tokens": 50,
    })
    store.log_request({
        "model": "gpt-3.5-turbo",
        "cost_usd": 0.01,
        "latency_ms": 80.0,
        "input_tokens": 50,
        "output_tokens": 30,
    })

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


def test_aggregates_p95_p99():
    store = InMemoryTelemetryStore()
    for i in range(100):
        store.log_request({
            "model": "gpt-4",
            "cost_usd": 0.01,
            "latency_ms": float(i + 1),
            "input_tokens": 10,
            "output_tokens": 10,
        })

    agg = store.get_aggregates()
    assert agg["total_calls"] == 100
    assert agg["p95_latency_ms"] > 0
    assert agg["p99_latency_ms"] > 0
