# Stage 8 Conditional Re-validation — Phase A Closeout Readiness

- **Track:** `20260717-dcp-child-session-safety`
- **Validator:** `conductor-track-validator-alt` (`openai/gpt-5.6-sol`, low), independent from executor `zai-coding-plan/glm-5.2`
- **Prior report:** `validation-report-20260719-020453Z.md`
- **Validation time (UTC):** 2026-07-19T02:16:15Z
- **Scope:** Post-fix artifacts only; no source, test, or config edits. No Stage 9 artifact check was performed.

## Closeout Verdict

**Not ready to close; Phase A is not ready to route to Stage 9.** The principal Stage 7 fixes were applied, and product evidence remains qualified green, but reconciliation introduced or left three bookkeeping/provenance inconsistencies. Because this is the single permitted Stage 8 pass, the remaining blockers are recorded in `validation-blockers-20260719-021615Z.md`.

## Evidence Checked

- Prior validation: `C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\validation-report-20260719-020453Z.md`
- Track truth: `plan.md`, `spec.md`, `metadata.json`, `handoff.md`, `handover.md`, `validation-matrix.md`, `execution-log-2026-07-17.md`
- Corrections: `audit-correction-2026-07-19-provenance-reconcile.md`, `audit-correction-2026-07-19-stage6-report-control-chars.md`, `audit-correction-2026-07-18-stage6-retry.md`
- Artifacts: `artifacts/source-map.json`, `artifacts/full-suite-results.json`, `artifacts/rca-evidence.json`, and the RCA blocker artifact
- Indexes: `C:\development\opencode\.conductor\tracks.md` and `C:\development\opencode\.conductor\tracks-ledger.md`
- Stage 8 gate reruns:
  - Corrected 3.3 command: **8 pass / 0 fail**, exit 0.
  - Corrected 3.6 command: **3 pass / 0 fail**, exit 0.
  - Task 0.2 authoritative `source-map.json` check: **FAIL**, because reconciliation added top-level `provenance_history` while the plan still requires `set(d)=={'opencode','dcp'}`.

## Fix Confirmation

1. **0.1 explicitly and honestly deferred — PASS.** `plan.md` marks it `[~]` and `[DEFERRED 2026-07-19]`; the disposition states that 200/22/0 cannot be established without forbidden content-bearing columns, does not claim acceptance, names the waiver/redefinition needed to resume, and points to blocked evidence.
2. **5.2 explicitly and honestly deferred/waived — PASS.** `plan.md` preserves the unmet literal all-zero criterion, records DCP 123/0 and OpenCode 3203/9 plus one sandbox hang, states zero changed-module regressions, identifies the environment required to lift the waiver, and does not claim the full-suite gate passed.
3. **Task counts — PASS.** Numbered plan tasks reconcile to **29 total = 26 completed + 2 deferred + 1 pending Stage 9**. The same counts appear in metadata, handoff, execution log, and both index entries.
4. **Control-character audit correction — PASS.** The historical Stage 6 report remains immutable; the correction names the corrupted tokens and points to readable qualified-green evidence.
5. **Corrected 3.3/3.6 gates — PASS.** Independent bounded reruns produced 8/0 and 3/0 respectively.
6. **Tests remain qualified green — PASS, qualified.** No source/test changes occurred in reconciliation. Preserved evidence remains DCP 123/0, OpenCode changed-module 34/34 and zero changed-module regressions; OpenCode full-suite literal all-zero remains explicitly deferred rather than misreported.
7. **Canonical ledger/index cardinality — PASS.** Exactly one matching row exists in `tracks.md` and exactly one matching entry exists in `tracks-ledger.md`.
8. **F.4 pending Stage 9 — PASS in plan/metadata/handoff.** It is `[~] [PENDING STAGE 9]`, with Stage 9 documentation, mandatory post-doc validation, and terminal closeout still required. No Stage 9 artifact was sought.

## Mismatches Found

1. **`validation-matrix.md` -> expected post-reconciliation truth -> actual stale pre-retry evidence.** Criterion 10 still says DCP exit 1 and OpenCode timeout, although the authoritative retry evidence says DCP 123/0 exit 0 and OpenCode 3203/9 plus one environment hang. Its open-items section still calls 5.2 merely BLOCKED, and its F.4 text says Stage 7/8 are deferred to later agents. Its pinned-source section still lists `45cd8d7` / `85b6f5c`, contradicting reconciled `source-map.json` revisions `c4018482d` / `558e037`. This makes the provenance/bookkeeping correction incomplete.
2. **`tracks-ledger.md` -> expected current disposition language -> actual stale checkbox/stage wording.** The sole canonical entry still says 5.2 was “left [ ]” and F.4 “Stage 7/8 + Stage 9 deferred to later agents.” The plan now uses `[~]`, Stage 8 has run, and only Stage 9 plus terminal closeout remains.
3. **`artifacts/source-map.json` / plan Task 0.2 -> expected authoritative gate to remain valid -> actual regression.** Adding top-level `provenance_history` was auditable and preserves history, but the unchanged Task 0.2 check requires exactly two top-level keys. The authoritative check now raises `AssertionError` while Task 0.2 remains `[x]`.

## Required Fixes Before Close

1. **Bookkeeping-only:** reconcile `validation-matrix.md` to the Stage 6 retry, formal deferrals, current revisions, completed Stage 7/8 state, and pending Stage 9 state. Preserve the qualified-green limitation.
2. **Bookkeeping-only:** update the single `tracks-ledger.md` entry so checkbox/disposition and stage wording match the plan and this Stage 8 result; do not create a second row.
3. **Plan/spec bookkeeping flaw:** make Task 0.2 provenance history compatible with its authoritative acceptance check—prefer updating the check to validate `opencode` and `dcp` while allowing the documented `provenance_history`, then rerun it. Do not delete the preserved history merely to satisfy the old exact-key assertion.
4. **Pipeline stop:** the one re-validation pass is exhausted. Reconcile these blockers before Stage 9; do not claim Phase A ready until the corrected artifacts are deterministically checked by the orchestrator.

## Final Recommendation

Hold Stage 9 routing until the stale matrix and ledger wording are reconciled and the Task 0.2 source-map gate passes with preserved provenance history.