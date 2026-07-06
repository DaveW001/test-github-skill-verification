# Anomaly Summary - 20260704-session-continuation-codex-skill-architecture-fix

- Source JSONL: `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl`
- Filter: track == `20260704-session-continuation-codex-skill-architecture-fix`
- Generated at (local): 2026-07-04 21:21:40 -04:00
- Total entries for this track: 5

## Per-entry breakdown

| ts (UTC) | stage | subagent | type | severity | detail (truncated 200) |
|---|---|---|---|---|---|
| 07/05/2026 00:34:07 | orchestrator | conductor-pipeline-orchestrator | tool-error | warn | Native Read/Edit/Write tools returned Bun is not defined; orchestrator switched whole session to PowerShell-first via bash tool. |
| 07/04/2026 22:25:00 | stage-2 | conductor-plan-reviewer | tool-error | warn | Native Read/Write tools returned Bun is not defined in this host. Switched whole session to PowerShell-first via bash tool using -LiteralPath and Set-Content/Get-Content. All read-only verification... |
| 07/05/2026 00:47:52 | stage-3 | conductor-plan-reviewer-alt | tool-error | warn | Native file tools unavailable in this host environment: Bun is not defined; using PowerShell-first workflow per preflight. |
| 07/05/2026 00:55:25 | stage-4 | conductor-track-executor | tool-error | warn | Native file tools (Read/Edit/Write/glob/grep) return "Bun is not defined" in this host. Orchestrator preflight confirmed broken. Switching whole session to PowerShell-first via bash tool. No retry ... |
| 07/05/2026 01:21:35 | stage-5 | conductor-track-validator | tool-error | warn | Native file tools (Read/Edit/Write/glob/grep) return Bun is not defined in this host. Switched whole session to PowerShell-first via bash tool using -LiteralPath and Get-Content/Set-Content/Select-... |

