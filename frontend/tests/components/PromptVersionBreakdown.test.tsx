import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  PromptVersionBreakdown,
  toVersionRows,
} from "@/components/PromptVersionBreakdown";
import { mockMetrics } from "@/lib/mockData";
import type { Metrics } from "@/types";

describe("PromptVersionBreakdown", () => {
  it("renders one row per prompt version", () => {
    render(<PromptVersionBreakdown metrics={mockMetrics} />);
    expect(screen.getAllByTestId("version-row")).toHaveLength(
      Object.keys(mockMetrics.cost_by_prompt_version).length
    );
  });

  it("computes cost shares that sum to ~1", () => {
    const rows = toVersionRows(mockMetrics);
    const total = rows.reduce((s, r) => s + r.share, 0);
    expect(total).toBeCloseTo(1, 4);
  });

  it("shows an empty state when there are no versions", () => {
    const empty: Metrics = { ...mockMetrics, cost_by_prompt_version: {} };
    render(<PromptVersionBreakdown metrics={empty} />);
    expect(screen.getByTestId("empty-state")).toBeInTheDocument();
  });
});
