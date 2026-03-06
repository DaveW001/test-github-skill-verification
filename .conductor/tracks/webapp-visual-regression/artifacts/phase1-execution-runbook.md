# Phase 1 Execution Runbook

## Purpose
Turn the Phase 1 plan into executable work items for the Build agent while keeping scope tight: deterministic rendering + native snapshot workflow + manifest-driven coverage.

## Locked Decisions (Execution)
- Use Playwright native snapshots (`toHaveScreenshot`) as the default baseline/diff mechanism.
- Start with Chromium only for deterministic baseline generation.
- Use the manifest as source of truth for page/state/viewport coverage.
- Do not add custom image-diff infrastructure in Phase 1.

## Inputs
- Spec: `.conductor/tracks/webapp-visual-regression/spec.md`
- Plan: `.conductor/tracks/webapp-visual-regression/plan.md`
- Template: `.conductor/tracks/webapp-visual-regression/artifacts/page-state-manifest.template.yaml`
- Draft: `.conductor/tracks/webapp-visual-regression/artifacts/page-state-manifest.draft.yaml`

## Execution Sequence

### Step A: Deterministic Profile (Task 1.1)
1. Add test-run defaults:
   - locale: `en-US`
   - timezone: `UTC`
   - reduced motion
2. Add capture stylesheet for volatile elements and animations.
3. Add readiness gates:
   - wait for fonts
   - wait for image selectors
   - wait for network-idle
4. Record defaults in skill documentation.

Definition of done:
- Same page/state produces stable snapshots in 3 consecutive local runs.

### Step B: Manifest Hardening (Task 1.2)
1. Confirm canonical base URL and app route inventory.
2. Replace placeholder selectors (`stickyHeaderSelector`, `primaryCtaSelector`).
3. Replace placeholder setup hooks with executable fixture/mocks/actions.
4. Confirm P0 pages for PR gating.

Definition of done:
- All P0 page states have concrete setup and ready selectors.

### Step C: Native Snapshot Workflow (Task 1.3)
1. Configure project-level screenshot thresholds.
2. Implement manifest-driven snapshot test generation.
3. Document baseline creation/update flow.

Recommended command flow:
```bash
npx playwright test -c .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts
npx playwright test -c .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts --update-snapshots
npx playwright show-report .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright-report
```

Equivalent root scripts:
```bash
npm run test:visual
npm run test:visual:update
npm run test:visual:report
```

Definition of done:
- Visual failures output expected/actual/diff artifacts in HTML report.

### Step D: Viewports + Scroll Probes (Task 1.4)
1. Wire all 5 viewports from manifest.
2. Add probe captures for `top`, `mid`, `lower` where required.
3. Validate sticky-header visibility checks at probe points.

Definition of done:
- P0 pages run across all configured viewports without flaky false positives.

### Step E: Noise Controls + Governance (Task 1.5 and 1.7)
1. Set global ignore selector policy.
2. Add per-page threshold override support.
3. Enforce baseline update rationale in PR template.
4. Enforce no automatic baseline updates in standard PR checks.

Definition of done:
- Baseline updates require explicit, reviewable intent.

## Risks to Watch During Execution
- Missing route tree/selectors can stall test generation.
- Dynamic content can produce noisy baselines if masks are incomplete.
- Overly broad P0 scope can slow PR feedback loops.

## Immediate Next Action for Build Agent
Start with Step A and Step B in parallel:
- A: deterministic defaults and capture style policy
- B: route/selectors hardening for `openchamber-root` P0 page
