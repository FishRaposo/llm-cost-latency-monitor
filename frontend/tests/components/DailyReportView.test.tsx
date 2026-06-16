import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DailyReportView } from "@/components/DailyReportView";
import { toDailySeries } from "@/components/TimeSeriesCharts";
import { mockDailyReport } from "@/lib/mockData";
import type { DailyReport } from "@/types";

describe("DailyReportView", () => {
  it("renders one row per day in the report", () => {
    render(<DailyReportView report={mockDailyReport} />);
    expect(screen.getAllByTestId("daily-row")).toHaveLength(
      Object.keys(mockDailyReport.days).length
    );
  });

  it("shows the all-time totals summary", () => {
    render(<DailyReportView report={mockDailyReport} />);
    expect(screen.getByText(/All-time:/i)).toBeInTheDocument();
  });

  it("shows an empty state when there are no days", () => {
    const empty: DailyReport = {
      generated_at: new Date().toISOString(),
      days: {},
    };
    render(<DailyReportView report={empty} />);
    expect(screen.getByTestId("empty-state")).toBeInTheDocument();
  });
});

describe("toDailySeries", () => {
  it("flattens days into a chronologically sorted series", () => {
    const series = toDailySeries(mockDailyReport);
    expect(series).toHaveLength(Object.keys(mockDailyReport.days).length);
    for (let i = 1; i < series.length; i++) {
      expect(series[i - 1].day.localeCompare(series[i].day)).toBeLessThan(0);
    }
    expect(series[0]).toHaveProperty("cost");
    expect(series[0]).toHaveProperty("p95");
  });
});
