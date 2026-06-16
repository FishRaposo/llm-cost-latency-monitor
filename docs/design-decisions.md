# Key Technical Decisions — LLM Cost & Latency Monitor

The core design choices and trade-offs behind the monitor.

---

## 1. Pricing delegated to `shared_core.pricing` (single source of truth)

- **Decision**: Remove the local static pricing table as the source of truth. `pricing.py` is now a thin wrapper whose `estimate_cost` calls `shared_core.pricing.calculate_cost`, and whose `PRICING_MAP` is *derived* from the shared per-1M registry (projected to per-1k units for display only).
- **Rationale**: Multiple workspace projects price LLM calls. Divergent tables silently disagree on cost. One registry — override-able via JSON/YAML — keeps every service consistent and lets ops adjust prices without code changes.
- **Trade-offs**: A local import indirection; mitigated by keeping the wrapper API identical so existing callers (SDK, dashboard, tests) are unaffected.

---

## 2. Aggregation delegated to `shared_core.llmmetrics.LLMMetrics`

- **Decision**: Totals, per-model and per-prompt-version cost, p50/p95/p99 latency, and error rate all come from `LLMMetrics.summary()`. Both the in-memory and the DB store feed records into an `LLMMetrics` instance.
- **Rationale**: Percentile math is easy to get subtly wrong (off-by-one indexing, interpolation). Computing it once, in a shared, tested module, guarantees the two backends return identical numbers and removes duplicated logic from `main.py`.
- **Trade-offs**: The DB store loads all rows into memory to aggregate. Acceptable at showcase scale; a production deployment would push aggregation into SQL or a rollup table.

---

## 3. DB persistence by default, in-memory fallback (offline-first)

- **Decision**: On startup a `db_available` probe decides the backend: PostgreSQL when reachable, `InMemoryTelemetryStore` otherwise. The `DatabaseManager` is built **lazily** so importing the app never requires a DB driver.
- **Rationale**: The project must run and test with **no database** (CI, demos) yet persist by default in production. The probe pattern — mirrored from the migrated `knowledgeops` services — gives both without branching consumer code.
- **Trade-offs**: Two code paths to keep in sync; mitigated by a shared store interface and tests that exercise the DB store against in-memory SQLite.

---

## 4. Mock-by-default SDK, real-when-keyed

- **Decision**: `MonitoredLLMClient.generate(mocked_response=...)` short-circuits to a deterministic simulated response. Without a mock, it calls `shared_core.llm.LLMClientFactory`; missing SDK or no API key raises `ImportError` and falls back to a mock, and any real-call exception is captured in `telemetry["error"]` rather than raised.
- **Rationale**: Tests and demos run offline and deterministically; production gets real calls by setting keys. Capturing errors (instead of raising) keeps the error-rate metric accurate and never crashes the caller for an observability concern.
- **Trade-offs**: Token counts for mocked calls use a `len // 4` heuristic; real calls use provider-reported usage.

---

## 5. Decoupled SDK callback pattern

- **Decision**: `MonitoredLLMClient` takes a `storage_callback`. The same client can append to a list, write to the DB store, POST to `/log`, or enqueue a task — without changing the SDK.
- **Rationale**: Separates instrumentation from transport. The demo uses an in-memory list; a service uses the active store; an integration could fire an async task.

---

## 6. Two middlewares from `shared_core`

- **Decision**: Wire `RequestLoggingMiddleware` (correlation IDs, structured request logs) and `MetricsMiddleware` (Prometheus request count/duration), and expose `/metrics/prometheus`.
- **Rationale**: Reuse the shared, tested observability stack rather than hand-rolling per-route hooks. `prometheus_client` is an optional dependency, imported dynamically, so the import never hard-fails.

---

## 7. Reports & budgets as pure functions, reused by API and worker

- **Decision**: `reports.build_daily_report` / `report_to_csv` and `budgets.evaluate_budget` operate on any store via its public interface and are called from both HTTP endpoints and Celery tasks.
- **Rationale**: One implementation, two invocation paths (synchronous request vs. scheduled async task). The worker stays importable without a broker because task bodies are thin wrappers over these pure functions.
