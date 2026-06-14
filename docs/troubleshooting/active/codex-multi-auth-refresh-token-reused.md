# Troubleshooting: Codex Multi-Auth `refresh_token_reused` / Disabled Account

**Status:** Active troubleshooting note  
**Plugin:** `oc-codex-multi-auth` v6.1.8 (ndycode, third-party)  
**Date Captured:** May 25, 2026

---

## Incident Summary

User observed Codex model requests failing with:
```
All 1 account(s) failed (server errors or auth issues).
```

`codex-health` reported `0 healthy, 1 unhealthy` with `refresh_token_reused` error. The actual root cause was **not** an expired token — it was a **valid account marked `enabled: false`** by the plugin's scope validation logic.

---

## Architecture Context

OpenCode's auth storage has **three layers** that can create confusion:

### Layer 1: OpenCode Core Auth (GLOBAL)

**File:** `~/.local/share/opencode/auth.json`  
**Source:** `packages/opencode/src/auth/index.ts` — `path.join(Global.Path.data, "auth.json")`

Stores one entry per provider (`codex`, `openai`, `zai-coding-plan`, etc.). This is a **single global file** shared across all projects, not per-project.

### Layer 2: Third-Party Plugin `oc-codex-multi-auth` (PER-PROJECT)

**GitHub:** https://github.com/ndycode/oc-codex-multi-auth  
**Installed via:** `~/.config/opencode/opencode.json` plugin array

Stores multi-account data in **per-project** files:
```
~/.opencode/projects/<hash>/oc-codex-multi-auth-accounts.json
```

The hash is derived from the project path. `process.cwd()` determines which project directory is active at request time.

**This is the file that matters for Codex model requests when the plugin is installed.**

### Layer 3: Windows Credential Store (OPT-IN)

`cmdkey /list` — no entries unless `CODEX_KEYCHAIN=1` is set. Not commonly used.

### Important

`ndycode/oc-codex-multi-auth` is a **third-party community plugin**, not an official OpenCode plugin. OpenCode has its own built-in `CodexAuthPlugin` (at `packages/opencode/src/plugin/codex.ts`) which uses the global auth store. The two can conflict (see OpenCode GitHub issue #10898).

---

## Root Cause

The per-project accounts file contained one valid account with:
- `refreshToken`: valid (not expired)
- `expiresAt`: future date (June 2, 2026)
- `enabled`: **false**
- `accountNote`: "Re-auth required for missing OAuth scope(s): openid, profile, email, offline_access."

The plugin's account loader **excludes disabled accounts** from the routing pool. All `activeIndexByFamily` entries pointed to index 0 (the disabled account), so every request failed even though the underlying token was valid.

### Why Was It Disabled?

The plugin's OAuth scope validation likely flagged the account during a previous session. However, the token had been re-authenticated since then with proper scopes, and the plugin's stale scope check had disabled it incorrectly.

---

## Fix

Set `"enabled": true` in the per-project accounts file:

```
~/.opencode/projects/<hash>/oc-codex-multi-auth-accounts.json
```

```diff
  {
    "accountId": "...",
-   "enabled": false,
+   "enabled": true,
-   "accountNote": "Re-auth required for missing OAuth scope(s): ...",
+   "accountNote": "Primary account"
  }
```

Restart OpenCode after making this change.

---

## Diagnostic Commands

```powershell
# Check which project directories have accounts
Get-ChildItem "$env:USERPROFILE\.opencode\projects" -Recurse -Filter "*codex*accounts*" |
  Select-Object FullName, LastWriteTime, Length

# Inspect the current project's accounts file
codex-list
codex-health
codex-status

# Check the raw JSON for enabled/disabled state
# (run from PowerShell, replace <hash> with actual project hash)
python -c "
import json
with open(r'C:\Users\<USER>\.opencode\projects\<HASH>\oc-codex-multi-auth-accounts.json') as f:
    data = json.load(f)
for i, a in enumerate(data['accounts']):
    print(f'Account {i}: enabled={a[\"enabled\"]}, expires={a.get(\"expiresAt\")}, note={a.get(\"accountNote\", \"none\")}')
"

# Core auth health
opencode auth status
opencode auth list
```

---

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `refresh_token_reused` | Active account is disabled or using stale refresh token | Enable the valid account or re-auth from project directory |
| Account `enabled: false` with misleading note | Plugin scope validation flagged account incorrectly | Set `enabled: true`, verify token has required scopes |
| Empty accounts array | Migration failed or plugin never initialized for this project | Run `opencode auth login` from the project directory |
| Different tokens in different projects | Per-project storage (plugin design) | Re-auth from the affected project directory |
| `codex-health` shows 0 healthy after re-login | Re-login saved to wrong project directory | Verify `process.cwd()` matches the intended project |

---

## If Re-Auth Is Needed

```bash
# Navigate to the project directory FIRST
cd C:\development\playground

# Run OpenCode auth login from this directory
# This ensures the plugin writes to the correct project directory
opencode auth login
```

After re-auth, verify:
1. The new account appears in the per-project file
2. `enabled` is `true`
3. `expiresAt` is a future date

---

## Token Mapping (Observed in This Incident)

| Location | Token Prefix | Expiry | Status |
|----------|-------------|--------|--------|
| Global auth `codex` | `rt_eop7...` | Jan 31, 2026 | Expired (pre-plugin era) |
| Global auth `openai` | `rt_-y6C...` | Jun 2, 2026 | Valid |
| Plugin (playground) | `rt_-y6C...` | Jun 2, 2026 | Valid (was disabled) |
| Plugin (email-triage) | `rt_pUqT...` | Apr 29, 2026 | Expired |
| Plugin (opencode) | `rt_7MSb...` | Mar 25, 2026 | Expired |

The `rt_-y6C...` token appears in both global `openai` and plugin account — these are the same credential shared between layers. The global `codex` entry (`rt_eop7...`) is a different, older token from before the multi-auth plugin consolidated authentication.

---

## Decision Tree (Fast)

1. See `refresh_token_reused` or "all accounts failed" error
2. Run `codex-health` to confirm which accounts are unhealthy
3. Read the per-project accounts file — check `enabled` field on each account
4. If an account has a valid token and `expiresAt` in the future but `enabled: false` → **set `enabled: true`**
5. If all accounts have stale/expired tokens → run `opencode auth login` from the project directory
6. Restart OpenCode
7. Verify with `codex-health` and a test request

---

## Lessons Learned

1. **OpenCode core auth is global, the plugin's auth is per-project.** Don't conflate the two — they are separate systems with separate storage.
2. **The plugin can disable valid accounts.** The `enabled: false` flag with a misleading accountNote was the sole blocker — the token was actually valid.
3. **Always read the actual account file state before forming conclusions.** Surface-level tool output (`codex-health` → "unhealthy") may mask the real issue.
4. **Per-project token fragmentation is real but plugin-driven.** Users who re-authenticate from different project directories may end up with valid tokens in the wrong project's storage.

---

## Related Documentation

- Command context troubleshooting:  
  [codex-refresh-not-recognized-and-proxy-10048.md](file:///C:/development/opencode/docs/troubleshooting/active/codex-refresh-not-recognized-and-proxy-10048.md)
- Gemini proxy active guide:  
  [gemini-proxy-down.md](file:///C:/development/opencode/docs/troubleshooting/active/gemini-proxy-down.md)
- Gemini proxy reference:  
  [gemini-proxy.md](file:///C:/development/opencode/docs/reference/gemini-proxy.md)
