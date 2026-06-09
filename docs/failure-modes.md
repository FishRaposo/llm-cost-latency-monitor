# Failure Modes & Mitigation - LLM Cost & Latency Monitor

This document details anticipated failure modes, detection strategies, and mitigation pathways for the LLM Cost & Latency Monitor.

---

## 1. Out-of-Memory (OOM) via Memory Store

- **Cause**: Sustained high-throughput usage sends millions of logs to the API. Because `InMemoryTelemetryStore` accumulates events in a Python list (`self.logs`), RAM usage increases indefinitely.
- **Impact**: The FastAPI worker process crashes due to OOM, dropping the service and failing all requests with 502/504 gateways.
- **Detection**: 
  - System memory usage alerts.
  - Process exit codes matching memory limit terminations.
- **Mitigation**: Restarting the service clears memory but drops historical metrics.
- **Future Fix**: Implement a rolling list limit (e.g., store only the last 10,000 requests) or flush records to a database (PostgreSQL/ClickHouse) periodically in batches, clearing the in-memory array.

---

## 2. Model Pricing Defaulting to Zero

- **Cause**: The client application requests a model string not defined in `PRICING_MAP` (e.g., `gpt-4o`, `claude-3.5-sonnet`).
- **Impact**: The cost calculations in `estimate_cost()` fallback to rates of `0.0`, resulting in a recorded cost of `$0.00` for that query. This skews total cost metrics.
- **Detection**: `/metrics` aggregates report high query count but disproportionately low or zero total cost.
- **Mitigation**: Update the `PRICING_MAP` dictionary in `pricing.py` with the correct model rates and redeploy.
- **Future Fix**: Store pricing maps in a database table or Redis cache that can be updated dynamically via API, and return a default fallback cost (e.g., average token rate) instead of `$0.00` when a model is not matched.

---

## 3. Synchronous Network Overhead in Client App

- **Cause**: If the client SDK is configured to perform a blocking HTTP POST to the monitor's `/log` endpoint within the execution thread.
- **Impact**: Any network jitter, packet loss, or high latency on the monitor server will block the client application thread, directly increasing user-facing latency.
- **Detection**: Client application latency logs show a massive spike in overall request times, even though the raw LLM generation latency (`latency_ms`) remains constant.
- **Mitigation**: Re-route the `storage_callback` to fire asynchronously (e.g., using `asyncio` or threading) or log to a local file that is scraped out-of-band.
- **Future Fix**: Build thread-safe, non-blocking queueing within the SDK client, batching telemetry updates and flushing them in the background.

---

## 4. Database / Redis Connectivity Degradation

- **Cause**: Sibling Postgres or Redis containers go offline.
- **Impact**: The `/health` endpoint responds with status `"degraded"`, but the core telemetry `/log` and `/metrics` routes continue to operate normally (since the telemetry store is currently in-memory).
- **Detection**:
  - `GET /health` returns status degraded.
  - Log traces show connection warnings.
- **Mitigation**: Run `make docker-up` to restart background infrastructure.
- **Future Fix**: Build alert integrations that notify operators when dependencies drop, separating critical API paths from secondary reporting structures.
