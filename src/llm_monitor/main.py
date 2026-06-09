import time as time_module

from fastapi import FastAPI
from pydantic import BaseModel, Field
from shared_core.database import DatabaseManager
from shared_core.errors import BaseApplicationError, application_error_handler
from shared_core.health import check_health
from shared_core.logging import setup_logging
from shared_core.redis import RedisManager

from .config import AppConfig
from .dashboard import generate_text_report, generate_html_dashboard
from .middleware import telemetry_middleware
from .storage import InMemoryTelemetryStore

config = AppConfig()
setup_logging(level=config.LOG_LEVEL, service_name=config.APP_NAME)

app = FastAPI(title=config.APP_NAME, version="0.1.0")
db_manager = DatabaseManager(
    config.DATABASE_URL,
    pool_size=config.DB_POOL_SIZE,
    max_overflow=config.DB_MAX_OVERFLOW,
    pool_timeout=config.DB_POOL_TIMEOUT,
)
redis_manager = RedisManager(config.REDIS_URL)

app.add_exception_handler(BaseApplicationError, application_error_handler)

store = InMemoryTelemetryStore()


class TelemetryPayload(BaseModel):
    model: str
    prompt_length: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)
    latency_ms: float = Field(ge=0.0)
    timestamp: float = Field(default_factory=time_module.time)


@app.middleware("http")
async def add_telemetry(request, call_next):
    return await telemetry_middleware(request, call_next)


@app.post("/log")
def log_telemetry(data: TelemetryPayload):
    store.log_request(data.model_dump())
    return {"status": "logged"}


@app.get("/metrics")
def get_metrics():
    aggregates = store.get_aggregates()
    if store.logs:
        latencies = [x["latency_ms"] for x in store.logs]
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        aggregates["p95_latency_ms"] = (
            sorted_lat[int(n * 0.95)] if n > 0 else 0.0
        )
        idx99 = min(int(n * 0.99), n - 1)
        aggregates["p99_latency_ms"] = (
            sorted_lat[idx99] if n > 0 else 0.0
        )
    else:
        aggregates["p95_latency_ms"] = 0.0
        aggregates["p99_latency_ms"] = 0.0

    by_model = {}
    for entry in store.logs:
        m = entry.get("model", "unknown")
        if m not in by_model:
            by_model[m] = {"calls": 0, "total_cost": 0.0, "total_tokens": 0}
        by_model[m]["calls"] += 1
        by_model[m]["total_cost"] += entry.get("cost_usd", 0)
        by_model[m]["total_tokens"] += (
            entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
        )
    aggregates["by_model"] = by_model

    return aggregates


@app.get("/health")
def health_check():
    return check_health(db_manager, redis_manager, config.APP_NAME)


@app.get("/dashboard")
def dashboard(format: str = "json"):
    """Returns a dashboard view of telemetry data."""
    if format == "text":
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(generate_text_report(store))
    if format == "html":
        from fastapi.responses import HTMLResponse

        return HTMLResponse(generate_html_dashboard(store))
    return get_metrics()
