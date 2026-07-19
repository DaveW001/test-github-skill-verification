# Stage 7 Validation Report: 20260715-minimax-m3-half-routing

**Track:** 20260715-minimax-m3-half-routing
**Validator model:** opencode-go/minimax-m3 (Stage 7, per file frontmatter)
**Date:** 2026-07-15T23:54:30Z
**Stage:** 7 (independent re-validation, M3 cross-family from Qwen executor)
**Mode:** bookkeeping direct (1 -> 5 -> 7 -> 9; Stage 9 waived by executor)
**Tooling:** PowerShell-first via bash; native file tools down (Bun is not defined)

## Closeout Verdict

**Not ready to close. Material mismatch: the 50%-usage target is not met and the indivisible-count exception is only partially justified. Route back to Stage 5 for precise remediation before re-validation.**

Minor follow-ups: bookkeeping indices (tracks.md, tracks-ledger.md) are stale; plan task 2.2 acceptance check is now expected to be false post-3.1 (it is meant to fire on the pending snapshot, not the post-approval snapshot).

## Evidence Checked (fully qualified Windows paths)

Track artifacts (all under C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\):

- preflight.json - 38 Git roots enumerated; OpenCode 1.18.1; PowerShell 7.5.8; UTC 2026-07-15T23:34:44Z.
- baseline-manifest.json - 3 target files hashed (plan-reviewer, test-runner, validator); bulk_restore_forbidden=true; preserve_preexisting_changes=true; preexisting_git_status captured.
- routing-decision.md - Installed version 1.18.1; "Unsupported by verified evidence"; selected mechanism = fixed pins with paired agents and stage-mapping invocation rule; openai/gpt-5.6 cited.
- m3-inventory.json - 3 active M3 pins (plan-reviewer, test-runner, validator); 220 historical hits (all in .conductor artifacts); C:\Users\DaveWitkin\.config\opencode\agent in scanned_roots; C:\Users\DaveWitkin\.config\opencode\agents in missing_roots; unreadable_paths empty.
- approved-routing-map.json - approval_status=approved; 1 assignment changed (test-runner -> openai/gpt-5.6-terra medium); 2 retained (plan-reviewer, validator); indivisible_count_exception populated; tera_ratio=0.333; map_hash present.
- parse-validation.json - 2 files, all status=ok, all exit_code=0.
- post-change-inventory.json - coverage_complete=true; unexplained_active_count=0; historical_unchanged_count=220; unreadable_paths=0.
- diversity-validation.json - status=ok; same_family_pair_count=0; auditable_selection_count=3 == assignment_count; indivisible_count_exception populated.
- rollback-validation.json - 1 file entry (conductor-test-runner.md): backup_exists=true, pre_hash_matches=true, restore_command present, post_restore_hash_command present.
- restart-decision.json - restart_required=true; evidence list of 3 items; safe_to_test_now=false; reason populated.
- runtime-validation.md - all required sections present; verdict = "runtime blocked: Error: Session not found (pre-existing)".
- final-validation.md - all 10 required sections present; GLM-5.1 and Qwen both cited.
- execution-log-2026-07-15.md - 16/16 tasks recorded as [x]; model-tier deviation documented; 1 anomaly recorded.

Edited source files (cross-checked against approved-routing-map.json assignments):

- C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md - frontmatter: model: openai/gpt-5.6-terra, variant: medium. Body still says "Runs on MiniMax M3" (stale description; not deliverable-blocking). Current SHA256 FCCFBADBB490D4CD7016D4EE7318E11CE5F444D2A809819053D8CD55A5E8E8B6.
- C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md.bak-20260715-194208 - SHA256 7293BBC60F1F0AD76913A0DEC23F55B15D997414810987CB4C00AB101F5274C4 (matches baseline-manifest pre_hash).
- C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md - contains all required substrings: zai-coding-plan/glm-5.2, zai-coding-plan/glm-5.1, opencode-go/qwen3.7-plus, GLM-5.2 quota exhausted, start with GLM-5.1, then Qwen.
- C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md.bak-20260715-194257 - SHA256 DA8BC738C1FBEC98AF1705123BE5E6B77BE013E71F4750D9CFD29FFC2D0A87AA.

Active agent frontmatter re-scan (independent verification):

- conductor-plan-reviewer.md - frontmatter pins model: opencode-go/minimax-m3 (no variant).
- conductor-track-validator.md - frontmatter pins model: opencode-go/minimax-m3 (no variant).
- conductor-test-runner.md - frontmatter pins model: openai/gpt-5.6-terra, variant: medium.
- conductor-pipeline-orchestrator.md - frontmatter pins model: zai-coding-plan/glm-5.2, variant: high (not M3; the one body mention is a documentation reference to the diversity log).
- No other active agent in C:\Users\DaveWitkin\.config\opencode\agent has model: opencode-go/minimax-m3 in frontmatter.

Index files (cross-checked against metadata.json):

