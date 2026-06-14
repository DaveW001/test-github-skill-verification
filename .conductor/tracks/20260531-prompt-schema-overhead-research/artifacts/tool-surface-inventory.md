# Tool Surface Inventory

## Visible tools recorded from session

| Tool Name | Namespace | Category (native/plugin/MCP/unknown) | Notes |
|---|---|---|---|
| bash | built-in | native | Shell execution |
| read | built-in | native | File reading |
| write | built-in | native | File writing |
| edit | built-in | native | File editing |
| glob | built-in | native | File pattern search |
| grep | built-in | native | Content search |
| osgrep | built-in | native | Semantic code search |
| compress | built-in | native | Context management |
| task | built-in | native | Subagent task execution |
| skill | built-in | native | Skill loading |
| skill_find | built-in | native | Skill search |
| skill_resource | built-in | native | Skill resource reading |
| skill_use | built-in | native | Skill usage loading |
| todowrite | built-in | native | Task list management |
| question | built-in | native | User questioning |
| webfetch | built-in | native | URL content fetching |
| websearch | built-in | native | Web searching |
| codex-dashboard | codex | plugin | Codex Authenticator |
| codex-diag | codex | plugin | Codex Authenticator |
| codex-diff | codex | plugin | Codex Authenticator |
| codex-doctor | codex | plugin | Codex Authenticator |
| codex-export | codex | plugin | Codex Authenticator |
| codex-health | codex | plugin | Codex Authenticator |
| codex-help | codex | plugin | Codex Authenticator |
| codex-import | codex | plugin | Codex Authenticator |
| codex-keychain | codex | plugin | Codex Authenticator |
| codex-label | codex | plugin | Codex Authenticator |
| codex-limits | codex | plugin | Codex Authenticator |
| codex-list | codex | plugin | Codex Authenticator |
| codex-metrics | codex | plugin | Codex Authenticator |
| codex-next | codex | plugin | Codex Authenticator |
| codex-note | codex | plugin | Codex Authenticator |
| codex-refresh | codex | plugin | Codex Authenticator |
| codex-remove | codex | plugin | Codex Authenticator |
| codex-setup | codex | plugin | Codex Authenticator |
| codex-status | codex | plugin | Codex Authenticator |
| codex-switch | codex | plugin | Codex Authenticator |
| codex-tag | codex | plugin | Codex Authenticator |

## Summary
- Total native tools: 20 (bash, read, write, edit, glob, grep, osgrep, compress, task, skill, skill_find, skill_resource, skill_use, todowrite, question, webfetch, websearch, tokenscope)
- Total plugin/MCP tools: 20 (Codex Authenticator suite - codex-*)
- Total MCP server tools: 0 (all 3 MCP servers disabled in config: playwright, control-chrome, slack)
- Total task/subagent tools: 1 (task tool)
- Notes: tokenscope is treated as a native measurement/diagnostic tool. All MCP servers are disabled. Codex tools are injected by the "oc-codex-multi-auth" plugin.
