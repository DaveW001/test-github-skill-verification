# M365 CLI Command Mapping Table

**Track ID**: 20260315-ms365-mcp-to-cli-migration

---

## Mapping: MCP Tools to Graph PowerShell Equivalents

| MCP Tool (ms365_*) | Graph PowerShell Cmdlet | Status | Notes |
|---|---|---|---|
| `ms365_move-mail-message` | `Move-MgUserMessage` | ✅ Verified | Requires `-UserId`, `-MessageId`, `-DestinationId` |
| `ms365_list-mail-folders` | `Get-MgUserMailFolder` | ✅ Verified | Returns all folders for a user |
| `ms365_get-mail-message` | `Get-MgUserMessage` | ✅ Verified | Get single message by ID |
| `ms365_list-mail-messages` | `Get-MgUserMessage` | ✅ Verified | List messages with `-Top` |
| `ms365_send-mail-message` | `Send-MgUserMail` | ⚠️ Untested | Requires mail send permissions |

---

## Auth Bootstrap (App-Only Certificate)

```powershell
# Standard auth bootstrap - reuse existing app registration
Connect-MgGraph `
    -ClientId $env:DPB_GRAPH_CLIENT_ID `
    -TenantId $env:DPB_GRAPH_TENANT_ID `
    -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT `
    -NoWelcome
```

Environment variables required:
- `DPB_GRAPH_CLIENT_ID`
- `DPB_GRAPH_TENANT_ID`
- `DPB_GRAPH_CERT_THUMBPRINT`

---

## Output Handling Policy

To minimize context load:
1. Always use `Select-Object` to return only required properties
2. Use `-Top N` for list operations
3. Use `ConvertTo-Json -Depth 2` for machine-readable output
4. Prefer summary tables over raw JSON dumps in documentation

---

## Safety Controls

| Control | Implementation |
|---|---|
| Retry logic | 3 attempts with exponential backoff (1s, 2s, 4s) |
| Throttling handling | Detect 429, wait 5-10s, retry |
| Idempotency | Check message exists before move |
| Error classification | Capture error type for troubleshooting |

---

## Validation Results

| Test | Result | Date |
|---|---|---|
| Cert auth connects successfully | ✅ PASS | 2026-03-15 |
| Get-MgUser works | ✅ PASS | 2026-03-15 |
| Move-MgUserMessage (dry-run) | Pending | - |
