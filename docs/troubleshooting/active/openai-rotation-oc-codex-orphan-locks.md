# OpenAI Model Rotation Failure (oc-codex-multi-auth Orphan Locks) - Troubleshooting Guide

**Status:** Resolved 2026-07-20 (active reference - keep for recurrence)
**Applies To:** OpenCode agents using `openai` provider models (GPT-5.x Codex / gpt-5.6-luna / gpt-5.6-sol, etc.)
**Symptoms:** OpenAI-backed agents hang/fail with repeated `AI_APICallError: The usage limit has been reached`, retrying the SAME account forever and never rotating, even though other accounts have quota. opencode-go-backed agents work fine.
**Mechanism:** `oc-codex-multi-auth` OpenCode plugin (NOT the Gemini proxy)
**Last Updated:** July 20, 2026

---

## One-Line Summary

Orphaned `proper-lockfile` `.lock` files from dead PIDs blocked the `oc-codex-multi-auth` plugin from reading/writing its account-health state, so it could never observe a rate limit or rotate to a healthy account. Deleting the orphan locks and restarting OpenCode fixes it.

---

## Quick Diagnosis Table

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| `AI_APICallError: The usage limit has been reached` repeating forever, no rotation | Orphan `.lock` file blocking account-health read/write | Delete orphan locks + restart OpenCode |
| Only `openai` provider failing; `opencode-go` fine | Not a network/provider outage - it's the rotation layer | Confirm it's the plugin, not the proxy |
| `codex-refresh` "not recognized" in PowerShell | `codex-*` are in-session plugin commands, not shell CLIs | Run them INSIDE an OpenCode session, or use the standalone CLI |
| Plugin "sees" 0 accounts / wrong accounts | Per-project account storage; wrong project key resolved | Find the correct per-project accounts file (see Storage Layout) |

**NOT these (common false leads):**
- **NOT the Gemini proxy** (`127.0.0.1:8000`, API keys, Scheduled Task). That serves Google models only. Unrelated.
- **NOT Antigravity** / `antigravity-accounts.json` under `%APPDATA%\opencode\`. That is the Antigravity container's own state. Unrelated. (This was a repeated misread during diagnosis - do not chase it.)

---

## Ground Truth: What Was Actually Wrong

### The rotation mechanism
OpenCode's OpenAI multi-account failover is provided by the **`oc-codex-multi-auth`** plugin (npm v6.10.0, by ndycode, MIT; https://github.com/ndycode/oc-codex-multi-auth). It is enabled in `~/.config/opencode/opencode.jsonc` under the `plugin` array (entry `"oc-codex-multi-auth"`). It supplies ChatGPT Plus/Pro OAuth for the `openai` provider, multi-account rotation (`rotationStrategy` default `hybrid`), account switching, health checks, quota visibility, diagnostics, and a 24-tool `codex-*` toolkit.

### Root cause
The plugin guards its accounts JSON with `proper-lockfile`, which writes a sibling `<file>.lock` containing the owning process metadata (`pid`, `hostname`, `cwd`, `startedAt`, `lastActive`). When an owning process dies without releasing the lock, the lock becomes **orphaned**. A stuck orphan lock prevented the plugin from updating/reading account health, so a rate-limited account was never flagged and rotation never triggered - every OpenAI request hammered the one exhausted account until it errored, then retried it again.

### Orphan locks found and removed (this incident)
| # | Lock file | PID | Status |
|---|-----------|-----|--------|
| 1 | `~/.opencode/oc-codex-multi-auth-accounts.json.lock` (global) | 66536 | DEAD - removed |
| 2 | `~/.opencode/projects/davewitkin-aa5b8f7d71d5/oc-codex-multi-auth-accounts.json.lock` (per-project) | 4176 | DEAD - removed (this was the effective one) |
| 3 | `~/.opencode/projects/opencode-2676293a9de0/oc-codex-multi-auth-accounts.json.lock` (per-project) | 54808 | DEAD - removed |

All three PIDs were confirmed dead via `Get-Process -Id <pid>` before deletion. After removal, OpenCode was restarted and OpenAI models worked.

---

## Storage Layout (critical - this is where people get lost)

`~` = `C:\Users\DaveWitkin` on this box.

| Purpose | Path |
|---------|------|
| OpenCode config (canonical here) | `~/.config/opencode/opencode.jsonc` |
| OpenCode auth tokens | `~/.opencode/auth/openai.json` |
| Plugin config | `~/.opencode/openai-codex-auth-config.json` (may be absent; plugin uses defaults) |
| **GLOBAL** account storage | `~/.opencode/oc-codex-multi-auth-accounts.json` |
| **PER-PROJECT** accounts (default-enabled) | `~/.opencode/projects/<project-key>/oc-codex-multi-auth-accounts.json` |
| Flagged accounts | `~/.opencode/oc-codex-multi-auth-flagged-accounts.json` |
| Plugin logs | `~/.opencode/logs/codex-plugin/` |
| Backups | `~/.opencode/backups/` and per-project backups |

**Two gotchas:**
1. **Per-project storage is the default and overrides global.** On this box the global accounts file does not exist - only the per-project one does. The EFFECTIVE accounts file here is `~/.opencode/projects/davewitkin-aa5b8f7d71d5/oc-codex-multi-auth-accounts.json` (v3 schema, `activeIndex: 0`, 4 account entries; index 0 was the rate-limited/exhausted one with `lastSwitchReason: rate-limit`).
2. **Multiple project keys exist.** Both `davewitkin-aa5b8f7d71d5` and `opencode-2676293a9de0` have appeared under `~/.opencode/projects/`. The plugin derives the project key by walking up to the project root, and that resolution has differed across sessions. Each per-project dir can carry its OWN accounts file AND its OWN `.lock`. You must check EVERY project dir, not just one.

---

## Resolution Procedure (do this when it recurs)

### Step 1 - Confirm it's the rotation layer, not the provider
- opencode-go agents work but `openai` agents fail with the usage-limit error => rotation layer.
- If BOTH fail => it's a real provider/network issue, not this.

### Step 2 - Find every orphan lock and check PID liveness
```powershell
Get-ChildItem -Path "$HOME\.opencode" -Recurse -File `
  -Filter 'oc-codex-multi-auth-accounts.json.lock' -ErrorAction SilentlyContinue |
  ForEach-Object {
    $lock = $_.FullName
    $j = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
    $alive = if ($j.pid) { [bool](Get-Process -Id $j.pid -ErrorAction SilentlyContinue) } else { $false }
    [pscustomobject]@{
      Lock = $lock
      PID = $j.pid
      Started = $j.startedAt
      LastActive = $j.lastActive
      Alive = $alive
      Orphan = -not $alive
    }
  } | Format-Table -AutoSize
```

