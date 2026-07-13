# Plan: Conductor Pipeline Closeout Hardening

**Track ID**: `20260706-conductor-pipeline-closeout-hardening`  
**Created**: 2026-07-06  
**Status**: plan-ready-for-review  
**Track type**: bookkeeping  

> Read first: `C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\spec.md`. This plan implements the still-valid recommendations from `C:\development\opencode\.conductor\reviews\20260706-email-triage-pipeline-peer-review-checklist.md`. Do not execute production-code changes from this track.

---

## Phase 0 - Setup & Preconditions

**Objective:** confirm scope, preserve pre-edit state, and gather the few remaining facts needed before any global agent/skill files are edited.

- [ ] 0.1 **Confirm Conductor plan prompt source and capture it in the execution log.** Record that the full Stage 1 plan-creation prompt is in `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` under `## Stage 1 - Plan Creation (conductor-plan-creator)`, while the `conductor` skill provides the templates and completion hygiene.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch '## Stage 1 - Plan Creation (conductor-plan-creator)' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'` returns at least one match and `execution-log-2026-07-06.md` contains the literal string `Stage 1 plan-creation prompt source confirmed`.
  - Diagnostic checks: `Select-String -SimpleMatch 'Required plan structure: Phase 0 Setup & Preconditions' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'`.
  - Error recovery: If the Stage 1 heading is missing, stop and inspect `SKILL.md` for the new prompt location before editing any pipeline file.

