# OpenAI / Codex Multi-Auth: Setup & Troubleshooting Guide

**Status:** Active reference guide  
**Applies to:** OpenCode with `oc-codex-multi-auth` plugin (v6.1.8+)  
**Last Updated:** June 22, 2026  

---

## Overview

OpenCode uses the third-party `oc-codex-multi-auth` plugin to manage multiple OpenAI/Codex OAuth accounts with automatic rotation, health-aware failover, and per-account cooldowns. This guide covers setup, daily operation, and troubleshooting.

---

## Table of Contents

1. [Architecture: How Auth Layers Work](#1-architecture-how-auth-layers-work)
2. [Initial Setup: Multi-Account Configuration](#2-initial-setup-multi-account-configuration)
3. [Daily Operation Commands](#3-daily-operation-commands)
4. [Choosing Per-Project vs Global Storage](#4-choosing-per-project-vs-global-storage)
5. [Troubleshooting Decision Tree](#5-troubleshooting-decision-tree)
6. [Common Errors & Fixes](#6-common-errors--fixes)
7. [Step-by-Step Fix Runbook: Burned Token Recovery](#7-step-by-step-fix-runbook-burned-token-recovery)
8. [Best Practices](#8-best-practices)

---

## 1. Architecture: How Auth Layers Work

OpenCode auth has three layers. Understanding the interaction is critical.

### Layer 1: OpenCode Core Auth (Global - Fallback Source)

| Property | Value |
|----------|-------|
| **File** | `~/.local/share/opencode/auth.json` |
| **Scope** | Global, shared across all projects |
| **Capacity** | One entry per provider (`openai`, `codex`, etc.) |
| **Role** | Fallback when plugin storage is empty |
| **Written by** | `opencode auth login` (standard OAuth flow) |

### Layer 2: Plugin Multi-Account Storage

| Property | Value |
|----------|-------|
| **Plugin** | `oc-codex-multi-auth` (ndycode) |
| **Per-project path (default)** | `~/.opencode/projects/<project-key>/oc-codex-multi-auth-accounts.json` |
| **Global path** | `~/.opencode/oc-codex-multi-auth-accounts.json` |
| **Capacity** | Multiple accounts with rotation |
| **Role** | Primary source for runtime requests |
| **Written by** | Plugin's multi-account OAuth flow |

### Layer 3: OS Keychain (Opt-in)

| Property | Value |
|----------|-------|
| **Activation** | `CODEX_KEYCHAIN=1` env var |
| **Role** | Secure credential backend instead of JSON files |
| **Manage via** | `codex-keychain status/migrate/rollback` |

### Key Insight: Why "0 Accounts" but "1 Account Failed"

This is the #1 source of confusion:
- `codex-list` reads Layer 2 only -> shows "0 accounts" (empty plugin storage)
- The runtime falls back to Layer 1 -> uses the single global `openai` entry -> reports "All 1 account(s) failed"
- The "1 account" IS the global fallback, and it's failing (likely burned refresh token)

**Fix:** Populate Layer 2 with multiple accounts via the plugin flow (see [Section 7: Fix Runbook](#7-step-by-step-fix-runbook-burned-token-recovery)).

---

## 2. Initial Setup: Multi-Account Configuration

### Prerequisites

- OpenCode installed and configured
- `oc-codex-multi-auth` in your `opencode.jsonc` plugin array:
  ```jsonc
  {
    "plugin": {
      "install": ["oc-codex-multi-auth"]
    }
  }
  ```

### Step-by-Step Setup

```powershell
# Step 1: Install/update the plugin config
npx -y oc-codex-multi-auth@latest

# Step 2: Authenticate with multiple accounts
opencode auth login
# -> Browser opens for OAuth
# -> After login, plugin prompts: "Add another account?"
# -> Select YES and authenticate with a second account
# -> Repeat for a third account (recommended: 2-3 accounts)

# Step 3: Verify all accounts are stored
codex-list          # Should show all accounts
codex-health        # Should show all healthy
codex-status        # Shows active account + limits
```

> **Important:** Steps 1 and 2 run in an **external terminal** (PowerShell). Step 3 commands are **agent tools** - ask the OpenCode agent to run them. See [Section 7](#7-step-by-step-fix-runbook-burned-token-recovery) for the full breakdown of who runs what and where.

### Recommended Account Count

| Accounts | Use Case |
|----------|----------|
| 1 | Minimum (no rotation benefit over global fallback) |
| **2-3** | **Recommended** - rotation on rate limits, failover on token burn |
| 4+ | Heavy usage, team scenarios |

### Labeling Accounts (Recommended)

```powershell
# Set readable labels for easy identification
codex-label --index 1 --label "Primary"
codex-label --index 2 --label "Backup"
codex-label --index 3 --label "Team"

# Tag for grouping
codex-tag --index 1 --tags "work,priority"
codex-tag --index 2 --tags "personal"
```

---

## 3. Daily Operation Commands

### Quick Reference

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `codex-list` | List all accounts + active index | Check what's configured |
| `codex-status` | Detailed status + rate limits | Before heavy usage |
| `codex-health` | Validate all refresh tokens | After errors or weekly |
| `codex-switch` | Change active account | Manual rotation |
| `codex-refresh` | Refresh all tokens | Force token refresh |
| `codex-doctor` | Diagnose issues | Troubleshooting |
| `codex-doctor --fix` | Auto-fix (refresh + switch) | Quick remediation |
| `codex-limits` | Show usage limits | Monitor consumption |
| `codex-dashboard` | Live overview | Real-time monitoring |
| `codex-export` | Backup accounts to JSON | Before changes |
| `codex-import` | Restore from backup | Recovery |
| `codex-next` | Recommended next action | When unsure |

> **These are agent tools, not terminal commands.** Ask the OpenCode agent to run them: "run codex-list", "check codex health", etc. Typing them in an external terminal will fail.

### Backup & Recovery

```powershell
# ALWAYS export before making auth changes
codex-export  # auto-generates timestamped backup

# Or specify a path
codex-export --path ~/codex-backup.json

# Preview import (dry run)
codex-import --path ~/codex-backup.json --dry-run

# Restore (auto-backs up current state first)
codex-import --path ~/codex-backup.json
```

---

## 4. Choosing Per-Project vs Global Storage

The plugin defaults to **per-project** storage. Here's how to choose:

### Per-Project (Default)

**Pros:**
- Different accounts for different projects (e.g., work vs personal)
- Isolation between projects

**Cons:**
- Must re-auth in each project directory
- Token fragmentation across projects
- Can cause "wrong project, no accounts" confusion

### Global (Single Pool)

**Pros:**
- One set of accounts shared across all projects
- No fragmentation
- Simpler mental model

**Cons:**
- All projects share the same accounts/rate limits

### Switching to Global Storage

```powershell
# Option A: Environment variable (User scope)
[Environment]::SetEnvironmentVariable("CODEX_AUTH_PER_PROJECT_ACCOUNTS", "0", "User")

# Option B: Config file
# Edit ~/.opencode/openai-codex-auth-config.json:
# { "perProjectAccounts": false }

# After changing, restart OpenCode
```

---

## 5. Troubleshooting Decision Tree

```
START: OpenAI/Codex model request fails
  |
  v
Ask agent to run: codex-list
  |
  +-- "0 accounts" or "No accounts configured"
  |     |
  |     v
  |   The runtime is using the global fallback (Layer 1).
  |   The "All 1 account(s) failed" error = fallback is burned.
  |     |
  |     v
  |   FIX: Follow the Step-by-Step Runbook in Section 7.
  |        Populate plugin storage with 2-3 accounts.
  |
  +-- Shows 1+ accounts
        |
        v
      Ask agent to run: codex-health
        |
        +-- "0 healthy, N unhealthy"
        |     |
        |     v
        |   Ask agent to run: codex-doctor --fix
        |   If still unhealthy, check raw JSON for enabled:false
        |   See: codex-multi-auth-refresh-token-reused.md
        |
        +-- "All healthy"
              |
              v
            Issue is NOT auth. Check:
            - Model name spelling in config
            - Provider npm package ("@ai-sdk/openai")
            - Network/proxy issues
            - Rate limits: ask agent to run codex-limits
```

---

## 6. Common Errors & Fixes

### Error: "All 1 account(s) failed"

**Meaning:** Runtime using global fallback (Layer 1), which is failing.

**Fix:** Follow the [Step-by-Step Fix Runbook](#7-step-by-step-fix-runbook-burned-token-recovery) in Section 7.

### Error: "refresh_token_reused"

**Meaning:** An account's refresh token was used twice (rotated/burned).

**Fix:** See [codex-multi-auth-refresh-token-reused.md](codex-multi-auth-refresh-token-reused.md).

### Error: "Re-auth required for missing OAuth scope(s)"

**Meaning:** Plugin's scope validation disabled a valid account.

**Fix:**
```powershell
# Find the disabled account (ask agent to run)
codex-list

# Check raw JSON - look for enabled:false
$acctFile = "$env:USERPROFILE\.opencode\projects\<key>\oc-codex-multi-auth-accounts.json"
(Get-Content $acctFile -Raw | ConvertFrom-Json).accounts |
  Select-Object accountId, enabled, accountNote

# Re-enable by editing the JSON (set enabled:true) or re-auth:
opencode auth login
```

### Error: Account count mismatch (codex-list shows 0, error says 1)

**Meaning:** Agent tools read Layer 2 only; runtime uses Layer 1 fallback.

**Fix:** Populate Layer 2 via the [Fix Runbook](#7-step-by-step-fix-runbook-burned-token-recovery). The fallback is not meant for production use.

### Error: Tokens work in one project but not another

**Meaning:** Per-project storage fragmentation.

**Fix (choose one):**
- Re-auth in each project: `opencode auth login` from each project directory
- Switch to global storage: `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0`

---

## 7. Step-by-Step Fix Runbook: Burned Token Recovery

**Use this runbook when:** You see "All 1 account(s) failed" errors, or `codex-list` shows "0 accounts" after reauthorizing. This is the exact process verified on June 22, 2026.

### Where Commands Run (Critical Distinction)

This is the #1 source of confusion. Two types of commands exist, and they run in **different places**:

| Command Type | Run By | Where | How to Invoke | Examples |
|--------------|--------|-------|---------------|----------|
| **Plugin setup & auth** | **YOU (the user)** | External terminal (PowerShell) | Type directly in terminal | `npx -y oc-codex-multi-auth@latest`, `opencode auth login` |
| **Account diagnostics & management** | **The OpenCode agent** | Internal to OpenCode (MCP tool) | Ask the agent: "run codex-list" | `codex-list`, `codex-health`, `codex-status`, `codex-doctor`, `codex-switch`, `codex-refresh` |

**If you type `codex-list` in an external terminal, it will fail** - it is not a standalone executable. These are MCP tools exposed through the OpenCode plugin interface. You run them by asking any OpenCode agent to execute them.

---

### Phase 1: Diagnose (Agent runs these)

**Who:** The OpenCode agent (ask the agent to check your accounts)  
**Where:** Internal to OpenCode - do NOT type these in a terminal

```
YOU SAY TO AGENT: "Check my codex account health"
```

The agent runs these tools and reports results:

| Step | Tool | What It Checks | What "Broken" Looks Like |
|------|------|----------------|--------------------------|
| 1 | `codex-list` | How many accounts are stored | "No accounts configured" or "0 accounts" |
| 2 | `codex-health` | Token validity for each account | "No accounts configured" or "0 healthy" |
| 3 | `codex-doctor --fix` | Full diagnostic + auto-fix | "Accounts: 0, Healthy: 0" |

**Diagnosis confirmed if:** All three show 0 accounts. This means:
- Plugin storage (Layer 2) is empty
- Runtime is falling back to global auth (Layer 1)
- The global fallback token is burned (from repeated `opencode auth login` calls)
- Proceed to Phase 2

---

### Phase 2: Fix (You run these in a terminal)

**Who:** YOU (the user)  
**Where:** External PowerShell terminal (NOT inside OpenCode)

#### Step 1: Update the plugin config

```powershell
npx -y oc-codex-multi-auth@latest
```

**What this does:** Ensures the plugin configuration is current and the multi-account auth flow is registered.

#### Step 2: Authenticate with multiple accounts

```powershell
opencode auth login
```

**What happens next:**
1. Your default browser opens to an OAuth login page
2. Log in with your first OpenAI account
3. Browser redirects back and confirms authentication
4. **The plugin prompts: "Add another account?"**
5. Select **YES** (or the equivalent affirmative option)
6. Browser opens again for the second account
7. Log in with your second OpenAI account
8. Repeat for a third account (recommended: 2-3 accounts total)
9. Select **NO / Done** after the last account

**Important:** Each account must have the required OAuth scopes: `openid, profile, email, offline_access`. The standard OpenAI OAuth flow includes these automatically.

#### Step 3: Return to OpenCode

Once you've added all accounts, switch back to your OpenCode session and ask the agent to verify.

---

### Phase 3: Verify (Agent runs these)

**Who:** The OpenCode agent  
**Where:** Internal to OpenCode

```
YOU SAY TO AGENT: "Verify my codex accounts are set up correctly"
```

The agent runs these tools in order:

#### Verification Step 1: `codex-list`

**Expected result:** Shows all accounts (2-3) with indices.

```
Accounts
- Account 1 (email@domain.com, workspace:...) [current]
- Account 2 (email@domain.com, workspace:...) [ok]
- Account 3 (email@domain.com, workspace:...) [ok]
```

**If still "0 accounts":** The accounts saved to global auth but not plugin storage. Re-run Phase 2 and ensure the plugin's "Add another account?" prompt appeared (if not, the plugin wasn't active during login - re-run `npx -y oc-codex-multi-auth@latest` first).

#### Verification Step 2: `codex-health`

**Expected result:** All accounts healthy.

```
+ Account 1 (...): Healthy
+ Account 2 (...): Healthy
+ Account 3 (...): Healthy

Summary: 3 healthy, 0 unhealthy
```

**If any unhealthy:** Run `codex-doctor --fix` (next step).

#### Verification Step 3: `codex-status`

**Expected result:** No rate limits, no cooldowns.

```
Accounts
- Account 1 (...) [active]
  rate limit: none
  cooldown: none
- Account 2 (...) [ok]
  rate limit: none
  cooldown: none
```

#### Verification Step 4: `codex-doctor --fix`

**Expected result:** No issues, tokens refreshed.

```
Accounts: 3
Healthy: 3
Blocked: 0
Failure rate: 0%

Findings
- [ok] No critical issues detected.

Auto-fix
- Refreshed 3 account token(s).
- Cleared stale TUI quota cache.
```

**Fix confirmed if:** All accounts healthy, 0 blocked, 0% failure rate. The "All account(s) failed" error should now be resolved.

---

### Quick Reference: Complete Fix Sequence

```
PHASE 1 - DIAGNOSE (agent, internal to OpenCode)
  Agent: codex-list          -> confirms 0 accounts stored
  Agent: codex-health        -> confirms 0 healthy
  Agent: codex-doctor        -> confirms no accounts in plugin storage

PHASE 2 - FIX (user, external PowerShell terminal)
  User:  npx -y oc-codex-multi-auth@latest
  User:  opencode auth login -> add 2-3 accounts via "Add another account?" prompt

PHASE 3 - VERIFY (agent, internal to OpenCode)
  Agent: codex-list          -> confirms 3 accounts stored
  Agent: codex-health        -> confirms 3 healthy
  Agent: codex-status        -> confirms no rate limits or cooldowns
  Agent: codex-doctor --fix  -> refreshes tokens, clears stale cache
```

---

## 8. Best Practices

1. **Always populate the plugin's multi-account storage** - don't rely on the global fallback for daily use. The fallback has no rotation or failover.

2. **Use 2-3 accounts minimum** for rotation benefits. One account in the plugin is barely better than the fallback.

3. **Export before auth changes:**
   ```powershell
   codex-export  # always
   ```

4. **Don't run `opencode auth login` repeatedly without the plugin flow.** Each call rotates the refresh token, burning the previous one. The global auth store holds one entry per provider.

5. **Label your accounts** for easy management:
   ```powershell
   codex-label --index 1 --label "Primary"
   ```

6. **Run weekly health checks:**
   ```powershell
   codex-health
   codex-doctor
   ```

7. **Monitor limits before heavy sessions:**
   ```powershell
   codex-limits
   codex-status
   ```

8. **Consider global storage if per-project fragmentation causes issues:**
   ```powershell
   [Environment]::SetEnvironmentVariable("CODEX_AUTH_PER_PROJECT_ACCOUNTS", "0", "User")
   ```

---

## Related Documentation

- [codex-multi-auth-refresh-token-reused.md](codex-multi-auth-refresh-token-reused.md) - Disabled account / refresh token issues
- [codex-refresh-not-recognized-and-proxy-10048.md](codex-refresh-not-recognized-and-proxy-10048.md) - Command context and proxy issues
- [plugin-status-and-remediation.md](plugin-status-and-remediation.md) - General plugin health

## Plugin References

- **GitHub:** https://github.com/ndycode/oc-codex-multi-auth
- **npm:** `oc-codex-multi-auth`
- **Version:** 6.1.8+ (check with `npx oc-codex-multi-auth@latest --version`)