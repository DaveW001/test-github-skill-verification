import { test, expect } from '@playwright/test';

const BASE_URL = process.env.PW_BASE_URL ?? 'https://www.packagedagile.com';
const routes = ['/', '/contact', '/insights'];

for (const route of routes) {
  test(`page health ${route}`, async ({ page }) => {
    const response = await page.goto(new URL(route, BASE_URL).toString(), { waitUntil: 'domcontentloaded' });
    expect(response?.ok()).toBeTruthy();
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    await expect(page.locator('meta[name="description"]')).toHaveCount(1);
    // Some pages may have more than one h1; check for at least one instead of exactly one.
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);
  });
}
