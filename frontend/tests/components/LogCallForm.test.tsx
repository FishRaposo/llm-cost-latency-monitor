import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LogCallForm } from "@/components/LogCallForm";
import { apiClient } from "@/lib/api";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("LogCallForm", () => {
  it("renders prefilled defaults", () => {
    render(<LogCallForm />);
    expect(screen.getByTestId("log-call-form")).toBeInTheDocument();
    expect(screen.getByDisplayValue("gpt-4o")).toBeInTheDocument();
    expect(screen.getByDisplayValue("v3-summarize")).toBeInTheDocument();
  });

  it("submits telemetry and reports success", async () => {
    const spy = vi
      .spyOn(apiClient, "logTelemetry")
      .mockResolvedValue({ status: "logged" });
    const onLogged = vi.fn();
    const user = userEvent.setup();

    render(<LogCallForm onLogged={onLogged} />);
    await user.click(screen.getByRole("button", { name: /log call/i }));

    await waitFor(() =>
      expect(screen.getByTestId("log-success")).toBeInTheDocument()
    );
    expect(spy).toHaveBeenCalledOnce();
    expect(onLogged).toHaveBeenCalledOnce();
  });

  it("shows a demo-mode notice when the backend is unreachable", async () => {
    vi.spyOn(apiClient, "logTelemetry").mockRejectedValue(
      new Error("offline")
    );
    const user = userEvent.setup();

    render(<LogCallForm />);
    await user.click(screen.getByRole("button", { name: /log call/i }));

    await waitFor(() =>
      expect(screen.getByTestId("log-demo")).toBeInTheDocument()
    );
  });
});
