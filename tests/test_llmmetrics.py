"""Tests that the store delegates aggregation to shared_core.llmmetrics."""

from shared_core.llmmetrics import LLMMetrics

from llm_monitor.storage import InMemoryTelemetryStore


def test_store_uses_llmmetrics_summary_shape():
    store = InMemoryTelemetryStore()
    store.log_request(
        {
            "model": "gpt-4o",
            "prompt_length": 20,
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.001,
            "latency_ms": 100.0,
            "prompt_version": "v1",
        }
    )
    summary = store.summary()
    reference_keys = set(LLMMetrics().summary().keys())
    assert reference_keys.issubset(set(summary.keys()))


def test_percentiles_match_llmmetrics():
    store = InMemoryTelemetryStore()
    ref = LLMMetrics()
    for latency in (10.0, 20.0, 30.0, 40.0, 50.0):
        store.log_request(
            {
                "model": "gpt-4o",
                "prompt_length": 4,
                "input_tokens": 1,
                "output_tokens": 1,
                "cost_usd": 0.0,
                "latency_ms": latency,
            }
        )
        ref.record(
            model="gpt-4o",
            prompt_tokens=1,
            completion_tokens=1,
            latency_ms=latency,
            cost_usd=0.0,
        )
    s = store.summary()
    r = ref.summary()
    assert s["p50_latency_ms"] == r["p50_latency_ms"]
    assert s["p95_latency_ms"] == r["p95_latency_ms"]
    assert s["p99_latency_ms"] == r["p99_latency_ms"]


def test_error_rate_and_versions():
    store = InMemoryTelemetryStore()
    payloads = [
        {"prompt_version": "v1", "error": None},
        {"prompt_version": "v1", "error": "boom"},
        {"prompt_version": "v2", "error": None},
    ]
    for p in payloads:
        store.log_request(
            {
                "model": "gpt-4o",
                "prompt_length": 4,
                "input_tokens": 2,
                "output_tokens": 2,
                "cost_usd": 0.001,
                "latency_ms": 50.0,
                **p,
            }
        )
    summary = store.summary()
    assert round(summary["error_rate"], 4) == round(1 / 3, 4)
    assert set(summary["cost_by_prompt_version"]) == {"v1", "v2"}
