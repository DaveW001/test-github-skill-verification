# Plan: AGENTS.md Optimization and Review

`plan.md` is the authoritative source of truth for execution progress.

## Outcome, Constraints, and Definition of Done

### Goal / outcome

Deliver an evidence-backed review and safe optimization of 43 active
`AGENTS.md` files: two global client files first, followed by 41 files in nine
qualifying local roots, with verified backups, client-aware loading checks, a
complete rubric matrix, and independently validated Conductor closeout.

### Constraints / non-goals

- Capture the run date and 120-day cutoff once: `2026-07-26` and
  `2026-03-28T00:00:00-04:00`.
- The target set and exclusions in `spec.md` are frozen unless new evidence
  proves an inventory error; scope expansion requires a documented plan
  correction before edits.
- Global review, fixes, and validation must finish before local-file review.
- Preserve dirty worktrees and all unrelated user changes. Never restore,
  reset, delete, rename, merge, commit, push, publish, restart, or make an
  external mutation.
- Use `apply_patch` or a schema-aware deterministic editor for file changes.
  Never perform regex bulk rewrites across instruction files.
- Execute every listed command and acceptance check in a bounded,
  non-interactive host tool call capped at 600 seconds. A command that owns a
  child client process must also enforce its narrower `--timeout-seconds`
  value, terminate only that owned process on timeout, and stop rather than
  retrying a silent hang.
- Treat Codex and OpenCode discovery/reference semantics separately.
- Review duplicate OpenCode clone content once where byte-identical, but
  validate and edit each live target independently.

### Definition of done

All 17 executable tasks are complete; every scoped file has a complete rubric
packet; all changes have verified recovery copies and narrow diffs; deterministic
checks pass or limitations are explicitly Unverified; an independent validator
returns ready-to-close; Stage 9 and terminal Conductor checks pass; no
out-of-scope mutation occurred.

## Pipeline Determination

- Track type: `bookkeeping`
- Classification: `certain`
- Production code changes: no
- Test framework: none
- Risk: medium because two global files affect all future sessions and nested
  precedence spans multiple repositories.
- Selected mode: `bookkeeping` with explicit review
- Selected path: `1 -> 2 -> 3 -> 5 -> 7 -> 8? -> 9`
- Stage 2 was required by the user. Stage 3 ran once because the Stage 2
  readiness score was 45/100, below the B+C threshold.
  Stages 4/4b/6 are skipped because no production behavior or test framework is
  in scope. Stage 8 runs only if Stage 7 triggers A+C.

## Phase 0: Setup and Preconditions

Objective: freeze scope, rubric, evidence schemas, and recoverable baselines
before any AGENTS.md edit.

