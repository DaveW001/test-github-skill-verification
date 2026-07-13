# Microsoft Graph PowerShell Search Reference

## 1. Broad Full-Text Search (Recommended)
Use `$search` to find keywords across subjects and bodies.

```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$UserId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
$encodedQuery = [System.Uri]::EscapeDataString('"your keyword"')
$uri = "https://graph.microsoft.com/v1.0/me/messages?`$search=$encodedQuery"
$response = Invoke-MgGraphRequest -Method GET -Uri $uri
$response.value | Select-Object subject, receivedDateTime, @{N='sender';E={$_.from.emailAddress.address}}, bodyPreview
```

## 2. Narrow Filter (Fallback)
Use `-Filter` for specific senders or dates.

**Warning:** Combining `contains()` with `-Sort` often fails with "too complex" errors in OData. Keep filters simple.

```powershell
Get-MgUserMessage -UserId "me" -Filter "from/emailAddress/address eq 'sender@example.com'" -Top 10
```

## 3. Targeted Message Fetch
After identifying a message by ID, retrieve full details including body:

```powershell
Get-MgUserMessage -UserId "me" -MessageId $messageId -Property subject,body,from,receivedDateTime
```

## Fallback Sequence
1. Use `$search` via `Invoke-MgGraphRequest` for broad discovery.
2. Narrow locally by sender/date/subject.
3. Use targeted message fetch for body/link extraction.

## Common Failure Modes
- `contains()` combined with `-Sort` → "too complex" error. Solution: use `$search` instead, or filter locally after retrieval.
- `Connect-MgGraph` fails → verify certificate thumbprint `764A4240264B0F302BE55247A9BC4AB1FBD5C357` is installed in CurrentUser\My store. Run `scripts/validate-graph-app-only-auth.ps1` from the email-triage repo.
- `$search` requires URL-encoded query strings → always use `[System.Uri]::EscapeDataString()`.
