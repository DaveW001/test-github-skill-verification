# Spec: Enable GPT-5.4 Mini Across OpenCode CLI and Desktop

**Track ID**: 20260319-gpt-54-mini-opencode-rollout  
**Created**: 2026-03-19  
**Status**: In Progress  
**Priority**: High  
**Owner**: 01-Planner

---

## Problem Statement

The operator wants to use the newly released `gpt-5.4-mini` model in OpenCode across CLI and Desktop, and wants a verified rollout plan that reflects the real OpenAI connection path (including whether an OpenAI proxy is in use).

---

## Current State (Verified)

1. Active OpenCode config is `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
2. OpenAI auth is handled by plugin `oc-chatgpt-multi-auth@5.4.4` (ChatGPT OAuth path).
3. OpenAI provider in current config contains custom GPT-5.1/GPT-5.2 model entries; default model is `openai/gpt-5.3-codex`.
4. No OpenAI `baseURL` proxy is configured in the `openai` provider block today.
5. Existing proxy configuration is for Google only (`provider.google.options.baseURL = http://127.0.0.1:8000/v1beta`).
6. OpenCode OAuth credentials are present in `C:\Users\DaveWitkin\.local\share\opencode\auth.json` under `openai` and `codex` entries.
7. Plugin runtime model normalization maps legacy/general GPT-5 IDs to `gpt-5.4`; no explicit `gpt-5.4-mini` canonical path is present in plugin model map.

---

## Key Technical Finding

The current OpenAI path is ChatGPT OAuth via `oc-chatgpt-multi-auth`, not OpenAI Platform API key + direct model ID passthrough. Under current plugin behavior, `gpt-5.4-mini` is at risk of normalization/fallback to `gpt-5.4` rather than preserving the exact upstream model ID.

This creates a decision point:

- If true requirement is exact upstream API model `gpt-5.4-mini`, an API/provider lane (direct or proxy) is required.
- If requirement is only "small/fast GPT-5.4 class behavior," OAuth lane may appear to work but may not be true mini.

---

## Goals

- Make `gpt-5.4-mini` selectable and runnable in both OpenCode CLI and Desktop.
- Preserve existing Codex/OAuth workflows used for daily coding.
- Provide explicit verification proving the upstream model ID actually used.
- Support optional OpenAI proxy routing if operator is using or wants one.

---

## Non-Goals

- Reworking unrelated providers (Google, Moonshot, OpenRouter).
- Rotating or replacing all existing OAuth/account setup.
- Any production deployment or billing migration beyond model-path enablement.

---

## Recommended Architecture

Adopt a dual-lane OpenAI strategy:

1. **Lane A (keep):** Existing `openai` OAuth/Codex lane via `oc-chatgpt-multi-auth` for Codex-centric workflows.
2. **Lane B (add):** New API-compatible provider lane dedicated to exact API model IDs (including `gpt-5.4-mini`), routed either:
   - directly to OpenAI Platform endpoint, or
   - through an OpenAI-compatible proxy endpoint (if used).

This avoids breaking existing OAuth tooling while enabling exact model targeting for new API-only models.

---

## Decision Gate

Before implementation, choose one of the following as authoritative for `gpt-5.4-mini`:

- **Option 1 (Preferred):** API lane with exact model ID guarantee (`gpt-5.4-mini`).
- **Option 2 (Fallback):** OAuth lane alias that may normalize to `gpt-5.4` (not strict mini guarantee).

---

## Risks and Mitigations

- **Risk:** Model picker shows a label but runtime calls a different canonical model.
  - **Mitigation:** Add request-level verification evidence (logs/debug traces) during rollout.
- **Risk:** Config drift between CLI and Desktop sessions.
  - **Mitigation:** Single source of truth in global config + cold restart validation in both clients.
- **Risk:** Plugin conflict when both OAuth and API lanes use similar model names.
  - **Mitigation:** Use explicit provider prefixes and distinct model IDs.
- **Risk:** Secret leakage while testing proxy/API credentials.
  - **Mitigation:** Redact outputs, avoid committing auth files, and validate via non-secret metadata.

---

## Success Criteria

- `gpt-5.4-mini` appears in usable model selections (or equivalent explicit provider-prefixed model choice) in CLI and Desktop.
- A run from CLI and a run from Desktop both complete successfully on the new model path.
- Validation artifact proves upstream target model is `gpt-5.4-mini` (not silently remapped).
- Existing `openai/gpt-5.3-codex` workflow remains functional after change.
- Rollback path is documented and tested.
