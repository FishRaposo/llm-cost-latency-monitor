class InMemoryTelemetryStore:
    """Persists historical LLM query metrics for aggregate analytics."""

    def __init__(self):
        self.logs = []

    def log_request(self, telemetry_data: dict):
        self.logs.append(telemetry_data)

    def get_aggregates(self):
        if not self.logs:
            return {
                "total_calls": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
            }
        total_cost = round(sum(x["cost_usd"] for x in self.logs), 8)
        avg_latency = round(
            sum(x["latency_ms"] for x in self.logs) / len(self.logs), 2
        )
        latencies = sorted(x["latency_ms"] for x in self.logs)
        n = len(latencies)
        p95 = latencies[int(n * 0.95)]
        p99 = latencies[min(int(n * 0.99), n - 1)]
        return {
            "total_calls": len(self.logs),
            "total_cost": total_cost,
            "avg_latency": avg_latency,
            "p95_latency_ms": p95,
            "p99_latency_ms": p99,
        }
