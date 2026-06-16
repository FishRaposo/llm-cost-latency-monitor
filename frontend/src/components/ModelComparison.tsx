"use client";

// Model-comparison table + cost bar chart from GET /metrics (by_model / cost_by_model).

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import type { Metrics } from "@/types";
import {
  formatCurrency,
  formatNumber,
  formatTokens,
} from "@/lib/format";
import { EmptyState } from "@/components/StateViews";

const BAR_COLORS = ["#4c6ef5", "#22c55e", "#a855f7", "#f59e0b", "#06b6d4", "#ef4444"];

export interface ModelRow {
  model: string;
  calls: number;
  cost: number;
  tokens: number;
  costPerCall: number;
}

export function toModelRows(metrics: Metrics): ModelRow[] {
  return Object.entries(metrics.by_model)
    .map(([model, b]) => ({
      model,
      calls: b.calls,
      cost: b.total_cost,
      tokens: b.total_tokens,
      costPerCall: b.calls > 0 ? b.total_cost / b.calls : 0,
    }))
    .sort((a, b) => b.cost - a.cost);
}

export function ModelComparison({ metrics }: { metrics: Metrics }) {
  const rows = toModelRows(metrics);

  if (rows.length === 0) {
    return (
      <EmptyState
        title="No model data"
        message="Once calls are logged, per-model cost and usage appears here."
      />
    );
  }

  return (
    <div className="card" data-testid="model-comparison">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">
        Model comparison
      </h3>
      <p className="mb-4 text-xs text-gray-400">Cost and usage by model</p>

      <div style={{ width: "100%", height: 240 }}>
        <ResponsiveContainer>
          <BarChart
            data={rows}
            margin={{ top: 8, right: 12, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#eef0f4" />
            <XAxis
              dataKey="model"
              tick={{ fontSize: 11, fill: "#6b7280" }}
              interval={0}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6b7280" }}
              tickFormatter={(v: number) => `$${v}`}
            />
            <Tooltip
              formatter={(v: number) => [formatCurrency(Number(v)), "Cost"]}
            />
            <Bar dataKey="cost" radius={[4, 4, 0, 0]}>
              {rows.map((_, i) => (
                <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-5 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-xs uppercase tracking-wide text-gray-500">
              <th className="py-2 pr-4 font-medium">Model</th>
              <th className="py-2 pr-4 text-right font-medium">Calls</th>
              <th className="py-2 pr-4 text-right font-medium">Cost</th>
              <th className="py-2 pr-4 text-right font-medium">Tokens</th>
              <th className="py-2 text-right font-medium">Cost / call</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={row.model}
                className="border-b border-gray-100 last:border-0"
                data-testid="model-row"
              >
                <td className="py-2 pr-4">
                  <span className="inline-flex items-center gap-2">
                    <span
                      className="inline-block h-2.5 w-2.5 rounded-full"
                      style={{
                        backgroundColor: BAR_COLORS[i % BAR_COLORS.length],
                      }}
                    />
                    <span className="font-medium text-gray-800">
                      {row.model}
                    </span>
                  </span>
                </td>
                <td className="py-2 pr-4 text-right text-gray-600">
                  {formatNumber(row.calls)}
                </td>
                <td className="py-2 pr-4 text-right font-medium text-gray-900">
                  {formatCurrency(row.cost)}
                </td>
                <td className="py-2 pr-4 text-right text-gray-600">
                  {formatTokens(row.tokens)}
                </td>
                <td className="py-2 text-right text-gray-600">
                  {formatCurrency(row.costPerCall)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
