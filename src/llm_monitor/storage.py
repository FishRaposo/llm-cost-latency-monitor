"""In-memory telemetry store backed by ``shared_core.llmmetrics.LLMMetrics``.

This is the offline-first default store used by tests and the demo. It keeps a
raw ``logs`` list (for callers that iterate records) and delegates all
aggregation — totals, per-model, per-prompt-version, p50/p95/p99 latency, and
error rate — to ``shared_core.llmmetrics.LLMMetrics`` so the math lives in one
place. The DB-backed store (``storage_db.DatabaseTelemetryStore``) exposes the
same interface for production persistence.
"""

from typing import Any, Dict, List

from shared_core.llmmetrics import LLMMetrics


class InMemoryTelemetryStore:
    """Persists historical LLM query metrics for aggregate analytics."""

    def __init__(self) -> None:
        self.logs: List[Dict[str, Any]] = []
        self._metrics = LLMMetrics()

    def log_request(self, telemetry_data: dict) -> None:
        """Record one telemetry payload (as produced by the SDK or /log)."""
        self.logs.append(telemetry_data)
        self._metrics.record(
            model=telemetry_data.get("model", "unknown"),
            prompt_tokens=int(telemetry_data.get("input_tokens", 0)),
            completion_tokens=int(telemetry_data.get("output_tokens", 0)),
            latency_ms=float(telemetry_data.get("latency_ms", 0.0)),
            prompt_version=telemetry_data.get("prompt_version"),
            error=telemetry_data.get("error"),
            cost_usd=telemetry_data.get("cost_usd"),
        )

    def summary(self) -> Dict[str, Any]:
        """Return the full ``LLMMetrics`` summary dictionary."""
        return self._metrics.summary()

    def get_aggregates(self) -> Dict[str, Any]:
        """Return aggregate metrics in the project's stable response shape.

        Combines the canonical ``LLMMetrics.summary()`` (totals, percentiles,
        error rate, per-model and per-prompt-version cost) with the legacy
        ``total_calls`` / ``total_cost`` / ``avg_latency`` keys and a richer
        ``by_model`` breakdown (calls + tokens) that dashboards depend on.
        """
        summary = self._metrics.summary()

        by_model: Dict[str, Any] = {}
        for entry in self.logs:
            model = entry.get("model", "unknown")
            bucket = by_model.setdefault(
                model, {"calls": 0, "total_cost": 0.0, "total_tokens": 0}
            )
            bucket["calls"] += 1
            bucket["total_cost"] = round(
                bucket["total_cost"] + float(entry.get("cost_usd", 0.0)), 8
            )
            bucket["total_tokens"] += int(entry.get("input_tokens", 0)) + int(
                entry.get("output_tokens", 0)
            )

        return {
            "total_calls": summary["total_requests"],
            "total_cost": summary["estimated_cost"],
            "total_tokens": summary["total_tokens"],
            "avg_latency": summary["average_latency_ms"],
            "p50_latency_ms": summary["p50_latency_ms"],
            "p95_latency_ms": summary["p95_latency_ms"],
            "p99_latency_ms": summary["p99_latency_ms"],
            "error_rate": summary["error_rate"],
            "by_model": by_model,
            "cost_by_model": summary["cost_by_model"],
            "cost_by_prompt_version": summary["cost_by_prompt_version"],
        }
