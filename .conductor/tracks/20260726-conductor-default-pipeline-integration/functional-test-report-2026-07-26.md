# Conductor Default Pipeline Integration — Functional Smoke Test

Offline static simulation for the representative request: “Use conductor to create a new plan for a localized bookkeeping skill update. Do not execute the plan.” No track plan, skill, command, agent definition, configuration, source code, or external system was changed.

## Instructions followed

- Examined the active Conductor skill, Conductor Pipeline skill, canonical stage prompts, threshold policy, command, orchestrator, plan and metadata templates, and pipeline README named in the test request.
- The request invokes `conductor` for a new plan, so Conductor requires automatic composition of `conductor-pipeline` and the non-waivable opening sequence `Stage 0 -> Stage 1 -> Stage 2` (`conductor/SKILL.md`, Mandatory Composition with Conductor Pipeline).
- Stage 0 is the canonical baseline prompt: for bookkeeping it runs the closest deterministic structural/behavioral checks, writes `baseline-report-<timestamp>.md`, and records exactly `PASS`, `KNOWN-RED`, or `BLOCKED` (`conductor-pipeline/references/stage-prompts.md`, Stage 0). The pipeline and orchestrator also require this evidence to be persisted before deliverable edits.
- Stage 1 must receive the baseline and use the canonical `Stage 1 - Plan Creation (conductor-plan-creator)` prompt. That prompt requires metadata with baseline evidence, creator identity/model, track classification, test command, and recommended risk-adjusted pipeline fields.
- Stage 2 must use a reviewer identity and model different from Stage 1. The canonical Stage 2 prompt requires both comparisons to be recorded in metadata and the review report; inability to prove either is a Blocking finding. The default dispatch satisfies this: `conductor-plan-creator` / `openai/gpt-5.6-sol` / `low` versus `conductor-plan-reviewer` / `opencode-go/minimax-m3` / variant not configured. Independence verdict: PASS (different agent identity and exact model ID).
- Blocking Stage 2 findings must be resolved before execution. The review prompt permits confident corrections to the track, requires an `EXECUTION_READY` or `BLOCKED` verdict, and forbids execution readiness while any Blocking item remains.
- Because this is explicitly plan-only, the governing prompt, policy, command, orchestrator, and README all stop after Stage 2 and return the reviewed plan plus review report. Stages 5–9 must not execute in this run.
- The Stage 1 prompt still preserves the later risk-adjusted route in metadata. For this localized, non-production skill update, the expected recommendation is certain `bookkeeping`, `pipeline_path: 0 -> 1 -> 2 -> 5 -> 7 -> 9`, with later-stage skips/reasons recorded. If execution is later authorized, it retains Execute -> Validate -> Closeout; conditional re-review/re-validation remain governed by their thresholds rather than being discarded.
- Every dispatch must record the stage, exact agent, exact model ID, reasoning variant, default/substitution status, capability-floor verdict, and applicable independence verdict (`threshold-policy.md`, Capability Floor section). The exact-stage-prompt preflight repeats the agent/model/variant requirement for every handoff.

## Expected output produced

The simulated compliant plan-only run produces these Conductor artifacts under the active track, then stops:

- Baseline evidence artifact: `baseline-report-<YYYY-MM-DD-HHMMSS>.md`
- Creator identity/model: `conductor-plan-creator` / `openai/gpt-5.6-sol`
- Reviewer identity/model: `conductor-plan-reviewer` / `opencode-go/minimax-m3`
- Plan-only stop point: Stage 2
- Bookkeeping later-stage path: `0 -> 1 -> 2 -> 5 -> 7 -> 9`

- `baseline-report-<YYYY-MM-DD-HHMMSS>.md` containing command/check, working directory, exit code, relevant output, and `PASS`, `KNOWN-RED`, or `BLOCKED`.
- `spec.md`, `plan.md`, and `metadata.json` created by Stage 1 using the canonical prompt and the Conductor templates.
- `metadata.json` containing baseline fields, `plan_creator`, `plan_creator_model`, `plan_reviewer`, `plan_reviewer_model`, `review_status`, and the retained risk-adjusted `pipeline_mode`, `pipeline_path`, rationale, and skipped-stage reasons.
- `review-report-<YYYY-MM-DD-HHMMSS>.md` and `review-diff-summary-<YYYY-MM-DD-HHMMSS>.md` from Stage 2, with the creator/reviewer model-diversity result and an `EXECUTION_READY` verdict only after all Blocking findings are resolved.
- Return of the reviewed plan and review report only. No execution log, implementation edit, validation report, or documentation-closeout action is produced unless a later execution authorization is given.

## Forbidden actions avoided

- Did not execute the representative plan or dispatch any stage agent.
- Did not run external APIs, contact a provider, use credentials, or modify an external system.
- Did not modify global skills, commands, agent definitions, application configuration, source code, or track artifacts other than this required smoke-test report.
- Did not weaken the plan-only stop rule or silently skip Stage 0/Stage 2.

## Capability-floor test

Attempted substitution outcome:

| Candidate | Required result | Evidence |
|---|---|---|
| `openai/gpt-5.4-mini` | REJECT | Explicitly prohibited. |
| Any model ID containing `-mini` | REJECT | Explicitly prohibited. |
| Any model ID containing `-nano` | REJECT | Explicitly prohibited. |
| Economy or low-capability tier | REJECT | Explicitly prohibited. |
| No capable, independence-preserving substitute | STOP | The workflow must surface the limitation rather than downgrade or self-review. |

All 13 active `C:\Users\DaveWitkin\.config\opencode\agent\conductor-*.md` assignments were checked against the approved defaults/capability floor. Result: 13/13 COMPLIANT; none contains a prohibited `gpt-5.4-mini`, `-mini`, `-nano`, economy, or low-capability assignment. `low` on the approved Sol roles is a reasoning variant, not a low-capability model tier.

| Agent | Exact model | Variant | Floor result |
|---|---|---|---|
| conductor-doc-writer | opencode-go/deepseek-v4-flash | high | COMPLIANT |
| conductor-pipeline-orchestrator | openai/gpt-5.6-luna | high | COMPLIANT |
| conductor-plan-creator | openai/gpt-5.6-sol | low | COMPLIANT |
| conductor-plan-reviewer-alt | openai/gpt-5.6-sol | low | COMPLIANT |
| conductor-plan-reviewer | opencode-go/minimax-m3 | not configured | COMPLIANT |
| conductor-test-runner | openai/gpt-5.6-luna | high | COMPLIANT |
| conductor-test-writer | opencode-go/qwen3.7-plus | not configured | COMPLIANT |
| conductor-track-executor-glm51 | zai-coding-plan/glm-5.1 | high | COMPLIANT |
| conductor-track-executor-mimo2.5pro | opencode-go/mimo-v2.5-pro | high | COMPLIANT |
| conductor-track-executor | zai-coding-plan/glm-5.2 | high | COMPLIANT |
| conductor-track-validator-alt | openai/gpt-5.6-sol | low | COMPLIANT |
| conductor-track-validator-m3 | opencode-go/minimax-m3 | not configured | COMPLIANT |
| conductor-track-validator | openai/gpt-5.6-luna | high | COMPLIANT |

## Verdict

FUNCTIONAL_SMOKE_TEST_PASSED
