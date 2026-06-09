import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from llm_monitor.sdk import MonitoredLLMClient
from llm_monitor.storage import InMemoryTelemetryStore


def main():
    store = InMemoryTelemetryStore()
    client = MonitoredLLMClient(store.log_request)

    print("--- Simulating Monitored LLM Requests ---")
    client.generate(
        "gpt-4",
        "Explain quantum computing in one paragraph.",
        "Quantum computing uses qubits...",
    )
    client.generate(
        "gpt-3.5-turbo",
        "What is the capital of France?",
        "The capital of France is Paris.",
    )

    aggregates = store.get_aggregates()
    print("Accumulated telemetry metrics:")
    print(f"Total Calls: {aggregates['total_calls']}")
    print(f"Total Estimated Cost: ${aggregates['total_cost']:.6f}")
    print(f"Average Latency: {aggregates['avg_latency']:.2f}ms")


if __name__ == "__main__":
    main()
