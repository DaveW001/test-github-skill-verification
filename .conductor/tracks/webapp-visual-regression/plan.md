# Plan: WebApp Visual QA and Regression Track

**Track ID:** webapp-visual-regression  
**Status:** In Progress - Phase 3  
**Created:** 2026-03-04  
**Estimated Completion:** 4 weeks  
**Priority:** High  
**Owner:** Dave Witkin

## Phase 1: Visual Baseline MVP (Current Priority)
**Timeline:** Week 1  
**Goal:** Reliable, low-noise visual regression workflow for human review.

### Task 1.1: Deterministic Rendering Foundation
- [x] Define test locale/timezone defaults (starter config)
- [x] Add capture stylesheet strategy for volatile UI (animations/transitions/iframes)
- [x] Define readiness checks (fonts loaded, key images loaded)
- [x] Document deterministic run profile in execution artifact (`artifacts/deterministic-rendering-profile.md`)
- [x] Starter helper implemented (`artifacts/starter/tests/visual/helpers/deterministic.ts`)

### Task 1.2: Page/State Manifest
- [x] Create manifest for routes and required states
- [x] Include state minimums: default, empty, loading, error, overlay, long-content
- [x] Tag each page/state with severity expectation and owner
- [x] Mark P0 critical pages for PR gate
- [x] Draft manifest created at `.conductor/tracks/webapp-visual-regression/artifacts/page-state-manifest.draft.yaml`
- [x] Reusable template created at `.conductor/tracks/webapp-visual-regression/artifacts/page-state-manifest.template.yaml`
- [x] Set canonical base URL to `http://localhost:3000`
- [x] Select initial P0 routes for gate: `/` and `/contact`
- [~] Validate and refine selectors during first implementation pass
- [~] Intake template created for concrete route/selector handoff (`artifacts/app-route-selector-intake.md`)

### Task 1.3: Native Snapshot Workflow
- [x] Implement Playwright snapshot assertions as default mechanism (starter spec)
- [x] Configure project-level screenshot diff settings (starter config)
- [x] Document baseline create/update flow using snapshot flags (`README.md`, runbook, npm scripts)
- [x] Add first-pass local run command set and examples (`artifacts/phase1-execution-runbook.md`)
- [x] Starter config + P0 spec scaffolded (`artifacts/starter/playwright.visual.config.ts`, `artifacts/starter/tests/visual/p0.visual.spec.ts`)
- [x] Run first baseline generation in target environment
- [x] Verify baseline pass without update flag (35/35 passing)

### Task 1.4: Viewport Matrix and Scroll Probes
- [ ] Configure matrix: 360x800, 390x844, 768x1024, 1366x768, 1920x1080
- [ ] Add scroll probe captures for long pages (top/mid/lower)
- [ ] Validate sticky header behavior at each probe point

### Task 1.5: Noise Controls and Ignore Policy
- [ ] Define global ignore selectors list
- [ ] Add per-page threshold override capability
- [ ] Add optional retry-once strategy for flaky visual checks
- [ ] Document when masking is allowed vs not allowed

### Task 1.6: Reporting and Triage in Phase 1
- [ ] Enable HTML report output from first implementation
- [ ] Ensure artifacts include expected/actual/diff images
- [ ] Define triage labels: blocker, warn, info
- [ ] Create short reviewer checklist for PR visual review

### Task 1.7: Governance
- [ ] Define baseline update policy
- [ ] Require baseline-change rationale template in PR
- [ ] Define who can approve baseline updates
- [ ] Add no-silent-baseline-churn rule to docs

### Phase 1 Deliverables
- [ ] Deterministic capture profile
- [ ] Page/state manifest
- [ ] Native Playwright snapshot-based checks
- [ ] Viewport + scroll probe coverage
- [ ] HTML report and triage workflow
- [ ] Baseline governance policy

## Phase 2: Layout Guardrails
**Timeline:** Week 2  
**Goal:** Add targeted checks for visual failures that screenshot diffs can miss or obscure.

### Task 2.1: Sticky/Fixed Overlap Checks
- [x] Detect sticky/fixed top elements and measured occupied region
- [x] Check heading/anchor/CTA visibility after scroll-jump and manual scroll points
- [x] Emit severity-classified findings

### Task 2.2: Overflow and Off-Page Checks
- [x] Detect new horizontal scrolling at page and key container levels
- [x] Detect bounding boxes leaving viewport/container unexpectedly
- [x] Capture evidence screenshots for each finding

### Task 2.3: Focused Spacing Drift Heuristics
- [x] Add simple gap consistency checks for repeated card/list layouts
- [x] Flag only clear outliers to avoid noise
- [x] Keep advanced spacing inference out of scope

### Task 2.4: Integrate with Visual Workflow
- [x] Merge heuristic findings into visual test output
- [x] Include severity + suggested next step per finding
- [x] Validate using synthetic known-bad pages

### Phase 2 Deliverables
- [ ] Sticky overlap detector
- [ ] Overflow/off-page detector
- [ ] Low-noise spacing outlier checks
- [ ] Unified report output with severity

## Phase 3: CI/CD and PR Workflow
**Timeline:** Week 3  
**Goal:** Reliable PR gating with reviewable artifacts and controlled baseline updates.

