# Microsoft Graph WAM Account Picker During App-Only Auth

**Status:** Active troubleshooting note / remediation plan  
**Discovered:** 2026-05-04  
**Primary fix:** `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1`

## What Happened

OpenWork tested the existing Microsoft Graph PowerShell pattern:

```powershell
Connect-MgGraph -ClientId $ClientId -TenantId $TenantId -CertificateThumbprint $CertThumbprint -NoWelcome
```

The command successfully connected with:

- `AuthType: AppOnly`
- `TokenCredentialType: ClientCertificate`
- App name: `daily-priority-briefing-graph`

However, Dave still received Microsoft Web Account Manager (WAM) account-picker popups. One popup showed only the Packaged Agile account; a second popup showed both the Packaged Agile account and a W Consulting account. The user had to choose an account and saw “authentication complete.”

This means direct `Connect-MgGraph -CertificateThumbprint` is **not safe for unattended agent use on this workstation**, even when the resulting Graph context is app-only.

## What Did Not Fully Fix It

OpenWork set these user-level environment variables and also tested setting them in-process:

```powershell
MSAL_DISABLE_WAM=true
AZURE_PS_DISABLE_WAM=true
MSAL_ENABLE_WAM=false
```

These variables are safe and may help in some contexts, but they did **not** reliably suppress the account picker for direct Microsoft Graph PowerShell certificate auth.

Important: these variables only affect programmatic PowerShell/MSAL behavior. They do **not** remove Dave's ability to manually choose accounts in a normal browser session.

## Final Working Solution

Bypass MSAL/WAM token acquisition entirely:

1. Load the certificate from `Cert:\CurrentUser\My`.
2. Create a JWT client assertion signed with the certificate private key.
3. POST directly to the Entra OAuth2 token endpoint with `grant_type=client_credentials` and `scope=https://graph.microsoft.com/.default`.
4. Convert the returned access token string to `SecureString`.
5. Connect Graph PowerShell with:

```powershell
Connect-MgGraph -AccessToken $secureToken -NoWelcome
```

This produced:

- `AuthType: UserProvidedAccessToken`
- `TokenCredentialType: UserProvidedAccessToken`
- Successful mailbox read
- No observed Microsoft account-picker popup

Use the reusable wrapper:

```powershell
. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
```

## Future-Agent Rule

For agent-driven Outlook, calendar, OneDrive, or Microsoft Graph operations:

1. Load the `microsoft_graph` skill.
2. Use `connect-graph-no-wam.ps1` / `Connect-GraphNoWam`.
3. Perform the Graph operation in the same `bash`/PowerShell command.
4. Do not use delegated auth (`-Scopes`, `-UseDeviceCode`) in an agent session.
5. Do not use direct `Connect-MgGraph -CertificateThumbprint` unless intentionally testing this issue.

## Scripts That Need Migration

These were identified by searching for `Connect-MgGraph`, `CertificateThumbprint`, and `-Scopes`.

### High priority: production / validation scripts

1. `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
   - Current pattern: direct `Connect-MgGraph -CertificateThumbprint`.
   - Risk: scheduled task may trigger WAM/account picker even though it logs AppOnly.
   - Update: dot-source `connect-graph-no-wam.ps1`, replace direct certificate connection with `Connect-GraphNoWam`.
   - Validate: run the scheduled-task script in dry-run/safe mode if available, or run a read-only mailbox scan path; confirm no popup and successful message retrieval.

2. `C:\development\email-triage\scripts\validate-graph-app-only-auth.ps1`
   - Current pattern: validates direct `Connect-MgGraph -CertificateThumbprint`.
   - Risk: the validator itself can trigger the popup and gives a false sense of safety by checking only `AuthType=AppOnly`.
   - Update: make this validate `Connect-GraphNoWam`; expect `AuthType=UserProvidedAccessToken` / `TokenCredentialType=UserProvidedAccessToken` instead of `AppOnly`.
   - Validate: run script end-to-end; confirm certificate preflight, token mint, Graph connect, mailbox access, and clean disconnect.

3. `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\search-outlook-messages.ps1`
   - Current status: documentation updated to require `Connect-GraphNoWam` before invocation.
   - Optional update: add a `-ConnectNoWam` mode so the script can self-connect when ClientId/TenantId/CertThumbprint are provided.
   - Validate: run a narrow date/topic search and export to a temp file.

### Medium priority: ad hoc / conductor track scripts

4. `C:\development\email-triage\scripts\test-live-dry-run.ps1`
   - Current pattern: `Connect-MgGraph -Scopes 'Mail.Read'` interactive auth.
   - Update: replace delegated auth with `Connect-GraphNoWam` or mark script as manual-only.

5. `C:\development\email-triage\.conductor\tracks\20260502-later-junk-pattern-analysis\extract-headers.ps1`
   - Current pattern: `Connect-MgGraph -Scopes 'Mail.Read'` interactive auth.
   - Update: replace with `Connect-GraphNoWam` if this track will be reused.

6. `C:\development\email-triage\.conductor\tracks\20260502-later-junk-pattern-analysis\search-messages.ps1`
   - Current pattern: `Connect-MgGraph -Scopes 'Mail.Read'` interactive auth.
   - Update: replace with `Connect-GraphNoWam` if this track will be reused.

7. `C:\development\email-triage\.conductor\tracks\20260502-later-junk-pattern-analysis\search-folders.ps1`
   - Current pattern: `Connect-MgGraph -Scopes 'Mail.Read'` interactive auth.
   - Update: replace with `Connect-GraphNoWam` if this track will be reused.

### Documentation references to keep aligned

8. `C:\development\opencode\docs\reference\m365-cli-quickstart.md`
   - Current status: updated to reference `Connect-GraphNoWam` as the standard.

9. `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\SKILL.md`
   - Current status: updated to reference `Connect-GraphNoWam` as the standard.

10. `C:\development\opencode\docs\reference\ADR-003-m365-mcp-to-cli-migration.md`
    - Current pattern: describes app-only certificate auth using `Connect-MgGraph`.
    - Update: add note that current implementation uses no-WAM REST token wrapper for agent sessions.

11. `C:\development\opencode\docs\junk-email-workflow.md`
    - Current pattern: direct `Connect-MgGraph` / certificate thumbprint examples.
    - Update: swap examples to `Connect-GraphNoWam`.

## Validation Plan

For every migrated script:

1. Static check:
   - Search the file for `Connect-MgGraph -Scopes`, `-UseDeviceCode`, and direct `-CertificateThumbprint`.
   - The only acceptable `Connect-MgGraph` use should be `Connect-MgGraph -AccessToken` inside the wrapper.

2. Auth smoke check:
   - Dot-source `connect-graph-no-wam.ps1`.
   - Run `Connect-GraphNoWam`.
   - Confirm `Get-MgContext` returns `AuthType=UserProvidedAccessToken`.

3. Mailbox read check:
   - Run a read-only call such as:
     ```powershell
     Get-MgUserMessage -UserId $UserId -Top 1 -Property Subject,ReceivedDateTime
     ```

4. User-observed popup check:
   - Ask Dave whether an account-picker popup appeared during the smoke check.
   - If any popup appears, stop using Microsoft.Graph auth path and use raw `Invoke-RestMethod` Graph calls with the REST-minted token instead.

5. Scheduled task check, where applicable:
   - Run the task manually.
   - Check logs for successful token mint/connect/read.
   - Confirm no account picker appears.