- [x] **0.1 Create and self-test the deterministic review toolchain, frozen rubric, and packet schema.**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/rubric.json`, `.conductor/tracks/20260726-agents-md-optimization-review/schemas/review-packet.schema.json`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/bootstrap_review_toolchain.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/inventory_agents.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/verify_agents_review.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/backup_agents.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/audit_agents.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/audit_batch.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/consolidate_review.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/apply_agent_fixes.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/validate_instruction_loading.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/generate_report.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/sync_execution.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/sync_ledgers.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/dispatch_stage7.py`, `.conductor/tracks/20260726-agents-md-optimization-review/scripts/complete_closeout.py`, `.conductor/tracks/20260726-agents-md-optimization-review/tests/test_review_toolchain.py`
  - Prerequisites: none.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\bootstrap_review_toolchain.py" --self-test --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`
  - Body requirements: first author `bootstrap_review_toolchain.py` with `apply_patch`; when invoked, that bootstrap may create only the remaining declared track-local helper/schema/test files, then must run the complete disposable-fixture self-test before returning PASS. Encode exact equality with the 24 rubric IDs in `spec.md`; require result, applicability, severity, confidence, evidence, finding ID, and disposition; implement checks named `scope`, `rubric`, `backups`, `global-review`, `global-changes`, `local-review`, `local-changes`, `portfolio`, `execution-sync`, `ledgers`, `stage7`, and `terminal-closeout`; implement every later CLI exactly as invoked by this plan. The self-test must use disposable fixtures and prove: exact rubric/schema PASS and unknown/duplicate-ID FAIL; inventory include/exclude/cutoff/non-Git-root/mirror behavior; backup path-escape/junction/hash/duplicate-map rejection plus disposable restore; packet completeness/client semantics/mirror identity preservation; consolidation mismatch failure; apply dry-run, exact-hash/dirty/backup/unique-anchor/output-root guards, failed-guard no-write, disposable apply/restore, and zero live-target touches; timeout cleanup and Pass/Fail/Unverified loading transcripts; report reconciliation mismatch failure; duplicate-safe ledger upsert; strict validator alternation with `last_used` as the sole selector and no state flip on failed/timeout/empty dispatch; and refusal to mark terminal complete before a valid Stage 9 artifact or waiver and orchestrator Phase B. Only `apply_agent_fixes.py` may edit an AGENTS.md, and only after all guards pass.
  - Authoritative acceptance check: the command above returns JSON containing `"check": "toolchain-self-test", "status": "PASS", "helpers": 14, "negative_cases_passed": true, "live_targets_touched": 0`, plus an integer `negative_case_count` of at least 15.
  - Diagnostic checks: parse schemas, run every helper's `--help`, compile every helper, and run `python -m unittest discover -s "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\tests" -p "test_review_toolchain.py"`.
  - Error recovery: any false-pass, path escape, live-target touch, or terminal false-green is Blocking; repair tooling/fixtures only and rerun the whole self-test.

