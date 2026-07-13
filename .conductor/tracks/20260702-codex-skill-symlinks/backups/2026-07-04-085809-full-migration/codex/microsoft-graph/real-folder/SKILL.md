---
tool_context:
  with_tools: [bash]
name: microsoft-graph
description: "Reusable Microsoft Graph PowerShell patterns for reading email, calendar, and OneDrive via app-only certificate authentication. Use when the user mentions Outlook, email, calendar, OneDrive, Microsoft Graph, or Exchange operations via PowerShell."
triggers:
  intent:
    - graph powershell auth
    - app-only certificate auth
  user_phrases:
    - graph auth
    - graph connection
    - connect to graph
---

# Microsoft Graph PowerShell

## When to Use
- Any task requiring Outlook email search, read, or export
- Calendar event listing or creation
- OneDrive file operations
- Bulk mailbox operations (move, sort, triage)

## Critical: Agent Execution Model
Every `bash` tool call creates a new PowerShell process. You **MUST** connect to Graph and perform your operation in a **single bash command**. Auth does not persist between calls.

## Authentication
Always use app-only certificate authentication through the no-WAM wrapper. Do **not** use `Connect-MgGraph -CertificateThumbprint` directly in agent sessions.

### Why the wrapper is required
On 2026-05-04, `Connect-MgGraph -ClientId ... -CertificateThumbprint ...` successfully authenticated as `AppOnly`, but still triggered Microsoft Web Account Manager (WAM) account-picker popups because the workstation has multiple Microsoft accounts. Persistent env vars (`MSAL_DISABLE_WAM=true`, `AZURE_PS_DISABLE_WAM=true`, `MSAL_ENABLE_WAM=false`) did not reliably suppress the popup.

The final working solution was to bypass MSAL/WAM entirely: mint the app-only Graph token via OAuth2 REST with a certificate-signed JWT assertion, convert it to `SecureString`, then call `Connect-MgGraph -AccessToken`. Use `scripts/connect-graph-no-wam.ps1` for that flow.

This does **not** affect Dave's normal browser sign-in or manual Microsoft account picker behavior. It only affects programmatic PowerShell Graph connections.

```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$UserId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint

# Perform Graph work in the SAME bash command / PowerShell process.
Get-MgUserMessage -UserId $UserId -Top 1 -Property Subject,ReceivedDateTime
```

## Scripts
- `scripts/connect-graph-no-wam.ps1` — Standard non-interactive no-WAM Graph auth wrapper
- `scripts/search-outlook-messages.ps1` — Search messages by subject keywords and export as Markdown

## Reference
- Full quickstart: `C:\development\opencode\docs\reference\m365-cli-quickstart.md`
- App registration: `C:\development\daily-priority-briefing\config\graph-app-registration.json`
- Runtime env: `C:\development\daily-priority-briefing\config\dpb-runtime.env`
- Production example: `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
- Access inventory: `C:\development\email-triage\MICROSOFT-EMAIL-ACCESS-INVENTORY-2026-04-19.md`

## Permission Status (as of 2026-05-08)

### SharePoint access: RESOLVED ✅
The app registration `daily-priority-briefing-graph` (Client ID: `23040dc9-20db-4645-99f7-71ba5e79b35e`) has these scopes:
- `Calendars.Read` ✅
- `Mail.Read` ✅
- `User.Read.All` ✅
- `Sites.Read.All` ✅ — SharePoint site enumeration, document library access, and file listing all validated 2026-05-08

**Validated against**: Packaged Agile root site, Delivery site (`/sites/Delivery`), and document library folder listing.

**Historical note**: This permission was missing until 2026-05-08. If SharePoint access fails again, check that `Sites.Read.All` is still granted in Entra ID → API permissions.
