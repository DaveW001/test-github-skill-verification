import { Page } from "@playwright/test";

const STABILIZE_CSS = `
*, *::before, *::after {
  animation: none !important;
  transition: none !important;
  caret-color: transparent !important;
}
html {
  scroll-behavior: auto !important;
}
`;

export async function prepareDeterministicPage(page: Page): Promise<void> {
  await page.emulateMedia({ reducedMotion: "reduce", colorScheme: "light" });
  await page.addStyleTag({ content: STABILIZE_CSS });
}

type StableRenderOptions = {
  imageReadySelectors?: string[];
  settleMs?: number;
};

export async function waitForStableRender(
  page: Page,
  readySelector: string,
  options: StableRenderOptions = {},
): Promise<void> {
  const { imageReadySelectors = [], settleMs = 150 } = options;

  await page.waitForLoadState("domcontentloaded");
  if (readySelector) {
    await page.locator(readySelector).first().waitFor({ state: "visible", timeout: 10_000 });
  }

  for (const selector of imageReadySelectors) {
    const image = page.locator(selector).first();
    await image.waitFor({ state: "visible", timeout: 10_000 });
  }

  await page.evaluate(async () => {
    if (document.fonts && "ready" in document.fonts) {
      await document.fonts.ready;
    }
  });

  await page.waitForTimeout(settleMs);
}

export async function scrollProbe(page: Page, probe: "top" | "mid" | "lower"): Promise<void> {
  if (probe === "top") {
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(120);
    return;
  }
  if (probe === "mid") {
    await page.evaluate(() => {
      const y = Math.round(window.innerHeight * 0.9);
      window.scrollTo(0, y);
    });
    await page.waitForTimeout(140);
    return;
  }
  await page.evaluate(() => {
    const y = Math.round(window.innerHeight * 2.2);
    window.scrollTo(0, y);
  });
  await page.waitForTimeout(160);
}
