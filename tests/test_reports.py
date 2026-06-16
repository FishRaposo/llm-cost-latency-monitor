"""Tests for the daily report generator (JSON + CSV)."""

import time
from datetime import datetime, timezone

from llm_monitor.reports import build_daily_report, report_to_csv
from llm_monitor.storage import InMemoryTelemetryStore


def _seed(store, n=3, ts=None):
    for i in range(n):
        store.log_request(
            {
                "model": "gpt-4o",
                "prompt_length": 10,
                "input_tokens": 10,
                "output_tokens": 5,
                "cost_usd": 0.001,
                "latency_ms": 50.0 + i,
                "prompt_version": "v1",
                "error": None,
                "timestamp": ts if ts is not None else time.time(),
            }
        )


def test_build_daily_report_has_totals():
    store = InMemoryTelemetryStore()
    _seed(store, 3)
    report = build_daily_report(store)
    assert "generated_at" in report
    assert "days" in report
    assert "totals" in report
    assert report["totals"]["total_requests"] == 3


def test_build_daily_report_buckets_by_day():
    store = InMemoryTelemetryStore()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    _seed(store, 2)
    report = build_daily_report(store)
    assert today in report["days"]
    assert report["days"][today]["total_requests"] == 2


def test_build_daily_report_day_filter():
    store = InMemoryTelemetryStore()
    # One record on a fixed historical day.
    old_ts = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    store.log_request(
        {
            "model": "gpt-4o",
            "prompt_length": 10,
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.001,
            "latency_ms": 50.0,
            "timestamp": old_ts,
        }
    )
    _seed(store, 2)  # today
    report = build_daily_report(store, day="2020-01-01")
    assert report["day"] == "2020-01-01"
    assert list(report["days"].keys()) == ["2020-01-01"]
    assert report["days"]["2020-01-01"]["total_requests"] == 1


def test_report_to_csv_has_header_and_rows():
    store = InMemoryTelemetryStore()
    _seed(store, 2)
    csv_text = report_to_csv(build_daily_report(store))
    lines = csv_text.strip().splitlines()
    assert lines[0].startswith("day,total_requests")
    assert len(lines) == 2  # header + one day


def test_report_empty_store():
    store = InMemoryTelemetryStore()
    report = build_daily_report(store)
    assert report["days"] == {}
    assert report["totals"]["total_requests"] == 0
    csv_text = report_to_csv(report)
    assert csv_text.strip().startswith("day,total_requests")
