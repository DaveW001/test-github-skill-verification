# Reference

## Graph PowerShell Execution

All Outlook operations use **Microsoft Graph PowerShell** cmdlets via `bash`. Key patterns:

### Connect (required every invocation — no-WAM app-only auth, no browser prompt)
```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$UserId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
```

### Get message details for task creation
```powershell
$msg = Get-MgUserMessage -UserId $userId -MessageId $messageId
$subject = $msg.Subject
$body = $msg.Body.Content
$sender = $msg.From.EmailAddress.Address
$webLink = $msg.WebLink
```

### Archive message
```powershell
$folders = Get-MgUserMailFolder -UserId $userId -Property "id,displayName"
$archiveFolder = $folders | Where-Object { $_.DisplayName -eq 'Archive' } | Select-Object -First 1
Move-MgUserMessage -UserId $userId -MessageId $messageId -DestinationId $archiveFolder.Id
```

### Critical Gotchas
- **Never use `-UserId me`** — always use full UPN `dave.witkin@packagedagile.com`
- **Session doesn't persist** — `Connect-MgGraph` required at start of every script
- **Message ID changes after move** — use returned ID for subsequent operations
- Full reference: `C:\development\opencode\.conductor\tracks\20260429-email-calendar-mcp-audit\artifacts\graph-powershell-reference.md`
