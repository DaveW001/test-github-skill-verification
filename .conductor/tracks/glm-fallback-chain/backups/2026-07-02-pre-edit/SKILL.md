---
name: conductor-pipeline
description: Six-stage Conductor pipeline orchestration protocol (plan -> review -> conditional re-review -> execute -> validate -> conditional re-validation) with model diversity, measurable gates, auditable handoffs, and failure/rollback. Use when running or building the /conductor-pipeline command and its stage subagents.
---

# Conductor Pipeline

Orchestrates a request from idea to validated result across six stages. Each stage runs on a **model-pinned subagent**. Hard diversity gates: the reviewer model is never the creator model, and the validator model is never the executor model. All output paths are fully qualified absolute Windows paths.

## Approved decisions (2026-06-28)
- Autonomy: **full-auto through validation** (no human checkpoint between stages). The execution-failure stop rule below still applies.
- Re-review trigger (Stage 3): **B+C hybrid**.
- Re-validation trigger (Stage 6): **A+C hybrid**.
- Layout: thin command + this skill reference pack.

## Scope Language

Conductor Pipeline work spans two distinct scopes that have different ownership and re-review triggers:

- **deliverable/application scope** - changes to the user's actual application, runtime code, or end-user deliverables. These edits are owned by the track's deliverable intent and re-trigger execution re-review when they change behavior.
- **pipeline bookkeeping scope** - changes to Conductor artifacts only (plan.md, metadata.json, tracks.md, tracks-ledger.md, execution logs, and repo-local .conductor/docs and .conductor/scripts). These edits are owned by the executor/validator bookkeeping workflow and do not re-trigger deliverable re-review.

Deliverable edits and bookkeeping edits have different ownership and re-review triggers: a stale bookkeeping entry is a minor closeout fix, not a deliverable regression.

## Model assignments (pinned per subagent)

| Stage | Subagent | Model | Variant |
|---|---|---|---|
| 1 Plan creation | conductor-plan-creator | openai/gpt-5.5 | low |
| 2 Plan review | conductor-plan-reviewer | opencode-go/minimax-m3 | - |
| 3 Conditional re-review | conductor-plan-reviewer-alt | openai/gpt-5.5 | low |
| 4 Execution | conductor-track-executor | zai-coding-plan/glm-5.2 | - |
| 5 Validation | conductor-track-validator | opencode-go/minimax-m3 | - |
| 6 Conditional re-validation | conductor-track-validator-alt | openai/gpt-5.5 | low |

Orchestrator (this pipeline's coordinator) runs on zai-coding-plan/glm-5.2 and is NOT a stage model.

Diversity checks to log at every gate: creator model != reviewer model; executor model != validator model. Re-review model must differ from the immediately preceding reviewer; re-validation model must differ from the executor.

## Stage flow

1. **Plan creation** - conductor-plan-creator writes spec.md + plan.md into `.conductor/tracks/<track-id>/`. Does not execute.
2. **Plan review** - conductor-plan-reviewer reviews spec/plan, applies confident improvements, surfaces uncertain ones. Writes `review-report-<ts>.md` and `review-diff-summary-<ts>.md`.
3. **Conditional re-review decision** - evaluate the B+C hybrid threshold (see references/threshold-policy.md). If triggered, conductor-plan-reviewer-alt runs one extra review pass. Cap: 1 extra pass, then pause for the user.
4. **Execution** - conductor-track-executor runs pending non-deferred plan items in order, checks off items, syncs metadata, writes `execution-log-<date>.md`.
5. **Validation** - conductor-track-validator validates closeout artifacts (plan/metadata/ledgers/logs) and writes `validation-report-<ts>.md` with a closeout verdict.
6. **Conditional re-validation decision** - evaluate the A+C hybrid threshold. If triggered, conductor-track-validator-alt runs one extra validation pass. Cap: 1 extra pass, then write `validation-blockers-<ts>.md` and pause for the user.

The exact standard prompt text for every stage lives in `references/stage-prompts.md`. The thresholds, iteration caps, and failure/rollback rules live in `references/threshold-policy.md`.

## Context handoff rule
Each subagent receives a self-contained prompt with absolute artifact paths and the exact stage prompt. Never assume a child session shares state. Pass full paths under `C:\development\opencode\.conductor\tracks\<track-id>\` (or the active workspace root).

## Failure / stop rule (applies even in full-auto)
- Stop immediately on unclear, destructive, or blocked tasks; do not guess.
- Model unavailable: log `model-unavailable` with the attempted model + stage, then use the documented fallback while preserving diversity.
- Execution failure: executor leaves incomplete tasks unchecked, updates the log, and stops. Orchestrator runs validation only if there is enough evidence.
- Validation finds major issues: route back to execution once; after one fix/re-validation loop, stop and ask the user.

## Autonomy note
Full-auto means no pause between stages. It does NOT remove the obligation to stop on the failure conditions above or to respect iteration caps.

## Related references

PowerShell edit hazards, including parse-check limitations, content-anchored edits, markdown indentation bleed, structural-character literal edits, and session-spanning date handling, live in references/powershell-edit-hazards.md. Mid-run authorization tiers live in references/threshold-policy.md#mid-run-authorization.

## Model fallback chain

Stage 4 execution uses a procedural fallback chain because OpenCode agents have one pinned `model:` and no native `fallbackModels` field.

| Tier | Subagent | Model |
|---|---|---|
| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` |
| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` |
| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` |

Retry transient failure signals (timeout/abort, HTTP 429/5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze) on the same tier up to two additional attempts, then escalate. Failure-signal examples include HTTP 429, HTTP 5xx, chunk timeout, and freeze; retry the same tier up to two additional attempts with brief backoff before escalating to the next tier. If Tier 3 fails, log `model-unavailable` and stop.

Diversity remains intact because each executor tier differs from validator `opencode-go/minimax-m3`.

Orchestrator limitation: the orchestrator itself remains pinned to `zai-coding-plan/glm-5.2` and cannot self-swap at runtime; provider timeouts fail fast, and recovery is to restart OpenCode, optionally after changing the orchestrator `model:` line to a fallback tier.

