# Plan

## Global Execution Bound (Applies to Every Command)

Task 0.2 must create `C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py`. It must invoke a child argument vector with `subprocess.run(..., timeout=<seconds>, shell=False, check=False)`, capture stdout/stderr, terminate the child process tree on timeout, redact output before persistence, and return exit code `124` on timeout. It must pass one child and fail one child that exceeds a two-second synthetic timeout before any live inspection.

Every Python, PowerShell, Git, and OpenCode command in this plan—including diagnostics—must run through this wrapper with an explicit timeout. Direct command text in explanatory prose is an argument vector to the wrapper, never authorization for an unbounded invocation.

## Phase 0 - Setup & Preconditions

### Objective

Establish an immutable evidence baseline, exact review standards, and safe operating boundaries before ranking or editing.

- [x] **0.1 Capture the immutable baseline with an exact schema.**
  - Create `C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\capture_baseline.ps1`, then run it with `-RepoRoot "C:\development\opencode" -VaultRoot "C:\Users\DaveWitkin\.opencode-lazy-vault" -SkillRoot "C:\Users\DaveWitkin\.config\opencode\skill" -AgentRoot "C:\Users\DaveWitkin\.config\opencode\agent" -CodexSkillRoot "C:\Users\DaveWitkin\.codex\skills" -OutFile "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\baseline-inventory.json"`.
  - The JSON must contain UTC `captured_at`, canonical resolved paths, Codex `link_path` and `target_path`, per-root file lists/counts with SHA-256, redacted `git_status`, and `redaction_applied: true`; it must not contain file bodies, tokens, or secrets.
  - `capture_baseline.ps1` may enumerate names, paths, sizes, timestamps, and hashes only; it must reject content-bearing fields, resolve roots with `Resolve-Path -LiteralPath`, emit deterministic sorted arrays, and run through `run_bounded.py --timeout-seconds 120`.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check baseline --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints JSON `{"check":"baseline","status":"PASS"}` and exits `0`.
  - Diagnostic checks: compare baseline hashes after each correction cohort.
  - Recovery: if the resolved Codex target is not exactly the resolved vault root, write `baseline-topology-blocker.md`, leave all targets unchanged, and stop.

- [x] **0.2 Freeze the complete machine-readable review contract and verifier.**
  - Create `C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\review-rubric.md`, `schemas\skill-packet.schema.json`, `schemas\agent-packet.schema.json`, and `scripts\verify_portfolio_review.py`.
  - The skill schema must require a result (`Pass`, `Fail`, `Not Applicable`, or `Unverified`), severity, confidence, source path, and nonempty evidence/reason for every checklist item: scope/intent/decision tree; naming/placement; all-caps `SKILL.md`; frontmatter/name/description/triggers; progressive disclosure/one-level links; gotchas/default/alternatives; scripts/error handling/magic numbers/dependencies; forward-slash portability/compatibility; permissions/agent overrides; structural checks; functional smoke/trigger phrases/scripts/test case; troubleshooting.
  - The agent schema must require the same evidence fields for activation/purpose, frontmatter/body, mode, model/variant availability, permissions/least privilege, tools/skills, Windows/path/shell/bounded-command guidance, safety stops, output contract, overlap, smoke outcome, and Conductor diversity/applicability.
  - Use the stable skill IDs and agent IDs in the `Frozen Rubric IDs` appendix. Each ID must declare `required`, `conditional`, or `not_applicable_allowed`, its evidence type, and minimum nonempty evidence fields. The verifier must reject missing, duplicate, or unknown IDs; invalid N/A reasons; `Pass` without evidence; and packet identities that do not exactly equal the frozen 20/10 selections.
  - Dry-run the verifier on one passing and one deliberately incomplete synthetic packet; the incomplete packet must fail without reading any live skill/agent target.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check rubric --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"rubric","status":"PASS"}` and exits `0`.
  - Diagnostic checks: compare the frozen skill items with `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-creator\reference.md`.
  - Recovery: if a checklist item cannot be operationalized, record it in `rubric-open-question.md` and stop before selection.

- [x] **0.3 Create a safe evidence scaffold and Git-metadata backup root.**
  - Confirm the repository-local backup path is not ignored using `git -C "C:\development\opencode" check-ignore -v -- ".conductor/tracks/20260726-top-skills-agents-review/backups"`; record the observed `NOT_IGNORED` result and prohibit copying target contents there.
  - Resolve the live Git directory with `git -C "C:\development\opencode" rev-parse --path-format=absolute --git-dir`; require it to be a directory. Create evidence directories under the track and the actual backup root under the resolved Git directory at `codex-track-backups\20260726-top-skills-agents-review\2026-07-26-pre-edit`, which cannot be staged.
  - Write `backup-dir.json` containing the canonical backup path, `trackId`, `copy_targets_started: false`, and the destination-safety rationale.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check scaffold --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"scaffold","status":"PASS"}` and exits `0`.
  - Diagnostic checks: confirm the backup root is beneath the resolved `.git` directory and no target contents exist in the track directory.
  - Recovery: require the backup root to be absent or empty. Reuse it only when `trackId`, baseline capture hash, and immutable backup-manifest identity all match; otherwise stop.

