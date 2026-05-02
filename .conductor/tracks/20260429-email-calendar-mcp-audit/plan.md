# Plan: Email & Calendar MCP Integration Audit & Repair

## Phase 1 — Audit & PowerShell Discovery
- [x] Test key `Microsoft.Graph.Mail` and `Microsoft.Graph.Calendar` cmdlets via bash to ensure auth context is valid
- [x] Identify which cmdlets replace the broken `mcp__codex_apps__*` tools
- [x] Draft reference markdown files that show exact PowerShell syntax for: reading inbox, drafting replies, moving messages
- [x] Artifact: `artifacts/graph-powershell-reference.md` (448 lines, 21 operations tested)

## Phase 2 — Refactor Outlook Email Skills
- [x] Update `outlook-inbox-triage` skill — replaced frontmatter `tool_context.with_tools` with `execution_layer: graph-powershell`, added Graph PowerShell section
- [x] Update `email-draft-reply` skill — same frontmatter + body updates, added reply draft syntax
- [x] Update `email-auto-sorter` skill — frontmatter + body, replaced `_move_email` with `Move-MgUserMessage`, added folder resolution + mark-as-read syntax
- [ ] Update `email-routing-config` skill — SKIPPED: no MCP tool references, JSON config only
- [x] Update `email-to-clickup` skill — frontmatter + body, replaced `_move_email` + `destination_well_known_folder` with Graph PowerShell archive pattern
- [x] Validation: grep confirms zero `mcp__codex_apps__` references across all skill directories
- [ ] Smoke-test each skill end-to-end (requires Build agent to execute)

## Phase 3 — Google MCP Server Selection & Installation
- [x] Evaluate candidates: `mcp-google`, `google-mcp`, `@cocal/google-calendar-mcp`, `@prmichaelsen/google-calendar-mcp`
- [x] Select winner: `mcp-google` (27 tools, npx-compatible, Calendar + Gmail + Contacts)
- [x] Artifact: `artifacts/google-mcp-evaluation.md`
- [ ] Add MCP server entry to `opencode.json` under `mcp.google`
- [ ] Enable Gmail API + People API in Google Cloud project
- [ ] Create OAuth Desktop credentials
- [ ] Run OAuth2 flow to get refresh token
- [ ] Verify server starts without errors in OpenCode

## Phase 4 — Google MCP Validation
- [ ] Test Gmail: `list messages` → `get message` → `send message` → `create draft`
- [ ] Test Calendar: `list calendars` → `list events` → `create event` → `update event`
- [ ] Document available tool names in `artifacts/google-mcp-tools.md`
- [ ] Record any limitations or missing features

## Phase 5 — Outlook Calendar Skills
- [x] Calendar reference syntax included in `artifacts/graph-powershell-reference.md` (Ops C.1–C.6)
- [x] Create `calendar-today` skill:
  - Shows today's events with time, title, location, attendees
  - Flags conflicts and back-to-back meetings
  - Surfaces upcoming meetings in next 2 hours
  - Supports "am I free at 3pm?" follow-ups
- [x] Create `calendar-schedule` skill:
  - Natural language scheduling ("schedule 30min with X tomorrow at 2pm")
  - Find available slots via `getSchedule` API
  - Create/update/cancel events
  - Confirmation before creating or deleting
- [ ] Test each calendar skill end-to-end (requires Build agent to execute)

## Phase 6 — Test Plan & Documentation
- [x] Create `artifacts/test-plan.md` with:
  - Outlook email test procedures (5 skills)
  - Outlook calendar test procedures (2 skills)
  - Google Gmail test procedures
  - Google Calendar test procedures
  - Cross-cutting validation (orphaned references)
  - Smoke test checklist
- [ ] Final review: all acceptance criteria met
- [ ] Update tracks-ledger.md with completion

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ms365 tool names differ from docs | Skills break silently | Phase 1 mapping table validated against live server |
| Google OAuth2 requires browser interaction | Blocks automated setup | Run OAuth manually, cache tokens |
| Google MCP server abandoned/unstable | Wasted time | `mcp-google` built on proven `@cocal` codebase; can be forked |
| Graph session doesn't persist | Empty results in scripts | Every skill includes `Connect-MgGraph` + `Start-Sleep -Seconds 2` |

## Dependencies

- OpenCode desktop running with Graph PowerShell modules installed
- Node.js/npm available for Google MCP server installation
- Google Cloud project `gws-contacts-audit-20260306` with Gmail/Calendar API enabled (Phase 3-4)
- Microsoft 365 account `dave.witkin@packagedagile.com` with Graph API permissions (already configured)

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.