### Step 3 - Delete ONLY orphaned locks (PID confirmed dead)
```powershell
# Re-verify the PID is dead, then:
Remove-Item -LiteralPath "<full-path-to-orphan-lock>" -Force
```
Never delete a lock whose PID is still alive - that's a live session holding it.

### Step 4 - Restart OpenCode
The plugin re-reads the accounts file and can rotate again. Test an `openai` model.

### Step 5 - If restart alone doesn't fix it
In order of least to most invasive:
1. From INSIDE an OpenCode session: `codex-health`, then `codex-doctor --fix`, then `codex-switch` to a known-good account.
2. Manually edit the effective per-project accounts JSON and set `activeIndex` to a known-good entry (back it up first).
3. Reinstall/refresh: `npx -y oc-codex-multi-auth@latest` (rewrites config, clears the plugin cache), then restart OpenCode.

---

## Commands by Context (frequent confusion)

| Where | Command |
|-------|---------|
| **Inside an OpenCode session** (plugin context) | `codex-health`, `codex-doctor`, `codex-switch`, `codex-refresh`, `codex-dashboard`, `codex-limits`, `codex-diag` |
| **Standalone terminal, no tokens needed** | `oc-codex-multi-auth status\|list\|warm\|doctor\|health\|limits\|dashboard\|diag` or `npx -y oc-codex-multi-auth@latest ...` |
| **Standalone terminal, re-auth** | `opencode auth status`, `opencode auth login` |

Useful env overrides: `CODEX_AUTH_ROTATION_STRATEGY=hybrid|sticky|round-robin`, `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0|1`, `ENABLE_PLUGIN_REQUEST_LOGGING=1`, `CODEX_PLUGIN_LOG_BODIES=1` (sensitive - logs request bodies), `CODEX_KEYCHAIN=1`.

---

## Decision Tree (fast path)

1. `openai` models failing, opencode-go fine? -> rotation layer (continue). Otherwise real outage.
2. Scan for `oc-codex-multi-auth-accounts.json.lock` under `~/.opencode` (Step 2).
3. Any lock with a DEAD PID? -> orphan (Step 3) -> delete -> restart (Step 4).
4. Still failing? -> in-session `codex-health` / `codex-doctor --fix` / `codex-switch` (Step 5).
5. Still failing? -> set `activeIndex` manually, or `npx -y oc-codex-multi-auth@latest` + restart.

---

## Prevention Checklist

- [ ] If OpenAI agents start retrying the same account endlessly, suspect an orphan lock FIRST.
- [ ] When cleaning up, check EVERY `~/.opencode/projects/*` dir for its own lock - not just the current project key.
- [ ] Only delete a lock after confirming its PID is dead.
- [ ] Keep the plugin updated; `npx -y oc-codex-multi-auth@latest` is the supported refresh path.
- [ ] Remember: `codex-*` only run inside a session; use the standalone CLI from a plain terminal.

---

## Agent/Environment Notes (read before troubleshooting on this box)

- **Native Read/Write/Edit file tools may fail with `Bun is not defined`.** When that happens, do the whole session via PowerShell through the bash tool (`Get-Content -Raw`, `Get-ChildItem`, `ConvertFrom-Json`, `Remove-Item`, here-strings for writes). Do NOT keep retrying the native tools.
- **Secrets handling:** the accounts JSON and `~/.opencode/auth/openai.json` contain OAuth refresh tokens. Never print, copy, commit, or paste token values. When inspecting, redact. This document deliberately records account structure/indices but NO token values and NO account email addresses.
- **Don't chase Antigravity.** `antigravity-accounts.json` under `%APPDATA%\opencode\` is the container's own state and is unrelated to OpenAI rotation.

---

## Related Documentation

- Gemini proxy (separate mechanism, unrelated): `docs/troubleshooting/active/gemini-proxy-down.md`
- `codex-refresh` context distinction: `docs/troubleshooting/active/codex-refresh-not-recognized-and-proxy-10048.md`
- OpenCode config reference: `docs/reference/opencode-configuration.md`
- Plugin README: https://github.com/ndycode/oc-codex-multi-auth

---

**Document Version:** 1.0
**Created:** July 20, 2026
**Resolved:** July 20, 2026 (3 orphan locks removed; restart; OpenAI models working)
