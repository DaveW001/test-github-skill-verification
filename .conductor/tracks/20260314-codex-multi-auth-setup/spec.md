# Spec: Switch to Multi-Account Codex OAuth Plugin

**Track ID**: 20260314-codex-multi-auth-setup  
**Created**: 2026-03-14  
**Status**: In Progress  
**Priority**: High  
**Owner**: 01-Planner

---

## Problem Statement

Current OpenCode user config uses a single-account OAuth plugin (`opencode-openai-codex-auth@4.2.0`), but operator now has a second Codex-capable ChatGPT account and needs automatic failover/rotation when one account hits usage limits.

---

## Goals

- Replace single-account auth plugin with a multi-account OAuth plugin that supports automatic account failover.
- Keep existing OpenCode configuration stable (providers, model aliases, permissions, and other plugins).
- Validate plugin load and readiness without disrupting current working setup.
- Provide a clear split of actions: what agent can automate vs what operator must do in browser OAuth.

---

## Scope

In scope:

- Validate plugin package availability and compatibility assumptions.
- Update `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` plugin entry from single-account to multi-account plugin.
- Verify resolved OpenCode runtime config and plugin registration.
- Run a controlled two-account auth setup flow and verify account rotation tooling.
- Capture evidence and operator runbook.

Out of scope:

- Migrating/rewriting all model definitions unless required by plugin behavior.
- Modifying unrelated providers (`google`, `moonshot`) or non-auth workflows.
- Any production API billing migration.

---

## Research Notes (2026-03-14)

- `npm view oc-chatgpt-multi-auth version` => `5.4.4`
- `npm view opencode-openai-multi-auth version` => `5.0.6`
- `npm view opencode-openai-codex-auth version` => `4.4.0`
- `oc-chatgpt-multi-auth` README indicates it is the renamed/maintained multi-account package and supports health-aware failover, account tools, and per-project account storage.
- `npm view oc-chatgpt-multi-auth@5.4.4 peerDependencies dependencies` confirms TypeScript peer (`^5`) and no immediate blocking dependency mismatch for current OpenCode runtime validation workflow.

---

## Risks and Decisions

- **Version pinning risk**: `@latest` can drift unexpectedly; plan defaults to pinning (`oc-chatgpt-multi-auth@5.4.4`) unless operator prefers auto-updates.
- **Config filename mismatch risk**: local machine uses `opencode.jsonc`, while plugin docs often show `opencode.json`; implementation must edit actual active file only.
- **OAuth cannot be fully automated**: browser/device-auth steps for each account require operator interaction.
- **Behavioral deltas**: account storage and rotation behavior may differ from old plugin; validation includes explicit tooling checks (`codex-list`, `codex-status`, `codex-switch`).
- **Rollback readiness**: migration must define explicit rollback triggers and a known-good restore path before cutover completion.
- **Session consistency risk**: multi-session state drift is possible during account switching; add lightweight concurrent session validation.

---

## Success Criteria

- Config references multi-account plugin and removes single-account plugin entry.
- `opencode debug config` shows resolved multi-auth plugin.
- Two accounts are present in plugin account list and one is marked active.
- Simulated/observed failover and recovery paths are documented (including refresh and re-login behavior) and operator can switch or recover accounts with provided commands.
- Track artifacts include a concise operator-auth runbook.
- Rollback procedure and 24-48h post-handover monitoring checklist are included in artifacts.
