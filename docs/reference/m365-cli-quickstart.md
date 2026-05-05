# M365 CLI Operator Quickstart

**Track ID**: 20260315-ms365-mcp-to-cli-migration

This guide provides the standard command patterns for Microsoft 365 operations following the move from MCP to CLI.

---

## 0. Critical: OpenCode Agent Execution Model

**Every `bash` tool call creates a new PowerShell process.** Graph authentication sessions do NOT persist between calls. You MUST connect to Graph and perform your operation in a **single bash command**. This is the #1 gotcha.

```
# WRONG - auth lost between calls
bash: Connect-MgGraph ...
bash: Get-MgUserMessage ...  ← FAILS: "Authentication needed"

# RIGHT - everything in one command
bash: . connect-graph-no-wam.ps1; Connect-GraphNoWam ...; Get-MgUserMessage ...
```

**Never use `Connect-MgGraph -Scopes ...` (delegated/interactive) in an agent session.** It requires a browser popup. Also avoid direct `Connect-MgGraph -CertificateThumbprint` in agent sessions: on this workstation it authenticated as AppOnly but still triggered Microsoft WAM account-picker popups. Always use the no-WAM app-only wrapper below.

---

## 1. Authentication (App-Only Cert, No WAM)

### Standard wrapper

Use this wrapper for all agent-driven Microsoft Graph work:

```
C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1
```

It bypasses MSAL/WAM token acquisition by minting an OAuth2 client-credentials token via REST with a certificate-signed JWT assertion, then calls `Connect-MgGraph -AccessToken` with a `SecureString`. This prevents account-picker popups while preserving Dave's normal browser-based ability to choose Microsoft accounts manually.

### Auth Constants (copy these into your script)

```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"  # daily-priority-briefing-graph
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$UserId         = "dave.witkin@packagedagile.com"
```

### Connection (must be in same command as your operations)

```powershell
. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
```

### Environment variable alternative

If env vars are loaded first (via `C:\development\daily-priority-briefing\scripts\load-dpb-env.ps1`):

```powershell
. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $env:DPB_GRAPH_CLIENT_ID -TenantId $env:DPB_GRAPH_TENANT_ID -CertThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT
```

### What works vs what doesn't

| Method | Works in Agent? | Why |
|--------|----------------|-----|
| `Connect-GraphNoWam -ClientId ... -CertThumbprint ...` | ✅ Yes | App-only, bypasses MSAL/WAM |
| `Connect-MgGraph -ClientId ... -CertificateThumbprint ...` | ⚠️ Avoid | Can still trigger WAM account picker on this workstation |
| `Connect-MgGraph -Scopes "Mail.Read"` | ❌ No | Opens browser for delegated auth |
| `Connect-MgGraph -UseDeviceCode` | ❌ No | Requires user to visit URL in browser |
| Reusing auth from user's PowerShell | ❌ No | Token cache is session-scoped, not shared |

### App permissions

The `daily-priority-briefing-graph` app has these **Application** permissions (admin-consented):

- `Mail.Read` — read all mailboxes in scoped group
- `Calendars.Read` — read calendars
- `User.Read.All` — read user profiles

App is restricted to scoped mailboxes via Exchange Application Access Policy (group: `dpb-graph-scoped-mailboxes`, member: `dave.witkin@packagedagile.com`).

---

## 2. Mailbox Operations

### Search Messages by Subject Keywords (the most common agent task)

```powershell
# Single-topic search
$filter = [System.Uri]::EscapeDataString("receivedDateTime ge 2026-01-01T00:00:00Z and contains(subject, 'OIP')")
$uri = "https://graph.microsoft.com/v1.0/users/$UserId/messages?`$filter=$filter&`$top=50&`$select=subject,receivedDateTime,from,toRecipients,body,conversationId"
$result = Invoke-MgGraphRequest -Method GET -Uri $uri
$result.value | ForEach-Object { $_.subject }
```

### Multi-topic search with deduplication

For extracting emails matching many topics, use the reusable script:

```
C:\Users\DaveWitkin\.config\opencode\skills\microsoft-graph\scripts\search-outlook-messages.ps1
```

Usage:
```powershell
. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
& "C:\Users\DaveWitkin\.config\opencode\skills\microsoft-graph\scripts\search-outlook-messages.ps1" `
    -Topics @("OIP","Trilogy","Tribility","Agile") `
    -StartDate "2026-01-29" -EndDate "2026-04-29" `
    -OutputPath "C:\development\02-Kx-to-process\10 inbox\outlook_export.md"
```

