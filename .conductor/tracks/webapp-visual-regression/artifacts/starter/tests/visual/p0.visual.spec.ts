import { expect, test, type Page } from "@playwright/test";
import { prepareDeterministicPage, scrollProbe, waitForStableRender } from "./helpers/deterministic";
import { runLayoutGuards, type GuardFinding } from "./helpers/layout-guards";
import { runContrastGuards } from "./helpers/contrast-guards";
import { primeLongContent } from "./helpers/long-content";

type Probe = "top" | "mid" | "lower";

type CaseDef = {
  id: string;
  route: string;
  readySelector: string;
  stickySelector: string;
  ctaSelector: string;
  ctaVisibleMinWidth: number;
  ctaVisibleProbes: Probe[];
  imageReadySelectors: string[];
  probes: Probe[];
  overlayTriggerSelector?: string;
  overlayReadySelector?: string;
  fullMaxDiffPixels?: number;
  fullMaxDiffPixelRatio?: number;
  guardOffPageSelectors: string[];
  guardSpacingSelectors: string[];
  contrastTargets: Array<{ selector: string; minRatio: number; label: string }>;
};

const viewports = [
  { name: "mobile-narrow", width: 360, height: 800 },
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "laptop", width: 1366, height: 768 },
  { name: "desktop", width: 1920, height: 1080 },
];

const p0Cases: CaseDef[] = [
  {
    id: "home",
    route: "/",
    readySelector: "header.fixed",
    stickySelector: "header.fixed",
    ctaSelector: "a[href='/contact']",
    ctaVisibleMinWidth: 768,
    ctaVisibleProbes: ["top", "mid"],
    imageReadySelectors: ["img[alt='Packaged Agile Logo']"],
    probes: ["top", "mid", "lower"],
    overlayTriggerSelector: "button[aria-haspopup='dialog']",
    overlayReadySelector: "button[aria-haspopup='dialog'][aria-expanded='true']",
    guardOffPageSelectors: ["main a", "main button", "main img", "main h1", "main h2"],
    guardSpacingSelectors: ["#who-we-serve .grid > a", "#results-section .grid > div"],
    contrastTargets: [
      { selector: "a[href='/how-we-deliver'] button", minRatio: 4.5, label: "home hero CTA" },
      { selector: "a[href='/services'] button", minRatio: 4.5, label: "home services CTA" },
    ],
  },
  {
    id: "contact",
    route: "/contact",
    readySelector: "form",
    stickySelector: "header.fixed",
    ctaSelector: "form button[type='submit']",
    ctaVisibleMinWidth: 0,
    ctaVisibleProbes: ["top"],
    imageReadySelectors: ["img[alt='Packaged Agile office lobby']"],
    probes: ["top", "mid"],
    fullMaxDiffPixels: 4500,
    fullMaxDiffPixelRatio: 0.012,
    guardOffPageSelectors: ["main a", "main button", "main img", "main h1", "main h2", "form input", "form textarea"],
    guardSpacingSelectors: ["form > div"],
    contrastTargets: [
      { selector: "form button[type='submit']", minRatio: 4.5, label: "contact submit" },
      { selector: "a[href='/contact']", minRatio: 4.5, label: "header contact link" },
    ],
  },
];

async function hasHorizontalOverflow(page: Page) {
  return page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    return root.scrollWidth > root.clientWidth + 1 || body.scrollWidth > body.clientWidth + 1;
  });
}

async function stabilizeScreenshotFrame(page: Page) {
  await page.evaluate(() => {
    document.documentElement.style.overflowX = "clip";
    document.body.style.overflowX = "clip";
  });
  await page.waitForTimeout(150);
}

const strictLayout = process.env.PW_STRICT_LAYOUT === "1";
const strictOverlay = process.env.PW_STRICT_OVERLAY === "1";
const strictGuards = process.env.PW_STRICT_GUARDS === "1";
const strictA11y = process.env.PW_STRICT_A11Y === "1";

