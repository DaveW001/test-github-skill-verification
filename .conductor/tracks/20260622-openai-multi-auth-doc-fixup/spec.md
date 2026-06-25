# Spec: OpenAI Multi-Auth Doc Fixup

**Status:** Completed  
**Date:** June 22, 2026  
**Type:** Documentation only (no code changes)  
**Plugin:** `oc-codex-multi-auth` v6.1.8  

---

## Problem

The OpenAI/Codex multi-auth plugin is the recommended way to manage multiple OpenAI accounts with rotation, health-aware failover, and per-account cooldowns. However, the existing troubleshooting documentation contained several incorrect architectural claims:

1. Incorrectly framed the plugin's per-project storage as "required"
2. Treated global auth (`~/.local/share/opencode/auth.json`) and plugin multi-account storage as separate, non-interacting systems
3. Failed to document the global auth fallback behavior in the plugin's runtime
4. Lacked clear step-by-step instructions for multi-account setup
5. Did not clearly distinguish between user-executed terminal commands and agent-executed MCP tools

The user encountered a real-world failure ("All 1 account(s) failed") and the existing documentation would have been misleading for diagnosing and fixing it.

---

## Goal

Create accurate, step-by-step documentation that:

1. Correctly describes the three-layer auth architecture
2. Documents the global auth fallback behavior
3. Provides a clear, runnable step-by-step fix procedure
4. Clearly distinguishes "user runs in external terminal" from "agent runs internally"
5. Serves as a reliable reference for future incidents

---

## Deliverables

- `docs/troubleshooting/active/openai-codex-multi-auth-guide.md` (NEW) — comprehensive 8-section guide with step-by-step runbook
- `docs/troubleshooting/active/codex-multi-auth-refresh-token-reused.md` (REWRITTEN) — corrected incident note with proper architecture description

---

## Non-Goals

- No code changes
- No configuration changes
- No plugin changes
- No new features or tools