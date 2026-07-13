---
name: agent-writer
description: Create and update OpenCode agents. Use when the user wants a new agent, agent frontmatter, permissions, tools, or validation against OpenCode standards.
compatibility: OpenCode agents (global or project-local).
---

# Agent Writer

Use this skill to design, implement, and validate OpenCode agents (primary and subagents).

## Decision Tree

If the user says "create/add an agent":
- Clarify agent type (primary, read-only subagent, write-enabled subagent)
- Identify required tools and justify any write/edit/bash access
- Draft frontmatter and body instructions
- Validate against agent standards and checklists
- Test the new agent frontmatter using the CLI (opencode run --agent <name> "test")

If the user says "my agent isn't working":
- Check agent file location and naming
- Check frontmatter keys and indentation
- Check tools + permission.skill settings
- Verify conflicts with project/global rules

## Quick Start

- Templates and checklists: `references/agent-templates.md`
- Validation checklist: `references/validation.md`

## Required References

- Global rules: `~/.config/opencode/AGENTS.md`
- Agent standards: `~/.config/opencode/agent-development-standards.md`
- Command standards: `~/.config/opencode/command-development-standards.md`
- Standards reference: `~/.config/opencode/opencode-standards-reference.md`
- OpenCode specifics: `skill-guidelines/03-opencode-specifics.md`
- Practical guide: `skill-guidelines/02-practical-skill-writing-guide.md`

## Activation Examples

Use this skill for prompts like:
- "Create a read-only PR review agent"
- "Add a write-enabled subagent for generating reports"
- "Fix my agent frontmatter"
- "What permissions should this agent have?"

## Gotchas / Guardrails

- Read-only agents must set `skill: true` and grant all read-only skills.
- Write-enabled subagents must justify write/edit/bash access.
- Avoid duplicating standards; reference canonical docs instead.

## Output Expectations

- Provide a full agent frontmatter template and clear reasoning.
- Include a validation checklist for final review.
- **CRITICAL**: If you created a new agent file, you MUST explicitly tell the user: *"Please restart this OpenCode session so the Task tool can register the new agent."*
