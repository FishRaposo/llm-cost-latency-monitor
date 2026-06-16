"""PostgreSQL-backed telemetry persistence.

Mirrors the interface of ``storage.InMemoryTelemetryStore`` so the API and
reports work against either store. Aggregation is delegated to
``shared_core.llmmetrics.LLMMetrics`` (the same engine the in-memory store uses)
by loading persisted rows into a fresh metrics object — keeping percentile and
error-rate math identical across both backends.
"""

from contextlib import closing, contextmanager
from typing import Any, Dict, Iterator, List

from loguru import logger
from shared_core.llmmetrics import LLMMetrics
from sqlalchemy.orm import Session

from .models import LLMCall


class DatabaseTelemetryStore:
    """SQLAlchemy-backed telemetry persistence using a session factory."""

    def __init__(self, session_factory):
        # session_factory() yields a Session (FastAPI/DatabaseManager generator).
        self.session_factory = session_factory

    @contextmanager
    def _session(self) -> Iterator[Session]:
        # Drive the factory generator deterministically so its finally/close
        # runs when the block exits, rather than being left to the GC.
        with closing(self.session_factory()) as gen:
            yield next(gen)

    def log_request(self, telemetry_data: dict) -> None:
        """Persist one telemetry payload as an ``LLMCall`` row."""
        with self._session() as session:
            try:
                call = LLMCall(
                    model=telemetry_data.get("model", "unknown"),
                    prompt_length=int(telemetry_data.get("prompt_length", 0)),
                    input_tokens=int(telemetry_data.get("input_tokens", 0)),
                    output_tokens=int(telemetry_data.get("output_tokens", 0)),
                    cost_usd=float(telemetry_data.get("cost_usd", 0.0)),
                    latency_ms=float(telemetry_data.get("latency_ms", 0.0)),
                    prompt_version=telemetry_data.get("prompt_version"),
                    error=(
                        str(telemetry_data["error"])[:500]
                        if telemetry_data.get("error")
                        else None
                    ),
                )
                session.add(call)
                session.commit()
            except Exception as exc:
                session.rollback()
                logger.error(f"Failed to persist telemetry: {exc}")
                raise
            finally:
                session.close()

    def _load_metrics(self) -> tuple[LLMMetrics, List[LLMCall]]:
        """Load all rows into an LLMMetrics object for aggregation."""
        with self._session() as session:
            try:
                rows = session.query(LLMCall).all()
            finally:
                session.close()

        metrics = LLMMetrics()
        for row in rows:
            metrics.record(
                model=row.model,
                prompt_tokens=row.input_tokens,
                completion_tokens=row.output_tokens,
                latency_ms=row.latency_ms,
                prompt_version=row.prompt_version,
                error=row.error,
                cost_usd=row.cost_usd,
            )
        return metrics, rows

    def summary(self) -> Dict[str, Any]:
        """Return the full ``LLMMetrics`` summary dictionary."""
        metrics, _ = self._load_metrics()
        return metrics.summary()

    def get_aggregates(self) -> Dict[str, Any]:
        """Return aggregate metrics in the project's stable response shape."""
        metrics, rows = self._load_metrics()
        summary = metrics.summary()

        by_model: Dict[str, Any] = {}
        for row in rows:
            bucket = by_model.setdefault(
                row.model, {"calls": 0, "total_cost": 0.0, "total_tokens": 0}
            )
            bucket["calls"] += 1
            bucket["total_cost"] = round(bucket["total_cost"] + row.cost_usd, 8)
            bucket["total_tokens"] += row.input_tokens + row.output_tokens

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

    @property
    def logs(self) -> List[Dict[str, Any]]:
        """Return persisted rows as telemetry dicts (dashboard/report compat)."""
        _, rows = self._load_metrics()
        return [
            {
                "model": r.model,
                "prompt_length": r.prompt_length,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "cost_usd": r.cost_usd,
                "latency_ms": r.latency_ms,
                "prompt_version": r.prompt_version,
                "error": r.error,
            }
            for r in rows
        ]
