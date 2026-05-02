# Test Plan: Email & Calendar MCP Integration

> **Track:** 20260429-email-calendar-mcp-audit | **Date:** 2026-04-29

---

## 1. Outlook Email Skills (Graph PowerShell)

### 1.1 outlook-inbox-triage

| Test | Command | Expected | Pass? |
|------|---------|----------|-------|
| List recent inbox | `Get-MgUserMessage -UserId $userId -Top 10 -Sort "receivedDateTime desc"` | Returns ≤10 messages with subject, from, receivedDateTime | |
| Get message by ID | `Get-MgUserMessage -UserId $userId -MessageId $id` | Returns full message with body | |
| Search by subject | `Get-MgUserMessage -UserId $userId -Top 20 -Filter "contains(subject,'test')"` | Returns matching messages | |
| Search by sender | `Get-MgUserMessage -UserId $userId -Top 20 -Filter "from/emailAddress/address eq 'x@y.com'"` | Returns matching messages | |
| Skill frontmatter | Read SKILL.md frontmatter | No `mcp__codex_apps__` references | |
| Body references | Grep SKILL.md for `mcp__codex_apps` | Zero matches | |

### 1.2 email-draft-reply

| Test | Command | Expected | Pass? |
|------|---------|----------|-------|
| Get message context | `Get-MgUserMessage -UserId $userId -MessageId $id` | Returns full message | |
| Create reply draft | `New-MgUserMessageReply -UserId $userId -MessageId $id -BodyParameter @{...}` | Returns draft with WebLink | |
| Draft has webLink | `$draft.WebLink` | Valid Outlook Web URL | |
| Skill frontmatter | Read SKILL.md frontmatter | No `mcp__codex_apps__` references | |
| Body references | Grep SKILL.md for `mcp__codex_apps` | Zero matches | |

### 1.3 email-auto-sorter

| Test | Command | Expected | Pass? |
|------|---------|----------|-------|
| List unread | `Get-MgUserMessage -UserId $userId -Top 20 -Filter "IsRead eq false"` | Returns unread messages | |
| List folders | `Get-MgUserMailFolder -UserId $userId -Property "id,displayName"` | Returns all folders with IDs | |
| Move message | `Move-MgUserMessage -UserId $userId -MessageId $id -DestinationId $folderId` | Returns moved message with new ID | |
| Mark as read | `Update-MgUserMessage -UserId $userId -MessageId $id -BodyParameter @{IsRead=$true}` | No error, message marked read | |
| Skill frontmatter | Read SKILL.md frontmatter | No `mcp__codex_apps__` references, has `execution_layer: graph-powershell` | |
| Body references | Grep SKILL.md for `_move_email` | Zero matches | |

### 1.4 email-routing-config

| Test | Expected | Pass? |
|------|----------|-------|
| No MCP tool references | SKILL.md contains no `mcp__codex_apps__` | |
| Config files exist | All 3 JSON files present and valid | |
| Skill unchanged | No changes needed (JSON config only) | |

### 1.5 email-to-clickup

| Test | Command | Expected | Pass? |
|------|---------|----------|-------|
| Get message | `Get-MgUserMessage -UserId $userId -MessageId $id` | Returns full message with body | |
| Archive message | `Move-MgUserMessage -UserId $userId -MessageId $id -DestinationId $archiveId` | Returns moved message | |
| Skill frontmatter | Read SKILL.md frontmatter | No `mcp__codex_apps__` references, has `execution_layer: graph-powershell` | |
| Body references | Grep SKILL.md for `_move_email` and `destination_well_known_folder` | Zero matches | |

---

## 2. Outlook Calendar Skills (Graph PowerShell)

### 2.1 calendar-today

| Test | Command | Expected | Pass? |
|------|---------|----------|-------|
| List today's events | `Get-MgUserCalendarView -UserId $userId -StartDateTime $today -EndDateTime $tomorrow` | Returns today's events | |
| Event properties | Check Subject, Start, End, Location, Organizer | All populated | |
| Get event details | `Get-MgUserEvent -UserId $userId -EventId $id` | Returns body + attendees | |
| Check availability | `Invoke-MgGraphRequest` to `/calendar/getSchedule` | Returns availability string | |
| Skill loads | Load skill in OpenCode | Activates on "what's on my calendar" | |

### 2.2 calendar-schedule

| Test | Command | Expected | Pass? |
|------|---------|----------|-------|
| Create event | `New-MgUserEvent -UserId $userId -BodyParameter @{...}` | Returns event with ID + WebLink | |
| Update event | `Update-MgUserEvent -UserId $userId -EventId $id -BodyParameter @{...}` | Updated properties reflected | |
| Delete event | `Remove-MgUserEvent -UserId $userId -EventId $id` | No error, event gone | |
| Find free slots | `Invoke-MgGraphRequest` to `/calendar/getSchedule` | Returns availability with free slots | |
| Natural language | Parse "schedule 30min with X tomorrow at 2pm" | Correctly resolves to date/time | |
| Skill loads | Load skill in OpenCode | Activates on "schedule a meeting" | |

---

## 3. Google Gmail/Calendar MCP (Post-Install)

### 3.1 Gmail Operations

| Test | Tool/Command | Expected | Pass? |
|------|-------------|----------|-------|
| MCP server starts | Start OpenCode with google MCP config | No errors in console | |
| List messages | Gmail list tool | Returns recent messages | |
| Get message | Gmail get tool with message ID | Returns full message with body | |
| Create draft | Gmail draft create tool | Returns draft ID | |
| Send message | Gmail send tool | Returns sent message ID | |

### 3.2 Google Calendar Operations

| Test | Tool/Command | Expected | Pass? |
|------|-------------|----------|-------|
| List calendars | Calendar list tool | Returns user's calendars | |
| List events | Calendar events list tool | Returns upcoming events | |
| Create event | Calendar event create tool | Returns new event with ID | |
| Update event | Calendar event update tool | Updated properties reflected | |
| Delete event | Calendar event delete tool | No error, event gone | |

---

## 4. Cross-Cutting Validation

| Check | Method | Expected | Pass? |
|-------|--------|----------|-------|
| No orphaned MCP refs | `grep -r "mcp__codex_apps" C:\Users\DaveWitkin\.config\opencode\skill\ C:\Users\DaveWitkin\.agents\skills\` | Zero matches across all skills | |
| No orphaned MCP refs (body) | `grep -r "_move_email\|_list_messages\|_fetch_message\|_draft_email\|_search_messages\|destination_well_known_folder" C:\Users\DaveWitkin\.config\opencode\skill\ C:\Users\DaveWitkin\.agents\skills\` | Zero matches in all SKILL.md files | |
| Graph auth works | `Connect-MgGraph` + `Get-MgUserMessage` | Successful connection + data returned | |
| All skills have reference doc | Check `graph-powershell-reference.md` exists | File present at artifacts path | |

---

## 5. Smoke Test Checklist (Run After All Refactoring)

```
[ ] OpenCode starts without errors with current config
[ ] outlook-inbox-triage: Can list and search inbox messages
[ ] email-draft-reply: Can create a draft reply and return webLink
[ ] email-auto-sorter: Can list unread, resolve folders, move messages
[ ] email-to-clickup: Can get message details and archive
[ ] calendar-today: Can show today's events in formatted view
[ ] calendar-schedule: Can create, update, and delete events
[ ] Google MCP: Server starts (after installation)
[ ] Google Gmail: Can list and read messages (after installation)
[ ] Google Calendar: Can list events (after installation)
```
