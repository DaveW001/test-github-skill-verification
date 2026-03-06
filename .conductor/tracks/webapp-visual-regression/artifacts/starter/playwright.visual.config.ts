import { defineConfig } from "@playwright/test";

const baseURL = process.env.PW_BASE_URL || "http://localhost:3000";
const crossBrowser = process.env.PW_CROSS_BROWSER === "1";
const reportDir = process.env.PW_REPORT_DIR || "playwright-report";
const outputDir = process.env.PW_TEST_OUTPUT_DIR || "test-results";
const projects = [
  {
    name: "chromium",
    use: { browserName: "chromium" as const },
  },
];

if (crossBrowser) {
  projects.push(
    {
      name: "firefox",
      use: { browserName: "firefox" as const },
    },
    {
      name: "webkit",
      use: { browserName: "webkit" as const },
    }
  );
}

export default defineConfig({
  testDir: "tests/visual",
  outputDir,
  snapshotPathTemplate: "snapshots/{projectName}/{testFilePath}/{arg}{ext}",
  workers: process.env.CI ? 2 : 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  timeout: 45_000,
  expect: {
    timeout: 10_000,
    toHaveScreenshot: {
      maxDiffPixels: 250,
      maxDiffPixelRatio: 0.002,
    },
  },
  reporter: [
    ["list"],
    ["html", { outputFolder: reportDir, open: "never" }],
  ],
  use: {
    baseURL,
    locale: "en-US",
    timezoneId: "UTC",
    colorScheme: "light",
    reducedMotion: "reduce",
    headless: true,
    screenshot: "only-on-failure",
    trace: "on-first-retry",
  },
  projects,
});
