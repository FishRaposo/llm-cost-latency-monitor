// Prompt-version cost breakdown from GET /metrics (cost_by_prompt_version).

import type { Metrics } from "@/types";
import { formatCurrency, formatPercent } from "@/lib/format";
import { EmptyState } from "@/components/StateViews";
import { GitBranch } from "lucide-react";

export interface VersionRow {
  version: string;
  cost: number;
  share: number;
}

export function toVersionRows(metrics: Metrics): VersionRow[] {
  const entries = Object.entries(metrics.cost_by_prompt_version);
  const total = entries.reduce((sum, [, c]) => sum + c, 0);
  return entries
    .map(([version, cost]) => ({
      version,
      cost,
      share: total > 0 ? cost / total : 0,
    }))
    .sort((a, b) => b.cost - a.cost);
}

export function PromptVersionBreakdown({ metrics }: { metrics: Metrics }) {
  const rows = toVersionRows(metrics);

  if (rows.length === 0) {
    return (
      <EmptyState
        title="No prompt versions"
        message="Tag calls with a prompt_version to compare spend across versions."
        icon={<GitBranch className="h-9 w-9" />}
      />
    );
  }

  return (
    <div className="card" data-testid="prompt-version-breakdown">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">
        Prompt-version breakdown
      </h3>
      <p className="mb-4 text-xs text-gray-400">Cost share by prompt version</p>
      <ul className="space-y-3">
        {rows.map((row) => (
          <li key={row.version} data-testid="version-row">
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="inline-flex items-center gap-1.5 font-medium text-gray-800">
                <GitBranch className="h-3.5 w-3.5 text-gray-400" />
                {row.version}
              </span>
              <span className="text-gray-600">
                {formatCurrency(row.cost)}{" "}
                <span className="text-xs text-gray-400">
                  ({formatPercent(row.share, 1)})
                </span>
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
              <div
                className="h-full rounded-full bg-brand-500"
                style={{ width: `${Math.max(row.share * 100, 1)}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
