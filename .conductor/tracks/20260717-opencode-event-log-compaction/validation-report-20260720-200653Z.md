# Stage 8 Conditional Re-validation Report

**Track:** `20260717-opencode-event-log-compaction`  
**Validator:** `conductor-track-validator-alt` (OpenAI GPT-5.6 SOL)  
**Generated:** 20260720-200653Z  
**Prior report:** `validation-report-20260720-195430Z.md`  
**Scope:** Capped, read-only re-validation after the single remediation pass. No rollback, live database mutation, OpenCode shutdown, VACUUM, or deletion was performed.

## Closeout Verdict

**Not ready to close.** Four of the five prior fix groups were applied, and deterministic parser/source/type/JSON checks are credible. A material rollback/swap safety overclaim remains: the current acceptance matrix marks open-handle/partial-rename and activation fail-closed criteria complete, but the implementation does not prove those behaviors. Because this is the capped Stage 8 pass, no further remediation loop is authorized here; exact blockers are recorded in `validation-blockers-20260720-200653Z.md`.

## Evidence Checked

- Prior report and remediation artifacts: `validation-report-20260720-195430Z.md`, `execution-log-2026-07-20-stage8-remediation.md`, and both 2026-07-20 audit addenda.
- Current skill surfaces under `C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor`: `SKILL.md`, `tests\test-cases.md`, all 10 PowerShell scripts, `references\rollback.md`.
- Track surfaces: `spec.md`, `plan.md`, `metadata.json`, `acceptance-evidence-matrix-2026-07-20.md`, `next-steps-runbook.md`, Stage 9 artifacts, execution logs, `.conductor\tracks.md`, and `.conductor\tracks-ledger.md`.
- Independent PowerShell parser harness: **10/10 scripts syntax-valid**.
- Exact source test command: **56 pass, 0 fail, 118 assertions, exit 0**.
- `bun run typecheck`: **exit 0**.
- Authoritative JSON parsing: metadata, upstream decision, validator alternation, 14-day batch result, and 7-day batch result all parse. `compaction-result.json` remains explicitly non-authoritative and fails whole-file parsing as expected.
- Targeted privacy/credential/raw payload-key scan across current skill and track text/code: **0 findings**.

## Prior Fix Verification

| Prior required fix | Result | Evidence |
|---|---|---|
| Current 10-script inventory; historical 9-script claims superseded | **PASS** | Exactly 10 `.ps1` files; SKILL inventory lists all 10; test checklist says 10; historical occurrences are either historical records or accompanied by dated parser-fix/reconciliation supersession notes. |
| 25/242,484 labeled reported/non-authoritative; artifact counts retained | **PASS** | Skill, runbook, metadata note, and ledger label the total non-authoritative/user-reported; authoritative counts remain 9/89,223 plus 14/133,259. Historical execution claims are preserved as historical records. |
| Stage 9 and post-doc historical claims superseded | **PASS** | Both 2026-07-17 artifacts contain explicit 2026-07-20 supersession sections and point to current reconciliation/status. |
| Rollback implementation/docs fail closed and coordinate DB/WAL/SHM | **PARTIAL / BLOCKED** | `-Rollback` now blocks detected OpenCode/bun processes and handles DB/WAL/SHM as a set. However, the same activation script's forward path offers force-kill-and-continue rather than fail-closed, has no explicit open-handle probe, no `SupportsShouldProcess`, and no recovery transaction/try-catch for partial multi-file moves. Documentation and matrix overstate these guarantees. |
| Acceptance matrix maps all 42 with honest deferrals | **PARTIAL / BLOCKED** | Matrix has exactly 42 criterion rows and explicitly defers 7.2/7.3. But criteria 33 and 34 are marked `[x] DONE` without evidence for fail-closed forward activation, open-handle refusal, or partial-rename recovery. |

## Bookkeeping Consistency

- `plan.md`: **40 `[x]`, 2 `[~]`, 0 `[ ]`, 42 total**.
- Deferred items: **7.2** post-swap application smoke and **7.3** rollback rehearsal.
- `metadata.json`: valid JSON; `status=closed-with-deferred-followups`, `progress=95.2`, `completedTasks=40`.
- `.conductor\tracks.md`: exactly one current row, aligned to 40/42 and status.
- `.conductor\tracks-ledger.md`: exactly one canonical entry, aligned to status/counts and correctly qualifies reported totals.
- Stage 9 artifact and post-doc artifact exist. Their old terminal claims are explicitly historical/superseded.

## Mismatches Found

1. **Safety implementation -> expected fail-closed activation -> actual force-kill path.** `Activate-CompactedDb.ps1` forward activation detects OpenCode/bun but allows `Read-Host` confirmation followed by `Stop-Process -Force` and continuation. This is not fail-closed behavior.
2. **Acceptance criterion 34 -> expected open-handle/partial-rename protection -> actual unproven behavior.** The script has no explicit file-handle probe and no transactional recovery/try-catch around the ordered DB/WAL/SHM moves. A failure after one move can leave a partial state for manual recovery.
3. **Matrix/documentation -> expected evidence-scoped status -> actual overclaim.** Matrix rows 33 and 34 are `[x] DONE`; rollback.md/runbook describe fail-closed coordinated handling without distinguishing process-name detection from open-handle detection or documenting partial-move recovery limits.

## Required Fixes Before Close

1. **Deliverable/safety:** make forward activation fail closed when OpenCode/bun or other DB writers/open handles are detected; do not offer force-kill-and-continue in the activation script.
2. **Deliverable/safety:** add bounded open-handle/write-lock refusal and recoverable/transaction-like handling for partial DB/WAL/SHM move failures, or route all activation/restore operations exclusively through an implementation that already supplies those guarantees.
3. **Bookkeeping/evidence:** until independently tested, change acceptance-matrix criteria 33/34 from DONE to PARTIAL/DEFERRED and state exactly which behaviors are implemented versus unverified. Keep 7.2/7.3 deferred.

## Stage 9 / Terminal Gate

Stage 9 historical doc-update and post-doc-validation artifacts exist and have valid supersession addenda, but Stage 9 cannot be declared satisfied by this addendum while the current rollback/activation safety documentation overclaims implementation evidence. A closeout-ready verdict is therefore withheld.

## Final Recommendation

Stop at the capped Stage 8 blocker state; do not close until the activation/open-handle/partial-move guarantees are implemented or honestly deferred and the matrix is corrected.

## Tool Preflight

The native file tool failed at session start with `Bun is not defined`; the session switched to bounded PowerShell-first inspection and did not retry native file tools.
