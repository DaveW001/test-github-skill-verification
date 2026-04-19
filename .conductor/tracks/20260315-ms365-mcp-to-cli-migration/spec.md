# Spec: Migrate M365 Operations from MCP to CLI

**Track ID**: 20260315-ms365-mcp-to-cli-migration  
**Created**: 2026-03-15  
**Status**: Proposed  
**Priority**: High  
**Owner**: 01-Planner

---

## Problem Statement

Current OpenCode setup enables a Microsoft 365 MCP server (`@softeria/ms-365-mcp-server`) that likely contributes substantial context overhead due to large tool schema injection. This can reduce effective working context for actual task reasoning and increase per-turn token cost.

We need a controlled migration to a CLI-first approach (Microsoft Graph PowerShell SDK) that preserves functionality while reducing context pressure and keeping operator workflows clear.

---

## Why Switch to CLI

- MCP tools inject schema into model context, often including large JSON input definitions.
- The configured M365 MCP server can expose a broad tool surface (repo docs advertise 90+ tools in broad modes).
- CLI execution keeps most operational detail outside persistent model context and can be summarized back as needed.
- Existing environment already supports Graph PowerShell with reusable app+certificate auth, reducing migration risk.

---

## Goals

- Remove or tightly disable M365 MCP dependence for daily operations.
- Standardize a CLI-first M365 workflow using Microsoft Graph PowerShell SDK.
- Reuse existing Azure app registration and local certificate-based app auth.
- Publish clear documentation explaining the migration rationale, operating model, and rollback.
- Produce a complete inventory of docs/config references that must be changed.

---

## Non-Goals

- Re-architecting unrelated Slack MCP workflows in this track.
- Replacing all existing scripts immediately if they are outside active workflows.
- Building a new custom MCP server.

---

## Scope

In scope:

- OpenCode config updates for M365 MCP posture (`disable`/remove server entry).
- Workflow/documentation updates where `ms365_*` OpenCode tools are currently referenced.
- Standard command patterns for Graph PowerShell equivalents.
- Validation checklist for auth, mailbox operations, throttling behavior, and failure handling.
- Risk controls and rollback steps.

Out of scope:

- Broader repository refactors unrelated to M365 operations.
- Automated migration of every historical artifact file.

---

## Confirmed Baseline Inputs

- Current user config includes:
  - `mcp.ms365` => local server command `npx -y @softeria/ms-365-mcp-server`
  - `mcp.slack` => retained separately with explicit tool allowlist
- Existing Graph app auth variables are present in the environment and app-only cert auth has been validated in-session.

---

## Documentation Strategy

1. **Decision Record**
   - Add a clear architecture decision note describing why M365 moved from MCP to CLI (context budget, determinism, maintainability).
2. **Primary Workflow Update**
   - Update junk mail workflow docs to make CLI path the primary path.
   - Keep MCP path as historical/deprecated note only during transition.
3. **Operator Runbook**
   - Create or update concise runbook with:
     - auth method (cert-based app auth),
     - daily commands,
     - troubleshooting,
     - fallback and rollback.
4. **Configuration Documentation**
   - Document exact config knobs changed in OpenCode user config and expected post-change behavior.
5. **Verification Record**
   - Capture before/after context impact observations and command-level validation evidence.

---

## Full Inventory: Existing Docs and Config Options to Change

Detailed inventory is maintained in `artifacts/docs-and-config-inventory.md`.

At minimum, this track will update:

- `C:\Users\DaveWitkin\.config\opencode\opencode.json` (user config; `mcp.ms365` posture and secret handling hygiene)
- `docs/junk-email-workflow.md` (currently recommends `ms365_move-mail-message` as primary option)
- `PROJECT_STATUS.md` (currently references `ms365_move-mail-message` operational path)

Likely follow-on updates (if approved in implementation phase):

- `move_remaining_junk.ps1` (currently invokes `ms365_move-mail-message`; may be migrated to Graph cmdlets)
- New migration/decision doc under `docs/` or track artifacts for rationale and rollback evidence

---

## Risks and Mitigations

- **Auth/session drift risk**: Graph PowerShell auth can be session-scoped in interactive runs.  
  **Mitigation**: standardize app-only cert auth bootstrap in each script/session.
- **Command parity risk**: Some `ms365_*` tools may not map 1:1 to Graph cmdlets.  
  **Mitigation**: maintain operation mapping table and explicit tested equivalents.
- **Operational regression risk**: mailbox operations could fail due to throttling/permissions.  
  **Mitigation**: keep retry/backoff policy and validation checklist.
- **Change sprawl risk**: references may be scattered across docs/scripts.  
  **Mitigation**: inventory-first phase and signoff before edits.

---

## Success Criteria

- M365 MCP is disabled/removed for normal OpenCode runs.
- CLI-first workflow is documented as default with clear rationale.
- All identified high-impact docs/config references are updated and cross-linked.
- Operator can run core mailbox operations via Graph PowerShell using existing app+cert setup.
- Rollback path is documented and tested at least once.
