"use client";

// Cost-over-time and latency-over-time charts built from GET /reports/daily.

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import type { DailyReport } from "@/types";
import { EmptyState } from "@/components/StateViews";

export interface DailyPoint {
  day: string;
  cost: number;
  requests: number;
  avgLatency: number;
  p95: number;
  p99: number;
}

/** Flatten the daily report's `days` map into a sorted series for charting. */
export function toDailySeries(report: DailyReport): DailyPoint[] {
  return Object.entries(report.days)
    .map(([day, s]) => ({
      day,
      cost: Number(s.estimated_cost.toFixed(4)),
      requests: s.total_requests,
      avgLatency: s.average_latency_ms,
      p95: s.p95_latency_ms,
      p99: s.p99_latency_ms,
    }))
    .sort((a, b) => a.day.localeCompare(b.day));
}

function shortDay(day: string): string {
  // YYYY-MM-DD -> MM-DD
  return day.length >= 10 ? day.slice(5) : day;
}

export function CostOverTimeChart({ report }: { report: DailyReport }) {
  const data = toDailySeries(report);
  if (data.length === 0) {
    return (
      <EmptyState
        title="No cost history"
        message="Log some calls to see cost trends over time."
      />
    );
  }
  return (
    <div className="card" data-testid="cost-chart">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">
        Cost over time
      </h3>
      <p className="mb-4 text-xs text-gray-400">Estimated USD spend per day</p>
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer>
          <AreaChart
            data={data}
            margin={{ top: 8, right: 12, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="costFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4c6ef5" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#4c6ef5" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#eef0f4" />
            <XAxis
              dataKey="day"
              tickFormatter={shortDay}
              tick={{ fontSize: 12, fill: "#6b7280" }}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#6b7280" }}
              tickFormatter={(v: number) => `$${v}`}
            />
            <Tooltip
              formatter={(v: number) => [`$${Number(v).toFixed(4)}`, "Cost"]}
            />
            <Area
              type="monotone"
              dataKey="cost"
              stroke="#4c6ef5"
              strokeWidth={2}
              fill="url(#costFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function LatencyOverTimeChart({ report }: { report: DailyReport }) {
  const data = toDailySeries(report);
  if (data.length === 0) {
    return (
      <EmptyState
        title="No latency history"
        message="Log some calls to see latency trends over time."
      />
    );
  }
  return (
    <div className="card" data-testid="latency-chart">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">
        Latency over time
      </h3>
      <p className="mb-4 text-xs text-gray-400">
        Average, p95 and p99 latency per day (ms)
      </p>
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer>
          <LineChart
            data={data}
            margin={{ top: 8, right: 12, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#eef0f4" />
            <XAxis
              dataKey="day"
              tickFormatter={shortDay}
              tick={{ fontSize: 12, fill: "#6b7280" }}
            />
            <YAxis tick={{ fontSize: 12, fill: "#6b7280" }} />
            <Tooltip
              formatter={(v: number, name: string) => [
                `${Number(v).toFixed(0)} ms`,
                name,
              ]}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line
              type="monotone"
              dataKey="avgLatency"
              name="avg"
              stroke="#4c6ef5"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="p95"
              name="p95"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="p99"
              name="p99"
              stroke="#a855f7"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
