# Graph PowerShell Reference for Email & Calendar Skills

> **Date:** 2026-04-29 | **Account:** dave.witkin@packagedagile.com | **Modules:** Microsoft.Graph.Mail 2.29.1, Microsoft.Graph.Calendar 2.29.1, Microsoft.Graph.Users 2.29.1

---

## Authentication

### Required Scopes
```
Mail.Read, Mail.ReadWrite, Mail.Send, Calendars.Read, Calendars.ReadWrite
```

### Connection Pattern
```powershell
Connect-MgGraph -Scopes "Mail.Read","Mail.ReadWrite","Mail.Send","Calendars.Read","Calendars.ReadWrite" -NoWelcome
```

### Verified Auth Result
```
Account: dave.witkin@packagedagile.com
Available Scopes: Application.Read.All, Application.ReadWrite.All, AppRoleAssignment.ReadWrite.All,
  Calendars.Read, Calendars.ReadWrite, Directory.Read.All, email, Files.Read,
  GroupMember.Read.All, Mail.Read, Mail.ReadBasic, Mail.ReadWrite, Mail.Send,
  openid, profile, User.Read.All
```

### Critical Gotcha: Session Persistence
Graph PowerShell sessions do NOT persist across `pwsh` invocations. Every skill script that runs via `bash` must call `Connect-MgGraph` at the start. Add `Start-Sleep -Seconds 2` after connect to avoid transient empty-result issues.

---

## Common Variables

All cmdlets below use `$userId = "dave.witkin@packagedagile.com"`.

**CRITICAL:** `-UserId me` does NOT work. You must use the full UPN (User Principal Name).

---

## Skill 1: outlook-inbox-triage

### Op 1.1: List Recent Inbox Messages

**Cmdlet:**
```powershell
$msgs = Get-MgUserMessage -UserId $userId -Top 10 -Sort "receivedDateTime desc"
```

**With selective properties (faster):**
```powershell
$msgs = Get-MgUserMessage -UserId $userId -Top 10 -Sort "receivedDateTime desc" `
    -Property "id,subject,from,receivedDateTime,isRead,hasAttachments"
```

**Key properties per message:**
- `$m.Id` - Message ID (long base64 string)
- `$m.Subject` - Email subject
- `$m.From.EmailAddress.Address` - Sender email
- `$m.ReceivedDateTime` - Received timestamp (DateTimeOffset)
- `$m.IsRead` - Boolean read status
- `$m.WebLink` - Outlook Web Access URL

**Tested:** ✅ Returns 10 messages with all properties populated.

### Op 1.2: Get Specific Message by ID (including body)

**Cmdlet:**
```powershell
$msg = Get-MgUserMessage -UserId $userId -MessageId $messageId
```

**Key properties:**
- `$msg.Body.Content` - Full HTML/text body
- `$msg.Body.ContentType` - "html" or "text"
- `$msg.From.EmailAddress.Address` - Sender
- `$msg.ToRecipients` - Array of recipients (`.EmailAddress.Address` each)
- `$msg.CcRecipients` - CC recipients array
- `$msg.BccRecipients` - BCC recipients array
- `$msg.ReplyTo` - Reply-to addresses
- `$msg.Subject` - Subject line
- `$msg.WebLink` - Direct Outlook Web link

**Tested:** ✅ Body length 26818 chars returned successfully. WebLink present.

### Op 1.3: Search Messages by Sender/Subject

**By subject substring:**
```powershell
$msgs = Get-MgUserMessage -UserId $userId -Top 20 `
    -Filter "contains(subject, 'search term')"
```

**By exact sender:**
```powershell
$msgs = Get-MgUserMessage -UserId $userId -Top 20 `
    -Filter "from/emailAddress/address eq 'sender@example.com'"
```

**Combined filter:**
```powershell
$msgs = Get-MgUserMessage -UserId $userId -Top 20 `
    -Filter "contains(subject, 'term') and from/emailAddress/address eq 'x@y.com'"
```

**Tested:** ✅ Subject search returns results. Sender search works (may be slow for large mailboxes).

---

## Skill 2: email-draft-reply

### Op 2.1: Get Message (for thread context)

Same as Op 1.2:
```powershell
$msg = Get-MgUserMessage -UserId $userId -MessageId $messageId
```

### Op 2.2: Create Draft Reply

**Reply to existing message (preserves thread):**
```powershell
$replyParams = @{
    UserId = $userId
    MessageId = $originalMessageId
    BodyParameter = @{
        message = @{
            body = @{
                contentType = "HTML"
                content = "<p>Reply body text here.</p>"
            }
        }
    }
}
$draft = New-MgUserMessageReply @replyParams
```