### Exit Criteria

- Baseline, rubric, and backup scaffold exist; topology is safe; no deliverable artifact has been edited.

## Phase 1 - Usage Evidence and Portfolio Selection

### Objective

Select the actual review population from reproducible usage evidence rather than intuition.

- [x] **1.1 Inspect and record the read-only database contract.**
  - Adapt `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\scripts\query_sessions.py` into `C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\rank_portfolio.py`.
  - Run `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\rank_portfolio.py" --inspect-schema --db "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" --output "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\evidence\database-schema-summary.json" --read-only --timeout-seconds 60`.
  - The script must open `file:...opencode.db?mode=ro`, include archived sessions, emit only table/column names and aggregate counts, state the verified millisecond-to-UTC conversion, and never print/store raw message bodies.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check database-schema --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"database-schema","status":"PASS"}` and exits `0`.
  - Diagnostic checks: compare aggregate session/agent counts with `opencode stats`.
  - Recovery: if structured skill-call records are absent, record the precise missing tables/columns and enable only the documented inferred-signal fallback.

- [x] **1.2 Rank the portfolio reproducibly from the recorded contract.**
  - Before reading candidate totals, freeze `ranking-contract.json` with weights: observed frequency `0.55`, unique-session breadth `0.25`, recency `0.15`, and operational importance `0.05`. Normalize frequency and breadth as `value / maximum_value` within artifact type; compute recency as `exp(-days_since_last_use / 90)` from the captured UTC reference timestamp; score operational importance as `1.0` only for active safety/orchestration/validation infrastructure, `0.5` for active cross-client business workflow infrastructure, and `0.0` otherwise, with the classification reason recorded.
  - Missing signals contribute `0` and lower confidence; aliases and cross-source records deduplicate by resolved canonical identity before totals; eligible candidates must be active canonical artifacts. Implement final sort `(score desc, unique_sessions desc, recency desc, canonical_name casefold asc)`; embed the ranking-contract SHA-256 in `usage-ranking.json`.
  - Each candidate must include canonical path, artifact type, source signals, counts, recency, score components, confidence, and exclusion/tie-break rationale; fallback signals must be labeled `inferred`.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check ranking --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"ranking","status":"PASS"}` and exits `0`.
  - Diagnostic checks: preserve near-cutoff candidates and per-source totals; do not use metered cost as a universal activity proxy.
  - Recovery: do not invent zero/raw-body evidence; downgrade confidence and record the fallback rationale.

