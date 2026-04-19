# ADR 003: Migrate M365 Operations from MCP to CLI

**Date**: 2026-03-15  
**Status**: Accepted  
**Context**: [Migrate M365 Operations from MCP to CLI](../../.conductor/tracks/20260315-ms365-mcp-to-cli-migration/spec.md)

## Context and Problem Statement

The OpenCode environment was using the `@softeria/ms-365-mcp-server` to provide Microsoft 365 tools to the LLM. Analysis revealed that MCP servers with large tool inventories (90+ tools in this case) inject substantial JSON schema definitions into every model context window. This "context tax" (~20k-70k tokens) reduces the space available for task-specific reasoning and increases token costs.

## Decision

We have decided to decommission the M365 MCP server and switch to a CLI-first approach using the **Microsoft Graph PowerShell SDK**.

## Rationale

1. **Context Budget**: Moving to CLI eliminates the persistent schema injection, freeing up significant context window for the model.
2. **Determinism**: CLI commands provide predictable output and error handling that is easier to parse and summarize for the model than raw MCP tool outputs.
3. **Maturity**: The Microsoft Graph PowerShell SDK is the official, maintained path for Graph operations.
4. **Reuse**: The existing environment already has a certificate-based Azure AD app registration (`daily-priority-briefing-graph`) that can be reused for non-interactive CLI auth.

## Consequences

- **Positive**: Reduced token usage, more stable model performance, and better alignment with official Microsoft tooling.
- **Negative**: Requires explicit auth bootstrap (certificate-based) in scripts and manual mapping of some `ms365_*` tools to PowerShell cmdlets.
- **Neutral**: Agents must be instructed to use CLI instead of searching for `ms365_*` tools.

## Implementation Details

- **Auth**: App-only certificate authentication using `Connect-MgGraph`.
- **Primary Tools**: `Get-MgUserMailFolder`, `Get-MgUserMessage`, `Move-MgUserMessage`.
- **Config**: M365 block removed from `opencode.json`.

## Rollback Plan

To rollback, restore the `opencode.json` from the backup at `.conductor/tracks/20260315-ms365-mcp-to-cli-migration/artifacts/opencode.json.backup-pre-migration`.
