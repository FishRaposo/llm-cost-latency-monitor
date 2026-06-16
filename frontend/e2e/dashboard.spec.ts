import { test, expect } from "@playwright/test";

// Smoke E2E: navigates the demo-mode UI with no backend running. The dashboard
// falls back to bundled demo data, so every view renders offline.

test("overview renders KPIs in demo mode", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/LLM Monitor/i);
  await expect(
    page.getByRole("heading", { name: "Overview", level: 1 })
  ).toBeVisible();
  // Demo-mode indicator should be visible since there's no backend.
  await expect(page.getByTestId("demo-banner")).toBeVisible();
  await expect(page.getByText("Total requests")).toBeVisible();
});

test("navigates across all dashboard sections", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("link", { name: "Models" }).click();
  await expect(
    page.getByRole("heading", { name: "Models", level: 1 })
  ).toBeVisible();
  await expect(page.getByTestId("model-comparison")).toBeVisible();

  await page.getByRole("link", { name: "Daily report" }).click();
  await expect(
    page.getByRole("heading", { name: "Daily report", level: 1 })
  ).toBeVisible();
  await expect(page.getByTestId("daily-report")).toBeVisible();

  await page.getByRole("link", { name: "Budgets" }).click();
  await expect(
    page.getByRole("heading", { name: "Budgets", level: 1 })
  ).toBeVisible();
  await expect(page.getByTestId("budget-panel")).toBeVisible();

  await page.getByRole("link", { name: "Log a call" }).click();
  await expect(page.getByTestId("log-call-form")).toBeVisible();
});

test("log-a-call form reports demo mode on submit with no backend", async ({
  page,
}) => {
  await page.goto("/log");
  await page.getByRole("button", { name: /log call/i }).click();
  await expect(page.getByTestId("log-demo")).toBeVisible();
});
