// story: e01s01
import { defineConfig, devices } from "@playwright/test";


export default defineConfig({
  expect: { timeout: 5_000 },
  fullyParallel: false,
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  reporter: "list",
  testDir: "./apps/web/e2e",
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "retain-on-failure",
  },
  webServer: {
    command:
      "npm run dev --workspace @medinfo/web -- --hostname 127.0.0.1 --port 3000",
    reuseExistingServer: false,
    timeout: 120_000,
    url: "http://127.0.0.1:3000",
  },
  workers: 1,
});
