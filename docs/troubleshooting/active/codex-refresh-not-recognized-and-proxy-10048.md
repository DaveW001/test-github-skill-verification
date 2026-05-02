# Troubleshooting: `codex-refresh` Not Recognized + Proxy `WinError 10048`

**Status:** Active troubleshooting note  
**Applies To:** OpenCode plugin tooling + local Gemini proxy (`127.0.0.1:8000`)  
**Date Captured:** April 20, 2026

---

## Incident Summary

User observed:
- Very low model usage despite normal daily expectations
- "Total API errors" appearing in usage/monitoring
- PowerShell error when trying `codex-refresh`

Session findings:
- Proxy process was **already healthy and listening** on port 8000.
- Repeated daily log errors were **startup collisions**, not request failures.
- `codex-refresh` was run in plain PowerShell, but it is an **OpenCode plugin command** (not a standalone shell command).

---

## What We Observed (Ground Truth)

### 1) Proxy logs showed repeated bind collisions

Recent log pattern:
- `error while attempting to bind on address ('127.0.0.1', 8000)`
- `[winerror 10048] only one usage of each socket address ...`

Interpretation:
- A scheduled startup attempted to launch a new proxy instance while an existing instance was still running.
- This creates noisy startup errors, but does **not** necessarily indicate downtime.

### 2) Port check confirmed proxy was running

`netstat -ano | Select-String ":8000"` showed:
- `LISTENING` on `127.0.0.1:8000`
- active local established connection(s)

### 3) OAuth accounts were healthy

`codex-health` result during troubleshooting:
- 4 healthy, 0 unhealthy

### 4) User-facing PowerShell error cause

PowerShell error:
- `The term 'codex-refresh' is not recognized ...`

Cause:
- `codex-refresh` is available inside OpenCode agent/plugin context, not as a native PowerShell executable/cmdlet.

---

## Fix Applied

Executed token refresh in OpenCode context:
- `codex-refresh` → **4 refreshed, 0 failed**

Result:
- OAuth tokens validated and refreshed successfully.
- User confirmed Codex functionality after refresh.

---

## Correct Commands by Context

## A) Inside OpenCode session (agent/plugin context)

Use:
- `codex-refresh`
- `codex-health`
- `codex-dashboard`

## B) In standalone PowerShell terminal

Use:

```powershell
opencode auth status
opencode auth login
```

Use `opencode auth login` when you specifically want to open browser OAuth and re-login.

---

## Decision Tree (Fast)

1. See API errors + suspect auth issue.
2. Check proxy listener:
   - `netstat -ano | Select-String ":8000"`
3. If LISTENING exists, proxy may still be healthy; inspect logs for `WinError 10048` startup collision pattern.
4. Validate account health in OpenCode context:
   - `codex-health`
5. Refresh tokens in OpenCode context:
   - `codex-refresh`
6. If running from plain terminal and needing re-auth:
   - `opencode auth login`

---

## Preventive Follow-Up

- Improve starter task behavior so scheduled launch does not attempt to bind when proxy is already running.
- Keep this distinction explicit in docs and runbooks:
  - OpenCode plugin commands (`codex-*`) vs shell CLI commands (`opencode auth ...`).

---

## Related Documentation

- Gemini proxy active guide:  
  [gemini-proxy-down.md](file:///C:/development/opencode/docs/troubleshooting/active/gemini-proxy-down.md)
- Gemini proxy reference:  
  [gemini-proxy.md](file:///C:/development/opencode/docs/reference/gemini-proxy.md)
