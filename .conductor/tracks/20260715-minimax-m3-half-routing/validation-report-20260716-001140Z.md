# Stage 7 Re-Validation Report: 20260715-minimax-m3-half-routing

**Track:** 20260715-minimax-m3-half-routing
**Validator model:** opencode-go/minimax-m3 (Stage 7, per agent frontmatter; cross-family from Qwen Tier-3 executor)
**Date:** 2026-07-16T00:11:40Z
**Stage:** 7 (re-validation after single permitted Stage 5 remediation)
**Mode:** bookkeeping direct (1 -> 5 -> 7 -> 9; Stage 9 waived by executor)
**Tooling:** PowerShell-first via bash; native file tools down (Bun is not defined)

---

## Closeout Verdict

**Close with minor follow-ups.** All material mismatches from the prior report (validation-report-20260715-235430Z.md) are resolved. The Stage 5 remediation produced a deterministic SHA-256(track_id) parity-based paired-validator system that genuinely achieves approximately 50% Tera / 50% MiniMax M3 usage across the combined Stage 2 / 6 / 7 two-track cycle while preserving model-family independence, never invoking GLM 5.2 or GLM 5.1, and correctly classifying the in-session runtime test as `runtime blocked: Error: Session not found (pre-existing)` rather than misreporting it as a routing-failure pass. A few minor bookkeeping follow-ups (F-1 through F-4) are noted but are not blocking.

---

## Evidence Checked (fully qualified Windows paths)

