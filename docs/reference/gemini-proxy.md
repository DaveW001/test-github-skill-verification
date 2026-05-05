# Gemini API Key Rotator Proxy - Reference Guide

**Location:** `C:\Users\DaveWitkin\.local\gemini-proxy\`  
**Port:** `127.0.0.1:8000`  
**Purpose:** Load-balanced proxy for Google Gemini API with automatic key rotation  
**Last Updated:** May 2, 2026

---

## Overview

The Gemini API Key Rotator Proxy is a FastAPI-based local proxy server that:
- Automatically rotates through multiple Google Gemini API keys
- Provides a single local endpoint (`127.0.0.1:8000`) for OpenCode and other tools
- Handles rate limiting with exponential backoff
- Supports both streaming and non-streaming requests

## Current Operational State (2026-03-14)

- Primary runtime is `main.py` on `127.0.0.1:8000`.
- OpenCode is configured to route Google provider traffic through proxy base URL `http://127.0.0.1:8000/v1beta`.
- Legacy manual tasks were retired; scheduler ownership is now via opencode-scheduler tasks:
  - `opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-monitor`
  - `opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter`
  - `opencode-job-opencode-global-7a3f9c2e1b84-osgrep-auto-indexer`
- Enhanced request forensics are active in `logs\detailed_requests.log`.
- Startup marker verification is active in `logs\startup-state.json`.

### Operator Fast Path

```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy

# Single-pass health (0=ok,1=warn,2=fail)
.\health-check.ps1

# Run monitor logic once (same logic as scheduled monitor)
.\monitor-proxy.ps1

# Live connection/process view for port 8000
.\monitor-connections.ps1
```

### Why Multiple Keys?
Google's free tier has rate limits per API key. By rotating through multiple keys, we effectively multiply the available quota.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   OpenCode      │────▶│  Gemini Proxy        │────▶│  Google Gemini  │
│   (or other     │     │  (127.0.0.1:8000)    │     │  API            │
│    tools)       │     │                      │     │                 │
└─────────────────┘     │  • Key rotation      │     └─────────────────┘
                        │  • Rate limit        │              ↑
                        │    handling          │              │
                        │  • Auto-retry        │              │
                        └──────────────────────┘     Rotates through:
                                                       • Key 1
                                                       • Key 2
                                                       • Key 3
                                                       • Key 4
