"""Monitored LLM client SDK.

Wraps an LLM call to record latency, token usage, cost, prompt version, and
errors, then dispatches the telemetry to a storage callback. Mirrors the
offline-first / real-when-keyed pattern: a ``mocked_response`` short-circuits to
a deterministic simulated response, otherwise the real provider path runs via
``shared_core.llm.LLMClientFactory`` with a graceful fallback to simulation when
the SDK is missing or no API key is configured.
"""

import time
from typing import Any, Dict, Optional

from loguru import logger

from .pricing import estimate_cost


class MonitoredLLMClient:
    """Wraps LLM calls to record duration, token usage, cost, and errors.

    Supports both real API calls (via ``shared_core.llm.LLMClientFactory``)
    and deterministic mock generation for testing/demos.
    """

    def __init__(self, storage_callback, api_keys: Optional[dict] = None):
        self.storage_callback = storage_callback
        self.api_keys = api_keys or {}

    def generate(
        self,
        model: str,
        prompt: str,
        mocked_response: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        prompt_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a completion and record telemetry.

        Args:
            model: model identifier (e.g. ``gpt-4o-mini``, ``claude-3-haiku``).
            prompt: the user prompt.
            mocked_response: when set, short-circuits to a deterministic
                simulated response (offline-first default for tests/demos).
            temperature / max_tokens: forwarded to the real provider path.
            prompt_version: optional label for A/B prompt-version tracking.

        Returns:
            ``{"response": str, "telemetry": dict}``. On a real-call failure the
            error is captured in ``telemetry["error"]`` and re-raised never —
            the telemetry is always recorded so error rates stay accurate.
        """
        start_time = time.time()
        error: Optional[str] = None

        if mocked_response is not None:
            # Deterministic simulated path — no network, no keys.
            time.sleep(0.05)
            text = mocked_response
            input_tokens = len(prompt) // 4
            output_tokens = len(text) // 4
        else:
            try:
                text, input_tokens, output_tokens = self._call_llm(
                    model, prompt, temperature, max_tokens
                )
            except ImportError:
                logger.warning("LLM SDK not installed — falling back to mock mode")
                time.sleep(0.05)
                text = f"Mock response for: {prompt[:50]}..."
                input_tokens = len(prompt) // 4
                output_tokens = len(text) // 4
            except Exception as exc:  # noqa: BLE001 - record, don't crash caller
                error = f"{type(exc).__name__}: {exc}"
                logger.error("LLM call failed for model {}: {}", model, error)
                time.sleep(0.05)
                text = ""
                input_tokens = len(prompt) // 4
                output_tokens = 0

        latency = (time.time() - start_time) * 1000.0
        cost = estimate_cost(model, input_tokens, output_tokens)

        telemetry = {
            "model": model,
            "prompt_length": len(prompt),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "latency_ms": latency,
            "prompt_version": prompt_version,
            "error": error,
            "timestamp": time.time(),
        }
        self.storage_callback(telemetry)
        return {"response": text, "telemetry": telemetry}

    def _call_llm(self, model: str, prompt: str, temperature: float, max_tokens: int):
        """Invoke the real provider via shared_core. Raises on no SDK / no key."""
        import asyncio

        from shared_core.llm import LLMClientFactory

        openai_key = self.api_keys.get("openai")
        anthropic_key = self.api_keys.get("anthropic")
        factory = LLMClientFactory(
            openai_api_key=openai_key,
            anthropic_api_key=anthropic_key,
        )

        is_anthropic = "claude" in model.lower()
        if is_anthropic and not anthropic_key:
            raise ImportError("No Anthropic API key configured")
        if not is_anthropic and not openai_key:
            raise ImportError("No OpenAI API key configured")

        if is_anthropic:
            response = asyncio.run(
                factory.generate_anthropic(
                    model, prompt, temperature=temperature, max_tokens=max_tokens
                )
            )
        else:
            response = asyncio.run(
                factory.generate_openai(
                    model, prompt, temperature=temperature, max_tokens=max_tokens
                )
            )

        return response.text, response.prompt_tokens, response.completion_tokens