- [x] **1.3 Reconcile ranked candidates with live artifact identity and freeze the 20/10 selection.**
  - Resolve each selected skill to one canonical folder and each selected agent to one active definition; detect aliases, archived folders, package-managed duplicates, missing definitions, and naming collisions.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check selection --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"selection","status":"PASS","skills":20,"agents":10}` only when all selected artifacts are active, unique, canonical, scored, evidenced, and confidence-labeled.
  - Diagnostic checks: record excluded near-cutoff candidates and tie-break reasons in `usage-ranking.json`.
  - Recovery: replace a missing/archived candidate with the next-ranked active candidate and record the substitution; do not resurrect archived artifacts.

### Exit Criteria

- Exactly 20 canonical skills and 10 canonical agents are selected with source evidence and confidence labels.

## Phase 2 - Comprehensive Skill Review

### Objective

Apply the entire required skill checklist to every selected skill, with structural and representative behavioral evidence.

- [x] **2.1 Generate one complete static review packet per selected skill.**
  - For each selected skill, inspect the entire canonical folder and run every named frozen-rubric check. Parse frontmatter with the declared parser; enumerate internal links and scripts; record the exact command/output for syntax, link, frontmatter, uniqueness, length, portability, permission, guardrail, test-case, decision-tree, trigger-schema/two-phrase, script-error/magic-number/dependency, default/alternative, and progressive-disclosure results.
  - Write one packet per skill under `review-batches\skills\<canonical-name>.json` conforming to `skill-packet.schema.json`; `Pass` requires evidence, while `Unverified`/`Not Applicable` requires a precise reason.
  - Generate packets only by iterating the exact selected identities and exact rubric IDs; fail closed on missing/unknown IDs. Acceptance compares packet IDs as set equality with the frozen rubric, never a count or `rubric_complete` Boolean.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check skill-static --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"skill-static","status":"PASS","skills":20}` only when every selected name and every frozen checklist item is present with evidence/reason.
  - Diagnostic checks: run the skill-test harness structural mode and syntax parsers for included Python/PowerShell/JavaScript files.
  - Recovery: mark inaccessible or platform-dependent checks `Unverified` with the exact reason; never convert missing evidence into Pass.

- [x] **2.2 Run one safe representative functional smoke test for each selected skill.**
  - For each selected skill, run the harness through `run_bounded.py --timeout-seconds 60`, then execute at most one functional case in a disposable fixture directory through `run_bounded.py --timeout-seconds 180`.
  - Cap each case at one isolated session, 20 tool calls, and 10K token growth. Network and external mutations are prohibited. If a fixture cannot prove the role without credentials or external mutation, record `FUNCTIONAL_SMOKE_TEST_UNVERIFIED` and do not dispatch it.
  - Record the exact safe command/prompt, expected behavior, exit code, redacted output excerpt, and one verdict in the packet. Never send a message, change a calendar, publish, use credentials, mutate production, or perform a destructive operation.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check skill-functional --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"skill-functional","status":"PASS","skills":20}` only when every packet contains complete safe-test evidence or an explicit safety/credential reason for `FUNCTIONAL_SMOKE_TEST_UNVERIFIED`.
  - Diagnostic checks: preserve bounded test commands and redacted output excerpts under `evidence\skill-smoke-tests`.
  - Recovery: if a live test would mutate external state or require unavailable credentials, use a fixture/dry-run; if that is insufficient, mark Unverified rather than acting.

- [x] **2.3 Consolidate all skill evidence into the review matrix and prioritized fix queue.**
  - Generate `skill-review-matrix.md` from validated packets; each structured entry must contain canonical name, every rubric-item result, evidence reference, functional verdict, confidence, and exact proposed fix.
  - Create `fix-queue.json` only from high-confidence Critical/Major/Minor findings. Each queue entry must include a stable ID, canonical path, evidence reference, before/after intent, safety classification, and `authority_delta: none`.
  - Generate matrix and queue with one bounded script. Prove bidirectional reconciliation: every high-confidence Critical/Major/Minor finding has exactly one queue entry or explicit no-fix disposition, and every queue entry maps to exactly one finding.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check skill-matrix --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"skill-matrix","status":"PASS","skills":20}` only when the matrix is derived from all packets and every queued fix maps one-to-one to a high-confidence finding.
  - Diagnostic checks: list Optional items separately and ensure no unresolved Critical/Major item is omitted.
  - Recovery: conflicting or subjective findings remain Optional/Unverified and are not auto-fixed.

