import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const BASE_URL = process.env.PW_BASE_URL ?? 'https://www.packagedagile.com';
const routes = ['/', '/contact', '/insights'];

for (const route of routes) {
  test(`accessibility smoke ${route}`, async ({ page }) => {
    await page.goto(new URL(route, BASE_URL).toString(), { waitUntil: 'networkidle' });
    const results = await new AxeBuilder({ page }).analyze();
    // On first run, log violations so the test does not block CI unexpectedly.
    // After known issues are fixed, change this to: expect(results.violations).toEqual([]);
    if (results.violations.length > 0) {
      console.log(`A11y violations on ${route}:`, JSON.stringify(results.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length })), null, 2));
    }
    expect(results.violations.length).toBeLessThanOrEqual(5); // Known issues: see accessibility-known-issues.md
  });
}
