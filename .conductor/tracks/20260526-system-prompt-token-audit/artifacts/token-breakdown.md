# Token Breakdown

## Measurement Method

Approximate token estimation using character count / 4 rule. Model-specific tokenization unavailable (approx mode per tokenscope).

Baseline system tokens (from tokenscope): 27,280

## AGENTS.md

- Source file: C:\Users\DaveWitkin\.config\opencode\AGENTS.md
- Character count: 11,497
- Estimated tokens: 2,875

## Skill Tool Metadata

- Skills counted: 32
- Description-only tokens: ~2,151
- Full skill tool description tokens: ~5,712

## Subagent Definitions

- Subagents counted: 8
- Description-only tokens: ~363
- Full task tool description tokens: ~901

## Native Tool Schemas

15 native tools observed with long JSON Schema parameter definitions.

High-overhead tools (extensive inline docs, examples, and rules):
- bash: ~2500 chars (terminal execution with shell notes, quoting rules, git/github guidance)
- task: ~2000 chars (subagent types, usage notes, batching rules)
- skill: ~800 chars (skill loading instructions)
- compress: ~1200 chars (compression philosophy, format spec, boundary IDs)

Medium-overhead tools (standard schemas with usage notes):
- read: ~600 chars
- edit: ~500 chars
- write: ~400 chars
- websearch: ~400 chars
- webfetch: ~300 chars
- tokenscope: ~200 chars
- todowrite: ~300 chars
- question: ~300 chars

Lower-overhead tools (minimal schemas):
- glob: ~200 chars
- grep: ~200 chars
- osgrep: ~300 chars

Total estimated characters: ~9,400
Estimated tokens (chars/4): ~2,350

Note: These are estimated from visible tool descriptions in the system prompt. Actual schema JSON is likely larger due to nested parameter definitions.

## MCP Tool Schemas

MCP tool schemas could not be directly measured due to the OpenCode export failure (bun index.js missing).

Estimated ranges per family:
- Codex (20 tools): estimated range 2,000-3,500 tokens, justification: ~20 focused tools with JSON schemas, moderate parameter docs each (~100-175 tokens/tool)
- Chrome DevTools MCP: estimated range 500-1,500 tokens, justification: many action-oriented tools with repeated parameter patterns
- Slack MCP: estimated range 300-800 tokens, justification: moderate number of tools with simple message schemas

Total estimated MCP range: 2,800-5,800 tokens
Best single estimate: ~4,300 tokens (midpoint)

Note: This is a rough estimate. The OpenCode export failure prevented direct measurement. The actual contribution may be higher or lower.

## Agent Base Prompt / Environment Remainder

- Baseline system tokens: 27,280
- Measured subtotal: 16,138
- Remainder: 11,142
- Interpretation: base agent prompt + environment block + AGENTS.md system instructions + any unmeasured overhead

The remainder (~40.8% of system prompt) includes:
- The OpenCode base agent prompt (identity, behavioral rules, format instructions)
- The environment block (working directory, platform, date)
- The skill listing block (available_skills XML with all 32 skill entries)
- The AGENTS.md system instructions block
- Any additional formatting overhead (XML tags, section separators)

Variance check: Measured subtotal + remainder = 27,280 = baseline (0% variance)

## Summary Table

| Component | Estimated Tokens | Percent of System | Configurable? | Evidence Source |
|---|---:|---:|---|---|
| Agent Base Prompt / Environment Remainder | 11,142 | 40.8% | No | calculated remainder |
| Skill Tool Metadata (full tool desc) | 5,712 | 20.9% | Partial | baseline-tokenscope.txt |
| MCP Tool Schemas | 4,300 | 15.8% | Partial | mcp-tool-inventory.md (estimated) |
| AGENTS.md | 2,875 | 10.5% | Yes | AGENTS.md character count |
| Native Tool Schemas | 2,350 | 8.6% | No / Partial | native-tool-inventory.md |
| Subagent Definitions (full tool desc) | 901 | 3.3% | Partial | baseline-tokenscope.txt |
| **Total** | **27,280** | **100%** | | |

Note: MCP Tool Schemas uses midpoint estimate (range 2,800-5,800). The Agent Base Prompt remainder includes the available_skills XML listing (~2,151 tokens of skill descriptions) and the OpenCode core agent instructions.






