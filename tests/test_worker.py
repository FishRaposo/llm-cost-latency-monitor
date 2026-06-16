"""Tests for the Celery worker — importable without a broker, real tasks."""

from unittest.mock import patch

from llm_monitor import worker
from llm_monitor.storage import InMemoryTelemetryStore


def test_celery_app_importable_without_broker():
    assert worker.celery_app is not None
    assert "llm_monitor.generate_daily_report" in worker.celery_app.tasks
    assert "llm_monitor.check_budget" in worker.celery_app.tasks


def test_daily_report_helper():
    store = InMemoryTelemetryStore()
    store.log_request(
        {
            "model": "gpt-4o",
            "prompt_length": 10,
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.001,
            "latency_ms": 50.0,
            "prompt_version": "v1",
        }
    )
    result = worker._daily_report(store)
    assert "report" in result
    assert "csv" in result
    assert result["report"]["totals"]["total_requests"] == 1
    assert result["csv"].startswith("day,total_requests")


def test_generate_daily_report_task_runs_eagerly():
    store = InMemoryTelemetryStore()
    store.log_request(
        {
            "model": "gpt-4o",
            "prompt_length": 10,
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.002,
            "latency_ms": 60.0,
        }
    )
    with patch.object(worker, "_resolve_store", return_value=store):
        # Call the task function body directly (no broker needed).
        out = worker.generate_daily_report.run()
    assert out["report"]["totals"]["total_requests"] == 1


def test_check_budget_task_flags_overrun():
    store = InMemoryTelemetryStore()
    store.log_request(
        {
            "model": "gpt-4",
            "prompt_length": 10,
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 5.0,
            "latency_ms": 60.0,
        }
    )
    with patch.object(worker, "_resolve_store", return_value=store):
        out = worker.check_budget.run(threshold_usd=1.0)
    assert out["flagged"] is True
    assert out["total_alerts"] >= 1


def test_check_budget_task_no_overrun():
    store = InMemoryTelemetryStore()
    store.log_request(
        {
            "model": "gpt-4",
            "prompt_length": 10,
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.01,
            "latency_ms": 60.0,
        }
    )
    with patch.object(worker, "_resolve_store", return_value=store):
        out = worker.check_budget.run(threshold_usd=100.0)
    assert out["flagged"] is False