### Exit Criteria

- All 20 selected skills have complete rubric packets, functional verdicts, and a consolidated matrix.

## Phase 3 - Comprehensive Agent Review

### Objective

Review the 10 selected agent definitions for correctness, safety, routing, and overlap.

- [x] **3.1 Generate one complete review packet per selected agent.**
  - For each selected agent, inspect frontmatter and complete prompt body, active-definition resolution, configured model/variant against `opencode models`, parsed permissions/tools/skills, Windows-safe bounded-command guidance, safety stops, output contract, role overlap, and applicable Conductor diversity.
  - Write a schema-valid packet under `review-batches\agents\<canonical-name>.json` with result, severity, confidence, evidence, and source line range for every frozen agent-rubric item.
  - Run `opencode models` and the agent inventory through `run_bounded.py --timeout-seconds 60`; a route passes only when the exact provider/model and requested variant are supported. Permission results come from parsed definitions/config, not prose.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check agent-static --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"agent-static","status":"PASS","agents":10}` only when every selected agent and every rubric item has evidence/reason.
  - Diagnostic checks: compare `opencode agent list`, `opencode models`, current config permissions, and related Conductor model-diversity rules.
  - Recovery: do not change a model or permission based on style preference; require a concrete failure, inconsistency, safety risk, or obsolete route.

- [x] **3.2 Run bounded representative dry-run/smoke checks and build the agent matrix.**
  - Create one fixture-only prompt JSON record per selected agent with allowed tools, prohibited effects, expected output shape, working directory, and configured model/variant.
  - Run `opencode run --pure --agent "<canonical-agent-name>" --format json --dir "<disposable-fixture-directory>" "<fixture-prompt>"` through `run_bounded.py --timeout-seconds 180`, without `--auto`, sharing, credentials, attachments, or an existing server. Cap each case at one new session, 20 tool calls, and 10K token growth; unavailable safe routes are `Unverified` without substitution.
  - Generate `agent-review-matrix.md` from the packets and append only high-confidence, evidence-backed Critical/Major/Minor fixes to `fix-queue.json`.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check agent-matrix --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"agent-matrix","status":"PASS","agents":10}` only when every selected agent has complete rubric and smoke evidence/reason and every queued fix maps to a finding.
  - Diagnostic checks: preserve commands, session IDs, exit codes, and redacted outcome summaries in `evidence\agent-smoke-tests`.
  - Recovery: unavailable models or unsafe live paths are recorded as Unverified; do not silently substitute a different model when testing the definition itself.

### Exit Criteria

- All 10 selected agents have complete review packets, bounded test evidence or explicit Unverified reasons, and a consolidated matrix.

## Phase 4 - Safe Corrections

### Objective

Apply only verified, high-confidence fixes while preserving rollback and unrelated user work.

- [x] **4.1 Back up every target in the approved fix queue and verify the backup manifest.**
  - Encode each destination as the lowercase SHA-256 of the canonical source path plus a sanitized leaf name; reject collisions. Write `backup-manifest.json` with source path, backup path, source/backup SHA-256 tree hashes, target type, queue IDs, preexistence marker, and exact restore command.
  - If the queue has zero distinct targets, emit `status: NOT_APPLICABLE`, `targets: 0`, and no `PASS`.
  - For files, restore by bounded copy to a temporary sibling, verify SHA-256, then replace the exact file. For directories, restore to a temporary sibling, verify the sorted tree hash, then replace the exact target directory so introduced files cannot survive overlay. Recompute the restored target hash and require equality with the pre-edit manifest; never restore an unmanifested target.
  - Do not copy a target until Task 0.3's destination-safety gate passes; never store target bodies in the track directory.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check backups --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"backups","status":"PASS","targets":N}` only when `N` equals the distinct queued target count and every entry has hash-equal backup material or an absent-before-edit marker.
  - Diagnostic checks: compare counts and hashes; verify backups are under this track only.
  - Recovery: if any backup cannot be verified, remove that target from execution and leave its finding unresolved.