async function checkOverlayOpen(page: Page, triggerSelector: string, readySelector?: string) {
  try {
    await page.waitForFunction(
      ({ triggerSelector: selector, readySelector: ready }) => {
        const trigger = document.querySelector(selector);
        const expanded = trigger?.getAttribute("aria-expanded") === "true";
        const stateOpen = trigger?.getAttribute("data-state") === "open";
        const readyFound = ready ? !!document.querySelector(ready) : false;
        const dialogVisible = !!document.querySelector("[role='dialog']");
        const portalOpen = !!document.querySelector("[data-state='open']");
        const bodyLocked = getComputedStyle(document.body).overflow === "hidden";
        return expanded || stateOpen || readyFound || dialogVisible || portalOpen || bodyLocked;
      },
      { triggerSelector, readySelector },
      { timeout: 3_000 }
    );
    return true;
  } catch {
    return false;
  }
}

async function reportLayoutFindings(page: Page, findings: GuardFinding[], context: string) {
  if (!findings.length) {
    return;
  }

  const counts = findings.reduce(
    (acc, finding) => {
      acc[finding.severity] += 1;
      return acc;
    },
    { blocker: 0, warn: 0, info: 0 }
  );

  for (const finding of findings) {
    test.info().annotations.push({
      type: finding.severity,
      description: `[${finding.kind}] ${context}: ${finding.message}`,
    });
  }

  if (strictGuards && counts.blocker > 0) {
    throw new Error(`Layout guard blockers detected (${counts.blocker}) for ${context}`);
  }

  const evidence = await page.screenshot({ fullPage: false });
  await test.info().attach(`layout-guards-${context.replace(/\s+/g, "-")}.png`, {
    body: evidence,
    contentType: "image/png",
  });
}

async function reportContrastFindings(findings: Array<{ severity: "warn" | "info"; selector: string; message: string }>, context: string) {
  if (!findings.length) {
    return;
  }

  const warnCount = findings.filter((finding) => finding.severity === "warn").length;
  for (const finding of findings) {
    test.info().annotations.push({
      type: finding.severity,
      description: `[contrast] ${context}: ${finding.message} (${finding.selector})`,
    });
  }

  await test.info().attach(`contrast-findings-${context.replace(/\s+/g, "-")}.json`, {
    body: Buffer.from(JSON.stringify(findings, null, 2), "utf8"),
    contentType: "application/json",
  });

  if (strictA11y && warnCount > 0) {
    throw new Error(`Contrast warnings detected (${warnCount}) for ${context}`);
  }
}

