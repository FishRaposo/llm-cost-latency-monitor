import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { KpiCards, buildKpis } from "@/components/KpiCards";
import { mockMetrics } from "@/lib/mockData";
import { formatCurrency, formatNumber } from "@/lib/format";

describe("KpiCards", () => {
  it("renders all six KPI cards with formatted values", () => {
    render(<KpiCards metrics={mockMetrics} />);
    expect(screen.getAllByTestId("kpi-card")).toHaveLength(6);
    expect(screen.getByText("Total requests")).toBeInTheDocument();
    // Use the same formatters the component uses so assertions are locale-stable.
    expect(
      screen.getByText(formatNumber(mockMetrics.total_calls))
    ).toBeInTheDocument();
    expect(
      screen.getByText(formatCurrency(mockMetrics.total_cost))
    ).toBeInTheDocument();
    expect(screen.getByText("Error rate")).toBeInTheDocument();
  });

  it("flags an error rate above 5% as danger", () => {
    const kpis = buildKpis({ ...mockMetrics, error_rate: 0.12 });
    const errorKpi = kpis.find((k) => k.label === "Error rate");
    expect(errorKpi?.danger).toBe(true);
    expect(errorKpi?.value).toBe("12.00%");
  });

  it("does not flag an error rate within threshold", () => {
    const kpis = buildKpis({ ...mockMetrics, error_rate: 0.01 });
    const errorKpi = kpis.find((k) => k.label === "Error rate");
    expect(errorKpi?.danger).toBeFalsy();
  });
});
