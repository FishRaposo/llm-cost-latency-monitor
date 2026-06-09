# Implementation Plan - LLM Cost & Latency Monitor

This document details the step-by-step technical implementation plan and development milestones for **LLM Cost & Latency Monitor**.

---

## 1. Project Goal
An observability middleware proxy server that intercepts LLM outbound calls, logs prompt/completion metrics, calculates token cost estimations, and presents metrics via dashboards.

---

## 2. Architecture & Component Map

The repository is structured as a standalone project conforming to operator workspace standards. The core module responsibilities are mapped below:

### 2.1 File Map & Responsibilities
* **`src/llm_monitor/proxy.py`**: FastAPI middleware proxy intercepting chat completion requests and routing them to vendors.
* **`src/llm_monitor/metrics.py`**: Extracts token usage, latency metrics, and updates running averages.
* **`src/llm_monitor/storage.py`**: Persists call logs and calculated costs to the metrics database.
* **`src/llm_monitor/api.py`**: API endpoints serving queries for aggregate latencies, models cost distribution, and call histories.

### 2.2 Shared Core Dependencies
This service imports standard layers from `shared-core` (sibling dependency library):
* `shared_core.config.BaseAppConfig`: Settings parsing, reading configs from `.env`.
* `shared_core.database.DatabaseManager`: SQL database engine instantiation and session factories.
* `shared_core.redis.RedisManager`: Caching connections and health checks.
* `shared_core.logging.setup_logging`: Structured log formats and correlation ID tracing.
* `shared_core.errors.BaseApplicationError`: Exception mapping and global handlers.

---

## 3. Database Schema & Data Models

### 3.1 Data Schema
PostgreSQL: `llm_calls` (id, correlation_id, provider, model, prompt_tokens, completion_tokens, cost, latency_ms, status_code, timestamp, client_service).
Redis: Cache layer for model configurations and rate-limits counters.

### 3.2 Redis Storage & Caching Patterns
* Caching: Utilizing `@cache` decorator with prefix keys.
* Concurrency: Lock critical tasks using `RedisLock` context managers.

---

## 4. Step-by-Step Implementation Sequence

The project development checklist is ordered into six milestones:

- `[ ]` **Milestone 1 (Design): Design cost tables for OpenAI/Anthropic and request-interception middleware.**
- `[ ]` **Milestone 2 (Skeleton): Initialize FastAPI routing, DB schemas, and mock external API responder.**
- `[ ]` **Milestone 3 (Core Loop): Implement call interceptor logging token counts and calculated cost metric.**
- `[ ]` **Milestone 4 (Reliability): Add retry queues for metric storage to prevent losing telemetry data.**
- `[ ]` **Milestone 5 (Showcase): Create demo script querying LLM and displaying aggregate costs dashboard in CLI.**
- `[ ]` **Milestone 6 (Publish): Document API specifications and estimated cost calculation limits.**

---

## 5. Standard Makefile & Developer Commands

```bash
make install          # Set up virtual environment and local editable package
make dev              # Boot the microservice API server locally
make test             # Run local pytest / jest test suites
make lint             # Execute Ruff checks / ESLint verifications
make format           # Standardize style formatting
make typecheck        # Verify static types (Pyright / TypeScript)
make docker-up        # Spawn isolated local PostgreSQL and Redis service containers
make docker-down      # Teardown the isolated local containers stack
make demo             # Execute the runnable demo workflow
make clean            # Remove caches and temporary files
```

---

## 6. Verification & Testing Plan

### 6.1 Automated Tests
* **Core Logic Verification**: Verify middleware token extraction, cost calculator logic, and mock downstream proxy routing.
* **Type Safety & Style**: Run `make typecheck` and `make lint` as a pipeline validation hook.
* **Mock Environments**: Utilize `MockDatabase` and `MockRedisClient` inside `tests/conftest.py` to assert correct lifecycle transactions without depending on live network services.

### 6.2 Manual Verification
* Deploy local PostgreSQL and Redis containers with `make docker-up`.
* Execute the runnable script demo `make demo` and review Loguru stdout records.
