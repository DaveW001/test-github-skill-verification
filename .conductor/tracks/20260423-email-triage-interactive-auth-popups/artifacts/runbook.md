# Runbook: Email Triage Scheduled Task — Non-Interactive Auth

## Overview

The hourly email auto-sort scheduled task uses Microsoft Graph app-only authentication via certificate credential. This runbook covers setup, verification, incident response, and rollback.

---

## Architecture

| Component | Detail |
|---|---|
| **Scheduled Task** | `\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort` |
| **Script** | `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1` |
| **Auth Mode** | App-only (certificate-based) — no interactive login |
| **Entra App** | `daily-priority-briefing-graph` (AppId: `23040dc9-20db-4645-99f7-71ba5e79b35e`) |
| **Tenant** | `520005c9-0db3-4780-9c20-50fca961f83a` |
| **Certificate** | `CN=daily-priority-briefing-graph`, Thumbprint: `764A4240264B0F302BE55247A9BC4AB1FBD5C357` |
| **Cert Expiry** | March 9, 2029 |
| **Cert Location** | `Cert:\CurrentUser\My` (Windows certificate store) |
| **Mailbox** | `dave.witkin@packagedagile.com` |
| **Trigger** | Every 1 hour (PT1H), starting 2026-04-21 |
| **Logs** | `C:\development\email-triage\logs\` (per-run markdown + `latest-status.md`) |

---

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 10 | Auth/token failure |
| 20 | Permissions/consent failure |
| 30 | Mailbox/folder access failure |
| 40 | Partial failure (some message moves failed) |
| 50 | Config load failure |
| 99 | Unknown/unhandled error |

---

## Verification Commands

```powershell
# Check last run result
Get-ScheduledTaskInfo -TaskPath "\OpenCode\" -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" |
    Select-Object LastRunTime, LastTaskResult, NextRunTime

# Read latest run log
Get-Content (Get-ChildItem "C:\development\email-triage\logs\*_run.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# Check latest status summary
Get-Content "C:\development\email-triage\logs\latest-status.md"

# Manual dry run (non-interactive, no popup)
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\development\email-triage\scripts\hourly-email-auto-sort.ps1"
Write-Output "Exit code: $LASTEXITCODE"
```

---

## Certificate Lifecycle

### Current Certificate

- **Subject**: `CN=daily-priority-briefing-graph`
- **Thumbprint**: `764A4240264B0F302BE55247A9BC4AB1FBD5C357`
- **Valid**: 2026-03-09 to 2029-03-09
- **Store**: `Cert:\CurrentUser\My`

### When Rotation is Needed (before March 2029)

1. Generate new self-signed certificate:
   ```powershell
   $cert = New-SelfSignedCertificate -Subject "CN=daily-priority-briefing-graph" -CertStoreLocation "Cert:\CurrentUser\My" -KeyExportPolicy Exportable -NotAfter (Get-Date).AddYears(3)
   Write-Output "New thumbprint: $($cert.Thumbprint)"
   Write-Output "New expiry: $($cert.NotAfter)"
   ```

2. Upload the new cert to the Entra app registration:
   ```powershell
   Connect-MgGraph -TenantId '520005c9-0db3-4780-9c20-50fca961f83a' -Scopes 'Application.ReadWrite.All' -NoWelcome
   Import-Module Microsoft.Graph.Applications
   # Update with new cert (replace THUMBPRINT with actual value)
   $app = Get-MgApplication -ApplicationId 'aa9be85b-e7d4-41b5-8dc4-dac8647847a4'
   # Use Update-MgApplication to add new keyCredential
   ```

3. Update the script's `$CertThumbprint` variable.

4. Remove the old certificate from both Entra and the cert store.

---

## Incident Triage

### Task returning exit code 10 (auth failure)

- Check if certificate still exists in store: `Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Thumbprint -eq '764A4240264B0F302BE55247A9BC4AB1FBD5C357' }`
- Check if certificate has expired.
- Check if the Entra app registration still has the certificate credential.

### Task returning exit code 20 (permissions failure)

- Verify `Mail.ReadWrite` (Application) permission is still admin-consented on the app.
- Check if any conditional access policies were added that block the app.

### Task returning exit code 30 (mailbox/folder access failure)

- Verify folder IDs in the script still match actual mailbox folders.
- Verify the target user's mailbox is still active and accessible.

### Task returning exit code 40 (partial failure)

- Check individual error messages in the run log for which messages failed to move.
- May be transient; monitor next run.

---

## Rollback Procedure

If the new app-only auth causes issues:

1. Restore the original script from backup:
   ```
   C:\development\opencode\.conductor\tracks\20260423-email-triage-interactive-auth-popups\artifacts\hourly-email-auto-sort-backup-YYYYMMDD-HHMMSS.ps1
   ```
   Copy it back to `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`.

2. Restore the original scheduled task:
   ```
   C:\development\opencode\.conductor\tracks\20260423-email-triage-interactive-auth-popups\artifacts\task-backup-YYYYMMDD-HHMMSS.xml
   ```
   Register it: `Register-ScheduledTask -Xml (Get-Content 'path\to\task-backup.xml' | Out-String) -TaskPath '\OpenCode\' -TaskName 'opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort' -Force`

3. The next scheduled run will use the old delegated interactive auth. **Warning**: popups will resume.

---

## Prerequisites

- Certificate `CN=daily-priority-briefing-graph` must be present in `Cert:\CurrentUser\My` with private key.
- Entra app `daily-priority-briefing-graph` must have `Mail.Read` and `Mail.ReadWrite` application permissions with admin consent.
- Microsoft.Graph.Authentication and Microsoft.Graph.Mail PowerShell modules must be installed.