- C:\development\opencode\.conductor\tracks.md - exactly 1 row for 20260715-minimax-m3-half-routing; row shows Status=planned, Completed blank.
- C:\development\opencode\.conductor\tracks-ledger.md - exactly 1 entry for 20260715-minimax-m3-half-routing; entry shows Phase=planning ready 2026-07-15.
- C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\metadata.json - status=executed-deterministic-complete-runtime-pending, phase=stage-5-executed, completed_tasks=16, total_tasks=16, pipeline_mode=bookkeeping, execution_model=opencode-go/qwen3.7-plus, restart_required=true.

C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl - 2 prior records for this track (Stage 1 skill_use not_found warn; Stage 5 model-fallback warn). No new anomaly was appended for the 50% mismatch by the executor.

Acceptance check dry-runs (executed against the real artifacts; all return True except where noted):

| Plan task | Check | Result |
|---|---|---|
| 0.1 | preflight.json fields populated, includes C:\development\opencode in git_roots | True |
| 0.2 | baseline-manifest flags + preexisting_git_status + targets | True |
| 1.1 | routing-decision.md has 6 required sections, "Unsupported by verified evidence" or "Supported", and "openai/gpt-5.6" | True |
| 2.1 | m3-inventory records have all 6 fields, scanned_roots includes user agent dir, missing/unreadable present | True |
| 2.2 | approved-routing-map approval_status=pending, ratio 40-60% or indivisible_count_exception, all assignments have invocation_rule + diversity_counterpart | False (approval_status is now "approved" because task 3.1 has run; this is the expected post-3.1 state, not a regression) |
| 3.1 | approved-routing-map approval_status=approved + approved_at + approved_summary + map_hash | True |
| 3.2 | each approved assignment's path contains model: <new_model> and variant: <new_variant> if non-empty | True |
| 3.3 | pipeline_files concatenation contains the 5 required substrings | True |
| 4.1 | parse-validation all files status=ok and exit_code=0 | True |
| 4.2 | post-change-inventory coverage_complete=true, unexplained_active_count=0, historical_unchanged_count present, unreadable_paths=0 | True |
| 4.3 | diversity-validation status=ok, same_family_pair_count=0, auditable_selection_count==assignment_count, ratio 40-60% or indivisible_count_exception | True (indivisible_count_exception populated) |
| 4.4 | rollback-validation every file has backup_exists, pre_hash_matches, restore_command, post_restore_hash_command | True |
| 5.1 | restart-decision has restart_required (non-null), evidence (>=1), safe_to_test_now, reason | True |
| 5.2 | runtime-validation has 5 required sections, verdict contains "runtime passed" OR "runtime blocked: Error: Session not found" | True (verdict = "runtime blocked: Error: Session not found (pre-existing)") |
| 5.3 | final-validation has 10 required sections + GLM-5.1 + Qwen | True |
| 5.4 | exactly 1 row in tracks.md, exactly 1 row in tracks-ledger.md, metadata.track_id matches, completed_tasks <= total_tasks, pipeline_mode=bookkeeping | True |

GLM non-invocation check (cross-validated): Stage 5 used opencode-go/qwen3.7-plus (Tier 3) directly. No zai-coding-plan/glm-5.2 or zai-coding-plan/glm-5.1 invocation. SKILL.md preserves the canonical chain and adds the operational note. Stage 7 validation used PowerShell/Get-Content via bash (no model invocation). No GLM models called during this validation.

## Mismatches Found

### M-1 (MATERIAL, deliverable) - 50%-usage target not met; indivisible_count_exception only partially justified

User intent (verbatim): "reduce explicit MiniMax M3 use approximately 50%". User's explicit Stage 7 instruction: "do not accept a static 1/3 replacement as '50%' unless the artifacts prove how ongoing usage will approximate half".

Actual state of approved-routing-map.json and diversity-validation.json:
- 3 active M3 assignments pre-change. 1 changed to Tera Medium (test-runner). 2 retained (plan-reviewer, validator).
- tera_ratio = 1/3 = 0.333. M3 reduction = 33% (3 -> 2).
- 33% Tera is below the 40-60% acceptance gate.
- indivisible_count_exception documents only the Stage 2 plan-reviewer as ineligible: "creator counterpart is openai/gpt-5.6-sol (same OpenAI family)".
- The Stage 7 validator's diversity_counterpart is "conductor-track-executor (Stage 5, GLM)" and the diversity table in routing-decision.md explicitly states "Stage 5 (GLM) vs Stage 7 (MiniMax): different families. OK" - so changing the validator to Tera (OpenAI family) would still produce a different-family pair (GLM != OpenAI). No diversity constraint blocks changing the validator.
- The map itself acknowledges two feasible splits: "The nearest possible split is 1/3 (33%) or 2/3 (67%). Selected: 1/3 with Stage 6 test-runner changed." No reason is given for selecting 1/3 over 2/3.

