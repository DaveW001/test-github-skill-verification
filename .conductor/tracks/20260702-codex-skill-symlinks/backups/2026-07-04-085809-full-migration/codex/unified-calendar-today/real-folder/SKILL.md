---
tool_context:
  with_tools: [bash]
name: unified-calendar-today
description: Show today's combined schedule across both Outlook and Google calendars with conflict detection. Use when the user asks "what's on my calendar today" without specifying Outlook or Google, or says "show all my meetings", "full schedule", or "combined calendar".
triggers:
  intent:
    - combined calendar overview
    - full daily schedule
    - all meetings today
    - cross-platform calendar
  user_phrases:
    - what's on my calendar today
    - show all my meetings
    - full schedule today
    - combined calendar view
    - what do I have today across both calendars
    - am I free at 3pm
  execution_layer: mixed
  priority: normal
  suggest_only: false
---

# Unified Calendar Today

Show today's combined schedule across both Outlook and Google calendars. Detect cross-platform conflicts and present one unified view.

## Why Unified

The user has two primary calendar systems:
- **Outlook** (`dave.witkin@packagedagile.com`) — via Microsoft Graph PowerShell
- **Google** (`dave.witkin@packagedagile.com`) — via Google MCP server

This skill queries both and merges the results into a single chronological view.

## Workflow

### Step 1: Query Outlook Calendar (via Graph PowerShell)

Run via `bash`:

```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$userId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
$start = (Get-Date).Date.ToUniversalTime().ToString('s') + 'Z'
$end = (Get-Date).Date.AddDays(1).ToUniversalTime().ToString('s') + 'Z'
Get-MgUserCalendarView -UserId $userId -CalendarId "Calendar" -StartDateTime $start -EndDateTime $end | Select-Object Subject, Start, End, Location, IsAllDay | ConvertTo-Json
```

Parse the response. Each event has:
- `Subject` → title
- `Start.DateTime` + `Start.TimeZone` → start time
- `End.DateTime` + `End.TimeZone` → end time
- `Location.DisplayName` → location

Tag each event with source: `Outlook`.

### Step 2: Query Google Calendar (via MCP)

Use the `list-events` tool from the Google MCP server:

```json
{
  "calendarId": "primary",
  "timeMin": "2026-04-29T00:00:00Z",
  "timeMax": "2026-04-30T00:00:00Z",
  "timeZone": "America/New_York"
}
```

Parse the response. Each event has:
- `summary` → title
- `start.dateTime` → start time
- `end.dateTime` → end time
- `location` → location

Tag each event with source: `Google`.

### Step 3: Merge & Sort

1. Combine both event lists.
2. Convert all times to the user's local timezone (Eastern / `America/New_York`).
3. Sort chronologically by start time.
4. Detect overlaps between ANY two events regardless of source.

### Step 4: Format Output

```
📅 Unified Calendar — Today (Wed, Apr 29)

  09:00–09:30  Team Standup             📍 Zoom        [Outlook]
  09:30–10:00  Gmail Sync Review        📍 Meet        [Google]
  10:00–11:00  Client Review            📍 Office      [Outlook]
  ⚠️  CONFLICT:
  11:00–12:00  Design Sync              📍 Google Meet [Google]
  11:15–12:00  Vendor Call              📍 Phone       [Outlook]
  14:00–15:00  1:1 with Sarah           📍 Zoom        [Outlook]
  16:00–16:30  Gmail Follow-up          📍 Meet        [Google]
  ---
  7 events · 1 conflict · Next free: 12:00–14:00
  Sources: 4 Outlook · 3 Google
```

### Step 5: Conflict Detection

Two events conflict if:
- Event A ends after Event B starts AND Event A starts before Event B ends.

Check across ALL events regardless of source. Flag each pair of conflicting events.

## Time Handling

- User's timezone: `America/New_York` (Eastern)
- All queries use UTC for API calls
- Display in local time
- Outlook: use `ToUniversalTime()` for query, parse response timezone
- Google: use `timeZone: "America/New_York"` in the response

## Guardrails

- Read-only — do not create, modify, or delete events. Direct the user to `calendar-schedule` or `google-calendar-schedule`.
- If one source fails, show the other and note the failure.
- Do not expose attendee email addresses unless asked.

## Fallback Behavior

- If Outlook Graph auth fails: show Google-only results with a note.
- If Google MCP is unavailable: show Outlook-only results with a note.
- If both fail: report the error and suggest manual calendar check.

## Related Skills

- **calendar-today** — Outlook-only calendar view.
- **google-calendar-today** — Google-only calendar view.
- **calendar-schedule** — Schedule Outlook events.
- **google-calendar-schedule** — Schedule Google events.

For tool names and parameters, see [reference.md](reference.md).
