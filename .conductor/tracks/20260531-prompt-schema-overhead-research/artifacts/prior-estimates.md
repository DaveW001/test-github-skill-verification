# Prior Estimates

Source: C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\token-breakdown.md

Line 13: - Estimated tokens: 2,875
Line 15: ## Skill Tool Metadata
Line 19: - Full skill tool description tokens: ~5,712
Line 21: ## Subagent Definitions
Line 23: - Subagents counted: 8
Line 27: ## Native Tool Schemas
Line 29: 15 native tools observed with long JSON Schema parameter definitions.
Line 33: - task: ~2000 chars (subagent types, usage notes, batching rules)
Line 53: Estimated tokens (chars/4): ~2,350
Line 57: ## MCP Tool Schemas
Line 59: MCP tool schemas could not be directly measured due to the OpenCode export failure (bun index.js missing).
Line 62: - Codex (20 tools): estimated range 2,000-3,500 tokens, justification: ~20 focused tools with JSON schemas, moderate parameter docs each (~100-175 tokens/tool)
Line 66: Total estimated MCP range: 2,800-5,800 tokens
Line 67: Best single estimate: ~4,300 tokens (midpoint)
Line 71: ## Agent Base Prompt / Environment Remainder
Line 89: | Component | Estimated Tokens | Percent of System | Configurable? | Evidence Source |
Line 91: | Agent Base Prompt / Environment Remainder | 11,142 | 40.8% | No | calculated remainder |
Line 92: | Skill Tool Metadata (full tool desc) | 5,712 | 20.9% | Partial | baseline-tokenscope.txt |
Line 93: | MCP Tool Schemas | 4,300 | 15.8% | Partial | mcp-tool-inventory.md (estimated) |
Line 95: | Native Tool Schemas | 2,350 | 8.6% | No / Partial | native-tool-inventory.md |
Line 96: | Subagent Definitions (full tool desc) | 901 | 3.3% | Partial | baseline-tokenscope.txt |
Line 99: Note: MCP Tool Schemas uses midpoint estimate (range 2,800-5,800). The Agent Base Prompt remainder includes the available_skills XML listing (~2,151 tokens of skill descriptions) and the OpenCode core agent instructions.
