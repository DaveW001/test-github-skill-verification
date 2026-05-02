# Spec

## Goal
Create Google-side skills that mirror the existing Outlook email + calendar skills, closing all capability gaps identified in the email/calendar infrastructure audit. Also create a unified calendar skill that checks both Outlook and Google calendars for conflicts.

## Context
Track `20260429-email-calendar-mcp-audit` (completed) delivered:
- 5 Outlook email skills refactored to Graph PowerShell
- 2 Outlook calendar skills (`calendar-today`, `calendar-schedule`)
- Google MCP server (`mcp-google`) installed with 27 tools (Gmail 14, Calendar 8, Contacts 5)
- OAuth tokens at `C:\Users\DaveWitkin\.config\google-calendar-mcp\tokens.json`
- Config in `opencode.json` under `mcp.google`

The Google MCP tools are available but no skills exist to guide agents in using them for common workflows (triage, drafting, scheduling, calendar review).

## Requirements
- [ ] `gmail-inbox-triage` — Guided Gmail triage skill mirroring `outlook-inbox-triage` (batched, interview-style)
- [ ] `gmail-draft-reply` — Gmail reply drafting skill mirroring `email-draft-reply` (Dave's voice, draft-only)
- [ ] `google-calendar-today` — Google Calendar schedule view mirroring `calendar-today`
- [ ] `google-calendar-schedule` — Google Calendar scheduling mirroring `calendar-schedule`
- [ ] `unified-calendar-today` — Cross-platform calendar view (Outlook + Google combined, conflict detection)
- [ ] `google-contacts` — Basic contact lookup/management using Google MCP Contacts tools
- [ ] All skills use Google MCP tools directly (NOT bash/PowerShell — Google has no Graph equivalent)
- [ ] All skills have proper frontmatter (`tool_context.with_tools` listing MCP tools)
- [ ] All skills have `reference.md` files with tool name mappings and syntax examples

## Non-Requirements
- [ ] Google email auto-sorting (Gmail has native labels/filters; not a priority)
- [ ] Google email routing config (no equivalent JSON config system for Gmail)
- [ ] Email-to-ClickUp for Gmail (can use existing skill if needed; low priority)
- [ ] Google Drive / Google Docs / Google Sheets MCP integration
- [ ] Any changes to existing Outlook skills

## Acceptance Criteria
- [ ] All 6 new skills loadable via `skill({ name: "..." })` and show correct instructions
- [ ] Each skill has valid frontmatter with correct `tool_context.with_tools`
- [ ] Each skill has a `reference.md` with Google MCP tool names and example parameters
- [ ] `unified-calendar-today` successfully queries both Outlook (Graph PowerShell) and Google (MCP) calendars
- [ ] Skills appear in agent skill listing with correct descriptions
- [ ] All tasks in `plan.md` marked [x]
- [ ] Track closed in ledger

## Related Tracks
- `20260429-email-calendar-mcp-audit` (completed) — prerequisite that installed Google MCP and created Outlook skills
