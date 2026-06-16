import { describe, it, expect, vi, afterEach } from "vitest";
import { apiClient } from "@/lib/api";
import {
  mockMetrics,
  mockBudgetAlerts,
  mockDailyReport,
} from "@/lib/mockData";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("apiClient demo-mode fallback", () => {
  it("falls back to mock metrics and tags source=demo on fetch error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new Error("ECONNREFUSED")))
    );
    const res = await apiClient.getMetrics();
    expect(res.source).toBe("demo");
    expect(res.data).toEqual(mockMetrics);
  });

  it("falls back to mock budget alerts on fetch error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new Error("offline")))
    );
    const res = await apiClient.getBudgetAlerts();
    expect(res.source).toBe("demo");
    expect(res.data).toEqual(mockBudgetAlerts);
  });

  it("returns live data tagged source=live on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockMetrics),
        } as Response)
      )
    );
    const res = await apiClient.getMetrics();
    expect(res.source).toBe("live");
    expect(res.data).toEqual(mockMetrics);
  });

  it("treats a non-ok response as demo fallback", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: "Internal Server Error",
          json: () => Promise.resolve({ detail: "boom" }),
        } as Response)
      )
    );
    const res = await apiClient.getDailyReport();
    expect(res.source).toBe("demo");
    expect(res.data).toEqual(mockDailyReport);
  });

  it("throws on a failed write (POST /log) rather than faking success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new Error("offline")))
    );
    await expect(
      apiClient.logTelemetry({
        model: "gpt-4o",
        input_tokens: 10,
        output_tokens: 5,
        cost_usd: 0.001,
        latency_ms: 100,
      })
    ).rejects.toThrow();
  });
});
