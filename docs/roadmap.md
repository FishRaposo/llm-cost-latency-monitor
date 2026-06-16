# Roadmap — LLM Cost & Latency Monitor

---

## Phase 1 — MVP (Completed)

- FastAPI telemetry service with `/log` and `/metrics`.
- Monitored SDK client with callback logging and token approximation.
- Cost estimation and in-memory aggregate analytics.
- Health checks against PostgreSQL and Redis.

---

## Phase 2 — Display-Ready (Completed)

- **Pricing as a single source of truth** — delegated to `shared_core.pricing`; local module is a thin wrapper.
- **Unified aggregation** — totals, per-model, per-prompt-version, p50/p95/p99 latency, and error rate via `shared_core.llmmetrics.LLMMetrics`.
- **DB persistence with graceful fallback** — `DatabaseTelemetryStore` wired via a `db_available` probe; in-memory fallback for tests/demos; Alembic migration for the `llm_calls` table.
- **Prompt-version and error tracking** end to end (SDK → store → metrics → reports).
- **Daily report generator** (JSON + CSV) via `/reports/daily` and the `generate_daily_report` Celery task.
- **Budget alerts** (total + per-model USD thresholds) via `/budgets/alerts` and the `check_budget` Celery task.
- **Prometheus + request-logging middleware** and a `/metrics/prometheus` endpoint.
- **Real Celery worker** replacing the sample task; importable without a broker.
- **Two integration examples** — a wrapped FastAPI app and a wrapped RAG app (offline embeddings).
- **Comprehensive tests** — unit, integration, API, worker, persistence, and demo smoke tests.

---

## Phase 3 — Showcase (Planned)

- Interactive dashboard UI (cost charts, latency trends, prompt-version comparison) — the API already exposes everything a dashboard needs.
- Per-model **cost gauges** in the Prometheus exposition (today's Prometheus endpoint covers HTTP request metrics; cost/latency detail is in the JSON `/metrics`).
- **Webhook / push alerting** when a budget is breached, in addition to the pull-based endpoint.
- Dynamic pricing registry editable via API (built on `shared_core.pricing.load_pricing_override`).
- Per-query latency/cost threshold rules.

---

## Phase 4 — Future

- **tiktoken-based** token counting for exact (not heuristic) input/output tokens.
- **Streaming-response** telemetry (time-to-first-token, inter-token latency).
- **OpenTelemetry** export so telemetry flows into Datadog / Grafana / Tempo.
- Async queue buffering (Redis list → worker → DB) to shield the API from spikes; optional ClickHouse backend for high-volume analytical queries.
- Prompt-hash auditing to measure cache-hit / duplicate-query ratios.
