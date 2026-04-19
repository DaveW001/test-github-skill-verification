# Plan: M365 MCP Decommissioning & Hardening

**Track ID**: 20260315-m365-mcp-cleanup-and-hardening
**Spec**: [spec.md](./spec.md)

> [!IMPORTANT]
> **User Note**: This plan may not be needed. If the user restarts OpenCode and the Microsoft 365 MCP server is confirmed gone from the tools list, this track should be deleted/cancelled.

---

## Phase 1: Restart Verification
- [x] Create a restart reminder for the user (`M365_MCP_RESTART_CHECK.txt` + `artifacts/restart-reminder.ps1`).
- [x] Register Windows Scheduled Task `OpenCode-M365-MCP-Removal-Check`.
  - Registered successfully via `gsudo`; task state is `Ready`.
  - Verification: `schtasks /Query /TN "OpenCode-M365-MCP-Removal-Check" /V /FO LIST` confirms At logon trigger and reminder script action.
- [ ] Verify if the MCP server is gone after a full OpenCode restart.
- [ ] If gone, delete this track. If not, proceed to Phase 2.

## Phase 2: Environment Audit
- [ ] List all environment variables and check for any `M365_` or `GRAPH_` variables used specifically by the old MCP server (distinguish from those needed by the new CLI).
- [ ] Search for any `.env` files or local shell profiles (`Microsoft.PowerShell_profile.ps1`) that might be auto-loading the MCP server.

## Phase 2: Configuration Hardening
- [ ] Verify `opencode.json` is clean of any `ms365` keys.
- [ ] Add a comment or documentation entry in the `artifacts/` folder of this track summarizing the final "Safe State".

## Phase 3: Documentation Scouring
- [ ] Run a global search for `ms365_` (the prefix used by the MCP tools).
- [ ] Replace any remaining MCP-style tool calls with the corresponding CLI commands or a pointer to the Quickstart.

## Phase 4: Final Validation
- [ ] Restart a test shell session and verify no `ms365` tools are available to the agent.
- [ ] Final sign-off on the transition.