**Standalone draft (no thread):**
```powershell
$draft = New-MgUserMessage -UserId $userId `
    -Subject "Draft Subject" `
    -Body @{ ContentType = "HTML"; Content = "<p>Body text</p>" } `
    -ToRecipients @(@{ EmailAddress = @{ Address = "recipient@example.com" } })
```

**Key draft properties:**
- `$draft.Id` - Draft message ID
- `$draft.Subject` - Auto-prefixed with "RE:" for replies
- `$draft.WebLink` - **Direct Outlook Web link for user review**

**Tested:** ✅ Both reply and standalone draft work. WebLink returns valid Outlook URL.

### Op 2.3: Get Draft webLink

The `webLink` property is returned directly from both `New-MgUserMessageReply` and `New-MgUserMessage`:
```
https://outlook.office365.com/owa/?ItemID=AAMkAG...&exvsurl=1&viewmodel=ReadMessageItem
```

**Tested:** ✅ Valid URL that opens the draft in Outlook Web.

### Cleanup (delete test draft):
```powershell
Remove-MgUserMessage -UserId $userId -MessageId $draft.Id
```

**Tested:** ✅

---

## Skill 3: email-auto-sorter

### Op 3.1: List Unread Inbox Messages

```powershell
$unreadMsgs = Get-MgUserMessage -UserId $userId -Top 20 `
    -Filter "IsRead eq false" `
    -Sort "receivedDateTime desc" `
    -Property "id,subject,from,receivedDateTime"
```

**Tested:** ✅ Returns unread messages with sender, subject, date.

### Op 3.2: List Mail Folders (resolve folder IDs)

```powershell
$folders = Get-MgUserMailFolder -UserId $userId -Property "id,displayName,unreadItemCount,totalItemCount"
```

**Resolved folder IDs for this mailbox:**
| Folder | ID (prefix) | Unread | Total |
|--------|-------------|--------|-------|
| Archive | AAMkAG...SHwNAAA= | 4750 | 73611 |
| Deleted Items | AAMkAG...AAEKAAA= | 30159 | 65446 |
| Drafts | AAMkAG...AAEPAAA= | 0 | 0 |
| Inbox | AAMkAG...AAEMAAA= | 3 | 4 |
| Junk Email | AAMkAG...SHvdAAA= | 1260 | 1263 |
| Sent Items | AAMkAG...AAEJAAA= | 0 | 33309 |
| Snoozed | AAMkAG...TpmkAAA= | 0 | 0 |

**Resolve folder ID by name:**
```powershell
$targetFolder = $folders | Where-Object { $_.DisplayName -eq 'Archive' } | Select-Object -First 1
$folderId = $targetFolder.Id
```

**Tested:** ✅ All folders returned with IDs.

### Op 3.3: Move Message to Folder

```powershell
$movedMsg = Move-MgUserMessage -UserId $userId -MessageId $messageId -DestinationId $folderId
```

**Returns:** New message object with updated ID (ID changes when moved).

**Tested:** ✅ Moved message to Archive and back to Inbox successfully.

### Op 3.4: Mark Message as Read

```powershell
Update-MgUserMessage -UserId $userId -MessageId $messageId -BodyParameter @{ IsRead = $true }
```

**CRITICAL:** Do NOT use `-IsRead $true` directly. Must use `-BodyParameter @{ IsRead = $true }`.

**Tested:** ✅

---

## Skill 4: email-routing-config

**No Microsoft Graph API calls needed.** This skill only reads/writes a local JSON configuration file that defines email routing rules (sender patterns, folder mappings, priority overrides).

**Verified:** ✅ No Graph cmdlets required.

---

## Skill 5: email-to-clickup

### Op 5.1: Get Specific Message (extract task details)

Same as Op 1.2:
```powershell
$msg = Get-MgUserMessage -UserId $userId -MessageId $messageId
```

Extract task-relevant fields:
```powershell
$subject = $msg.Subject
$body = $msg.Body.Content        # Full HTML body
$sender = $msg.From.EmailAddress.Address
$toAddresses = $msg.ToRecipients | ForEach-Object { $_.EmailAddress.Address }
$receivedDate = $msg.ReceivedDateTime
```

### Op 5.2: Move/Archive Message

Same as Op 3.3:
```powershell
Move-MgUserMessage -UserId $userId -MessageId $messageId -DestinationId $archiveFolderId
```

