# Handover: OpenCode Desktop Config Troubleshooting

Date: 2026-05-19

## Current State

- Track status is still `active`, but the investigation is effectively at validation/closeout.
- The main fix has already been applied: `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` were promoted to Windows user-level environment variables.
- `opencode debug config` parses successfully.
- CLI smoke test passed with `opencode run -m opencode-go/glm-5.1`.
- Desktop GUI prompts worked after restart with both `opencode-go/glm-5.1` and `opencode-go/deepseek-v4-pro`.

## What Was Proven

1. The problem was not a broken JSONC structure.
2. The `.env`-only Go API key setup was unreliable for Desktop.
3. Desktop works when the Go keys exist at Windows user level.
4. The white-window / stale-resume behavior is consistent with Desktop state drift rather than a config parse failure.

## Remaining Work

- Write the final diagnostic report.
- Update `metadata.json` to close the track cleanly.
- Update `.conductor/tracks-ledger.md` to match the final status.
- Optionally decide whether stale Desktop session-state cleanup should be pursued as a separate preventative task.

## Useful Artifacts

- Execution log: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-config-troubleshoot\execution-log.md`
- Plan: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-config-troubleshoot\plan.md`
- Metadata: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-config-troubleshoot\metadata.json`
- Repo note: `C:\development\opencode\docs\troubleshooting\active\opencode-desktop-white-window-startup.md`

## New-Session Starting Point

Start by reading the execution log and then write the final report/closeout artifacts without re-running the full investigation unless Desktop behavior has changed.
