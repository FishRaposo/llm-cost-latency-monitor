import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  DemoModeBadge,
  DemoModeBanner,
} from "@/components/DemoModeBadge";

describe("DemoModeBadge", () => {
  it("renders a live badge when connected to the backend", () => {
    render(<DemoModeBadge source="live" />);
    expect(screen.getByTestId("source-badge-live")).toBeInTheDocument();
    expect(screen.getByText("Live")).toBeInTheDocument();
  });

  it("renders a demo badge when using bundled data", () => {
    render(<DemoModeBadge source="demo" />);
    expect(screen.getByTestId("source-badge-demo")).toBeInTheDocument();
    expect(screen.getByText("Demo mode")).toBeInTheDocument();
  });
});

describe("DemoModeBanner", () => {
  it("renders nothing in live mode", () => {
    const { container } = render(<DemoModeBanner source="live" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders an explanatory banner in demo mode", () => {
    render(<DemoModeBanner source="demo" />);
    expect(screen.getByTestId("demo-banner")).toBeInTheDocument();
    expect(screen.getByText(/Demo mode\./)).toBeInTheDocument();
  });
});
