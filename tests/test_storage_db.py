from unittest.mock import MagicMock

import pytest
from llm_monitor.storage_db import DatabaseTelemetryStore


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = []
    return session


@pytest.fixture
def mock_session_factory(mock_session):
    def factory():
        yield mock_session

    return factory


@pytest.fixture
def store(mock_session_factory):
    return DatabaseTelemetryStore(mock_session_factory)


class TestDatabaseTelemetryStore:
    def test_log_request_commits(self, store, mock_session):
        store.log_request({
            "model": "gpt-4",
            "prompt_length": 100,
            "input_tokens": 25,
            "output_tokens": 50,
            "cost_usd": 0.003,
            "latency_ms": 200.0,
        })
        mock_session.commit.assert_called_once()

    def test_log_request_rolls_back_on_error(self, store, mock_session):
        mock_session.commit.side_effect = Exception("DB write error")
        with pytest.raises(Exception, match="DB write error"):
            store.log_request({"model": "gpt-4", "prompt_length": 10, "input_tokens": 2, "output_tokens": 3, "cost_usd": 0.0, "latency_ms": 10.0})
        mock_session.rollback.assert_called_once()

    def test_get_aggregates_empty(self, store, mock_session):
        mock_session.query.return_value.scalar.return_value = 0
        result = store.get_aggregates()
        assert result["total_calls"] == 0
        assert result["total_cost"] == 0.0
        assert result["avg_latency"] == 0.0

    def test_get_aggregates_with_data(self, store, mock_session):
        from unittest.mock import MagicMock

        call_counts = {"count": 0}

        def mock_scalar():
            call_counts["count"] += 1
            idx = call_counts["count"]
            if idx == 1:
                return 5
            elif idx == 2:
                return 0.025
            elif idx == 3:
                return 150.0
            return 0

        mock_scalar_mock = MagicMock()
        mock_scalar_mock.scalar = mock_scalar

        mock_groupby = MagicMock()
        mock_groupby.group_by.return_value.all.return_value = [
            ("gpt-4", 5, 0.025, 200)
        ]

        mock_orderby = MagicMock()
        mock_orderby.order_by.return_value.all.return_value = [
            (100.0,), (150.0,), (200.0,),
        ]

        def query_side_effect(*args, **kwargs):
            idx = mock_session.query.call_count
            if idx <= 3:
                return mock_scalar_mock
            elif idx == 4:
                return mock_groupby
            else:
                return mock_orderby

        mock_session.query.side_effect = query_side_effect
        mock_session.query.call_count = 0

        result = store.get_aggregates()
        assert result["total_calls"] == 5
        assert "gpt-4" in result["by_model"]
