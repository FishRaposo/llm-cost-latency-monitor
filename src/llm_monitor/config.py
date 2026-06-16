from shared_core.config import BaseAppConfig


class AppConfig(BaseAppConfig):
    """Project-specific configuration extending the shared core settings."""

    APP_NAME: str = "llm-cost-latency-monitor"

    # USD budget threshold used by /budgets/alerts and the daily report task.
    BUDGET_THRESHOLD_USD: float = 10.0
    # Optional per-model USD budget; None disables per-model alerting by default.
    BUDGET_PER_MODEL_THRESHOLD_USD: float | None = None