- [x] **4.2 Apply queued skill fixes in disjoint bounded cohorts.**
  - Process only backed-up skill targets named in `fix-queue.json`; preserve capability and authority; keep `SKILL.md` concise; do not rename, archive, merge, delete, or publish.
  - For every change, record queue ID, target, before/after hashes, diff path, correction, and `authority_delta: none` in `change-manifest.json`; compare tracked targets with `git diff -- <path>` and untracked targets with `git diff --no-index <backup> <target>`.
  - Derive authority/capability deltas from parsed before/after entrypoint, permissions, tools, external-action verbs, and referenced scripts; self-reported `authority_delta` is supporting metadata only.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check skill-changes --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"skill-changes","status":"PASS","changes":N}` only when every changed skill is queued, backed up, diffed, and no unapproved file/authority expansion exists; zero changes must return `NOT_APPLICABLE`, not vacuous `PASS`.
  - Diagnostic checks: use `git diff --no-index` from backups to targets and inspect all supporting files, not only `SKILL.md`.
  - Recovery: if a fix expands capability or changes authority boundaries, revert that target from the track backup and move the item to Dave-decision.

- [x] **4.3 Apply queued agent fixes in disjoint bounded cohorts.**
  - Process only backed-up active agent definitions named in `fix-queue.json`; preserve role/model diversity and do not edit backups or obsolete `.bak` files.
  - Parse and record before/after permission, tool, skill, model, and variant fields; permission/tool/skill expansion or silent model substitution is a blocker, not a self-reported Boolean.
  - A failed/ambiguous comparison must invoke Task 4.1's exact target replacement and post-restore hash check before the cohort continues.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check agent-changes --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"agent-changes","status":"PASS","changes":N}` only when every changed agent maps to a backup and queue item with no parsed permission/tool/skill broadening; zero changes returns `NOT_APPLICABLE`.
  - Diagnostic checks: parse frontmatter, resolve configured models, and compare full before/after diffs.
  - Recovery: on an unavailable route or ambiguous permission change, restore from backup and retain the finding for decision.

### Exit Criteria

- Every applied change maps to one high-confidence queue item, has a verified backup and narrow diff, and crosses no authority boundary.

## Phase 5 - Validation and Portfolio Report

### Objective

Prove the changed artifacts work and deliver a decision-ready review of the complete selected portfolio.

- [x] **5.1 Structurally and functionally revalidate every changed skill.**
  - Derive the exact changed-skill set from `change-manifest.json`; run every applicable structural, script-syntax, safe script-functional, trigger, and representative harness check required by its packet; write evidence-linked `validation-results.json`.
  - Reuse the original packet's fixture and bounds. On failure, complete Task 4.1's exact restore and post-restore tree-hash check or leave the task unchecked with a blocker.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check changed-skills --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"changed-skills","status":"PASS|NOT_APPLICABLE"}` only when the validated set exactly equals the manifest set and each changed skill passes all applicable checks.
  - Diagnostic checks: compare pre/post review packets and capture script outputs.
  - Recovery: restore any failed changed skill from backup unless the failure is proven pre-existing and the change reduces risk; otherwise leave it changed only with an explicit blocker and rationale.

- [x] **5.2 Parse and smoke-test every changed agent, then verify cross-agent constraints.**
  - Derive changed agents from `change-manifest.json`; parse each definition, confirm its configured route, run its bounded safe smoke case, and evaluate diversity only for applicable changed Conductor roles.
  - Reuse the exact Task 3.2 fixture, model, variant, permission mode, and working directory; any deviation invalidates before/after comparison unless explicitly marked `Unverified`.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check changed-agents --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"changed-agents","status":"PASS|NOT_APPLICABLE"}` only when the validated set equals the manifest set and no applicable model, permission, or diversity defect remains.
  - Diagnostic checks: `opencode agent list`, `opencode models`, and bounded role-specific dry-runs.
  - Recovery: restore a failing agent from backup and record the unresolved finding; do not weaken validation or swap models silently.

