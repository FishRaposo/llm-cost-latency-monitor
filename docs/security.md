# Security Boundaries & Rules - LLM Cost & Latency Monitor

This document outlines the security parameters, boundaries, and data-handling rules for the LLM Cost & Latency Monitor.

---

## 1. Secrets Isolation & Credentials Handling

- **No API Provider Secrets**: The monitor service does NOT store, handle, or forward LLM provider API credentials (such as `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
- **Telemetry Separation**: The Telemetry API is purely a monitoring sink. It is isolated from model generation pathways. If the monitor is compromised, active LLM provider API keys in client applications remain secure.

---

## 2. Personal Identifiable Information (PII) Protection

- **Length-Only Tracking**: By design, the `MonitoredLLMClient` tracks only the character count (`prompt_length`), input tokens, and output tokens. It **does not transmit the raw prompt text** or output text to the server.
- **Zero-Storage of Payload Data**: Preventing prompt-text ingestion eliminates the risk of logging PII, credit card details, or proprietary business logic inside telemetry databases.
- **Opt-in Hashing**: If request auditing is added, prompts must be hashed using SHA-256 before transmission.

---

## 3. API Boundary Protections

- **Payload Validation**: The `/log` endpoint must validate incoming JSON structure (requiring numeric validation on cost, latency, and tokens) to prevent buffer overflows or numeric injections.
- **Write Path Access**: In multi-tenant systems, client SDKs must authenticate using a write-only API token, restricting telemetry generation to registered workloads.
- **Rate Limiting**: Telemetry endpoints are high-throughput and must be protected by rate-limiting middleware to prevent denial-of-service (DoS) attempts that could consume available worker memory.
