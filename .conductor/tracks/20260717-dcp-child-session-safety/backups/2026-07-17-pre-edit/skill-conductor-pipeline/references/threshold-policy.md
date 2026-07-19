# Threshold Policy (Conductor Pipeline)

# Pipeline Selection Policy (added 2026-07-06)

The Conductor pipeline is risk-adjusted. The full nine-stage path is available, but it is not mandatory for every track. Before execution, the orchestrator records a Pipeline Determination and selects one of four modes:

- `full`: high-risk or meaningful production-code/TDD path, `1 -> 2 -> 3? -> 4 -> 4b -> 5 -> 6 -> 7 -> 8? -> 9`.
- `standard`: localized code path with adequate existing tests, `1 -> 2 -> 5 -> 6 -> 7 -> 9`.
- `bookkeeping`: markdown/config/skill/agent/process-only path, `1 -> 5 -> 7 -> 9` or `5 -> 7 -> 9` for an already-ready plan.
- `emergency`: urgent restoration path, `triage -> minimal fix -> targeted test/check -> validation -> follow-up note`.

Auto-select `bookkeeping` only when all are true: no production-code changes, no application source files in scope, no executable test framework applies, deterministic literal/schema/file checks are sufficient, and no security/data-loss/migration/deployment risk exists.

Ask before abbreviating if any are true: production code changes, behavior lacks tests that should exist, auth/storage/payments/deployment/secrets/scheduling/CI/shared infrastructure is touched, user requested full pipeline, or classification is uncertain. When uncertainty remains, prefer `full` or ask rather than silently downgrading.

Skipped stages are intentional only when the determination records a reason. Missing `pipeline_mode`, `pipeline_path`, or skipped-stage rationale is a bookkeeping validation issue.

Approved thresholds, diversity rules, iteration caps, and failure/rollback behavior. Decisions recorded 2026-06-28.

## Stage 3 re-review trigger - B+C hybrid
**Mode scope:** Stage 3 applies only when the selected `pipeline_mode` includes Stage 2 (plan review) - i.e. `full` or `standard` modes, or when a `bookkeeping`/`emergency` track has re-enabled review due to ambiguity or broad risk. If Stage 2 was skipped, Stage 3 does not apply.
Run ONE additional re-review (conductor-plan-reviewer-alt) when ANY of these is true:
- Structural change is large: acceptance-criteria count changed by >=2, OR phase count changed, OR task count changed by >=20%, OR
- Readiness score < 90%, OR
- Any task rated Blocking remains unresolved.

Else skip re-review.

## Stage 8 re-validation trigger - A+C hybrid
**Mode scope:** Stage 8 applies only when the selected `pipeline_mode` includes Stage 7 (validation) and validation/fix evidence materially requires a second pass. For `bookkeeping` tracks where Stage 7 produced a clean deterministic verdict and no fixes were needed, Stage 8 does not apply.
Run ONE additional re-validation (conductor-track-validator-alt) after fixes when ANY of these is true:
- Closeout verdict is "Not ready to close", OR a required fix touches production files, OR
- Any acceptance criterion is unmet, OR
- metadata.json progress differs from actual checklist completion by > 5 percentage points.

Else skip re-validation.

Metadata/checklist comparison rule:
- Compare `metadata.json` task progress to the plan's executable task checkboxes, not to separate readiness or quality checklist items unless metadata explicitly counts those items.
- If a plan contains both executable tasks and readiness/quality checkboxes, validators should report both counts separately (for example, `29/29 tasks` and `8/8 readiness checks`) and explain the mapping.
- A mismatch is material only when metadata claims a task-progress state that the executable task checklist does not support.

## Metadata schema guidance

Use distinct metadata fields when a plan mixes executable tasks with readiness or quality checklists:

- `task_count` - count executable implementation task checkboxes only.
- `readiness_check_count` - count readiness, quality, or handover checklist items that are not executable implementation tasks.
- `total_checkbox_count` - count all markdown checkboxes in the plan; this should equal `task_count + readiness_check_count` when those are the only checkbox categories.
- `completed_tasks` - map this value to completed executable tasks out of `task_count`, not to `total_checkbox_count`.

Validators must not compare `completed_tasks` to readiness or quality checklist counts unless metadata explicitly defines a separate completed-readiness field. Report separate units such as `29/29 executable tasks`, `8/8 readiness checks`, and `37/37 total checkboxes`.

