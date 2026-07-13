# Spec

## Goal
Create a reusable, triggerable `session-db-query` OpenCode lazy-vault skill that teaches agents how to search the OpenCode session SQLite database for arbitrary useful information, distilling the existing `/session-history` command knowledge into a general query reference.

## Restated Goal / Outcome
Build `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\` with concise skill guidance, detailed reference documentation, and an adaptable Python query script template so any agent can discover the skill with `skill_find` and load it with `skill_use` for session lookup, cost analysis, activity tracking, date filtering, and related OpenCode session database questions.

## Restated Constraints / Non-Goals
- Create the skill only in the lazy vault at `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\`.
- Do not place the skill under `C:\Users\DaveWitkin\.config\opencode\skill\` or make it always-loaded.
- Use the existing command `C:\Users\DaveWitkin\.config\opencode\commands\session-history.md` as authoritative source material, but do not copy the full command or report generator verbatim.
- Do not copy private session data, tokens, raw IDs, or secrets into skill files.
- Make the skill self-contained and general-purpose, not limited to history reports.
- Follow skill-creator patterns: valid frontmatter, progressive disclosure, concise `SKILL.md`, detailed `reference.md`, and a ready-to-adapt script under `scripts\`.
- Execution must use PowerShell via `bash` for file operations because native file tools are broken on this machine.

## Restated Definition of Done
- `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\SKILL.md` exists with valid YAML frontmatter: `name: session-db-query`; description includes trigger keywords; filename is all caps.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\reference.md` exists with detailed schema documentation, column interpretation guidance, query patterns, and provider billing classification guidance.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\scripts\query_sessions.py` exists and is a general-purpose Python script template accepting optional args such as project path, date range, and limit; Python syntax is valid.
- Structural validation passes: directory name matches frontmatter name, YAML is parseable, `SKILL.md` is uppercase, and required files exist.

## Requirements
- [ ] Distill database location, access method, timestamp conversion, archive semantics, Windows/Python execution gotchas, and reusable query examples from `C:\Users\DaveWitkin\.config\opencode\commands\session-history.md`.
- [ ] Create a discoverable lazy-vault skill named `session-db-query` with trigger-rich frontmatter description.
- [ ] Provide detailed reference documentation for schema gotchas, column interpretation, query recipes, and provider billing classification.
- [ ] Provide an adaptable Python script template that uses `sqlite3`, avoids `python -c`, auto-discovers project/session relationships where practical, supports bounded CLI arguments, and prints structured output.
- [ ] Validate file existence, frontmatter correctness, YAML parseability, and Python syntax.
- [ ] Register this Conductor track in `.conductor\tracks.md` and `.conductor\tracks-ledger.md` if present.

## Non-Requirements
- [ ] Do not implement a new OpenCode command.
- [ ] Do not query or export real private session content as part of the skill artifacts.
- [ ] Do not install dependencies or require the unavailable `sqlite3` CLI.
- [ ] Do not build a full reporting application or duplicate `/session-history` formatting.
- [ ] Do not modify production application code.

## Acceptance Criteria
- [ ] `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\SKILL.md` contains `name: session-db-query`, trigger keywords including `session database`, `opencode.db`, `SQLite`, `session history`, `cost analysis`, and `token usage`, plus clear instructions to read `reference.md` and adapt `scripts\query_sessions.py`.
- [ ] `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\reference.md` documents `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`, Unix milliseconds timestamp handling with `/ 1000`, the instruction not to filter `time_archived IS NULL`, Python `sqlite3` usage, and temp-file script execution on Windows.
- [ ] `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\scripts\query_sessions.py` compiles with Python and supports `--project-path`, `--start-date`, `--end-date`, `--limit`, and `--format` arguments.
- [ ] The skill files contain no raw private session rows, no OAuth tokens, and no copied full `/session-history` report generator.
- [ ] `.conductor\tracks.md` and `.conductor\tracks-ledger.md` have exactly one row/entry for `20260710-session-db-query-skill` after execution.
