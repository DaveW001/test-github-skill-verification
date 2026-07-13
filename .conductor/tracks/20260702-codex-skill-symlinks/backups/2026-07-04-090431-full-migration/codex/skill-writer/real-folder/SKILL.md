---
name: skill-writer
description: Create and update OpenCode skills (SKILL.md) with valid frontmatter, strong activation descriptions, structured trigger metadata, decision trees, and progressive disclosure.
compatibility: OpenCode skills system; works for both project-local and global skill locations.
---

# Skill Writer

Use this skill when you want to create, refactor, or validate OpenCode skills.

## Decision Tree

If the user says "create a skill":
- gather scope + triggers
- choose location (project vs global)
- write frontmatter (name=slug, description, optional triggers metadata, optional compatibility)
- keep SKILL.md concise and push details into references

If the user says "my skill isn't loading":
- check file name is `SKILL.md`
- check frontmatter YAML validity
- check `name` matches the folder slug and naming regex

If the user says "improve my skill":
- tighten description for activation
- add activation examples
- add compatibility notes
- implement progressive disclosure

## Quick Start

- Checklist and patterns: `reference.md`
- Validation notes: `VALIDATION.md`
- Shared prompt templates: `patterns/prompts/README.md`

## Required References

- OpenCode specifics: `skill-guidelines/03-opencode-specifics.md`
- Practical guide: `skill-guidelines/02-practical-skill-writing-guide.md`

## Activation Examples

Use this skill for prompts like:
- "Create an OpenCode skill for <workflow>"
- "Fix my SKILL.md frontmatter"
- "Why isn't my skill being discovered?"
- "Refactor this skill to use progressive disclosure"

## Gotchas / Guardrails

- Unknown frontmatter keys are ignored by OpenCode.
- Keep references one level deep (avoid `SKILL.md -> A -> B`).
