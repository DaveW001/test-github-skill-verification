# Plan: Migrate M365 Operations from MCP to CLI

**Track ID**: 20260315-ms365-mcp-to-cli-migration  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-03-15  
**Status**: Proposed

---

## Phase 1: Inventory Freeze and Scope Confirmation

- [x] Snapshot current OpenCode user config for rollback (`opencode.json` backup).
- [x] Confirm migration scope for this track:
  - baseline: M365 MCP only,
  - optional: broader MCP minimization strategy.
- [x] Finalize inventory in `artifacts/docs-and-config-inventory.md` with owner and priority per item.
- [x] Mark each inventory item as: `must-change`, `should-change`, or `defer`.
- [x] **Validation**: Graph cert auth baseline verified working

## Phase 2: CLI Operating Model Definition

- [x] Define canonical auth bootstrap for Graph PowerShell (app-only certificate mode).
- [x] Define command mapping table from current `ms365_*` usage to Graph PowerShell equivalents.
- [x] Define output handling policy to minimize context load (summarize command results, avoid raw dumps).
- [x] Define safety controls: retries, backoff, idempotency checks, and failure classification.
- [x] **Validation**: Mail.Read verified; Mail.ReadWrite (move) currently failing with 403 (Permission Gap)

## Phase 3: Config Migration Plan

- [x] Plan exact `opencode.json` changes for `mcp.ms365`:
  - disable/remove server block,
  - preserve Slack MCP block unless separately approved.
- [ ] Plan secrets hygiene updates (remove plaintext tokens from config where feasible; move to env-based sourcing).
- [x] Define rollback toggles and rollback command sequence.
- [x] **Execution**: M365 MCP server removed from `opencode.json`

## Phase 4: Documentation Migration

- [x] Update primary workflow docs to make CLI the default path.
- [x] Add a migration rationale doc (decision record) explaining why CLI replaced MCP.
- [x] Update status docs to reflect CLI-first operational reality.
- [x] Add operator quickstart for common mailbox operations (connect, list, move, verify).
- [x] Add troubleshooting section for auth, throttling, and permission issues.
- [x] **Execution**: Updated `docs/junk-email-workflow.md`, `PROJECT_STATUS.md`, and created `docs/reference/ADR-003-m365-mcp-to-cli-migration.md` and `docs/reference/m365-cli-quickstart.md`

## Phase 5: Validation and Evidence

- [x] Execute validation matrix for core operations with CLI equivalents.
- [x] Capture before/after context impact observations (qualitative plus any measurable proxies).
- [x] Verify no critical doc still presents `ms365_*` MCP path as primary workflow.
- [x] Verify rollback works.
- [x] **Results**: Auth/Read ✅; Write ⚠️ (Requires Azure Permission Update)

## Phase 6: Handover and Decommission

- [x] Publish final implementation checklist for Build agent execution.
- [x] Publish post-cutover monitoring checklist (7-day stabilization).
- [x] Decommission residual M365 MCP references marked `must-change`.
- [x] Close track after acceptance review.
- [x] **Execution**: Handover complete; `move_remaining_junk.ps1` migrated to CLI.

---

## Deliverables

- Updated OpenCode configuration plan and rollback notes.
- Updated workflow/status documentation with CLI-first guidance.
- Decision record documenting rationale and tradeoffs.
- Verified inventory with explicit disposition for each impacted doc/config.
- Build-ready implementation checklist.
