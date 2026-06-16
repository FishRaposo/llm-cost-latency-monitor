"""Tests for the database availability probe and store selection."""

from unittest.mock import MagicMock, patch

from shared_core.database import DatabaseManager

from llm_monitor import db as db_module
from llm_monitor.storage import InMemoryTelemetryStore
from llm_monitor.storage_db import DatabaseTelemetryStore


def test_check_db_returns_false_when_driver_missing(monkeypatch):
    """When the manager cannot be built, probe must degrade gracefully."""
    monkeypatch.setattr(db_module, "db_manager", None)

    def boom_get_manager():
        raise ImportError("No module named 'psycopg'")

    monkeypatch.setattr(db_module, "_get_manager", boom_get_manager)
    assert db_module.check_db() is False
    assert db_module.db_available is False


def test_check_db_true_with_sqlite(monkeypatch):
    mgr = DatabaseManager("sqlite:///:memory:")
    monkeypatch.setattr(db_module, "db_manager", mgr)
    monkeypatch.setattr(db_module, "_get_manager", lambda: mgr)
    assert db_module.check_db() is True
    assert db_module.db_available is True


def test_build_store_in_memory_when_unavailable(monkeypatch):
    monkeypatch.setattr(db_module, "db_available", False)
    store = db_module.build_store()
    assert isinstance(store, InMemoryTelemetryStore)


def test_build_store_db_when_available(monkeypatch):
    mgr = DatabaseManager("sqlite:///:memory:")
    mgr.create_tables()
    monkeypatch.setattr(db_module, "db_available", True)
    monkeypatch.setattr(db_module, "db_manager", mgr)
    store = db_module.build_store()
    assert isinstance(store, DatabaseTelemetryStore)


def test_build_store_uses_provided_fallback(monkeypatch):
    monkeypatch.setattr(db_module, "db_available", False)
    fallback = InMemoryTelemetryStore()
    fallback.log_request(
        {
            "model": "gpt-4",
            "prompt_length": 1,
            "input_tokens": 1,
            "output_tokens": 1,
            "cost_usd": 0.0,
            "latency_ms": 1.0,
        }
    )
    store = db_module.build_store(in_memory_fallback=fallback)
    assert store is fallback


def test_check_db_handles_query_failure(monkeypatch):
    mgr = MagicMock()
    mgr.SessionLocal.side_effect = RuntimeError("connection refused")
    monkeypatch.setattr(db_module, "db_manager", mgr)
    monkeypatch.setattr(db_module, "_get_manager", lambda: mgr)
    with patch("llm_monitor.db.text"):
        assert db_module.check_db() is False
