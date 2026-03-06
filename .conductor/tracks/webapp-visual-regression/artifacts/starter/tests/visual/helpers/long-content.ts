import { Page } from "@playwright/test";

type PrimeLongContentOptions = {
  passes?: number;
  settleMs?: number;
};

export async function primeLongContent(page: Page, options: PrimeLongContentOptions = {}): Promise<void> {
  const { passes = 2, settleMs = 180 } = options;

  for (let i = 0; i < passes; i += 1) {
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await page.waitForTimeout(settleMs);
  }

  await page.evaluate(() => {
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(settleMs);
}