### Task 3.1: GitHub Actions Pipeline
- [x] Add visual regression workflow triggered on PR
- [x] Run P0 page/state manifest by default
- [x] Add manual full-suite run option

### Task 3.2: Artifacts and Reporting
- [x] Upload HTML report and screenshot artifacts on failure
- [x] Keep artifacts for a practical retention window
- [x] Add concise CI output summary

### Task 3.3: Baseline Update Workflow
- [x] Add explicit manual baseline update workflow path (`workflow_dispatch` with `update_baselines=true`)
- [x] Require approval + rationale before merge (snapshot-changing PRs require rationale fields + `visual-baseline-approved` label)
- [x] Prevent automatic baseline writes in regular PR checks

### Task 3.4: Parallelization
- [x] Parallelize by viewport/project where stable
- [x] Keep deterministic settings constant across runners
- [x] Measure runtime and set practical limits

### Phase 3 Deliverables
- [x] PR visual gate with artifacts
- [x] Controlled baseline update workflow
- [x] Parallelized stable execution

## Phase 4: Advanced Expansion
**Timeline:** Week 4+  
**Goal:** Expand coverage after Phase 1-3 stability is proven.

### Task 4.1: Cross-Browser Visual Checks
- [x] Add Firefox and WebKit projects (scaffolded behind `PW_CROSS_BROWSER=1`)
- [x] Maintain browser-specific baselines where needed (strategy documented; Firefox/WebKit baselines validated; blocking mode enabled)

### Task 4.2: Component-Level Visuals
- [x] Add optional component visual runs
- [x] Document adoption path for teams using Storybook

### Task 4.3: Accessibility Visual Checks
- [x] Add contrast-focused checks (critical CTA target guards integrated)
- [x] Include accessibility findings in report output

### Task 4.4: Long Content Helpers
- [x] Improve lazy-load/infinite-scroll capture helpers
- [x] Document reliable long-page capture patterns

### Phase 4 Deliverables
- [x] Cross-browser visual coverage
- [x] Component-level visual examples
- [x] Accessibility visual checks
- [x] Long-content capture helpers

## Current Status

### In Progress
- [ ] None

### Completed
- [x] Initial planning and scope alignment
- [x] Phase 1.2 Page/State Manifest (draft v1)
- [x] Baseline generated and verified (35/35 passing on starter suite)
- [x] Root visual scripts added in `package.json`
- [x] Active CI workflow scaffolded at `.github/workflows/visual-regression.yml`
- [x] Overlay checks enabled by default (warning-first)
- [x] Guardrail checks integrated into P0 suite (sticky overlap, off-page, spacing)
- [x] Baseline re-verified after guardrail integration (37/37 passing)
- [x] CI workflow supports P0 default + manual full mode
- [x] CI workflow supports manual baseline update mode
- [x] CI step summary output added
- [x] Cross-browser project toggle scaffolded in Playwright config (`PW_CROSS_BROWSER=1`)
- [x] CI cross-browser guard modes added (`off`, `non_blocking`, `blocking`)
- [x] Cross-browser baseline rollout strategy documented (`artifacts/cross-browser-baseline-strategy.md`)
- [x] Contrast-focused accessibility guards added to P0 visual flow (warning-first + strict mode)
- [x] Component synthetic visual spec + baseline (`tests/visual/components.synthetic.spec.ts`)
- [x] Storybook adoption path documented (`artifacts/storybook-adoption-path.md`)
- [x] Long-content priming helper integrated for lower probes (`tests/visual/helpers/long-content.ts`)
- [x] Long-page capture guidance documented (`artifacts/long-page-capture-patterns.md`)
- [x] Cross-browser stability log added (`artifacts/cross-browser-stability-log.md`)
- [x] Initial Firefox/WebKit baseline validation completed (component pack + full P0 matrix)
- [x] Weekday CI schedule added to build cross-browser stability signal
- [x] Stability-log helper script added (`npm run test:visual:stability-log`)
- [x] Five non-blocking CI cycles recorded from GitHub workflow dispatch runs
- [x] Default cross-browser mode promoted to `blocking`

### Pending
- [ ] Monitor first blocking cross-browser CI cycle and triage if needed

### Blocked (Needs Target App Inputs)
- [ ] Refine selectors for mobile-menu overlay behavior to support strict CI enforcement
- [x] Overlay investigation notes captured (`artifacts/starter/overlay-investigation.md`)

## Milestones
- Week 1: Deterministic native-snapshot MVP complete
- Week 2: Layout guardrails complete
- Week 3: CI/PR workflow complete
- Week 4+: Advanced expansion complete

## Key Decisions (Updated)
1. Native Playwright snapshots are the default baseline mechanism.
2. Deterministic rendering and page/state manifest are mandatory before broad rollout.
3. Governance for baseline updates is part of MVP, not deferred.
4. Start with Chromium only; add browsers after stability.

## Open Questions
1. Which P1 route should be promoted to P0 after week-1 signal quality review?
2. Preferred artifact retention window in CI?
3. Should full-suite visual runs be nightly or manual-only initially?

## Progress Snapshot
**Current Phase:** 4 of 4 (complete)  
**Plan Health:** On track  
**Last Updated:** 2026-03-06 (cross-browser promoted to blocking after 5 successful non-blocking CI runs)