- [x] **5.3 Write the decision-ready portfolio report.**
  - Generate `portfolio-review-report.md` from ranking, packet, queue, manifest, and validation JSON. Include exactly 20 structured skill entries and 10 agent entries, methodology/confidence, fixes, validation, unresolved Critical/Major/Minor findings, Optional improvements, explicit Unverified items, and Dave decisions.
  - Generate the report with one bounded command from immutable sources; reconcile stable identity and finding-ID sets, not headings/row counts alone.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check portfolio-report --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"portfolio-report","status":"PASS","skills":20,"agents":10}` only when entries and all finding/change/decision counts reconcile to the source JSON.
  - Diagnostic checks: cross-check all counts against `usage-ranking.json`, matrices, fix queue, change manifest, and validation results.
  - Recovery: if evidence conflicts, report the conflict and lower confidence; never choose the more favorable number without support.

### Exit Criteria

- All changed artifacts are confirmed or restored; the report accounts for all 20 skills, all 10 agents, every material finding, and every decision item.

## Final Phase - Validation & Handover

### Objective

Synchronize Conductor evidence and obtain independent closeout readiness.

- [x] **F.1 Write the execution log and reconcile all task/metadata counts.**
  - Create `execution-log-2026-07-26.md` with a dated command/result/deviation/skipped-item/model-session table; synchronize metadata from actual plan states: `totalTasks: 21`, completed count, derived percentage, `readiness_check_count: 8`, and `total_checkbox_count: 29`; preserve the pipeline fields and record the B+C/A+C decisions from `threshold-policy.md`.
  - `metadata.status` remains `planned` before execution, becomes `in_progress` after the first completed task, and becomes `complete` only after terminal Phase B.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check execution-sync --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"execution-sync","status":"PASS","tasks":21,"checkboxes":29}` only when counts, percentage, pipeline fields, and nonempty execution-log rows reconcile.
  - Diagnostic checks: count readiness checkboxes separately from executable tasks.
  - Recovery: correct bookkeeping without rewriting historical evidence; use an audit-correction artifact for a material reporting mismatch.

- [x] **F.2 Upsert the single track row in both Conductor ledgers.**
  - Update `.conductor\tracks.md` and `.conductor\tracks-ledger.md` in place with the same status/date/progress convention and no duplicate row.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check ledgers --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"ledgers","status":"PASS"}` only when each ledger contains exactly one structurally parsed record whose status/date/progress equals metadata.
  - Diagnostic checks: parse both ledgers and compare track ID, status, date, executable-task progress, and uniqueness as structured fields; visual comparison is optional only.
  - Recovery: update the existing row; never append a second row.

- [x] **F.3 Obtain independent Stage 7 closeout-readiness validation.**
  - Atomically select/update `.conductor\validator-alternation.json`, pass the validator all absolute artifact paths and the Stage 7 prompt, and write a timestamped report containing validator identity, task reconciliation, artifact evidence, blockers, Stage 9 readiness, and structured `verdict`; also write `anomaly-summary-2026-07-26.md`.
  - Record prior `last_used`, selected validator, resulting `last_used`, model identity, and diversity comparison. Bound dispatch-side calls and cap the validator at 40 tool calls/30K token growth.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check stage7 --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"stage7","status":"PASS","verdict":"ready_to_close"}` only when the newest report selected by parsed timestamp has the expected validator identity, zero unresolved blockers, and evidence for every non-deferred task.
  - Diagnostic checks: verify every claimed artifact exists, all non-deferred tasks are complete, and matrices/report/counts agree.
  - Recovery: route concrete blockers under the bounded correction-cycle policy; stop on repeated signatures or authority-sensitive changes.

