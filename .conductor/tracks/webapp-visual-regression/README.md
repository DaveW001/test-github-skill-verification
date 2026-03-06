# WebApp Visual QA and Regression Track

**Track ID:** webapp-visual-regression  
**Status:** In Progress - Phase 1  
**Created:** 2026-03-04

## Quick Links
- [Specification](./spec.md)
- [Plan](./plan.md)
- [Metadata](./metadata.json)
- [Artifacts](./artifacts/)

## What Changed in This Revision
- Shifted to a native Playwright snapshot-first strategy.
- Moved deterministic rendering setup into Phase 1 core work.
- Added required page/state manifest before broad rollout.
- Added baseline governance (approval and rationale) to MVP.
- Added immediate HTML artifact reporting in Phase 1.
- Narrowed early layout checks to high-value heuristics.

## Current Priority
Phase 1 only:
1. Deterministic rendering profile
2. Page/state manifest
3. Native snapshot workflow
4. Viewport and scroll probe coverage
5. Noise controls and governance

## Execution Started
- Manifest template created: `.conductor/tracks/webapp-visual-regression/artifacts/page-state-manifest.template.yaml`
- Initial draft created: `.conductor/tracks/webapp-visual-regression/artifacts/page-state-manifest.draft.yaml`
- Execution runbook created: `.conductor/tracks/webapp-visual-regression/artifacts/phase1-execution-runbook.md`
- Deterministic profile doc created: `.conductor/tracks/webapp-visual-regression/artifacts/deterministic-rendering-profile.md`
- Route/selector intake created: `.conductor/tracks/webapp-visual-regression/artifacts/app-route-selector-intake.md`
- Canonical base URL locked: `http://localhost:3000`
- Initial P0 routes locked: `/` and `/contact`
- Starter kit scaffolded: `.conductor/tracks/webapp-visual-regression/artifacts/starter/`
- Baseline generated and verified: 35/35 passing in starter suite
- Root scripts wired:
  - `npm run test:visual`
  - `npm run test:visual:update`
  - `npm run test:visual:report`
- Active workflow scaffolded: `.github/workflows/visual-regression.yml`
- PR baseline rationale template added: `.github/pull_request_template.md`
- Next execution item: harden mobile overlay selectors and decide when to enable overlay checks by default

## CI Variables
- `VISUAL_APP_BASE_URL`: app URL for CI visual checks (defaults to `http://localhost:3000`)
- `VISUAL_APP_START_COMMAND`: optional command CI can run to start the app before tests

## Phase Overview
- Phase 1: Visual Baseline MVP
- Phase 2: Layout Guardrails
- Phase 3: CI/CD and PR Workflow
- Phase 4: Advanced Expansion

## Primary Use Case
Visual review that catches obvious regressions quickly:
- Off-page or clipped content
- Content hidden under sticky headers
- Spacing drift and layout breaks
- Unintended visual changes across key viewports

## Notes
This track intentionally avoids building custom image processing in the first phase unless native snapshot capabilities are insufficient for a specific verified gap.
