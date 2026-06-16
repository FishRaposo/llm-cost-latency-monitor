"use client";

// Models: model-comparison table + bar chart and prompt-version breakdown,
// both from GET /metrics.

import { RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useSourcedData } from "@/lib/useSourcedData";
import { PageHeader } from "@/components/PageHeader";
import { DemoModeBanner } from "@/components/DemoModeBadge";
import { ModelComparison } from "@/components/ModelComparison";
import { PromptVersionBreakdown } from "@/components/PromptVersionBreakdown";
import { ChartSkeleton, TableSkeleton } from "@/components/LoadingSkeleton";
import { ErrorState } from "@/components/StateViews";

export default function ModelsPage() {
  const metrics = useSourcedData(() => apiClient.getMetrics());
  const source = metrics.source ?? "live";

  return (
    <div>
      <PageHeader
        title="Models"
        subtitle="Compare cost, usage and efficiency across models and prompt versions."
        source={metrics.loading ? undefined : source}
        actions={
          <button
            onClick={metrics.reload}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        }
      />

      {!metrics.loading && <DemoModeBanner source={source} />}

      <div className="mt-6 space-y-6">
        {metrics.loading ? (
          <>
            <ChartSkeleton />
            <TableSkeleton />
          </>
        ) : metrics.error || !metrics.data ? (
          <ErrorState
            message={metrics.error ?? "No metrics available."}
            onRetry={metrics.reload}
          />
        ) : (
          <>
            <ModelComparison metrics={metrics.data} />
            <PromptVersionBreakdown metrics={metrics.data} />
          </>
        )}
      </div>
    </div>
  );
}
