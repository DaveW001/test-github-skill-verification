# Spec: M365 MCP Decommissioning & Hardening

**Track ID**: 20260315-m365-mcp-cleanup-and-hardening
**Status**: In Progress

## 1. Problem Statement
The Microsoft 365 MCP server has been removed from `opencode.json`, but residual configuration, documentation, or environment variables may still reference it. This creates a risk of "zombie" tools appearing or accidental re-enablement that would bloat the context window.

## 2. Goals
- Ensure absolute removal of M365 MCP from the runtime environment.
- Harden the `opencode.json` config against accidental re-entry.
- Audit all workspace documentation to ensure only CLI paths are documented.
- Verify that no environment variables are providing credentials to an MCP process that is no longer needed.

## 3. Scope
- `C:\Users\DaveWitkin\.config\opencode\opencode.json`
- Workspace `.ps1` and `.py` scripts.
- Workspace `.md` documentation.
- Runtime Environment Variables.

## 4. Constraints
- Do NOT remove the `slack` MCP server without explicit user request.
- Ensure the backup of the original M365 config is preserved for emergencies.
