# Spec: GLM 5.2 Model Migration

## Goal / Outcome

Migrate all OpenCode agent model configurations from GLM 5.1 (and GLM 4.7) to GLM 5.2 as the universal default, with an architecture that ensures subagents never inherit an expensive orchestrator model (e.g., GPT-5.5) when the user switches their session model.

The end state has two distinct layers:

1. **Primary agents** (01-Planner, Boost, Build) inherit the global default (GLM 5.2) but can be overridden per-session via `/model` -- this is the flexibility layer.
2. **Subagents** (all 6 custom + 3 built-in: general, explore, scout) have explicit model pins to GLM 5.2 -- this is the cost-isolation layer. They NEVER inherit the invoking primary's model.

**Why this matters:** OpenCode's documented behavior is -- *"If you don't specify a model, primary agents use the model globally configured while subagents will use the model of the primary agent that invoked the subagent."* Without explicit pins, a GPT-5.5 orchestrator would make every inheriting subagent run on GPT-5.5.

## Constraints / Non-Goals

- **Do NOT modify permissions.** The `permissions:` (plural) vs `permission:` (singular) issue is explicitly out of scope per user direction. Do not touch any permission blocks in any file.
- **Do NOT change agent prompts, descriptions, tools, or modes.** Only `model:` frontmatter lines are touched.
- **Do NOT create new agent files.** No new agents (e.g., no `glm-researcher`).
- **Do NOT remove the built-in Plan agent model override** (`"plan": { "model": "openai/gpt-5.3-codex" }`). Keep it as-is; expand the `agent` block additively.
- **Do NOT restart OpenCode as part of this plan.** Restart is the user's responsibility post-completion.
- **Do NOT touch any `permissions:`, `tools:`, `description:`, or body text** in agent files.

## Definition of Done

- [x] `opencode.jsonc` global `model` and `small_model` are both `zai-coding-plan/glm-5.2`.
- [x] `opencode.jsonc` `agent` block includes `general`, `explore`, and `scout` subagent pins to `zai-coding-plan/glm-5.2` (alongside the existing `plan` override).
- [x] Primary agents (`01-planner.md`, `boost.md`, `build.md`) have NO `model:` line in frontmatter.
- [x] All 6 custom subagents have `model: zai-coding-plan/glm-5.2` in frontmatter.
- [x] `cove-verifier.md` updated from `zai-coding/glm-4.7` to `zai-coding-plan/glm-5.2`.
- [x] No permission blocks, tools blocks, or prompts were modified.
- [x] All changes verified by automated checks (file content assertions).
- [x] No `glm-5.1` or `glm-4.7` string remains in any agent file.