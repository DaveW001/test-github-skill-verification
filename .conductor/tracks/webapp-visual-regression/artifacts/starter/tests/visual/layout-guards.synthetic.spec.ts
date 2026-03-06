import { expect, test } from "@playwright/test";
import { runLayoutGuards } from "./helpers/layout-guards";

test.describe("layout guards synthetic", () => {
  test("detects sticky overlap blocker", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.setContent(`
      <style>
        body { margin: 0; font-family: sans-serif; }
        header { position: fixed; top: 0; left: 0; right: 0; height: 96px; background: #111; }
        main { padding-top: 24px; }
      </style>
      <header></header>
      <main>
        <h1>Title hidden by header</h1>
        <a href="/contact">Contact</a>
      </main>
    `);

    const findings = await runLayoutGuards(page, {
      stickySelector: "header",
      criticalSelectors: ["main h1", "a[href='/contact']"],
      offPageSelectors: ["a[href='/contact']"],
      spacingGroupSelectors: [],
    });

    expect(findings.some((f) => f.kind === "sticky-overlap" && f.severity === "blocker")).toBeTruthy();
  });

  test("detects off-page warn", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.setContent(`
      <style>
        body { margin: 0; overflow-x: auto; }
        .escape { margin-left: 280px; width: 220px; height: 40px; }
      </style>
      <main>
        <button class="escape">Escaping button</button>
      </main>
    `);

    const findings = await runLayoutGuards(page, {
      stickySelector: "header",
      criticalSelectors: ["button.escape"],
      offPageSelectors: ["button.escape"],
      spacingGroupSelectors: [],
    });

    expect(findings.some((f) => f.kind === "off-page" && f.severity === "warn")).toBeTruthy();
  });

  test("detects spacing outlier info", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.setContent(`
      <style>
        body { margin: 0; }
        .cards { display: flex; flex-direction: column; width: 320px; }
        .card { height: 60px; background: #e5e7eb; }
        .gap-small { margin-top: 16px; }
        .gap-large { margin-top: 120px; }
      </style>
      <main>
        <div class="cards">
          <div class="card"></div>
          <div class="card gap-small"></div>
          <div class="card gap-large"></div>
          <div class="card gap-small"></div>
        </div>
      </main>
    `);

    const findings = await runLayoutGuards(page, {
      stickySelector: "header",
      criticalSelectors: ["main h1"],
      offPageSelectors: [".cards .card"],
      spacingGroupSelectors: [".cards .card"],
    });

    expect(findings.some((f) => f.kind === "spacing-outlier" && f.severity === "info")).toBeTruthy();
  });
});
