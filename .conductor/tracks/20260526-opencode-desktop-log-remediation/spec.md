# OpenCode Desktop Log Remediation

## Track ID

20260526-opencode-desktop-log-remediation

## Goal / Outcome

Prepare an execution-ready remediation track for an AI build agent to stabilize OpenCode Desktop by addressing the concrete issues verified in the May 26, 2026 logs: repeated plugin load failures, Git snapshot blockage caused by `git gc`, and excessive duplicate skill warnings. The plan must guide the build agent through safe backups, targeted cleanup, validation, and handoff without requiring additional repo exploration.

## Constraints / Non-Goals

- Do not implement application/product code changes anywhere in the repo.
- Do not modify source files outside documentation and conductor artifacts as part of this planning task.
- Do not execute the remediation plan in this track.
- Do not assume the Desktop issue is an installer or auto-update bug unless new evidence is captured.
- Do not delete broad OpenCode state, auth material, or unrelated cache directories without first creating backups and recording rollback steps.
- Do not remove duplicate skill directories unless the plan explicitly backs them up and validates the authoritative replacement path.
- Do not print secrets or full sensitive config values in logs, reports, or screenshots.

## Definition Of Done

- A build agent can execute the remediation without additional discovery beyond what is written in `plan.md`.
- The plan explicitly addresses the three validated problem classes:
  1. failing cached plugins (`@zenobius/opencode-skillful`, `@tarquinen/opencode-dcp`, `opencode-mystatus`)
  2. Git snapshot blockage from `git gc` / stale GC state
  3. duplicate skill-root warnings across global and workspace roots
- Every task in `plan.md` is atomic, ordered, tied to exact file paths, and includes verification and recovery guidance.
- The plan states that installer/update-loop behavior is unproven from the inspected logs and should only be investigated if failures persist after the targeted fixes.
- The plan includes final validation steps for Desktop startup, log inspection, and handoff documentation.

## Evidence Summary

The following findings were verified from `C:\Users\DaveWitkin\.local\share\opencode\log` on 2026-05-26:

1. **Plugin load failures are repeated and high-confidence**
   - Verified in `C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T123547.log`
   - `@zenobius/opencode-skillful` fails with `__require is not a function`
   - `@tarquinen/opencode-dcp@latest` fails with missing `dist\lib\config`
   - `opencode-mystatus` fails with missing `@opencode-ai\plugin\dist\tool`
   - These failures repeat many times within seconds, indicating repeated startup/plugin initialization failure.

2. **Git snapshotting is blocked by active or stale garbage collection**
   - Verified in `C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T133546.log`
   - Snapshot service reports: `fatal: gc is already running on machine 'dwitkin2025' pid 62132`
   - The affected repository is likely `C:\development\marketing` based on surrounding duplicate-skill and workspace activity.

3. **Duplicate skill warnings are widespread but likely secondary**
   - Verified in `C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T123547.log`
   - Verified in `C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T133546.log`
   - Duplicate skill roots include:
     - `C:\Users\DaveWitkin\.agents\skills\...`
     - `C:\Users\DaveWitkin\.config\opencode\skill\...`
     - `C:\Users\DaveWitkin\.config\opencode\skills\...`
     - workspace-local duplicates under `C:\development\marketing\.agents\skills\...` and `C:\development\marketing\.opencode\skills\...`

4. **Installer/update failure is not evidenced by the inspected logs**
   - Searches for `installer`, `update`, `updating`, `restart`, `crash`, `exception`, `panic`, `electron-updater`, and `squirrel` returned no direct matches in the focused logs.
   - The current best-supported hypothesis is runtime startup instability rather than installer failure.

5. **A minor non-blocking MCP warning is present**
   - `service=mcp clientName=slack error=MCP error -32601: prompts not supported failed to get prompts`
   - This does not currently appear to be the primary remediation target.

## Scope

In scope:

- `C:\Users\DaveWitkin\.local\share\opencode\log`
- `C:\Users\DaveWitkin\.cache\opencode\packages`
- `C:\Users\DaveWitkin\.config\opencode`
- `C:\Users\DaveWitkin\.agents\skills`
- `C:\development\marketing\.agents\skills`
- `C:\development\marketing\.opencode\skills`
- `C:\development\marketing\.git`
- `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation`

Out of scope unless post-fix validation still fails:

- Reinstalling OpenCode Desktop
- Investigating updater internals
- Refactoring skills or plugins at source level
- Editing repo production code

## Implementation Strategy

Use the smallest reversible sequence:

1. Capture backups and a fresh evidence snapshot.
2. Resolve the Git snapshot blockage.
3. Purge only the failing plugin cache directories.
4. Relaunch Desktop and validate whether plugin errors disappear.
5. If Desktop still starts noisily, inventory and then optionally reduce duplicate skill roots with explicit rollback.
6. Only investigate installer/update mechanisms if the targeted fixes do not stabilize startup.

## Risks

1. **Deleting the wrong cache directory** could force unnecessary redownloads or lose evidence.
   - Mitigation: back up target directories and record exact paths before deletion.
2. **Killing an active `git gc` during legitimate repository maintenance** could leave temporary Git lock artifacts.
   - Mitigation: capture process details first, then verify and remove only known stale GC lock files.
3. **Duplicate skill cleanup could break expected skill resolution order** if the wrong root is treated as authoritative.
   - Mitigation: make duplicate cleanup conditional, backup-first, and validate loaded roots after each change.

## Build-Agent Expectations

The build agent executing this track should:

- follow the checklist in strict order,
- avoid improvising beyond the documented recovery branches,
- update checkbox state as work progresses,
- record final evidence in the track artifacts,
- stop and document blockers instead of making broad destructive changes.
