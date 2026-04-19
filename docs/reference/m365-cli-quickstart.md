# M365 CLI Operator Quickstart

**Track ID**: 20260315-ms365-mcp-to-cli-migration

This guide provides the standard command patterns for Microsoft 365 operations following the move from MCP to CLI.

---

## 1. Authentication (App-Only Cert)

Run this once per session to authenticate as the `daily-priority-briefing-graph` app.

```powershell
Connect-MgGraph `
    -ClientId $env:DPB_GRAPH_CLIENT_ID `
    -TenantId $env:DPB_GRAPH_TENANT_ID `
    -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT `
    -NoWelcome
```

---

## 2. Mailbox Operations (`Mail.ReadWrite`, `Mail.Send`)

### List Folders for a User
```powershell
$userId = "dave.witkin@packagedagile.com"
Get-MgUserMailFolder -UserId $userId -Top 20 | Select-Object DisplayName, Id | Format-Table
```

### Move a Message
```powershell
$messageId = "AAMkAGU4NTQ1NTVk..."
$destFolderId = "AAMkAGU4NTQ1NTVk..."
Move-MgUserMessage -UserId $userId -MessageId $messageId -DestinationId $destFolderId
```

### Send an Email
```powershell
$params = @{
    Message = @{
        Subject = "Summary from OpenCode"
        Body = @{
            ContentType = "Text"
            Content = "The junk mail cleanup is complete."
        }
        ToRecipients = @(
            @{ EmailAddress = @{ Address = "dave.witkin@packagedagile.com" } }
        )
    }
}
Send-MgUserMail -UserId $userId -BodyParameter $params
```

---

## 3. Calendar & Meetings (`Calendars.ReadWrite`)

### List Calendar Events
```powershell
Get-MgUserCalendarEvent -UserId $userId -Top 5 | Select-Object Subject, Start, End
```

### Create a Quick Meeting
```powershell
$params = @{
    Subject = "OpenCode Strategy Session"
    Start = @{ DateTime = "2026-03-16T14:00:00"; TimeZone = "Eastern Standard Time" }
    End = @{ DateTime = "2026-03-16T15:00:00"; TimeZone = "Eastern Standard Time" }
    Attendees = @(
        @{ EmailAddress = @{ Address = "assistant@packagedagile.com" }; Type = "Required" }
    )
}
New-MgUserCalendarEvent -UserId $userId -BodyParameter $params
```

---

## 4. OneDrive & Files (`Files.Read.All`)

### Search for Files
```powershell
# Search for files containing "Strategy"
Get-MgUserDriveSearch -UserId $userId -Q "Strategy" | Select-Object Name, WebUrl
```

### List Root Files
```powershell
Get-MgUserDriveItem -UserId $userId -DriveId (Get-MgUserDrive -UserId $userId).Id | Select-Object Name, Size
```

---

## 5. Troubleshooting

| Issue | Likely Cause | Solution |
|---|---|---|
| 403 Forbidden | Permission Gap | Ensure App Registration has correct **Application** permissions and **Admin Consent** is granted. |
| 400 Bad Request (TargetId) | Using "me" | Replace "me" with UPN or GUID in app-only context. |
| Auth Failure (Length 40) | Thumbprint format | Ensure `$env:DPB_GRAPH_CERT_THUMBPRINT` is 40 hex characters. |

---

## 6. Rollback

To restore the M365 MCP server:
1. Copy backup from `.conductor/tracks/20260315-ms365-mcp-to-cli-migration/artifacts/opencode.json.backup-pre-migration`
2. Overwrite `C:\Users\DaveWitkin\.config\opencode\opencode.json`
