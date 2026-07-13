# Gmail Workspace — Detailed Reference

## Scrum Inc. Account Quick Reference

**Account:** `dave.witkin@scruminc.com` — managed Google Workspace domain, NO Google Cloud Console access.

| Method | Viable? | Notes |
|--------|---------|-------|
| Chrome browser tools | Yes | Best for 1-5 specific emails. User signs in manually. |
| Google Apps Script | Yes | Best for bulk exports. User has used this before. |
| Python Gmail API | No | Requires Cloud Console OAuth credentials. |
| gws CLI | Blocked | OAuth 403 on bundled client. |

See SKILL.md for full Scrum Inc. process guide.

---

## Script: export-gmail-window.py

**Location:** `scripts/export-gmail-window.py`

Full-featured Gmail export using the Gmail API v1 with OAuth 2.0 (read-only scope).

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--account` | Yes | Gmail account email (e.g. `dave.witkin@scruminc.com`) |
| `--start-date` | Yes | Start date ISO format (e.g. `2026-02-01`) |
| `--end-date-exclusive` | Yes | End date exclusive ISO format |
| `--output` | Yes | Path to output markdown file |
| `--manifest` | Yes | Path to output manifest file |
| `--credentials` | Yes | Path to OAuth `credentials.json` |
| `--token` | Yes | Path to OAuth `token.json` (created on first run) |
| `--max-results` | No | Limit number of messages exported |
| `--dry-run` | No | Authenticate and count only; skip export |

### OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download `credentials.json`
6. First run opens browser for auth; subsequent runs use saved token

### Output Files

- **Markdown export:** One section per message with metadata table and body
- **Manifest:** Summary of export parameters, message count, and timestamp

### Architecture Notes

- Uses epoch-based date queries (`after:EPOCH before:EPOCH`) for precise filtering
- Handles multi-part MIME messages (prefers `text/plain`, falls back to `text/html` via BeautifulSoup)
- Paginates through results in batches of 500
- Error handling: logs warnings for individual message fetch failures, continues export

---

## Script: gmail-export-apps-script.js

**Location:** `scripts/gmail-export-apps-script.js`

Google Apps Script for browser-only export (no local dependencies).

**Primary method for Scrum Inc. bulk exports** — this is the go-to approach for `@scruminc.com` accounts because it runs under the user's own Google session and requires no Cloud Console access. The user has used this method successfully before.

### Configuration

Edit these variables at the top of the script:

```javascript
var START_DATE = "2026/02/01";        // Start date (inclusive)
var END_DATE = "2026/05/01";          // End date (exclusive)
var MAX_MESSAGES = 500;               // Max messages to export
var OUTPUT_FILENAME = "gmail_export_90days.md";
```

### How to Run

1. Open https://script.google.com/
2. New project → paste the full script
3. Click Run (grant permissions when prompted)
4. Check Execution log for progress
5. Download output from Google Drive root

### Limitations

- No raw Gmail thread IDs (generates synthetic `thread-{timestamp}-{n}`)
- Date filtering uses `GmailApp.search()` which can be imprecise on boundaries
- Maximum execution time: 6 minutes (Google Apps Script limit)
- For large exports, may need to run in batches

---

## Script: pretriage-gmail-export.py

**Location:** `scripts/pretriage-gmail-export.py`

Classifies, scores, and organizes exported Gmail messages into review queues.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input` | Yes | Path to Gmail markdown export |
| `--config` | Yes | Path to pre-triage config JSON |
| `--output-csv` | Yes | Path to output CSV |
| `--triage-md` | Yes | Path to message-triage-auto.md |
| `--priority-md` | Yes | Path to priority-review-queue.md |
| `--skip-sample-md` | Yes | Path to skip-auto-sample.md |
| `--thread-groups-md` | Yes | Path to thread-groups.md |
| `--summary-md` | Yes | Path to pretriage-summary.md |

### Config JSON Structure

