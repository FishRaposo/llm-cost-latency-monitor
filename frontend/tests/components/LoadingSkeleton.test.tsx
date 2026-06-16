import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  KpiGridSkeleton,
  ChartSkeleton,
  TableSkeleton,
} from "@/components/LoadingSkeleton";

describe("LoadingSkeleton", () => {
  it("renders a grid of KPI skeletons", () => {
    render(<KpiGridSkeleton count={6} />);
    expect(screen.getAllByTestId("kpi-skeleton")).toHaveLength(6);
  });

  it("renders a chart skeleton", () => {
    const { container } = render(<ChartSkeleton />);
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("renders a table skeleton with the requested number of rows", () => {
    render(<TableSkeleton rows={5} />);
    expect(screen.getByTestId("table-skeleton")).toBeInTheDocument();
  });
});
