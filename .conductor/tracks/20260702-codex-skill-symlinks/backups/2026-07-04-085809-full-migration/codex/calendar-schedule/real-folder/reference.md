# Reference

## Graph PowerShell Execution

### Connect (required every invocation â€” no-WAM app-only auth, no browser prompt)
```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$userId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
```

### Create new event
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
# CRITICAL: Must use -BodyParameter hashtable. Named params like -StartDateTime do NOT work.
```

### Create a non-blocking marker event

Use this pattern for reminders or location/context markers that should appear on the calendar but should not block availability.

Requirements:
- Set `start.dateTime` and `end.dateTime` to the same timestamp for a 0-minute event.
- Set `showAs = "free"`.
- Set `isAllDay = $false`.

Example:
```powershell
$markerBody = @{
    subject = "DC Co-Working Day 1 - Scrum Inc. Georgetown"
    body = @{
        contentType = "HTML"
        content = "<p>Reminder marker only. Does not block availability.</p>"
    }
    start = @{
        dateTime = "2026-05-12T09:00:00"
        timeZone = "Eastern Standard Time"
    }
    end = @{
        dateTime = "2026-05-12T09:00:00"
        timeZone = "Eastern Standard Time"
    }
    location = @{
        displayName = "Scrum Inc. Georgetown Office"
    }
    showAs = "free"
    isAllDay = $false
}

New-MgUserEvent -UserId $userId -BodyParameter $markerBody
```

### Find available time slots
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
    -Body $json -ContentType "application/json"
# AvailabilityView: each char = 30 min. 0=free, 1=tentative, 2=busy, 3=OOO, 4=working elsewhere
```

### Update existing event
```powershell
$updateBody = @{
    subject = "Updated Title"
    start = @{
        dateTime = "2026-05-06T15:00:00"
        timeZone = "Eastern Standard Time"
    }
    end = @{
        dateTime = "2026-05-06T16:00:00"
        timeZone = "Eastern Standard Time"
    }
}
Update-MgUserEvent -UserId $userId -EventId $eventId -BodyParameter $updateBody
# CRITICAL: Must use -BodyParameter for complex properties
```

### Delete/cancel event
```powershell
Remove-MgUserEvent -UserId $userId -EventId $eventId
```

### Get event details (to confirm before modifying)
```powershell
$event = Get-MgUserEvent -UserId $userId -EventId $eventId `
    -Property "id,subject,start,end,attendees,location,organizer,webLink"
```

### Create event with rich HTML body and online meeting details

For events with Zoom/Teams links, meeting context, and multiple attendees â€” write the script to a temp file and execute it (see Execution Pattern below).

```powershell
$bodyHtml = @"
<p>Meeting description with <strong>formatting</strong>.</p>
<p><a href="https://zoom.us/j/123456">Join Zoom</a><br/>
Passcode: abc123</p>
"@

$eventBody = @{
    subject = "Meeting Title"
    body = @{
        contentType = "HTML"
        content = $bodyHtml
    }
    start = @{
        dateTime = "2026-05-05T17:15:00"
        timeZone = "Eastern Standard Time"
    }
    end = @{
        dateTime = "2026-05-05T18:00:00"
        timeZone = "Eastern Standard Time"
    }
    location = @{
        displayName = "Zoom Meeting"
    }
    attendees = @(
        @{ emailAddress = @{ address = "person1@example.com" }; type = "required" },
        @{ emailAddress = @{ address = "person2@example.com" }; type = "required" }
    )
}
$newEvent = New-MgUserEvent -UserId $userId -BodyParameter $eventBody
Write-Output "Subject: $($newEvent.Subject)"
Write-Output "Start: $($newEvent.Start.DateTime)"
Write-Output "End: $($newEvent.End.DateTime)"
Write-Output "WebLink: $($newEvent.WebLink)"
```

> **Note:** Do NOT use `isOnlineMeeting = $true` or `onlineMeetingProvider = "teams"` for Zoom meetings - these are Microsoft Teams-specific and will either fail or create a broken Teams meeting. For Zoom events, just put the Zoom link in the HTML body (as shown above).

### Execution Pattern: Script File vs Inline

**Always use the script-file pattern when running Graph PowerShell through the bash tool.**

Inline PowerShell via `powershell -Command "..."` fails with complex hashtables due to variable expansion and escaping conflicts between bash and PowerShell ($, @, backticks).

**Correct pattern:**
1. Write the full PowerShell script to `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\<name>.ps1` using the Write tool
2. Execute with: `powershell -NoProfile -ExecutionPolicy Bypass -File "<path>.ps1"`

**Avoid:**
```
# BAD â€” inline complex hashtables fail due to bash/PowerShell escaping
powershell -NoProfile -Command "$eventBody = @{ ... }"
```

### Critical Gotchas
- **Never use `-UserId me`** â€” always use full UPN `dave.witkin@packagedagile.com`
- **Session doesn't persist** â€” `Connect-MgGraph` required at start of every script
- **Must use `-BodyParameter`** for New-MgUserEvent and Update-MgUserEvent â€” named params do NOT work
- **Timezone** â€” always use "Eastern Standard Time" unless user specifies otherwise
- **Use script files** â€” never pass complex hashtables inline through bash â†’ PowerShell (see Execution Pattern above)
- **HTML entities in here-strings** â€” use `&amp;` for `&` inside @" "@ here-strings in HTML content
- Full reference: `C:\development\opencode\.conductor\tracks\20260429-email-calendar-mcp-audit\artifacts\graph-powershell-reference.md`
