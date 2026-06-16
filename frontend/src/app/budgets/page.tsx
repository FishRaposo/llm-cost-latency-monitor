"use client";

// Budgets: tunable total + per-model thresholds, evaluated against spend via
// GET /budgets/alerts.

import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useSourcedData } from "@/lib/useSourcedData";
import { PageHeader } from "@/components/PageHeader";
import { DemoModeBanner } from "@/components/DemoModeBadge";
import { BudgetAlertsPanel } from "@/components/BudgetAlertsPanel";
import { ChartSkeleton } from "@/components/LoadingSkeleton";
import { ErrorState } from "@/components/StateViews";

export default function BudgetsPage() {
  const [totalBudget, setTotalBudget] = useState(10);
  const [perModelBudget, setPerModelBudget] = useState(25);

  const budgets = useSourcedData(
    () =>
      apiClient.getBudgetAlerts({
        thresholdUsd: totalBudget,
        perModelThresholdUsd: perModelBudget,
      }),
    [totalBudget, perModelBudget]
  );
  const source = budgets.source ?? "live";

  return (
    <div>
      <PageHeader
        title="Budgets"
        subtitle="Evaluate spend against total and per-model USD thresholds."
        source={budgets.loading ? undefined : source}
        actions={
          <button
            onClick={budgets.reload}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        }
      />

      {!budgets.loading && <DemoModeBanner source={source} />}

      <div className="mt-6 space-y-6">
        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-gray-800">
            Thresholds
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-gray-600">
                Total budget (USD)
              </span>
              <input
                type="number"
                min={0}
                step="0.5"
                value={totalBudget}
                onChange={(e) => setTotalBudget(Number(e.target.value))}
                className="input"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-gray-600">
                Per-model budget (USD)
              </span>
              <input
                type="number"
                min={0}
                step="0.5"
                value={perModelBudget}
                onChange={(e) => setPerModelBudget(Number(e.target.value))}
                className="input"
              />
            </label>
          </div>
        </div>

        {budgets.loading ? (
          <ChartSkeleton height={160} />
        ) : budgets.error || !budgets.data ? (
          <ErrorState
            message={budgets.error ?? "No budget data available."}
            onRetry={budgets.reload}
          />
        ) : (
          <BudgetAlertsPanel data={budgets.data} />
        )}
      </div>
    </div>
  );
}