```

---

## File Locations

### Proxy Installation
```
C:\Users\DaveWitkin\.local\gemini-proxy\
├── main.py                          # Main proxy server (FastAPI)
├── main-openai.py                   # OpenAI-compatible mode (not used)
├── api_keys.txt                     # API keys (one per line)
├── key_names.json                   # Friendly names for each API key
├── requirements.txt                 # Python dependencies
├── README.md                        # Original proxy documentation
├── QUICK-REFERENCE.md              # Original quick reference
├── logs/                           # Log files
│   ├── proxy.log                   # Main proxy log
│   ├── detailed_requests.log       # Per-request forensic log (headers/body preview/user-agent)
│   ├── startup-state.json          # Starter lifecycle marker file
│   ├── alerts.log                  # Alert history
│   └── monitor-state.json          # Monitor state
├── venv/                           # Python virtual environment
│
├── Management Scripts (Created):
├── start-proxy-background.ps1      # Start proxy headless
├── stop-proxy.ps1                   # Stop proxy
├── proxy-status.ps1                 # Check status + key health
├── health-check.ps1                 # One-shot health report (exit codes)
├── monitor-connections.ps1          # Real-time connection/process monitor
├── gemini-proxy-dashboard.ps1       # Console dashboard
├── Create-GeminiProxyTask.ps1      # Create Windows Scheduled Task
└── CreateTask.bat                   # Alternative task creation
```

### OpenCode Configuration
```
C:\Users\DaveWitkin\.config\opencode\opencode.jsonc
```

**Key Configuration:**
```jsonc
"google": {
  "options": {
    "baseURL": "http://127.0.0.1:8000/v1beta",
    "apiKey": "proxy-will-replace-this"
  }
}
```

---

## Current API Keys

**File:** `C:\Users\DaveWitkin\.local\gemini-proxy\api_keys.txt`

Current configuration: **1 active key**

```
AIzaSyCND2NSbn3Sjkp0fFJb4Rkt4RdmDNe1q3g    # Dave Personal for OC (davidawitkin@gmail.com) — replaced 2026-04-20
```

**Removed keys (2026-05-02):** Raquel and Tiberius keys removed — Google changed the family plan, no longer allowing API usage except for the primary account holder (`davidawitkin@gmail.com`). Both keys showed 0 successes and 11 failures.

**Note:** API keys are rotated automatically. The proxy tracks success/failure per key and implements exponential backoff for failed keys.

### Key Rotation History (2026-04-20)

All 3 previous keys were flagged by Google as **leaked/compromised** (HTTP 403 "Your API key was reported as leaked"). They were replaced in-place:

| Old Key (Compromised)                    | New Key (Active)                          | Owner    |
| ---------------------------------------- | ----------------------------------------- | -------- |
| `AIzaSyC40vaghThPpg86B2siZVWhCNUt6rF2AVA`  | `AIzaSyCND2NSbn3Sjkp0fFJb4Rkt4RdmDNe1q3g` | Dave     |
| `AIzaSyCqs5AFWOjpkt48qi-R_O-0pDEIy3UZgJM`  | `AIzaSyAIHoxsjwpCRS9vCw6hxWSMw2afsvrCxG4` | Raquel   |
| `AIzaSyBX5g0ZGBc2RVd6WK14RzFERlKXNoyHfww`  | `AIzaSyDQJD_pwtyIPAiJ_-clerkI1hgQRnhzh50` | Tiberius |

---

## Google Gemini API Model Restrictions (2026-04-20, updated 2026-05-02)

**⚠️ Critical: Google has revoked access to Pro-tier models for non-primary family plan accounts.**

As of April 2026, Google AI Studio has restricted model access **per account/key**, with significant differences between accounts. As of May 2, 2026, Google further changed the family plan so that **only the primary account holder** (`davidawitkin@gmail.com`) can use the API at all — family member accounts (Raquel, Tiberius) are no longer authorized.

### Per-Key Model Availability

| Model                  | Dave (`AIzaSyCND2NS...`) |
| ---------------------- | ------------------------ |
| Gemini 3.1 Pro         | ✅ Available (limited)   |
| Gemini 2.5 Pro         | ✅ Available (limited)   |
| Gemini 2.5 Flash       | ✅ Available             |
| Gemini 3.1 Flash Lite  | ✅ Available             |
| Gemma (open-source)    | ✅ Available             |

**Key takeaway:** Only Dave's key (`davidawitkin@gmail.com`) is active in the proxy. Raquel's and Tiberius's keys were removed on 2026-05-02 after Google changed the family plan to restrict API access to the primary account only. Both keys had 0 successes and 11 failures at time of removal.

**Proxy behavior impact:** Single-key operation means no round-robin rotation. All requests go through Dave's key. Rate limits will be hit sooner under heavy use. If additional quota is needed, consider:
1. Using a different Google Cloud project with paid billing enabled
2. Using alternative providers (OpenAI, Anthropic) for additional capacity
3. Optimizing prompts to stay within single-key quota

---

## Management Commands

### Quick Status Check
```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\proxy-status.ps1
```

### Start Proxy (Manual)
```powershell
# Start in background (headless)
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\start-proxy-background.ps1

# Or using the quiet script (logs to file)
.\start-proxy-quiet.ps1
```

### Stop Proxy
```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\stop-proxy.ps1
```

### View Logs
```powershell
# View last 20 lines
Get-Content C:\Users\DaveWitkin\.local\gemini-proxy\logs\proxy.log -Tail 20

# Watch logs in real-time
Get-Content C:\Users\DaveWitkin\.local\gemini-proxy\logs\proxy.log -Tail 50 -Wait
```

---

## Admin Endpoints

The proxy exposes two admin endpoints (require `x-proxy-admin: changeme_local_only` header):

### Check Key Status
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/status" `
  -Headers @{"x-proxy-admin"="changeme_local_only"}
```

**Sample Response:**
```json
{
  "keys": [
    {
      "key_preview": "AIzaSyC40vag...",
      "available_in": 0,
      "backoff": 0,
      "success": 150,
      "fail": 2
    }
  ]
}
```

> **Tip:** For friendly names in status output, see `C:\Users\DaveWitkin\.local\gemini-proxy\key_names.json`

### Reload Keys Without Restart
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" `
  -Method POST `
  -Headers @{"x-proxy-admin"="changeme_local_only"}
```

**Use this after editing `api_keys.txt`** - no restart required!

---

## Windows Scheduled Tasks

Proxy-related automation is managed by opencode-scheduler.

### Task Details
| Property | Value |
|----------|-------|
| **Task Name** | `opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter` |
| **Trigger** | Daily 06:00 |
| **Action** | Runs starter command headlessly |
| **Run As** | Current user |

Companion monitor task:

| Property | Value |
|----------|-------|
| **Task Name** | `opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-monitor` |
| **Trigger** | Every 30 minutes |
| **Action** | Runs `monitor-proxy.ps1` headlessly |
| **Run As** | Current user |

### Task Management Commands
```powershell
# View managed task status
Get-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-*"

# Start now
Start-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"

# Stop
Stop-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"

# Disable auto-start
Disable-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"

# Re-enable
Enable-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"

# Remove completely
Unregister-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter" -Confirm:$false
```

### Recreate Task (if needed)
```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy
"C:\Program Files\gsudo\Current\gsudo.exe" powershell -ExecutionPolicy Bypass -File "Create-GeminiProxyTask.ps1"
```