Why this is material: the user-stated acceptance criterion is "approximately 50%". A 33% Tera ratio / 33% M3 reduction is 17 pp off the target. A 67% Tera ratio / 67% M3 reduction (changing the validator as well) is also 17 pp off the target. The executor chose the more conservative (less-M3-reducing) option without justification. The user explicitly flagged static 1/3 as not "50%" without a how-it-approximates-half argument. Neither option, on its own, is a deterministic mechanism that approximates 50% across ongoing usage; the choice between them is what determines whether the deliverable meets intent.

### M-2 (bookkeeping-only) - tracks.md row stale

C:\development\opencode\.conductor\tracks.md row for 20260715-minimax-m3-half-routing:
- Status: planned
- Completed: (blank)

metadata.json actual:
- status: executed-deterministic-complete-runtime-pending
- executed_at: 2026-07-15T23:46:21Z

The stage-5 bookkeeping sync (Task 5.4) was not applied to tracks.md. Index does not reflect the executed state.

### M-3 (bookkeeping-only) - tracks-ledger.md row stale

C:\development\opencode\.conductor\tracks-ledger.md entry for 20260715-minimax-m3-half-routing:
- Phase: planning ready 2026-07-15

metadata.json actual:
- phase: stage-5-executed

The stage-5 bookkeeping sync (Task 5.4) was not applied to tracks-ledger.md. Ledger does not reflect the executed state.

### M-4 (plan-text, not blocking) - Plan task 2.2 acceptance check is post-3.1 false by design

Plan task 2.2 authoritative acceptance check asserts approval_status -eq 'pending'. After task 3.1 has run, the file legitimately has approval_status -eq 'approved'. The check is meant to fire at the state of the artifact immediately after task 2.2 completes; it is expected to be false after task 3.1. This is a plan-text style issue (check was written for the pre-approval snapshot), not a real regression. Worth noting so the orchestrator does not re-flag the same file in a future re-run.

## Required Fixes Before Close

Classify each per the Stage 7 output format (bookkeeping-only / deliverable / plan-text).

1. (deliverable) Route back to Stage 5 - either change conductor-track-validator to openai/gpt-5.6-terra (medium) and update approved-routing-map + diversity-validation + post-change-inventory + parse-validation + rollback-validation + final-validation + execution-log, OR add an explicit rationale in approved-routing-map.json indivisible_count_exception AND diversity-validation.json explaining why conductor-track-validator cannot be changed to Tera despite the GLM != OpenAI family difference. Without this, the 50% target is asserted but not met and the indivisible exception is only half-justified. If validator is changed: new tera_ratio=2/3=0.667 (17 pp above 50%) and the indivisible_count_exception should be updated to state that the nearest 50%-approximating split under diversity constraints is 2/3. If validator is retained: the exception must justify why 1/3 is the chosen split, not just enumerate 1/3 vs 2/3. Either resolution must also re-document how ongoing usage will approximate half (per user instruction), not just how the static assignment looks at one moment.

2. (bookkeeping-only) Upsert C:\development\opencode\.conductor\tracks.md row: change Status to executed-deterministic-complete-runtime-pending and Completed to 2026-07-15. Use upsert (check-then-update-in-place), do not duplicate. Then re-run the task 5.4 acceptance check.

3. (bookkeeping-only) Upsert C:\development\opencode\.conductor\tracks-ledger.md entry: change Phase to executed-deterministic-complete-runtime-pending 2026-07-15 (runtime-pending-restart). Use upsert, do not duplicate. Then re-run the task 5.4 acceptance check.

4. (plan-text, non-blocking) Note in execution-log or audit-correction that the task 2.2 authoritative acceptance check is meant to fire on the pre-3.1 snapshot; the post-3.1 False is expected and not a regression. Future re-runs of the Stage 5 acceptance suite should not re-flag the approved-routing-map.json file for "approval_status=pending".

5. (deliverable, after M-1 fix) Re-run the affected acceptance checks: 2.2 (will now need indivisible_count_exception populated, and the per-assignment invocation_rule/diversity_counterpart constraints), 3.2 (every assignment's path must contain the new model/variant), 4.2 (post-change-inventory must show 0 unexplained M3 active), 4.3 (diversity validation must show 0 same-family pairs under the new assignment set), 4.4 (rollback validation must list a backup for every newly changed file), 5.3 (final-validation must reflect new ratio), 5.4 (tracks.md / tracks-ledger.md / metadata.json in sync). All must return True on dry-run.

6. (audit-trail) Append one seven-key JSONL anomaly record to C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl for the 50%-target material mismatch (this validation finding). Schema per references/anomaly-logging.md. No truncation; one append; one record per observed anomaly.

## Final Recommendation

**Route back to Stage 5 with the remediation in M-1. After Stage 5 produces a revised approved-routing-map + supporting artifacts and the bookkeeping is upserted in M-2 / M-3, this track can be re-validated. The deliverable is currently correct in shape (deterministic checks all pass) but does not yet meet the user-stated 50%-usage target and the bookkeeping has not been synchronized to the executed state.**

---
**Author:** conductor-track-validator (Stage 7) - opencode-go/minimax-m3
**Stage:** 7
**Date:** 2026-07-15T23:54:30Z
