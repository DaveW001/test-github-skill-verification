# Gemini Proxy Down - Troubleshooting Guide

**Status:** Active troubleshooting guide  
**Applies To:** OpenCode agents using Google Gemini models via local proxy  
**Symptoms:** `fetch failed`, `ECONNREFUSED 127.0.0.1:8000`, `429 Too Many Requests`, proxy not responding  
**Last Updated:** April 20, 2026

---

## Quick Diagnosis Table

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| `ECONNREFUSED 127.0.0.1:8000` | Proxy not running | Start proxy: `Start-ScheduledTask -TaskName 'opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter'` |
| `429 Too Many Requests` + "all keys rate-limited" | All API keys hit rate limits | Wait 1-10 minutes; keys auto-recover with backoff |
| Proxy runs but OpenCode can't connect | Wrong baseURL in config | Verify `opencode.jsonc` has `baseURL: http://127.0.0.1:8000/v1beta` |
| Admin endpoints return 404 | Bug in route ordering | Fixed in main.py as of 2026-03-12; restart proxy if using old version |
| High failure rate on specific key | API key issue | Remove problematic key from `api_keys.txt` and reload |
| `403 Forbidden` + "API key was reported as leaked" | Key compromised/revoked by Google | Generate new key at [Google AI Studio](https://aistudio.google.com/app/apikey), replace in `api_keys.txt`, reload |
| Models return errors or are unavailable | Google revoked Pro-tier model access | Only Gemini 2.5 Flash, 3.1 Flash Lite, and Gemma models are available (see [Model Restrictions](#google-gemini-api-model-restrictions-2026-04-20)) |
| `WinError 10048` at startup, but proxy still responds | Scheduled startup collision (proxy already running on 8000) | Verify listener with `netstat -ano | findstr :8000`; treat as noisy restart attempt unless listener is missing |

Related troubleshooting note: [`codex-refresh` not recognized + proxy 10048](file:///C:/development/opencode/docs/troubleshooting/active/codex-refresh-not-recognized-and-proxy-10048.md)

---

## Step-by-Step Troubleshooting

## Quick Operator Commands (Current)

```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy

# One-shot health report
.\health-check.ps1

# Run monitor logic once
.\monitor-proxy.ps1

# Live connection tracking
.\monitor-connections.ps1
```

### Step 1: Check if Proxy is Running

```powershell
# Check if port 8000 is listening
netstat -ano | findstr :8000

# Expected output:
# TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    [PID]
```

**If no output:** Proxy is not running → Go to [Start Proxy](#start-the-proxy)

**If output shows:** Proxy is running → Go to [Check Key Health](#step-2-check-key-health)

---

### Step 2: Check Key Health

```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\proxy-status.ps1
```

**Look for:**
- ✅ **Status: RUNNING** - Good
- ❌ **Status: NOT RUNNING** - Proxy stopped → [Start Proxy](#start-the-proxy)
- ⚠️ **Keys showing "COOLDOWN"** - Normal, will recover automatically
- ❌ **All keys showing high fail counts** - Possible API key issues → [Check API Keys](#step-4-check-api-keys)

---

### Step 3: Check Logs

```powershell
# View last 50 lines
Get-Content C:\Users\DaveWitkin\.local\gemini-proxy\logs\proxy.log -Tail 50

# Look for patterns:
# - "Key ... failed with status 429" = Rate limited (normal, auto-recovers)
# - "Key ... failed with status 400" = Invalid key (needs removal)
# - "Key ... failed with status 503" = Google server error (temporary)
# - "All keys rate-limited" = All keys in cooldown (wait or add more keys)
```

---

### Step 4: Check API Keys

```powershell
# View current keys
Get-Content C:\Users\DaveWitkin\.local\gemini-proxy\api_keys.txt

# Should show one key per line, like:
# AIzaSyC40vaghThPpg86B2siZVWhCNUt6rF2AVA
# AIzaSyCqs5AFWOjpkt48qi-R_O-0pDEIy3UZgJM
# AIzaSyBX5g0ZGBc2RVd6WK14RzFERlKXNoyHfww
```

**If file is empty or missing:**
1. Check backup: `Get-ChildItem C:\Users\DaveWitkin\.local\gemini-proxy\api_keys.txt*`
2. Restore from backup or add new keys from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Common Issues & Solutions

### Issue 1: Proxy Not Running

**Symptoms:**
- `ECONNREFUSED 127.0.0.1:8000`
- `fetch failed` errors
- `netstat` shows nothing on port 8000

**Solutions:**

**Option A: Start via Scheduled Task (Recommended)**
```powershell
Start-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"
Start-Sleep 3
# Verify
netstat -ano | findstr :8000
```

**Option B: Start Manually**
```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\start-proxy-background.ps1
```

**Option C: Check Scheduled Task**
```powershell
Get-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-*"
# If missing, rehydrate via opencode-scheduler job definitions
```

---

### Issue 2: All Keys Rate-Limited (429 Errors)

**Symptoms:**
- Error message: "all keys rate-limited or in backoff"
- All keys show high `available_in` values in status
- Multiple "failed with status 429" in logs

**Solutions:**

**Option A: Wait (Recommended)**
- Keys auto-recover with exponential backoff
- Wait 5-10 minutes and try again
- Proxy will automatically use keys as they become available

**Option B: Add More Keys**
```powershell
# Get new API keys from Google AI Studio
# https://aistudio.google.com/app/apikey

# Edit keys file
notepad C:\Users\DaveWitkin\.local\gemini-proxy\api_keys.txt

# Add new key (one per line), save

# Reload without restart
Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" `
  -Method POST `
  -Headers @{"x-proxy-admin"="changeme_local_only"}
```

**Option C: Identify and Remove Problematic Key**
```powershell
# Check which key has highest failure rate
.\proxy-status.ps1

# Remove the key with highest fail count from api_keys.txt
# Reload keys
```

---

### Issue 3: Admin Endpoints Return 404

**Symptoms:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/status" `
  -Headers @{"x-proxy-admin"="changeme_local_only"}
# Error: 404 Not Found
```

**Cause:** Old version of `main.py` had catch-all route before admin endpoints.

**Solution:**
- **This was fixed on 2026-03-12** - The route ordering in `main.py` was corrected
- If you're still seeing this, restart the proxy to load the fixed version:

```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\stop-proxy.ps1
Start-Sleep 2
.\start-proxy-background.ps1
```

---

### Issue 4: Invalid or Leaked API Key (400/403 Errors)

**Symptoms:**
- Log shows: "Key ... failed with status 400" or "Key ... failed with status 403"
- Specific key has high fail count
- Error message mentions "API key not valid" or **"Your API key was reported as leaked"**

**Cause:** Google may revoke keys if they detect them in public repositories, logs, or other exposed locations. This happened on 2026-04-20 when all 3 keys were flagged as leaked.

**Solution:**
```powershell
# 1. Identify which key is failing
.\proxy-status.ps1

# 2. Edit keys file and remove the problematic key
notepad C:\Users\DaveWitkin\.local\gemini-proxy\api_keys.txt

# 3. Reload keys
Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" `
  -Method POST `
  -Headers @{"x-proxy-admin"="changeme_local_only"}

# 4. Get new key from Google AI Studio if needed
# https://aistudio.google.com/app/apikey
```

---

### Issue 5: OpenCode Not Using Proxy

**Symptoms:**
- OpenCode shows different models than expected
- No connection errors but using different provider
- Seeing "Antigravity" models when expecting Gemini

**Diagnosis:**
```powershell
# Check OpenCode configuration
cat C:\Users\DaveWitkin\.config\opencode\opencode.jsonc | findstr "baseURL"

# Should show: "baseURL": "http://127.0.0.1:8000/v1beta"
```

**Solution:**
```powershell
# Edit OpenCode config
notepad C:\Users\DaveWitkin\.config\opencode\opencode.jsonc

# Verify this section exists:
"google": {
  "options": {
    "baseURL": "http://127.0.0.1:8000/v1beta",
    "apiKey": "proxy-will-replace-this"
  }
}
```

---

### Issue 6: Scheduled Task Not Working

**Symptoms:**
- Proxy doesn't start at logon
- Task shows "Disabled" or "Ready" but never runs

**Diagnosis:**
```powershell
# Check task status (starter + monitor)
Get-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-*" | Format-List

# Check task history
Get-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-*" | Get-ScheduledTaskInfo
```

**Solutions:**

**If task is disabled:**
```powershell
Enable-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"
```

**If task is missing:**
```powershell
# Rehydrate using opencode-scheduler job definitions and sync
# (Do not recreate legacy manual tasks)
```

**If task fails to start:**
```powershell
# Check if start-proxy-quiet.ps1 exists
Test-Path C:\Users\DaveWitkin\.local\gemini-proxy\start-proxy-quiet.ps1

# If missing, recreate management scripts
# (See reference doc for script content)
```

---

## Diagnostic Commands Reference

### Quick Status Check
```powershell
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\proxy-status.ps1
```

### Test Proxy Connection
```powershell
# Test basic connectivity
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000

# Test admin endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:8000/status" `
  -Headers @{"x-proxy-admin"="changeme_local_only"}

# Test Gemini API through proxy
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1beta/models" -Method GET
```

### Process Management
```powershell
# Find proxy process
tasklist | findstr python
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Kill proxy process (if needed)
taskkill /PID [PID] /F
# Or
Stop-Process -Id [PID] -Force
```

### Log Analysis
```powershell
# View recent errors
Get-Content C:\Users\DaveWitkin\.local\gemini-proxy\logs\proxy.log | 
  Select-String "ERROR|WARNING|failed" | 
  Select-Object -Last 20

# Count errors by key
Get-Content C:\Users\DaveWitkin\.local\gemini-proxy\logs\proxy.log | 
  Select-String "failed" | 
  Group-Object { $_ -match "AIzaSy(\w+)" } | 
  Select-Object Name, Count
```

---

## Recovery Procedures

### Full Restart (Nuclear Option)

If nothing else works, do a full restart:

```powershell
# 1. Stop proxy
Stop-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"
cd C:\Users\DaveWitkin\.local\gemini-proxy
.\stop-proxy.ps1
Start-Sleep 3

# 2. Verify stopped
netstat -ano | findstr :8000  # Should show nothing

# 3. Clear old logs (optional)
Move-Item logs\proxy.log logs\proxy.log.old -Force

# 4. Start fresh
.\start-proxy-background.ps1

# 5. Verify
.\proxy-status.ps1
```

### Reset to Defaults

If configuration is corrupted:

```powershell
# 1. Backup current setup
Copy-Item api_keys.txt api_keys.txt.backup
Copy-Item main.py main.py.backup

# 2. Check git status
cd C:\Users\DaveWitkin\.local\gemini-proxy
git status

# 3. Restore original files from git
git checkout main.py
git checkout README.md

# 4. Re-apply route ordering fix (see reference doc)
# Edit main.py to move admin endpoints before catch-all route

# 5. Restart proxy
.\stop-proxy.ps1
.\start-proxy-background.ps1
```

---

## Prevention Checklist

- [ ] **Monitor logs weekly** - Check for recurring errors
- [ ] **Verify key health** - Run `proxy-status.ps1` periodically
- [ ] **Keep keys rotated** - Add/remove keys as needed
- [ ] **Update documentation** - Log any changes made
- [ ] **Test after Windows updates** - Some updates may affect scheduled tasks

---

## Google Gemini API Model Restrictions (2026-04-20)

**⚠️ Critical: Google has restricted Pro-tier model access per account/key.**

As of April 2026, Google AI Studio has restricted model access **per account**, with significant differences:

| Model                  | Dave (`AIzaSyCND2NS...`) | Raquel (`AIzaSyAIHoxs...`) | Tiberius (`AIzaSyDQJD_p...`) |
| ---------------------- | ------------------------ | -------------------------- | ----------------------------- |
| Gemini 3.1 Pro         | ✅ Available (limited)   | **BLOCKED (0 quota)**      | **BLOCKED (0 quota)**         |
| Gemini 2.5 Pro         | ✅ Available (limited)   | **BLOCKED (0 quota)**      | **BLOCKED (0 quota)**         |
| Gemini 2.5 Flash       | ✅ Available             | ✅ Available                | ✅ Available                  |
| Gemini 3.1 Flash Lite  | ✅ Available             | ✅ Available                | ✅ Available                  |
| Gemma (open-source)    | ✅ Available             | ✅ Available                | ✅ Available                  |

**Key takeaway:** Only Dave's key (`davidawitkin@gmail.com`) retains Gemini 3.1 Pro access. Raquel's and Tiberius's keys are Flash-only. The reason for this account-level difference is unknown.

**Proxy behavior impact:** Round-robin rotation means Pro-tier requests generate 2 failures (Raquel + Tiberius) before hitting Dave's key. This wastes quota and increases latency.

**Symptoms you might see:**
- Intermittent 403 errors on Gemini 3.1 Pro requests (2 of 3 keys will fail)
- Higher-than-expected backoff times on Pro model requests
- Flash models work reliably across all keys

**Workaround:**
1. Use Flash models when possible (all 3 keys work)
2. Expect latency on Pro-tier requests due to round-robin failures
3. Consider alternative providers for Pro-tier capability

---

## Related Documentation

- **Full Reference:** `C:\development\opencode\docs\reference\gemini-proxy.md`
- **AGENTS.md Entry:** Line 95-100 in `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
- **Proxy Location:** `C:\Users\DaveWitkin\.local\gemini-proxy\`
- **Evaluation Report:** `C:\development\playground\gemini-proxy-evaluation-report.md`

---

## Quick Reference Card

```powershell
# Status
.\proxy-status.ps1

# Start
Start-ScheduledTask -TaskName "opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter"

# Stop
.\stop-proxy.ps1

# Restart
.\stop-proxy.ps1; .\start-proxy-background.ps1

# View logs
Get-Content logs\proxy.log -Tail 20

# Reload keys
Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" `
  -Method POST -Headers @{"x-proxy-admin"="changeme_local_only"}
```

---

**Document Version:** 1.0  
**Created:** March 12, 2026  
**Last Verified:** Proxy running with 3 keys, opencode-scheduler tasks active, health-check exit 0