- [x] **F.4 Complete Stage 9 documentation closeout and terminal confirmation.**
  - Write `doc-update-log-<UTC timestamp>.md` listing each documentation file, before/after contract assessment, and whether post-doc validation is required. If required, write `post-doc-validation-<UTC timestamp>.md`; otherwise record a dated reasoned waiver in both the doc log and execution log. Set metadata `complete` only after Phase B passes.
  - Select Stage 9/post-doc artifacts by parsed UTC timestamp and schema, never filesystem enumeration order; compare documentation changes to the pre-Stage-9 manifest.
  - Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py" --check terminal-closeout --track "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"` prints `{"check":"terminal-closeout","status":"PASS"}` only when the newest parsed doc log has a valid companion/waiver, no unpermitted semantic change, and final metadata is complete.
  - Diagnostic checks: confirm Stage 9 made no source/skill/agent changes and documentation introduced no unsupported contract.
  - Recovery: route back to Stage 9 once for missing closeout evidence, then stop and surface any remaining blocker.

### Exit Criteria

- Independent validation is ready-to-close; Stage 9 evidence or waiver exists; metadata and ledgers are synchronized; the portfolio report is the authoritative handoff.

## Execution-Readiness Checklist

- [ ] The selected pipeline and skipped-stage reasons are recorded in `metadata.json`.
- [ ] Every executable task has exactly one authoritative acceptance check.
- [ ] All commands use exact paths and bounded, non-interactive behavior.
- [ ] Backups precede edits; junction and unversioned-global-file hazards are addressed.
- [ ] Skill reviews use every applicable `skill-creator` checklist category.
- [ ] Functional confirmation is distinct from structural validation.
- [ ] External mutations, publication, restarts, destructive actions, schedule changes, and permission broadening remain out of scope.
- [ ] Parallel work, if used, is limited to disjoint review packets; shared manifests and plan bookkeeping are updated serially.

## Top Risks and Mitigations

1. **Usage evidence may not expose structured skill invocations.** Mitigation: inspect schema first, use an explicit evidence hierarchy, label confidence, and preserve near-cutoff candidates.
2. **Twenty functional skill tests can accidentally cross external authority boundaries.** Mitigation: use fixtures/dry-runs and mark Unverified when safe confirmation is impossible.
3. **Parallel reviews can conflict or become inconsistent.** Mitigation: use disjoint per-artifact packets, one frozen rubric, serial consolidation, and independent validation.

## Frozen Rubric IDs

Task 0.2 must encode these exact sets in the schemas. Each packet must contain set equality with its applicable set; unknown or duplicate IDs fail.

### Skill item IDs

