# Stage 3 Conditional Re-review — Top Skills and Agents Portfolio

Date: 2026-07-26  
Track: `20260726-top-skills-agents-review`  
Stage: 3 — one bounded conditional re-review  
Verdict: **Needs Work — not execution-ready**

## Executive conclusion

The revision fixes the first review's headline structural defects: the plan now has exactly 21 executable tasks, 29 total checkboxes, and one authoritative acceptance check, diagnostic section, and recovery section for each task. Metadata records `pipeline_mode: bookkeeping`, the deliberately expanded path `1 -> 2 -> 5 -> 7 -> 9`, 21 executable tasks, 8 readiness checks, and 29 total checkboxes.

Execution should still **not** begin. Five material blockers remain:

1. The planned skill and agent evidence schemas are category summaries, not a frozen item-by-item rubric with stable IDs, conditional applicability rules, and complete coverage of the controlling skill checklist.
2. The ranking task refers to a “documented scoring formula” but supplies no formula or weights, so two executors can produce different top-20/top-10 portfolios.
3. All 21 authoritative commands parse, but none is explicitly time-bounded and all target a verifier that does not yet exist. The Stage 2/3 prompt therefore requires them to remain untested and prevents a Ready rating.
4. The skill and agent smoke-test tasks have sound authority prohibitions but no exact bounded agent invocation, per-test timeout, total session/tool-call cap, or deterministic disposable fixture contract.
5. The backup location is currently outside the worktree and cannot be staged, but directory restore semantics are incomplete: the destination-name encoding is undefined, zero-target handling can pass vacuously, restore-by-overlay can leave newly introduced files behind, and no post-restore tree-hash gate is required.

The B+C threshold was correctly triggered because the first-pass readiness score was 22/100. This report consumes the one permitted Stage 3 extra pass. Under the threshold policy, unresolved plan blockers now require a pause for manual plan correction or explicit approval to proceed with known risks.

## Readiness score

**63/100**

| Dimension | Score | Finding |
|---|---:|---|
| Structure, counts, ordering, metadata | 20/20 | Corrected and internally consistent for the requested bookkeeping route. |
| Atomicity, paths, and executor guidance | 15/20 | Phase order and paths are strong; several tasks still state outcomes without an exact creation/execution command. |
| Evidence schema and non-vacuous proof | 12/20 | Canonical verifier architecture is a major improvement, but rubric itemization and several zero-state contracts remain incomplete. |
| Backup and recovery safety | 8/15 | Destination is presently unstaged and isolated, but exact restore and post-restore proof are not safe enough for folders. |
| Smoke-test safety and bounds | 8/15 | External-authority restrictions are good; runtime, session, and fixture bounds are missing. |
| Reviewer command confirmation | 0/10 | 21/21 commands parse; 0/21 are runnable now, and 0/21 carry an explicit timeout. |

The score includes more than the required five-point deduction for reviewer-added commands that cannot be dry-run against either real outputs or a completed temporary implementation.

## Standards and artifacts reviewed

- `spec.md`
- `plan.md`
- `metadata.json`
- `review-report-peer-2026-07-26.md`
- `review-diff-summary-2026-07-26.md`
- `conductor-pipeline/references/stage-prompts.md`, especially Stage 2/3 and the all-stage anti-stall rule
- `conductor-pipeline/references/threshold-policy.md`, especially the B+C trigger, bookkeeping selection, metadata counting, iteration cap, and authority boundaries
- The required checklist in `skill-creator/reference.md` for direct coverage comparison

No plan task was executed. No skill, agent, spec, plan, or metadata file was changed.

## Structural verification

