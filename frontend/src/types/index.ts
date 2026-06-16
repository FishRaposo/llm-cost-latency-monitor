// Type definitions mirroring the FastAPI backend response shapes.
// Source of truth: src/llm_monitor/{main,storage,reports,budgets}.py and
// shared_core.llmmetrics.LLMMetrics.summary().

/** Per-model breakdown bucket from `metrics.by_model`. */
export interface ModelBreakdown {
  calls: number;
  total_cost: number;
  total_tokens: number;
}

/** Aggregate metrics returned by `GET /metrics` (store.get_aggregates()). */
export interface Metrics {
  total_calls: number;
  total_cost: number;
  total_tokens: number;
  avg_latency: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  error_rate: number;
  by_model: Record<string, ModelBreakdown>;
  cost_by_model: Record<string, number>;
  cost_by_prompt_version: Record<string, number>;
}

/** Canonical per-window summary from LLMMetrics.summary(). */
export interface MetricsSummary {
  total_requests: number;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  estimated_cost: number;
  average_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  error_rate: number;
  cost_by_model: Record<string, number>;
  cost_by_prompt_version: Record<string, number>;
}

/** Response from `GET /reports/daily` (build_daily_report()). */
export interface DailyReport {
  generated_at: string;
  days: Record<string, MetricsSummary>;
  totals?: MetricsSummary;
  day?: string;
}

/** One alert entry from `GET /budgets/alerts`. */
export interface BudgetAlert {
  type: string;
  scope: "total" | "model";
  severity: "critical" | "warning";
  message: string;
  current_value: number;
  threshold: number;
  model?: string;
}

/** Response from `GET /budgets/alerts` (evaluate_budget()). */
export interface BudgetAlertsResponse {
  threshold_usd: number;
  per_model_threshold_usd: number | null;
  total_cost: number;
  flagged: boolean;
  alerts: BudgetAlert[];
  total_alerts: number;
}

/** Request body for `POST /log` (TelemetryPayload). */
export interface TelemetryPayload {
  model: string;
  prompt_length?: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  prompt_version?: string | null;
  error?: string | null;
  timestamp?: number;
}

/** Response from `POST /log`. */
export interface LogResponse {
  status: string;
}

/** Response from `GET /health`. */
export interface HealthCheck {
  status: string;
  service: string;
  dependencies?: Record<string, string>;
}
