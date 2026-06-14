# Diagnose OpenCode Scheduler Desktop/CLI State Divergence

## Goal / Outcome

Determine whether `opencode-scheduler` is truly installed, persisted, and operational across OpenCode Desktop, the CLI/global configuration, plugin cache locations, scheduler scope files, and Windows Task Scheduler registrations. Produce a decision-ready diagnosis that says whether to execute the existing remediation track, revise it, or take no plugin remediation action.

## Constraints / Non-Goals

- Do not modify `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` during this diagnostic track.
- Do not add, remove, reinstall, or update any OpenCode plugin during this diagnostic track.
- Do not delete, recreate, disable, or enable Windows scheduled tasks.
- Do not edit scheduler scope JSON files.
- Do not edit production code in `C:\development\email-triage`.
- Do not execute the remediation track `20260508-restore-opencode-scheduler-plugin` from this diagnostic track.
- Read-only inspection and manual non-mutating validation commands are allowed.

## Definition of Done

- The Desktop-visible plugin list is compared against the on-disk global config and likely alternate config/cache locations.
- The installed/cached location of `opencode-scheduler`, if any, is identified.
- The hourly email auto-sort scheduler scope file is validated as present and parseable.
- The Windows scheduled task state for hourly email auto-sort is captured, including any `Get-ScheduledTaskInfo` inconsistency.
- Recent run evidence for hourly email auto-sort is captured from logs and/or Windows Task Scheduler operational history.
- A final diagnostic report states one of three decisions: execute the restore track, revise/replace the restore track, or skip plugin remediation and focus only on task/runtime validation.

## Current Context

- OpenCode Desktop status screen shows 7 plugins and includes `opencode-scheduler` with a green status indicator.
- CLI/file inspection of `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` showed no `opencode-scheduler` entry in the top-level plugin array.
- CLI inspection of `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler` returned `False`.
- A previous remediation track exists at `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/`, but it should not be executed until this diagnostic track resolves the state divergence.
- The hourly email auto-sort scheduled task exists by name, but earlier diagnostics showed blank `LastRunTime`/`NextRunTime` and a `Get-ScheduledTaskInfo` inconsistency.

## Primary Files and Artifacts

- Global OpenCode config: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- Standard OpenCode plugin cache: `C:\Users\DaveWitkin\.cache\opencode\node_modules\`
- Scheduler scope root: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\`
- Hourly email auto-sort scope file: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json`
- Email triage repo: `C:\development\email-triage`
- Hourly email auto-sort script: `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
- Diagnostic report to create: `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/diagnostic-report.md`
- Handover note to create: `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/handover.md`

## Diagnostic Decision Rules

- If `opencode-scheduler` is absent from all persisted config/cache locations and only appears in Desktop UI, recommend finding Desktop's effective config/cache before remediation.
- If `opencode-scheduler` is present in a Desktop-specific config/cache but absent from CLI/global config, recommend revising the restore track to reconcile config sources rather than blindly adding the plugin.
- If `opencode-scheduler` is present and persisted in the effective config/cache used by Desktop, recommend not executing plugin remediation; focus on task registration/runtime validation.
- If the scheduler plugin is healthy but hourly email auto-sort has no successful recent runs, recommend a separate task/runtime diagnostic track or focused fix.
