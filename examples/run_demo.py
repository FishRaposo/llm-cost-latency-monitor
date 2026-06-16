"""End-to-end demo of the LLM Cost & Latency Monitor (offline, no API keys).

Simulates a batch of monitored LLM requests across models and prompt versions,
then prints aggregate telemetry, a daily report, and budget-alert evaluation —
exercising the SDK, the LLMMetrics-backed store, the report generator, and the
budget engine without any network or database.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from llm_monitor.budgets import evaluate_budget  # noqa: E402
from llm_monitor.reports import build_daily_report, report_to_csv  # noqa: E402
from llm_monitor.sdk import MonitoredLLMClient  # noqa: E402
from llm_monitor.storage import InMemoryTelemetryStore  # noqa: E402


def main() -> int:
    store = InMemoryTelemetryStore()
    client = MonitoredLLMClient(store.log_request)

    print("--- Simulating Monitored LLM Requests (offline / mocked) ---")
    samples = [
        (
            "gpt-4",
            "Explain quantum computing in one paragraph.",
            "Quantum computing uses qubits...",
            "v1",
        ),
        (
            "gpt-3.5-turbo",
            "What is the capital of France?",
            "The capital of France is Paris.",
            "v1",
        ),
        (
            "gpt-4o-mini",
            "Summarize the plot of Hamlet.",
            "A prince seeks revenge...",
            "v2",
        ),
        (
            "claude-3-haiku",
            "Write a haiku about latency.",
            "Tokens flow like streams...",
            "v2",
        ),
        ("gpt-4o", "Translate 'hello' to French.", "Bonjour.", "v1"),
    ]
    for model, prompt, response, version in samples:
        result = client.generate(
            model, prompt, mocked_response=response, prompt_version=version
        )
        t = result["telemetry"]
        print(
            f"  {model:<16} v={version}  "
            f"cost=${t['cost_usd']:.6f}  latency={t['latency_ms']:.1f}ms"
        )

    print("\n--- Aggregate Telemetry ---")
    agg = store.get_aggregates()
    print(f"Total Calls:           {agg['total_calls']}")
    print(f"Total Estimated Cost:  ${agg['total_cost']:.6f}")
    print(f"Average Latency:       {agg['avg_latency']:.2f}ms")
    print(f"P95 Latency:           {agg['p95_latency_ms']:.2f}ms")
    print(f"P99 Latency:           {agg['p99_latency_ms']:.2f}ms")
    print(f"Error Rate:            {agg['error_rate']:.2%}")
    print(f"Cost by prompt version: {agg['cost_by_prompt_version']}")

    print("\n--- Daily Report (JSON totals) ---")
    report = build_daily_report(store)
    print(json.dumps(report["totals"], indent=2))
    print("\n--- Daily Report (CSV) ---")
    print(report_to_csv(report).strip())

    print("\n--- Budget Alerts (threshold $0.0001 to force a flag) ---")
    alerts = evaluate_budget(store, threshold_usd=0.0001)
    print(f"Flagged: {alerts['flagged']}  Alerts: {alerts['total_alerts']}")
    for alert in alerts["alerts"]:
        print(f"  [{alert['severity']}] {alert['message']}")

    print("\nDemo complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
