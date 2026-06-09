from unittest.mock import MagicMock, patch

from llm_monitor.storage import InMemoryTelemetryStore


def _make_client():
    mock_db = MagicMock()
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    fresh_store = InMemoryTelemetryStore()

    with (
        patch("llm_monitor.main.db_manager", mock_db),
        patch("llm_monitor.main.redis_manager", mock_redis),
        patch("llm_monitor.main.store", fresh_store),
    ):
        from fastapi.testclient import TestClient

        from llm_monitor.main import app

        with TestClient(app) as client:
            yield client


def test_log_telemetry_valid():
    gen = _make_client()
    client = next(gen)
    try:
        payload = {
            "model": "gpt-4",
            "prompt_length": 100,
            "input_tokens": 25,
            "output_tokens": 30,
            "cost_usd": 0.05,
            "latency_ms": 150.0,
        }
        response = client.post("/log", json=payload)
        assert response.status_code == 200
        assert response.json() == {"status": "logged"}
    finally:
        gen.close()


def test_log_telemetry_invalid():
    gen = _make_client()
    client = next(gen)
    try:
        response = client.post("/log", json={"model": "gpt-4"})
        assert response.status_code == 422
    finally:
        gen.close()


def test_metrics_endpoint():
    gen = _make_client()
    client = next(gen)
    try:
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_calls" in data
        assert "total_cost" in data
        assert "avg_latency" in data
        assert "by_model" in data
    finally:
        gen.close()


def test_metrics_with_data():
    gen = _make_client()
    client = next(gen)
    try:
        client.post("/log", json={
            "model": "gpt-4",
            "prompt_length": 100,
            "input_tokens": 25,
            "output_tokens": 30,
            "cost_usd": 0.05,
            "latency_ms": 150.0,
        })
        client.post("/log", json={
            "model": "gpt-3.5-turbo",
            "prompt_length": 50,
            "input_tokens": 10,
            "output_tokens": 20,
            "cost_usd": 0.01,
            "latency_ms": 80.0,
        })
        response = client.get("/metrics")
        data = response.json()
        assert data["total_calls"] == 2
        assert data["total_cost"] == 0.06
        assert "gpt-4" in data["by_model"]
        assert "gpt-3.5-turbo" in data["by_model"]
    finally:
        gen.close()
