"use client";

// Overview: KPI cards (GET /metrics), cost/latency-over-time charts
// (GET /reports/daily), prompt-version breakdown (GET /metrics), and a
// budget-alerts summary (GET /budgets/alerts).

import { RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useSourcedData } from "@/lib/useSourcedData";
import { PageHeader } from "@/components/PageHeader";
import { DemoModeBanner } from "@/components/DemoModeBadge";
import { KpiCards } from "@/components/KpiCards";
import {
  CostOverTimeChart,
  LatencyOverTimeChart,
} from "@/components/TimeSeriesCharts";
import { PromptVersionBreakdown } from "@/components/PromptVersionBreakdown";
import { BudgetAlertsPanel } from "@/components/BudgetAlertsPanel";
import {
  KpiGridSkeleton,
  ChartSkeleton,
} from "@/components/LoadingSkeleton";
import { ErrorState } from "@/components/StateViews";

export default function OverviewPage() {
  const metrics = useSourcedData(() => apiClient.getMetrics());
  const report = useSourcedData(() => apiClient.getDailyReport());
  const budgets = useSourcedData(() =>
    apiClient.getBudgetAlerts({ thresholdUsd: 10, perModelThresholdUsd: 25 })
  );

  // The page is in demo mode if any underlying call fell back to demo data.
  const source =
    metrics.source === "demo" ||
    report.source === "demo" ||
    budgets.source === "demo"
      ? "demo"
      : "live";

  function reloadAll() {
    metrics.reload();
    report.reload();
    budgets.reload();
  }

  return (
    <div>
      <PageHeader
        title="Overview"
        subtitle="Aggregate cost, latency and error metrics across all LLM calls."
        source={metrics.loading ? undefined : source}
        actions={
          <button
            onClick={reloadAll}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        }
      />

      {!metrics.loading && <DemoModeBanner source={source} />}

      <div className="mt-6 space-y-6">
        <section aria-label="Key metrics">
          {metrics.loading ? (
            <KpiGridSkeleton />
          ) : metrics.error || !metrics.data ? (
            <ErrorState
              message={metrics.error ?? "No metrics available."}
              onRetry={metrics.reload}
            />
          ) : (
            <KpiCards metrics={metrics.data} />
          )}
        </section>

        <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {report.loading ? (
            <>
              <ChartSkeleton />
              <ChartSkeleton />
            </>
          ) : report.error || !report.data ? (
            <div className="lg:col-span-2">
              <ErrorState
                message={report.error ?? "No report data available."}
                onRetry={report.reload}
              />
            </div>
          ) : (
            <>
              <CostOverTimeChart report={report.data} />
              <LatencyOverTimeChart report={report.data} />
            </>
          )}
        </section>

        <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {metrics.loading || !metrics.data ? (
            <ChartSkeleton height={180} />
          ) : (
            <PromptVersionBreakdown metrics={metrics.data} />
          )}
          {budgets.loading ? (
            <ChartSkeleton height={180} />
          ) : budgets.error || !budgets.data ? (
            <ErrorState
              message={budgets.error ?? "No budget data available."}
              onRetry={budgets.reload}
            />
          ) : (
            <BudgetAlertsPanel data={budgets.data} />
          )}
        </section>
      </div>
    </div>
  );
}
