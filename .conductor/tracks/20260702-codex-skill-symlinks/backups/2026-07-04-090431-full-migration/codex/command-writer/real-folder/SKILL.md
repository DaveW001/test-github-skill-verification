---
name: command-writer
description: Create and improve OpenCode/Claude slash commands. Use when the user asks to create a command, add a slash command, define command frontmatter, add arguments, file references, tool permissions, or interactive prompts.
compatibility: Works for OpenCode commands and Claude-compatible command layouts. Examples assume Markdown-based commands.
---

# Command Writer

Use this skill to design, implement, and troubleshoot slash commands (structure, YAML frontmatter, arguments, tool permissions, and testing).

## Decision Tree

If the user says "create/add a command":
- Decide scope: project command vs user command
- Draft command file + frontmatter + prompt
- Add argument handling (`$ARGUMENTS`) and file references only if needed

If the user says "my command isn't working":
- Check frontmatter keys/indentation
- Check allowed-tools permissions
- Check file location and naming conventions

## Quick Start

- For a minimal command example, see `examples/simple-commands.md`.
- For interactive command patterns (asking user questions), see `references/interactive-commands.md`.
- For a frontmatter field reference, see `references/frontmatter-reference.md`.

## Required References

- Global rules: `~/.config/opencode/AGENTS.md`
- Command standards: `~/.config/opencode/command-development-standards.md`
- Agent standards (for agent-invoking commands): `~/.config/opencode/agent-development-standards.md`
- Standards reference: `~/.config/opencode/opencode-standards-reference.md`
- OpenCode specifics: `skill-guidelines/03-opencode-specifics.md`

## Activation Examples

Use this skill for prompts like:
- "Create a /git-push command"
- "Add a slash command that runs tests and summarizes failures"
- "How do I add command arguments and autocomplete hints?"
- "Why is my allowed-tools frontmatter being ignored?"

## Gotchas / Guardrails

- Commands are instructions for the agent, not user-facing documentation.
- Keep command bodies short; link out to references for long guidance.
- Prefer `allowed-tools` to the minimum necessary.

## References

- Full legacy content: `references/legacy-SKILL-2026-01-18.md`
- Examples: `examples/simple-commands.md`, `examples/plugin-commands.md`
- Advanced workflows: `references/advanced-workflows.md`
- Interactive patterns: `references/interactive-commands.md`
- Frontmatter reference: `references/frontmatter-reference.md`
