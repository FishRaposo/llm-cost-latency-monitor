// Small presentation helpers shared across dashboard views.

/** Format a USD amount. Uses more precision for tiny costs. */
export function formatCurrency(value: number): string {
  if (!isFinite(value)) return "$0.00";
  if (value !== 0 && Math.abs(value) < 0.01) {
    return `$${value.toFixed(6)}`;
  }
  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/** Format an integer count with thousands separators. */
export function formatNumber(value: number): string {
  if (!isFinite(value)) return "0";
  return Math.round(value).toLocaleString();
}

/** Format a latency in milliseconds. */
export function formatLatency(ms: number): string {
  if (!isFinite(ms)) return "0 ms";
  return `${ms.toLocaleString(undefined, { maximumFractionDigits: 0 })} ms`;
}

/** Format a 0..1 error rate as a percentage. */
export function formatPercent(rate: number, digits = 2): string {
  if (!isFinite(rate)) return "0%";
  return `${(rate * 100).toFixed(digits)}%`;
}

/** Compact token counts (e.g. 9.2M, 3.1k). */
export function formatTokens(value: number): string {
  if (!isFinite(value)) return "0";
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}k`;
  return String(Math.round(value));
}
