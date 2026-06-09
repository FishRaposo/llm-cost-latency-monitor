from llm_monitor.pricing import estimate_cost
from llm_monitor.sdk import MonitoredLLMClient


def test_generate_mock_mode():
    logs = []

    def store_log(data):
        logs.append(data)

    client = MonitoredLLMClient(store_log)
    result = client.generate(
        "gpt-4",
        "Test prompt",
        mocked_response="Test response",
    )

    assert result["response"] == "Test response"
    assert len(logs) == 1
    assert logs[0]["model"] == "gpt-4"
    assert logs[0]["input_tokens"] > 0
    assert logs[0]["output_tokens"] > 0
    assert logs[0]["cost_usd"] > 0
    assert logs[0]["latency_ms"] > 0


def test_generate_telemetry_has_all_fields():
    logs = []

    client = MonitoredLLMClient(logs.append)
    result = client.generate("gpt-4", "prompt", mocked_response="response")

    telemetry = result["telemetry"]
    assert "model" in telemetry
    assert "input_tokens" in telemetry
    assert "output_tokens" in telemetry
    assert "cost_usd" in telemetry
    assert "latency_ms" in telemetry
    assert "timestamp" in telemetry
    assert "prompt_length" in telemetry


def test_generate_cost_matches_pricing():
    logs = []

    client = MonitoredLLMClient(logs.append)
    result = client.generate(
        "gpt-4o-mini", "short", mocked_response="short"
    )

    expected_cost = estimate_cost(
        "gpt-4o-mini",
        len("short") // 4,
        len("short") // 4,
    )
    assert result["telemetry"]["cost_usd"] == expected_cost
