# Spec: Install and Validate opencode-tool-search Plugin

**Track ID**: 20260425-tool-search-plugin  
**Created**: 2026-04-25  
**Status**: Active  
**Priority**: High  
**Owner**: Build  

---

## Problem Statement

The `opencode-tool-search` plugin (by M0Rf30) implements Claude's Tool Search pattern using BM25 + regex to let the model discover tools on demand rather than loading all tool descriptions upfront. This reduces per-turn context usage by an estimated 88–91% (~8,400–57,000 tokens depending on tool count). The plugin needs to be installed, configured, and validated in this environment.

**Repository**: https://github.com/M0Rf30/opencode-tool-search  
**Latest version**: v0.4.3 (2026-04-18)  
**npm package**: `opencode-tool-search`  
**License**: MIT  

---

## Goals

1. Install `opencode-tool-search` as a plugin in OpenCode's global configuration.
2. Configure `alwaysLoad` list to preserve core tools that should never be deferred (crucially including context management tools like `compress`).
3. Benchmark system prompt token usage before and after installation to empirically prove the savings.
4. Validate that the plugin loads correctly and the two search tools (`tool_search`, `tool_search_regex`) are available via headless CLI execution.
5. Validate that deferred tools show `[d]` stubs while core tools retain full descriptions.
6. Update OpenCode configuration reference documentation.
7. Capture reproducible verification evidence in track artifacts.

---

## Requirements

- [ ] Plugin `opencode-tool-search` added to `opencode.jsonc` plugin array with `alwaysLoad` configuration.
- [ ] `alwaysLoad` list includes: `read`, `write`, `edit`, `bash`, `glob`, `grep`, `task`, `skill`, `todowrite`, `todoread`, `webfetch`, `websearch`, `compress`.
- [ ] BM25 tuning parameters left at defaults initially (k1=0.9, b=0.4).
- [ ] Immediate config syntax validation confirms JSONC parses correctly (tuple format validation).
- [ ] Token savings are measured and recorded (baseline vs. post-install).
- [ ] Two new tools (`tool_search`, `tool_search_regex`) are discoverable and functional via headless `opencode run` checks.
- [ ] Deferred tools show shortened `[d]` stub descriptions.
- [ ] Configuration reference doc (`docs/reference/opencode-configuration.md`) updated to list the new plugin.

---

## Non-Requirements

- Modifying plugin source code.
- Cloning/building from source (npm install is sufficient).
- Tuning BM25 parameters beyond defaults.
- Compatibility testing with RTK plugin (confirmed compatible per README).

---

## Acceptance Criteria

- [ ] `opencode.jsonc` plugin array includes `["opencode-tool-search", { "alwaysLoad": [...] }]`.
- [ ] Immediate `opencode debug config` shows successful parsing (no JSONC tuple errors).
- [ ] Baseline and post-install token usage recorded in validation log.
- [ ] Headless CLI tests (`opencode run`) confirm `tool_search` and `tool_search_regex` operate correctly.
- [ ] Core tools retain full descriptions; Non-core tools show `[d]` deferred stubs.
- [ ] Configuration reference doc updated.
- [ ] Validation log captured in track artifacts.
- [ ] All plan.md tasks marked [x].

---

## Risks

| Risk | Mitigation |
|------|-----------|
| JSONC parser chokes on tuple syntax | Immediate syntax check after file edit, before running functional tests. |
| Context management breakage | `compress` explicitly added to `alwaysLoad` so the agent always knows how to prune context. |
| Plugin conflicts with existing DCP plugin | Both use different hooks (`tool.definition` vs `tool.execute.before`); confirmed compatible. |
| OpenAI models may call deferred tools ignoring stubs | Plugin v0.4.3+ includes provider-aware system prompts; parameter schemas preserved. |
| `tool.definition` hook not supported | Requires OpenCode v1.4.10+; verify version before install. |

---

## References

- Plugin README: https://github.com/M0Rf30/opencode-tool-search  
- Claude Tool Search docs: https://platform.claude.com/docs/en/agents-and-tools/tool-search-tool  
- Upstream issue for `hidden` field: opencode#23297  
- Precedent track: 20260314-dcp-install-validation
