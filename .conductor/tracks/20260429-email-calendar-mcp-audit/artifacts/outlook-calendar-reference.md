# Outlook Calendar Graph PowerShell Reference

> **Date:** 2026-04-29 | **Account:** dave.witkin@packagedagile.com | **Modules:** Microsoft.Graph.Calendar 2.29.1, Microsoft.Graph.Users 2.29.1

---

## Authentication

### Required Scopes
```
Calendars.Read, Calendars.ReadWrite
```

### Connection Pattern
```powershell
Connect-MgGraph -Scopes "Calendars.Read","Calendars.ReadWrite" -NoWelcome
Start-Sleep -Seconds 2
```

**CRITICAL:** Session does NOT persist across `pwsh` invocations. Every script must call `Connect-MgGraph` at the start.

---

## Common Variables

All cmdlets below use `$userId = "dave.witkin@packagedagile.com"`.

**CRITICAL:** `-UserId me` does NOT work. You must use the full UPN.

---

## Calendar Operations

### Op C.1: List Today's Calendar Events

```powershell
$start = (Get-Date).Date.ToUniversalTime().ToString('s') + 'Z'
$end = (Get-Date).Date.AddDays(1).ToUniversalTime().ToString('s') + 'Z'

$events = Get-MgUserCalendarView -UserId $userId `
    -StartDateTime $start `
    -EndDateTime $end `
    -Property "id,subject,start,end,organizer,location,isAllDay"
```

**Key properties:**
- `$evt.Subject` - Event title
- `$evt.Start.DateTime` - Start time string
- `$evt.End.DateTime` - End time string
- `$evt.Location.DisplayName` - Location name/URL
- `$evt.Organizer.EmailAddress.Address` - Organizer
- `$evt.IsAllDay` - Boolean

### Op C.2: Get Event Details (body, attendees)

```powershell
$event = Get-MgUserEvent -UserId $userId -EventId $eventId `
    -Property "id,subject,body,start,end,attendees,location,organizer,webLink"
```

**Key properties:**
- `$event.Body.Content` - Full HTML body
- `$event.Attendees` - Array with `.EmailAddress.Address` and `.Status.Response`
- `$event.Location.DisplayName` - Location
- `$event.WebLink` - Direct Outlook Web link

### Op C.3: Create New Event

```powershell
$eventBody = @{
    subject = "Event Title"
    body = @{
        contentType = "HTML"
        content = "<p>Event description</p>"
    }
    start = @{
        dateTime = "2026-05-06T14:00:00"
        timeZone = "Eastern Standard Time"
    }
    end = @{
        dateTime = "2026-05-06T15:00:00"
        timeZone = "Eastern Standard Time"
    }
    location = @{
        displayName = "Virtual"
    }
    attendees = @(
        @{
            emailAddress = @{ address = "attendee@example.com" }
            type = "required"
        }
    )
}
$newEvent = New-MgUserEvent -UserId $userId -BodyParameter $eventBody
```

**CRITICAL:** Must use `-BodyParameter` hashtable. Named params like `-StartDateTime` do NOT work.

### Op C.4: Update Event

```powershell
$updateBody = @{
    subject = "Updated Title"
    start = @{
        dateTime = "2026-05-06T15:00:00"
        timeZone = "Eastern Standard Time"
    }
}
Update-MgUserEvent -UserId $userId -EventId $eventId -BodyParameter $updateBody
```

### Op C.5: Delete/Cancel Event

```powershell
Remove-MgUserEvent -UserId $userId -EventId $eventId
```

### Op C.6: Find Available Time Slots

**No dedicated cmdlet exists** in Microsoft.Graph.Calendar 2.29.1. Use `Invoke-MgGraphRequest`:

```powershell
$scheduleBody = @{
    Schedules = @($userId)
    StartTime = @{
        dateTime = "2026-04-29T09:00:00"
        timeZone = "Eastern Standard Time"
    }
    EndTime = @{
        dateTime = "2026-04-29T17:00:00"
        timeZone = "Eastern Standard Time"
    }
    availabilityViewInterval = 30
}
$json = $scheduleBody | ConvertTo-Json -Depth 5
$result = Invoke-MgGraphRequest -Method POST `
    -Uri "https://graph.microsoft.com/v1.0/users/$userId/calendar/getSchedule" `
    -Body $json `
    -ContentType "application/json"
```

**AvailabilityView encoding:** Each character = 30 min slot. `0`=free, `1`=tentative, `2`=busy, `3`=out of office, `4`=working elsewhere.

---

## Gotchas & Limitations

### 1. `-UserId me` is Broken
`-UserId "me"` returns error: `TargetIdShouldNotBeMeOrWhitespace`. Always use the full UPN: `dave.witkin@packagedagile.com`.

### 2. `-BodyParameter` Required for Complex Updates
These cmdlets do NOT accept simple named params for complex properties:
- `New-MgUserEvent`   must use `-BodyParameter @{...}`
- `Update-MgUserEvent`   must use `-BodyParameter @{...}`

### 3. `Get-MgUserDefaultCalendarSchedule` Does Not Exist
Despite being in some documentation, this cmdlet does NOT exist in module v2.29.1. Use `Invoke-MgGraphRequest` with the `/calendar/getSchedule` endpoint.
