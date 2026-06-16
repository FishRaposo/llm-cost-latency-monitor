"use client";

// Daily report: time-series charts + per-day table from GET /reports/daily,
// with an optional day filter passed through to the backend.

import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useSourcedData } from "@/lib/useSourcedData";
import { PageHeader } from "@/components/PageHeader";
import { DemoModeBanner } from "@/components/DemoModeBadge";
import {
  CostOverTimeChart,
  LatencyOverTimeChart,
} from "@/components/TimeSeriesCharts";
import { DailyReportView } from "@/components/DailyReportView";
import { ChartSkeleton, TableSkeleton } from "@/components/LoadingSkeleton";
import { ErrorState } from "@/components/StateViews";

export default function ReportsPage() {
  const [day, setDay] = useState<string>("");
  const report = useSourcedData(
    () => apiClient.getDailyReport(day || undefined),
    [day]
  );
  const source = report.source ?? "live";

  return (
    <div>
      <PageHeader
        title="Daily report"
        subtitle="Per-day rollup of requests, cost, latency percentiles and error rate."
        source={report.loading ? undefined : source}
        actions={
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={day}
              onChange={(e) => setDay(e.target.value)}
              className="input w-auto"
              aria-label="Filter by day"
            />
            <button
              onClick={report.reload}
              className="btn-secondary inline-flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>
        }
      />

      {!report.loading && <DemoModeBanner source={source} />}

      <div className="mt-6 space-y-6">
        {report.loading ? (
          <>
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <ChartSkeleton />
              <ChartSkeleton />
            </div>
            <TableSkeleton rows={6} />
          </>
        ) : report.error || !report.data ? (
          <ErrorState
            message={report.error ?? "No report data available."}
            onRetry={report.reload}
          />
        ) : (
          <>
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <CostOverTimeChart report={report.data} />
              <LatencyOverTimeChart report={report.data} />
            </div>
            <DailyReportView report={report.data} />
          </>
        )}
      </div>
    </div>
  );
}
