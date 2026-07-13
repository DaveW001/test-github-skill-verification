# Spec

## Track
- Track ID: `20260706-bookkeeping-smoke-test`
- Title: Bookkeeping Smoke Test Marker
- Track type: `bookkeeping`
- Created: 2026-07-06

## Goal / Outcome
Create a deterministic bookkeeping smoke-test marker file at `.conductor/smoke-test-4.2-bookkeeping.md` containing the exact requested markdown body.

## Constraints / Non-Goals
- Do not modify application source code, tests, build configuration, package metadata, or schemas.
- Do not create or invoke unit tests; this repo track declares `test_framework: none` and `test_command: n/a`.
- Do not run Stage 2 review, Stage 4 test writing, Stage 4b RED gate, Stage 6 test runner, or Stage 8 re-validation for this bookkeeping track unless the orchestrator explicitly overrides.
- Use shell-first PowerShell commands because native file tools are unavailable in this host session.
- Keep all shell commands bounded and non-interactive.

## Definition of Done
- `.conductor/smoke-test-4.2-bookkeeping.md` exists.
- The marker file content exactly equals:

```markdown
# Bookkeeping Smoke Test Marker

The 9-stage Conductor pipeline bookkeeping branch was smoke-tested on 2026-07-06.
This track type skips TDD stages (4 Write Tests / 4b RED-gate / 6 Run Tests) and reaches Stage 9 (Documentation / Closeout).
```

- `.conductor/tracks.md` has exactly one up-to-date row for `20260706-bookkeeping-smoke-test`.
- `.conductor/tracks-ledger.md` has exactly one up-to-date row for `20260706-bookkeeping-smoke-test`.
- `.conductor/tracks/20260706-bookkeeping-smoke-test/plan.md` is synchronized with completed task states.
- `.conductor/tracks/20260706-bookkeeping-smoke-test/metadata.json` is synchronized with final status/progress.
- An execution log exists in `.conductor/tracks/20260706-bookkeeping-smoke-test/` and records validation, skipped stages, and deviations, if any.

## Requirements
- [ ] Create `.conductor/smoke-test-4.2-bookkeeping.md` with exactly the requested body content.
- [ ] Preserve the blank line between the heading and first paragraph.
- [ ] Preserve the final period at the end of the second paragraph.
- [ ] Upsert Conductor track rows during execution closeout without creating duplicates.
- [ ] Record closeout evidence in the active track folder.

## Non-Requirements
- [ ] No application code changes.
- [ ] No test harness creation.
- [ ] No unit/integration test execution.
- [ ] No public API or setup documentation changes beyond closeout artifacts, unless Stage 9 determines a non-contractual note is needed.

## Acceptance Criteria
- [ ] The authoritative content comparison command in `plan.md` returns `True` for `.conductor/smoke-test-4.2-bookkeeping.md`.
- [ ] The ledger duplicate-check commands in `plan.md` return count `1` for both `.conductor/tracks.md` and `.conductor/tracks-ledger.md`.
- [ ] The final metadata status is `executed-complete`, with `track_type: bookkeeping`, `pipeline_mode: bookkeeping`, and `pipeline_path: [1, 5, 7, 9]`.
- [ ] Stage 9 records a documentation/post-doc-validation waiver or non-contractual documentation closeout note for this docs-only bookkeeping track.
