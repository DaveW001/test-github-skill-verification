
# Final Report: Prompt Schema Overhead Research

**Date:** 2026-06-01
**Track:** 20260531-prompt-schema-overhead-research

---

## Executive Summary

The baseline system prompt consumes **17,377 tokens** (inferred from API telemetry). The target of **15,000 tokens is reachable** through a single aggressive but fully reversible local toggle: disabling the Codex/account-management plugin (oc-codex-multi-auth), which is estimated to save 2,000-3,500 tokens. This would bring the estimated range to **13,877-15,377 tokens**.

However, the Codex A/B test to confirm this estimate precisely has been **deferred** pending a fresh OpenCode session (other sessions currently running). All other components (MCP servers, native tools, task/subagent schemas) contribute significant but less actionable overhead.

---

## Measurements

| Scenario | System Tokens | Delta vs Baseline | Artifact | Confidence |
|---|---:|---:|---|---|
| Baseline (Codex enabled) | 17,377 | 0 | artifacts/baseline-tokenscope.txt | High |
| Codex disabled (estimated) | 13,877-15,377 | -2,000 to -3,500 | Prior estimate (A/B test deferred) | Medium |
| MCP servers | 0 (all disabled) | 0 | artifacts/mcp-enabled-test-decision.md | High |
| Native tool schemas (estimated) | ~2,350 | part of baseline | artifacts/schema-token-estimates.md | Medium |
| Task/subagent definitions | ~1,095 | part of baseline | artifacts/schema-token-estimates.md | Medium |
| Skill metadata | ~962 | part of baseline | artifacts/schema-token-estimates.md | Medium |
| Runtime/agent scaffolding (remainder) | ~10,220 | part of baseline | Calculated remainder | Low |

---

## Codex Tooling Findings

- **Origin identified:** The oc-codex-multi-auth plugin in opencode.jsonc (line 5 of the plugin array)
- **Tool count:** 20 Codex tools injected (codex-dashboard, codex-doctor, codex-list, codex-status, codex-switch, etc.)
- **Estimated overhead:** 2,000-3,500 tokens (prior estimate midpoint: 2,750; ~15.8% of baseline)
- **Config toggle:** Remove the plugin entry from opencode.jsonc plugin array
- **User impact:** Loses Codex account management tools (auth switching, health checks, etc.)
- **A/B status:** DEFERRED - requires fresh session. Script for config edit prepared in Task 4.2.

---

## MCP Schema Findings

- **MCP servers in config:** 3 (playwright, control-chrome, slack) - ALL disabled
- **Current overhead:** 0 tokens - no schemas injected when disabled
- **If re-enabled:** Estimated 2,800-5,800 tokens additional overhead (prior estimate)
- **Recommendation:** Keep disabled unless MCP features are specifically needed
- **User has NOT approved enabling MCP servers for A/B testing**

---

## Native Tool Schema Findings

- **Tool count:** 18+ native tools (bash, read, write, edit, glob, grep, osgrep, compress, task, skill, skill_find, skill_resource, skill_use, todowrite, question, webfetch, websearch, tokenscope)
- **Estimated overhead:** ~2,350 tokens (prior estimate)
- **Configurable?:** No - schemas are built into OpenCode runtime
- **Upstream opportunity:** Compact schema mode would save ~1,000-1,500 tokens

---

## Task/Subagent Findings

- **Skill metadata:** ~962 tokens (379 skills listing + 583 full tool description boilerplate)
- **Subagent definitions:** ~1,095 tokens (305 subagent listing + 790 full task tool description)
- **Total:** ~2,057 tokens combined
- **Configurable?:** Partial - skill/task tool descriptions may have config-slimming options
- **Upstream opportunity:** Compact descriptions mode would save ~500-800 tokens

---

## Can We Reach 15,000 Tokens?

**Conclusion: Aggressive reversible local toggles may reach 15,000 tokens, but safe defaults do not.**

### Reasoning:
1. **Baseline:** 17,377 tokens (safe defaults, all plugins enabled)
2. **Required savings:** 17,377 - 15,000 = 2,377 tokens
3. **Codex plugin disable estimated savings:** 2,000-3,500 tokens
4. **Estimated range with Codex disabled:** 13,877-15,377
5. **Conclusion:** The single Codex toggle alone likely brings system prompts to or below 15,000 tokens

### What's required:
- Remove the oc-codex-multi-auth entry from opencode.jsonc plugin array
- Restart OpenCode for config to take effect
- Re-enable the plugin if Codex account tools are needed

### Verdict: **REACHABLE with aggressive local toggle**

---

## Recommended Next Actions

| Priority | Action | Impact | Effort |
|---:|---|---|---|
| 1 | **Run Codex A/B test** in fresh session to confirm 2,000-3,500 savings | Confirms/exact measurement | 1 session restart |
| 2 | **Consider disabling Codex plugin** if Codex tools aren't regularly used | Saves 2,000-3,500 tokens | Config edit + restart |
| 3 | **Keep MCP servers disabled** unless needed | Prevents 2,800-5,800 token regression | Already done |
| 4 | **File upstream issue** for compact native tool schema mode | Potential additional savings | One-time |
| 5 | **File upstream issue** for compact skill/task tool descriptions | Potential additional savings | One-time |

---

## Caveats

1. **Codex estimate is from prior track (indirect measurement), not from a controlled experiment in this track.** The A/B test was deferred because other OpenCode sessions are running.
2. **Tokenscope context export remains broken** due to a missing un runtime dependency in the tokenscope plugin. Direct schema token measurement was unavailable.
3. **Native tool and task/subagent estimates are from prior track data**, not re-measured in this session.
4. **The 15,000-token target assumes aggressive local toggles** (disabling Codex). With all defaults enabled, the baseline is 17,377.
5. **MCP server overhead (0 tokens currently) will increase if any MCP server is enabled.**

---

## Artifacts

- Baseline: artifacts/baseline-tokenscope.txt
- Config inventory: artifacts/effective-config-inventory.md
- Tool surface: artifacts/tool-surface-inventory.md
- Codex origin: artifacts/codex-tool-origin-analysis.md
- Schema estimates: artifacts/schema-token-estimates.md
- A/B results (pending): artifacts/ab-test-results.md
- MCP decision: artifacts/mcp-enabled-test-decision.md
- Upstream draft: artifacts/upstream-issue-draft.md