| Required property | Result | Evidence |
|---|---|---|
| Exactly 21 executable tasks | **PASS** | Static count: 21 task checkboxes. |
| Exactly 29 total checkboxes | **PASS** | Static count: 21 tasks + 8 readiness checks. |
| Exactly 21 authoritative acceptance checks | **PASS** | Static count: 21; every task block contains exactly one. |
| Exactly 21 diagnostic sections | **PASS** | Static count: 21; every task block contains exactly one. |
| Exactly 21 recovery sections | **PASS** | Static count: 21; every task block contains exactly one. |
| Metadata task/readiness/total counts | **PASS** | `21`, `8`, and `29`, respectively. |
| Bookkeeping mode and requested path | **PASS** | `bookkeeping`; `1 -> 2 -> 5 -> 7 -> 9`; Stage 2 retention is rationalized by broad unversioned global-artifact risk. |
| Complete skill evidence-schema rubric | **BLOCKING** | Coarse categories are listed, but stable item IDs, per-item applicability rules, exact item count, and several controlling checklist details are not frozen. |
| Complete agent evidence-schema rubric | **BLOCKING** | Categories are listed, but no stable IDs, conditional/applicability logic, or exact packet-level cross-field rules are supplied. |
| Non-vacuous acceptance behavior | **PARTIAL** | Zero-change `NOT_APPLICABLE` is specified for four change/validation checks; backup zero-target behavior and literal `PASS|NOT_APPLICABLE` output remain ambiguous. |
| Safe untracked backup destination | **PARTIAL PASS** | Live check resolves `.git` to `C:\development\opencode\.git`, a directory; the planned root does not yet exist and cannot be staged. It is not “external” to the repository, and restore semantics remain incomplete. |
| Verified restore mapping | **BLOCKING** | Manifest fields are planned, but exact folder replacement, introduced-file removal, destination collision prevention, and post-restore tree-hash equality are not required. |
| Authority-safe smoke tests | **PASS on authority / BLOCKING on bounds** | External messages, calendar edits, publication, credentials, production mutation, and destructive operations are prohibited; exact timeout/session/fixture limits are absent. |

## Safe command parsing and simulation

- All 21 authoritative command lines parse successfully as PowerShell command syntax.
- The 21 distinct verifier check IDs are present: `baseline`, `rubric`, `scaffold`, `database-schema`, `ranking`, `selection`, `skill-static`, `skill-functional`, `skill-matrix`, `agent-static`, `agent-matrix`, `backups`, `skill-changes`, `agent-changes`, `changed-skills`, `changed-agents`, `portfolio-report`, `execution-sync`, `ledgers`, `stage7`, and `terminal-closeout`.
- `scripts\verify_portfolio_review.py`, `scripts\rank_portfolio.py`, `scripts\capture_baseline.ps1`, both packet schemas, and `review-rubric.md` do not yet exist. This is expected before execution, but it means none of the expected PASS outputs can be confirmed during review.
- Zero of the 21 authoritative commands includes an explicit timeout or bounded wrapper.
- The exact `git check-ignore -v -- ".conductor/tracks/20260726-top-skills-agents-review/backups"` check exits `1`, confirming the repository-local track backup path is not ignored. The plan correctly prohibits target copies there.
- The planned root `C:\development\opencode\.git\codex-track-backups\20260726-top-skills-agents-review\2026-07-26-pre-edit` is beneath the live `.git` directory and does not currently exist.
- `opencode run --help` confirms a non-interactive agent invocation can use `--agent`, `--format json`, `--dir`, and a positional prompt. The plan does not state that exact command or wrap it in a timeout.
- The skill harness accepts `-SkillPath` and `-PrintFunctionalPrompt`; that call is structural/prompt generation only. The plan does not define the subsequent exact functional invocation or its timeout.

## Task-by-task ratings

Every task is at least **Needs Work** because its authoritative verifier command cannot currently be run or simulated to the claimed PASS result. Tasks are **Blocking** where the task text itself also leaves a material scope, determinism, safety, or rollback gap.

