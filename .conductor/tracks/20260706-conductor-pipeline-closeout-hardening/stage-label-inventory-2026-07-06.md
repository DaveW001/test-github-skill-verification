# Stage Label Inventory - 2026-07-06

Scope: global Conductor pipeline/agent files only.

## conductor-track-executor-glm51.md

| Line | Content (stale) |
|------|-----------------|
| 4 | `description: Stage 4 of the Conductor pipeline. Executes pending non-deferred Conductor plan items in order.` |
| 21 | `You are the **Conductor Track Executor** (Stage 4). Use the track's plan.md as the source of truth.` |
| 23 | `Load the Stage 4 prompt from skill/conductor-pipeline/references/stage-prompts.md and follow it. Execute .` |

Defect: describes fallback **execution** as Stage 4. Correct stage is **Stage 5** (GREEN phase). Stage 4 is the
test-writer (TDD RED). The glm51 agent is a Tier-2 fallback executor, not a test writer.

## conductor-track-executor-qwen.md

| Line | Content (stale) |
|------|-----------------|
| 4 | `description: Stage 4 of the Conductor pipeline. Executes pending non-deferred Conductor plan items in order.` |
| 21 | `You are the **Conductor Track Executor** (Stage 4). Use the track's plan.md as the source of truth.` |
| 23 | `Load the Stage 4 prompt from skill/conductor-pipeline/references/stage-prompts.md and follow it. Execute .` |

Defect: identical to glm51. The qwen agent is a Tier-3 fallback executor; correct stage is **Stage 5**.

## Remediation plan (Phase 2)

Change the three occurrences in each agent from `Stage 4` -> `Stage 5`, preserving model/tier/fallback semantics.
Lines referencing `Stage 4 prompt` must point to `Stage 5 prompt` (the execution prompt), NOT the test-writer prompt.
