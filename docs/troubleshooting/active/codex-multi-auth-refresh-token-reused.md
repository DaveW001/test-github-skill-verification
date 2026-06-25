# Troubleshooting: Codex Multi-Auth `refresh_token_reused` / Disabled Account

**Status:** Active troubleshooting note  
**Plugin:** `oc-codex-multi-auth` v6.1.8 (ndycode, third-party)  
**Date Captured:** May 25, 2026  
**Last Revised:** June 22, 2026 (corrected architecture description - see "Revision Notes")

---

## Incident Summary

User observed Codex model requests failing with:
```
All 1 account(s) failed (server errors or auth issues).
```

`codex-health` reported `0 healthy, 1 unhealthy` with `refresh_token_reused` error. The actual root cause was **not** an expired token - it was a **valid account marked `enabled: false`** by the plugin's scope validation logic.

> **The "1 account" in the error message is significant.** It means the plugin's runtime resolved exactly one account (typically the global auth fallback) and that one account failed. When the per-project accounts file is empty, the plugin falls back to the global OpenCode auth store. See [Architecture Context](#architecture-context) below.

---

## Architecture Context

OpenCode's auth storage has **three layers**. Understanding how they interact is essential for diagnosing multi-auth failures.

### Layer 1: OpenCode Core Auth (GLOBAL - Fallback Source)

**File:** `~/.local/share/opencode/auth.json`  
**Source:** `packages/opencode/src/auth/index.ts` - `path.join(Global.Path.data, "auth.json")`

Stores **one entry per provider** (`codex`, `openai`, `zai-coding-plan`, etc.). This is a single global file shared across all projects.

**Critical behavior:** When the plugin's multi-account storage (Layer 2) is empty for the current project, the plugin's `initializeFromStorage(authFallback, stored)` method **falls back to this global auth entry** and creates a single ad-hoc account from it. This is why the error says "All **1** account(s) failed" even when `codex-list` reports "No accounts configured" - the CLI diagnostic tools read Layer 2 only, but the runtime request path uses the Layer 1 fallback.

### Layer 2: Plugin Multi-Account Storage (PER-PROJECT by default, GLOBAL optional)

**Plugin:** `oc-codex-multi-auth`  
**GitHub:** https://github.com/ndycode/oc-codex-multi-auth  
**Installed via:** `~/.config/opencode/opencode.jsonc` plugin array

The plugin stores multi-account data in **two possible locations**, controlled by the `perProjectAccounts` config flag (default: `true`):

| Mode | Config | Storage Path |
|------|--------|--------------|
| **Per-project (DEFAULT)** | `perProjectAccounts: true` | `~/.opencode/projects/<project-key>/oc-codex-multi-auth-accounts.json` |
| **Global** | `perProjectAccounts: false` or `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0` | `~/.opencode/oc-codex-multi-auth-accounts.json` |

The `<project-key>` is derived from the project root path. `process.cwd()` determines which project directory is active at request time.

**Per-project is the default but is NOT required.** To force a single global pool of accounts shared across all projects:
- Set env var `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0`, OR
- Set `"perProjectAccounts": false` in `~/.opencode/openai-codex-auth-config.json`

### Layer 3: Windows Credential Store (OPT-IN)

`cmdkey /list` - no entries unless `CODEX_KEYCHAIN=1` is set. Not commonly used.

### Important

`ndycode/oc-codex-multi-auth` is a **third-party community plugin**, not an official OpenCode plugin. OpenCode has its own built-in `CodexAuthPlugin` (at `packages/opencode/src/plugin/codex.ts`) which uses the global auth store (Layer 1). The multi-auth plugin extends this with rotation, health-aware failover, and multi-account pools.

**The two layers are complementary, not conflicting:**
- Layer 1 (global auth) is the **fallback** when Layer 2 (plugin storage) is empty
- Layer 2 (plugin storage) is the **recommended** approach for multi-account rotation
- CLI tools (`codex-list`, `codex-health`, `codex-doctor`) read Layer 2 only
- The runtime request path checks Layer 2 first, then falls back to Layer 1

---

## Recommended Setup: Multi-Account Rotation

For resilience against rate limits and token burnout, configure **2-3 accounts** in the plugin's multi-account pool. The plugin handles automatic rotation, health-aware failover, and per-account cooldowns.

### Initial Setup

```powershell
# 1. Install or update the plugin config
npx -y oc-codex-multi-auth@latest

# 2. Authenticate - the plugin provides the multi-account OAuth flow
opencode auth login
# -> Browser opens for OAuth
# -> Plugin prompts: "Add another account?" after each login
# -> Repeat for each account (recommended: 2-3)

# 3. Verify accounts are stored
codex-list          # Should show all accounts
codex-health        # Should show all healthy
codex-status        # Shows active account + limits
```

