# OpenCode Subagent Model Routing

Last verified: 2026-06-15

## Short answer

To run a Task/subagent on a specific model, define the target as an OpenCode **subagent** and set an explicit `model` on that subagent.

Do **not** try to call a primary agent such as `01-Planner` through the Task tool. Primary agents are session/orchestrator agents; Task-callable agents must be configured with `mode: subagent` or `mode: all` and must be allowed by the invoking agent's `permission.task` rules.

Official docs: <https://opencode.ai/docs/agents/>  
Config schema: <https://opencode.ai/config.json>

## Why this matters

OpenCode's documented behavior is:

> If you don't specify a model, primary agents use the model globally configured while subagents will use the model of the primary agent that invoked the subagent.

That means a subagent such as `general` or `explore` can unexpectedly inherit an expensive primary/orchestrator model such as GPT-5.5 unless that subagent has its own `model` configured.

For cost-controlled research, ClickUp gathering, repo scanning, and similar delegated work, create a GLM-backed subagent with an explicit model, for example `zai-coding-plan/glm-5.1`.

## Correct pattern: dedicated GLM subagent

Preferred file location for a global user agent:

```text
C:\Users\DaveWitkin\.config\opencode\agent\glm-researcher.md
```

Example frontmatter:

```markdown
---
name: glm-researcher
description: GLM-backed research subagent for repo, docs, web, and ClickUp/context gathering when the primary model is expensive.
mode: subagent
model: zai-coding-plan/glm-5.1
permission:
  edit: deny
  bash: ask
  webfetch: allow
  websearch: allow
---

You are a cost-controlled research subagent. Gather evidence, read files, search docs, and return concise findings with sources. Do not edit production code.
```

Then ensure the primary/orchestrator agent allows it through `permission.task`:

```yaml
permission:
  task:
    "*": deny
    glm-researcher: allow
```

Important: OpenCode permission matching is last-match-wins, so put broad rules first and specific allows/denies later.

## Alternative: make a primary agent dual-use only if intentional

If the goal is to call an existing primary agent through Task, it must be changed or copied to support subagent mode:

```yaml
mode: all
model: zai-coding-plan/glm-5.1
```

This is not the preferred fix for `01-Planner` because `mode: all` changes the agent's role surface. A safer approach is to copy the relevant planner instructions into a separate subagent file, for example `01-planner-subagent.md`, with `mode: subagent` and an explicit GLM model.

## Inline `opencode.json(c)` equivalent

Agents can also be configured inline under the top-level `agent` key:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "glm-researcher": {
      "description": "GLM-backed research subagent for cost-controlled delegated research.",
      "mode": "subagent",
      "model": "zai-coding-plan/glm-5.1",
      "permission": {
        "edit": "deny",
        "bash": "ask",
        "webfetch": "allow",
        "websearch": "allow"
      }
    }
  }
}
```

Prefer a markdown agent file for anything with substantial instructions.

## Current local observations

- `C:\Users\DaveWitkin\.config\opencode\agent\01-planner.md` is configured as `mode: primary` with `model: zai-coding-plan/glm-5.1`. Because it is primary-only, it is not a valid Task subagent target.
- Existing subagents such as `brand-voice-validator`, `gen-headlines`, `peer-review`, and `seo-auditor` are `mode: subagent` but, at the time of this check, several did not declare an explicit `model`; by official OpenCode behavior, they may inherit the invoking primary model.
- `cove-verifier` already declares `model: zai-coding/glm-4.7`, but it is specialized for blind fact-check questions and should not be reused as a broad research worker.
- Several local agent files use `permissions:` in frontmatter. The official schema and docs use singular `permission:`. Treat `permissions:` as a compatibility risk unless confirmed by the current loader; new or edited files should use `permission:`.

## Diagnostics from this investigation

- `opencode agent list` showed `01-Planner (primary)`, confirming it is a primary agent rather than a subagent.
- The Task tool rejected `subagent_type: "01-planner"` because primary agents are not exposed as Task subagent types.
- Attempting to use native CLI runs with `opencode run --agent "01-Planner" --model "zai-coding-plan/glm-5.1" ...` failed in this environment with `Error: Session not found`. Treat that as a CLI/session runtime issue, not as evidence against the documented agent model-routing mechanism.
- A 2026 GitHub issue about model assignment not being recognized was resolved in practice by restarting OpenCode. Config and agent files are loaded at startup and are not hot-reloaded.

## Required restart

After creating or editing any OpenCode agent/config file, quit and restart OpenCode before testing. Running sessions keep the already-loaded config.

## Verification checklist

1. Add a dedicated subagent with `mode: subagent` and explicit `model`.
2. Ensure the primary agent's `permission.task` allows that subagent name.
3. Restart OpenCode.
4. Run `opencode agent list` and confirm the new agent appears as a subagent.
5. From an expensive primary session, invoke a small Task using the new subagent and inspect session/model history to confirm it ran on the GLM provider/model.

## Recommended next fix

Create a new `glm-researcher` or `01-planner-subagent` agent file instead of changing `01-Planner` directly. Give it:

- `mode: subagent`
- `model: zai-coding-plan/glm-5.1`
- read/search/web tools as needed
- `edit: deny` unless the subagent is explicitly intended to write documentation/config
- a clear description so it is exposed in Task tool choices

Then add an explicit allow rule for that subagent under the primary agent's `permission.task` rules and restart OpenCode.
