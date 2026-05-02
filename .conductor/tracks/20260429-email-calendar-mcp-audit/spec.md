# Spec: Email & Calendar MCP Integration Audit & Repair

## Goal

Audit the entire email/calendar MCP toolchain in OpenCode desktop, fix the critical tool-name mismatch in existing Outlook skills, evaluate and recommend a Google Gmail/Calendar MCP server for installation, and create dedicated calendar skills for Outlook.

## Background

OpenCode desktop has a Microsoft 365 MCP server (`@softeria/ms-365-mcp-server`) configured and working, providing 200+ tools for email, calendar, files, and more. Five Outlook email skills exist but reference `mcp__codex_apps__microsoft_outlook_email.*` tool names from Codex CLI — these names do NOT match the actual `ms365` MCP server tools, so the skills will break when invoked.

No Google Gmail or Google Calendar MCP server is installed. No calendar-specific skills exist for either platform.

## Requirements

### R1: Transition Outlook Email Skills to Graph PowerShell
- [ ] Audit all 5 Outlook email skills for obsolete `mcp__codex_apps__*` tool references
- [ ] Refactor the instructions in these skills to instruct the agent to use `bash` to call `Microsoft.Graph` PowerShell cmdlets (e.g., `Get-MgUserMessage`) instead of MCP tools
- [ ] Create clear skill reference files (`reference.md` or similar) for each skill demonstrating exact PowerShell commands needed for common operations
- [ ] Validate each skill works end-to-end natively via Graph PowerShell

### R2: Evaluate & Install Google Gmail/Calendar MCP Server
- [ ] Research top Google MCP server options (npm packages already identified)
- [ ] Select the best option based on: auth method, tool coverage, maintenance, compatibility
- [ ] Install and configure in `opencode.json` alongside existing `ms365` server
- [ ] Complete OAuth2 flow or service account setup
- [ ] Validate Gmail read/write and Calendar read/write operations

### R3: Create Calendar Skills for Outlook
- [ ] Create `calendar-today` skill — show today's schedule, upcoming meetings, conflicts
- [ ] Create `calendar-schedule` skill — schedule/edit/cancel meetings with natural language
- [ ] Ensure skills use `Microsoft.Graph.Calendar` PowerShell cmdlets for deterministic execution
- [ ] Create skill reference files documenting the exact PowerShell syntax for these calendar operations

### R4: Create Test Plan
- [ ] Document test procedures for Outlook email (PowerShell)
- [ ] Document test procedures for Outlook calendar (PowerShell)
- [ ] Document test procedures for Google Gmail (MCP)
- [ ] Document test procedures for Google Calendar (MCP)
- [ ] Include auth verification, CRUD operations, error handling
- [ ] Create a validation checklist for each skill

## Non-Requirements

- [ ] Not building new MCP servers from scratch — using existing npm packages
- [ ] Not migrating away from `@softeria/ms-365-mcp-server` — it works and is comprehensive
- [ ] Not replacing the email routing config system (routing-overrides.json, etc.)
- [ ] Not creating Google-specific email/calendar skills in this track (future work)
- [ ] Not modifying the Slack MCP server configuration

## Acceptance Criteria

- [ ] All 5 Outlook email skills use correct `ms365` MCP tool names
- [ ] Each Outlook email skill tested and confirmed working
- [ ] Google MCP server installed, configured, and authenticated
- [ ] Google Gmail read + send validated
- [ ] Google Calendar list + create validated
- [ ] At least 1 Outlook calendar skill created and tested
- [ ] Test plan documented and saved to track artifacts
- [ ] All tasks in plan.md marked [x]
