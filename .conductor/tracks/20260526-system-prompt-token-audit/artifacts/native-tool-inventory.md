# Native Tool Inventory

These tools are provided by the OpenCode runtime (non-MCP, non-skill tools):

## functions.*

- unctions.bash - terminal command execution (PowerShell 7+) - long schema: yes
- unctions.read - file/directory reading - long schema: yes
- unctions.edit - exact string replacement in files - long schema: yes
- unctions.write - file writing/creation - long schema: yes
- unctions.glob - file pattern matching search - long schema: yes
- unctions.grep - content search using regex - long schema: yes
- unctions.osgrep - semantic code search (CLI-only canary) - long schema: yes
- unctions.skill - load lazy skills - long schema: yes
- unctions.task - launch subagents - long schema: yes
- unctions.compress - compress conversation sections into summaries - long schema: yes
- unctions.tokenscope - analyze token usage across session - long schema: yes
- unctions.todowrite - create/maintain task lists - long schema: yes
- unctions.question - ask user questions during execution - long schema: yes
- unctions.webfetch - fetch content from URLs - long schema: yes
- unctions.websearch - web search with live crawling - long schema: yes

## multi_tool_use.*

- Not directly visible; multi-tool invocation is handled by the OpenCode runtime.

## Notes

- All unctions.* tools have long parameter schemas including JSON Schema definitions.
- The skill, task, compress, and tokenscope tools have the most verbose descriptions due to extensive inline documentation.