- [x] **0.2 Generate and verify the frozen scope inventory.**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/scope-inventory.json`
  - Prerequisites: `0.1`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\inventory_agents.py" --development-root "C:\development" --cutoff "2026-03-28T00:00:00-04:00" --output "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scope-inventory.json"`
  - Body requirements: record the two global files; 41 active local files; eight qualifying Git repositories plus `chief-of-staff`; Git commit/dirty evidence; nested scope; file bytes/hash; tracked state; mirror groups; and explicit exclusions for archive, backup, vendor, `.git`, and `node_modules`.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check scope --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "global": 2, "local": 41, "roots": 9`.
  - Diagnostic checks: compare `rg --files -g 'AGENTS.md'` output and `git log --since` evidence.
  - Error recovery: if counts differ, stop before backup/edit, document the exact added/missing path, and correct spec/plan/metadata through peer review.

- [x] **0.3 Back up and hash every potential edit target.**
  - Files: all 43 paths in `scope-inventory.json`, `.git/codex-track-backups/20260726-agents-md-optimization-review/2026-07-26-pre-edit/`, `.conductor/tracks/20260726-agents-md-optimization-review/backup-manifest.json`
  - Prerequisites: `0.2`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\backup_agents.py" --inventory "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scope-inventory.json" --backup-root "C:\development\opencode\.git\codex-track-backups\20260726-agents-md-optimization-review\2026-07-26-pre-edit" --manifest "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\backup-manifest.json"`
  - Body requirements: copy all 43 files without following junctions; preserve a canonical source-to-backup mapping; verify byte length and SHA-256 equality; record tracked/dirty state; refuse any backup path outside the named backup root; restore every backup into a disposable temp tree and prove its hash matches without touching a live target.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check backups --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "targets": 43, "verified": 43, "restore_simulation": "PASS"`.
  - Diagnostic checks: sample `git diff --no-index` for global, tracked, and non-Git targets.
  - Error recovery: do not edit any target unless its own verified backup exists; a failed target remains review-only and is recorded as blocked.

Phase exit criteria: exact 43-file scope, frozen rubric/verifier, and 43 verified
recovery copies exist before any target edit.

## Phase 1: Global Files First

Objective: review, optimize, and validate both global instruction files before
any local repository packet begins.

- [x] **1.1 Review the global Codex AGENTS.md against current official behavior.**
  - Files: `C:\Users\DaveWitkin\.codex\AGENTS.md`, `.conductor/tracks/20260726-agents-md-optimization-review/review-packets/global/codex.json`
  - Prerequisites: `0.3`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\audit_agents.py" --client codex --target "C:\Users\DaveWitkin\.codex\AGENTS.md" --manual "C:\Users\DAVEWI~1\AppData\Local\Temp\openai-docs-cache\codex-manual.md" --output "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\review-packets\global\codex.json"`
  - Body requirements: complete all applicable rubric items; verify global discovery/override rules, 32-KiB combined guidance risk, personal-versus-repo scope, safety gates, duplication, command/tool validity, and current durable preferences without weakening the mandatory title gate.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check global-review --target codex --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "target": "codex", "rubric_complete": true`.
  - Diagnostic checks: run bounded instruction-source discovery and inspect for `AGENTS.override.md`.
  - Error recovery: label runtime discovery Unverified if the bounded probe is unavailable; static review must still complete.

- [x] **1.2 Review the global OpenCode AGENTS.md against current rules and live paths.**
  - Files: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`, `C:\development\opencode-upstream\packages\web\src\content\docs\rules.mdx`, `.conductor/tracks/20260726-agents-md-optimization-review/review-packets/global/opencode.json`
  - Prerequisites: `1.1`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\audit_agents.py" --client opencode --target "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" --reference "C:\development\opencode-upstream\packages\web\src\content\docs\rules.mdx" --output "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\review-packets\global\opencode.json"`
  - Body requirements: complete all applicable rubric items; verify first-match precedence, non-automatic reference parsing, custom-instructions interaction, live tool/skill names, all referenced paths, ghost labels, global-versus-project scope, and token-heavy reference-index value.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check global-review --target opencode --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "target": "opencode", "rubric_complete": true`.
  - Diagnostic checks: inspect `opencode.jsonc` instruction settings and run path/reference probes.
  - Error recovery: retain client-specific rules when equivalence is uncertain; record the item Unverified instead of generalizing from Codex.

- [x] **1.3 Apply only approved high-confidence global optimizations and generate diffs.**
  - Files: the two global AGENTS.md files, `.conductor/tracks/20260726-agents-md-optimization-review/global-fix-queue.json`, `.conductor/tracks/20260726-agents-md-optimization-review/change-manifest-global.json`, `.conductor/tracks/20260726-agents-md-optimization-review/evidence/diffs/global/`
  - Prerequisites: `1.1`, `1.2`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\apply_agent_fixes.py" --scope global --packets-root "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\review-packets\global" --queue "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\global-fix-queue.json" --manifest "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\change-manifest-global.json" --diff-root "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\evidence\diffs\global"`
  - Body requirements: deterministically consolidate both packets into the queue, then fix only confirmed stale/duplicate/mis-scoped/invalid guidance; preserve active preferences and safety gates; record before/after bytes, changed sections, authority delta, rationale, backup, and exact diff; do not restart either client.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check global-changes --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"` returns JSON containing `"check": "global-changes", "status": "PASS", "authority_expansion": false`.
  - Diagnostic checks: `git diff --no-index` each backup/live pair and compare heading/bullet counts.
  - Error recovery: restore only the failed target from its verified backup after confirming the exact path; never roll back the other global file.

- [x] **1.4 Validate global loading, precedence, and instruction behavior.**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/evidence/global-validation.json`
  - Prerequisites: `1.3`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\validate_instruction_loading.py" --scope global --timeout-seconds 120 --output "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\evidence\global-validation.json"`
  - Body requirements: run bounded fresh-process probes for Codex and OpenCode when available; verify reported instruction sources and critical-rule retention; never grant auto-approval, mutate a repo, or restart an app; record timed-out/unavailable probes as Unverified.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check global-changes --require-loading-evidence --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS"` and per-client `Pass` or justified `Unverified`.
  - Diagnostic checks: compare probe output with documented precedence and static marker checks.
  - Error recovery: terminate only owned bounded probe processes; keep global changes only when static/diff checks pass and runtime limitation is explicitly Unverified.