---

## Modifying API Keys

### To Remove a Key:

1. **Edit the keys file:**
   ```powershell
   notepad C:\Users\DaveWitkin\.local\gemini-proxy\api_keys.txt
   ```

2. **Remove the line** containing the key to exclude

3. **Save the file**

4. **Reload keys** (no restart needed):
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" `
     -Method POST `
     -Headers @{"x-proxy-admin"="changeme_local_only"}
   ```

5. **Verify:**
   ```powershell
   cd C:\Users\DaveWitkin\.local\gemini-proxy
   .\proxy-status.ps1
   ```

### To Add a Key:

1. Get a new API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. Add to `api_keys.txt` (one per line)

3. Reload keys using command above

---

## Troubleshooting

See: [Gemini Proxy Troubleshooting Guide](./../troubleshooting/active/gemini-proxy-down.md)

### Quick Diagnostics

```powershell
# Check if port 8000 is listening
netstat -ano | findstr :8000

# Check if process is running
tasklist | findstr python

# Test proxy directly
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1beta/models" `
  -Method GET
```

---

## Technical Details

### Proxy Configuration (`main.py`)

```python
KEYS_FILE = "api_keys.txt"          # API keys location
ADMIN_TOKEN = "changeme_local_only"  # Admin endpoint auth
UPSTREAM_BASE_GEMINI = "https://generativelanguage.googleapis.com/v1beta"
BACKOFF_MIN = 5                      # Minimum backoff (seconds)
BACKOFF_MAX = 600                    # Maximum backoff (seconds)
```

### Rate Limiting Behavior

- When a key hits rate limit (429 error), it's temporarily disabled
- Backoff increases exponentially: 5s → 10s → 20s → 40s... up to 600s (10 min)
- Successful requests reset the backoff to 0
- Proxy automatically tries next available key

### Supported Endpoints

All Google Gemini API endpoints are proxied:
- `/v1beta/models` - List models
- `/v1beta/models/{model}:generateContent` - Generate content
- `/v1beta/models/{model}:streamGenerateContent` - Streaming generation
- Plus all other Gemini API endpoints

---

## Related Documentation

- **Troubleshooting:** `C:\development\opencode\docs\troubleshooting\active\gemini-proxy-down.md`
- **AGENTS.md Reference:** Line 95-100 in `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
- **Original Proxy Docs:** `C:\Users\DaveWitkin\.local\gemini-proxy\README.md`
- **Evaluation Report:** `C:\development\playground\gemini-proxy-evaluation-report.md`

---

## Changes & Maintenance Log

| Date | Change | Description |
|------|--------|-------------|
| 2026-03-12 | Fixed route ordering | Moved `/status` and `/reload-keys` endpoints before catch-all route so they work correctly |
| 2026-03-12 | Reduced keys | Removed 1 API key (now using 3 keys for financial testing) |
| 2026-03-12 | Created management scripts | Added `start-proxy-background.ps1`, `stop-proxy.ps1`, `proxy-status.ps1` |
| 2026-03-12 | Created scheduled task | Added Windows Task Scheduler integration for auto-start |
| 2026-03-14 | Migrated scheduler ownership | Retired legacy manual tasks; opencode-scheduler tasks are source of truth |
| 2026-03-14 | Added startup verification | `start-proxy-quiet.ps1` now writes `startup-state.json` lifecycle markers |
| 2026-03-14 | Added scheduler health checks | `monitor-proxy.ps1` now validates task existence, lag, and last result |
| 2026-03-14 | Added one-shot health check | `health-check.ps1` reports operational state with exit codes |
| 2026-03-14 | Added request forensics | `detailed_requests.log` records user-agent, headers, and body preview |
| 2026-04-20 | **Emergency key rotation** | All 3 keys flagged as leaked by Google (403). Replaced all keys in `api_keys.txt` and `key_names.json`. Reloaded via `/reload-keys` (no restart needed). |
| 2026-04-20 | **Model access revoked (per-key)** | Google removed Pro-tier access for Raquel and Tiberius keys (0 quota). Dave's key retains both Gemini 3.1 Pro and 2.5 Pro (limited). Only Flash models + Gemma universally available across all keys. |
| 2026-05-02 | **Family plan keys removed** | Google changed the family plan — only the primary account (`davidawitkin@gmail.com`) can use the API. Removed Raquel and Tiberius keys from `api_keys.txt` (both had 0 successes, 11 failures). Proxy now running single-key. Reloaded via `/reload-keys`. Updated docs. |

---

## Contact & Issues

If the proxy is down or experiencing issues:
1. Check this reference guide
2. Check the troubleshooting guide
3. Verify scheduled task status
4. Check logs for errors
5. Restart if needed: `.\stop-proxy.ps1; .\start-proxy-background.ps1`
