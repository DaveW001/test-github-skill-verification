# Audit Correction - Stage 8 Bookkeeping Fixes (2026-07-19)

**Track:** 20260717-dcp-child-session-safety  
**Scope:** Final user-authorized bookkeeping correction after the single permitted Stage 8 pass (`validation-report-20260719-021615Z.md` / `validation-blockers-20260719-021615Z.md`). **No source, test, or config behavior changes. No completion claims changed.** Responds to the three documented blockers.

## Blocker 1 - `validation-matrix.md` stale post-retry evidence - FIXED
Reconciled `validation-matrix.md` to current truth:
- Criterion 10 now reflects the Stage 6 retry result: DCP full = exit 0 (123 pass / 0 fail); OpenCode full = exit 1 (3203 pass / 9 pre-existing sandbox-env failures + 1 live-subprocess hang, 0 changed-module regressions). Status QUALIFIED-GREEN (was "DCP=1 / opencode=TIMEOUT / PARTIAL-BLOCKED").
- Open/pending section: 0.1 = DEFERRED (was "BLOCKED"); 5.2 = DEFERRED/WAIVED with user-authorized-continuation rationale and future required environment (was "BLOCKED"); F.4 = PENDING STAGE 9 with Stage 7 + Stage 8 complete (was "deferred to later agents").
- Pipeline-state header added: product/changed-module acceptance GREEN; DCP 123/0; OpenCode 34/34 changed-module + 3203 full; Stage 7 + Stage 8 COMPLETE; F.4 PENDING STAGE 9.
- Current source revisions: opencode `c4018482d` (clean), dcp `558e037` (dirty test-only `tests/prompts.test.ts`); prior pinned bases preserved in `artifacts/source-map-provenance-history.json`.

## Blocker 2 - `tracks-ledger.md` stale checkbox/stage wording - FIXED
Corrected the single canonical entry (still exactly one row) so disposition/stage wording matches the plan and Stage 8 result:
- 5.2 wording: "left [ ] per no-falsification" -> "deferred [~] (user-authorized continuation; not claimed passed)".
- F.4 wording: "Stage 7/8 + Stage 9 deferred to later agents" -> "F.4 pending Stage 9 (Stage 7 + Stage 8 complete)".
- Task counts unchanged and accurate: 29 total = 26 completed + 2 deferred (0.1, 5.2) + 1 pending Stage 9 (F.4).

## Blocker 3 - Task 0.2 `source-map.json` top-level shape - FIXED
Restored `artifacts/source-map.json` to its exact authoritative top-level shape `{opencode, dcp}` (the Stage 7 reconciliation had added a top-level `provenance_history` key, which broke the Task 0.2 `set(d)=={'opencode','dcp'}` assertion). Per user instruction, the provenance history was moved to a separate track artifact `artifacts/source-map-provenance-history.json` (no top-level keys added to source-map.json). Reconciled commit/dirty values retained (opencode `c4018482d` clean; dcp `558e037` dirty test-only). The prior provenance audit correction (`audit-correction-2026-07-19-provenance-reconcile.md`) was updated to reference the separate history file.

**Task 0.2 acceptance (exact plan command) rerun:** `python -c "...assert set(d)=={'opencode','dcp'} and all(...); print('PASS source-map')"` -> **PASS source-map**, exit 0.

## What was NOT changed
- No source, test, or config behavior changes.
- No completion claims changed (0.1 and 5.2 remain explicitly deferred `[~]`; F.4 remains `[~] PENDING STAGE 9`; 26 completed unchanged).
- F.4 is NOT marked complete; Stage 8 was NOT rerun; Stage 9 has NOT run.
- Immutable historical reports (`test-run-report-2026-07-18-212156.md`, prior validation reports) not edited.