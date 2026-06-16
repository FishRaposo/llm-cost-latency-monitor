"use client";

// Log a call: a demo form that POSTs telemetry to /log, alongside a live
// preview of the current aggregate metrics (GET /metrics) that refreshes on
// each successful submission.

import { apiClient } from "@/lib/api";
import { useSourcedData } from "@/lib/useSourcedData";
import { PageHeader } from "@/components/PageHeader";
import { DemoModeBanner } from "@/components/DemoModeBadge";
import { LogCallForm } from "@/components/LogCallForm";
import { KpiCards } from "@/components/KpiCards";
import { KpiGridSkeleton } from "@/components/LoadingSkeleton";
import { ErrorState } from "@/components/StateViews";

export default function LogPage() {
  const metrics = useSourcedData(() => apiClient.getMetrics());
  const source = metrics.source ?? "live";

  return (
    <div>
      <PageHeader
        title="Log a call"
        subtitle="Send a telemetry record to the backend and watch the metrics update."
        source={metrics.loading ? undefined : source}
      />

      {!metrics.loading && <DemoModeBanner source={source} />}

      <div className="mt-6 space-y-6">
        <LogCallForm onLogged={metrics.reload} />

        <section aria-label="Current metrics">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">
            Current metrics
          </h2>
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
      </div>
    </div>
  );
}
