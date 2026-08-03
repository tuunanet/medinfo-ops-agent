// story: e01s01
import { expect, test } from "@playwright/test";


test("healthy workspace shows truthful ready states", async ({ page }) => {
  await page.route("**/api/health/ready", async (route) => {
    await route.fulfill({
      body: JSON.stringify({
        checks: { database: "ready", pgvector: "ready" },
        status: "ready",
      }),
      contentType: "application/json",
      status: 200,
    });
  });

  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "Reviewer workspace" }),
  ).toBeVisible();
  await expect(page.getByText("Synthetic demonstration only")).toBeVisible();
  await expect(page.getByTestId("overall-status")).toHaveText("Ready");
  await expect(page.getByTestId("api-status")).toHaveText("Ready");
  await expect(page.getByTestId("database-status")).toHaveText("Ready");
  await expect(page.getByTestId("pgvector-status")).toHaveText("Ready");
});


test("API failure never appears ready", async ({ page }) => {
  await page.route("**/api/health/ready", async (route) => {
    await route.abort("failed");
  });

  await page.goto("/");

  await expect(page.getByTestId("overall-status")).toHaveText("Unavailable");
  await expect(page.getByTestId("api-status")).toHaveText("Unavailable");
  await expect(page.getByTestId("database-status")).toHaveText("Not checked");
  await expect(page.getByTestId("pgvector-status")).toHaveText("Not checked");
  await expect(
    page.getByText("Check that the FastAPI process is running"),
  ).toBeVisible();
});


const dependencyFailures = [
  {
    checks: { database: "unavailable", pgvector: "not_checked" },
    expectedDatabase: "Unavailable",
    expectedGuidance: "Start the local PostgreSQL container",
    expectedPgvector: "Not checked",
    name: "database unavailable",
  },
  {
    checks: { database: "ready", pgvector: "unavailable" },
    expectedDatabase: "Ready",
    expectedGuidance: "Verify that pgvector 0.8.6 is installed",
    expectedPgvector: "Unavailable",
    name: "pgvector unavailable",
  },
] as const;

test("readiness status is announced without color dependence", async ({ page }) => {
  await page.route("**/api/health/ready", async (route) => {
    await route.fulfill({
      body: JSON.stringify({
        checks: { database: "ready", pgvector: "ready" },
        status: "ready",
      }),
      contentType: "application/json",
      status: 200,
    });
  });

  await page.goto("/");

  await expect(page.getByRole("status")).toContainText("Local readiness");
  await expect(page.getByRole("status")).toContainText("Ready");
  await expect(page.getByText("API")).toBeVisible();
  await expect(page.getByText("Database")).toBeVisible();
  await expect(page.getByText("pgvector")).toBeVisible();
});


for (const scenario of dependencyFailures) {
  test(`${scenario.name} remains distinct`, async ({ page }) => {
    await page.route("**/api/health/ready", async (route) => {
      await route.fulfill({
        body: JSON.stringify({
          checks: scenario.checks,
          status: "unavailable",
        }),
        contentType: "application/json",
        status: 503,
      });
    });

    await page.goto("/");

    await expect(page.getByTestId("overall-status")).toHaveText("Unavailable");
    await expect(page.getByTestId("api-status")).toHaveText("Ready");
    await expect(page.getByTestId("database-status")).toHaveText(
      scenario.expectedDatabase,
    );
    await expect(page.getByTestId("pgvector-status")).toHaveText(
      scenario.expectedPgvector,
    );
    await expect(page.getByText(scenario.expectedGuidance)).toBeVisible();
  });
}