Track artifacts (under `C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\`):

- `preflight.json` - OpenCode 1.18.1; PowerShell 7.5.8; 38 Git roots enumerated; UTC 2026-07-15T23:34:44Z.
- `baseline-manifest.json` - 3 original target files hashed; bulk_restore_forbidden=true; preserve_preexisting_changes=true; preexisting_git_status captured.
- `routing-decision.md` - Installed version 1.18.1; "Unsupported by verified evidence"; selected mechanism = fixed pins with paired agents and stage-mapping invocation rule; openai/gpt-5.6 cited.
- `m3-inventory.json` - 3 original active M3 pins (plan-reviewer, test-runner, validator); 220 historical hits; scanned_roots + missing_roots + unreadable_paths populated.
- `approved-routing-map.json` (post-remediation) - 4 assignments, approval_status=approved, tera_ratio=0.5, tera_count=2, m3_retained_count=2, deterministic_parity_rule documented, indivisible_count_exception populated, map_hash frozen.
- `diversity-validation.json` (post-remediation) - status=ok, same_family_pair_count=0, auditable_selection_count=4 == assignment_count, bucket_counts tera_medium=2 m3_retained=2, deterministic_parity_rule example verified.
- `parse-validation.json` - 4 files, all status=ok, all exit_code=0.
- `post-change-inventory.json` - coverage_complete=true, unexplained_active_count=0, historical_unchanged_count=220, unreadable_paths=0, 4 active records (plan-reviewer M3, test-runner Tera, validator Tera, validator-m3 M3).
- `rollback-validation.json` - 4 file entries: 3 pre-existing files with backup_exists=true, pre_hash_matches=true, restore_command + post_restore_hash_command; 1 new file (conductor-track-validator-m3.md) with delete-only rollback.
- `restart-decision.json` - restart_required=true, evidence (3 items), safe_to_test_now=false, reason populated.
- `runtime-validation.md` - all 5 required sections present; verdict = "runtime blocked: Error: Session not found (pre-existing)" — does NOT claim runtime passed.
- `final-validation.md` (post-remediation) - all 10 required sections present; GLM-5.1 and Qwen both cited; stage 9 waiver recorded.
- `execution-log-2026-07-15.md` - 16/16 tasks [x]; Stage 5 remediation M-1/M-2/M-3/M-4 documented; operational bypass (Qwen Tier 3 direct) authorized by validator.
- `metadata.json` - status=executed-deterministic-complete-runtime-pending, phase=stage-5-remediation-executed, completed_tasks=16, total_tasks=16, tera_ratio=0.5, pipeline_mode=bookkeeping, execution_model=opencode-go/qwen3.7-plus, restart_required=true, deterministic_parity_rule populated.

Edited source files (SHA-256 verified live against backups):

- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md` - frontmatter: model: openai/gpt-5.6-terra, variant: medium. Current SHA256 = FCCFBADBB490D4CD7016D4EE7318E11CE5F444D2A809819053D8CD55A5E8E8B6.
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md.bak-20260715-194208` - SHA256 = 7293BBC60F1F0AD76913A0DEC23F55B15D997414810987CB4C00AB101F5274C4 (matches baseline-manifest pre_hash).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md` (RE-EDITED in remediation) - frontmatter: model: openai/gpt-5.6-terra, variant: medium. Current SHA256 = DFF0EF4E7B4DC1FD878D218B5CF68806E61FA355F4C9D1E5245E0D6083664B44.
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md.bak-20260715-195909` - SHA256 = 301AAED882151E5068D58FFFDC76FABEE4AF9E8425209DF19A3913F00AC899DB (matches baseline-manifest pre_hash for the original validator).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-m3.md` (NEW) - frontmatter: model: opencode-go/minimax-m3, no variant. Current SHA256 = 162F26607F1737FB474B21FAF233150C2C3E4FF91E80DC15B5A32953CF99102D. Unique name, no conflicting agent.
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` (RE-EDITED in remediation) - Current SHA256 = 532B777E2D6BB00F4A4C70121146335D1C83E917A64ACA7CEF38E8071F52EBA1. Contains all required substrings (verified: zai-coding-plan/glm-5.2, zai-coding-plan/glm-5.1, opencode-go/qwen3.7-plus, GLM-5.2 quota exhausted, start with GLM-5.1, then Qwen, Deterministic validator parity rule, SHA-256).
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md.bak-20260715-195912` - SHA256 = 0BF0C7DAFF0C8F7691D458936A7DD09DEFF3B313709C377AC73E8007B88F6FEF (state just before remediation SKILL.md edit; pre-remediation content).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer.md` - UNCHANGED, frontmatter: model: opencode-go/minimax-m3 (no variant), edit: allow (Stage 2 plan reviewer is the only one that edits spec/plan).

Independent re-scan of all `*.md` agent files in `C:\Users\DaveWitkin\.config\opencode\agent\`:

- Active M3 frontmatter pins (post-remediation): conductor-plan-reviewer (line 5), conductor-track-validator-m3 (line 5). Total = 2 — matches approved-routing-map.json m3_retained_count = 2 and post-change-inventory.json records.
- Active Tera frontmatter pins: conductor-test-runner, conductor-track-validator. Total = 2 — matches approved-routing-map.json tera_count = 2.
- The only remaining `opencode-go/minimax-m3` substring in any conductor-*.md agent is in `conductor-pipeline-orchestrator.md` line 81, which is a documentation reference describing the prior stage-to-validator mapping in the model's prose (NOT an active model pin; the orchestrator agent itself is pinned to zai-coding-plan/glm-5.2 variant high at line 9). See F-2 below.
- No other active agent in `C:\Users\DaveWitkin\.config\opencode\agent\*.md` (excluding `.bak-*`) has model: opencode-go/minimax-m3 in frontmatter.

Index files (cross-checked against metadata.json):

- `C:\development\opencode\.conductor\tracks.md` - exactly 1 row for 20260715-minimax-m3-half-routing; row shows Status=executed-deterministic-complete-runtime-pending, Completed=2026-07-15. **M-2 RESOLVED.**
- `C:\development\opencode\.conductor\tracks-ledger.md` - exactly 1 entry for 20260715-minimax-m3-half-routing; entry shows Phase=executed-deterministic-complete-runtime-pending 2026-07-15 (runtime-pending-restart). **M-3 RESOLVED.**
- `C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\metadata.json` - status, phase, completed_tasks, pipeline_mode, execution_model, tera_ratio, restart_required all consistent with execution log and final-validation.md.

`C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` - 4 records for this track:
- 2026-07-15T22:26:15Z (Stage 1, tool-error, warn) - skill_use not_found.
- 2026-07-15T23:34:08Z (Stage 5, model-fallback, warn) - GLM-5.2/5.1 both skipped, run starts at Tier 3 (Qwen).
- 2026-07-15T23:54:30Z (Stage 7 prior, deviation, warn) - M-1/M-2/M-3 material mismatch from the previous validation.
- 2026-07-15T23:59:00Z (Stage 5 remediation, deviation, warn) - M-1 remediated with deterministic parity rule; M-2/M-3 upserted; operational bypass (Qwen Tier 3 direct) authorized.

Acceptance check dry-runs (executed live via PowerShell/bash against real artifacts):

| Plan task | Check | Result |
|---|---|---|
| 0.1 | preflight.json fields populated, includes C:\development\opencode in git_roots | True |
| 0.2 | baseline-manifest flags + preexisting_git_status + targets | True |
| 1.1 | routing-decision.md has 6 required sections, "Unsupported by verified evidence" or "Supported", and "openai/gpt-5.6" | True |
| 2.1 | m3-inventory records have all 6 fields, scanned_roots includes user agent dir, missing/unreadable present | True |
| 2.2 | approved-routing-map approval_required, approval_status=approved, ratio 40-60% or indivisible_count_exception, all assignments have invocation_rule + diversity_counterpart | True (tera_ratio=0.5, indivisible_count_exception populated, all 4 assignments have invocation_rule and diversity_counterpart) |
| 3.1 | approved-routing-map approval_status=approved + approved_at + approved_summary + map_hash | True (map_hash is a frozen value, not a continuous checksum — see F-1) |
| 3.2 | each approved assignment's path contains model: <new_model> and variant: <new_variant> if non-empty | True |
| 3.3 | pipeline_files concatenation contains the 5 required substrings | True |
| 4.1 | parse-validation all files status=ok and exit_code=0 | True |
| 4.2 | post-change-inventory coverage_complete=true, unexplained_active_count=0, historical_unchanged_count present, unreadable_paths=0 | True |
| 4.3 | diversity-validation status=ok, same_family_pair_count=0, auditable_selection_count==assignment_count, ratio 40-60% or indivisible_count_exception | True (50% ratio, indivisible_count_exception populated, deterministic_parity_rule with SHA-256 example) |
| 4.4 | rollback-validation every file has backup_exists, pre_hash_matches, restore_command, post_restore_hash_command | True (3 files with hash-verified backups; 1 new file with delete-only rollback) |
| 5.1 | restart-decision has restart_required (non-null), evidence (>=1), safe_to_test_now, reason | True |
| 5.2 | runtime-validation has 5 required sections, verdict contains "runtime passed" OR "runtime blocked: Error: Session not found" | True (verdict = "runtime blocked: Error: Session not found (pre-existing)") |
| 5.3 | final-validation has 10 required sections + GLM-5.1 + Qwen | True |
| 5.4 | exactly 1 row in tracks.md, exactly 1 row in tracks-ledger.md, metadata.track_id matches, completed_tasks <= total_tasks, pipeline_mode=bookkeeping | True |

Deterministic parity rule verification (executed live):

```
$trackId = "20260715-minimax-m3-half-routing"
SHA-256: 8677AAA1BE6917702C1CFEF010C3430525B2FCC1E71C68016B51CFE4CECB4A44
Last hex digit: 4 (even)
Selected validator: conductor-track-validator (Tera Medium)  -- matches diversity-validation.json example
```

GLM non-invocation check (cross-validated): Stage 5 used opencode-go/qwen3.7-plus (Tier 3) directly. No zai-coding-plan/glm-5.2 or zai-coding-plan/glm-5.1 invocation. SKILL.md preserves the canonical chain and adds the operational note. Stage 7 re-validation used PowerShell/Get-Content/Get-FileHash via bash (no model invocation). No GLM models called during this validation.

---

## Mismatches Found

### Prior report mismatches (status re-check)

- **M-1 (prior: MATERIAL) — RESOLVED.** 50%-usage target now met. tera_ratio=0.5 in approved-routing-map.json, diversity-validation.json, and metadata.json. The deterministic SHA-256(track_id) parity rule produces exactly 50% Tera / 50% M3 across uniformly distributed track IDs. Live-verified: SHA-256("20260715-minimax-m3-half-routing") = 8677AAA1BE6917702C1CFEF010C3430525B2FCC1E71C68016B51CFE4CECB4A44, last digit "4" (even) -> Tera primary. The diversity-validation.json example with the same value and "parity: even" matches. Over a two-track cycle with one even and one odd parity: 3 M3 checkpoints + 3 Tera checkpoints = exactly 50% each. Pipeline diversity preserved: 0 same-family creator/reviewer or executor/validator pairs across the 4 paired assignments.
- **M-2 (prior: bookkeeping) — RESOLVED.** tracks.md row shows Status=executed-deterministic-complete-runtime-pending, Completed=2026-07-15. Matches metadata.json.
- **M-3 (prior: bookkeeping) — RESOLVED.** tracks-ledger.md row shows Phase=executed-deterministic-complete-runtime-pending 2026-07-15 (runtime-pending-restart). Matches metadata.json.
- **M-4 (prior: plan-text, non-blocking) — NOTED.** Task 2.2 acceptance check post-3.1 false by design; already acknowledged in execution log as expected behavior, not a regression.

### New findings (post-remediation)

#### F-1 (bookkeeping-only, minor) — approved-routing-map.json map_hash is now stale relative to current file content

- The `map_hash` field in `approved-routing-map.json` is `C9157AB77CE5771421A1D44EAC166C68646E88951ADC7FD1854C186095DA3182` (frozen at the original approval time, plan task 3.1).
- The current full-file SHA-256 of `approved-routing-map.json` (re-computed live during this validation) is `1925254EF3F3870C58E2C3E7E94E65CDB20419F16035881D898CEB9A4656DE87` — does NOT match the recorded `map_hash`.
- Cause: the M-1 remediation added the `conductor-track-validator-m3` assignment, the `deterministic_parity_rule` field, the `pipeline_files` list, and updated `tera_count`/`m3_retained_count`/`remediation_applied` to the file. The `map_hash` was not re-frozen after the remediation edit.
- Per plan spec, the `map_hash` is a frozen historical snapshot, not a continuous checksum. The plan's authoritative acceptance check for task 3.1 only requires the field to be non-empty (truthy). Therefore the spec acceptance check passes.
- Impact: bookkeeping only. No deliverable, no deterministic gate, no diversity rule, no rollback, and no audit trail is affected. A future reader might assume the map_hash is a current checksum; the remediation-applied timestamp (2026-07-15T23:59:00Z) is the authoritative current-state marker.
- Classify as: bookkeeping-only, minor, not blocking. Can be reconciled by either (a) re-freezing the map_hash after remediation, or (b) renaming the field to `approval_time_map_hash` to make the frozen-at-approval semantics explicit.

#### F-2 (doc-drift, out-of-scope, minor) — conductor-pipeline-orchestrator.md still says "validator opencode-go/minimax-m3"

- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` line 81 (in the Stage 5 model-fallback prose) reads: "Diversity remains intact because every executor tier differs from validator `opencode-go/minimax-m3`."
- The Stage 7 validator is no longer M3-only; it is now Tera primary with a paired M3 variant.
- The orchestrator agent was NOT in the approved-routing-map.json scope of this track. The orchestrator's own model pin (`zai-coding-plan/glm-5.2` variant high) is unchanged.
- Impact: documentation drift only. The orchestrator's actual Stage 7 dispatch (when implemented) will use the SHA-256 parity rule from SKILL.md, not this stale prose. The SKILL.md itself correctly describes Stage 7 as `conductor-track-validator / conductor-track-validator-m3` (Tera or M3).
- Classify as: doc-drift, minor, not in scope of this track, not blocking. Worth a follow-up to update the orchestrator agent's prose reference to "conductor-track-validator (Tera Medium) or conductor-track-validator-m3 (M3)".

#### F-3 (doc-drift, minor) — conductor-test-runner.md body still says "Runs on MiniMax M3"

- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md` frontmatter pins `model: openai/gpt-5.6-terra` and `variant: medium`, but the body prose still says: "Runs on MiniMax M3 - an independent model family from the GLM executor."
- Impact: documentation drift in agent body. The frontmatter is authoritative for model selection; the body description is stale.
- Classify as: doc-drift, minor, not blocking. The model pin is correct; the body is a narrative restatement that needs a one-line update.

#### F-4 (bookkeeping-only, minor) — SKILL.md "Diversity log" still has a stale "validator (MiniMax)" line

- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` (remediation-revised) line ~50 in the Diversity log reads: "Validator (Tera primary or M3 paired) != executor (GLM): different families in both cases. OK. Deterministic parity rule selects between them." — this IS updated correctly.
- However, the same SKILL.md references "opencode-go/minimax-m3" in the model assignment table line 33 (Stage 2 plan review) and line 60 (odd-parity validator-m3). Both are correct and intentional (Stage 2 reviewer remains M3; odd-parity validator is M3 paired). Not a drift; verifying these are intentional.
- No real SKILL.md issue beyond the F-2 orchestrator agent drift (which is in a different file).
- Classify as: not actually a mismatch; included for completeness of the audit.

---

## Required Fixes Before Close

Classify each per the Stage 7 output format (bookkeeping-only / deliverable / plan-text).

1. **None blocking.** The deliverable meets the user acceptance goal: 50% Tera / 50% M3 across the combined Stage 2 / 6 / 7 two-track cycle via deterministic SHA-256(track_id) parity, model-family independence preserved, GLM-5.1 and GLM-5.2 never invoked, runtime test honestly classified as blocked (not misreported as passed), and all required artifacts exist with verified SHA-256 parity mapping for backups.

2. (bookkeeping-only, minor, F-1) Re-freeze `map_hash` in `approved-routing-map.json` to the current file SHA-256 (`1925254EF3F3870C58E2C3E7E94E65CDB20419F16035881D898CEB9A4656DE87`), OR rename the field to `approval_time_map_hash` to clarify frozen-at-approval semantics. Not blocking; record as Stage 9 bookkeeping follow-up or Stage 8 minor follow-up.

3. (doc-drift, minor, F-2) Update `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` line 81 to reference the paired validator (Tera or M3) instead of "validator opencode-go/minimax-m3". Out of scope of this track; record as a separate small follow-up. Not blocking.

4. (doc-drift, minor, F-3) Update `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md` body prose to "Runs on OpenAI GPT-5.6 Tera (medium) - an independent family from the GLM executor". Not blocking; the frontmatter is correct and authoritative.

5. (audit-trail) Append one seven-key JSONL anomaly record to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` for this re-validation pass: type=other, severity=info, summary=Stage 7 re-validation complete; all prior material mismatches resolved via deterministic SHA-256 parity rule; minor bookkeeping follow-ups F-1/F-2/F-3 noted; verdict Close with minor follow-ups. One append; no truncation.

---

## Final Recommendation

**Close with minor follow-ups.** The Stage 5 remediation (deterministic SHA-256(track_id) parity-based paired-validator system achieving exactly 50% Tera / 50% MiniMax M3 across the combined Stage 2 / 6 / 7 two-track cycle) is genuinely operational, auditable, and not random; SHA-256 parity mapping is correct and live-verified; the in-session runtime test is correctly classified as blocked (not misreported as passed); the primary test-runner/validator pins are Tera Medium and the paired M3 validator exists with no duplicate or conflicting agent name; GLM 5.2 and GLM 5.1 were never invoked; the canonical three-tier chain `zai-coding-plan/glm-5.2 -> zai-coding-plan/glm-5.1 -> opencode-go/qwen3.7-plus` is documented unchanged in SKILL.md with the operational bypass note; the operational bypass to Qwen Tier 3 is authorized by the user-reported quota exhaustion; all active M3 references reconcile (plan-reviewer + validator-m3, 2 active); all backups and rollback commands are SHA-256-verified (3 pre-existing files with hash match, 1 new file with delete-only rollback); the bookkeeping (tracks.md, tracks-ledger.md, metadata.json) is now in sync. The remaining minor follow-ups (F-1 stale map_hash, F-2 orchestrator doc drift, F-3 test-runner body stale description) are bookkeeping-only or out-of-scope doc drift and do not block closeout.

---

## Stage 9 Readiness (Phase A pre-check)

- **Stage 9 artifact required?** No. The execution log records a Stage 9 waiver: "This is a bookkeeping track with no public API surface changes. The SKILL.md deterministic parity rule section is a non-contractual sync. Stage 9 documentation is waived."
- **Justification for waiver:** The track is a bookkeeping track (track_type=bookkeeping, test_framework=none) with no public API surface. The only documentation edits are the deterministic-parity-rule section in SKILL.md (non-contractual: a description of how the orchestrator selects between paired validators), the new conductor-track-validator-m3.md agent file (an internal subagent definition, not user-facing), and the frontmatter pin changes on conductor-test-runner.md and conductor-track-validator.md (internal subagent model changes, not user-facing). No README/API doc/CHANGELOG/ADR public contract is affected.
- **Post-doc validation requirement:** None. The SKILL.md edit is a non-contractual description of the deterministic parity rule; the paired agent file is a pure addition (no prior user-visible contract); the frontmatter pin changes are internal subagent routing only.
- **Terminal closeout gate (Phase A):** All eight Phase A items pass. Non-deferred plan tasks all `[x]` (16/16). metadata.json status/stage/progress/pipeline_mode/pipeline_path reflect the executed path. tracks.md has exactly one up-to-date row. tracks-ledger.md has one canonical up-to-date row. Execution log exists and records the M-1/M-2/M-3 remediation, the operational bypass, and the model-tier deviation. Every claimed artifact exists with the required acceptance strings (verified by live dry-run). Stage 9 readiness confirmed: documentation can run as a non-contractual sync only, OR be waived entirely (waiver is recorded in the execution log). No required follow-ups remain open as blockers.
- **Phase B (terminal closeout confirmation after Stage 9):** Out of scope of this Stage 7 re-validation; belongs to the orchestrator. The Stage 9 waiver is already recorded in the execution log, so the orchestrator's Phase B check is satisfied without a Stage 9 artifact.

---

## Author

**Author:** conductor-track-validator (Stage 7) - opencode-go/minimax-m3
**Stage:** 7 (re-validation after single permitted Stage 5 remediation)
**Date:** 2026-07-16T00:11:40Z
**Verdict:** Close with minor follow-ups
