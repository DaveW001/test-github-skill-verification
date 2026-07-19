# Conductor Pipeline

A risk-adjusted OpenCode-native workflow that moves a request from idea to validated result with model diversity and auditable handoffs. The full nine-stage/TDD sequence is available, but the orchestrator first performs **Pipeline Determination** and selects the smallest safe path.

## Invocation

```text
/conductor-pipeline <your request>
```

Runs under the `conductor-pipeline-orchestrator` agent. Autonomy is **full-auto through the selected path**. The pipeline still stops on unclear/destructive/blocked tasks, classification uncertainty, missing required tests, invalid RED state, unavailable models without fallback, and iteration caps.

## Pipeline Determination

Every run must print and, when possible, persist this decision in track metadata:

- `track_type`: `code` or `bookkeeping`
- `classification`: `certain` or `uncertain`
- production-code changes: yes/no/uncertain
- `test_framework` and `test_command`
- risk level
- selected `pipeline_mode`: `full`, `standard`, `bookkeeping`, or `emergency`
- selected path
- skipped stages with reasons

## Pipeline modes

| Mode | Path | Use when |
|---|---|---|
| `full` | `1 -> 2 -> 3? -> 4 -> 4b -> 5 -> 6 -> 7 -> 8? -> 9` | Meaningful/high-risk production-code changes; TDD/test authoring; APIs/auth/storage/migrations/security/deployment/shared infrastructure; ambiguous acceptance criteria; high failure cost; or explicit full-pipeline request. |
| `standard` | `1 -> 2 -> 5 -> 6 -> 7 -> 9` | Localized low/medium-risk code changes where existing tests are adequate and RED test-writing is unnecessary or explicitly waived. |
| `bookkeeping` | `1 -> 5 -> 7 -> 9`, or `5 -> 7 -> 9` for an already-ready track | Markdown/config/skill/agent/process-only changes with deterministic literal/schema/file checks and no production-code/test framework. This is the normal **Execute -> Validate -> Closeout** abbreviated path after a plan exists. |
| `emergency` | `triage -> minimal fix -> targeted test/check -> validation -> follow-up note` | Explicit urgent restoration/incident work where scope must stay minimal and follow-up hardening is tracked separately. |

## Stage catalog

| # | Stage | Subagent / owner | Model | Runs by default in |
|---|---|---|---|---|
| 1 | Plan creation | conductor-plan-creator | openai/gpt-5.5 (low) | full, standard, bookkeeping when no ready plan exists |
| 2 | Plan review | conductor-plan-reviewer | opencode-go/minimax-m3 | full, standard |
| 3 | Conditional re-review | conductor-plan-reviewer-alt | openai/gpt-5.5 (low) | full when B+C threshold triggers |
| 4 | Write tests (RED) | conductor-test-writer | opencode-go/qwen3.7-plus | full/TDD code paths |
| 4b | RED-state gate | orchestrator logic | n/a | full/TDD code paths |
| 5 | Execution / GREEN | conductor-track-executor + fallbacks | zai-coding-plan/glm-5.2 primary (variant high) | all modes except pure triage-only emergency steps |
| 6 | Run tests | conductor-test-runner | opencode-go/minimax-m3 | full, standard code paths |
| 7 | Validation | conductor-track-validator | opencode-go/minimax-m3 | full, standard, bookkeeping |
| 8 | Conditional re-validation | conductor-track-validator-alt | openai/gpt-5.5 (low) | when A+C threshold triggers |
| 9 | Documentation / Closeout | conductor-doc-writer | zai-coding-plan/glm-5.1 | all modes, or explicit waiver |

Conductor tracks are the source of truth: `.conductor/tracks/<track-id>/`.

## Model diversity

- Reviewer model != creator model when review runs.
- Validator model != executor model.
- Re-review differs from the preceding reviewer; re-validation differs from the executor.
- Doc-writer is terminal closeout, not an independent validation gate.

## Fallbacks / rollback

- Model unavailable: log `model-unavailable`, then apply the Stage 5 three-tier fallback chain (Tier 1 glm-5.2 -> Tier 2 glm-5.1 -> Tier 3 qwen3.7-plus), retrying each tier up to 2x before escalating.
- Execution failure: stop, log, leave incomplete tasks unchecked; prefer OpenCode `/undo` or snapshots; never auto-delete untracked files.
- Validation blockers: route back once according to issue type, then stop and ask.

## Files in this pipeline package

- Command: `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`
- Orchestrator: `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`
- Subagents: `C:\Users\DaveWitkin\.config\opencode\agent\conductor-{plan-creator,plan-reviewer,plan-reviewer-alt,test-writer,test-runner,track-executor,track-executor-glm51,track-executor-qwen,track-validator,track-validator-alt,doc-writer}.md`
- Skill: `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` plus `references\`

## After editing any of these files

OpenCode does not hot-reload config. **Quit and restart OpenCode** before testing. Verify with `opencode agent list` and `opencode models`.


## GLM-5.2 thinking default

Z.AI `glm-5.2` defaults to the `high` thinking variant for quota efficiency. Keep `max` as an explicit opt-in for rare edge cases where high has already failed or marginal extra reasoning is worth the quota cost.