- [ ] 0.2 **Back up all global files this plan may edit.** Create `C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\backups\2026-07-06-pre-edit\` and copy every existing target file into mirrored subfolders before edits.
  - Required backup targets: `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md`, `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`, and any Bun troubleshooting doc edited in Phase 4.
  - **Authoritative acceptance check:** `(Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\backups\2026-07-06-pre-edit\agent\conductor-track-executor-glm51.md.pre-edit.bak') -and (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\backups\2026-07-06-pre-edit\agent\conductor-track-executor-qwen.md.pre-edit.bak') -and (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\backups\2026-07-06-pre-edit\skill\conductor-pipeline\SKILL.md.pre-edit.bak') -and (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\backups\2026-07-06-pre-edit\skill\conductor-pipeline\references\stage-prompts.md.pre-edit.bak') -and (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\backups\2026-07-06-pre-edit\skill\conductor-pipeline\references\threshold-policy.md.pre-edit.bak')` returns `True`.
  - Diagnostic checks: `Get-ChildItem -Recurse -File 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\backups\2026-07-06-pre-edit'`.
  - Error recovery: If a target does not exist, create a `__FILE_DID_NOT_EXIST__.<name>.bak` marker and record it in the execution log; do not silently skip it.

- [ ] 0.3 **Inventory current stale stage-label occurrences.** Search only global Conductor pipeline/agent files for stale Stage 4 execution wording and write the raw result summary to `stage-label-inventory-2026-07-06.md` in this track.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'conductor-track-executor-glm51.md' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\stage-label-inventory-2026-07-06.md'` and `Select-String -SimpleMatch 'conductor-track-executor-qwen.md' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\stage-label-inventory-2026-07-06.md'` both return at least one match.
  - Diagnostic checks: `rg -n "Stage 4|Stage 5" "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md" "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md"`.
  - Error recovery: If `rg` is unavailable, use PowerShell `Select-String -SimpleMatch` against the two exact files.

- [ ] 0.4 **Confirm the Bun issue evidence and local recommendation.** Use GitHub CLI to record upstream issue status for `https://github.com/anomalyco/opencode/issues/25880` and capture the current local fallback protocol from `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'https://github.com/anomalyco/opencode/issues/25880' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\bun-issue-research-2026-07-06.md'` and `Select-String -SimpleMatch 'PowerShell-first' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\bun-issue-research-2026-07-06.md'` both return at least one match.
  - Diagnostic checks: `gh issue view 25880 --repo anomalyco/opencode --json number,title,state,url,updatedAt`.
  - Error recovery: If `gh` is unauthenticated or unavailable, use `webfetch`/browser fetch of the issue URL and record the fallback source.

- [ ] 0.5 **Classify the email-triage PSParser/mojibake cleanup scope.** Inspect only the existing validation report and parser-error evidence from `C:\development\email-triage\.conductor\tracks\20260706-email-triage-move-failure-observability\validation-report-2026-07-06-120000.md`; decide whether this track should create a separate email-triage track or explicitly defer it.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'PSParser/mojibake disposition:' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\execution-log-2026-07-06.md'` returns at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'PSParser' 'C:\development\email-triage\.conductor\tracks\20260706-email-triage-move-failure-observability\validation-report-2026-07-06-120000.md'`.
  - Error recovery: If the email-triage report path is missing, stop and ask whether the repo moved before creating a cross-repo track.

## Phase 1 - Terminal Closeout Gate

**Objective:** make final pipeline success contingent on synchronized Stage 9 documentation and Conductor bookkeeping.

- [ ] 1.1 **Add terminal closeout gate policy to `SKILL.md`.** Update `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` with a `Terminal closeout gate` section stating that final success is blocked unless Stage 9 has emitted `doc-update-log-<timestamp>.md` or a documented skip/waiver, `metadata.json` status/stage/progress matches the executed path, `.conductor\tracks.md` has one up-to-date row, `tracks-ledger.md` is updated when the repo uses one, and required follow-ups are either created or explicitly deferred.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'Terminal closeout gate' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md'` and `Select-String -SimpleMatch 'doc-update-log-<timestamp>.md' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md'` both return at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'tracks-ledger.md' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md'`.
  - Error recovery: If an equivalent section already exists, update it in place rather than creating a duplicate heading.

- [ ] 1.2 **Add closeout gate steps to `stage-prompts.md`.** Update the Stage 7/8 validation prompt in `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` so validators explicitly machine-check Stage 9 artifact/skip, metadata, track index, ledger behavior, and follow-up disposition before accepting closeout.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'machine-check Stage 9 artifact' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'` and `Select-String -SimpleMatch 'required follow-ups are created or explicitly deferred' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'` both return at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch '## Stage 7 / 8 - Validation' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'`.
  - Error recovery: If the Stage 7/8 heading changed, locate the validator section by `conductor-track-validator` and edit that section only.

- [ ] 1.3 **Add terminal gate stop/route behavior to `threshold-policy.md`.** Update `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md` so missing terminal closeout evidence is a closeout blocker, not a successful run with notes.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'terminal closeout blocker' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md'` returns at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'Stage 9' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md'`.
  - Error recovery: If threshold policy already contains closeout-blocker text, merge the missing checks into that section rather than duplicating it.

## Phase 2 - Stage Label Corrections

**Objective:** remove stale Stage 4 execution wording from fallback executor agents.

- [ ] 2.1 **Correct `conductor-track-executor-glm51.md` stage wording.** Edit `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md` so its description/body refers to fallback execution as Stage 5, and any instruction to load the execution prompt points to Stage 5 rather than Stage 4.
  - **Authoritative acceptance check:** `(Select-String -SimpleMatch 'Stage 5' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md').Count -ge 1 -and -not (Select-String -SimpleMatch 'Stage 4 execution' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md' -Quiet)` returns `True`.
  - Diagnostic checks: `Select-String -Pattern 'Stage [45]' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md'`.
  - Error recovery: If the phrase is not exact, inspect all Stage 4/5 lines and preserve model/fallback behavior while changing only numbering/labels.

- [ ] 2.2 **Correct `conductor-track-executor-qwen.md` stage wording.** Edit `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md` so its description/body refers to fallback execution as Stage 5, and any instruction to load the execution prompt points to Stage 5 rather than Stage 4.
  - **Authoritative acceptance check:** `(Select-String -SimpleMatch 'Stage 5' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md').Count -ge 1 -and -not (Select-String -SimpleMatch 'Stage 4 execution' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md' -Quiet)` returns `True`.
  - Diagnostic checks: `Select-String -Pattern 'Stage [45]' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md'`.
  - Error recovery: If the phrase is not exact, inspect all Stage 4/5 lines and preserve model/fallback behavior while changing only numbering/labels.

- [ ] 2.3 **Verify no stale fallback Stage 4 execution labels remain.** Re-run the inventory from Phase 0 and write `stage-label-verification-2026-07-06.md`.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'No stale fallback Stage 4 execution labels remain' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\stage-label-verification-2026-07-06.md'` returns at least one match.
  - Diagnostic checks: `rg -n "Stage 4 execution|load Stage 4" "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md" "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md"` should return no matches.
  - Error recovery: If matches remain, decide whether they refer to the test-writer Stage 4; only execution/fallback labels are defects.

## Phase 3 - Audit-Correction Convention

**Objective:** give future validators/executors a standard artifact for correcting audit-trail mismatches discovered after the fact.

- [ ] 3.1 **Document `audit-correction-<timestamp>.md` artifact format.** Add or update the artifact convention in `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\artifact-output-format.md`, which is the preferred Conductor pipeline artifact-format reference. If that file is unexpectedly absent, stop and inspect the sampled skill file list before choosing an alternate location.
  - Required body fields: original artifact path, mismatch summary, evidence source, corrected interpretation, whether deliverable behavior changed, whether follow-up work is required, author/stage/date.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'audit-correction-<timestamp>.md' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\artifact-output-format.md'` and `Select-String -SimpleMatch 'corrected interpretation' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\artifact-output-format.md'` both return at least one match.
  - Diagnostic checks: `Test-Path -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\artifact-output-format.md'`.
  - Error recovery: If the chosen file does not exist, do not create a duplicate reference file without checking existing Conductor pipeline references.

- [ ] 3.2 **Teach validation prompt when to request or write audit corrections.** Update the Stage 7/8 validation prompt so reporting mismatches like “execution log said parse check clean but validation found parser errors” produce an audit-correction artifact or a clearly labeled correction section.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'audit-correction-<timestamp>.md' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'` and `Select-String -SimpleMatch 'reporting mismatch' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'` both return at least one match.
  - Diagnostic checks: none.
  - Error recovery: If Stage 7 validators remain read-only, phrase this as “emit/request” according to the agent’s actual permissions and documented artifact-writing scope.

- [ ] 3.3 **Tie audit corrections to anomaly logging.** Update anomaly/threshold documentation so audit corrections are referenced from `pipeline-anomalies.jsonl` when a mismatch is significant enough to log.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'audit-correction' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md'` returns at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'pipeline-anomalies.jsonl' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md'`.
  - Error recovery: If anomaly logging lives in a separate `anomaly-logging.md`, update that file instead and add a cross-reference from `threshold-policy.md`.

## Phase 4 - Stage 9 Post-Doc Validation and Bun Fallback

**Objective:** prevent docs from drifting after Stage 9 and clarify what is actually actionable for `Bun is not defined`.

- [ ] 4.1 **Add post-doc validation/waiver rule to Stage 9 prompt.** Update the Stage 9 documentation prompt so when docs describe runtime/semantic behavior, the doc writer must either rerun the relevant validation/test command and emit `post-doc-validation-<timestamp>.md`, or write a waiver explaining why no post-doc validation was needed.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'post-doc-validation-<timestamp>.md' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'` and `Select-String -SimpleMatch 'waiver' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'` both return at least one match within or near the Stage 9 section.
  - Diagnostic checks: `Select-String -SimpleMatch '## Stage 9 - Documentation' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'`.
  - Error recovery: If Stage 9 is not allowed to run tests, require it to request the test-runner/validator post-doc check rather than running tests itself.

- [ ] 4.2 **Add post-doc validation policy to `SKILL.md` or `threshold-policy.md`.** Ensure the high-level pipeline docs say Stage 9 semantic/runtime documentation requires post-doc validation or waiver.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'post-doc validation' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md'` or `Select-String -SimpleMatch 'post-doc validation' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md'` returns at least one match; record the actual file in the execution log.
  - Diagnostic checks: none.
  - Error recovery: Avoid duplicating policy in both files unless one is a short cross-reference.

- [ ] 4.3 **Document actionable `Bun is not defined` recommendation.** Update the canonical troubleshooting doc at `C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md` to state: exact symptom, likely Desktop/sidecar Bun-vs-Node class of issue where applicable, upstream issue links (reference #35573 as the primary match for the native-tools symptom and #25880 as the related broader plugin-sidecar issue), local CLI/session fallback, when not to retry native tools, and what evidence to collect before filing/commenting upstream.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'Bun is not defined' 'C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md'` and `Select-String -SimpleMatch 'https://github.com/anomalyco/opencode/issues/35573' 'C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md'` and `Select-String -SimpleMatch 'https://github.com/anomalyco/opencode/issues/25880' 'C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md'` and `Select-String -SimpleMatch 'PowerShell-first' 'C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md'` all return at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'Tool-Layer Failure Protocol' 'C:\Users\DaveWitkin\.config\opencode\AGENTS.md'`.
  - Error recovery: If the docs directory does not exist, create the minimum missing documentation directories only after verifying `C:\Users\DaveWitkin\.config\opencode` is the intended parent.

- [ ] 4.4 **Add a short cross-reference from AGENTS.md only if needed.** If `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` does not already reference the canonical troubleshooting doc, add a single-line pointer to the existing Tool-Layer Failure Protocol without changing the protocol semantics.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'docs/troubleshooting/tool-failure-bun-undefined.md' 'C:\Users\DaveWitkin\.config\opencode\AGENTS.md'` returns at least one match, or `Select-String -SimpleMatch 'AGENTS.md Bun cross-reference not needed' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\execution-log-2026-07-06.md'` returns at least one match.
  - Diagnostic checks: none.
  - Error recovery: Do not rewrite AGENTS.md wholesale; use a literal content-anchored insertion under the existing Tool-Layer Failure Protocol.

## Phase 5 - PSParser / Mojibake Follow-Up Disposition

**Objective:** either create a separate email-triage planning track for parser/mojibake cleanup or document why it is deferred.

- [ ] 5.1 **Create separate email-triage Conductor track if parser cleanliness matters.** If Phase 0.5 disposition is “create track,” create `C:\development\email-triage\.conductor\tracks\20260706-psparser-mojibake-cleanup\spec.md`, `plan.md`, and `metadata.json` describing investigation/remediation of pre-existing PSParser/mojibake issues without conflating it with move-failure observability. Do not edit email-triage production scripts in this track.
  - **Authoritative acceptance check:** Either `Test-Path -LiteralPath 'C:\development\email-triage\.conductor\tracks\20260706-psparser-mojibake-cleanup\plan.md'` returns `True`, or `Select-String -SimpleMatch 'PSParser/mojibake cleanup deferred' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\execution-log-2026-07-06.md'` returns at least one match.
  - Diagnostic checks: `Test-Path -LiteralPath 'C:\development\email-triage\.conductor\tracks'`.
  - Error recovery: If email-triage has no Conductor ledger/index, create only the track folder artifacts and record the ledger deviation.

- [ ] 5.2 **If the email-triage track is created, update its local Conductor index/ledger if present.** Upsert, do not duplicate, any `C:\development\email-triage\.conductor\tracks.md` and `tracks-ledger.md` entries if those files exist.
  - **Authoritative acceptance check:** If `C:\development\email-triage\.conductor\tracks.md` exists, `Select-String -SimpleMatch '20260706-psparser-mojibake-cleanup' 'C:\development\email-triage\.conductor\tracks.md'` returns at least one match; if it does not exist, `execution-log-2026-07-06.md` contains `email-triage tracks.md absent for PSParser follow-up`.
  - Diagnostic checks: `Test-Path -LiteralPath 'C:\development\email-triage\.conductor\tracks.md'`; `Test-Path -LiteralPath 'C:\development\email-triage\.conductor\tracks-ledger.md'`.
  - Error recovery: Do not create duplicate index rows if a row already exists.

## Final Phase - Validation & Handover

**Objective:** validate edits, synchronize Conductor bookkeeping, and prepare the user for restart/review.

- [ ] F.1 **Write execution log for this track.** Create/update `C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\execution-log-2026-07-06.md` with changed files, backups, deviations, Bun issue findings, PSParser disposition, and validation commands run.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'Changed files:' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\execution-log-2026-07-06.md'` and `Select-String -SimpleMatch 'Validation commands:' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\execution-log-2026-07-06.md'` both return at least one match.
  - Diagnostic checks: none.
  - Error recovery: If a command could not run because a tool failed, record the exact failure and fallback used.

- [ ] F.2 **Verify all target acceptance strings.** Run the authoritative checks from Phases 1-5 and summarize pass/fail in `validation-summary-2026-07-06.md`.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'Overall verdict: PASS' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\validation-summary-2026-07-06.md'` returns at least one match.
  - Diagnostic checks: include `git diff --stat` in the validation summary but do not use it as sole proof.
  - Error recovery: If any acceptance check fails, leave the relevant plan task unchecked and record blocker details.

- [ ] F.3 **Synchronize `metadata.json`.** Update `C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\metadata.json` so status/progress reflect actual task completion and include `track_type: bookkeeping`, `test_framework: none`, `test_command: n/a`.
  - **Authoritative acceptance check:** `(Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\metadata.json' | ConvertFrom-Json).track_type -eq 'bookkeeping'` returns `True` and `.status` matches the plan’s final state.
  - Diagnostic checks: `Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\metadata.json' | ConvertFrom-Json | ConvertTo-Json -Depth 8`.
  - Error recovery: If JSON parsing fails, restore from the pre-edit metadata backup or recreate from this plan.

- [ ] F.4 **Upsert OpenCode Conductor index and ledger rows.** Update exactly one row each in `C:\development\opencode\.conductor\tracks.md` and `C:\development\opencode\.conductor\tracks-ledger.md` for this track.
  - **Authoritative acceptance check:** `(Select-String -SimpleMatch '20260706-conductor-pipeline-closeout-hardening' 'C:\development\opencode\.conductor\tracks.md').Count -eq 1 -and (Select-String -SimpleMatch '20260706-conductor-pipeline-closeout-hardening' 'C:\development\opencode\.conductor\tracks-ledger.md').Count -eq 1` returns `True`.
  - Diagnostic checks: none.
  - Error recovery: If duplicates exist, rewrite the affected small row region or full file section to one canonical row.

- [ ] F.5 **Handover and restart notice.** Tell the user which files changed and that global agent/skill changes require quitting and restarting OpenCode before new instructions are fully loaded by future sessions/subagents.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'Restart OpenCode before relying on updated global agents/skills' 'C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\execution-log-2026-07-06.md'` returns at least one match.
  - Diagnostic checks: none.
  - Error recovery: If no global agent/skill file changed, record that restart is not required.

---

## Execution-Readiness Checklist

- [ ] The user agrees this remains a bookkeeping/config/documentation track.
- [ ] Backups are created before global file edits.
- [ ] Bun recommendation is documentation/fallback-first, not an assumed runtime code fix.
- [ ] Email-triage PSParser/mojibake is handled as a separate track or explicitly deferred.
- [ ] All global OpenCode config/skill changes are followed by a restart notice.

## Top 3 Risks + Mitigations

1. **Breaking global Conductor agent prompts with broad edits.** Mitigation: back up first; use content-anchored literal edits; verify exact acceptance strings.
2. **Over-promising a local Bun fix.** Mitigation: document upstream issue #25880 and current fallback; do not patch runtime internals in this track.
3. **Cross-repo confusion with email-triage parser cleanup.** Mitigation: create a separate email-triage track for planning-only cleanup if needed; do not edit email-triage production scripts here.

## First Task to Execute

Task 0.1 — confirm and log that the full Conductor plan-creation prompt is available in `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` under Stage 1, while the `conductor` skill provides templates/completion hygiene.