---

## Calendar Operations (Future Skills)

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

**Tested:** ✅ Returned 10 events for today with all properties.

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

**Tested:** ✅ Full event details including body and attendees.

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

**Tested:** ✅ Created, returns ID and WebLink.

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

**Tested:** ✅ Updated subject successfully.

### Op C.5: Delete/Cancel Event

```powershell
Remove-MgUserEvent -UserId $userId -EventId $eventId
```

**Tested:** ✅ Deleted successfully.

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

**Tested:** ✅ Returns 16-character availability string (08:00-16:00 in 30-min slots).

---

## Gotchas & Limitations

### 1. `-UserId me` is Broken
`-UserId "me"` returns error: `TargetIdShouldNotBeMeOrWhitespace`. Always use the full UPN: `dave.witkin@packagedagile.com`.

### 2. Session Does Not Persist
Each `pwsh -File` invocation is a fresh process. `Connect-MgGraph` must be called at the start of every script. Add `Start-Sleep -Seconds 2` after connect.

### 3. Intermittent Empty Results with `-Top 1`
When `-Top 1` returns a single object, PowerShell may not properly enumerate it. Use `-Top 2` and iterate:
```powershell
$msgs = @(Get-MgUserMessage -UserId $userId -Top 2 -Sort "receivedDateTime desc")
$msg = $msgs | Where-Object { $_.Id } | Select-Object -First 1
```

### 4. `-BodyParameter` Required for Complex Updates
These cmdlets do NOT accept simple named params for complex properties:
- `New-MgUserEvent` → must use `-BodyParameter @{...}`
- `Update-MgUserEvent` → must use `-BodyParameter @{...}`
- `Update-MgUserMessage` → must use `-BodyParameter @{ IsRead = $true }` for mark-as-read

### 5. `Get-MgUserDefaultCalendarSchedule` Does Not Exist
Despite being in some documentation, this cmdlet does NOT exist in module v2.29.1. Use `Invoke-MgGraphRequest` with the `/calendar/getSchedule` endpoint.

### 6. Message ID Changes on Move
When a message is moved to a different folder via `Move-MgUserMessage`, the returned object has a **new ID**. Use the new ID for subsequent operations.

### 7. HTML Body Content
`$msg.Body.Content` returns raw HTML (including `<html>`, `<head>`, styles). For display/summary, you'll need to strip HTML tags or extract text content.

---

## Skill-to-Cmdlet Quick Reference

| Skill | Operation | Cmdlet | Status |
|-------|-----------|--------|--------|
| S1: triage | List messages | `Get-MgUserMessage` | ✅ |
| S1: triage | Get message by ID | `Get-MgUserMessage -MessageId` | ✅ |
| S1: triage | Search by subject | `Get-MgUserMessage -Filter "contains(subject,...)"` | ✅ |
| S1: triage | Search by sender | `Get-MgUserMessage -Filter "from/emailAddress/address eq ..."` | ✅ |
| S2: reply | Get thread message | `Get-MgUserMessage -MessageId` | ✅ |
| S2: reply | Create reply draft | `New-MgUserMessageReply -BodyParameter` | ✅ |
| S2: reply | Create standalone draft | `New-MgUserMessage` | ✅ |
| S2: reply | Get draft webLink | `$draft.WebLink` | ✅ |
| S3: sorter | List unread messages | `Get-MgUserMessage -Filter "IsRead eq false"` | ✅ |
| S3: sorter | List mail folders | `Get-MgUserMailFolder` | ✅ |
| S3: sorter | Move message | `Move-MgUserMessage -DestinationId` | ✅ |
| S3: sorter | Mark as read | `Update-MgUserMessage -BodyParameter @{IsRead=$true}` | ✅ |
| S4: routing | (none - JSON config only) | N/A | ✅ |
| S5: to-clickup | Get message details | `Get-MgUserMessage -MessageId` | ✅ |
| S5: to-clickup | Archive message | `Move-MgUserMessage -DestinationId` | ✅ |
| Calendar | List events | `Get-MgUserCalendarView` | ✅ |
| Calendar | Get event details | `Get-MgUserEvent -EventId` | ✅ |
| Calendar | Create event | `New-MgUserEvent -BodyParameter` | ✅ |
| Calendar | Update event | `Update-MgUserEvent -BodyParameter` | ✅ |
| Calendar | Delete event | `Remove-MgUserEvent` | ✅ |
| Calendar | Find free slots | `Invoke-MgGraphRequest` (getSchedule) | ✅ |
