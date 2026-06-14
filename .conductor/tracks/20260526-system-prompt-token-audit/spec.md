# Spec: System Prompt Token Audit Remediation & Final Validation

## Goal / Outcome

Repair the partially completed `20260526-system-prompt-token-audit` track, validate that prior local prompt-reduction edits did not break OpenCode behavior, capture a fresh post-reduction token measurement, and produce an evidence-based final conclusion about whether the `<=15000` system-token target was achieved locally or remains blocked by non-local prompt overhead.

## Current Track Fit Decision

The existing conductor track at `.conductor/tracks/20260526-system-prompt-token-audit/` is the correct active track for this work. Do not create a new track. The requested next steps are remediation, validation, and handover for the same system-prompt-token audit objective.

## Constraints / Non-Goals

- Do not modify OpenCode application source code.
- Do not execute additional prompt-reduction edits beyond narrowly repairing broken local configuration/metadata created by the prior partial implementation.
- Do not disable MCP servers without explicit user approval.
- Preserve rollback paths before any additional edit.
- Keep skill frontmatter valid YAML.
- Prefer ASCII-safe text in artifacts to avoid control-character corruption.
- Treat the `<=15000` target as an outcome to validate, not a claim to force.
- If the target is not achieved, distinguish achieved local savings from prompt overhead that is likely controlled by OpenCode core, native tool schemas, MCP schemas, or other non-local prompt assembly.

## Definition of Done

- The four known broken skill `SKILL.md` frontmatter blocks parse as valid YAML.
- All 14 previously edited skill frontmatter blocks parse as valid YAML.
- Corrupted control characters are removed from the named local artifacts and `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`.
- Knowledge-graph and Slack trigger metadata is verified and restored if missing.
- `artifacts/post-reduction-tokenscope.txt` exists from a fresh OpenCode session.
- `artifacts/final-report.md` contains token comparison, component changes, validation results, and a clear conclusion.
- `metadata.json`, `.conductor/tracks.md`, `.conductor/tracks-ledger.md`, `plan.md`, `execution-log.md`, and `change-log.md` agree on the final track status.
- The build agent can hand off with no required extra repository exploration.

## In Scope

- Fix YAML quoting in these external skill files:
  - `C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md`
  - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md`
  - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md`
  - `C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md`
- Validate all 14 previously edited skill frontmatter blocks.
- Repair ASCII/control-character corruption in:
  - `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/reduction-proposals.md`
  - `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
  - `.conductor/tracks/20260526-system-prompt-token-audit/execution-log.md`
  - `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
- Verify trigger metadata in:
  - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md`
  - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md`
  - `C:\Users\DaveWitkin\.agents\skills\slack-messaging\SKILL.md`
- Capture and analyze post-reduction token telemetry.
- Synchronize conductor track bookkeeping.

## Out of Scope

- Editing `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.go`, `.rs`, or other application source files in the OpenCode repository.
- Rewriting skill body workflows for stylistic improvements.
- Removing or disabling Codex, Chrome DevTools, Slack, Google, Outlook, or other MCP servers.
- Re-attempting subagent prompt reductions unless an exact local config file is discovered by evidence already in the track artifacts.

## Required Artifacts

- `.conductor/tracks/20260526-system-prompt-token-audit/spec.md`
- `.conductor/tracks/20260526-system-prompt-token-audit/plan.md`
- `.conductor/tracks/20260526-system-prompt-token-audit/metadata.json`
- `.conductor/tracks/20260526-system-prompt-token-audit/execution-log.md`
- `.conductor/tracks/20260526-system-prompt-token-audit/change-log.md`
- `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/post-reduction-tokenscope.txt`
- `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`

## Acceptance Criteria

- [ ] YAML validation passes for every edited skill file listed in the plan.
- [ ] Control-character scan reports no disallowed control characters in the specified markdown/config files.
- [ ] Trigger metadata check passes or missing triggers are restored from backups and revalidated.
- [ ] Fresh-session `tokenscope` output is copied to `artifacts/post-reduction-tokenscope.txt`.
- [ ] Final report states one of these exact conclusions:
  - `Target achieved locally.`
  - `Target not achieved locally; remaining overhead appears non-local.`
  - `Validation incomplete; target status cannot be concluded.`
- [ ] Track status files are internally consistent.

## Known Starting State

- Baseline system tokens were captured as approximately `27280` in `artifacts/baseline-tokenscope.txt`.
- Prior local edits were applied to `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` and 14 skill files.
- Four skill files currently have invalid YAML frontmatter due to unquoted `: ` in description values.
- Subagent config location was not found and should remain blocked unless a precise local path is already documented.
- MCP reduction was skipped and should remain skipped without explicit user approval.
