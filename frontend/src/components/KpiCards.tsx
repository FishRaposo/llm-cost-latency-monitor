// KPI cards summarising the aggregate metrics from GET /metrics.

import {
  Activity,
  DollarSign,
  Gauge,
  Timer,
  TimerReset,
  AlertCircle,
  type LucideIcon,
} from "lucide-react";
import type { Metrics } from "@/types";
import {
  formatCurrency,
  formatLatency,
  formatNumber,
  formatPercent,
} from "@/lib/format";

interface Kpi {
  label: string;
  value: string;
  hint: string;
  icon: LucideIcon;
  accent: string;
  danger?: boolean;
}

export function buildKpis(metrics: Metrics): Kpi[] {
  const errorBad = metrics.error_rate > 0.05;
  return [
    {
      label: "Total requests",
      value: formatNumber(metrics.total_calls),
      hint: `${formatNumber(metrics.total_tokens)} tokens`,
      icon: Activity,
      accent: "text-brand-600 bg-brand-50",
    },
    {
      label: "Total cost",
      value: formatCurrency(metrics.total_cost),
      hint: `${Object.keys(metrics.cost_by_model).length} models`,
      icon: DollarSign,
      accent: "text-emerald-600 bg-emerald-50",
    },
    {
      label: "Avg latency",
      value: formatLatency(metrics.avg_latency),
      hint: `p50 ${formatLatency(metrics.p50_latency_ms)}`,
      icon: Gauge,
      accent: "text-indigo-600 bg-indigo-50",
    },
    {
      label: "p95 latency",
      value: formatLatency(metrics.p95_latency_ms),
      hint: "95th percentile",
      icon: Timer,
      accent: "text-amber-600 bg-amber-50",
    },
    {
      label: "p99 latency",
      value: formatLatency(metrics.p99_latency_ms),
      hint: "99th percentile",
      icon: TimerReset,
      accent: "text-purple-600 bg-purple-50",
    },
    {
      label: "Error rate",
      value: formatPercent(metrics.error_rate),
      hint: errorBad ? "above 5% threshold" : "within threshold",
      icon: AlertCircle,
      accent: errorBad
        ? "text-red-600 bg-red-50"
        : "text-gray-600 bg-gray-100",
      danger: errorBad,
    },
  ];
}

function KpiCard({ kpi }: { kpi: Kpi }) {
  return (
    <div className="card flex items-start justify-between" data-testid="kpi-card">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
          {kpi.label}
        </p>
        <p
          className={`mt-1 text-2xl font-semibold ${
            kpi.danger ? "text-red-600" : "text-gray-900"
          }`}
        >
          {kpi.value}
        </p>
        <p className="mt-1 text-xs text-gray-400">{kpi.hint}</p>
      </div>
      <span className={`rounded-lg p-2 ${kpi.accent}`}>
        <kpi.icon className="h-5 w-5" />
      </span>
    </div>
  );
}

export function KpiCards({ metrics }: { metrics: Metrics }) {
  const kpis = buildKpis(metrics);
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {kpis.map((kpi) => (
        <KpiCard key={kpi.label} kpi={kpi} />
      ))}
    </div>
  );
}
