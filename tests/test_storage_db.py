"""Tests for the SQLAlchemy-backed telemetry store using in-memory SQLite.

A real SQLite engine exercises the persistence path end-to-end (commit, query,
aggregation) without a Postgres server, so persistence is genuinely verified
rather than mocked.
"""

import pytest
from shared_core.database import DatabaseManager

from llm_monitor.storage_db import DatabaseTelemetryStore


@pytest.fixture
def db_manager():
    mgr = DatabaseManager("sqlite:///:memory:")
    mgr.create_tables()
    return mgr


@pytest.fixture
def store(db_manager):
    return DatabaseTelemetryStore(db_manager.get_session)


def _payload(**overrides):
    base = {
        "model": "gpt-4",
        "prompt_length": 40,
        "input_tokens": 10,
        "output_tokens": 20,
        "cost_usd": 0.0006,
        "latency_ms": 120.0,
        "prompt_version": "v1",
        "error": None,
    }
    base.update(overrides)
    return base


class TestDatabaseTelemetryStore:
    def test_log_request_persists(self, store):
        store.log_request(_payload())
        agg = store.get_aggregates()
        assert agg["total_calls"] == 1
        assert agg["total_cost"] == pytest.approx(0.0006)

    def test_get_aggregates_empty(self, store):
        agg = store.get_aggregates()
        assert agg["total_calls"] == 0
        assert agg["total_cost"] == 0.0
        assert agg["avg_latency"] == 0.0
        assert agg["by_model"] == {}

    def test_by_model_breakdown(self, store):
        store.log_request(_payload(model="gpt-4"))
        store.log_request(_payload(model="gpt-3.5-turbo", cost_usd=0.0001))
        agg = store.get_aggregates()
        assert agg["total_calls"] == 2
        assert "gpt-4" in agg["by_model"]
        assert "gpt-3.5-turbo" in agg["by_model"]
        assert agg["by_model"]["gpt-4"]["calls"] == 1

    def test_error_rate_tracked(self, store):
        store.log_request(_payload())
        store.log_request(_payload(error="TimeoutError: boom"))
        agg = store.get_aggregates()
        assert agg["error_rate"] == 0.5

    def test_prompt_version_cost_breakdown(self, store):
        store.log_request(_payload(prompt_version="v1"))
        store.log_request(_payload(prompt_version="v2", cost_usd=0.0009))
        agg = store.get_aggregates()
        assert set(agg["cost_by_prompt_version"]) == {"v1", "v2"}

    def test_logs_property_roundtrip(self, store):
        store.log_request(_payload(model="claude-3-haiku"))
        logs = store.logs
        assert len(logs) == 1
        assert logs[0]["model"] == "claude-3-haiku"
        assert logs[0]["prompt_version"] == "v1"

    def test_summary_has_percentiles(self, store):
        for latency in (50.0, 100.0, 150.0, 200.0):
            store.log_request(_payload(latency_ms=latency))
        summary = store.summary()
        assert summary["total_requests"] == 4
        assert summary["p95_latency_ms"] > 0
        assert summary["p99_latency_ms"] > 0

    def test_session_factory_generator_is_cleaned_up(self):
        """The factory generator's finally/close must run deterministically.

        Regression: ``_session()`` previously did ``next(factory())`` and
        abandoned the generator, leaving its cleanup to the GC. Driving it via
        ``contextlib.closing`` must run the generator's ``finally`` block.
        """

        class TrackingSession:
            def __init__(self):
                self.closed = False

            def query(self, *a, **k):
                raise AssertionError("not used in this test")

            def add(self, *a):
                pass

            def commit(self):
                pass

            def rollback(self):
                pass

            def close(self):
                self.closed = True

        session = TrackingSession()
        finally_ran = {"value": False}

        def factory():
            try:
                yield session
            finally:
                finally_ran["value"] = True

        store = DatabaseTelemetryStore(factory)
        store.log_request(_payload())

        assert finally_ran["value"] is True
        assert session.closed is True

    def test_rollback_on_bad_session(self):
        class BoomSession:
            def add(self, *a):
                pass

            def commit(self):
                raise RuntimeError("db write error")

            def rollback(self):
                self.rolled_back = True

            def close(self):
                pass

        boom = BoomSession()

        def factory():
            yield boom

        store = DatabaseTelemetryStore(factory)
        with pytest.raises(RuntimeError, match="db write error"):
            store.log_request(_payload())
        assert getattr(boom, "rolled_back", False) is True
