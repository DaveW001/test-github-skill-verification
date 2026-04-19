# Environment Variables (Windows User-Level)

**Purpose:** This document tracks all environment variables set at the Windows **user level** (persisted in the registry via `[Environment]::SetEnvironmentVariable(..., "User")`). These propagate to ALL processes your user launches — scheduled tasks, CLI tools, GUIs, etc.

**Why this doc exists:** Without it, registry-stored env vars become invisible "mystery variables" that nobody remembers setting or understands. Every variable listed here must have a clear purpose, date set, and removal criteria.

---

## How to View All User-Level Variables

```powershell
# List all user env vars
[Environment]::GetEnvironmentVariables("User")

# Check a specific one
[Environment]::GetEnvironmentVariable("OPENCODE_ENABLE_EXA", "User")
```

---

## Active Variables

| Variable | Value | Set Date | Purpose | Source/Why | Removal Criteria |
|----------|-------|----------|---------|------------|------------------|
| `OPENCODE_ENABLE_EXA` | `1` | 2026-03-25 | Enables the `websearch` tool in OpenCode (Exa AI). Required when NOT using the OpenCode provider. Allows any process launching OpenCode (TUI, CLI, scheduled jobs) to use web search. | [OpenCode docs](https://opencode.ai/docs/tools/) state: "only available when using the OpenCode provider or when `OPENCODE_ENABLE_EXA` is set to a truthy value." | Remove if we switch to the OpenCode provider, or if Exa search is no longer needed. |
| `OPENROUTER_API_KEY` | `[redacted]` | 2026-04-06 | Supplies the OpenRouter API key to OpenCode when the active provider config uses `apiKey: {env:OPENROUTER_API_KEY}`. Required for OpenCode Desktop and other GUI-launched processes, because a local `~/.config/opencode/.env` file does not reliably propagate into the Desktop runtime environment. | Added after OpenCode Desktop failed with `Missing Authentication header` while using default model `openrouter/qwen/qwen3.6-plus:free`; Desktop logs showed requests reaching `https://openrouter.ai/api/v1/chat/completions` without an Authorization header until the key was promoted to a Windows user-level env var. | Remove only if OpenRouter is no longer used, or if the provider is reconfigured to use a different credential mechanism that Desktop can resolve reliably. |
| | | | | | |
| | | | | | |

---

## How to Set a New Variable

```powershell
# Set (use "User" scope, NOT "Machine" which requires admin)
[Environment]::SetEnvironmentVariable("MY_VAR", "my_value", "User")

# After setting, restart terminal or log out/in for it to propagate
```

## How to Remove a Variable

```powershell
# Remove by setting to $null
[Environment]::SetEnvironmentVariable("MY_VAR", $null, "User")
```

---

## OpenRouter Desktop Fix Notes

### Symptom
- OpenCode Desktop shows `Missing Authentication header` in a fresh session.

### Root Cause
- The active OpenCode config references `OPENROUTER_API_KEY` via environment substitution.
- The key existed in `C:\Users\DaveWitkin\.config\opencode\.env`, but Desktop did not inherit that file automatically.
- As a result, Desktop sent OpenRouter requests without the Authorization header.

### Fix Applied
```powershell
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "<existing key>", "User")
```

### Verification
```powershell
[bool][Environment]::GetEnvironmentVariable("OPENROUTER_API_KEY", "User")
```

Expected result:
- `True`

### Important
- Fully quit and reopen OpenCode Desktop after setting the variable.
- If Desktop was already running before the change, it may need a full restart or Windows sign-out/sign-in to pick up the new user environment.

---

## Rules for This Document

1. **Every user-level env var must be documented here** — no exceptions
2. **Date set** — so you know when it was added
3. **Purpose** — what it does in plain English
4. **Source/Why** — link to docs or explanation of why it was needed
5. **Removal criteria** — under what conditions can we delete it
6. **Before adding a new var, add a row to the table above**