## Diversity rules (log each at the gate)
- Stage 2 reviewer model != Stage 1 creator model.
- Stage 7 validator model != Stage 5 executor model.
- Stage 3 re-review model != immediately preceding reviewer model; and must not equal the creator model if Stage 2 fell back to the creator model.
- Stage 8 re-validation model != Stage 5 execution model; preferably != Stage 7 validation model.

Default route (all resolve in `opencode models`):
- Creation/Re-review/Re-validation: openai/gpt-5.6-sol (variant low)
- Review/Validation: opencode-go/minimax-m3
- Execution: zai-coding-plan/glm-5.2 (variant high)

## Iteration caps
- Conditional re-review: max 1 extra pass. After cap: pause, ask user to approve manual plan correction or proceed with known risks.
- Conditional re-validation: max 1 extra pass after fixes. After cap: write validation-blockers-<ts>.md and ask user whether to run another execution/fix cycle.

Advanced flag (future): /conductor-pipeline --max-review-passes N --max-validation-passes N. Defaults stay conservative.

## Failure / rollback paths
Model unavailable:
1. Orchestrator logs model-unavailable with attempted model ID + stage.
2. Select fallback from the model table while preserving diversity rules.
3. If no fallback preserves diversity, pause and ask user to allow same-provider-different-variant, same-family-different-account, or stop.

Plan creation/review fails:
1. Do not proceed to execution.
2. Save partial artifacts.
3. Produce a plain-language question with exact missing context.

Execution fails mid-way:
1. Executor stops on unclear/destructive/blocked tasks.
2. Update plan.md only for completed tasks; leave incomplete tasks unchecked.
3. Write execution-log-<date>.md with completed tasks, failed command/tool call, files changed before failure, suggested rollback/resume point.
4. Orchestrator runs validation only if there is enough evidence; otherwise pauses.
5. Rollback: prefer OpenCode /undo or snapshots when failure is in the same session; use Git only as inspection unless user approves reset/revert; never auto-delete untracked files without confirmation.

Validation finds major issues:
1. Classify the issue before routing:
   - Bookkeeping-only stale artifacts: orchestrator may fix bookkeeping directly, then run Stage 8 if A+C is met or the evidence changed materially.
   - Deliverable/code/test fixes: route back to Stage 5 once with the validator report as input; for code tracks rerun Stage 6 before Stage 7/8.
   - Plan/spec flaw: route back to Stage 2/3 review rather than forcing execution to guess.
2. After one fix/re-validation loop, stop and ask user before more cycles.
3. If still blocked, write validation-blockers-<ts>.md.

## Artifact names (per track)
- review-report-<YYYY-MM-DD-HHMMSS>.md
- review-diff-summary-<YYYY-MM-DD-HHMMSS>.md
- execution-log-<YYYY-MM-DD>.md
- validation-report-<YYYY-MM-DD-HHMMSS>.md
- validation-blockers-<YYYY-MM-DD-HHMMSS>.md (only when blocked)
- red-gate-report-<YYYY-MM-DD-HHMMSS>.md or equivalent RED-state evidence (code tracks)
- test-run-report-<YYYY-MM-DD-HHMMSS>.md (code tracks, Stage 6)
- doc-update-log-<YYYY-MM-DD-HHMMSS>.md (Stage 9)
- red-gate-report-<YYYY-MM-DD-HHMMSS>.md or equivalent RED-state evidence (code tracks)
- test-run-report-<YYYY-MM-DD-HHMMSS>.md (code tracks, Stage 6)
- doc-update-log-<YYYY-MM-DD-HHMMSS>.md (Stage 9)
- issues-and-deviations-<YYYY-MM-DD>.md (optional; use when non-blocking process lessons, tool workarounds, or reviewer/executor deviations are substantial enough that burying them in the execution log would reduce reuse)
- audit-correction-<YYYY-MM-DD-HHMMSS>.md (validator/executor; corrects an after-the-fact audit-trail mismatch such as a log reporting a clean check that validation found failing)

The optional issues/deviations artifact is not required for clean runs. It is an observability aid, not a closeout blocker, unless a separate stop rule requires a blocker artifact such as `validation-blockers-<YYYY-MM-DD-HHMMSS>.md`. Significant audit-trail mismatches recorded in an `audit-correction-<YYYY-MM-DD-HHMMSS>.md` must also be appended to `<workspace-root>\.conductor\logs\pipeline-anomalies.jsonl` (see `references/anomaly-logging.md`).

