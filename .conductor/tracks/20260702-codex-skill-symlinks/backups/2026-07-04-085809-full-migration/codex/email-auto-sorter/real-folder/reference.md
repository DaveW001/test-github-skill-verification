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

### List unread inbox messages
```powershell
Get-MgUserMessage -UserId $userId -Top 20 -Filter "IsRead eq false" -Sort "receivedDateTime desc" -Property "id,subject,from,receivedDateTime"
```

### List mail folders (resolve folder IDs)
```powershell
$folders = Get-MgUserMailFolder -UserId $userId -Property "id,displayName,unreadItemCount"
$targetFolder = $folders | Where-Object { $_.DisplayName -eq 'Inbox Urgent' } | Select-Object -First 1
```

### Move message to folder
```powershell
$movedMsg = Move-MgUserMessage -UserId $userId -MessageId $messageId -DestinationId $folderId
# IMPORTANT: Message ID changes after move. Use $movedMsg.Id for subsequent operations.
```

### Mark message as read
```powershell
Update-MgUserMessage -UserId $userId -MessageId $messageId -BodyParameter @{ IsRead = $true }
# CRITICAL: Must use -BodyParameter, NOT -IsRead $true directly
```

### Critical Gotchas
- **Never use `-UserId me`** — always use full UPN `dave.witkin@packagedagile.com`
- **Session doesn't persist** — `Connect-MgGraph` required at start of every script
- **Must use `-BodyParameter @{ IsRead = $true }`** for mark-as-read
- **Message ID changes after move** — use returned ID
- Full reference: `C:\development\opencode\.conductor\tracks\20260429-email-calendar-mcp-audit\artifacts\graph-powershell-reference.md`
