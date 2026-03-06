# Spec: WebApp Visual QA and Regression Track

## Goal
Build a practical visual QA workflow for web pages that catches obvious UI regressions early: overflow, content hidden under sticky headers, spacing drift, and unintended visual changes.

This track prioritizes reliable human-reviewable visual checks over complex custom image-processing infrastructure.

## Strategy
- Use Playwright native visual snapshots first (`toHaveScreenshot`) for baseline and diff behavior.
- Make rendering deterministic before comparisons to reduce noise.
- Cover real pages and states via an explicit page/state manifest.
- Add lightweight layout heuristics (sticky overlap, overflow, off-page) where screenshot diffs are not enough.
- Add governance so baseline updates are controlled and auditable.

## Requirements

### Phase 1: Visual Baseline MVP (Execution Priority)
- [ ] **Deterministic rendering profile**
  - Freeze locale/timezone for tests
  - Disable or stabilize animations/transitions during capture
  - Wait for fonts and key images before screenshot
  - Mask volatile regions (timestamps, rotating banners, random IDs)
- [ ] **Page/state manifest**
  - Define explicit route inventory and capture states
  - Include core states: default, empty, loading, error, modal/open nav, long-content scroll
  - Define owners and review criticality for each page/state
- [ ] **Playwright-native visual comparisons**
  - Use snapshot assertions and update flow (`--update-snapshots`)
  - Configure project-wide screenshot expectations (`maxDiffPixels` or ratio)
  - Start with Chromium for deterministic baseline generation
- [ ] **Viewport matrix for responsive QA**
  - Support `mobile-narrow` (360x800), `mobile` (390x844), `tablet` (768x1024), `laptop` (1366x768), `desktop` (1920x1080)
- [ ] **Baseline governance v1**
  - Define who can approve baseline updates
  - Require rationale for baseline changes in PR
  - Block silent baseline churn
- [ ] **Human-readable reporting in Phase 1**
  - Enable HTML report artifact output immediately
  - Ensure failed runs attach snapshots and diffs for quick review
- [ ] **Skill documentation updates**
  - Add quick-start workflow for local visual QA
  - Add triage workflow for intentional vs accidental changes

### Phase 2: Layout Guardrails (Targeted Heuristics)
- [ ] **Sticky/fixed overlap probes**
  - Scroll-aware checks at multiple depths
  - Detect likely obscured anchors/headings/CTA elements
- [ ] **Overflow/off-page detection**
  - Detect horizontal scroll introduction
  - Detect elements escaping viewport/container bounds
- [ ] **Severity classification**
  - Classify findings as `blocker`, `warn`, or `info`
- [ ] **Noise controls**
  - Per-page thresholds
  - Optional retry-once before fail for flaky captures
  - Central ignore selector list

### Phase 3: CI/CD and PR Workflow
- [ ] **GitHub Actions workflow** for visual checks on PR
- [ ] **Artifact retention** for snapshots, diffs, and HTML report
- [ ] **PR triage template**
  - What changed
  - Intentional/unintentional
  - Baseline update justification
- [ ] **Parallel execution** for viewport matrix
- [ ] **Manual baseline update workflow** with explicit approval path

### Phase 4: Advanced Coverage
- [ ] Cross-browser visual checks (Firefox, WebKit) after Chromium stabilizes
- [ ] Component-level visual checks (optional Storybook integration)
- [ ] Accessibility visual checks (contrast-focused)
- [ ] Lazy-loading and infinite-scroll capture helpers

## Non-Requirements
- [ ] Replacing Playwright snapshot engine with custom diff tooling in Phase 1
- [ ] AI-generated tests or self-healing selectors
- [ ] Full functional/API testing expansion
- [ ] Large custom spacing inference engine in early phases
- [ ] Third-party paid visual platforms in initial rollout

## Acceptance Criteria

### Phase 1 Acceptance Criteria
- [ ] Deterministic profile documented and applied consistently
- [ ] Page/state manifest exists and is reviewed
- [ ] Snapshot assertions run locally for defined pages/states and viewports
- [ ] Baseline creation and update process is documented and tested
- [ ] HTML report with visual failures is generated and reviewable
- [ ] Skill docs include local run, review, and baseline update flows

### Phase 2 Acceptance Criteria
- [ ] Sticky overlap checks catch known synthetic examples
- [ ] Overflow/off-page checks catch known synthetic examples
- [ ] Severity model appears in outputs and docs
- [ ] Per-page threshold/noise controls are documented and usable

### Phase 3 Acceptance Criteria
- [ ] PR workflow runs visual checks on pull requests
- [ ] Failed runs publish usable artifacts (diffs + report)
- [ ] Baseline updates require explicit workflow and approval

### Phase 4 Acceptance Criteria
- [ ] Cross-browser projects enabled and documented
- [ ] Component-level visual examples provided
- [ ] Accessibility visual checks documented

## Technical Specifications

### Preferred Baseline Approach
- Primary: Playwright snapshot assertions and built-in diff behavior.
- Secondary (optional later): custom comparison helpers only when native behavior is insufficient for a targeted case.

### Viewport Matrix (Phase 1)
- `mobile-narrow`: 360x800
- `mobile`: 390x844
- `tablet`: 768x1024
- `laptop`: 1366x768
- `desktop`: 1920x1080

### State Matrix (minimum)
- `default`
- `empty`
- `loading`
- `error`
- `overlay` (modal/drawer/open menu)
- `long-content` (scroll positions: top, mid, lower)

### Triage Severity
- `blocker`: content hidden, critical CTA obscured, major overflow
- `warn`: noticeable spacing or alignment drift, non-critical overlap
- `info`: small cosmetic diffs under threshold review band

## Risks and Mitigation

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Snapshot noise from dynamic content | High | Deterministic profile, masks, fixed locale/timezone |
| Baseline drift accepted accidentally | High | Governance, approval rules, PR template |
| Too much initial complexity | Medium | Native snapshot-first approach in Phase 1 |
| CI runtime growth from viewport matrix | Medium | Parallel jobs, selective critical page set |

## Dependencies
- Playwright test runner and snapshot assertions
- Existing local server helper workflow
- GitHub Actions for CI rollout in Phase 3

## Timeline
- **Phase 1 (Week 1):** Deterministic baseline MVP using native snapshots
- **Phase 2 (Week 2):** Focused layout guardrails
- **Phase 3 (Week 3):** CI/CD and PR governance workflow
- **Phase 4 (Week 4+):** Advanced coverage and expansion
