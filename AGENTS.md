# AGENTS.md — LLM Cost & Latency Monitor

## What This Is

A specialized service and SDK wrapper designed to intercept, record, and aggregate latency, token usage, and dollar cost across various large language model (LLM) APIs.

## Commands

```bash
make install          # pip install -e ../shared-core && pip install -r requirements.txt
make dev              # python src/main.py (FastAPI on :8000)
make test             # pytest
make lint             # ruff check .
make format           # ruff format .
make typecheck        # pyright src/
make docker-up        # docker compose up -d (Postgres + Redis)
make demo             # python examples/run_demo.py
```

## Module Inventory & Architecture

The source code resides under `src/llm_monitor/`:
- **`main.py`**: API server. Exposes `/log` (to receive raw query telemetry) and `/metrics` (to retrieve aggregate statistics like total calls, total cost, average latency).
- **`sdk.py`**: Contains `MonitoredLLMClient` which wraps API calls to automatically track request duration, construct token estimate payloads, compute cost, and dispatch callbacks.
- **`pricing.py`**: Holds the `PRICING_MAP` (covering GPT-4, GPT-3.5, Claude 3 Opus rates per 1k tokens) and the `estimate_cost` function.
- **`middleware.py`**: Exposes `telemetry_middleware` which intercepts all incoming HTTP traffic to log endpoint path, method, response status, and duration.
- **`storage.py`**: Implementation of `InMemoryTelemetryStore` to store logged metrics and calculate runtime analytics.
- **`config.py`**: Custom `AppConfig` inheriting from `shared_core.config.BaseAppConfig`.
- **`errors.py`**: Application error mapping.

## Dependencies & Integrations

- **`shared-core`**: Core dependency. Must be installed as editable (`-e`).
- **Redis**: Alpine-based container for session/lock checks (broker setup).
- **PostgreSQL**: pgvector container (shared infrastructure baseline).

## When to Update This AGENTS.md

Update this file if the metrics format changes, new SDK APIs are added, pricing maps are moved to dynamic DB configuration, or extra middleware/broker endpoints are introduced.