for (const viewport of viewports) {
  test.describe(`p0 visual ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    for (const item of p0Cases) {
      test(`${item.id} default`, async ({ page }) => {
        await page.goto(item.route, { waitUntil: "domcontentloaded" });
        await prepareDeterministicPage(page);
        await waitForStableRender(page, item.readySelector, {
          imageReadySelectors: item.imageReadySelectors,
        });

        await expect(page.locator(item.stickySelector)).toBeVisible();
        if (viewport.width >= item.ctaVisibleMinWidth) {
          await expect(page.locator(item.ctaSelector).first()).toBeVisible();
        }
        if (await hasHorizontalOverflow(page)) {
          if (strictLayout) {
            throw new Error(`Horizontal overflow detected on ${item.id} ${viewport.name}`);
          }
          test.info().annotations.push({
            type: "warn",
            description: `Horizontal overflow detected on ${item.id} ${viewport.name}`,
          });
        }

        const defaultFindings = await runLayoutGuards(page, {
          stickySelector: item.stickySelector,
          criticalSelectors: [item.ctaSelector, "main h1", "main h2"],
          offPageSelectors: item.guardOffPageSelectors,
          spacingGroupSelectors: item.guardSpacingSelectors,
        });
        await reportLayoutFindings(page, defaultFindings, `${item.id} ${viewport.name} default`);

        const defaultContrast = await runContrastGuards(page, item.contrastTargets);
        await reportContrastFindings(defaultContrast, `${item.id} ${viewport.name} default`);

        await stabilizeScreenshotFrame(page);
        await expect(page).toHaveScreenshot(`${item.id}-${viewport.name}-full.png`, {
          fullPage: true,
          maxDiffPixels: item.fullMaxDiffPixels,
          maxDiffPixelRatio: item.fullMaxDiffPixelRatio,
        });
      });

      for (const probe of item.probes) {
        test(`${item.id} probe ${probe}`, async ({ page }) => {
          await page.goto(item.route, { waitUntil: "domcontentloaded" });
          await prepareDeterministicPage(page);
          await waitForStableRender(page, item.readySelector, {
            imageReadySelectors: item.imageReadySelectors,
          });

          await scrollProbe(page, probe);
          if (probe === "lower") {
            await primeLongContent(page);
            await scrollProbe(page, probe);
          }
          if (viewport.width >= item.ctaVisibleMinWidth && item.ctaVisibleProbes.includes(probe)) {
            await expect(page.locator(item.ctaSelector).first()).toBeVisible();
          }
          if (await hasHorizontalOverflow(page)) {
            if (strictLayout) {
              throw new Error(`Horizontal overflow detected on ${item.id} ${viewport.name} ${probe}`);
            }
            test.info().annotations.push({
              type: "warn",
              description: `Horizontal overflow detected on ${item.id} ${viewport.name} ${probe}`,
            });
          }

          const probeFindings = await runLayoutGuards(page, {
            stickySelector: item.stickySelector,
            criticalSelectors: [item.ctaSelector, "main h1", "main h2"],
            offPageSelectors: item.guardOffPageSelectors,
            spacingGroupSelectors: item.guardSpacingSelectors,
          });
          await reportLayoutFindings(page, probeFindings, `${item.id} ${viewport.name} ${probe}`);

          if (probe === "top") {
            const probeContrast = await runContrastGuards(page, item.contrastTargets);
            await reportContrastFindings(probeContrast, `${item.id} ${viewport.name} ${probe}`);
          }

          await stabilizeScreenshotFrame(page);
          await expect(page).toHaveScreenshot(`${item.id}-${viewport.name}-${probe}.png`, {
            fullPage: false,
          });
        });
      }

      if (item.overlayTriggerSelector && viewport.width < 768) {
        test(`${item.id} mobile overlay`, async ({ page }) => {
          await page.goto(item.route, { waitUntil: "domcontentloaded" });
          await prepareDeterministicPage(page);
          await waitForStableRender(page, item.readySelector, {
            imageReadySelectors: item.imageReadySelectors,
          });

          await page.locator(item.overlayTriggerSelector).first().click();
          const overlayOpen = await checkOverlayOpen(page, item.overlayTriggerSelector, item.overlayReadySelector);
          if (!overlayOpen) {
            if (strictOverlay) {
              throw new Error(`Overlay open-state signal not detected on ${item.id} ${viewport.name}`);
            }
            test.info().annotations.push({
              type: "warn",
              description: `Overlay open-state signal not detected on ${item.id} ${viewport.name}`,
            });
          }

          const overlayFindings = await runLayoutGuards(page, {
            stickySelector: item.stickySelector,
            criticalSelectors: [item.ctaSelector, "main h1", "main h2"],
            offPageSelectors: item.guardOffPageSelectors,
            spacingGroupSelectors: item.guardSpacingSelectors,
          });
          await reportLayoutFindings(page, overlayFindings, `${item.id} ${viewport.name} overlay`);

          const overlayContrast = await runContrastGuards(page, item.contrastTargets);
          await reportContrastFindings(overlayContrast, `${item.id} ${viewport.name} overlay`);

          await stabilizeScreenshotFrame(page);
          await expect(page).toHaveScreenshot(`${item.id}-${viewport.name}-overlay.png`, {
            fullPage: false,
          });
        });
      }
    }
  });
}
