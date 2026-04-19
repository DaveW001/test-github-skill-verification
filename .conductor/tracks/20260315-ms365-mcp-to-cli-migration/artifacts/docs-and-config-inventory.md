# Docs and Config Inventory: MCP to CLI Migration

**Track ID**: 20260315-ms365-mcp-to-cli-migration  
**Purpose**: Full list of existing documentation and configuration targets for migration from M365 MCP usage to CLI-first operations.

---

## A) Configuration Targets

| Priority | Target | Current State | Planned Change |
|---|---|---|---|
| must-change | `C:\Users\DaveWitkin\.config\opencode\opencode.json` | Contains `mcp.ms365` local server block and Slack token in plaintext | Disable/remove `mcp.ms365`; retain Slack block unless out-of-scope changes approved; move secrets to env-only handling where feasible |

### Config Options to Change (Detailed)

1. `mcp.ms365.type`
2. `mcp.ms365.command`
3. Optional add/adjust: tool disable patterns for ms365 tool namespace
4. Secret handling posture for Slack token (`SLACK_MCP_XOXP_TOKEN`) if touched during config hardening

---

## B) Documentation Targets (Repo)

| Priority | File | Current MCP Coupling | Planned Documentation Update |
|---|---|---|---|
| must-change | `docs/junk-email-workflow.md` | `ms365_move-mail-message` presented as recommended path; multiple examples use `ms365_*` tools | Make Graph PowerShell CLI path primary; move `ms365_*` content to deprecated/legacy section or remove |
| must-change | `PROJECT_STATUS.md` | Option 1 references `ms365_move-mail-message`; tool availability note references environment-specific MCP tool | Reframe completion and operational guidance around CLI path; remove MCP-first framing |
| should-change | New ADR/decision doc (path TBD under `docs/`) | No explicit rationale record exists for MCP-to-CLI decision | Add concise rationale: context budget, reliability, maintainability, rollback |
| should-change | New/updated operator runbook (track artifact or `docs/`) | No single CLI-first runbook tied to this migration | Add command quickstart, auth bootstrap, troubleshooting, rollback |

---

## C) Script/Automation Targets (Implementation Follow-On)

These are not documentation/config files, but are tracked because they can reintroduce MCP dependence.

| Priority | File | Current State | Planned Action |
|---|---|---|---|
| should-change | `move_remaining_junk.ps1` | Calls `ms365_move-mail-message` directly | Replace with Graph PowerShell cmdlets or split into new CLI-native script |

---

## D) Exclusions for This Track (Unless Scope Expands)

| Target | Reason |
|---|---|
| Slack MCP tooling in general | Current ask is M365 migration; Slack is separate and already allowlisted |
| Historical temp research files (`temp_*.json`, `tmp_sources_*.txt`) | Not operational docs/config; no migration dependency |

---

## E) Acceptance Check for Inventory Completion

- Every `must-change` item has a planned edit owner and expected output.
- Every `should-change` item is either scheduled or explicitly deferred.
- No remaining active doc marks `ms365_*` MCP as recommended default path.