### List Folders for a User
```powershell
Get-MgUserMailFolder -UserId $UserId -Top 20 | Select-Object DisplayName, Id | Format-Table
```

### Move a Message
```powershell
$messageId = "AAMkAGU4NTQ1NTVk..."
$destFolderId = "AAMkAGU4NTQ1NTVk..."
Move-MgUserMessage -UserId $UserId -MessageId $messageId -DestinationId $destFolderId
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
Send-MgUserMail -UserId $UserId -BodyParameter $params
```

---

## 3. Calendar & Meetings (`Calendars.Read`)

### List Calendar Events
```powershell
Get-MgUserCalendarEvent -UserId $UserId -Top 5 | Select-Object Subject, Start, End
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
New-MgUserCalendarEvent -UserId $UserId -BodyParameter $params
```

---

## 4. OneDrive & Files (`Files.Read.All`)

### Search for Files
```powershell
Get-MgUserDriveSearch -UserId $UserId -Q "Strategy" | Select-Object Name, WebUrl
```

### List Root Files
```powershell
Get-MgUserDriveItem -UserId $UserId -DriveId (Get-MgUserDrive -UserId $UserId).Id | Select-Object Name, Size
```

---

## 5. Troubleshooting

| Issue | Likely Cause | Solution |
|---|---|---|
| `Authentication needed` after `Connect-MgGraph` | Auth in different bash call | Put `Connect-MgGraph` AND your operation in the SAME bash command |
| 403 Forbidden | Permission Gap | Ensure App Registration has correct **Application** permissions and **Admin Consent** is granted |
| 400 Bad Request (TargetId) | Using "me" | Replace "me" with UPN (`dave.witkin@packagedagile.com`) in app-only context |
| Auth Failure (Length 40) | Thumbprint format | Ensure thumbprint is 40 hex characters, no spaces |
| Browser popup or device code prompt | Using delegated auth | Use app-only cert auth (`-ClientId ... -CertificateThumbprint ...`), never `-Scopes` |
| Account picker popup even though `AuthType=AppOnly` | MSAL/WAM broker initialized by direct `Connect-MgGraph -CertificateThumbprint` | Use `connect-graph-no-wam.ps1` / `Connect-GraphNoWam`; it uses REST token minting and `Connect-MgGraph -AccessToken` |
| `NO_CONTEXT` after `Connect-MgGraph` | Silent auth failure | Add `-ErrorAction Stop` and wrap in try/catch to surface the real error |
| `Get-MgUserMessage` fails but `Invoke-MgGraphRequest` works | SDK module not imported in same session | Prefer `Invoke-MgGraphRequest` for reliability in agent context |
| Empty results on search | `$filter` not URL-encoded | Use `[System.Uri]::EscapeDataString($filter)` for filter values |

---

## 6. Key Reference Files

| File | Purpose |
|------|---------|
| `C:\development\daily-priority-briefing\config\dpb-runtime.env` | Auth credentials (ClientId, TenantId, CertThumbprint, UserId) |
| `C:\development\daily-priority-briefing\config\graph-app-registration.json` | Full app registration metadata, permissions, cert details |
| `C:\development\daily-priority-briefing\scripts\load-dpb-env.ps1` | Loads env vars from dpb-runtime.env |
| `C:\development\daily-priority-briefing\scripts\get-graph-app-token.ps1` | Manual token minting (JWT assertion) |
| `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1` | Standard no-WAM Graph auth wrapper for agents |
| `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1` | Production example: app-only auth + message search + move |
| `C:\development\email-triage\MICROSOFT-EMAIL-ACCESS-INVENTORY-2026-04-19.md` | Full inventory of all email access paths |
| `C:\Users\DaveWitkin\.config\opencode\skills\microsoft-graph\scripts\search-outlook-messages.ps1` | Reusable search-and-export script |

---

## 7. Rollback

To restore the M365 MCP server:
1. Copy backup from `.conductor/tracks/20260315-ms365-mcp-to-cli-migration/artifacts/opencode.json.backup-pre-migration`
2. Overwrite `C:\Users\DaveWitkin\.config\opencode\opencode.json`