Phase exit criteria: both globals are fully reviewed, any safe changes are
validated, and no local review task has started early.

## Phase 2: Qualifying Local Files

Objective: complete evidence packets in disjoint batches, then consolidate
scope and precedence before editing any local file.

- [x] **2.1 Review knowledge, command-center, and chief-of-staff files.**
  - Files: `C:\development\02-Kx-to-process\AGENTS.md`, `C:\development\command-center\AGENTS.md`, `C:\development\chief-of-staff\AGENTS.md`, `.conductor/tracks/20260726-agents-md-optimization-review/review-packets/local/operations/`
  - Prerequisites: `1.4`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\audit_batch.py" --batch operations --inventory "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scope-inventory.json"`
  - Body requirements: complete three packets; verify current repo/folder layout, commands, evidence boundaries, human-authority rules, source-control applicability, and current KG/operations guidance.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check local-review --batch operations --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "files": 3`.
  - Diagnostic checks: compare manifests, recent commits/files, and referenced paths.
  - Error recovery: isolate a failing packet; do not block read-only completion of the other two.

- [x] **2.2 Review the marketing repository family without conflating scopes.**
  - Files: the six active files under `C:\development\marketing`, `C:\development\marketing\marketingskills`, and `C:\development\INACTIVE-content-marketing` listed by `scope-inventory.json`; `.conductor/tracks/20260726-agents-md-optimization-review/review-packets/local/marketing/`
  - Prerequisites: `1.4`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\audit_batch.py" --batch marketing --inventory "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scope-inventory.json"`
  - Body requirements: complete six packets; treat `marketingskills` as an independent nested Git repository; distinguish active and INACTIVE roots; inspect the `CLAUDE.md` fallback interaction without editing it.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check local-review --batch marketing --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "files": 6`.
  - Diagnostic checks: compare nested instruction chains and current build/content workflows.
  - Error recovery: do not copy rules between active/INACTIVE roots without path-specific evidence.

- [x] **2.3 Review both OpenCode clone trees with hash-deduplicated analysis.**
  - Files: 15 active files in `C:\development\opencode-core-dcp-fix`, 15 active files in `C:\development\opencode-upstream`, `.conductor/tracks/20260726-agents-md-optimization-review/review-packets/local/opencode-clones/`
  - Prerequisites: `1.4`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\audit_batch.py" --batch opencode-clones --inventory "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scope-inventory.json" --dedupe-identical`
  - Body requirements: produce 30 file identities and 30 applicability records while permitting one content analysis for byte-identical pairs; validate each clone's branch/remote/path independently; exclude vendored `node_modules`; never blindly port a change into the detached upstream clone.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check local-review --batch opencode-clones --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "files": 30, "mirror_pairs": 15`.
  - Diagnostic checks: compare SHA-256 pairs, remotes, HEADs, and nested chains.
  - Error recovery: split any divergent pair into independent packets; never overwrite one clone from the other.