## Autonomy
Full-auto through validation (approved). No human checkpoint between stages. The stop rules above and iteration caps still apply.

## Mid-Run Authorization

Conductor execution is full-auto through validation, but executors still encounter small, well-justified deviations mid-run (a clearly-correct fix that unblocks the goal, a slight wording ambiguity, a format question). Rather than stopping the human for every micro-decision, executors classify the deviation into a tier and act accordingly. The default is to proceed with documented reasoning.

### Tier 0 (default) - Proceed with documented reasoning

For low-risk, well-justified deviations with a clear root cause and low blast radius (typical for doc, skill, and reference work): apply the fix, document the reasoning in the execution log, and continue. Do NOT stop the human for this class.

Examples of Tier 0: correcting a single literal in a verification snippet, fixing an indentation bleed, choosing between two equivalent phrasings, normalizing line endings to match the target file, or capturing the run date once instead of recomputing it.

### Tier 1 - Stop and surface

Only for genuinely high-stakes, irreversible, destructive, or ambiguous decisions with no clear recommended path: stop and surface to the human before proceeding. Examples: deleting data, changing scheduler cadence, modifying alert routing, anything touching secrets, or any edit whose blast radius you cannot bound.

Tier-1 stop handoff format: when stopping, emit (1) the track id and current task id, (2) the exact deviation encountered, (3) the options you considered and their blast radius, (4) your recommended option with reasoning, and (5) the precise decision you need from the human. Do not silently guess; do not proceed until the human authorizes.
### Tier 2 - Rare human checkpoint

Reserved for decisions that are both high-stakes and structurally irreversible (e.g., force-pushing shared history, dropping a production table). These almost never occur in pipeline bookkeeping or doc/skill/reference tracks. When they do, stop and escalate exactly as Tier 1, but flag the irreversibility explicitly.

### Effect on Stage 8 (A+C re-validation)

An authorized Tier-0 or Tier-1 fix that touches production files counts toward the Stage 8 A+C re-validation threshold. Bookkeeping-only edits (plan.md, metadata.json, ledgers, logs) do not. When in doubt about whether an edit is deliverable/application scope vs pipeline bookkeeping scope, treat it as deliverable scope and count it.

### Resume vs restart

After an authorized mid-run edit or a stop/resume, prefer to resume by task id rather than restarting the plan from Phase 0. Check off only the tasks actually completed; leave incomplete tasks unchecked. Record the resume point and any state carried over (captured run date, baseline artifacts, partial outputs) in the execution log so a fresh session can continue deterministically.

### Arbitrator extension hook (reserved)

A future `conductor-arbitrator` subagent may be inserted between Tier 0 and Tier 1. It would adjudicate borderline deviations automatically. This is a reserved extension point only; do not build the arbitrator in this track. The current model is: executor decides tier, documents reasoning, and stops only at Tier 1 or above.

### Canonical lesson

The `kg-run-job.ps1:138` regex fix on 2026-06-29 should have been Tier 0. It was a clearly-correct, low-blast-radius fix that unblocked the goal, yet execution paused for authorization. Capture that class of decision as Tier 0 to keep full-auto throughput.

## Model fallback chain

