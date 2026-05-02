# opencode-tool-search Plugin Reference

**Last updated:** 2026-04-25  
**Plugin:** `opencode-tool-search@0.4.3`  
**Repository:** https://github.com/M0Rf30/opencode-tool-search  
**License:** MIT  
**Installed:** 2026-04-25 (track: 20260425-tool-search-plugin)

---

## What It Does

Reduces per-turn context/token usage by deferring tool descriptions for tools the model doesn't need every turn. Instead of loading all tool descriptions upfront (~8,400–57,000 tokens depending on tool count), non-core tools get a short `[d]` stub. The model uses two search tools (`tool_search` and `tool_search_regex`) to discover deferred tools on demand.

This implements Claude's [Tool Search Tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) pattern as a standalone OpenCode plugin — no core modifications needed.

---

## How It Works

1. The `tool.definition` hook intercepts every tool before the LLM sees it
2. Tools **not** in `alwaysLoad` get their descriptions replaced with a `[d]` stub (parameters preserved for OpenAI compatibility)
3. Two search tools (`tool_search` and `tool_search_regex`) are always available with full descriptions
4. The system prompt tells the model to use `tool_search` when it encounters deferred tools
5. When the model calls `tool_search("file operations")`, it gets back full descriptions and parameter schemas of matching tools

---

## Current Configuration

**Config location:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

```jsonc
["opencode-tool-search", {
  "alwaysLoad": ["read", "write", "edit", "bash", "glob", "grep", "task", "skill", "todowrite", "todoread", "webfetch", "websearch", "compress"]
}]
```

### `alwaysLoad` Strategy

These tools retain full descriptions at all times — they are never deferred:

| Tool           | Reason                                                                              |
| -------------- | ----------------------------------------------------------------------------------- |
| `read`         | Core file reading — used constantly                                                 |
| `write`        | Core file writing — used constantly                                                 |
| `edit`         | Core file editing — used constantly                                                 |
| `bash`         | Core shell access — used constantly (includes `gh` CLI for GitHub)                  |
| `glob`         | Core file search — used constantly                                                  |
| `grep`         | Core content search — used constantly                                               |
| `task`         | Agent orchestration — needed for subagent launches                                  |
| `skill`        | Skill loading — needed for specialized workflows                                    |
| `todowrite`    | Task tracking — needed for progress management                                      |
| `todoread`     | Task tracking — needed for progress management                                      |
| `webfetch`     | URL fetching — used frequently                                                      |
| `websearch`    | Web search — used frequently                                                        |
| `compress`     | **Critical** — context management via DCP plugin; must never be deferred            |

### Currently Deferred Tools (20)

These tools show `[d]` stubs and must be discovered via search:

- `osgrep` — semantic code search
- `codex-list`, `codex-switch`, `codex-status`, `codex-limits`, `codex-metrics`, `codex-help`, `codex-setup`, `codex-doctor`, `codex-next`, `codex-label`, `codex-tag`, `codex-note`, `codex-dashboard`, `codex-health`, `codex-remove`, `codex-refresh`, `codex-export`, `codex-import` — Codex management tools
- `mystatus` — AI platform quota query

### MCP Tools (Not Deferred)

MCP-sourced tools (Slack, Chrome DevTools) retain full descriptions automatically. They are not currently indexed by the plugin's search tools but this has no practical impact since they're always fully loaded.

---

## Search Tools

### `tool_search` — BM25 Keyword Search

Best for natural language queries.

```
tool_search({ query: "file operations" })        // → read, write, edit, glob
tool_search({ query: "search code" })             // → grep, osgrep
tool_search({ query: "github issues" })           // → bash (gh CLI)
```

### `tool_search_regex` — Regex Pattern Search

Best for specific name patterns (case-insensitive).

```
tool_search_regex({ pattern: "github.*issue" })   // → GitHub issue tools
tool_search_regex({ pattern: "^lsp_" })            // → all LSP tools
tool_search_regex({ pattern: "codex|dashboard" })  // → Codex management tools
```

---

## Configuration Options

| Option             | Type       | Default | Description                                          |
| ------------------ | ---------- | ------- | ---------------------------------------------------- |
| `alwaysLoad`       | `string[]` | `[]`    | Tool IDs that keep full descriptions (never deferred) |
| `searchLimit`      | `number`   | `5`     | Max results per search query                         |
| `bm25.k1`          | `number`   | `0.9`   | Term frequency saturation (0.5–2.0)                  |
| `bm25.b`           | `number`   | `0.4`   | Document length normalization (0–1)                   |
| `deferDescription` | `string`   | `[d]`   | Custom stub text for deferred tools                   |

### BM25 Tuning

Current defaults (`k1: 0.9`, `b: 0.4`) are optimized for smaller models sending vague queries. For capable models writing specific queries, increase `k1` toward `1.5`:

```jsonc
["opencode-tool-search", {
  "alwaysLoad": ["read", "write", "edit", "bash"],
  "bm25": { "k1": 1.5, "b": 0.75 },
  "searchLimit": 10
}]
```

---

## Compatibility

| Component               | Status | Notes                                                                                    |
| ----------------------- | ------ | ---------------------------------------------------------------------------------------- |
| DCP plugin (`@tarquinen/opencode-dcp`) | ✅ Compatible   | Different hooks: DCP uses `tool.execute.before`, this uses `tool.definition`                 |
| OpenAI models           | ✅ Compatible   | v0.4.3+ preserves parameter schemas; provider-aware system prompts                          |
| MCP tools (Slack, Chrome) | ⚠️ Partial    | Tools keep full descriptions but are not indexed in search (low practical impact)          |
| OpenCode < v1.4.10      | ❌ Not supported | Requires `tool.definition` hook                                                           |

---

## Known Gaps

1. **MCP tools not indexed by search**: MCP-sourced tools (Slack, Chrome DevTools) retain full descriptions but don't appear in `tool_search` / `tool_search_regex` results. If indexing is needed, file an issue at [M0Rf30/opencode-tool-search](https://github.com/M0Rf30/opencode-tool-search/issues).
2. **Deferred tools still occupy tool list slots**: Each deferred tool still has its name (~5-15 tokens), stub (~5 tokens), and parameter schema (~20-50 tokens). Upstream proposals ([opencode#23297](https://github.com/anomalyco/opencode/issues/23297), [opencode#23298](https://github.com/anomalyco/opencode/issues/23298)) would close this gap.

---

## Token Savings Reference

| Setup                | Total Tools | Deferred | Savings/Turn       |
| -------------------- | ----------- | -------- | ------------------ |
| Built-in only        | ~32         | ~24      | ~8,400 tokens (88%) |
| 3 MCP servers        | ~60         | ~52      | ~17,000 tokens (89%)|
| 6+ MCP servers       | ~190        | ~182     | ~57,000 tokens (91%)|

Current setup: ~35 tools, 20 deferred = **~600-1,000 tokens saved per turn**.

---

## Rollback

```powershell
cp C:\development\opencode\.conductor\tracks\20260425-tool-search-plugin\artifacts\opencode.jsonc.backup-pre-tool-search C:\Users\DaveWitkin\.config\opencode\opencode.jsonc
# Restart OpenCode TUI
```

---

## References

- Plugin README: https://github.com/M0Rf30/opencode-tool-search
- Claude Tool Search docs: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
- Conductor track: `.conductor/tracks/20260425-tool-search-plugin/`
- Validation log: `.conductor/tracks/20260425-tool-search-plugin/artifacts/validation-log.md`
