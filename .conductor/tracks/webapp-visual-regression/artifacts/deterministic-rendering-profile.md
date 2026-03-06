# Deterministic Rendering Profile (Phase 1)

## Objective
Reduce visual snapshot noise so diffs reflect real UI changes rather than environment jitter.

## Required Defaults
- `locale`: `en-US`
- `timezoneId`: `UTC`
- `colorScheme`: `light`
- `reducedMotion`: `reduce`
- Browser: Chromium only (Phase 1)

## Stabilization Rules
1. Disable animations and transitions during capture.
2. Wait for font readiness before screenshot (`document.fonts.ready`).
3. Wait for key image selectors where applicable.
4. Wait for network idle before capture on data-driven screens.
5. Mask dynamic regions (timestamps, rotating announcements, random IDs).

## Suggested Playwright Config Shape
```ts
use: {
  locale: 'en-US',
  timezoneId: 'UTC',
  colorScheme: 'light',
  reducedMotion: 'reduce'
}
```

## Capture Style Policy
Use a screenshot style file to neutralize volatility:
- pause CSS animations
- disable transitions
- hide dynamic iframes/widgets if not under test

## Readiness Contract
Before any snapshot:
1. Navigate to page state.
2. Apply state setup (fixture/mocks/actions from manifest).
3. Wait for ready selector.
4. Wait for fonts and network idle.
5. Capture screenshot.

## Validation Procedure
Run the same state three times locally.
- Pass condition: no unexpected diffs across three consecutive runs.
- If diffs persist, classify source:
  - dynamic content not masked
  - animation timing
  - async data not settled

## Exit Criteria for Task 1.1
- Deterministic defaults documented
- Capture policy documented
- Validation procedure documented
- Referenced by runbook and manifest