- [x] **2.4 Review root and GUI instructions in OpenCodex.**
  - Files: `C:\development\opencodex\AGENTS.md`, `C:\development\opencodex\gui\AGENTS.md`, `.conductor/tracks/20260726-agents-md-optimization-review/review-packets/local/opencodex/`
  - Prerequisites: `1.4`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\audit_batch.py" --batch opencodex --inventory "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scope-inventory.json"`
  - Body requirements: complete two packets; reconcile root versus GUI scope; verify current Windows build/run/test commands and recent local modifications without touching unrelated dirty files.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check local-review --batch opencodex --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "files": 2`.
  - Diagnostic checks: inspect manifests, GUI docs, status, and recent commits.
  - Error recovery: if either AGENTS.md is already dirty relative to baseline, stop edits for that file and record an overlap decision.

- [x] **2.5 Consolidate all local findings, chains, duplicates, and dispositions.**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/local-fix-queue.json`, `.conductor/tracks/20260726-agents-md-optimization-review/precedence-map.json`, `.conductor/tracks/20260726-agents-md-optimization-review/agents-review-matrix.md`
  - Prerequisites: `2.1`, `2.2`, `2.3`, `2.4`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\consolidate_review.py" --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`
  - Body requirements: reconcile exactly 41 local packets and 984 rubric item identities before applicability filtering; classify each finding by severity/confidence/disposition; map active parent/nested chains; distinguish duplication from necessary overrides; mark create-missing-file ideas Optional.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check local-review --batch all --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "files": 41, "rubric_identities": 984`.
  - Diagnostic checks: compare packet/name/finding set equality and inspect near-duplicate clusters.
  - Error recovery: do not resolve contradictory packets by choosing the favorable result; lower confidence and preserve both evidence paths.

Phase exit criteria: all 41 local files have complete, reconciled review packets
and an edit queue; no local target has yet been modified.

## Phase 3: Safe Local Optimization and Portfolio Validation

Objective: apply only confirmed local improvements serially, validate effective
instructions, and produce the decision-ready report.

- [x] **3.1 Apply queued high-confidence local edits serially with collision guards.**
  - Files: only targets with `disposition: apply` in `local-fix-queue.json`, `.conductor/tracks/20260726-agents-md-optimization-review/change-manifest-local.json`, `.conductor/tracks/20260726-agents-md-optimization-review/evidence/diffs/local/`
  - Prerequisites: `2.5`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\apply_agent_fixes.py" --queue "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\local-fix-queue.json" --manifest "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\change-manifest-local.json" --diff-root "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\evidence\diffs\local"`
  - Body requirements: recheck each target hash/dirty state against baseline immediately before editing; skip overlapping user changes; use content-anchored minimal edits; record authority delta, before/after bytes, diff, backup, and validation; do not mirror edits without independent applicability evidence.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check local-changes --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"` returns JSON containing `"check": "local-changes", "status": "PASS", "authority_expansion": false`.
  - Diagnostic checks: per-target `git diff` or `git diff --no-index` plus reference/command checks.
  - Error recovery: restore only a failed target from its exact backup after path/hash confirmation; leave other completed targets intact.

- [x] **3.2 Validate every changed local file and representative nested instruction chains.**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/evidence/local-validation.json`
  - Prerequisites: `3.1`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\validate_instruction_loading.py" --scope local --inventory "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scope-inventory.json" --timeout-seconds 120 --output "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\evidence\local-validation.json"`
  - Body requirements: rerun structure/reference/command checks for every changed file; probe root and deepest active nested chain per local root with each available client; preserve Pass/Unverified distinctions; confirm excluded archive/vendor files unchanged.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check local-changes --require-loading-evidence --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS"` and zero failed changed targets.
  - Diagnostic checks: inspect client probe transcripts and before/after byte totals.
  - Error recovery: stop on any failed changed target; restore or record a precise blocker without weakening the check.

- [x] **3.3 Generate and verify the decision-ready portfolio report.**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/portfolio-review-report.md`, `.conductor/tracks/20260726-agents-md-optimization-review/change-manifest.json`, `.conductor/tracks/20260726-agents-md-optimization-review/unresolved-decisions.json`
  - Prerequisites: `3.2`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\generate_report.py" --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`
  - Body requirements: include methodology/cutoff, exact scope, before/after byte totals, global findings first, per-root findings, changes, mirror handling, all Critical/Major/Minor findings, Optional gaps, Unverified probes, authority decisions, and recovery paths; reconcile all identities to JSON sources.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check portfolio --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"`; expected JSON includes `"status": "PASS", "global": 2, "local": 41, "total": 43`.
  - Diagnostic checks: cross-check file/finding/change sets against inventory, packets, queues, manifests, and validation evidence.
  - Error recovery: report conflicts and lower confidence; never choose a more favorable count without source reconciliation.

Phase exit criteria: every applied edit passes its checks and the portfolio report
accounts for all 43 scoped files and all unresolved items.

## Final Phase: Validation and Handover

Objective: synchronize evidence, obtain independent closeout readiness, and
complete documentation-only terminal closeout.

