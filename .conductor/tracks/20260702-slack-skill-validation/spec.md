# Spec: Slack Skill Validation and Documentation Cross-References

## Goal / Outcome
Validate the new `slack-send-message` OpenCode skill for quality, accuracy, structure, naming, internal references, and documentation consistency, then make minimal related documentation updates so Slack messaging guidance is discoverable and bidirectionally cross-referenced.

## Constraints / Non-Goals
- Do not expose, print, copy, or commit Slack token values; `secrets-index.jsonc` is metadata only.
- Do not modify `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` or any MCP configuration.
- Do not change existing `slack-messaging` MCP tool instructions except adding a minimal cross-reference.
- Use PowerShell-first via the `bash` tool only; native Read/Edit/Write/glob/grep tools are broken with active `Bun is not defined` errors.
- Use `-LiteralPath` and double-quoted Windows paths.
- Use literal `[string]::Replace()` / string operations for edits; do not use regex `-replace` for structural edits.
- Keep all edits minimal and surgical.

## Tool Preflight for All Stages
- file-tool status: BROKEN. Native Read/Edit/Write/glob/grep return `Bun is not defined`.
- fallback shell: PowerShell-first via `bash` tool.
- cmdlet mapping: Read = `Get-Content -Raw`; Write = `Set-Content -Encoding utf8 -NoNewline`; grep = `Select-String`; glob = `Get-ChildItem -Recurse`; edit = `[string]::Replace()` / literal string ops.
- path quoting: Always use `-LiteralPath` and double-quoted paths on Windows.
- artifact output format: Write reports/logs with PowerShell `Set-Content`, not native Write.

## Target Files
- `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\SKILL.md`
- `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\reference.md`
- `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\gotchas.md`
- `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\scripts\send-slack-message.py`
- `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\scripts\Send-SlackMessage.ps1`
- `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\.env.example`
- `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md`
- `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`

## Definition of Done
1. `slack-send-message` passes validation: frontmatter YAML is parseable, `name` matches directory, `description` is under 1024 characters, referenced files exist, and internal links are not broken.
2. `secrets-index.jsonc` includes `email-triage` as a Slack bot token consumer without adding any secret value.
3. `AGENTS.md` has a discoverable Reference Index entry for Slack messaging skills.
4. `slack-messaging` and `slack-send-message` cross-reference each other clearly.
5. Track execution creates an execution log and validation report under `C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\`.

## Deliverables
- Minimal edits to the target documentation files.
- `execution-log-2026-07-02.md` in this track.
- `validation-report-2026-07-02.md` in this track.
