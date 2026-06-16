"""API tests covering every endpoint, success and error paths.

Uses the FastAPI TestClient with the database and Redis managers mocked, and a
fresh in-memory store, so nothing touches a network or a real database.
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from llm_monitor.storage import InMemoryTelemetryStore


@contextmanager
def make_client():
    mock_db = MagicMock()
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    fresh_store = InMemoryTelemetryStore()

    import llm_monitor.main as main_module

    with (
        patch.object(main_module, "db_manager", mock_db),
        patch.object(main_module, "redis_manager", mock_redis),
        patch.object(main_module, "store", fresh_store),
        # Prevent lifespan from probing a real DB / replacing the store.
        patch("llm_monitor.db.check_db", return_value=False),
    ):
        # Disable DB swap in lifespan.
        with patch("llm_monitor.db.db_available", False):
            with TestClient(main_module.app) as client:
                yield client


def _payload(**overrides):
    base = {
        "model": "gpt-4",
        "prompt_length": 100,
        "input_tokens": 25,
        "output_tokens": 30,
        "cost_usd": 0.05,
        "latency_ms": 150.0,
        "prompt_version": "v1",
    }
    base.update(overrides)
    return base


# --- /log -----------------------------------------------------------------


def test_log_valid():
    with make_client() as client:
        resp = client.post("/log", json=_payload())
        assert resp.status_code == 200
        assert resp.json() == {"status": "logged"}


def test_log_invalid_missing_fields():
    with make_client() as client:
        resp = client.post("/log", json={"model": "gpt-4"})
        assert resp.status_code == 422


def test_log_invalid_negative_tokens():
    with make_client() as client:
        resp = client.post("/log", json=_payload(input_tokens=-5))
        assert resp.status_code == 422


# --- /metrics -------------------------------------------------------------


def test_metrics_empty():
    with make_client() as client:
        resp = client.get("/metrics")
        assert resp.status_code == 200
        data = resp.json()
        for key in (
            "total_calls",
            "total_cost",
            "avg_latency",
            "by_model",
            "error_rate",
            "p95_latency_ms",
            "cost_by_prompt_version",
        ):
            assert key in data
        assert data["total_calls"] == 0


def test_metrics_with_data():
    with make_client() as client:
        client.post("/log", json=_payload(model="gpt-4", cost_usd=0.05))
        client.post("/log", json=_payload(model="gpt-3.5-turbo", cost_usd=0.01))
        data = client.get("/metrics").json()
        assert data["total_calls"] == 2
        assert data["total_cost"] == 0.06
        assert "gpt-4" in data["by_model"]
        assert "gpt-3.5-turbo" in data["by_model"]


# --- /metrics/prometheus --------------------------------------------------


def test_prometheus_metrics():
    with make_client() as client:
        client.get("/metrics")  # generate at least one request metric
        resp = client.get("/metrics/prometheus")
        assert resp.status_code == 200
        assert "http_requests_total" in resp.text


# --- /reports/daily -------------------------------------------------------


def test_reports_daily_json():
    with make_client() as client:
        client.post("/log", json=_payload())
        resp = client.get("/reports/daily")
        assert resp.status_code == 200
        data = resp.json()
        assert "days" in data
        assert "totals" in data
        assert data["totals"]["total_requests"] == 1


def test_reports_daily_csv():
    with make_client() as client:
        client.post("/log", json=_payload())
        resp = client.get("/reports/daily", params={"format": "csv"})
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert "day,total_requests" in resp.text


def test_reports_daily_empty():
    with make_client() as client:
        resp = client.get("/reports/daily")
        assert resp.status_code == 200
        assert resp.json()["totals"]["total_requests"] == 0


# --- /budgets/alerts ------------------------------------------------------


def test_budget_alerts_no_overrun():
    with make_client() as client:
        client.post("/log", json=_payload(cost_usd=0.001))
        resp = client.get("/budgets/alerts", params={"threshold_usd": 100.0})
        assert resp.status_code == 200
        assert resp.json()["flagged"] is False


def test_budget_alerts_overrun():
    with make_client() as client:
        client.post("/log", json=_payload(cost_usd=5.0))
        resp = client.get("/budgets/alerts", params={"threshold_usd": 1.0})
        assert resp.status_code == 200
        body = resp.json()
        assert body["flagged"] is True
        assert body["total_alerts"] >= 1


def test_budget_alerts_uses_config_default():
    with make_client() as client:
        client.post("/log", json=_payload(cost_usd=0.001))
        resp = client.get("/budgets/alerts")
        assert resp.status_code == 200
        assert "threshold_usd" in resp.json()


# --- /health --------------------------------------------------------------


def test_health_endpoint():
    with make_client() as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["service"] == "llm-cost-latency-monitor"
        assert "dependencies" in body


# --- /dashboard -----------------------------------------------------------


@pytest.mark.parametrize("fmt", ["json", "text", "html"])
def test_dashboard_formats(fmt):
    with make_client() as client:
        client.post("/log", json=_payload())
        resp = client.get("/dashboard", params={"format": fmt})
        assert resp.status_code == 200
