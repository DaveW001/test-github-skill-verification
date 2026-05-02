# Spec: Headless Scheduled Tasks Fix

## Goal

Eliminate visible console windows from all OpenCode scheduled tasks by setting Windows Task Scheduler task-level `Settings.Hidden = True` on every interactive task that currently has it set to `False`.

## Background

The previous track (`opencode-headless-scheduled-jobs` in the 02-Kx-to-process repo, completed 2026-04-29) added PowerShell `-WindowStyle Hidden` wrappers to all job action arguments. However, Windows Task Scheduler has **two layers** of window control:

1. **Action-level**: `powershell.exe -WindowStyle Hidden` (already applied)
2. **Task-level**: `Settings.Hidden` property on the task registration (NOT applied for 8 of 10 tasks)

The action-level flag tells PowerShell to hide its own window, but Task Scheduler itself can still create a visible console allocation before PowerShell starts. Setting `Settings.Hidden = True` at the task level prevents Task Scheduler from creating a visible window at all.

## Requirements

- [ ] Set `Settings.Hidden = True` on all 8 interactive tasks that currently have `Hidden = False`
- [ ] Verify no visible windows appear after the fix
- [ ] Update `Sync-SchedulerRegistry.ps1` (or create a new script) to report the Hidden flag status
- [ ] Update `scheduler-registry.md` to reflect the new Hidden status
- [ ] Wrap `hourly-email-auto-sort` in a PowerShell `-WindowStyle Hidden` wrapper like the other jobs (currently uses raw `opencode run`)

## Non-Requirements

- [ ] Changing LogonType from Interactive to S4U (bigger security change, not needed if Hidden=True works)
- [ ] Modifying the actual job scripts or prompts
- [ ] Changes to gemini-proxy-monitor (runs as SYSTEM, already fully hidden)

## Acceptance Criteria

- [ ] All 8 previously-unhidden tasks now have `Settings.Hidden = True`
- [ ] `hourly-email-auto-sort` uses a PowerShell hidden wrapper instead of raw `opencode run`
- [ ] Running `Sync-SchedulerRegistry.ps1` (or updated equivalent) confirms Hidden=True on all tasks
- [ ] `scheduler-registry.md` updated with current status
- [ ] No visible console window appears on the next hourly run of `knowledge-base-ingest`

## Tasks to Modify

| # | Task Name | Current Hidden | Action Needed |
|---|-----------|---------------|---------------|
| 1 | conductor-weekly-report | False | Set Hidden=True |
| 2 | offer-validation-round1-daily-rollup | False (Disabled) | Set Hidden=True |
| 3 | osgrep-auto-indexer | False | Set Hidden=True |
| 4 | scheduler-registry-sync | False | Set Hidden=True |
| 5 | skill-health-validator | False | Set Hidden=True |
| 6 | knowledge-base-ingest | False | Set Hidden=True |
| 7 | skill-sync-monitor | False | Set Hidden=True |
| 8 | hourly-email-auto-sort | True | Wrap in PS `-WindowStyle Hidden` (action fix) |

Tasks already correctly configured (no changes needed):
- `gemini-proxy-monitor` (Hidden=True, ServiceAccount/SYSTEM)
- `gemini-proxy-starter` (Hidden=True, already set)

## Key Files

- Task definitions: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\development-88876ee600f5\jobs\`
- Job wrappers: `C:\development\_shared-scripts\*-quiet.ps1`, `C:\development\_shared-scripts\opencode-run-safe.ps1`
- Registry sync: `C:\development\_shared-scripts\Sync-SchedulerRegistry.ps1`
- Registry doc: `C:\development\_shared-scripts\scheduler-registry.md`