```json
{
  "scoreWeights": {
    "prioritySubject": 10,
    "prioritySender": 8,
    "autoSkipSubject": -5,
    "autoSkipSender": -3,
    "bodyPriorityTerm": 2,
    "hasCc": 1,
    "fromDavePenalty": -3
  },
  "thresholds": {
    "ingestCandidateScore": 8,
    "reviewScore": 3,
    "skipAutoScore": 0,
    "minimumSkipSample": 10,
    "samplePercent": 20
  },
  "prioritySubjectPatterns": ["urgent", "action required", "decision"],
  "prioritySenderPatterns": ["@scruminc\\.com$"],
  "autoSkipSubjectPatterns": ["newsletter", "unsubscribe", "receipt"],
  "autoSkipSenderPatterns": ["noreply@", "no-reply@"],
  "needsHumanPatterns": ["legal", "confidential", "contract"],
  "threadRepresentativeSort": ["score_desc", "body_length_desc"]
}
```

### Output Files

1. **CSV** — Full message data with scores and classifications
2. **Triage markdown** — All messages with classification summary table
3. **Priority queue** — Only INGEST-CANDIDATE + REVIEW, sorted by score
4. **Skip sample** — Random sample of SKIP-AUTO for audit
5. **Thread groups** — Messages grouped by thread with representative selection
6. **Summary** — Classification breakdown and next steps

### Classification Algorithm

1. **NEEDS-HUMAN** — Contains sensitive patterns (legal, confidential, contract)
2. **SKIP-AUTO** — Matches auto-skip patterns AND no priority patterns match
3. **INGEST-CANDIDATE** — Score >= threshold
4. **REVIEW** — Score >= review threshold
5. **SKIP-AUTO** — Score < skip threshold
6. **REVIEW** — Catch-all

### Thread Collapse

Messages with the same `ThreadId` are grouped. The highest-scoring message becomes the representative; others are marked `DUPLICATE-CANDIDATE`.

---

## Script: generate-gmail-extraction-register.py

**Location:** `scripts/generate-gmail-extraction-register.py`

Scans the export and identifies messages with extractable KB entity content.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input` | Yes | Gmail export markdown file |
| `--priority-csv` | Yes | Pre-triage CSV |
| `--output` | Yes | Output extraction register markdown |

---

## Script: generate-gmail-kb-files.py

**Location:** `scripts/generate-gmail-kb-files.py`

Generates KB entity files with YAML front matter from the extraction register.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input` | Yes | Gmail export markdown file |
| `--register` | Yes | Extraction register markdown |
| `--source-id` | No | Source note ID (default: `source-gmail-high-signal-ingestion`) |

---

## gws CLI Reference

**Status:** Installed but blocked by OAuth 403 error.

**Installed version:** v0.22.5
**Location:** `C:\Users\DaveWitkin\.cargo\bin\gws.exe`
**Install command:** `cargo install google-workspace-cli`

### Key Commands

```bash
# Check auth status
gws auth status

# Login (currently blocked by OAuth verification)
gws auth login -s gmail --readonly

# List emails (requires valid auth)
gws gmail list --query "in:inbox" --max-results 10

# Get specific email
gws gmail get <message-id>
```

### OAuth 403 Error Details

- The `gws` CLI bundles a client app named "chatgpt-desktop-auth"
- This app has not completed Google's OAuth verification process
- Error: `Error 403: access_denied`
- Only developer-approved testers can authenticate
- **Workaround:** Use your own OAuth credentials with the Python scripts, or use the Apps Script approach

### Resolution Options

1. **Custom OAuth client:** Create your own OAuth client in Google Cloud Console, download `credentials.json`, and configure `gws` to use it instead of the bundled client
2. **Contribute to gws:** Submit a PR to the googleworkspace/cli repo to update the bundled client
3. **Alternative CLIs:** Consider `gog` (steipete/gogcli) or `gm` (evoleinik/gm) which may use different OAuth clients
