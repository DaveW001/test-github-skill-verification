# Unified Calendar Today — Tool Reference

## Mixed Execution Layer

This skill uses TWO execution layers:

1. **Microsoft Graph PowerShell** (via `bash`) for Outlook calendar
2. **Google MCP Server** for Google calendar

## Outlook Calendar — Graph PowerShell (via bash)

### Connect (no-WAM app-only auth, no browser prompt)

Must run at the start of every bash invocation:

```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$userId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
```

### Get Today's Events

```powershell
$userId = "dave.witkin@packagedagile.com"
$start = (Get-Date).Date.ToUniversalTime().ToString('s') + 'Z'
$end = (Get-Date).Date.AddDays(1).ToUniversalTime().ToString('s') + 'Z'
Get-MgUserCalendarView -UserId $userId -CalendarId "Calendar" -StartDateTime $start -EndDateTime $end | Select-Object Subject, Start, End, Location, IsAllDay | ConvertTo-Json
```

### Parse Outlook Response

Each event object:
```json
{
  "Subject": "Team Standup",
  "Start": { "DateTime": "2026-04-29T09:00:00", "TimeZone": "UTC" },
  "End": { "DateTime": "2026-04-29T09:30:00", "TimeZone": "UTC" },
  "Location": { "DisplayName": "Zoom" },
  "IsAllDay": false
}
```

### Key Gotchas
- `-UserId me` is broken. Always use full UPN: `dave.witkin@packagedagile.com`
- Graph sessions don't persist across bash invocations. Must `Connect-MgGraph` each time.
- `Start.DateTime` may be in UTC — convert to local time for display.

## Google Calendar — Google MCP Server

### list-calendars

```json
{}
```

Returns array with `id`, `summary`, `primary`.

### list-events

```json
{
  "calendarId": "primary",
  "timeMin": "2026-04-29T00:00:00Z",
  "timeMax": "2026-04-30T00:00:00Z",
  "timeZone": "America/New_York"
}
```

Returns array of event objects:
```json
{
  "id": "evt123",
  "summary": "Design Sync",
  "start": { "dateTime": "2026-04-29T11:00:00-04:00" },
  "end": { "dateTime": "2026-04-29T12:00:00-04:00" },
  "location": "Google Meet"
}
```

### get-freebusy

```json
{
  "timeMin": "2026-04-29T00:00:00Z",
  "timeMax": "2026-04-30T00:00:00Z",
  "timeZone": "America/New_York",
  "items": [{"id": "dave.witkin@packagedagile.com"}]
}
```

## Time Conversion Reference

| Local (Eastern) | UTC |
|-----------------|-----|
| 00:00 EDT | 04:00Z |
| 09:00 EDT | 13:00Z |
| 12:00 EDT | 16:00Z |
| 17:00 EDT | 21:00Z |
| 23:59 EDT | 03:59Z+1 |

User's timezone: `America/New_York` (UTC-5 EST / UTC-4 EDT)
