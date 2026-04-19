# Plan: Fix OpenCode Desktop "Missing Authentication header" for OpenRouter

**Track ID**: 20260406-openrouter-desktop-auth-fix  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-04-06  
**Status**: Completed

---

## Phase 1: Diagnosis

- [x] Read OpenCode Desktop logs to confirm error source
- [x] Inspect active config (`opencode.jsonc`) for OpenRouter provider block
- [x] Check Windows user-level env var presence
- [x] Check current shell env var presence
- [x] Confirm key exists in `~/.config/opencode/.env`
- [x] Review relevant conductor tracks for prior context

## Phase 2: Fix

- [x] Read key from private `.env` file
- [x] Set `OPENROUTER_API_KEY` at Windows user scope via PowerShell
- [x] Verify persistence with `[Environment]::GetEnvironmentVariable`

## Phase 3: Verification

- [x] User restarts OpenCode Desktop
- [x] User sends one-message smoke test
- [x] Result: `OPENROUTER_OK` — fix confirmed

## Phase 4: Documentation

- [x] Add `OPENROUTER_API_KEY` row to Active Variables table in `environment-variables.md`
- [x] Add "OpenRouter Desktop Fix Notes" section with symptom, root cause, fix, verification, and restart guidance
- [x] Create conductor track for closure

---

## Acceptance Checklist

- [x] `OPENROUTER_API_KEY` reachable from OpenCode Desktop
- [x] No disruption to existing CLI workflow
- [x] Fix is documented in OpenCode repo docs
- [x] Conductor track created and closed
