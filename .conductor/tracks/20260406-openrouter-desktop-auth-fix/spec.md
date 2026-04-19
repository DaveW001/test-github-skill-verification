# Spec: Fix OpenCode Desktop "Missing Authentication header" for OpenRouter

## Goal

Resolve the `Missing Authentication header` error in OpenCode Desktop when using the OpenRouter provider, and document the fix so it does not recur.

## Context

- **User symptom:** OpenCode Desktop shows `Missing Authentication header` in a new session.
- **Active config:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - default model: `openrouter/qwen/qwen3.6-plus:free`
  - planner model: `openrouter/qwen/qwen3.6-plus:free`
  - OpenRouter provider uses `apiKey: {env:OPENROUTER_API_KEY}`
- **Key location before fix:** `C:\Users\DaveWitkin\.config\opencode\.env` (local file only)
- **Desktop log evidence:** `C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs\opencode-desktop_2026-04-06_12-01-27.log`
  - `providerID=openrouter`, `url=https://openrouter.ai/api/v1/chat/completions`
  - `error=Missing Authentication header`
- **Root cause:** OpenCode Desktop does not auto-load `~/.config/opencode/.env`. The `{env:OPENROUTER_API_KEY}` substitution resolved to empty, so requests were sent without an Authorization header.
- **Fix applied:** Promoted `OPENROUTER_API_KEY` from the private `.env` file into the **Windows user-level environment** via `[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "<key>", "User")`.
- **Verification:** Desktop restarted; a one-message smoke test (`Reply with exactly: OPENROUTER_OK`) succeeded.
- **Documentation:** Updated `C:\development\opencode\docs\reference\environment-variables.md` with a redacted variable entry and a troubleshooting section.

## Requirements

- [x] Identify root cause of `Missing Authentication header` in Desktop
- [x] Apply permanent fix (Windows user-level env var)
- [x] Verify fix in Desktop after restart
- [x] Document fix in OpenCode repo docs
- [x] Create conductor track for closure

## Non-Requirements

- Changing the OpenRouter provider config structure
- Rotating the API key (key was already exposed in prior session chat; rotation is optional)
- Fixing secondary issues (Gemini proxy, plugin load errors, malformed command frontmatter)

## Acceptance Criteria

- [x] `OPENROUTER_API_KEY` is set at Windows user scope
- [x] OpenCode Desktop can send OpenRouter requests successfully after restart
- [x] `C:\development\opencode\docs\reference\environment-variables.md` documents the variable and fix
- [x] Conductor track created and closed
