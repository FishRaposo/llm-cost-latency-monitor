"""Celery worker with real domain tasks.

Built via ``shared_core.tasks.create_celery_app`` and importable without a
running broker (the broker URL is only contacted when a worker actually starts
or a task is dispatched). Tasks operate on the active telemetry store, mirroring
the ``/reports/daily`` and ``/budgets/alerts`` endpoints so report generation
and budget evaluation can run asynchronously on a schedule.
"""

from typing import Any, Dict, Optional

from shared_core.tasks import create_celery_app

from .budgets import evaluate_budget
from .config import AppConfig
from .reports import build_daily_report, report_to_csv

config = AppConfig()
celery_app = create_celery_app(
    config.APP_NAME,
    broker_url=config.CELERY_BROKER_URL,
    backend_url=config.CELERY_RESULT_BACKEND,
)


def _resolve_store():
    """Return the active store: DB-backed when available, else in-memory."""
    from . import db as db_module

    db_module.check_db()
    return db_module.build_store()


def _daily_report(store, day: Optional[str] = None) -> Dict[str, Any]:
    """Pure helper: build a daily report dict plus its CSV rendering."""
    report = build_daily_report(store, day=day)
    return {"report": report, "csv": report_to_csv(report)}


@celery_app.task(name="llm_monitor.generate_daily_report")
def generate_daily_report(day: Optional[str] = None) -> Dict[str, Any]:
    """Generate the daily cost/latency report (JSON + CSV) from the active store."""
    store = _resolve_store()
    return _daily_report(store, day=day)


@celery_app.task(name="llm_monitor.check_budget")
def check_budget(
    threshold_usd: Optional[float] = None,
    per_model_threshold_usd: Optional[float] = None,
) -> Dict[str, Any]:
    """Evaluate current spend against the budget and return any alerts."""
    store = _resolve_store()
    total_budget = (
        config.BUDGET_THRESHOLD_USD if threshold_usd is None else threshold_usd
    )
    per_model_budget = (
        config.BUDGET_PER_MODEL_THRESHOLD_USD
        if per_model_threshold_usd is None
        else per_model_threshold_usd
    )
    return evaluate_budget(
        store,
        threshold_usd=total_budget,
        per_model_threshold_usd=per_model_budget,
    )