| Task | Phase | Rating | Re-review finding |
|---|---|---|---|
| 0.1 Capture baseline | Phase 0 | Needs Work | Exact run command and schema intent are present, but the capture implementation is left for the executor and its acceptance command is absent/unbounded. |
| 0.2 Freeze rubric and verifier | Phase 0 | **Blocking** | The rubric is not itemized to stable IDs and does not fully encode the controlling checklist's conditional rules and evidence semantics. |
| 0.3 Safe scaffold and backup root | Phase 0 | Needs Work | Destination is isolated from staging, but “external” is inaccurate and reuse/canonicalization protections are incomplete. |
| 1.1 Inspect database contract | Phase 1 | Needs Work | Read-only URI, archived-session scope, redaction, and 60-second internal timeout are good; the new script and its verifier are untested. |
| 1.2 Rank portfolio | Phase 1 | **Blocking** | No scoring formula, weights, normalization, missing-signal rule, or cross-source de-duplication rule is actually documented. |
| 1.3 Freeze 20/10 selection | Phase 1 | Needs Work | Selection proof is strong in intent, but the resolution/classification operation has no exact command and depends on the missing verifier. |
| 2.1 Static skill packets | Phase 2 | **Blocking** | Completeness depends on the incomplete rubric; no exact packet-generation command or stable per-item contract is supplied. |
| 2.2 Functional skill smoke tests | Phase 2 | **Blocking** | Authority limits are strong, but the harness only prints a prompt; the actual test invocation, fixture, timeout, and total bound are unspecified. |
| 2.3 Skill matrix and queue | Phase 2 | Needs Work | Source reconciliation is non-shallow, but generation is prose and queue completeness depends on the unproven packet/rubric contract. |
| 3.1 Static agent packets | Phase 3 | **Blocking** | The agent categories are good but not frozen as item IDs/cross-field rules; `opencode models` and related inspections are unbounded. |
| 3.2 Agent smoke tests and matrix | Phase 3 | **Blocking** | No exact `opencode run` command, deterministic prompt envelope, timeout, session cap, or disposable working directory is supplied. |
| 4.1 Backups and restore map | Phase 4 | **Blocking** | Tree hashes and manifest fields are good; encoding, zero-target disposition, exact folder replacement, and post-restore equality are missing. |
| 4.2 Skill fixes | Phase 4 | Needs Work | Queue/backup/diff linkage and zero-change N/A are good; skill authority comparison remains partly self-reported and restore inherits Task 4.1's blocker. |
| 4.3 Agent fixes | Phase 4 | Needs Work | Parsed permission/tool/skill comparison and zero-change N/A are good; restore inherits Task 4.1's blocker. |
| 5.1 Revalidate changed skills | Phase 5 | Needs Work | Exact manifest-set reconciliation is non-vacuous; bounded functional commands and a required post-restore hash check are missing. |
| 5.2 Revalidate changed agents | Phase 5 | Needs Work | Exact changed-set and applicability handling are good; smoke execution remains unbounded and underspecified. |
| 5.3 Portfolio report | Phase 5 | Needs Work | Counts and source reconciliation are rigorous in intent; no exact generation command exists and verifier behavior is untested. |
| F.1 Execution log and metadata | Final | Needs Work | Count contract is correct; `status/stage` transition rules and bounded verifier execution should be explicit. |
| F.2 Ledger upsert | Final | Needs Work | Structural acceptance is good; the mutation is prose and the diagnostic remains visual rather than deterministic. |
| F.3 Stage 7 validation | Final | Needs Work | Phase-A content is correct; atomic alternation and validator dispatch are not given as an exact bounded operation. |
| F.4 Stage 9 and Phase B | Final | Needs Work | Terminal evidence contract is good; timestamp selection, bounded verifier execution, and semantic-change comparison remain implemented only by the absent verifier. |

## Exact corrections required before execution

The following text is the minimum targeted correction. It can be incorporated without changing the track's 21-task/29-checkbox contract.

### Global command-bound rule — add to Phase 0 and apply to every task

> Create `C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py` in Task 0.2. It must invoke a child argument vector with `subprocess.run(..., timeout=<seconds>, shell=False, check=False)`, capture stdout/stderr, terminate the child process tree on timeout, redact output before persistence, and return exit code `124` on timeout. Dry-run it against one passing child and one child that exceeds a two-second timeout. Every Python, PowerShell, Git, and OpenCode command in this plan, including diagnostics, must run through this wrapper with an explicit timeout; no direct unbounded invocation is permitted.

Replace each authoritative command's direct `python "...verify_portfolio_review.py"` prefix with:

> `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 120 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\verify_portfolio_review.py"`

Keep the existing `--check ... --track ...` suffix for the applicable task.

### 0.1 — append

> `capture_baseline.ps1` must be created from a complete inline field map in `review-rubric.md`; it may enumerate names, paths, sizes, timestamps, and hashes only. It must reject content-bearing fields, resolve every root with `Resolve-Path -LiteralPath`, and emit a deterministic sorted array. Run it through `run_bounded.py --timeout-seconds 120`.

### 0.2 — replace the rubric-contract bullets with

