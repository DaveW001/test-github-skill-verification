# Spec: Global Skills Index Regeneration

**Track ID**: 20260530-global-skills-index-regen
**Created**: 2026-05-30
**Status**: pending
**Priority**: high

## Problem

The global skills index (`docs/reference/global-skills-index.md`) is 35 days stale (last updated 2026-04-25). It contains only 40 of 64 active skills, has 1 duplicate entry, and is missing 27 skills that exist on disk with valid frontmatter.

## Scope

Regenerate `global-skills-index.md` to accurately reflect all 64 active skills in the taxonomy.

## In Scope

- Read all 64 active skill SKILL.md frontmatters from `~/.agents/skills/`
- Build categorized index tables with name, description, and location
- Resolve the `notebooklm-meta-prompt` duplicate (keep in most relevant section only)
- Include all 27 missing skills with appropriate categories
- Update the "Last updated" date to 2026-05-30
- Preserve the existing markdown structure and formatting conventions

## Out of Scope

- Modifying any SKILL.md files
- Changing junction configuration
- Modifying archived skills
- Touching the canonical skill directory

## Acceptance Criteria

1. All 64 active skills appear in the index exactly once
2. No duplicates (including `notebooklm-meta-prompt`)
3. Each entry has accurate name and description matching its SKILL.md frontmatter
4. Categories are logically consistent with skill purposes
5. "Last updated" date reflects regeneration date
6. Markdown structure is valid (tables render correctly)

## Missing Skills to Add (27)

calendar-schedule, calendar-today, clickup, clickup-cli, doc, email-routing-config, find-info, gmail-draft-reply, gmail-inbox-triage, gmail-workspace, google-calendar-schedule, google-calendar-today, google-contacts, google-drive, imagegen, knowledge-graph-builder, knowledge-graph-maintainer, microsoft-graph, nlm-skill, outlook-email-search, playwright-interactive, skill-discovery, slack-messaging, speech, unified-calendar-today, vercel-deploy, visual-ocr

## Duplicate to Resolve

- `notebooklm-meta-prompt`: Remove from AI & Agent Tooling section, keep in NotebookLM & Research section
