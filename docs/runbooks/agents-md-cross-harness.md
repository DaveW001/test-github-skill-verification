# Cross-Harness AGENTS.md Runbook

This runbook describes the user-level instruction architecture shared by OpenCode and Codex. It is intentionally short; detailed rules belong in the linked owner files.

## Layout and progressive disclosure

- OpenCode adapter: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`.
- Codex adapter: `C:\Users\DaveWitkin\.codex\AGENTS.md`.
- Shared modules: `C:\Users\DaveWitkin\.config\opencode\agent-rules\`.
- OpenCode loads only `agent-rules/common-core.md` globally through the `instructions` entry in `opencode.jsonc`; the common core points to `reference-index.md`.
- The trigger index loads `authority-boundaries.md`, `filesystem-and-git.md`, `research-and-evidence.md`, or `agent-authoring.md` only when the task needs it. Project `AGENTS.md` files retain local commands, source lanes, and product constraints.

This progressive disclosure layout keeps always-on context small while preserving a discoverable path to the full rule set. Do not copy a triggered module into either global adapter merely to make it convenient.

## OpenCode and Codex behavior

OpenCode uses its own `permission:` frontmatter and config `instructions`; Codex reads its adapter and can follow the same shared Markdown modules by path. Do not put OpenCode permission syntax in Codex-only instructions. When a rule is universal, add it to the shared module and link it from both adapters; when it is harness-specific, keep it in that adapter.

## Environment and credential handling

Keep `C:\Users\DaveWitkin\.config\opencode\.env` as the central commented source of truth. Consumers should reference variables, not embed values. The affected OpenCode field is `mcp.slack.environment.SLACK_MCP_XOXP_TOKEN`, which must use `{env:SLACK_USER_TOKEN}`. Never print, compare, rotate, or copy the value during maintenance. `secrets-index.jsonc` is metadata-only and should be consulted before credential discovery.

## Safe update procedure

1. Read the relevant adapter, shared module, standards owner, and project file before editing.
2. Back up every existing target and record its SHA-256; record new files as `created-no-preimage`.
3. Edit only the approved target list, using `apply_patch` for normal text and a secret-safe targeted replacement when a literal credential must be removed without exposing it.
4. Read back files, run `validate-agents-architecture.ps1` in the narrow mode for the change, then run `-Mode All`.
5. Run `opencode debug config` in a bounded fresh process; retain only redacted output. Restart Codex/OpenCode sessions when global instructions or newly created agents need to be reloaded.
6. Inspect `git status --short` and `git diff --check`; preserve unrelated dirty worktree changes. Do not commit, push, publish, or rotate credentials as part of routine maintenance.

## Rollback

Restore modified files from `C:\Users\DaveWitkin\.config\opencode\backups\20260731-agents-md-remediation\` using the backup manifest. Remove only created paths marked `created-no-preimage`; never remove the user-level `.env` or alter its contents. After rollback, rerun the validator and effective-config check, then document the reason and remaining uncertainty in the Conductor track.

## Validation artifacts

The deterministic validator is `C:\development\opencode\scripts\validate-agents-architecture.ps1`. Its reports contain paths, names, counts, and hashes only. The Conductor track under `C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\` is the execution record; update its plan, metadata, dashboard, and authoritative ledger together.
