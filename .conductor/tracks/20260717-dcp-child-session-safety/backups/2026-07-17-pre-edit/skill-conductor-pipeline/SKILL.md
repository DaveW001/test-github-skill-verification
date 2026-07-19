---
name: conductor-pipeline
description: Risk-adjusted Conductor pipeline orchestration protocol. Selects full, standard, bookkeeping, or emergency paths before execution, while preserving model diversity, measurable gates, auditable handoffs, and failure/rollback. Use when running or building the /conductor-pipeline command and its stage subagents.
---

# Conductor Pipeline

Orchestrates a request from idea to validated result using a **risk-adjusted pipeline**. The nine stages are the full catalog, not a mandatory path for every track. Before execution, the orchestrator performs a Pipeline Determination step and selects the smallest safe path: full, standard, bookkeeping, or emergency. Stages that run are delegated to **model-pinned subagents**. Hard diversity gates still apply whenever the corresponding stages run: the reviewer model is never the creator model, and the validator model is never the executor model. All output paths are fully qualified absolute Windows paths.

Templates and completion hygiene (track-spec/plan/metadata templates, Completion Gate, ledger conventions) live in the separate `conductor` skill; this skill orchestrates staged execution.

## Approved decisions (2026-06-28)
- Autonomy: **full-auto through validation** (no human checkpoint between stages). The execution-failure stop rule below still applies.
- Re-review trigger (Stage 3): **B+C hybrid**.
- Re-validation trigger (Stage 8): **A+C hybrid**.
- Layout: thin command + this skill reference pack.
- Pipeline selection: **risk-adjusted, not mechanically nine-stage**. The orchestrator must classify the track, record the selected `pipeline_mode`, explain skipped stages, and proceed automatically when low-risk criteria are met.

## Scope Language

Conductor Pipeline work spans two distinct scopes that have different ownership and re-review triggers:

- **deliverable/application scope** - changes to the user's actual application, runtime code, or end-user deliverables. These edits are owned by the track's deliverable intent and re-trigger execution re-review when they change behavior.
- **pipeline bookkeeping scope** - changes to Conductor artifacts only (plan.md, metadata.json, tracks.md, tracks-ledger.md, execution logs, and repo-local .conductor/docs and .conductor/scripts). These edits are owned by the executor/validator bookkeeping workflow and do not re-trigger deliverable re-review.

Deliverable edits and bookkeeping edits have different ownership and re-review triggers: a stale bookkeeping entry is a minor closeout fix, not a deliverable regression.

## Model assignments (pinned per subagent)

| Stage | Subagent | Model | Variant |
|---|---|---|---|
| 1 Plan creation | conductor-plan-creator | openai/gpt-5.6-sol | low |
| 2 Plan review | conductor-plan-reviewer | opencode-go/minimax-m3 | - |
| 3 Conditional re-review | conductor-plan-reviewer-alt | openai/gpt-5.6-sol | low |
| 4 Write tests (RED) | conductor-test-writer | opencode-go/qwen3.7-plus | - |
| 4b RED-state gate | orchestrator logic (not an agent) | - | runs suite; tests MUST fail |
| 5 Write code (GREEN) | conductor-track-executor | zai-coding-plan/glm-5.2 | high |
| 6 Run tests | conductor-test-runner | openai/gpt-5.6-luna | high |
| 7 Validation | conductor-track-validator / conductor-track-validator-m3 | openai/gpt-5.6-luna or opencode-go/minimax-m3 | high (Luna) or - (M3) |
| 8 Conditional re-validation | conductor-track-validator-alt | openai/gpt-5.6-sol | low |
| 9 Documentation | conductor-doc-writer | opencode-go/mimo-v2.5-pro | - |

