# LLM Cost & Latency Monitor

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3+-37814a?logo=celery&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## An observability layer that wraps LLM API calls to track token usage, estimate cost, measure latency, and surface aggregate metrics — so you can answer "how much did that prompt cost?" before the invoice arrives.

---

## Why This Exists

Production LLM applications are expensive to run and difficult to debug. A single prompt experiment can cost dollars, yet most teams discover their spend only at the end of the billing cycle. Latency varies wildly across models and prompt lengths, errors are transient, and there is no standard way to compare cost-per-quality across providers.

This project provides a **lightweight, self-hosted observability layer** that sits between your application code and the LLM API. It captures every request, estimates its cost in real time using a local pricing table, records latency, and exposes aggregate metrics through a FastAPI service. It is designed to be embedded in any Python backend as an SDK wrapper or plugged in as middleware — no external SaaS dependency required.

This is a **Wave 1** project in the [showcase portfolio](https://github.com/FishRaposo/operator-shared-core/blob/main/docs/workspace-map.md). It provides the monitoring infrastructure that downstream AI projects ([`rag-evaluation-lab`](https://github.com/FishRaposo/rag-evaluation-lab), [`aria-agent`](https://github.com/FishRaposo/aria-agent), [`ai-support-simulator`](https://github.com/FishRaposo/ai-support-simulator)) can integrate with to track their own LLM spend.

## What It Demonstrates

- **SDK Wrapper Pattern** — `MonitoredLLMClient` wraps any LLM call, capturing telemetry without changing the caller's interface
- **FastAPI Middleware Design** — `telemetry_middleware` intercepts every HTTP request for latency instrumentation
- **Cost Estimation Engine** — `PRICING_MAP` with per-model input/output token rates and `estimate_cost()` calculation
- **In-Memory Metrics Aggregation** — `InMemoryTelemetryStore` collects telemetry and computes aggregates (total calls, total cost, average latency)
- **Structured Error Handling** — `BaseApplicationError` hierarchy from `shared-core` with JSON error responses
- **Health Check Pattern** — `/health` endpoint probing both database and Redis connectivity with degraded-state reporting
- **Background Task Infrastructure** — Celery worker skeleton with Redis broker, ready for async report generation

## Architecture

```mermaid
graph TD
    App["Your Application"] -->|wraps calls| SDK["MonitoredLLMClient<br/>(sdk.py)"]
    SDK -->|estimates cost| Pricing["PRICING_MAP<br/>(pricing.py)"]
    SDK -->|logs telemetry| Store["InMemoryTelemetryStore<br/>(storage.py)"]
    Store -->|serves| API["FastAPI Service<br/>(main.py)"]
    API -->|GET /metrics| Metrics["Aggregate Metrics"]
    API -->|POST /log| Ingest["External Telemetry Ingest"]
    API -->|middleware| MW["telemetry_middleware<br/>(middleware.py)"]
    API -->|health| HC["GET /health"]
    HC -->|probes| DB[(PostgreSQL)]
    HC -->|probes| Redis[(Redis)]
    Worker["Celery Worker<br/>(worker.py)"] -.->|future: async reports| Redis
```

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| API Framework | FastAPI + Uvicorn | Async-native, automatic OpenAPI docs, middleware support |
| SDK Client | Pure Python | Zero-dependency wrapper, portable across projects |
| Cost Engine | Static pricing map | No external API calls needed for estimates |
| Database | PostgreSQL 16 (pgvector) | Shared infrastructure across portfolio projects |
| Cache / Broker | Redis 7 | Celery message broker + future metrics caching |
| Task Queue | Celery 5.3+ | Async report generation and scheduled summaries |
| Config | pydantic-settings | Type-safe environment variable loading |
| Logging | Loguru via shared-core | Structured logging with service name tagging |
| Lint / Format | Ruff | Single tool for linting (E, W, F, I, C, B rules) and formatting |
| Type Checking | Pyright | Strict mode for `src/` |
| Testing | Pytest | FastAPI TestClient integration |
| Shared Library | [`shared-core`](../shared-core/) | Config, database, redis, logging, error base classes |

## Local Setup

```bash
# Enter project directory
cd llm-cost-latency-monitor

# Copy environment template
cp .env.example .env

# Start PostgreSQL and Redis containers
make docker-up

# Install shared-core and project dependencies
make install

# Run the API server (default: http://localhost:8000)
make dev

# Verify it works
curl http://localhost:8000/health
```

## Demo

The demo script simulates two monitored LLM requests (GPT-4 and GPT-3.5-turbo) using the `MonitoredLLMClient` SDK wrapper, then prints aggregate telemetry:

```bash
make demo
```

Expected output:

```
--- Simulating Monitored LLM Requests ---
Accumulated telemetry metrics:
Total Calls: 2
Total Estimated Cost: $0.000XXX
Average Latency: ~150.00ms
```

The demo does not call any real LLM APIs — `MonitoredLLMClient.generate()` uses a mocked response with a 150ms simulated delay. Token counts are estimated at 1 token per 4 characters.

## Tests

```bash
make test
```

Current test coverage:

- **`test_core.py`** — Verifies the `/health` endpoint returns HTTP 200, the correct service name (`llm-cost-latency-monitor`), and a `dependencies` object reporting database/redis status

Tests use FastAPI's `TestClient` for synchronous HTTP testing without a running server.

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Returns service health with database and Redis connectivity status |
| `POST` | `/log` | Accepts a telemetry payload `dict` and stores it in-memory |
| `GET` | `/metrics` | Returns aggregate metrics: `total_calls`, `total_cost`, `avg_latency` |

### Example: Log Telemetry

```bash
curl -X POST http://localhost:8000/log \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4","input_tokens":100,"output_tokens":50,"cost_usd":0.006,"latency_ms":230,"timestamp":1700000000}'
```

### Example: Get Metrics

```bash
curl http://localhost:8000/metrics
# {"total_calls": 1, "total_cost": 0.006, "avg_latency": 230.0}
```

## Configuration

Key environment variables from `.env.example`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `APP_NAME` | `llm-cost-latency-monitor` | Service identifier in logs and health checks |
| `ENV` | `development` | Runtime environment flag |
| `DEBUG` | `true` | Enable debug-level diagnostics |
| `LOG_LEVEL` | `INFO` | Loguru log threshold |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/postgres` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection for Celery broker and caching |
| `OPENAI_API_KEY` | *(placeholder)* | Required when using real OpenAI API calls |
| `ANTHROPIC_API_KEY` | *(placeholder)* | Required when using real Anthropic API calls |

## Known Limitations

- **In-memory storage only** — `InMemoryTelemetryStore` loses all data on restart; no PostgreSQL persistence yet
- **Mocked LLM calls** — `MonitoredLLMClient.generate()` simulates responses with `time.sleep(0.15)` instead of calling real APIs
- **Approximate token counting** — Uses `len(text) // 4` as a rough heuristic instead of tiktoken or provider-specific tokenizers
- **Static pricing table** — `PRICING_MAP` in `pricing.py` is hardcoded for 3 models (gpt-4, gpt-3.5-turbo, claude-3-opus); unknown models default to $0.00
- **No authentication** — `/log` and `/metrics` endpoints are open; anyone on the network can push telemetry or read metrics
- **No prompt version tracking** — The `prompt_version` field mentioned in the build plan is not yet implemented
- **Celery worker is a stub** — `sample_background_task` is a placeholder that adds two numbers; no real async tasks defined
- **No authentication** — `/log` and `/metrics` endpoints are open; anyone on the network can push telemetry or read metrics

## Roadmap

- **Phase 1 — MVP** *(current)*: SDK wrapper, pricing engine, in-memory store, FastAPI telemetry API, health checks
- **Phase 2 — Display-Ready**: PostgreSQL persistence, Pydantic request/response models, prompt version tracking, daily summary report via Celery, p95 latency calculation, cost-by-model breakdown
- **Phase 3 — Showcase**: Dashboard UI, model comparison view, budget alert thresholds, CSV export, integration examples with `rag-evaluation-lab` and `hermes-agent-framework`
- **Phase 4 — Future**: Real LLM API integration (OpenAI, Anthropic), tiktoken-based token counting, streaming response support, OpenTelemetry export, webhook notifications

See [docs/roadmap.md](docs/roadmap.md) for detailed milestone breakdowns.
ook notifications

See [docs/roadmap.md](docs/roadmap.md) for detailed milestone breakdowns.
