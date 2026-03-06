# Phase 1 Starter Kit

This starter kit provides an executable baseline for Phase 1 visual QA using Playwright native snapshots.

## Included
- `playwright.visual.config.ts`
- `tests/visual/p0.visual.spec.ts`
- `tests/visual/components.synthetic.spec.ts`
- `tests/visual/helpers/deterministic.ts`
- `tests/visual/helpers/layout-guards.ts`
- `tests/visual/helpers/contrast-guards.ts`
- `tests/visual/helpers/long-content.ts`
- `tests/visual/layout-guards.synthetic.spec.ts`

## P0 Routes Configured
- `/`
- `/contact`

## Quick Start
1. Install dependencies:
   - `npm i -D @playwright/test`
2. Install Chromium:
   - `npx playwright install chromium --with-deps`
3. Run visual checks:
   - `npx playwright test -c .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts`
   - `npm run test:visual` (P0 default)
   - `npm run test:visual:components` (component synthetic pack)
   - `npm run test:visual:full` (all specs)
   - `npm run test:visual:cross` (Chromium + Firefox + WebKit)
   - `npm run test:visual:cross:p0` (Firefox + WebKit on P0 only)
   - `npm run test:visual:cross:components` (Firefox + WebKit on synthetic components)
4. Create/update baselines intentionally:
   - `npx playwright test -c .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts --update-snapshots`
   - `npm run test:visual:update:components`
   - `npm run test:visual:update:cross`
5. Open report:
   - `npx playwright show-report .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright-report`
6. Prepare cross-browser stability rows from GitHub runs:
   - `npm run test:visual:stability-log`

## Useful Environment Flags
- `PW_BASE_URL` to override base URL (default `http://localhost:3000`)
- `PW_CROSS_BROWSER=1` to enable Firefox and WebKit projects in addition to Chromium
- `PW_STRICT_LAYOUT=1` to fail on horizontal overflow instead of warning
- `PW_STRICT_OVERLAY=1` to fail when a mobile overlay open-state signal is not detected
- `PW_STRICT_GUARDS=1` to fail when Phase 2 guardrails detect blocker findings
- `PW_STRICT_A11Y=1` to fail when contrast guard checks detect low-contrast targets

## Notes
- This is intentionally scoped to Phase 1.
- Phase 2 guardrails are integrated into the P0 suite with severity annotations:
  - sticky-header overlap probes
  - off-page element checks
  - spacing outlier checks for repeated layouts
- Contrast-focused accessibility guards are integrated for critical CTA targets (warning-first by default).
- Guardrails are warning-first by default and can be hardened with `PW_STRICT_GUARDS=1`.
- Synthetic known-bad guard tests are included to validate detector behavior.
- Cross-browser rollout strategy and CI policy: `../cross-browser-baseline-strategy.md`
- Cross-browser stability tracker: `../cross-browser-stability-log.md`
- CI defaults cross-browser mode to `blocking` unless overridden by `VISUAL_CROSS_BROWSER_MODE` or workflow input.
- CI schedule is enabled for weekday automatic runs (14:00 UTC) to accumulate stability signal.
- Storybook/component rollout plan: `../storybook-adoption-path.md`
- Long-page capture patterns: `../long-page-capture-patterns.md`
- Mobile overlay checks now run by default on mobile viewports.
- If the app does not expose a stable open-state signal in headless mode, the suite adds a warning annotation (or fails with `PW_STRICT_OVERLAY=1`).
- Investigation notes and selector follow-up: `overlay-investigation.md`
