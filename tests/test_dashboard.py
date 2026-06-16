"""Tests for the text and HTML dashboard renderers.

Focus on output safety: the HTML dashboard is server-rendered and interpolates
the user-controlled ``model`` string, so it must HTML-escape that value to
prevent stored XSS.
"""

from llm_monitor.dashboard import generate_html_dashboard, generate_text_report
from llm_monitor.storage import InMemoryTelemetryStore


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


def test_html_dashboard_escapes_model_script_tag():
    """A model name containing a <script> tag must be escaped, not injected."""
    store = InMemoryTelemetryStore()
    store.log_request(_payload(model="<script>alert('xss')</script>"))

    html_out = generate_html_dashboard(store)

    # The raw script tag must not appear verbatim in the rendered HTML.
    assert "<script>alert('xss')</script>" not in html_out
    # The escaped form must be present in the model cell instead.
    assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" in html_out


def test_html_dashboard_renders_plain_model():
    store = InMemoryTelemetryStore()
    store.log_request(_payload(model="gpt-4"))

    html_out = generate_html_dashboard(store)

    assert "<td>gpt-4</td>" in html_out
    assert html_out.startswith("<!DOCTYPE html>")


def test_text_report_renders():
    store = InMemoryTelemetryStore()
    store.log_request(_payload())

    report = generate_text_report(store)

    assert "LLM COST & LATENCY REPORT" in report
    assert "gpt-4" in report
