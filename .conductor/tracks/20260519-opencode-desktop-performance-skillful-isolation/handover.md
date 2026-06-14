# Handover: OpenCode Desktop Performance Skillful Isolation

Date: 2026-05-19

## Current State

- Track status is still `active`, but the major decision point is complete.
- MCPs `playwright`, `control-chrome`, and `slack` are disabled.
- `@zenobius/opencode-skillful` was temporarily removed, then restored after the A/B result did not show a clear win.
- Final config validation passed.
- CLI smoke test passed with `opencode run -m opencode-go/glm-5.1`.
- User GUI smoke test with Skillful disabled was acceptable and reasonably fast, but not clearly better than the baseline.

## What Was Proven

1. Disabling Skillful did not produce a decisive performance improvement.
2. The current environment still emits duplicate skill-name warnings from overlapping roots.
3. The Desktop log sampling was noisy because the newest file initially stayed stale across restarts.
4. The track recommendation is to keep Skillful enabled for now and investigate duplicate roots or Desktop state separately only if slowdown returns.

## Remaining Work

- Decide whether to clean up duplicate skill roots in a separate branch.
- Close the track if no further action is needed.
- Keep the rollback backup path documented if a future revert is needed.

## Useful Artifacts

- Execution log: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md`
- Plan: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\plan.md`
- Metadata: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\metadata.json`
- Issue log: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log-2026-05-19.md`
- Repo note: `C:\development\opencode\docs\troubleshooting\active\opencode-desktop-white-window-startup.md`

## New-Session Starting Point

Start from the handover summary, not the old interactive session. Re-read the execution log, then only continue if you need to take the duplicate-root cleanup branch or finalize closure.
