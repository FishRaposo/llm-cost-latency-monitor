# AGENTS.md — LLM Cost & Latency Monitor

## What This Is

A self-hosted observability layer and SDK wrapper that intercepts, records, and
aggregates token usage, dollar cost, latency, prompt versions, and errors across
LLM APIs. Offline-first (runs with no database and no API keys); persists to
PostgreSQL and calls real providers when configured.

## Commands

```bash
make install          # pip install -e "../shared-core[dev,docparse,embeddings]" && pip install -e ".[dev]"
make dev              # python -m llm_monitor.main (FastAPI on :8000)
make test             # pytest (91 tests; no network / no DB required)
make lint             # ruff check src/llm_monitor tests examples
make format           # ruff format src/llm_monitor tests examples
make typecheck        # pyright src/
make docker-up        # docker compose up -d (Postgres + Redis)
make demo             # python examples/run_demo.py
make examples         # run both integration examples
make worker           # celery -A llm_monitor.worker worker (needs Redis)
make upgrade          # alembic upgrade head
```

## Module Inventory (`src/llm_monitor/`)

- **`main.py`** — FastAPI app. Startup `db_available` probe selects the store. Endpoints: `POST /log`, `GET /metrics`, `GET /metrics/prometheus`, `GET /reports/daily`, `GET /budgets/alerts`, `GET /dashboard`, `GET /health`. Wires `MetricsMiddleware` and `RequestLoggingMiddleware`.
- **`sdk.py`** — `MonitoredLLMClient`: mock-by-default / real-when-keyed generation; records latency, tokens, cost, `prompt_version`, and `error`.
- **`pricing.py`** — thin wrapper delegating to `shared_core.pricing`; `PRICING_MAP` derived from the shared registry (display only).
- **`storage.py`** — `InMemoryTelemetryStore`, aggregation via `shared_core.llmmetrics.LLMMetrics`.
- **`storage_db.py`** — `DatabaseTelemetryStore` (SQLAlchemy persistence, same aggregation engine, same interface).
- **`db.py`** — lazy `DatabaseManager`, `check_db()` probe, `build_store()` selector.
- **`reports.py`** — `build_daily_report` (JSON) + `report_to_csv`.
- **`budgets.py`** — `evaluate_budget` (total + per-model USD thresholds → flagged alerts).
- **`worker.py`** — Celery app + `generate_daily_report` / `check_budget` tasks (importable without a broker).
- **`models.py`** — `LLMCall` ORM (adds `prompt_version`, `error`).
- **`dashboard.py`** — text/HTML renderers reading `get_aggregates()`.
- **`config.py`** — `AppConfig` (adds `BUDGET_THRESHOLD_USD`, `BUDGET_PER_MODEL_THRESHOLD_USD`).
- **`middleware.py`** — legacy `telemetry_middleware` helper (retained; primary instrumentation is shared_core middleware in `main.py`).

## Endpoints (what a dashboard consumes)

| Method | Path | Returns |
|--------|------|---------|
| POST | `/log` | `{status: logged}` |
| GET | `/metrics` | totals, by_model, cost_by_prompt_version, p50/p95/p99, error_rate |
| GET | `/metrics/prometheus` | Prometheus text (HTTP request metrics) |
| GET | `/reports/daily?day=&format=json\|csv` | daily rollups + totals |
| GET | `/budgets/alerts?threshold_usd=&per_model_threshold_usd=` | flagged alerts |
| GET | `/dashboard?format=json\|text\|html` | dashboard view |
| GET | `/health` | dependency status |

## Dependencies & Integrations

- **`shared-core` v1.3.0** (editable): config, database, redis, logging, errors, health, metrics, pricing, llmmetrics, llm, tasks, embeddings, testing.
- **PostgreSQL** — durable telemetry (optional; in-memory fallback otherwise). Schema via Alembic (`alembic/versions/0001_initial_llm_calls.py`).
- **Redis** — Celery broker for async report/budget tasks.

## Examples

- `examples/run_demo.py` — offline batch of monitored calls + report + budget alert.
- `examples/wrapped_fastapi_app.py` — a FastAPI app with a monitored `/chat`.
- `examples/wrapped_rag_app.py` — a RAG pipeline (offline embeddings) with monitored generation.

## When to Update This AGENTS.md

Update when the telemetry schema/columns change, new endpoints or Celery tasks
are added, the store-selection/persistence logic changes, or the set of adopted
`shared_core` modules changes.
