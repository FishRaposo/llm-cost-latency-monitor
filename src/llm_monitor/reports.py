"""Daily report generation (JSON + CSV).

Builds a per-day rollup of LLM telemetry — request counts, cost, latency
percentiles, error rate, and per-model breakdown — from any store exposing
``logs`` and ``get_aggregates``. Used by the ``/reports/daily`` endpoint and the
Celery ``generate_daily_report`` task. Pure-Python and offline-friendly.
"""

import csv
import io
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from shared_core.llmmetrics import LLMMetrics


def _day_key(ts: Optional[float]) -> str:
    """Map a unix timestamp to a UTC YYYY-MM-DD bucket (default: today)."""
    if ts is None:
        dt = datetime.now(timezone.utc)
    else:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def build_daily_report(store, day: Optional[str] = None) -> Dict[str, Any]:
    """Build a daily report dict.

    Args:
        store: a telemetry store with a ``logs`` list of telemetry dicts.
        day: optional ``YYYY-MM-DD`` filter (UTC). When ``None``, every day
            present in the data is rolled up and a ``totals`` block is added.

    Returns:
        ``{"generated_at", "days": {day: {...}}, "totals": {...}}``.
    """
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in store.logs:
        key = _day_key(entry.get("timestamp"))
        if day is not None and key != day:
            continue
        buckets[key].append(entry)

    days: Dict[str, Any] = {}
    for key, entries in sorted(buckets.items()):
        metrics = LLMMetrics()
        for e in entries:
            metrics.record(
                model=e.get("model", "unknown"),
                prompt_tokens=int(e.get("input_tokens", 0)),
                completion_tokens=int(e.get("output_tokens", 0)),
                latency_ms=float(e.get("latency_ms", 0.0)),
                prompt_version=e.get("prompt_version"),
                error=e.get("error"),
                cost_usd=e.get("cost_usd"),
            )
        days[key] = metrics.summary()

    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
    }

    if day is None:
        all_metrics = LLMMetrics()
        for entry in store.logs:
            all_metrics.record(
                model=entry.get("model", "unknown"),
                prompt_tokens=int(entry.get("input_tokens", 0)),
                completion_tokens=int(entry.get("output_tokens", 0)),
                latency_ms=float(entry.get("latency_ms", 0.0)),
                prompt_version=entry.get("prompt_version"),
                error=entry.get("error"),
                cost_usd=entry.get("cost_usd"),
            )
        report["totals"] = all_metrics.summary()
    else:
        report["day"] = day

    return report


def report_to_csv(report: Dict[str, Any]) -> str:
    """Render a daily report's per-day rows as CSV text."""
    output = io.StringIO()
    fieldnames = [
        "day",
        "total_requests",
        "total_tokens",
        "input_tokens",
        "output_tokens",
        "estimated_cost",
        "average_latency_ms",
        "p50_latency_ms",
        "p95_latency_ms",
        "p99_latency_ms",
        "error_rate",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for day, summary in sorted(report.get("days", {}).items()):
        row = {"day": day}
        for field in fieldnames[1:]:
            row[field] = summary.get(field, 0)
        writer.writerow(row)
    return output.getvalue()