### Operating Commands

| Command | Purpose |
|---------|---------|
| `codex-list` | List all accounts and active index |
| `codex-switch` | Switch active account (interactive picker) |
| `codex-status` | Show detailed status + rate limits |
| `codex-health` | Validate refresh tokens for all accounts |
| `codex-doctor --fix` | Diagnose and auto-fix (refresh tokens, switch to healthiest) |
| `codex-refresh` | Manually refresh all OAuth tokens |
| `codex-dashboard` | Live view of account eligibility, retry budgets, queue health |
| `codex-limits` | Show 5-hour and weekly usage limits |
| `codex-export` | Backup accounts to JSON |
| `codex-import` | Restore accounts from backup |
| `codex-label` | Set display label (e.g., "Work", "Personal") |
| `codex-tag` | Tag accounts for filtering |
| `codex-remove` | Remove an account by index |

### Backup Before Changes

```powershell
# Export current accounts before any auth changes
codex-export  # Auto-generates timestamped backup
```

---

## Root Cause (Original Incident)

The per-project accounts file contained one valid account with:
- `refreshToken`: valid (not expired)
- `expiresAt`: future date (June 2, 2026)
- `enabled`: **false**
- `accountNote`: "Re-auth required for missing OAuth scope(s): openid, profile, email, offline_access."

The plugin's account loader **excludes disabled accounts** from the routing pool. All `activeIndexByFamily` entries pointed to index 0 (the disabled account), so every request failed even though the underlying token was valid.

### Why Was It Disabled?

The plugin's OAuth scope validation (`getMissingRequiredOAuthScopes`) flagged the account during a previous session. Required scopes are: `openid, profile, email, offline_access`. However, the token had been re-authenticated since then with proper scopes, and the plugin's stale scope check had disabled it incorrectly.

---

## Fix: Re-enable a Valid Account

Set `"enabled": true` in the accounts file:

**Per-project path (default):**
```
~/.opencode/projects/<project-key>/oc-codex-multi-auth-accounts.json
```

**Global path (if `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0`):**
```
~/.opencode/oc-codex-multi-auth-accounts.json
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

## Fix: Burned Refresh Token (June 2026 Variant)

If you reauthorized multiple accounts via `opencode auth login` but the plugin's storage is empty, the refresh tokens were likely **burned**. Here's why:

1. OpenCode's global auth store (`auth.json`) holds **only one entry per provider**
2. Each `opencode auth login` OAuth flow rotates the refresh token, invalidating the previous one
3. If the plugin's multi-account storage wasn't populated (e.g., plugin not active during login, or per-project file empty), the 3 accounts collapsed into a single global entry - and only the **last** login's token survived
4. Earlier tokens are now permanently invalid

### Recovery Steps

```powershell
# 1. Check if the plugin storage is empty
codex-list
# If "No accounts configured" -> plugin storage is empty, using global fallback

# 2. Check the global fallback
codex-health
# The runtime is using the single global auth.json entry - if it's burned, all requests fail

# 3. Re-authorize properly through the PLUGIN's multi-account flow
#    Make sure the plugin is loaded FIRST
npx -y oc-codex-multi-auth@latest   # ensures plugin config is current
opencode auth login                  # use the plugin's "Add another account?" prompt

# 4. Verify accounts saved to plugin storage
codex-list    # should now show multiple accounts
codex-health  # all should be healthy
```

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
# (run from PowerShell, replace <project-key> with actual key)
$acctFile = "$env:USERPROFILE\.opencode\projects\<project-key>\oc-codex-multi-auth-accounts.json"
$data = Get-Content $acctFile -Raw | ConvertFrom-Json
$data.accounts | ForEach-Object {
    $i = [array]::IndexOf($data.accounts, $_)
    "Account $i: enabled=$($_.enabled), expires=$($_.expiresAt), note=$($_.accountNote)"
}

# Check the GLOBAL fallback token (Layer 1)
$authFile = "$env:USERPROFILE\.local\share\opencode\auth.json"
$auth = Get-Content $authFile -Raw | ConvertFrom-Json
$auth.openai | Format-List scope, expiresAt, refreshToken

# Core auth health
opencode auth status
opencode auth list

# Full diagnostic with auto-fix
codex-doctor --fix
```

