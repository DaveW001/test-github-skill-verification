# Storybook Adoption Path for Visual QA

## Goal
Add optional component-level visual coverage without coupling all checks to route-level pages.

## Phase A: Synthetic Component Pack (now)
- Use `tests/visual/components.synthetic.spec.ts` as a stable component token check.
- Keep this pack lightweight and deterministic.

## Phase B: Storybook Integration (optional)
1. Add Storybook to target app and define core stories for P0 components.
2. Add a dedicated Playwright spec to open Storybook iframe URLs and snapshot key states.
3. Keep component snapshots separate from route snapshots.

## Suggested File Layout
- `tests/visual/components.storybook.spec.ts`
- `artifacts/storybook-component-manifest.yaml`

## CI Recommendation
- Start in non-blocking mode for component snapshots.
- Promote to blocking once snapshots are stable across 1-2 weeks.

## Governance
- Reuse baseline rationale process for component snapshot updates.
- Require explicit reviewer note when visual token changes are intentional.
