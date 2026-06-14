# Restore OpenCode Scheduler Plugin and Validate Scheduled Jobs

## Goal / Outcome

Restore the `opencode-scheduler` plugin to the active OpenCode global configuration so existing scheduler scope definitions can be loaded again, then validate that the hourly email auto-sort job and other registered OpenCode scheduled jobs are visible, correctly registered, and capable of running under the intended headless pattern.

## Constraints / Non-Goals

- Do not redesign the scheduler architecture.
- Do not delete or recreate existing scheduler scope JSON files unless validation proves they are corrupt and a rollback-safe remediation is documented first.
- Do not change production application code in `C:\development\email-triage` except if a validation failure proves the already-existing scheduled-job wrapper command is wrong.
- Do not remove or downgrade existing OpenCode plugins.
- Do not clear the entire OpenCode cache as a first step; use targeted install/startup validation first.
- Do not run destructive scheduled task operations without a timestamped backup/export of current state.
- Treat `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` as the active global OpenCode config.

## Definition of Done

- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` contains `"opencode-scheduler"` in the top-level `plugin` array exactly once.
- OpenCode startup/plugin validation shows `opencode-scheduler` is installed/loaded or the plugin cache contains `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler` after startup.
- Existing scheduler scope file `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json` remains present and unchanged unless a documented, validated update is required.
- Windows Task Scheduler still contains the hourly email auto-sort task named `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`.
- A manual dry-run of `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1` reaches Graph authentication using the no-WAM/app-only path or fails with an actionable, documented auth/permission error.
- A handover note documents commands run, results, residual risks, and rollback path.

## Current Validated Starting State

- Active config file: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- Current top-level plugin array does not include `opencode-scheduler`.
- `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler` was not present during validation.
- Scheduler scope file for hourly email auto-sort exists at `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json`.
- Email auto-sort script already uses no-WAM/app-only Graph auth via `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1`.
- Windows scheduled task `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort` exists and is `Ready`, but recent validation showed blank `LastRunTime` and `NextRunTime`.

## Primary Files and Artifacts

- Active OpenCode config to modify: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- Config backup target pattern: `C:\Users\DaveWitkin\.config\opencode\backups\opencode.jsonc.pre-scheduler-restore-YYYYMMDD-HHMMSS.bak`
- Scheduler scope root: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\`
- Email auto-sort job scope file: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json`
- Email auto-sort script to validate only: `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
- No-WAM Graph auth wrapper to validate only: `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1`
- Track plan: `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/plan.md`
- Track metadata: `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/metadata.json`
- Handover note to create during execution: `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/handover.md`

## Expected Implementation Strategy

1. Snapshot the current config and scheduler/task state.
2. Add `opencode-scheduler` to the top-level plugin array in `opencode.jsonc` without disturbing existing plugins.
3. Validate JSONC syntax and plugin entry uniqueness.
4. Restart or invoke OpenCode once so plugin installation/loading can occur.
5. Confirm plugin cache/install state and scheduler scope visibility.
6. Validate Windows scheduled task registrations and the hourly email auto-sort dry-run.
7. Document results and any follow-up work.

## Rollback Strategy

- Restore the timestamped backup of `opencode.jsonc` created in Phase 0:

```powershell
Copy-Item "C:\Users\DaveWitkin\.config\opencode\backups\opencode.jsonc.pre-scheduler-restore-YYYYMMDD-HHMMSS.bak" "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Force
```

- Do not delete scheduler scope files during rollback.
- If plugin installation creates `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler` but rollback is required, leave the cache in place unless plugin load itself is causing repeat startup failure. If cache removal is required, remove only the scheduler package path:

```powershell
Remove-Item "C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler" -Recurse -Force
```