Tasks F.1 and F.2 are the final Stage 5 executor tasks. Gates F.3 and F.4 are
orchestrator-owned pipeline stages, not executable-task checkboxes and not part
of task-progress counts; this lets Stage 7 inspect all 17 executor tasks as
complete without validating itself or requiring the later Stage 9 gate to be
pre-completed.

- [x] **F.1 Write the execution log and synchronize plan/metadata counts.**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/execution-log-2026-07-26.md`, `.conductor/tracks/20260726-agents-md-optimization-review/metadata.json`
  - Prerequisites: `3.3`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\sync_execution.py" --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review" --run-date "2026-07-26"`
  - Body requirements: record every task result, model/subagent, commands, edits, backups, deviations, skips, retries, Unverified item, pipeline decision, and absence of external/destructive actions; set progress from the 17 executable tasks, separately recording eight readiness checks and 25 total checkboxes.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check execution-sync --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"` returns JSON containing `"status": "PASS", "tasks": 17, "readiness": 8, "checkboxes": 25`.
  - Diagnostic checks: count executable and readiness checkboxes separately.
  - Error recovery: append an audit correction for historical reporting mismatch; never rewrite evidence to hide a deviation.

- [x] **F.2 Upsert the track row in both Conductor ledgers.**
  - Files: `.conductor/tracks.md`, `.conductor/tracks-ledger.md`
  - Prerequisites: `F.1`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\sync_ledgers.py" --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review" --tracks "C:\development\opencode\.conductor\tracks.md" --ledger "C:\development\opencode\.conductor\tracks-ledger.md"`
  - Body requirements: exactly one row/entry per ledger; status/date/progress match metadata; update in place rather than append a duplicate.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check ledgers --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"` returns JSON containing `"check": "ledgers", "status": "PASS"`.
  - Diagnostic checks: parse and compare track ID, status, date, progress, and uniqueness.
  - Error recovery: update the existing row only; stop on ambiguous duplicate structure.

- **Gate F.3 Obtain independent Stage 7 closeout-readiness validation
  (orchestrator-owned; excluded from executable-task progress).**
  - Files: `.conductor/validator-alternation.json`, `.conductor/logs/pipeline-anomalies.jsonl`, `.conductor/tracks/20260726-agents-md-optimization-review/validation-report-<UTC timestamp>.md`, `.conductor/tracks/20260726-agents-md-optimization-review/anomaly-summary-2026-07-26.md`
  - Prerequisites: `F.2` is checked and the Stage 5 completion sync shows all 17 executable tasks complete in plan, metadata, and both ledgers.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\dispatch_stage7.py" --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review" --alternation "C:\development\opencode\.conductor\validator-alternation.json" --timeout-seconds 480`
  - Body requirements: refuse dispatch unless the 17/17 executor-task completion sync is exact. Under an exclusive state-file lock, use only `last_used`: `luna` selects `conductor-track-validator-m3` (`opencode-go/minimax-m3`), `m3` selects `conductor-track-validator` (`openai/gpt-5.6-luna`, variant `high`), and a missing state file defaults to Luna; reject any other identity. The persisted `next` field is advisory and must be derived from `last_used`, never used as the selector. Enforce the 480-second owned-child timeout; on launch failure, timeout, empty response, unavailable model, or malformed report, terminate only the owned child, append the anomaly/blocker evidence, leave alternation state unchanged, and stop. After a valid returned report, atomically persist the validator just used and derived next identity. Verify scope/rubric/backups/diffs/loading evidence/report/task ordering/metadata/ledgers/logs; require zero unresolved blockers and a structured ready-to-close verdict; append required one-line JSONL anomaly records to `.conductor/logs/pipeline-anomalies.jsonl`; cap correction cycles at five with early anti-runaway stops.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check stage7 --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"` returns JSON containing `"check": "stage7", "status": "PASS", "verdict": "ready_to_close", "alternation": "PASS", "state_flipped_after_success": true`.
  - Diagnostic checks: independently verify every claimed artifact and stable blocker signature.
  - Error recovery: route concrete fixes under A+C; stop on repeated signatures, unavailable evidence, or authority-sensitive work and write `validation-blockers-<timestamp>.md`.

