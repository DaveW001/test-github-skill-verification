---
name: osgrep
description: Semantic code search skill in CLI-only canary mode; avoid MCP/service workflows.
triggers:
  intent:
    - semantic code search
    - architecture discovery
    - code navigation
  user_phrases:
    - where do we handle
    - how does this work
    - find code path for
  file_context:
    extensions: [ts, tsx, js, jsx, py, md]
    paths: [src/**, docs/**]
  tool_context:
    before_tools: [read, grep]
    with_tools: [bash]
  error_context:
    - unknown code location
    - large-file exploration
  priority: medium
  suggest_only: false
compatibility: CLI-only canary mode. Do not use `osgrep mcp` for routine workflows.
---

## Status

Osgrep is re-enabled for CLI-only semantic search in canary mode.

- Use direct CLI-style osgrep usage for semantic discovery.
- Do not use `osgrep mcp` or bridge/server workflows for routine automation.
- If osgrep times out or fails, fall back to `grep`, `glob`, targeted `Read`, and focused `bash` commands.
- For explicit osgrep debugging, use `python scripts/utils/osgrep_debug_wrapper.py --help` from the repo root.

## Workaround

Use this operating sequence:

1. Use osgrep for semantic code-path and architecture discovery.
2. Use `grep` for exact symbols and `glob` to narrow likely files.
3. Use targeted `Read` calls once you know the file.
4. If osgrep fails, continue with fallback tools and note fallback in the response.
