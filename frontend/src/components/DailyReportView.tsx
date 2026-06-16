// Daily-report table from GET /reports/daily.

import type { DailyReport } from "@/types";
import {
  formatCurrency,
  formatLatency,
  formatNumber,
  formatPercent,
  formatTokens,
} from "@/lib/format";
import { EmptyState } from "@/components/StateViews";

export function DailyReportView({ report }: { report: DailyReport }) {
  const rows = Object.entries(report.days).sort(([a], [b]) =>
    b.localeCompare(a)
  );

  return (
    <div className="card" data-testid="daily-report">
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">Daily report</h3>
          <p className="text-xs text-gray-400">
            Generated {new Date(report.generated_at).toLocaleString()}
          </p>
        </div>
        {report.totals && (
          <p className="text-xs text-gray-500">
            <span className="font-medium text-gray-700">All-time:</span>{" "}
            {formatNumber(report.totals.total_requests)} requests ·{" "}
            {formatCurrency(report.totals.estimated_cost)} ·{" "}
            {formatPercent(report.totals.error_rate)} errors
          </p>
        )}
      </div>

      {rows.length === 0 ? (
        <EmptyState
          title="No days to report"
          message="No telemetry has been recorded for any day yet."
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-xs uppercase tracking-wide text-gray-500">
                <th className="py-2 pr-4 font-medium">Day</th>
                <th className="py-2 pr-4 text-right font-medium">Requests</th>
                <th className="py-2 pr-4 text-right font-medium">Tokens</th>
                <th className="py-2 pr-4 text-right font-medium">Cost</th>
                <th className="py-2 pr-4 text-right font-medium">Avg</th>
                <th className="py-2 pr-4 text-right font-medium">p95</th>
                <th className="py-2 pr-4 text-right font-medium">p99</th>
                <th className="py-2 text-right font-medium">Errors</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(([day, s]) => (
                <tr
                  key={day}
                  className="border-b border-gray-100 last:border-0"
                  data-testid="daily-row"
                >
                  <td className="py-2 pr-4 font-medium text-gray-800">{day}</td>
                  <td className="py-2 pr-4 text-right text-gray-600">
                    {formatNumber(s.total_requests)}
                  </td>
                  <td className="py-2 pr-4 text-right text-gray-600">
                    {formatTokens(s.total_tokens)}
                  </td>
                  <td className="py-2 pr-4 text-right font-medium text-gray-900">
                    {formatCurrency(s.estimated_cost)}
                  </td>
                  <td className="py-2 pr-4 text-right text-gray-600">
                    {formatLatency(s.average_latency_ms)}
                  </td>
                  <td className="py-2 pr-4 text-right text-gray-600">
                    {formatLatency(s.p95_latency_ms)}
                  </td>
                  <td className="py-2 pr-4 text-right text-gray-600">
                    {formatLatency(s.p99_latency_ms)}
                  </td>
                  <td
                    className={`py-2 text-right font-medium ${
                      s.error_rate > 0.05 ? "text-red-600" : "text-gray-600"
                    }`}
                  >
                    {formatPercent(s.error_rate)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
