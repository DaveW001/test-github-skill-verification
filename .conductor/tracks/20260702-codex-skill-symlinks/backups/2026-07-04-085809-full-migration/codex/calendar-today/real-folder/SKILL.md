---
tool_context:
  with_tools: [bash]
name: calendar-today
description: Show today's Outlook calendar schedule with times, titles, locations, and conflicts. Use when the user asks "what's on my calendar", "what do I have today", "show my schedule", or wants a quick view of upcoming meetings.
triggers:
  intent:
    - calendar overview
    - daily schedule
    - upcoming meetings
  user_phrases:
    - what's on my calendar today
    - what do I have today
    - show my schedule
    - what meetings do I have
    - am I free at 3pm
    - what's coming up next
  execution_layer: graph-powershell
  cmdlets: [Get-MgUserCalendarView, Get-MgUserEvent, Invoke-MgGraphRequest]
  priority: normal
  suggest_only: false
---

# Calendar Today

Show today's Outlook calendar schedule in a clean, scannable format. Flag conflicts, back-to-back meetings, and upcoming events.

## Graph PowerShell Execution

### Connect (required every invocation — no-WAM app-only auth, no browser prompt)
```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$userId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
```

### Get today's events
```powershell
$today = Get-Date -Format 'yyyy-MM-dd'
$tomorrow = (Get-Date).AddDays(1).ToString('yyyy-MM-dd')

$events = Get-MgUserCalendarView -UserId $userId `
    -StartDateTime "${today}T00:00:00" `
    -EndDateTime "${tomorrow}T00:00:00" `
    -Property "id,subject,start,end,organizer,location,isAllDay,webLink" `
    -Sort "start/dateTime"
```

### Get event details (body, attendees)
```powershell
$event = Get-MgUserEvent -UserId $userId -EventId $eventId `
    -Property "id,subject,body,start,end,attendees,location,organizer,webLink"
```

### Check availability for a specific time
```powershell
$scheduleBody = @{
    Schedules = @($userId)
    StartTime = @{
        dateTime = "2026-04-29T15:00:00"
        timeZone = "Eastern Standard Time"
    }
    EndTime = @{
        dateTime = "2026-04-29T16:00:00"
        timeZone = "Eastern Standard Time"
    }
    availabilityViewInterval = 30
}
$json = $scheduleBody | ConvertTo-Json -Depth 5
$result = Invoke-MgGraphRequest -Method POST `
    -Uri "https://graph.microsoft.com/v1.0/users/$userId/calendar/getSchedule" `
    -Body $json -ContentType "application/json"
# AvailabilityView: 0=free, 1=tentative, 2=busy, 3=out of office, 4=working elsewhere
```

### Key properties per event
- `$evt.Subject` — Event title
- `$evt.Start.DateTime` — Start time (string like "2026-04-29T14:00:00")
- `$evt.End.DateTime` — End time
- `$evt.Location.DisplayName` — Location or meeting link
- `$evt.Organizer.EmailAddress.Address` — Organizer
- `$evt.IsAllDay` — Boolean
- `$evt.WebLink` — Direct Outlook Web link

### Critical Gotchas
- **Never use `-UserId me`** — always use full UPN `dave.witkin@packagedagile.com`
- **Session doesn't persist** — `Connect-MgGraph` required at start of every script
- **`Get-MgUserDefaultCalendarSchedule` doesn't exist** — use `Invoke-MgGraphRequest` with `/calendar/getSchedule`
- Full reference: `C:\development\opencode\.conductor\tracks\20260429-email-calendar-mcp-audit\artifacts\graph-powershell-reference.md`

## Workflow

1. **Fetch today's events** using `Get-MgUserCalendarView`.
2. **Format output** as a clean schedule view:
   ```
   Today's Schedule — Wednesday, April 29, 2026

   09:00 – 09:30  ☕ Daily Standup (Virtual)
   10:00 – 11:00  📊 Q3 Planning Review (Conf Room A)
   11:00 – 11:30  ⚡ BACK-TO-BACK with Q3 Planning
   13:00 – 14:00  🔧 Technical Design Review
   15:00 – 15:30  ✅ Free slot available
   16:00 – 17:00  📞 Client Call — Acme Corp

   Summary: 5 meetings | 2 flags | Next free slot: 3:00 PM
   ```
3. **Flag issues:**
   - Back-to-back meetings (no break between)
   - Conflicts (overlapping events)
   - All-day events
   - Meetings without locations
4. **Show upcoming events** — highlight the next meeting within the next 2 hours.
5. **Answer follow-up questions** — "am I free at 3pm?", "when's my next break?"

## Output Format

Default to the schedule view above. If the user asks about a specific event, show:
- Full title and time
- Location/meeting link
- Organizer
- Attendees (if asked)
- Brief body summary (if asked)

## Guardrails

- Do not modify or delete events with this skill — use `calendar-schedule` for that.
- Do not show declined events unless the user asks.
- If the calendar is empty, say so plainly (don't fabricate meetings).
- Respect timezone — all times in Eastern (user's local timezone).

## Related Skills

- **calendar-schedule** — Create, update, or cancel meetings. Use when the user wants to schedule something new.
- **outlook-inbox-triage** — Email triage for meeting-related emails that may need scheduling follow-up.
