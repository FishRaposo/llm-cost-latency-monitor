# Security Boundaries & Rules — LLM Cost & Latency Monitor

Security parameters, boundaries, and data-handling rules.

---

## 1. Secrets isolation

- **Provider keys live with the caller, not the sink.** The telemetry API (`/log`, `/metrics`, `/reports/daily`, `/budgets/alerts`) never receives, stores, or forwards `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`. Keys are only read by `MonitoredLLMClient` inside the *client* process when the real provider path is used.
- **SecretStr handling.** Config keys are typed as `pydantic.SecretStr` in `BaseAppConfig`; `shared_core.llm` unwraps them only at call time, keeping them out of logs and `repr()` output.
- **Offline by default.** With no keys set, the SDK runs mocked — there is no credential surface at all in CI/demos.

---

## 2. PII protection

- **No raw prompt/response text is persisted.** Telemetry records `prompt_length`, `input_tokens`, `output_tokens`, `cost_usd`, `latency_ms`, `prompt_version`, and an optional `error` string — never the prompt or completion body. This eliminates the risk of logging PII or proprietary content in the telemetry database.
- **Error strings are truncated** to 500 chars before persistence (`storage_db.py`), limiting accidental leakage of payload fragments embedded in exception messages.
- **Prompt versions are labels, not content** — safe to store and group on.

---

## 3. API boundary protections

- **Schema validation.** `POST /log` is validated by the `TelemetryPayload` Pydantic model: numeric fields are non-negative (`ge=0`), types are enforced, and malformed bodies return `422` before touching the store.
- **Query validation.** `/budgets/alerts` thresholds and `/reports/daily` parameters are validated (`ge=0.0`, typed) at the framework boundary.
- **Correlation IDs.** `RequestLoggingMiddleware` assigns/propagates an `X-Correlation-ID` per request for auditability.

---

## 4. Known gaps & recommended hardening (showcase scope)

- **No authentication / authorization.** Endpoints are open. For production, place behind an API gateway and require a **write-only token** for `/log` and a read token for metrics/reports.
- **No built-in rate limiting.** Telemetry ingestion is high-throughput; add `shared_core.ratelimit` or gateway-level limits to prevent DoS / memory exhaustion (see failure-modes §2).
- **Transport.** Terminate TLS at a proxy; do not expose the service directly.
- **Budget data sensitivity.** Aggregate spend may be commercially sensitive; restrict `/metrics`, `/reports/daily`, and `/dashboard` to authorized readers.
