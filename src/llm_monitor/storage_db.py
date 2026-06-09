
from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import LLMCall


class DatabaseTelemetryStore:
    """PostgreSQL-backed telemetry persistence."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def log_request(self, telemetry_data: dict):
        session: Session = next(self.session_factory())
        try:
            call = LLMCall(
                model=telemetry_data.get("model", "unknown"),
                prompt_length=telemetry_data.get("prompt_length", 0),
                input_tokens=telemetry_data.get("input_tokens", 0),
                output_tokens=telemetry_data.get("output_tokens", 0),
                cost_usd=telemetry_data.get("cost_usd", 0.0),
                latency_ms=telemetry_data.get("latency_ms", 0.0),
            )
            session.add(call)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to persist telemetry: {e}")
            raise
        finally:
            session.close()

    def get_aggregates(self) -> dict:
        session: Session = next(self.session_factory())
        try:
            total_calls = session.query(func.count(LLMCall.id)).scalar() or 0
            total_cost = session.query(func.sum(LLMCall.cost_usd)).scalar() or 0.0
            avg_latency = session.query(func.avg(LLMCall.latency_ms)).scalar() or 0.0

            by_model_rows = (
                session.query(
                    LLMCall.model,
                    func.count(LLMCall.id),
                    func.sum(LLMCall.cost_usd),
                    func.sum(LLMCall.input_tokens + LLMCall.output_tokens),
                )
                .group_by(LLMCall.model)
                .all()
            )
            by_model = {}
            for model, calls, cost, tokens in by_model_rows:
                by_model[model] = {
                    "calls": calls,
                    "total_cost": cost or 0.0,
                    "total_tokens": tokens or 0,
                }

            latencies = [
                r[0]
                for r in session.query(LLMCall.latency_ms)
                .order_by(LLMCall.latency_ms)
                .all()
            ]
            p95 = 0.0
            p99 = 0.0
            if latencies:
                n = len(latencies)
                p95 = latencies[int(n * 0.95)]
                p99 = latencies[min(int(n * 0.99), n - 1)]

            return {
                "total_calls": total_calls,
                "total_cost": round(total_cost, 6),
                "avg_latency": round(avg_latency, 2),
                "p95_latency_ms": p95,
                "p99_latency_ms": p99,
                "by_model": by_model,
            }
        finally:
            session.close()
