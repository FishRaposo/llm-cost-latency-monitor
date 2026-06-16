// Typed API client for the LLM Cost & Latency Monitor backend.
//
// DEMO MODE: every read defaults to the live FastAPI backend and transparently
// falls back to bundled mock data (src/lib/mockData.ts) on any network/parse
// error. Each call returns `{ data, source }` where `source` is "live" or
// "demo" so the UI can surface a visible "Demo mode" indicator.

import type {
  Metrics,
  DailyReport,
  BudgetAlertsResponse,
  TelemetryPayload,
  LogResponse,
  HealthCheck,
} from "@/types";
import {
  mockMetrics,
  mockDailyReport,
  mockBudgetAlerts,
  mockHealth,
} from "@/lib/mockData";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type DataSource = "live" | "demo";

/** A data payload tagged with where it came from (live backend vs demo data). */
export interface Sourced<T> {
  data: T;
  source: DataSource;
}

const DEFAULT_TIMEOUT_MS = 6000;

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {},
    timeoutMs: number = DEFAULT_TIMEOUT_MS
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      });

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `API error: ${response.status}`);
      }

      return (await response.json()) as T;
    } finally {
      clearTimeout(timer);
    }
  }

  /**
   * Run a live request, falling back to bundled demo data on any error so the
   * UI is fully explorable offline. Returns the data tagged with its source.
   */
  private async withFallback<T>(
    live: () => Promise<T>,
    fallback: T
  ): Promise<Sourced<T>> {
    try {
      const data = await live();
      return { data, source: "live" };
    } catch {
      return { data: fallback, source: "demo" };
    }
  }

  /** GET /metrics — aggregate cost/latency/error metrics. */
  async getMetrics(): Promise<Sourced<Metrics>> {
    return this.withFallback(
      () => this.request<Metrics>("/metrics"),
      mockMetrics
    );
  }

  /** GET /reports/daily — per-day rollup of telemetry. */
  async getDailyReport(day?: string): Promise<Sourced<DailyReport>> {
    const qs = day ? `?day=${encodeURIComponent(day)}` : "";
    return this.withFallback(
      () => this.request<DailyReport>(`/reports/daily${qs}`),
      mockDailyReport
    );
  }

  /** GET /budgets/alerts — spend evaluated against budget thresholds. */
  async getBudgetAlerts(opts?: {
    thresholdUsd?: number;
    perModelThresholdUsd?: number;
  }): Promise<Sourced<BudgetAlertsResponse>> {
    const params = new URLSearchParams();
    if (opts?.thresholdUsd !== undefined) {
      params.set("threshold_usd", String(opts.thresholdUsd));
    }
    if (opts?.perModelThresholdUsd !== undefined) {
      params.set("per_model_threshold_usd", String(opts.perModelThresholdUsd));
    }
    const qs = params.toString() ? `?${params.toString()}` : "";
    return this.withFallback(
      () => this.request<BudgetAlertsResponse>(`/budgets/alerts${qs}`),
      mockBudgetAlerts
    );
  }

  /** GET /health — service + dependency status. */
  async getHealth(): Promise<Sourced<HealthCheck>> {
    return this.withFallback(
      () => this.request<HealthCheck>("/health"),
      mockHealth
    );
  }

  /**
   * POST /log — ingest one telemetry record. Unlike the read calls this is a
   * write, so a failure is surfaced as a thrown error rather than silently
   * faked; callers handle demo-mode messaging in the form UI.
   */
  async logTelemetry(payload: TelemetryPayload): Promise<LogResponse> {
    return this.request<LogResponse>("/log", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
}

export const apiClient = new ApiClient(API_BASE);
