import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BudgetAlertsPanel } from "@/components/BudgetAlertsPanel";
import { mockBudgetAlerts } from "@/lib/mockData";
import type { BudgetAlertsResponse } from "@/types";

describe("BudgetAlertsPanel", () => {
  it("renders each alert when spend is flagged", () => {
    render(<BudgetAlertsPanel data={mockBudgetAlerts} />);
    expect(screen.getByTestId("budget-status-flagged")).toBeInTheDocument();
    expect(screen.getAllByTestId("budget-alert")).toHaveLength(
      mockBudgetAlerts.alerts.length
    );
    expect(
      screen.getByText(/Total spend .* exceeds budget/)
    ).toBeInTheDocument();
  });

  it("shows a within-budget state when not flagged", () => {
    const ok: BudgetAlertsResponse = {
      threshold_usd: 100,
      per_model_threshold_usd: null,
      total_cost: 4.2,
      flagged: false,
      alerts: [],
      total_alerts: 0,
    };
    render(<BudgetAlertsPanel data={ok} />);
    expect(screen.getByTestId("budget-status-ok")).toBeInTheDocument();
    expect(
      screen.getByText(/within all configured budget thresholds/i)
    ).toBeInTheDocument();
  });
});