- **Gate F.4 Complete Stage 9 documentation and terminal closeout
  (orchestrator-owned; excluded from executable-task progress).**
  - Files: `.conductor/tracks/20260726-agents-md-optimization-review/doc-update-log-<UTC timestamp>.md`, optional `.conductor/tracks/20260726-agents-md-optimization-review/post-doc-validation-<UTC timestamp>.md`, plan, metadata, both ledgers
  - Prerequisites: Gate `F.3` returned `ready_to_close`.
  - Command: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\complete_closeout.py" --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review" --tracks "C:\development\opencode\.conductor\tracks.md" --ledger "C:\development\opencode\.conductor\tracks-ledger.md" --timeout-seconds 480`
  - Body requirements: first dispatch `conductor-doc-writer` on `opencode-go/deepseek-v4-flash` variant `high` with docs-only permissions and the standard Stage 9 prompt; enforce the 480-second owned-child timeout and leave metadata non-complete on launch failure, timeout, unavailable model, empty response, or malformed Stage 9 evidence. The doc-writer may create documentation and `doc-update-log` evidence but must not modify AGENTS.md, source, tests, configuration, metadata, plan, or ledgers. After a valid Stage 9 artifact or explicit waiver returns, the orchestrator portion performs Phase B: classify every documentation change, require post-doc validation for semantic guidance changes or a reasoned waiver for non-contractual/bookkeeping-only closeout, then synchronize plan/metadata/both ledgers and set metadata complete only after Phase B passes.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\scripts\verify_agents_review.py" --check terminal-closeout --track "C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review"` returns JSON containing `"check": "terminal-closeout", "status": "PASS"`.
  - Diagnostic checks: confirm Stage 9 changed no AGENTS.md, source, tests, config, or external system.
  - Error recovery: route to Stage 9 once for missing evidence, then stop with the exact terminal blocker.

Phase exit criteria: independent validation is ready-to-close; Stage 9 evidence
or waiver exists; terminal verification passes; metadata and both ledgers agree.

## Execution Readiness Checklist

- [x] Exact 43-file scope and exclusions are machine-verifiable.
- [x] Every executable task has exactly one authoritative acceptance check.
- [x] Every command is bounded, non-interactive, and uses exact Windows paths.
- [x] Backups precede edits and dirty-file collision guards are explicit.
- [x] Global completion precedes local review.
- [x] Codex and OpenCode loading/reference semantics remain distinct.
- [x] Parallel subagents write only disjoint review packets; shared files are consolidated serially.
- [x] No publication, commit, push, restart, deletion, or external mutation is authorized.

## Top 3 Implementation Risks and Mitigations

1. **Global guidance regression** — Back up first, preserve safety/title rules,
   use client-specific docs, diff narrowly, and validate through fresh bounded
   discovery probes.
2. **Nested or mirrored scope corruption** — Freeze chains and hashes, exclude
   archives/vendors, review byte-identical pairs once but edit/validate each
   live clone independently.
3. **False confidence from stale commands or unavailable clients** — Verify
   manifests/paths and bounded probes; label unavailable functional evidence
   Unverified rather than Pass.

## First Task to Execute Immediately

Execute `0.1`: author the track-local bootstrap, create the deterministic
review toolchain, and pass its disposable-fixture self-test with zero live
target touches before generating the frozen inventory or any backup/edit.

<!-- terminal-closeout-phase-b -->
## Terminal Closeout Record

- Phase A Stage 7: `ready_to_close` — `C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\validation-report-2026-07-27-123201Z.md`
- Stage 9 evidence: `C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\doc-update-log-2026-07-27-124021.md`
- Orchestrator Phase B: `PASS` — `C:\development\opencode\.conductor\tracks\20260726-agents-md-optimization-review\post-doc-validation-2026-07-27-124021.md`
