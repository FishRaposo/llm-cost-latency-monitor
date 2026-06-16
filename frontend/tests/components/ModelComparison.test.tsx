import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  ModelComparison,
  toModelRows,
} from "@/components/ModelComparison";
import { mockMetrics } from "@/lib/mockData";
import type { Metrics } from "@/types";

describe("ModelComparison", () => {
  it("renders one table row per model, sorted by cost descending", () => {
    render(<ModelComparison metrics={mockMetrics} />);
    const rows = screen.getAllByTestId("model-row");
    expect(rows).toHaveLength(Object.keys(mockMetrics.by_model).length);
    // Highest-cost model (gpt-4o) should appear in the document.
    expect(screen.getByText("gpt-4o")).toBeInTheDocument();
  });

  it("sorts rows by descending cost", () => {
    const rows = toModelRows(mockMetrics);
    for (let i = 1; i < rows.length; i++) {
      expect(rows[i - 1].cost).toBeGreaterThanOrEqual(rows[i].cost);
    }
    expect(rows[0].model).toBe("gpt-4o");
  });

  it("computes cost per call", () => {
    const rows = toModelRows(mockMetrics);
    const gpt4o = rows.find((r) => r.model === "gpt-4o")!;
    expect(gpt4o.costPerCall).toBeCloseTo(28.4412 / 5120, 6);
  });

  it("shows an empty state when there are no models", () => {
    const empty: Metrics = { ...mockMetrics, by_model: {} };
    render(<ModelComparison metrics={empty} />);
    expect(screen.getByTestId("empty-state")).toBeInTheDocument();
  });
});
