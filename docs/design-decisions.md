# Key Technical Decisions - LLM Cost & Latency Monitor

This document analyzes the core design choices, architectural trade-offs, and engineering decisions behind the LLM Cost & Latency Monitor.

---

## 1. In-Memory Telemetry Storage (`storage.py`)

- **Decision**: Persist logs in a python list inside an `InMemoryTelemetryStore` object rather than writing directly to PostgreSQL on every write.
- **Rationale**: Telemetry events occur on every LLM generation. Writing synchronously to a database on every call adds latency overhead to the user application. The in-memory store allows sub-millisecond writes.
- **Trade-offs**: If the server crashes or restarts, historical metrics are lost. This is acceptable for a showcase MVP. In production, this store would buffer logs and flush them asynchronously to PostgreSQL or ClickHouse.

---

## 2. Character-Count Token Approximation (`sdk.py`)

- **Decision**: Approximate input/output token counts using a character division heuristic (`len(prompt) // 4`) instead of importing tokenization libraries like `tiktoken` or Hugging Face `tokenizers`.
- **Rationale**: 
  - Importing tiktoken requires downloading vocabulary files and compiling Rust-based wheels, which increases setup complexity and dependency sizes.
  - A 4-character-per-token heuristic provides a standard approximation that is highly effective for calculating relative model costs without setup friction.
- **Trade-offs**: Slightly less accurate than using a model-specific BPE (Byte Pair Encoding) tokenizer.

---

## 3. Decoupled SDK Callback Pattern (`sdk.py`)

- **Decision**: The `MonitoredLLMClient` requires a `storage_callback` function parameter upon instantiation.
- **Rationale**: This decouples the client-side instrumentation from the network transport layer. The same client class can print logs, write directly to a local file, trigger an asynchronous task, or send an HTTP POST request to the monitor API without modifying the SDK codebase.
- **Trade-offs**: Developers must supply a callback function during client initialization.

---

## 4. Middleware-Based Telemetry Interception (`middleware.py`)

- **Decision**: Capture service performance parameters using ASGI middleware (`telemetry_middleware`) rather than adding tracking hooks inside route functions.
- **Rationale**: Decouples API monitoring from business endpoints. Ensures latency and status codes are captured uniformly across all routes, even if they fail and raise unhandled exceptions.
