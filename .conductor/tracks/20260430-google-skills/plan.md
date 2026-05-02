# Plan

## Phase 1 — Skill Scaffolding & Google MCP Tool Mapping
- [x] Create `reference.md` in each skill directory with Google MCP tool names, parameters, and examples
- [x] Map all 27 Google MCP tools to skill use-cases (which skill uses which tools)
- [x] Define frontmatter for each skill (triggers, description, tool_context)

## Phase 2 — Gmail Skills (HIGH priority)
- [x] Create `gmail-inbox-triage` skill — batched triage, interview pattern, action labels
- [x] Create `gmail-draft-reply` skill — Dave's voice, draft-only, scheduling link
- [x] Validate both skills have correct frontmatter

## Phase 3 — Google Calendar Skills (HIGH/MEDIUM)
- [x] Create `google-calendar-today` skill — today's schedule, conflicts, upcoming
- [x] Create `google-calendar-schedule` skill — natural language scheduling, find slots, CRUD
- [x] Validate both skills have correct frontmatter

## Phase 4 — Unified Calendar (MEDIUM)
- [x] Create `unified-calendar-today` skill — combine Outlook (Graph PowerShell via bash) + Google (MCP) calendars
- [x] Implement conflict detection across both platforms
- [x] Handle timezone normalization (both sources → local time)

## Phase 5 — Google Contacts (LOW)
- [x] Create `google-contacts` skill — search, lookup, create, update contacts
- [x] Reference MCP tools: list-contacts, get-contact, create-contact, update-contact, delete-contact

## Phase 6 — Validation & Cleanup
- [x] Test all 6 skills load via file validation
- [x] Verify frontmatter triggers match agent skill listing
- [x] Update tracks-ledger.md — move track to Completed
- [x] Update metadata.json — status=completed, percentage=100

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.
