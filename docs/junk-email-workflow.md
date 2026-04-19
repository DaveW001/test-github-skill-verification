# Junk Email Processing Workflow

## Overview

This document describes the standardized workflow for processing junk emails in Microsoft 365 using automated triage and bulk move operations.

**Last Updated:** 2026-03-15  
**Version:** 1.0  
**Author:** Dave Witkin / Packaged Agile

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Workflow](#detailed-workflow)
4. [Folder Configuration](#folder-configuration)
5. [Throttling & Rate Limits](#throttling--rate-limits)
6. [Troubleshooting](#troubleshooting)
7. [Tools Reference](#tools-reference)
8. [Pattern Maintenance](#pattern-maintenance)

---

## Prerequisites

### Required Access
- Microsoft 365 account with mailbox access
- Microsoft Graph API permissions:
  - `Mail.Read`
  - `Mail.ReadWrite`
  - `MailboxSettings.Read`

### Required Files
```
config/junk-indicators.json          # Junk detection patterns
junk_triage.py                       # Core classification engine
process_junk_emails.py               # Batch processor
delete_ids.txt                       # Message IDs marked for deletion
```

### Environment Setup
Ensure you have the Microsoft Graph PowerShell SDK installed and the environment variables for certificate-based authentication are set (`DPB_GRAPH_CLIENT_ID`, `DPB_GRAPH_TENANT_ID`, `DPB_GRAPH_CERT_THUMBPRINT`).

---

## Quick Start

For experienced users familiar with the workflow:

```bash
# 1. Export junk emails from Outlook to CSV
#    - Go to Junk Email folder
#    - Select all → Export to CSV
#    - Save as: YYYY-MM-DD-junk-email.CSV

# 2. Validate the CSV has the expected columns:
#    - Subject, Body, From: (Address), etc.

# 3. Run triage classification
python process_junk_emails.py

# 4. Review delete_ids.txt for message IDs to move

# 5. Move messages from Junk to Deleted Items using Graph PowerShell
#    (See Detailed Workflow Phase 3)

# 6. Verify Junk Email folder is empty
```

---

## Detailed Workflow

...

### Phase 3: Bulk Move Operations

**⚠️ WARNING:** Microsoft Graph API has rate limits. Do not exceed 10 concurrent operations.

#### Option A: Using Microsoft Graph PowerShell SDK (Recommended)

This is the standard, low-overhead path for mailbox operations.

```powershell
# 1. Connect using App-Only Certificate Auth
Connect-MgGraph `
  -ClientId $env:DPB_GRAPH_CLIENT_ID `
  -TenantId $env:DPB_GRAPH_TENANT_ID `
  -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT `
  -NoWelcome

# 2. Move message
$userId = "58dba6be-24ef-4a75-b968-c64f75b504b1" # Dave Witkin
$messageId = "AAMkAGU4NTQ1NTVk..."
$destinationFolderId = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEKAAA="

Move-MgUserMessage -UserId $userId `
  -MessageId $messageId `
  -DestinationId $destinationFolderId
```

#### Option B: Using Microsoft Graph REST API

...

#### Option C: [DEPRECATED] Using ms365_move-mail-message

This tool was part of the Microsoft 365 MCP server and is being phased out in favor of the direct CLI approach to reduce model context overhead.

```powershell
# Legacy command
ms365_move-mail-message `
  -messageId "AAMkAGU4NTQ1NTVk..." `
  -destinationFolderId "..." `
  -excludeResponse:$true
```

```python
import requests

# Configuration
access_token = "YOUR_ACCESS_TOKEN"
user_id = "user@domain.com"
message_id = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQBGAAAAAAA..."
destination_folder_id = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQBGAAAAAAA..."

# API endpoint
url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}/move"

# Request body
body = {
    "destinationId": destination_folder_id
}

# Headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Execute move
response = requests.post(url, json=body, headers=headers)

if response.status_code == 201:
    print(f"✓ Message moved successfully")
else:
    print(f"✗ Error: {response.status_code} - {response.text}")
```

### Phase 4: Batch Processing Script

For moving multiple messages efficiently:

```powershell
# move_junk_batch.ps1
param(
    [string]$MessageIdsFile = "delete_ids.txt",
    [int]$DelayMs = 500,
    [int]$ThrottleDelaySec = 5
)

$JunkFolderId = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAASHvdAAA="
$DeletedItemsFolderId = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEKAAA="

$MessageIds = Get-Content $MessageIdsFile
$success = 0
$failed = 0

foreach ($msgId in $MessageIds) {
    try {
        ms365_move-mail-message `
            -messageId $msgId `
            -destinationFolderId $DeletedItemsFolderId `
            -excludeResponse:$true
        
        $success++
        Write-Host "." -NoNewline -ForegroundColor Green
    }
    catch {
        if ($_.Exception.Message -match "429|throttl") {
            Write-Host "T" -NoNewline -ForegroundColor Yellow
            Start-Sleep -Seconds $ThrottleDelaySec
            
            # Retry
            try {
                ms365_move-mail-message -messageId $msgId -destinationFolderId $DeletedItemsFolderId -excludeResponse:$true
                $success++
            }
            catch {
                $failed++
                Write-Host "F" -NoNewline -ForegroundColor Red
            }
        }
        else {
            $failed++
            Write-Host "F" -NoNewline -ForegroundColor Red
        }
    }
    
    Start-Sleep -Milliseconds $DelayMs
}

Write-Host ""
Write-Host "Results: $success moved, $failed failed"
```

### Phase 5: Verification

1. **Check Junk Email folder** should show 0 messages
2. **Check Deleted Items folder** should contain the moved messages
3. **Review any error logs** for failed moves
4. **Retry failed items** individually if needed

---

## Folder Configuration

### Standard Folder IDs

These IDs are specific to the mailbox and remain constant:

| Folder | ID |
|--------|-----|
| **Junk Email** | `AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAASHvdAAA=` |
| **Deleted Items** | `AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEKAAA=` |

### Finding Folder IDs

If folder IDs change or you need to verify:

```powershell
# Using Microsoft Graph PowerShell
Get-MgUserMailFolder -UserId "user@domain.com" | 
    Select-Object DisplayName, Id | 
    Format-Table -AutoSize
```

---

## Throttling & Rate Limits

### Microsoft Graph Limits

| Resource | Limit | Window |
|----------|-------|--------|
| Mailbox operations | 10,000 requests | 10 minutes |
| Concurrent connections | 4 per mailbox | - |
| Message moves | ~100/minute | Sustained |

### Handling 429 Errors

When you receive a `429 ApplicationThrottled` error:

1. **Stop processing immediately**
2. **Wait 5-10 seconds**
3. **Retry the failed operation**
4. **Increase delay between operations** to 1-2 seconds

### Best Practices

- Process messages in batches of 10-20
- Add 500ms-1s delay between operations
- Monitor for 429 responses
- Implement exponential backoff for retries
- Use `excludeResponse: true` to reduce payload size

---

## Troubleshooting

### Error: 404 ErrorInvalidMailboxItemId

**Cause:** Message ID doesn't exist in the specified mailbox context

**Solution:**
1. Re-list folders to get current IDs
2. Verify the message hasn't been moved/deleted already
3. Check you're using the correct mailbox context

### Error: 429 ApplicationThrottled

**Cause:** Too many concurrent operations hitting mailbox concurrency limit

**Solution:**
1. Add delays between operations (500ms-1s)
2. Reduce batch size
3. Wait 5-10 seconds before retrying
4. Process during off-peak hours

### Error: 401 Unauthorized

**Cause:** Authentication token expired or insufficient permissions

**Solution:**
1. Re-authenticate: `Connect-MgGraph`
2. Verify scopes: `Mail.ReadWrite`
3. Check token expiration

### Error: Message already in destination folder

**Cause:** Duplicate processing or previous successful move

**Solution:**
1. Remove message ID from delete_ids.txt
2. Mark as completed in tracking

### Messages not appearing in Junk Email

**Cause:** Auto-filtering or already processed

**Solution:**
1. Check Deleted Items folder
2. Verify Outlook rules aren't auto-moving messages
3. Check if messages were already processed in previous batch

---

## Tools Reference

### Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `junk_triage.py` | Classify emails as delete/review/keep | Import as module or run `--test` |
| `process_junk_emails.py` | Batch process CSV export | `python process_junk_emails.py` |
| `prepare_deletions.py` | Prepare message IDs for deletion | Generate delete_ids.txt |
| `move_remaining_junk.ps1` | Bulk move messages | `./move_remaining_junk.ps1` |

### Configuration Files

| File | Purpose |
|------|---------|
| `config/junk-indicators.json` | Spam detection patterns and safe domains |
| `reports/junk-triage-results-*.json` | Classification output |
| `delete_ids.txt` | List of message IDs to move |

### OpenCode Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `ms365_move-mail-message` | Move email between folders | `ms365_move-mail-message -messageId $id -destinationFolderId $dest` |
| `ms365_list-mail-folders` | List mailbox folders | `ms365_list-mail-folders` |

---

## Pattern Maintenance

### Adding New Junk Domains

Edit `config/junk-indicators.json`:

```json
{
  "junk_domains": [
    "existing-domain.com",
    "new-spam-domain.com"
  ]
}
```

### Adding Username Patterns

Add regex patterns for suspicious usernames on consumer domains:

```json
{
  "junk_patterns": {
    "local_part": [
      "^existing_pattern[0-9]+",
      "^new_spammer_pattern"
    ]
  }
}
```

### Adding Safe Domains

Add legitimate domains to prevent false positives:

```json
{
  "safe_domains": [
    "trusted-vendor.com"
  ]
}
```

### Guidelines

- **Never** add consumer providers (gmail.com, outlook.com, hotmail.com) to junk_domains
- Use `local_part` patterns instead for consumer domain spam
- Document pattern rationale in the `notes` array
- Test patterns before committing to production

---

## Workflow Checklist

- [ ] Export junk emails to CSV
- [ ] Validate CSV contents (41 rows expected for full batch)
- [ ] Run classification script
- [ ] Review DELETE recommendations
- [ ] Extract message IDs to delete_ids.txt
- [ ] Verify folder IDs are current
- [ ] Execute bulk move with throttling protection
- [ ] Verify Junk Email folder is empty
- [ ] Document any new patterns discovered
- [ ] Update junk-indicators.json if needed

---

## Batch History

| Date | Batch Size | Moved | Remaining | Notes |
|------|------------|-------|-----------|-------|
| 2026-03-15 | 41 | 22 | 19 | Initial CSV export, throttling encountered |

---

## Related Documentation

- `docs/junk-patterns-analysis-20250314.md` - Pattern analysis and classification rules
- Microsoft Graph API Reference: https://docs.microsoft.com/en-us/graph/api/message-move

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-15 | 1.0 | Initial workflow documentation |

---

**End of Document**