> Assign a stable ID to every individual controlling checklist item, not only to category summaries. At minimum, encode separate IDs for one-capability scope; realistic trigger words; conditional decision tree; folder syntax; `SKILL.md` casing; frontmatter name/description; uniqueness; name regex and length; description content, length, and vagueness; optional-field justification; trigger v1 keys, `suggest_only`, and unknown-key non-reliance; entrypoint size; one-level references; optional multi-file layout applicability; gotchas; default/alternatives; concise examples; script errors, magic numbers, dependencies, syntax, and safe functional test; forward-slash documentation paths; compatibility; global permission applicability; permission patterns; per-agent overrides; activation; end-to-end safe task; critical-skill evaluation applicability; two trigger-phrase tests when triggers exist; structural-plus-functional confirmation; publish decision marked Not Applicable for review-only work; troubleshooting YAML, uniqueness, permission visibility, and reference existence. Each ID must declare `required`, `conditional`, or `not_applicable_allowed`, plus the evidence type and minimum nonempty evidence fields. The agent rubric must likewise use stable IDs and explicit applicability/cross-field rules for every named category. The verifier must reject missing IDs, duplicate IDs, unknown IDs, empty evidence, invalid N/A reasons, Pass without evidence, and packet selections that do not exactly equal the frozen 20/10 identities.

### 0.3 — append

> Resolve the live Git directory with `git -C "C:\development\opencode" rev-parse --path-format=absolute --git-dir`; do not hardcode `.git` until the resolved path is confirmed to be a directory. Require the planned backup root to be absent or empty. If it exists, reuse it only when `trackId`, baseline capture hash, and immutable backup-manifest identity all match; otherwise stop.

### 1.1 — replace the direct ranking command with

> `python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\run_bounded.py" --timeout-seconds 90 -- python "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\scripts\rank_portfolio.py" --inspect-schema --db "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" --output "C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review\evidence\database-schema-summary.json" --read-only --timeout-seconds 60`

### 1.2 — replace the undefined formula clause with

> Freeze `ranking-contract.json` before reading candidate totals. It must contain numeric weights summing to 1.0 for observed frequency, unique-session breadth, recency, and operational importance; normalization equations; the recency reference timestamp; missing-signal behavior; per-source confidence downgrades; alias/canonical de-duplication; candidate eligibility; and the final sort `(score desc, unique_sessions desc, recency desc, canonical_name casefold asc)`. `usage-ranking.json` must embed the SHA-256 of this contract. If the weights are not already approved in the spec or an existing controlling artifact, stop for Dave's decision rather than inventing them.

### 1.3 — append

> Resolve candidates with a generated, bounded selection command that writes canonical path, link path, target path, active-state reason, and replacement lineage. The verifier must reject a selected record whose path is missing, archived, package-managed-only, duplicated by resolved identity, or absent from the scored candidate list.

### 2.1 — append

> Generate packets only by iterating the exact `selected_skills` identities and exact rubric IDs. The packet generator must fail closed on a missing or unknown rubric ID, and the authoritative verifier must compare packet IDs as set equality with the frozen rubric, not as a count.

### 2.2 — replace the execution sentence with

> For each selected skill, run the harness through `run_bounded.py --timeout-seconds 60`. The harness output is planning evidence only. Execute at most one functional case per skill in a disposable fixture directory, through `run_bounded.py --timeout-seconds 180`, with network and external mutations prohibited. Cap each case at one OpenCode session, 20 tool calls, and 10K token growth. If a fixture cannot prove the role without credentials or external mutation, record `FUNCTIONAL_SMOKE_TEST_UNVERIFIED` and do not dispatch it.

### 2.3 — append

> Generate the matrix and queue with one bounded script invocation. The verifier must prove bidirectional reconciliation: every high-confidence Critical/Major/Minor packet finding has exactly one queue or explicit no-fix disposition, and every queue item maps to exactly one packet finding.

### 3.1 — append

> Freeze stable agent-rubric IDs and cross-field assertions before review. Run `opencode models` and agent inventory through `run_bounded.py --timeout-seconds 60`; a route is available only when the exact provider/model and requested variant are supported. A Pass for permissions must be derived from parsed before-state, not prose.

### 3.2 — replace the smoke-execution sentence with

> Create one fixture-only prompt JSON record per selected agent, including allowed tools, prohibited effects, expected output shape, working directory, and configured model/variant. Run `opencode run --pure --agent "<canonical-agent-name>" --format json --dir "<disposable-fixture-directory>" "<fixture-prompt>"` through `run_bounded.py --timeout-seconds 180`, without `--auto`, sharing, credentials, or attachment to an existing server. Cap each case at one new session, 20 tool calls, and 10K token growth. If the configured route or safe fixture is unavailable, record Unverified; do not substitute a model.

