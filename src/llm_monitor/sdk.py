import time
from typing import Any, Dict, Optional

from loguru import logger

from .pricing import estimate_cost


class MonitoredLLMClient:
    """Wraps LLM calls to record duration, token usage, and cost.

    Supports both real API calls (via shared_core.llm.LLMClientFactory)
    and mock generation for testing/demos.
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
    ) -> Dict[str, Any]:
        start_time = time.time()

        if mocked_response is not None:
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
                logger.warning(
                    "LLM SDK not installed — falling back to mock mode"
                )
                time.sleep(0.05)
                text = f"Mock response for: {prompt[:50]}..."
                input_tokens = len(prompt) // 4
                output_tokens = len(text) // 4

        latency = (time.time() - start_time) * 1000.0
        cost = estimate_cost(model, input_tokens, output_tokens)

        telemetry = {
            "model": model,
            "prompt_length": len(prompt),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "latency_ms": latency,
            "timestamp": time.time(),
        }
        self.storage_callback(telemetry)
        return {"response": text, "telemetry": telemetry}

    def _call_llm(self, model: str, prompt: str, temperature: float, max_tokens: int):
        from shared_core.llm import LLMClientFactory

        factory = LLMClientFactory(
            openai_api_key=self.api_keys.get("openai"),
            anthropic_api_key=self.api_keys.get("anthropic"),
        )

        if "claude" in model.lower():
            import asyncio
            response = asyncio.run(
                factory.generate_anthropic(
                    model, prompt, temperature=temperature, max_tokens=max_tokens
                )
            )
        else:
            import asyncio
            response = asyncio.run(
                factory.generate_openai(
                    model, prompt, temperature=temperature, max_tokens=max_tokens
                )
            )

        return response.text, response.prompt_tokens, response.completion_tokens
