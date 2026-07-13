# ADR-001: Registered OpenCode subagents for pptx-from-layouts

- **Status:** Accepted
- **Date:** 2026-07-10
- **Track:** `20260709-pptx-skill-adapt`
- **Decision owner:** User (explicit override of the plan-creator default)
- **Supersedes:** Plan-creator's reference-prompt-file default (rejected)

## Context

The source `pptx-from-layouts` Claude Code skill delegates to three distinct
roles, each with its own prompt:

1. **Outline architect** - turns raw source material (a brief, notes, a
   transcript) into a generation-ready `outline.md` with the correct
   `**Visual:**` declaration on every slide.
2. **Template onboarder** - one-time profiling of a user's own `.pptx` into a
   reusable, on-brand template (catalog + render config + smoke test).
3. **Deck QA** - runs `validate.py`, interprets the report, and either applies
   a surgical `edit.py` fix or recommends regeneration.

In the Claude Code source these were authored as agent prompt files installed to
`~/.claude/agents/` and activated by Claude's `tools:` / `model:` frontmatter
semantics. When adapting the skill for **OpenCode**, the way a primary agent
programmatically delegates to a specialized role is the **Task tool**, which
dispatches by a registered `subagent_type`. That mechanism requires the role to
exist as a **registered OpenCode agent** in the agent registry - it cannot
dispatch to an arbitrary unregistered prompt file.

Additionally, this skill is installed **globally** in the OpenCode lazy vault
(`~/.opencode-lazy-vault/pptx-from-layouts`), and the orchestrator / primary
agents are expected to invoke these roles across multiple sessions, not just
within a single project.

## Decision

Register **three global OpenCode subagents**, one per role, at the global agent
path rather than carrying reference prompt files inside the skill or folding the
role logic into the main skill body:

- `C:\Users\DaveWitkin\.config\opencode\agent\pptx-outline-architect.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\pptx-template-onboarder.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\pptx-deck-qa.md`

Each agent uses canonical OpenCode subagent frontmatter translated from the
Claude source:

- `mode: subagent`
- `hidden: true`
- `description: <specific activation trigger>` (this is what the Task tool
  matches on; it is **not** the Claude `model:` or a bare agent name)
- `permission: { edit: allow, bash: allow, task: { "*": deny } }` - they write
  outputs (`edit`), must run the bundled scripts (`bash`), and are denied
  further Task-tool delegation (`task`) to prevent recursion.
- No `tools:` block and no `model:` field (agents default to the session model).
- No `~/.claude/` paths anywhere in the prompt body.

Placement is **global** (`~/.config/opencode/agent/`) because the skill itself
is global (lazy vault) and the roles are reused across sessions and projects.

## Alternatives considered

1. **Reference prompt files inside the skill** (`<skill>\agents\*.md`, manually
   copy-pasted per invocation). **Rejected.** This was the plan-creator's
   default, but it requires a manual copy-paste of the prompt on every use,
   which does not match how the rest of the OpenCode pipeline invokes
   specialized roles (e.g. `peer-review`, `seo-auditor`), and it cannot be
   reached via `Task(subagent_type: ...)`.
2. **Fold the role logic into the main skill body.** **Rejected.** The three
   roles have distinct, specialized instructions and output contracts; merging
   them into one monolithic prompt would dilute the activation triggers and make
   per-role delegation impossible.
3. **Project-scoped agents** (under a project `.opencode/agent/`). **Rejected.**
   The skill is global and the roles are cross-session; project-scoping would
   require re-installing per project.

## Consequences

- **Positive:** Primary agents can delegate to each role programmatically via
  the Task tool with a stable, typed `subagent_type`, consistent with the rest
  of the OpenCode ecosystem. Per-role `permission` scopes limit blast radius
  (e.g. the QA agent can `edit`/`bash` but cannot spawn further subagents).
- **Positive:** The bundled `agents\` directory inside the skill retains
  scrubbed reference copies of the source Claude agents, preserving the
  provenance of the role prompts.
- **Negative / constraint - restart before invocation:** OpenCode caches agent
  types at startup, so agents registered during a running session are not yet
  Task-invokable in that session. A **session restart is required** after first
  registration. (Likewise, the `opencode run --agent <name>` CLI subcommand
  returns "Session not found" for all agents in some CLI contexts - an
  environmental quirk, not a frontmatter defect. No YAML/frontmatter parse
  errors occurred.)
- **Negative / constraint - agents live outside the skill dir:** Because the
  agents are registered globally and **outside** the skill directory, their
  prompt bodies must reference the skill root by **absolute path**
  (`C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts`) rather than a
  relative path. If the skill is ever relocated, the agent prompts must be
  updated in lockstep. This coupling is documented in `README.md` and the
  `CHANGELOG.md` Changed section.

## Tradeoffs

The chosen design prioritizes **programmatic, typed delegation and ecosystem
consistency** over **single-directory portability**. The cost is a registration
step, a one-time restart, and an absolute-path coupling between the global agent
prompts and the skill root. These costs are accepted because Task-tool
delegation is the primary intended interaction model for this skill, and the
restart/absolute-path requirements are one-time and well-documented.
