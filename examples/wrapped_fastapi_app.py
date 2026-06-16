"""Integration example: a FastAPI app whose LLM endpoint is monitored.

Shows how an application embeds ``MonitoredLLMClient`` so every LLM call is
automatically metered (cost, latency, tokens, prompt version, errors) into a
shared telemetry store, and exposes its own ``/metrics`` and ``/report``
endpoints. Runs fully offline using ``mocked_response``; set OPENAI_API_KEY /
ANTHROPIC_API_KEY and drop ``mocked_response`` to hit real providers.

Run directly to execute a self-contained smoke flow with the FastAPI TestClient
(no server, no network):

    python examples/wrapped_fastapi_app.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from fastapi import FastAPI  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from llm_monitor.budgets import evaluate_budget  # noqa: E402
from llm_monitor.reports import build_daily_report  # noqa: E402
from llm_monitor.sdk import MonitoredLLMClient  # noqa: E402
from llm_monitor.storage import InMemoryTelemetryStore  # noqa: E402

app = FastAPI(title="example-wrapped-app")
store = InMemoryTelemetryStore()
api_keys = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
}
client = MonitoredLLMClient(store.log_request, api_keys=api_keys)


class ChatRequest(BaseModel):
    model: str = "gpt-4o-mini"
    prompt: str
    prompt_version: str = "v1"
    # Offline default; omit in production so the real provider path runs.
    mocked_response: str | None = "This is a simulated completion."


@app.post("/chat")
def chat(req: ChatRequest):
    """Answer a prompt while transparently recording telemetry."""
    result = client.generate(
        model=req.model,
        prompt=req.prompt,
        mocked_response=req.mocked_response,
        prompt_version=req.prompt_version,
    )
    return result


@app.get("/metrics")
def metrics():
    """Expose the aggregate metrics collected by this app."""
    return store.get_aggregates()


@app.get("/report")
def report():
    """Expose the daily cost/latency report for this app."""
    return build_daily_report(store)


@app.get("/budget")
def budget(threshold_usd: float = 1.0):
    """Evaluate this app's spend against a USD budget."""
    return evaluate_budget(store, threshold_usd=threshold_usd)


def _smoke() -> int:
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        for i in range(3):
            resp = c.post(
                "/chat",
                json={"prompt": f"Question {i}", "prompt_version": "v1"},
            )
            assert resp.status_code == 200, resp.text
        metrics_resp = c.get("/metrics").json()
        assert metrics_resp["total_calls"] == 3
        print("wrapped_fastapi_app: 3 monitored calls, metrics:")
        print(f"  total_cost=${metrics_resp['total_cost']:.6f}")
        print(f"  avg_latency={metrics_resp['avg_latency']:.2f}ms")
        budget_resp = c.get("/budget", params={"threshold_usd": 0.0}).json()
        assert budget_resp["flagged"] is True
        print(f"  budget flagged: {budget_resp['flagged']}")
    print("wrapped_fastapi_app smoke complete.")
    return 0


if __name__ == "__main__":
    sys.exit(_smoke())
