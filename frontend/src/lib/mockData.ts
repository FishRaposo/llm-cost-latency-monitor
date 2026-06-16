// Bundled demo data so every view is fully explorable with no backend running.
// Shapes match the FastAPI responses exactly (see src/types). The dashboard
// defaults to the live API and falls back to these fixtures on any fetch error.

import type {
  Metrics,
  DailyReport,
  BudgetAlertsResponse,
  MetricsSummary,
  HealthCheck,
} from "@/types";

export const mockMetrics: Metrics = {
  total_calls: 18432,
  total_cost: 47.8231,
  total_tokens: 9_214_770,
  avg_latency: 842.51,
  p50_latency_ms: 712.34,
  p95_latency_ms: 1984.12,
  p99_latency_ms: 3120.88,
  error_rate: 0.0231,
  by_model: {
    "gpt-4o": { calls: 5120, total_cost: 28.4412, total_tokens: 3_842_110 },
    "gpt-4o-mini": { calls: 8240, total_cost: 6.1203, total_tokens: 3_120_440 },
    "claude-3-5-sonnet": {
      calls: 3180,
      total_cost: 11.2014,
      total_tokens: 1_780_220,
    },
    "claude-3-haiku": { calls: 1892, total_cost: 2.0602, total_tokens: 472_000 },
  },
  cost_by_model: {
    "gpt-4o": 28.4412,
    "gpt-4o-mini": 6.1203,
    "claude-3-5-sonnet": 11.2014,
    "claude-3-haiku": 2.0602,
  },
  cost_by_prompt_version: {
    "v3-summarize": 21.3401,
    "v2-summarize": 9.812,
    "v1-classify": 8.4407,
    unversioned: 8.2303,
  },
};

function summaryFor(
  totalRequests: number,
  cost: number,
  avgLatency: number,
  p50: number,
  p95: number,
  p99: number,
  errorRate: number,
  costByModel: Record<string, number>,
  costByVersion: Record<string, number>
): MetricsSummary {
  const inputTokens = Math.round(totalRequests * 280);
  const outputTokens = Math.round(totalRequests * 220);
  return {
    total_requests: totalRequests,
    total_tokens: inputTokens + outputTokens,
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    estimated_cost: cost,
    average_latency_ms: avgLatency,
    p50_latency_ms: p50,
    p95_latency_ms: p95,
    p99_latency_ms: p99,
    error_rate: errorRate,
    cost_by_model: costByModel,
    cost_by_prompt_version: costByVersion,
  };
}

// Seven days of rollups. Keys are UTC YYYY-MM-DD, ascending.
const days: Record<string, MetricsSummary> = {
  "2026-06-09": summaryFor(
    2210,
    5.4122,
    810.2,
    690.0,
    1820.4,
    2901.0,
    0.018,
    { "gpt-4o": 3.21, "gpt-4o-mini": 0.84, "claude-3-5-sonnet": 1.12, "claude-3-haiku": 0.24 },
    { "v3-summarize": 2.4, "v2-summarize": 1.3, "v1-classify": 1.0, unversioned: 0.71 }
  ),
  "2026-06-10": summaryFor(
    2540,
    6.1203,
    824.6,
    705.1,
    1901.2,
    2988.4,
    0.021,
    { "gpt-4o": 3.74, "gpt-4o-mini": 0.91, "claude-3-5-sonnet": 1.18, "claude-3-haiku": 0.29 },
    { "v3-summarize": 2.81, "v2-summarize": 1.42, "v1-classify": 1.1, unversioned: 0.79 }
  ),
  "2026-06-11": summaryFor(
    2680,
    7.0021,
    901.4,
    742.0,
    2104.7,
    3402.1,
    0.029,
    { "gpt-4o": 4.32, "gpt-4o-mini": 1.02, "claude-3-5-sonnet": 1.36, "claude-3-haiku": 0.3 },
    { "v3-summarize": 3.2, "v2-summarize": 1.6, "v1-classify": 1.3, unversioned: 0.9 }
  ),
  "2026-06-12": summaryFor(
    2890,
    7.4412,
    878.9,
    731.4,
    2010.3,
    3198.6,
    0.024,
    { "gpt-4o": 4.61, "gpt-4o-mini": 1.08, "claude-3-5-sonnet": 1.42, "claude-3-haiku": 0.33 },
    { "v3-summarize": 3.41, "v2-summarize": 1.71, "v1-classify": 1.38, unversioned: 0.94 }
  ),
  "2026-06-13": summaryFor(
    2410,
    6.2204,
    792.1,
    668.2,
    1788.0,
    2854.9,
    0.017,
    { "gpt-4o": 3.78, "gpt-4o-mini": 0.86, "claude-3-5-sonnet": 1.24, "claude-3-haiku": 0.34 },
    { "v3-summarize": 2.9, "v2-summarize": 1.32, "v1-classify": 1.1, unversioned: 0.9 }
  ),
  "2026-06-14": summaryFor(
    2602,
    6.8801,
    851.7,
    718.5,
    1960.4,
    3088.2,
    0.026,
    { "gpt-4o": 4.18, "gpt-4o-mini": 0.95, "claude-3-5-sonnet": 1.4, "claude-3-haiku": 0.35 },
    { "v3-summarize": 3.12, "v2-summarize": 1.5, "v1-classify": 1.34, unversioned: 0.92 }
  ),
  "2026-06-15": summaryFor(
    1100,
    2.7468,
    836.0,
    705.9,
    1944.2,
    3070.0,
    0.022,
    { "gpt-4o": 1.84, "gpt-4o-mini": 0.41, "claude-3-5-sonnet": 0.48, "claude-3-haiku": 0.21 },
    { "v3-summarize": 1.46, "v2-summarize": 0.6, "v1-classify": 0.4, unversioned: 0.29 }
  ),
};

export const mockDailyReport: DailyReport = {
  generated_at: "2026-06-15T14:02:11.482000+00:00",
  days,
  totals: summaryFor(
    16432,
    41.8231,
    842.51,
    712.34,
    1984.12,
    3120.88,
    0.0231,
    mockMetrics.cost_by_model,
    mockMetrics.cost_by_prompt_version
  ),
};

export const mockBudgetAlerts: BudgetAlertsResponse = {
  threshold_usd: 10.0,
  per_model_threshold_usd: 25.0,
  total_cost: 47.8231,
  flagged: true,
  alerts: [
    {
      type: "budget_overrun",
      scope: "total",
      severity: "critical",
      message: "Total spend $47.823100 exceeds budget $10.000000.",
      current_value: 47.8231,
      threshold: 10.0,
    },
    {
      type: "budget_overrun",
      scope: "model",
      model: "gpt-4o",
      severity: "warning",
      message:
        "Model 'gpt-4o' spend $28.441200 exceeds per-model budget $25.000000.",
      current_value: 28.4412,
      threshold: 25.0,
    },
  ],
  total_alerts: 2,
};

export const mockHealth: HealthCheck = {
  status: "degraded",
  service: "llm-cost-latency-monitor",
  dependencies: { database: "offline", redis: "offline" },
};
