# MCP Tool Inventory

MCP tool families visible in this session (inferred from available skills and tool references):

## Codex (OAuth Account Manager)

- Tools: codex-dashboard, codex-diag, codex-diff, codex-doctor, codex-export, codex-health, codex-import, codex-keychain, codex-label, codex-limits, codex-list, codex-metrics, codex-next, codex-note, codex-refresh, codex-remove, codex-setup, codex-status, codex-switch, codex-tag
- Always-on: yes
- Notes: Large family with ~20 tools. Each tool has a focused but complete JSON schema.

## Chrome DevTools MCP

- Tools: control-chrome_* (accessibility tree interaction, navigation, etc.)
- Always-on: configured but not directly visible in current tokenscope
- Notes: Reference in AGENTS.md mentions these tools as the standard for browser automation.

## Slack MCP

- Tools: Slack messaging tools (send, search, read)
- Always-on: configured, referenced via slack-messaging skill
- Notes: Moderate schema overhead.

## Notes

- The tokenscope baseline report did not enumerate individual MCP tool schemas separately.
- MCP contribution to the system prompt is inferred from the AGENTS.md references and skill descriptions rather than direct measurement.
- The OpenCode export failure (bun index.js not found) means detailed MCP tool schema enumeration was not possible in this session.