| Tier | Stage 5 executor subagent | Model | Use |
|---|---|---|---|
| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` (variant `high`) | Primary GLM-5.2 executor via Z.AI; `max` is opt-in only |
| 2 | `conductor-track-executor-glm51` | `opencode-go/mimo-v2.5-pro` | First Mimo fallback via OpenCode Go |
| 3 | `conductor-track-executor-mimo2.5pro` | `opencode-go/mimo-v2.5-pro` | Last-resort Mimo fallback via OpenCode Go |

Transient failure signals: timeout/abort, HTTP 429, HTTP 5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze, or stream stall.

Retry policy: retry the same tier up to two additional attempts with brief backoff, then escalate to the next tier. If Tier 3 fails, log `model-unavailable` with attempted model, stage, tier, and failure signal, then stop and ask the user.

Diversity note: executor fallback preserves validation diversity because `zai-coding-plan/glm-5.2` (variant `high`) and `opencode-go/mimo-v2.5-pro` differ from validator `openai/gpt-5.6-luna` (variant `high`) and `opencode-go/minimax-m3`.

Orchestrator self-swap limitation: the orchestrator is pinned to `zai-coding-plan/glm-5.2` (variant `high`) and cannot self-swap at runtime. Provider timeouts prevent indefinite hangs; if the orchestrator's own model is unavailable, restart OpenCode after the failure is surfaced, optionally after changing the orchestrator `model:` line to a fallback tier so configuration is re-read on startup.

## Failure detection scope & limitations (added 2026-07-02)

The fallback chain catches model/provider-level failures but cannot, by itself, catch every way a subagent can stall. Record the scope honestly so operators know what is and is not protected.

### Two timer layers

| Layer | What it bounds | Mechanism | Bounded? |
|---|---|---|---|
| Provider HTTP layer | One model<->provider request | `options.timeout` (600000 ms total), `options.headerTimeout` (60000 ms to first header), `options.chunkTimeout` (120000 ms max gap between streamed chunks) on `zai-coding-plan` and `opencode-go` in opencode.jsonc | Yes |
| Task-tool / subagent layer | An entire subagent invocation (many model turns + tool calls) | none - OpenCode provides no per-agent execution timeout, and the Task tool exposes no `timeout` parameter | No |

### What the chain DOES catch

- A frozen/overloaded provider that stops streaming tokens: `chunkTimeout` (2 min) aborts the model request inside the subagent and turns the silent freeze into an explicit error. Previously this hung forever.
- Total request overrun: `timeout` (10 min) caps any single model request.
- No headers / unreachable provider: `headerTimeout` (1 min) aborts fast.
- HTTP 429/5xx, connection refused, empty response: surfaced as errors.
- When the error surfaces, the executor reports `model-unavailable` and the orchestrator applies the retry/escalation routing (same tier x2, then next tier, then stop).

So for the dominant real-world GLM failure (provider freeze/overload), detection is ~2 min and recovery is automatic tier escalation.

### What the chain does NOT catch (the gap)

- A subagent that stalls on a NON-model operation: a bash/tool call that blocks indefinitely with no timeout, a hung MCP tool, `Read-Host`/`-Wait`/`tail -f`, or any command the provider timeouts never reach.
- In that case there is NO orchestrator-level watchdog. The orchestrator's Task-tool call blocks indefinitely until a human stops the run. The fallback chain does NOT engage, because it is triggered by the subagent's RETURNED message, and no message returns.

Why: OpenCode has no per-agent execution-timeout primitive. Provider `timeout`/`chunkTimeout` are the only timers available, and they reach only the model HTTP layer - not the agentic loop or tool calls inside the child. This cannot be closed from configuration alone.

### Mitigations

1. Tool-call self-bounding in EVERY stage subagent (executor applied 2026-07-02; broadened to all stages 2026-07-03): every agent body and every stage handoff prompt require shell/network calls to ALWAYS carry an explicit `timeout`, forbid commands that can block indefinitely, and instruct the subagent to report back promptly on a blocker. This removes the most common non-model stall trigger: a tool-side hang now self-aborts inside the child and surfaces as a failed tool call instead of hanging the pipeline. The 2026-07-03 broadening closes the non-executor gap: a Stage 1 plan-creator stall (no anti-stall guard) had previously hung the pipeline because only the executor carried this discipline.
2. Provider timers (already in place): `chunkTimeout`/`headerTimeout`/`timeout` bound model-side stalls.
3. Operational fallback: if an orchestrator run goes silent past ~6-8 min (beyond normal long-turn headroom), treat it as a stuck child, stop manually, and re-run. A single frozen model call should surface within ~2 min via chunkTimeout, so longer silence likely indicates a non-model stall.

### Recommended platform fix (not yet available)

A per-agent execution timeout that aborts the Task-tool call after N minutes with no progress. This is the single biggest remaining hole. Until OpenCode exposes it, the child-side self-bounding (mitigation 1) is the practical defense.

### Decision log
- 2026-07-01: adopted provider timeouts + procedural 3-tier fallback chain.
- 2026-07-02: added executor tool-call self-bounding to close the most common non-model-stall path; documented the residual gap (no orchestrator-level child watchdog) and the platform feature needed to fully close it.
- 2026-07-03: generalized tool-call self-bounding + anti-stall discipline from the executor to ALL stage subagents (plan-creator, reviewers, validator) via a new stage-prompts Tool-preflight bullet; trigger was a real Stage 1 plan-creator stall that hung the pipeline. Residual gap (no per-agent execution timeout in OpenCode) remains.

## TDD stage gates (added 2026-07-05)

Applies only to `code`-type tracks (bookkeeping tracks skip stages 4/4b/6).

### test-runner retry cap (Stage 6 -> Stage 5)
When Stage 6 (test-runner) reports failures after implementation, route back to Stage 5 (executor) once with the test-runner failure report as input, then re-run Stage 6. If still failing after one retry loop, stop and surface to the user (mirrors the validation "route back once, then stop" rule). Cap: 1 retry.

### Doc-writer re-validation scope (Stage 9)
Stage 9 (doc-writer) edits to README, API docs, changelog, and ADRs are bookkeeping-scope for re-validation purposes UNLESS they change user-facing behavior. Pure documentation sync (renamed headings, added examples, changelog entries) does not re-trigger deliverable-scope re-validation; a doc edit that alters a documented public contract or setup step DOES count as deliverable scope.

### RED-state gate (Stage 4b)
Before Stage 5 (executor / GREEN) runs, the orchestrator verifies **valid RED-state**: newly-written acceptance tests fail for expected behavioral/assertion reasons and map to spec acceptance criteria. A nonzero exit caused by syntax errors, missing dependencies, invalid test setup, unrelated existing failures, or malformed generated tests is NOT valid RED. Invalid RED or premature green routes back to Stage 4 once (cap 1). If valid RED is still not demonstrated after the cap, stop and surface to the user; stop instead of continuing.

### test-runner retry cap (Stage 6 -> Stage 5)
When Stage 6 (test-runner) reports failures after implementation, route back to Stage 5 (executor) once with the test-runner failure report as input, then re-run Stage 6. If still failing after one retry loop, stop and surface to the user (mirrors the validation "route back once, then stop" rule). Cap: 1 retry.

### Code track without a test framework
If `track_type=code` and `test_framework`/`test_command` are `none`, `n/a`, missing, or unusable, stop before Stage 4 unless the user explicitly approves one of these policies: scaffold a test harness, stop for user decision, or run a degraded non-TDD path with a documented confidence downgrade. Do not fabricate weak tests.

### Doc-writer re-validation scope (Stage 9)
Stage 9 (doc-writer) edits to README, API docs, changelog, and ADRs are bookkeeping-scope for re-validation purposes UNLESS they change public contract, setup steps, CLI/API behavior, or other user-facing semantics. Pure documentation sync (renamed headings, examples, changelog entries) can close without full re-validation; semantic doc changes require a lightweight post-doc validation/doc-diff review before final closeout.

## Terminal closeout gate (two-phase, added 2026-07-06, reordered 2026-07-06)

Closeout verification is split into two phases because Stage 7 runs **before** Stage 9.

### Phase A - Stage 7/8 validator: closeout-readiness verdict
The validator verifies execution correctness and Stage 9 readiness (all plan tasks [x], metadata/pipeline_mode/pipeline_path match executed path, tracks.md/ledger up to date, logs exist, Stage 9 readiness assessed, follow-ups dispositioned). It does NOT check for a Stage 9 artifact. If any Phase A item fails, route back once for reconciliation, then stop and write `validation-blockers-<ts>.md`.

### Phase B - Orchestrator: terminal closeout confirmation (after Stage 9)
After Stage 9 (documentation or waiver) runs, the orchestrator confirms:
- Stage 9 emitted `doc-update-log-<timestamp>.md` OR a documented skip/waiver exists;
- post-doc validation artifact or waiver exists (if Stage 9 made semantic/contract-affecting edits);
- `metadata.json` final status reflects closeout state.

Missing terminal closeout evidence is a **terminal closeout blocker** - the run does NOT succeed-with-notes. If any Phase B item is missing, route back to Stage 9 once, then stop and surface to the user. See `SKILL.md` (Terminal closeout gate) and `stage-prompts.md` Stage 7/8.

## Post-doc validation policy (added 2026-07-06)

Stage 9 documentation edits that are semantic/contract-affecting (public API, setup requirements, user-facing behavior) require orchestrator post-doc validation before the track may close. Non-contractual sync edits (typo fixes, reflow, internal cross-references) and docs-only bookkeeping tracks with no public API surface may close with an explicit post-doc validation waiver instead.

Requirements:
- A completed `post-doc-validation-<timestamp>.md` artifact, OR
- A recorded post-doc validation waiver (marked WAIVED) in `post-doc-validation-<timestamp>.md` or the execution log, with a dated reason.

A track that has neither a completed post-doc validation artifact nor a recorded waiver is a terminal closeout blocker.
