# Reference

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
$start = (Get-Date).Date.ToUniversalTime().ToString('s') + 'Z'
$end = (Get-Date).Date.AddDays(1).ToUniversalTime().ToString('s') + 'Z'

$events = Get-MgUserCalendarView -UserId $userId `
    -StartDateTime $start `
    -EndDateTime $end `
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
