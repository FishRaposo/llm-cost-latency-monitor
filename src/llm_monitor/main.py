"""FastAPI application for the LLM Cost & Latency Monitor.

Offline-first: boots and serves with no database (in-memory telemetry store) and
no API keys. When a database is reachable, telemetry persists to PostgreSQL via
the ``db_available`` probe. Wires shared_core request logging + Prometheus
metrics middleware, and exposes the telemetry, reporting, and budget endpoints a
dashboard would consume.
"""

import time as time_module
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from shared_core.errors import BaseApplicationError, application_error_handler
from shared_core.health import check_health
from shared_core.logging import RequestLoggingMiddleware, setup_logging
from shared_core.metrics import MetricsMiddleware, MetricsRegistry, metrics_endpoint
from shared_core.redis import RedisManager

from . import db as db_module
from .budgets import evaluate_budget
from .config import AppConfig
from .dashboard import generate_html_dashboard, generate_text_report
from .reports import build_daily_report, report_to_csv
from .storage import InMemoryTelemetryStore

config = AppConfig()
setup_logging(level=config.LOG_LEVEL, service_name=config.APP_NAME)

# In-memory fallback store; replaced by a DB-backed store on startup if the
# database is reachable. Tests patch this directly.
store: object = InMemoryTelemetryStore()

# ``db_manager`` is built lazily so importing the app never requires a DB driver.
# Tests patch this attribute directly with a mock manager.
db_manager: object = None
redis_manager = RedisManager(config.REDIS_URL)
metrics_registry = MetricsRegistry(config.APP_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Probe the database on startup and select the persistence backend."""
    global store, db_manager
    db_module.check_db()
    if db_module.db_available:
        db_manager = db_module.db_manager
        store = db_module.build_store()
    yield


app = FastAPI(
    title=config.APP_NAME,
    version="1.0.0",
    description=(
        "Self-hosted LLM observability: token usage, cost, latency, prompt "
        "versions, error rates, daily reports, and budget alerts."
    ),
    lifespan=lifespan,
)

app.add_exception_handler(BaseApplicationError, application_error_handler)
app.add_middleware(MetricsMiddleware, registry=metrics_registry)
app.add_middleware(RequestLoggingMiddleware)


class TelemetryPayload(BaseModel):
    """One LLM-call telemetry record accepted by ``POST /log``."""

    model: str
    prompt_length: int = Field(default=0, ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)
    latency_ms: float = Field(ge=0.0)
    prompt_version: Optional[str] = Field(default=None)
    error: Optional[str] = Field(default=None)
    timestamp: float = Field(default_factory=time_module.time)


@app.post("/log")
def log_telemetry(data: TelemetryPayload):
    """Ingest a telemetry record into the active store."""
    store.log_request(data.model_dump())
    return {"status": "logged"}


@app.get("/metrics")
def get_metrics():
    """Return the aggregate JSON metrics summary."""
    return store.get_aggregates()


@app.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Expose HTTP request metrics in Prometheus text format."""
    handler = metrics_endpoint(metrics_registry)
    return await handler()


@app.get("/reports/daily")
def daily_report(
    day: Optional[str] = Query(
        default=None, description="UTC day filter as YYYY-MM-DD"
    ),
    format: str = Query(default="json", description="json or csv"),
):
    """Generate a daily cost/latency report (JSON or CSV)."""
    report = build_daily_report(store, day=day)
    if format == "csv":
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(report_to_csv(report), media_type="text/csv")
    return report


@app.get("/budgets/alerts")
def budget_alerts(
    threshold_usd: Optional[float] = Query(
        default=None, ge=0.0, description="Total USD budget; overrides config"
    ),
    per_model_threshold_usd: Optional[float] = Query(
        default=None, ge=0.0, description="Per-model USD budget"
    ),
):
    """Evaluate spend against the configured (or supplied) budget threshold."""
    total_budget = (
        config.BUDGET_THRESHOLD_USD if threshold_usd is None else threshold_usd
    )
    per_model_budget = (
        config.BUDGET_PER_MODEL_THRESHOLD_USD
        if per_model_threshold_usd is None
        else per_model_threshold_usd
    )
    return evaluate_budget(
        store,
        threshold_usd=total_budget,
        per_model_threshold_usd=per_model_budget,
    )


@app.get("/health")
def health_check():
    """Service health, probing database and Redis connectivity.

    When no database manager is available (offline mode), reports the database
    as offline and degraded rather than failing — the service still serves
    metrics from the in-memory store.
    """
    if db_manager is None:
        redis_healthy = False
        try:
            redis_healthy = redis_manager.ping()
        except Exception:
            redis_healthy = False
        return {
            "status": "degraded",
            "service": config.APP_NAME,
            "dependencies": {
                "database": "offline",
                "redis": "online" if redis_healthy else "offline",
            },
        }
    return check_health(db_manager, redis_manager, config.APP_NAME)


@app.get("/dashboard")
def dashboard(format: str = "json"):
    """Return a dashboard view of telemetry data (json/text/html)."""
    if format == "text":
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(generate_text_report(store))
    if format == "html":
        from fastapi.responses import HTMLResponse

        return HTMLResponse(generate_html_dashboard(store))
    return store.get_aggregates()


def main():
    """Run the development server."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
