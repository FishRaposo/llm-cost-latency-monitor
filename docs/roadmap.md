# Project Roadmap - LLM Cost & Latency Monitor

This document outlines the planned developmental milestones for the LLM Cost & Latency Monitor.

---

## Milestone 1: Telemetry Instrumentation (Completed)
- **FastAPI Telemetry Middleware**: Intercept and log latency and HTTP path details across all server routes.
- **Static Pricing Engine**: Cost calculation engine supporting GPT-4, GPT-3.5, and Claude models.
- **Monitored SDK Client**: Light programmatic client wrapper supporting callback logs and token approximation rules.
- **In-Memory Aggregate Analytics**: `/metrics` aggregation route compiling real-time summary statistics.

---

## Milestone 2: Persistent Storage & Analytics Dashboard (Planned)
- **Database Persistence**: Move metrics storage from volatile server memory to PostgreSQL (leveraging SQLAlchemy maps).
- **Interactive Visual Dashboard**: Build a web-based frontend displaying real-time cost charts, latency trend lines, and token efficiency ratios.
- **Dynamic Pricing Registry**: Save model rates in Postgres so new model rates can be registered via API without redeploying code.
- **Alert Triggering Rules**: Configure rules to trigger alerts (logs, Webhooks) when a single query exceeds latency thresholds (e.g., >5 seconds) or cost limits.

---

## Milestone 3: Time-Series Scaling & Production Grade (Future)
- **Asynchronous Queue Buffering**: Use Redis lists as a buffer queue for incoming metrics. A Celery background worker consumes logs and writes to the DB, shielding the web API from spike traffic.
- **ClickHouse Integration**: Swap PostgreSQL with ClickHouse for telemetry log storage to support efficient high-volume analytical queries.
- **OpenTelemetry Compatibility**: Add support for OpenTelemetry collector exports, allowing telemetry data to integrate into systems like Datadog or Prometheus.
- **Semantic Request Auditing**: Optionally cache prompt hashes to identify duplicate queries and track caching optimization ratios.