---

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `refresh_token_reused` | Active account is disabled or using stale refresh token | Enable the valid account or re-auth via plugin flow |
| Account `enabled: false` with misleading note | Plugin scope validation flagged account incorrectly | Set `enabled: true`, verify token has required scopes |
| Empty accounts array | Plugin never initialized, or accounts saved to wrong project | Run `opencode auth login` with plugin active; verify with `codex-list` |
| "All 1 account(s) failed" but `codex-list` shows 0 accounts | Runtime using global auth fallback (Layer 1), which is burned | Re-auth through plugin multi-account flow; see [Fix: Burned Refresh Token](#fix-burned-refresh-token-june-2026-variant) |
| `codex-health` shows 0 healthy after re-login | Login saved to global auth only, not plugin storage | Ensure plugin is active during `opencode auth login`; use "Add another account?" prompt |
| Different tokens in different projects | Per-project storage (plugin default) | Either re-auth from each project, OR disable per-project with `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0` |
| Multiple reauthorizations collapse to one account | Global auth.json stores one entry per provider; refresh token rotation burns earlier tokens | Use the plugin's multi-account flow, not repeated `opencode auth login` |

---

## If Re-Auth Is Needed

```powershell
# Ensure the plugin is installed and current
npx -y oc-codex-multi-auth@latest

# Run OpenCode auth login - the plugin intercepts to provide multi-account flow
opencode auth login
# -> Browser OAuth
# -> Plugin prompts "Add another account?" - answer YES for each additional account
# -> Repeat for 2-3 accounts total
```

After re-auth, verify:
1. `codex-list` shows all accounts (not just one)
2. All accounts have `enabled: true`
3. `expiresAt` is a future date on each
4. `codex-health` shows all healthy

---

## Decision Tree (Fast)

1. See `refresh_token_reused` or "All N account(s) failed" error
2. Run `codex-list` - how many accounts are stored in the plugin?
   - **0 accounts** -> runtime is using global fallback (Layer 1); likely burned token -> [Fix: Burned Refresh Token](#fix-burned-refresh-token-june-2026-variant)
   - **1+ accounts** -> continue to step 3
3. Run `codex-health` - which accounts are unhealthy?
4. Read the accounts file - check `enabled` field on each account
5. If an account has a valid token and `expiresAt` in the future but `enabled: false` -> **set `enabled: true`**
6. If all accounts have stale/expired tokens -> run `opencode auth login` with the plugin active
7. Restart OpenCode
8. Verify with `codex-health` and a test request

---

## Lessons Learned

1. **Global auth is the fallback, not a replacement for multi-account storage.** When the plugin's storage is empty, the runtime creates a single ad-hoc account from the global auth entry. This works, but provides no rotation or failover - a single burned token takes down all requests.
2. **The plugin can disable valid accounts.** The `enabled: false` flag with a misleading `accountNote` was the sole blocker - the token was actually valid. Always check the raw JSON.
3. **Always read the actual account file state before forming conclusions.** Surface-level tool output (`codex-health` -> "unhealthy", or `codex-list` -> "0 accounts") may mask the real issue. The error message's account count tells you what the *runtime* sees, which includes the fallback.
4. **Per-project storage is the default but not required.** Use `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0` for a single global account pool if per-project fragmentation causes issues.
5. **Repeated `opencode auth login` burns refresh tokens.** The global auth store holds one entry per provider; each OAuth flow rotates the refresh token. Use the plugin's "Add another account?" prompt for multi-account setup.
6. **CLI diagnostics and the runtime see different things.** `codex-list`/`codex-health` read plugin storage (Layer 2) only. The runtime request path checks Layer 2 first, then falls back to Layer 1. This is why `codex-list` can show "0 accounts" while the error says "1 account failed."

---

## Revision Notes

**June 22, 2026:** Corrected the architecture description. The original version stated the plugin's auth is "per-project" in contrast to OpenCode's "global" core auth, implying they are separate, non-interacting systems. This is incorrect:
- The plugin's storage defaults to per-project but supports global storage (`CODEX_AUTH_PER_PROJECT_ACCOUNTS=0`)
- The plugin's runtime **falls back to** the global auth store (Layer 1) when its own storage (Layer 2) is empty - they are complementary
- The "All 1 account(s) failed" error specifically indicates the global fallback is in use (1 account = the fallback entry)
- CLI diagnostic tools read Layer 2 only, which is why they can show "0 accounts" while the runtime reports "1 account failed"

---

## Related Documentation

- Command context troubleshooting:  
  [codex-refresh-not-recognized-and-proxy-10048.md](file:///C:/development/opencode/docs/troubleshooting/active/codex-refresh-not-recognized-and-proxy-10048.md)
- Gemini proxy active guide:  
  [gemini-proxy-down.md](file:///C:/development/opencode/docs/troubleshooting/active/gemini-proxy-down.md)
- Gemini proxy reference:  
  [gemini-proxy.md](file:///C:/development/opencode/docs/reference/gemini-proxy.md)
- Comprehensive OpenAI multi-auth guide:  
  [openai-codex-multi-auth-guide.md](file:///C:/development/opencode/docs/troubleshooting/active/openai-codex-multi-auth-guide.md)