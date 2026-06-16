from shared_core.database import Base, TimestampMixin, UUIDMixin
from sqlalchemy import Column, Float, Integer, String


class LLMCall(Base, UUIDMixin, TimestampMixin):
    """A single recorded LLM invocation persisted to the database."""

    __tablename__ = "llm_calls"

    model = Column(String(100), nullable=False, index=True)
    prompt_length = Column(Integer, nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False, default=0.0)
    latency_ms = Column(Float, nullable=False)
    prompt_version = Column(String(100), nullable=True, index=True)
    error = Column(String(500), nullable=True)
