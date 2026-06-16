// Budget-alerts panel from GET /budgets/alerts.

import type { BudgetAlertsResponse } from "@/types";
import { formatCurrency } from "@/lib/format";
import { ShieldCheck, ShieldAlert, AlertTriangle } from "lucide-react";

export function BudgetAlertsPanel({ data }: { data: BudgetAlertsResponse }) {
  const ok = !data.flagged;

  return (
    <div className="card" data-testid="budget-panel">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">Budget alerts</h3>
          <p className="text-xs text-gray-400">
            Total spend {formatCurrency(data.total_cost)} vs budget{" "}
            {formatCurrency(data.threshold_usd)}
            {data.per_model_threshold_usd != null && (
              <>
                {" "}
                · per-model {formatCurrency(data.per_model_threshold_usd)}
              </>
            )}
          </p>
        </div>
        {ok ? (
          <span
            className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700"
            data-testid="budget-status-ok"
          >
            <ShieldCheck className="h-3.5 w-3.5" />
            Within budget
          </span>
        ) : (
          <span
            className="inline-flex items-center gap-1.5 rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700"
            data-testid="budget-status-flagged"
          >
            <ShieldAlert className="h-3.5 w-3.5" />
            {data.total_alerts} alert{data.total_alerts === 1 ? "" : "s"}
          </span>
        )}
      </div>

      {ok ? (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          <ShieldCheck className="h-4 w-4 shrink-0" />
          Spend is within all configured budget thresholds.
        </div>
      ) : (
        <ul className="space-y-2">
          {data.alerts.map((alert, i) => {
            const critical = alert.severity === "critical";
            return (
              <li
                key={i}
                data-testid="budget-alert"
                className={`flex items-start gap-2 rounded-lg border px-4 py-3 text-sm ${
                  critical
                    ? "border-red-200 bg-red-50 text-red-700"
                    : "border-amber-200 bg-amber-50 text-amber-800"
                }`}
              >
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs font-semibold uppercase ${
                        critical
                          ? "bg-red-100 text-red-700"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
                      {alert.scope}
                      {alert.model ? ` · ${alert.model}` : ""}
                    </span>
                  </div>
                  <p className="mt-1">{alert.message}</p>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
