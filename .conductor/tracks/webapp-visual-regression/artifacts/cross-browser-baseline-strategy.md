# Cross-Browser Baseline Strategy

## Purpose
Define how Firefox and WebKit visual checks are introduced without destabilizing PR gating.

## Rollout Modes

### Mode 1: `off`
- No cross-browser run in CI.
- Use when baseline set is still being prepared.

### Mode 2: `non_blocking` (recommended initial rollout)
- Run Firefox/WebKit checks in CI.
- Do not fail workflow on cross-browser mismatch.
- Always publish cross-browser artifacts for review:
  - `visual-cross-browser-report-*`
  - `visual-cross-browser-results-*`
- Keep Chromium as the only blocking gate.
- Current default fallback in workflow is `non_blocking` unless overridden.

### Mode 3: `blocking`
- Run Firefox/WebKit checks in CI.
- Fail workflow on cross-browser failures.
- Use after at least 1-2 weeks of stable non-blocking signal.

## Activation Controls
- Workflow input: `cross_browser_mode` (`off`, `non_blocking`, `blocking`)
- Optional repo variable default: `VISUAL_CROSS_BROWSER_MODE`
- Local run: `npm run test:visual:cross`
- Scheduled CI run (weekdays) supports steady non-blocking signal collection.

## Baseline Policy
- Do not update Firefox/WebKit baselines during regular PR checks.
- Baseline updates must be explicit via workflow dispatch (`update_baselines=true`) and include rationale in PR.
- For cross-browser mismatch triage:
  1. confirm issue reproduces in artifact report
  2. classify as intentional vs regression
  3. update baseline only with reviewer sign-off and `visual-baseline-approved` label

## Promotion Criteria to Blocking Mode
- Cross-browser run passes for at least 5 consecutive CI runs on active branch.
- No unresolved high-severity browser-specific rendering bugs in P0 routes.
- Team confirms baseline noise is acceptable.

## Ownership
- Primary owner: engineering
- Approval owner for baseline updates: designated reviewer in PR process

## Operational Tracking
- Use `cross-browser-stability-log.md` to record consecutive non-blocking outcomes.
- Use `npm run test:visual:stability-log` to generate markdown rows from recent GitHub workflow runs.
