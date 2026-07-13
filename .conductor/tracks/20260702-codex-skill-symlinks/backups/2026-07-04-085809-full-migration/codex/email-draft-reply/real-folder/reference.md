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

### Get message for thread context
```powershell
$msg = Get-MgUserMessage -UserId $userId -MessageId $messageId
```

### Create reply draft (preserves thread)
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

### Get draft webLink for user review
`$draft.WebLink` — returns direct Outlook Web URL.

### Critical Gotchas
- **Never use `-UserId me`** — always use full UPN `dave.witkin@packagedagile.com`
- **Session doesn't persist** — `Connect-MgGraph` required at start of every script
- **Must use `-BodyParameter`** for complex params (not named params)
- Full reference: `C:\development\opencode\.conductor\tracks\20260429-email-calendar-mcp-audit\artifacts\graph-powershell-reference.md`
