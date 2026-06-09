from llm_monitor.sdk import MonitoredLLMClient
from llm_monitor.storage import InMemoryTelemetryStore


class TestSDKErrorHandling:
    def test_falls_back_to_mock_on_import_error(self, monkeypatch):
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "shared_core.llm":
                raise ImportError("No shared_core.llm")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        store = InMemoryTelemetryStore()
        client = MonitoredLLMClient(storage_callback=store.log_request)
        result = client.generate(
            model="gpt-4",
            prompt="Test prompt",
            mocked_response=None,
        )
        assert "response" in result
        assert "Mock response" in result["response"]
        assert len(store.logs) == 1

    def test_mocked_response_bypasses_real_call(self):
        store = InMemoryTelemetryStore()
        client = MonitoredLLMClient(storage_callback=store.log_request)
        result = client.generate(
            model="claude-3-opus",
            prompt="Hello",
            mocked_response="Hi there!",
        )
        assert result["response"] == "Hi there!"
        assert result["telemetry"]["input_tokens"] >= 0
        assert result["telemetry"]["output_tokens"] >= 0
        assert result["telemetry"]["cost_usd"] >= 0

    def test_telemetry_fields_present(self):
        store = InMemoryTelemetryStore()
        client = MonitoredLLMClient(storage_callback=store.log_request)
        result = client.generate(
            model="gpt-3.5-turbo",
            prompt="What is 2+2?",
            mocked_response="4",
        )
        telemetry = result["telemetry"]
        for field in ["model", "prompt_length", "input_tokens", "output_tokens", "cost_usd", "latency_ms", "timestamp"]:
            assert field in telemetry, f"Missing field: {field}"

    def test_cost_is_nonzero_for_known_model(self):
        store = InMemoryTelemetryStore()
        client = MonitoredLLMClient(storage_callback=store.log_request)
        result = client.generate(
            model="gpt-4",
            prompt="Long prompt " * 50,
            mocked_response="Long response " * 50,
        )
        assert result["telemetry"]["cost_usd"] > 0

    def test_empty_prompt_handled(self):
        store = InMemoryTelemetryStore()
        client = MonitoredLLMClient(storage_callback=store.log_request)
        result = client.generate(
            model="gpt-4",
            prompt="",
            mocked_response="response",
        )
        assert result["telemetry"]["input_tokens"] == 0

    def test_storage_callback_receives_telemetry(self):
        store = InMemoryTelemetryStore()
        client = MonitoredLLMClient(storage_callback=store.log_request)
        client.generate(model="gpt-4", prompt="test", mocked_response="ok")
        assert len(store.logs) == 1
        assert store.logs[0]["model"] == "gpt-4"