Orchestrator (this pipeline's coordinator) runs on zai-coding-plan/glm-5.2 with variant high and is NOT a stage model.

Diversity log (log each at its gate):
- Test-writer (qwen3.7-plus) != planner (gpt-5.6-sol) and executor (glm-5.2). OK - stronger adversarial test design.
- Test-runner (openai Luna high) != executor (Mimo). OK - genuine cross-check.
- Doc-writer (Mimo) != executor (glm-5.2). OK - different models and families; doc-writer is a terminal closeout stage, not a review gate.
- Validator (Luna primary or M3 paired) != executor (Mimo): different families in both cases. OK. Persisted alternation rule selects between them.
- Re-review model must differ from the immediately preceding reviewer; re-validation model must differ from the executor.


### Deterministic validator alternation rule

Stage 7 validation uses one of two paired validator agents. Selection is a **persisted strict-alternation counter**, NOT a hash-parity rule (an earlier SHA-256 parity design was rejected because it could not guarantee an exact 50/50 split on any pair of consecutive tracks).

1. Read `last_used` from `<workspace-root>\.conductor\validator-alternation.json`.
2. If `last_used` is `tera`, dispatch `conductor-track-validator-m3` (opencode-go/minimax-m3) next.
3. If `last_used` is `m3`, dispatch `conductor-track-validator` (openai/gpt-5.6-luna, variant high) next.
4. After dispatch, flip `last_used` to the agent identity just used so the following run selects the other validator.

Each workspace root maintains its own `validator-alternation.json`. The orchestrator performs the read-select-flip atomically as part of Stage 7 dispatch; if the state file is missing, default to `conductor-track-validator` (Luna) and write `last_used=tera`.

This rule is:
- **Exact 50/50**: strict alternation guarantees exactly one Luna and one M3 validation across every two consecutive runs - not merely a statistical tendency.
- **Auditable**: the state file records the last validator used and the next expected identity.
- **Diversity-preserving**: both Luna (OpenAI family) and M3 (MiniMax family) differ from the executor (Mimo family), so executor/validator diversity is maintained on every run.

**Ongoing usage calculation (exact, per two consecutive validation runs):**
- Plan reviewer (Stage 2): always M3.
- Test runner (Stage 6): always Luna High.
- Validator (Stage 7): strictly alternating Luna / M3 - one of each per two runs.
- Combined checkpoints over a two-run cycle: 3 M3 + 3 Luna = exactly 50% each.
- Static agent count: 4 active agents (plan-reviewer M3, test-runner Luna, validator Luna, validator-m3 M3). Persisted alternation yields exactly 50/50.

No native weighted-routing field is used; selection is explicit orchestrator dispatch logic backed by a persistent counter.

## Pipeline Determination (mandatory pre-execution gate)

The orchestrator MUST perform and report a short **Pipeline Determination** before invoking execution stages. If Stage 1 creates or updates a track, the determination happens immediately after reading `metadata.json`; if the user points at an already-ready plan, the determination can happen before execution from the existing `spec.md`, `plan.md`, and `metadata.json`.

Record the decision in `metadata.json` when possible:

- `track_type`: `code` | `bookkeeping`
- `classification`: `certain` | `uncertain` (set to `uncertain` when track_type or risk cannot be confidently determined)
- `pipeline_mode`: `full` | `standard` | `bookkeeping` | `emergency`
- `pipeline_path`: ordered stage IDs/names that actually ran or will run
- `pipeline_rationale`: one or two sentences explaining why the selected path is sufficient
- `skipped_stages`: mapping/list of skipped stages with reasons

### Pipeline modes

| Mode | Default path | Use when | Notes |
|---|---|---|---|
| `full` | `1 -> 2 -> 3? -> 4 -> 4b -> 5 -> 6 -> 7 -> 8? -> 9` | Production code changes are meaningful or high-risk; tests must be authored; APIs/auth/storage/migrations/security/deployment/shared infrastructure are touched; acceptance criteria are ambiguous; failure cost is high; user explicitly asks for full pipeline. | This is the complete nine-stage/TDD path. Conditional stages 3 and 8 still obey thresholds. |
| `standard` | `1 -> 2 -> 5 -> 6 -> 7 -> 9` | Localized low/medium-risk code changes where existing tests are adequate and a separate RED test-writing stage is unnecessary or explicitly waived. | Skip stages 3/4/4b/8 unless thresholds/risk require them. If no usable tests exist, stop for user approval before degraded non-TDD execution. |
| `bookkeeping` | `1 -> 5 -> 7 -> 9` or, for an already-ready track, `5 -> 7 -> 9` | Markdown/config/skill/agent/process-only changes; no production-code files; `test_framework: none`; deterministic literal/schema/file-existence checks; no security/data-loss/deployment risk. | This is the normal abbreviated path: Execute -> Validate -> Closeout after a plan exists. Plan review and re-validation are skipped unless ambiguity, broad config risk, or validation failures justify them. |
| `emergency` | `triage -> minimal fix -> targeted test/check -> validation -> follow-up note` | Urgent restoration where speed matters and scope must stay minimal. | Requires explicit user urgency or incident context. Record follow-up hardening as deferred work. |

### Auto-select vs ask

Auto-select the abbreviated `bookkeeping` path when all are true: non-production/docs/config/bookkeeping scope; no application source files in scope; no executable test framework applies; checks are deterministic; and no security/data-loss/migration/deployment risk is present.

Ask for confirmation before abbreviating when any are true: production code changes; missing tests for behavior that should be tested; auth/storage/payments/deployment/secrets/scheduling/CI/shared infrastructure touched; user requested the full pipeline; or track classification is uncertain. When uncertain, prefer `full` or ask rather than silently downgrading.

### Required output snippet

Every run should include a visible determination like:

```markdown
## Pipeline Determination
Track type: bookkeeping
Production code changes: no
Test framework: none
Risk level: low
Selected pipeline_mode: bookkeeping
Selected path: Execute -> Validate -> Closeout
Skipped stages:
- Plan Review: skipped because plan is explicit and low-risk.
- RED/Test Writing: skipped because no executable behavior changes.
- Test Runner: skipped because no test suite applies.
- Re-Validation: skipped because validation is deterministic literal checks.
```

## Track-type discriminator (stage branching)

Stages 4 / 4b / 6 run ONLY for `code`-type tracks and only when the selected `pipeline_mode` requires TDD or test execution. `bookkeeping` tracks (skills, docs, config, agent config) normally select `pipeline_mode: bookkeeping` and take the abbreviated path **1 -> 5(executor) -> 7 -> 9**; if a plan already exists and is ready, the visible operational path is **5(executor) -> 7 -> 9** (Execute -> Validate -> Closeout). The plan-creator declares `track_type` (`code` | `bookkeeping`) plus a recommended `pipeline_mode` in `metadata.json`. **Classification-uncertainty rule:** if the plan-creator cannot confidently determine `track_type` or risk level, it must NOT default to `bookkeeping`. Instead it sets `classification: uncertain` in metadata.json, and the orchestrator either asks the user for confirmation or selects `full` to avoid silently downgrading a potentially risky track. Stage 9 (documentation/closeout or waiver) runs for all modes unless explicitly waived with rationale.

### RED-state gate (Stage 4b)
After Stage 4 writes tests, the orchestrator runs `test_command` once and verifies **valid RED-state**: newly-written acceptance tests fail for expected behavioral/assertion reasons mapped to spec acceptance criteria. A nonzero exit caused by syntax errors, missing dependencies, test harness setup failures, unrelated pre-existing failures, or invalid test placement is **not** valid RED and must be routed back to Stage 4 once (cap 1). If tests PASS immediately (premature green - tests assert existing behavior), reopen Stage 4 once (cap 1). If valid RED is still not demonstrated after the cap, stop and surface to the user; do not proceed silently. Only valid RED may proceed to Stage 5 (GREEN).

### Test-runner retry cap
When Stage 6 (test-runner) reports failures after implementation, route back to Stage 5 (executor) **once**, with the test-runner's failure report as input, then re-run Stage 6. If still failing after one retry loop, stop and surface to the user (mirrors the validation "route back once, then stop" rule).

## Stage flow

The list below is the full stage catalog. Do not run every stage mechanically. Use Pipeline Determination to choose `full`, `standard`, `bookkeeping`, or `emergency`, then run only the selected path while recording skipped-stage rationales. Stages 4 / 4b / 6 (TDD cluster) run only for code-type paths that require them. `bookkeeping` tracks normally skip 2/3/4/4b/6/8 and take 1 -> 5(executor) -> 7 -> 9 (or 5 -> 7 -> 9 when a reviewed plan already exists).

1. **Plan creation** - conductor-plan-creator writes spec.md + plan.md into `.conductor/tracks/<track-id>/` (declaring `track_type`, `classification`, recommended `pipeline_mode`, `pipeline_path`, `pipeline_rationale`, and skipped-stage candidates in metadata.json). Does not execute.
2. **Plan review** - conductor-plan-reviewer reviews spec/plan, applies confident improvements, surfaces uncertain ones. Writes `review-report-<ts>.md` and `review-diff-summary-<ts>.md`.
3. **Conditional re-review decision** - evaluate the B+C hybrid threshold (see references/threshold-policy.md). If triggered, conductor-plan-reviewer-alt runs one extra review pass. Cap: 1 extra pass, then pause for the user.
4. **Write tests (RED)** [code-type only] - conductor-test-writer writes failing tests from the spec acceptance criteria into the repo; emits a RED-state report.
4b. **RED-state gate** [code-type only] - orchestrator runs `test_command` and confirms the suite is RED (failing). On premature green, reopen Stage 4 once (cap 1).
5. **Write code (GREEN)** - conductor-track-executor writes the minimum implementation to make the tests pass (GREEN); for bookkeeping tracks, executes plan items directly. Writes `execution-log-<date>.md`.
6. **Run tests** [code-type only] - conductor-test-runner runs `test_command` and emits `test-run-report-<ts>.md` (per-test pass/fail). On failure, route back to Stage 5 once, then stop.
7. **Validation** - conductor-track-validator validates closeout artifacts (plan/metadata/ledgers/logs) and writes `validation-report-<ts>.md` with a closeout verdict.
8. **Conditional re-validation decision** - evaluate the A+C hybrid threshold. If triggered, conductor-track-validator-alt runs one extra validation pass. Cap: 1 extra pass, then write `validation-blockers-<ts>.md` and pause for the user.
9. **Documentation** - conductor-doc-writer updates README/API docs/changelog/ADRs and emits `doc-update-log-<ts>.md`.

The exact standard prompt text for every stage lives in `references/stage-prompts.md`. The thresholds, iteration caps, and failure/rollback rules live in `references/threshold-policy.md`.

## Terminal closeout gate (two-phase, respects stage ordering)

Closeout verification is split into two phases because Stage 7 runs **before** Stage 9. The validator must not be required to check a Stage 9 artifact that has not been created yet.

### Phase A - Stage 7/8 validator: closeout-readiness verdict
The validator (Stage 7, or Stage 8 if triggered) verifies **execution correctness and Stage 9 readiness** and issues a closeout-readiness verdict. It checks:

1. All non-deferred plan tasks are `[x]`; ordering/dependencies respected.
2. `metadata.json` status/stage/progress and `pipeline_mode`/`pipeline_path` reflect the actually executed path (including skipped stages for abbreviated tracks).
3. `.conductor\tracks.md` has exactly one up-to-date row for the track.
4. `tracks-ledger.md` (when the repo uses one) has one canonical up-to-date row.
5. Execution/change logs exist and record deviations, skipped items, and validation performed.
6. Every claimed artifact exists with required acceptance strings.
7. **Stage 9 readiness**: documentation can run without changing public contract/setup semantics, or a post-doc validation requirement is flagged.
8. Required follow-ups are created or explicitly deferred with a recorded reason.

If any Phase A item fails, the validator routes back once for reconciliation, then stops and writes `validation-blockers-<ts>.md` if still unresolved.

### Phase B - Orchestrator: terminal closeout confirmation (after Stage 9)
After Stage 9 (documentation or explicit waiver) runs, the **orchestrator** (not the Stage 7 validator) performs terminal closeout confirmation:

1. **Stage 9 artifact or waiver** - Stage 9 has emitted `doc-update-log-<timestamp>.md`, OR the execution log records a documented skip/waiver.
2. **Post-doc validation** - if Stage 9 made semantic/contract-affecting edits, a `post-doc-validation-<timestamp>.md` artifact exists or a recorded waiver is in place.
3. **metadata.json final sync** - `status` reflects final closeout state.

If any Phase B item is missing, the orchestrator routes back to Stage 9 once, then stops and surfaces to the user. Missing terminal closeout evidence is a **terminal closeout blocker**.

See `references/threshold-policy.md` (Terminal closeout gate) and `references/stage-prompts.md` (Stage 7/8 validation).

## Workspace-root convention

Throughout this skill, <workspace-root> refers to the active git repository root that contains the .conductor/ directory. The orchestrator MUST substitute <workspace-root> with the actual absolute path (e.g., C:\development\opencode or C:\development\pptx-pipeline) when assembling stage prompts for subagents. Subagents receive the substituted path; they never see the literal placeholder.

## Context handoff rule
Each subagent receives a self-contained prompt with absolute artifact paths and the exact stage prompt. Never assume a child session shares state. Pass full paths under `<workspace-root>\.conductor\tracks\<track-id>\` (or the active workspace root).

## Failure / stop rule (applies even in full-auto)
- Stop immediately on unclear, destructive, or blocked tasks; do not guess.
- Model unavailable: log `model-unavailable` with the attempted model + stage, then use the documented fallback while preserving diversity.
- Execution failure: executor leaves incomplete tasks unchecked, updates the log, and stops. Orchestrator runs validation only if there is enough evidence.
- Validation finds major issues: route back to execution once; after one fix/re-validation loop, stop and ask the user.

## Autonomy note
Full-auto means no pause between stages. It does NOT remove the obligation to stop on the failure conditions above or to respect iteration caps.

## Related references

PowerShell edit hazards, including parse-check limitations, content-anchored edits, markdown indentation bleed, structural-character literal edits, and session-spanning date handling, live in references/powershell-edit-hazards.md. Mid-run authorization tiers live in references/threshold-policy.md#mid-run-authorization.
Anomaly logging taxonomy, JSONL schema, FIFO-archive rotation, all-stages-append rule, and closeout summary generation live in references/anomaly-logging.md.

## Model fallback chain

Stage 5 execution uses a procedural fallback chain because OpenCode agents have one pinned `model:` and no native `fallbackModels` field.

| Tier | Subagent | Model |
|---|---|---|
| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` (variant `high`) |
| 2 | `conductor-track-executor-glm51` | `opencode-go/mimo-v2.5-pro` |
| 3 | `conductor-track-executor-mimo2.5pro` | `opencode-go/mimo-v2.5-pro` |

Retry transient failure signals (timeout/abort, HTTP 429/5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze) on the same tier up to two additional attempts, then escalate. Failure-signal examples include HTTP 429, HTTP 5xx, chunk timeout, and freeze; retry the same tier up to two additional attempts with brief backoff before escalating to the next tier. If Tier 3 fails, log `model-unavailable` and stop.

Diversity remains intact because the executor tiers (GLM 5.2 and Mimo) differ from both validator options (Luna/OpenAI and M3/MiniMax).

GLM-5.2 thinking-mode default: Z.AI `glm-5.2` is pinned to variant `high` for the orchestrator and primary executor. Use variant `max` only as an explicit operator override for rare edge cases where `high` has failed or deeper scrutiny is worth the quota cost.

**Operational note (2026-07-15):** GLM-5.2 quota exhausted. While GLM-5.2 is unavailable, Stage 5 execution uses the two Mimo fallback tiers. The canonical three-tier chain `zai-coding-plan/glm-5.2` -> `opencode-go/mimo-v2.5-pro` -> `opencode-go/mimo-v2.5-pro` remains unchanged; only the operational starting tier is shifted. Planning and deterministic validation do not require GLM-5.2.

Orchestrator limitation: the orchestrator itself remains pinned to `zai-coding-plan/glm-5.2` (variant `high`) and cannot self-swap at runtime; provider timeouts fail fast, and recovery is to restart OpenCode, optionally after changing the orchestrator `model:` line to a fallback tier.

### Failure detection scope (what the chain does/does not catch)

- Catches: model/provider stalls - provider `chunkTimeout` (2 min) / `headerTimeout` (1 min) / `timeout` (10 min) on `zai-coding-plan` and `opencode-go` abort a frozen/overloaded/unreachable model request and surface it as an error; the executor then reports `model-unavailable` and the orchestrator retries/escalates.
- Does NOT catch: a subagent stalled on a non-model operation (a bash/tool call blocking indefinitely, a hung MCP tool). OpenCode has no per-agent execution timeout and the Task tool has no `timeout`, so there is no orchestrator-level watchdog on a child. In that case the run hangs until a human stops it.
- Mitigation (child-side self-bounding, ALL stages): every stage subagent - executor AND non-executor stages (plan-creator, reviewers, validator) - MUST keep commands bounded (explicit `timeout`/`-TimeoutSec` on every shell/network call, non-interactive flags like `--yes`), avoid commands that can block indefinitely (Read-Host, uncapped network calls, Wait-Process/-Wait, tail -f, Start-Process -Wait, servers), and report back promptly on a blocker instead of hanging. This discipline is propagated via the stage-prompts Tool preflight (added 2026-07-03) and is NOT limited to the executor: a stall can occur at any stage (incident: a Stage 1 plan-creator stalled with no anti-stall guard). A tool-side hang then self-aborts inside the child instead of stalling the pipeline.
- Recommended platform fix (not yet available): a per-agent execution timeout that aborts the Task call after N idle minutes. See `references/threshold-policy.md` (Failure detection scope & limitations) for the full analysis.




