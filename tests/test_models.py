from llm_monitor.models import LLMCall


class TestLLMCallModel:
    def test_tablename(self):
        assert LLMCall.__tablename__ == "llm_calls"

    def test_columns_present(self):
        assert hasattr(LLMCall, "model")
        assert hasattr(LLMCall, "prompt_length")
        assert hasattr(LLMCall, "input_tokens")
        assert hasattr(LLMCall, "output_tokens")
        assert hasattr(LLMCall, "cost_usd")
        assert hasattr(LLMCall, "latency_ms")
        assert hasattr(LLMCall, "id")
        assert hasattr(LLMCall, "created_at")
        assert hasattr(LLMCall, "updated_at")

    def test_model_is_indexed(self):
        col = LLMCall.__table__.columns["model"]
        assert col.index is True

    def test_cost_usd_default(self):
        col = LLMCall.__table__.columns["cost_usd"]
        assert col.default.arg == 0.0

    def test_columns_not_nullable(self):
        assert LLMCall.__table__.columns["model"].nullable is False
        assert LLMCall.__table__.columns["prompt_length"].nullable is False
        assert LLMCall.__table__.columns["input_tokens"].nullable is False
        assert LLMCall.__table__.columns["output_tokens"].nullable is False
        assert LLMCall.__table__.columns["latency_ms"].nullable is False
