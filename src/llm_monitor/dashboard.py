from shared_core.llm import estimate_llm_cost

from .pricing import PRICING_MAP, estimate_cost


def generate_text_report(store) -> str:
    """Generates a terminal-friendly summary report of telemetry data."""
    aggregates = store.get_aggregates()
    lines = []
    lines.append("=" * 60)
    lines.append("  LLM COST & LATENCY REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Total Requests:      {aggregates.get('total_calls', 0)}")
    lines.append(
        f"  Total Cost (USD):    ${aggregates.get('total_cost', 0):.6f}"
    )
    lines.append(
        f"  Avg Latency (ms):    {aggregates.get('avg_latency', 0):.2f}"
    )
    lines.append(
        f"  Total Tokens:        {aggregates.get('total_tokens', 0)}"
    )
    lines.append("")

    if store.logs:
        latencies = [x["latency_ms"] for x in store.logs]
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        p95 = sorted_lat[int(n * 0.95)] if n > 0 else 0.0
        idx99 = min(int(n * 0.99), n - 1)
        p99 = sorted_lat[idx99] if n > 0 else 0.0
        lines.append(f"  P95 Latency (ms):    {p95:.2f}")
        lines.append(f"  P99 Latency (ms):    {p99:.2f}")
        lines.append("")

    by_model = {}
    for entry in store.logs:
        m = entry.get("model", "unknown")
        if m not in by_model:
            by_model[m] = {"calls": 0, "total_cost": 0.0, "total_tokens": 0}
        by_model[m]["calls"] += 1
        by_model[m]["total_cost"] += entry.get("cost_usd", 0)
        by_model[m]["total_tokens"] += (
            entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
        )

    if by_model:
        lines.append("  --- By Model ---")
        lines.append(
            f"  {'Model':<22} {'Calls':>6} {'Cost':>10} {'Tokens':>10}"
        )
        lines.append("  " + "-" * 50)
        for model, data in sorted(by_model.items()):
            lines.append(
                f"  {model:<22} {data['calls']:>6} "
                f"${data['total_cost']:>9.6f} {data['total_tokens']:>10}"
            )
        lines.append("")

    lines.append("  Supported Models (pricing available):")
    for model in sorted(PRICING_MAP.keys()):
        rates = PRICING_MAP[model]
        lines.append(
            f"    {model:<22} "
            f"in: ${rates['input_cost_per_1k']:.4f}/1k  "
            f"out: ${rates['output_cost_per_1k']:.4f}/1k"
        )
    lines.append("=" * 60)
    return "\n".join(lines)


def generate_html_dashboard(store) -> str:
    """Generates a minimal HTML dashboard page."""
    aggregates = store.get_aggregates()
    latencies = [x["latency_ms"] for x in store.logs] if store.logs else []
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    p95 = sorted_lat[int(n * 0.95)] if n > 0 else 0.0
    idx99 = min(int(n * 0.99), n - 1)
    p99 = sorted_lat[idx99] if n > 0 else 0.0

    by_model = {}
    for entry in store.logs:
        m = entry.get("model", "unknown")
        if m not in by_model:
            by_model[m] = {"calls": 0, "total_cost": 0.0, "total_tokens": 0}
        by_model[m]["calls"] += 1
        by_model[m]["total_cost"] += entry.get("cost_usd", 0)
        by_model[m]["total_tokens"] += (
            entry.get("input_tokens", 0) + entry.get("output_tokens", 0)
        )

    model_rows = ""
    for model, data in sorted(by_model.items()):
        model_rows += f"""
            <tr>
                <td>{model}</td>
                <td>{data['calls']}</td>
                <td>${data['total_cost']:.6f}</td>
                <td>{data['total_tokens']}</td>
            </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Cost & Latency Monitor</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0d1117; color: #c9d1d9; }}
        h1 {{ color: #58a6ff; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1.5rem; margin-bottom: 1rem; }}
        .metric {{ display: inline-block; margin-right: 2rem; }}
        .metric-label {{ font-size: 0.8rem; color: #8b949e; }}
        .metric-value {{ font-size: 1.5rem; font-weight: bold; color: #58a6ff; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #30363d; }}
        th {{ color: #8b949e; font-weight: 600; }}
    </style>
</head>
<body>
    <h1>LLM Cost & Latency Monitor</h1>
    <div class="card">
        <div class="metric">
            <div class="metric-label">Total Requests</div>
            <div class="metric-value">{aggregates.get('total_calls', 0)}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Total Cost</div>
            <div class="metric-value">${aggregates.get('total_cost', 0):.6f}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Avg Latency</div>
            <div class="metric-value">{aggregates.get('avg_latency', 0):.2f}ms</div>
        </div>
        <div class="metric">
            <div class="metric-label">P95 Latency</div>
            <div class="metric-value">{p95:.2f}ms</div>
        </div>
        <div class="metric">
            <div class="metric-label">P99 Latency</div>
            <div class="metric-value">{p99:.2f}ms</div>
        </div>
    </div>
    <div class="card">
        <h2>By Model</h2>
        <table>
            <thead>
                <tr><th>Model</th><th>Calls</th><th>Cost</th><th>Tokens</th></tr>
            </thead>
            <tbody>{model_rows}</tbody>
        </table>
    </div>
</body>
</html>"""
