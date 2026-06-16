# Execution Plan — LLM Cost & Latency Monitor

What was built to take the project from ~70–80% of MVP to a fully-implemented,
tested, documented state, and what remains.

---

## Starting point

A working SDK wrapper, a static local pricing table, an in-memory store, a
FastAPI service with `/log` and `/metrics`, a stub Celery task, partial docs, and
a handful of tests (mostly `/health`).

---

## What was built (this stage)

### Stubs made real
- **`pricing.py`** — was the source-of-truth static table; now a thin wrapper delegating all cost math to `shared_core.pricing.calculate_cost`, with `PRICING_MAP` *derived* from the shared per-1M registry for display.
- **`storage.py`** — `InMemoryTelemetryStore` now backs aggregation with `shared_core.llmmetrics.LLMMetrics` (p50/p95/p99, error rate, per-prompt-version cost).
- **`storage_db.py`** — `DatabaseTelemetryStore` rewritten to persist the new columns and aggregate via `LLMMetrics`; exposes the same interface as the in-memory store.
- **`worker.py`** — replaced `sample_background_task` with real `generate_daily_report` and `check_budget` tasks; importable without a broker.
- **`main.py`** — rewritten with a startup `db_available` probe, lifespan store selection, and all new endpoints.
- **`models.py`** — added `prompt_version` and `error` columns (indexed where useful).

### shared_core modules adopted
`pricing` (cost), `llmmetrics.LLMMetrics` (aggregation), `metrics` (MetricsMiddleware + Prometheus endpoint), `logging` (RequestLoggingMiddleware + setup_logging), `llm.LLMClientFactory` (real provider path), `tasks.create_celery_app` (worker), `database.DatabaseManager` (persistence), `health.check_health`, `errors.application_error_handler`, `config.BaseAppConfig`, `redis.RedisManager`, `embeddings.get_embedding_provider(offline=True)` (RAG example), `testing` mocks (tests).

### New modules
- **`db.py`** — lazy `DatabaseManager`, `check_db()` probe, `build_store()` selector.
- **`reports.py`** — `build_daily_report` (per-UTC-day JSON rollups + totals) and `report_to_csv`.
- **`budgets.py`** — `evaluate_budget` (total + per-model USD thresholds → flagged alerts).

### New endpoints
`GET /metrics/prometheus`, `GET /reports/daily` (json/csv), `GET /budgets/alerts`; `POST /log` and `GET /metrics` rounded out with prompt-version/error fields; `/health` and `/dashboard` retained (dashboard now reads unified aggregates).

### Examples
- `examples/run_demo.py` — expanded to show prompt versions, reports, and budget alerts.
- `examples/wrapped_fastapi_app.py` — a FastAPI app whose `/chat` endpoint is monitored.
- `examples/wrapped_rag_app.py` — a RAG pipeline using offline embeddings, monitored generation.

### Infrastructure / spine
- Alembic migration `0001_initial_llm_calls` for the `llm_calls` table.
- `requirements.txt` / `pyproject.toml` updated (alembic, prometheus-client, pytest-asyncio).
- `.env.example`, `Makefile`, `pytest.ini` updated; budget config added to `config.py`.

### Tests (from a handful → 91)
`test_sdk` (mock/real/error/prompt-version), `test_pricing` (delegation + derived map), `test_llmmetrics` (summary/percentile delegation), `test_storage` + `test_storage_db` (both backends, SQLite-backed persistence), `test_db` (probe + fallback), `test_reports`, `test_budgets`, `test_worker` (tasks run eagerly, importable without broker), `test_middleware`, `test_models`, `test_api` (every endpoint, success + error), `test_smoke` (demo + both examples run).

---

## Verification (this environment)

- `ruff format` + `ruff check src/llm_monitor tests examples` — clean.
- `pytest` — **91 passed**.
- `examples/run_demo.py` — exits 0.

All run **offline**: no network, no API keys, no database (the DB store is
exercised against in-memory SQLite).

---

## What's next

- Dashboard UI (Phase 3) — the API already exposes everything it needs.
- Per-model cost gauges in the Prometheus exposition.
- Webhook/push budget alerts; dynamic pricing registry via API.
- tiktoken token counting; streaming telemetry; OpenTelemetry export (Phase 4).
