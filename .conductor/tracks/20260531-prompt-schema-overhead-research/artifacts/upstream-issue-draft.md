# Upstream Issue Draft

## Problem
OpenCode system prompt overhead remains high at 17,377 tokens after local prompt reductions.

## Requested Improvements
1. Compact native tool schema mode - trim verbose JSON Schema parameter definitions
2. Lazy-loaded MCP/plugin tool schemas - don't inject schemas until servers connect
3. Configurable Codex/account-management tool loading - allow granular enable/disable
4. Compact task/subagent schema mode - shorten subagent type descriptions and usage notes
5. Tokenscope/context export reliability fix for missing Bun package import (import 'bun' only works under bun runtime, not Node.js)

## Evidence
- Baseline system tokens: 17,377
- Native tool schemas: estimated ~2,350 tokens
- Skill tool metadata: ~962 tokens
- Task/subagent definitions: ~1,095 tokens
- MCP server schemas (if enabled): estimated 2,800-5,800 tokens
- Codex tooling: estimated 2,000-3,500 tokens

## Artifacts
- Baseline: C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\baseline-tokenscope.txt
- Schema estimates: C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\schema-token-estimates.md
- Final report: C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\final-report.md
