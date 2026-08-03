# Stage 2 Independent Plan Re-review (R2)

## Verdict

**BLOCKED** — the original blocking findings have been repaired, but two new execution-readiness defects remain in the repaired plan. Do not begin Phase 1.

## Reviewer independence

- Plan creator: `root` on `gpt-5.6-sol`.
- Reviewer: `conductor-plan-reviewer-2` on `gpt-5.6-terra`.
- Gate: **PASS** — identity and model both differ.

## Evidence reviewed

- `C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\spec.md`, `plan.md`, `metadata.json`, and the historical blocked report `review-report-2026-07-31.md`.
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`, `C:\Users\DaveWitkin\.codex\AGENTS.md`, the complete `agent-writer` skill and both references, and the three OpenCode standards documents.
- Read-only dry runs: task-ID/count check (15), metadata count/classification/pipeline check, `opencode debug config --help`, and literal execution of the planned adapter acceptance commands. No target AGENTS/config/skill files were edited; no credential was printed, rotated, or changed.

## Repaired findings confirmed

- The active review-status vocabulary is consistently `accepted` / `blocked`; Task 0.2 and the phase exit use `accepted`.
- The plan has 15 tracked tasks, and `metadata.json.progress.totalTasks` is 15.
- Classification is `uncertain` with a `standard` path and rationale that explicitly covers the authentication-bearing shared configuration field.
- The closed table includes M01-M15 and C01-C09. It distinguishes modify, verify-only, and create entries; backup/rollback language requires pre-images only for modifications and `created-no-preimage` removal only for created paths.
- The plan requires a deterministic validator plus clean and negative fixtures, keeps diagnostics separate from named authoritative checks, and preserves dirty-worktree, no-print, and no-rotation boundaries.
- The approved property/value contract is exact: `mcp.slack.environment.SLACK_MCP_XOXP_TOKEN` -> `{env:SLACK_USER_TOKEN}`. `.env` is verify-only.
- The frontmatter policy distinguishes deprecated capability-map keys from the documented `tools.skill: false` exception and retains singular `permission:` controls.
- Instruction wiring requires the exact universal entry, resolved path, uniqueness, and absence of specialized modules; `opencode debug config --help` confirms the command exists.

## Blocking findings

### B1 — Three authoritative PowerShell commands cannot parse

The Task 2.1, 2.2, and 4.4 commands begin their scripts with `${p='...'` rather than `$p='...'`. A literal read-only execution of the Task 2.1 and 2.2 commands returns PowerShell `ParserError` ("Use `{` instead of { in variable names.") before any predicate runs. Task 4.4 has the same construct.

**Required repair:** replace `${p=` with `$p=` in all three commands, then dry-run each against a safe fixture or a copied/read-only target. Preserve their expected exits and artifact/report checks.

### B2 — The instruction-wiring effective-config check is not concretely bounded

Task 2.3 says a "bounded" `opencode debug config` child process will run, but it specifies neither its executable noninteractive form nor a timeout nor a named captured-output path. That does not meet the plan's own deterministic/explicit-command contract for an authentication-bearing shared configuration change.

**Required repair:** name one noninteractive `opencode debug config` command with an explicit timeout mechanism, stdout/stderr destination under the track folder, redaction/no-scalar-output rule, expected exit 0, and the validator's exact inputs. Keep it separate from diagnostics.

## Acceptance condition for the next re-review

Repair B1 and B2 in `plan.md`, keep the closed target table unchanged unless scope changes, and repeat Stage 2 with another independent reviewer identity/model. Do not alter target configuration, instruction, skill, or environment files during that repair.
