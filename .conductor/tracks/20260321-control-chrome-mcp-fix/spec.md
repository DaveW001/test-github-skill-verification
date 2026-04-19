# Spec

## Goal
Fix the "control-chrome" MCP server that shows a red dot (error state) in the OpenCode desktop application interface.

## Background
The OpenCode desktop application shows three MCP servers:
1. `control-chrome` - Red dot (error state)
2. `playwright` - Gray dot (disabled) 
3. `slack` - Green dot (connected)

The `control-chrome` server is not configured in the OpenCode configuration files (`opencode.json` or `opencode.jsonc`), yet it appears in the UI with an error state. This suggests it may be a built-in server or was recently installed through the UI but is failing to connect.

## Requirements
- [x] Identify the source/configuration of the "control-chrome" MCP server
- [x] Determine why it's showing an error state (red dot)
- [x] Move configuration from project-level to global user-level
  - [x] Add proper configuration to global config file
  - [x] Remove from project-level config file
  - [x] Fix command format to use npx
- [x] Ensure the fix doesn't affect other MCP servers (playwright, slack)

## Non-Requirements
- [ ] Implementing new MCP server functionality
- [ ] Modifying the playwright or slack MCP server configurations
- [ ] Changing the OpenCode application code

## Acceptance Criteria
- [x] The "control-chrome" server either connects successfully (green dot) or is removed from the UI
- [x] No other MCP servers are affected
- [x] The fix is documented for future reference
- [x] Real-world test cases are documented for validation
  - [x] 8 comprehensive test cases created
  - [x] Test execution script generated (test_chrome_devtools_mcp.py)
  - [x] All 8 tests executed successfully via MCP tools
  - [x] Test results documented with screenshots and metrics