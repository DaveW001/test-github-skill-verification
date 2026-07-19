# GPT-5.6 SOL Low-Thinking Migration

## Goal

Replace every active OpenCode agent and active OpenCode configuration/documentation reference that selects GPT-5.5 with `openai/gpt-5.6-sol` using the `low` reasoning variant.

## Scope

- Global active OpenCode configuration under `C:\Users\DaveWitkin\.config\opencode\`.
- Active global agents and global Conductor-pipeline skill documentation.
- Repository-local OpenCode agent/skill configuration across every Git repository directly under `C:\development\`.
- Deterministic configuration validation and a live model-selection smoke test.

## Discovered active inventory

| Kind | Absolute path | GPT-5.5 usage | Required migration |
|---|---|---|---|
| Agent | `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-creator.md` | `model: openai/gpt-5.5`; already `variant: low` | Set model to `openai/gpt-5.6-sol`; preserve low variant. |
| Agent | `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer-alt.md` | Model pin plus descriptive GPT-5.5-low text | Set model to SOL; retain low; update descriptive text. |
| Agent | `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-alt.md` | Model pin plus descriptive GPT-5.5-low text | Set model to SOL; retain low; update descriptive text. |
| Agent | `C:\Users\DaveWitkin\.config\opencode\agent\peer-review.md` | Model pin and body says GPT-5.5 with medium default | Set model to SOL, add `variant: low`, and update body text. |
| Provider model override | `C:\Users\DaveWitkin\.config\opencode\opencode.json` | Custom `gpt-5.5` and obsolete `gpt-5.5-fast` model definitions | Add/replace an explicit `gpt-5.6-sol` definition whose `low` variant has `reasoningEffort: low`; remove or retire the obsolete 5.5 overrides after no active consumer remains. |
| Skill docs | `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` | Stage 1, 3, 8 routing and diversity wording | Change all three routes and wording to SOL low. |
| Skill docs | `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md` | Stage-routing table | Change its three GPT routes to SOL low. |
| Skill docs | `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md` | Default model route | Change default creation/re-review/re-validation route to SOL low. |
| Reference doc | `C:\Users\DaveWitkin\.config\opencode\docs\reference\subagent-model-routing.md` | GPT-5.5 inheritance example | Update the illustrative model name to SOL. |

## Exclusions

- Timestamped `.bak*` files, archived skills, session logs, handoffs, knowledge-base indexes, and historical exports are evidence/history, not active runtime configuration. Do not rewrite them.
- No active repository-local agent or skill configuration in the Git repositories directly under `C:\development\` selected GPT-5.5. The sole repository-local hit was a historical handoff: `C:\development\opencode\.opencode\handoffs\20260704-2035-scheduled-task-read-inconsistency.md`.
- Do not change non-OpenAI stage assignments or the pipeline diversity policy.

## Evidence and constraints

- `opencode models openai` lists `openai/gpt-5.6-sol`, `openai/gpt-5.6-sol-fast`, and `openai/gpt-5.6-sol-pro`.
- The required target is specifically `openai/gpt-5.6-sol` with `variant: low`; it is not the generic `openai/gpt-5.6` model.
- A pre-change live probe using OpenCode 1.15.10 failed before model execution with `Error: Session not found`. This is a runtime/session issue, so a restart (and, if it persists, resolution of the known session issue) is required before live validation can pass.

## Acceptance criteria

1. Active global agents formerly pinned to GPT-5.5 all pin `openai/gpt-5.6-sol` and declare `variant: low`.
2. The active provider override exposes the SOL model with a valid `low` variant that maps to `reasoningEffort: low`.
3. All active global skill/reference routing documentation reflects SOL low; no active GPT-5.5 routing remains.
4. A targeted scan of active global config/agent/skill/reference paths and repository-local active config paths returns zero GPT-5.5 model-routing references.
5. OpenCode accepts `openai/gpt-5.6-sol` with `--variant low` in a post-restart live smoke test.
6. Pipeline diversity rules remain true because SOL differs from MiniMax reviewers/validators and GLM executor.