- Required for every selected skill: `SCOPE_01_ONE_CAPABILITY`, `SCOPE_02_REALISTIC_TRIGGERS`, `NAME_01_FOLDER_SLUG`, `NAME_02_SKILL_MD_CASE`, `NAME_03_FRONTMATTER_REQUIRED`, `NAME_04_UNIQUE_IDENTITY`, `NAME_05_REGEX_AND_LENGTH`, `DESC_01_WHAT_WHEN_KEYWORDS`, `DESC_02_LENGTH`, `DESC_03_NOT_VAGUE`, `FM_01_OPTIONAL_FIELDS_JUSTIFIED`, `TRIG_03_UNKNOWN_KEYS_NOT_RELIED_ON`, `STRUCT_01_ENTRYPOINT_SIZE`, `STRUCT_02_ADVANCED_DETAILS_DISCLOSED`, `STRUCT_03_ONE_LEVEL_REFERENCES`, `GUARD_01_GOTCHAS`, `GUARD_02_DEFAULT_AND_ALTERNATIVES`, `GUARD_03_CONCISE_ACTIONABLE_EXAMPLES`, `PATH_01_FORWARD_SLASH_DOCS`, `PATH_02_COMPATIBILITY`, `TEST_01_ACTIVATION`, `TEST_02_SAFE_END_TO_END`, `TEST_05_STRUCTURAL_AND_FUNCTIONAL`, `TEST_06_TEST_CASE_CONVENTION`, `HANDOFF_01_PUBLISH_DECISION`, `TROUBLE_01_YAML`, `TROUBLE_02_UNIQUENESS`, `TROUBLE_03_PERMISSION_VISIBILITY`, `TROUBLE_04_REFERENCE_EXISTENCE`.
- Conditional, with a nonempty applicability reason required: `SCOPE_03_DECISION_TREE` when multiple tools/options/products exist; `TRIG_01_V1_SCHEMA`, `TRIG_02_SUGGEST_ONLY_TRUE`, and `TEST_04_TWO_TRIGGER_PHRASES` when `triggers` exists; `STRUCT_04_MULTI_FILE_LAYOUT` for complex domains; `SCRIPT_01_ERROR_HANDLING`, `SCRIPT_02_MAGIC_NUMBERS`, `SCRIPT_03_DEPENDENCIES`, `SCRIPT_04_SYNTAX`, and `SCRIPT_05_SAFE_FUNCTIONAL` when scripts exist; `PERM_01_SENSITIVE_APPLICABILITY`, `PERM_02_PERMISSION_PATTERNS`, and `PERM_03_AGENT_OVERRIDES` when the skill can access secrets, production, destructive operations, or restricted tools; `TEST_03_CRITICAL_EVALUATION` for critical skills.
- `HANDOFF_01_PUBLISH_DECISION` must be `Not Applicable` with reason `review-only; no publish requested` unless a skill was materially updated and validated. Even then, publication remains prohibited in this track; the final report asks Dave separately.

Every item requires `result`, `severity`, `confidence`, `source_path`, and `evidence`. `Pass` requires nonempty command/inspection evidence; `Not Applicable` and `Unverified` require a nonempty applicability/blocker reason.

### Agent item IDs

- Required: `AGENT_01_IDENTITY_PURPOSE`, `AGENT_02_FRONTMATTER_BODY_PARSE`, `AGENT_03_MODE`, `AGENT_04_MODEL_ROUTE`, `AGENT_05_VARIANT`, `AGENT_06_PERMISSIONS_LEAST_PRIVILEGE`, `AGENT_07_TOOLS_SKILLS`, `AGENT_08_WINDOWS_PATH_SHELL`, `AGENT_09_BOUNDED_COMMANDS`, `AGENT_10_SAFETY_STOPS`, `AGENT_11_OUTPUT_CONTRACT`, `AGENT_12_ROLE_OVERLAP`, `AGENT_13_SMOKE_OUTCOME`.
- Conditional: `AGENT_14_CONDUCTOR_DIVERSITY` for Conductor creator/reviewer/executor/validator roles; `AGENT_15_EXTERNAL_AUTHORITY_BOUNDARY` for agents capable of messaging, publishing, scheduling, credential use, or production mutation; `AGENT_16_CROSS_FIELD_CONSISTENCY` whenever permissions/tools/model/mode constrain statements in the body.

Each agent item uses the same evidence/result rules as skill items. `AGENT_04_MODEL_ROUTE` and `AGENT_05_VARIANT` require exact live inventory evidence; `AGENT_06_PERMISSIONS_LEAST_PRIVILEGE` and `AGENT_07_TOOLS_SKILLS` require parsed fields; `AGENT_14_CONDUCTOR_DIVERSITY` requires the applicable cross-agent comparison.

## First Task to Execute

Task 0.1: capture and verify the live baseline before any ranking or edit.