### 4.1 — replace the restore-map clause with

> Encode each destination name as the lowercase SHA-256 of the canonical source path plus a sanitized leaf name; reject collisions. If the queue has zero distinct targets, emit `status: NOT_APPLICABLE`, `targets: 0`, and no PASS. For a file, restore by bounded copy to a temporary sibling, verify SHA-256, then replace the exact file. For a directory, restore to a temporary sibling, verify the complete sorted tree hash, then replace the exact target directory so files introduced by the failed edit cannot survive an overlay copy. After restore, recompute the target tree hash and require equality with the pre-edit manifest hash. Never restore a target not named by the manifest.

### 4.2 — append

> Derive skill authority/capability deltas from parsed before/after entrypoint, permissions, tools, external-action verbs, and referenced scripts. A self-reported `authority_delta: none` is supporting metadata only; parsed evidence is authoritative.

### 4.3 — append

> A failed or ambiguous parsed comparison must invoke Task 4.1's exact target replacement and post-restore hash check before the cohort can continue.

### 5.1 — append

> Run every structural and functional validation through `run_bounded.py` with the same fixture and bounds recorded in the original packet. If validation fails, complete Task 4.1's exact restore and post-restore tree-hash check; otherwise leave this task unchecked with a blocker.

### 5.2 — append

> Reuse the exact Task 3.2 fixture, configured route, and bounds for every changed agent. A different prompt, model, variant, permission mode, or working directory invalidates before/after comparison unless explicitly recorded as Unverified.

### 5.3 — append

> Generate the report with one bounded command from immutable source artifacts. The verifier must compare stable identity sets and finding IDs, not headings or row counts alone.

### F.1 — append

> `metadata.status` remains `planned` before execution, becomes `in_progress` after the first completed executable task, and becomes `complete` only after Phase B. Record the Stage 3 result as completed pipeline evidence without changing the requested delivery path unless the orchestrator's canonical metadata convention counts conditional review stages in `pipeline_path`.

### F.2 — replace the diagnostic sentence with

> Parse both ledger tables with the canonical verifier and compare track ID, status, date, executable-task progress, and uniqueness as structured fields. Visual comparison is optional and is not evidence.

### F.3 — append

> Select and update validator alternation with a single atomic write/replace operation; run all dispatch-side shell calls through explicit bounds. Record prior `last_used`, selected validator, resulting `last_used`, model identity, and diversity comparison. A validator session must obey the DCP child guardrail and stop before 40 tool calls or 30K token growth.

### F.4 — append

> Select Stage 9 and post-doc artifacts by parsed UTC timestamp and schema, never filesystem enumeration order. Compare documentation changes to the pre-Stage-9 manifest and require either a bounded post-doc validation or a dated, reasoned waiver before final metadata completion.

## Unresolved blockers

| ID | Blocker | Owner / resolution |
|---|---|---|
| RR-B1 | Item-level skill and agent rubric contracts are not frozen. | Plan correction: Task 0.2 exact item IDs, applicability, and verifier failure rules. |
| RR-B2 | Ranking formula and weights are undefined. | Dave decision if no controlling approved weights exist; otherwise cite and embed the controlling contract. |
| RR-B3 | All authoritative verification commands are untested and unbounded. | Plan correction: bounded runner plus synthetic bootstrap gate; dry-run before Task 0.2 completes. |
| RR-B4 | Twenty skill and ten agent smoke tests lack exact invocation and runtime/session bounds. | Plan correction: disposable fixtures, exact `opencode run` envelope, per-case and total caps. |
| RR-B5 | Folder rollback cannot prove exact restoration and zero-target backup status is vacuous. | Plan correction: collision-proof mapping, exact target replacement, and post-restore tree-hash equality. |

## Execution recommendation

**Do not execute Stage 5.** The requested structural corrections are real and worthwhile, but the remaining gaps affect portfolio identity, review completeness, authority safety, and rollback integrity.

Because the single Stage 3 extra pass is now exhausted, pause the pipeline and ask Dave to choose one of two explicit courses:

1. **Recommended:** authorize one targeted manual plan correction implementing RR-B1 through RR-B5, then perform a lightweight command-only confirmation of the corrected snippets before execution.
2. Proceed with the current plan while explicitly accepting the five known blockers and the resulting confidence downgrade.

No skill or agent change should be made until that decision is recorded.
