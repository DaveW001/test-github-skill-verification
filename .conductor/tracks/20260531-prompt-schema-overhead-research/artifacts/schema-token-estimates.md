# Schema Token Estimates

| Component | Method | Tokens | Confidence | Evidence |
|---|---|---:|---|---|
| Codex/account tool surface | pending | 0 | pending | pending |
| MCP tool schemas | pending | 0 | pending | pending |
| Native tool schemas | pending | 0 | pending | pending |
| Task/subagent tool definition | pending | 0 | pending | pending |
| Session/runtime scaffolding | pending | 0 | pending | pending |

## MCP current config status

Line 217:   "mcp": {
Line 218:     "playwright": { "type": "local", "command": ["npx", "@playwright/mcp@latest"], "enabled": false },
Line 219:     "control-chrome": { "type": "local", "command": ["npx", "-y", "chrome-devtools-mcp@latest", "--no-usage-statistics"], "enabled": false },
Line 220:     "slack": { "type": "local", "command": ["npx", "-y", "slack-mcp-server@latest", "-transport", "stdio"], "environment": { "SLACK_MCP_XOXP_TOKEN": "<SLACK_TOKEN_REDACTED>", "SLACK_MCP_ENABLED_TOOLS": "channels_list,conversations_history,conversations_search_messages,conversations_add_message,attachment_get_data,conversations_replies" }, "enabled": false }

## Native tool schema evidence

Line 13: - Estimated tokens: 2,875
Line 27: ## Native Tool Schemas
Line 29: 15 native tools observed with long JSON Schema parameter definitions.
Line 32: - bash: ~2500 chars (terminal execution with shell notes, quoting rules, git/github guidance)
Line 33: - task: ~2000 chars (subagent types, usage notes, batching rules)
Line 38: - read: ~600 chars
Line 48: - glob: ~200 chars
Line 49: - grep: ~200 chars
Line 50: - osgrep: ~300 chars
Line 53: Estimated tokens (chars/4): ~2,350
Line 89: | Component | Estimated Tokens | Percent of System | Configurable? | Evidence Source |
Line 95: | Native Tool Schemas | 2,350 | 8.6% | No / Partial | native-tool-inventory.md |

## Task/subagent evidence

Line 110:   Total: ~379 tokens (8 skills available)
Line 115: AVAILABLE SUBAGENTS (in task tool definition)
Line 131:   Total: ~305 tokens (8 subagents available)
Line 133:   Note: Full task tool description is ~790 tokens (includes instructions/examples).

## Updated Token Estimates (from current baseline of 17,377 system tokens)

| Component | Estimate (tokens) | % of System | Config-Togglable? | Evidence |
|---|---:|---:|---|---|
| Codex/account tooling | 2,750 (midpoint of 2,000-3,500) | 15.8% | Yes - remove plugin entry | Prior track estimate; 20 plugin tools confirmed |
| MCP tool schemas | 0 (all disabled) | 0% | N/A - already disabled | Confirmed from opencode.jsonc: playwright, control-chrome, slack all disabled |
| Native tool schemas | ~2,350 | 13.5% | No (upstream) | Prior track estimate; 18+ native tools |
| Skill metadata | ~962 | 5.5% | Partial (skill tool schema) | tokenscope: 379 tokens skills + 583 full desc |
| Subagent definitions | ~1,095 | 6.3% | Partial (task tool schema) | tokenscope: 305 tokens subagents + 790 full task desc |
| Runtime/agent scaffolding | ~10,220 (remainder) | 58.8% | No (upstream) | Calculated: 17,377 - 2,750 - 0 - 2,350 - 962 - 1,095 |

## Savings Opportunity Ranking

| Rank | Candidate | Estimated Savings | Reversibility | User Impact | Confidence | Next Action |
|---:|---|---:|---|---|---|---|
| 1 | Codex/account tooling (disable plugin) | 2,000-3,500 | Full revert (re-enable plugin) | Medium - loses codex-* tools | High | **DEFERRED** - Run A/B test in fresh session |
| 2 | Task/subagent schema compaction | ~500-800 | Config change? | Medium - affects task tool description | Medium | Investigate config option for compact task schema |
| 3 | Skill tool schema compaction | ~400-600 | Config change? | Low - affects skill descriptions | Medium | Investigate config option for compact skill schema |
| 4 | MCP server overhead (preventive) | savings if re-enabled: 2,800-5,800 | N/A | High - enables MCP server features | High | Keep disabled unless needed |
| 5 | Native tool schema compaction | ~1,000-1,500 | Upstream only | Low if schema remains functional | Low | Upstream issue |
| 6 | Runtime/agent base prompt reduction | ~2,000-5,000 | Upstream only | Low per design | Low | Upstream issue |

## Key insight
With Codex tooling disabled, estimated system tokens range: 17,377 - 2,750 = ~14,627 (if Codex is at midpoint). This would reach the 15,000 target. Even with lower-bound Codex savings (2,000), system tokens = 15,377, still very close.
