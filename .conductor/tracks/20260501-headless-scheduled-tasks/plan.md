# Plan: Headless Scheduled Tasks Fix

## Phase 1 - Create Remediation Script
- [x] Write `C:\development\_shared-scripts\Set-TaskHidden.ps1` - PowerShell script with:
  - Enumerates 7 target OpenCode scheduled tasks under `\OpenCode\`
  - For each task with `Settings.Hidden = False`, sets it to `True`
  - Logs each change to console
  - Uses `gsudo` elevation prompt since modifying scheduled tasks requires admin rights
  - Handles errors gracefully (skip disabled tasks, report failures)
- [x] Include a `-WhatIf` mode for safe preview before applying

## Phase 2 - Fix hourly-email-auto-sort Action
- [x] ~~Create `C:\development\_shared-scripts\email-auto-sort-quiet.ps1` wrapper~~ NOT NEEDED - task already had Hidden=True and PS wrapper
- [x] ~~Update the scheduled task action~~ NOT NEEDED - already correctly configured
- [x] Verified: task already uses `powershell.exe -WindowStyle Hidden -File hourly-email-auto-sort.ps1` with Hidden=True

## Phase 3 - Apply Hidden Flag to All Tasks
- [x] Run `Set-TaskHidden.ps1 -WhatIf` to preview changes - confirmed 7 tasks would change
- [x] Run `Set-TaskHidden.ps1` with gsudo to apply changes
  - 6/7 applied via `Set-ScheduledTask` directly
  - 1/7 (`skill-sync-monitor`) required XML export/modify/re-register due to Vista compatibility mode
- [x] Verify all 10 tasks now have `Settings.Hidden = True` - CONFIRMED

## Phase 4 - Update Registry & Documentation
- [x] Updated `Sync-SchedulerRegistry.ps1` to include Hidden column (new field + enrichment via Get-ScheduledTask)
- [x] Run `Sync-SchedulerRegistry.ps1` to regenerate `scheduler-registry.md` with Hidden status
- [x] Verify `scheduler-registry.md` shows all tasks as Hidden=True - CONFIRMED

## Phase 5 - Validate
- [x] Force-run `knowledge-base-ingest` via `Start-ScheduledTask`
- [x] Confirm no visible console window appeared (user-observed on rerun)
- [x] Check task history for successful completion - Result: 0 (success)
- [x] Mark track complete

## Implementation Notes

### PowerShell approach for setting Hidden
```powershell
$task = Get-ScheduledTask -TaskPath "\OpenCode\" -TaskName $taskName
$task.Settings.Hidden = $true
Set-ScheduledTask -InputObject $task
```

This requires admin elevation. Use `gsudo` prefix for the interactive approval flow.

### Why not change LogonType?
- Interactive + Hidden=True should fully suppress the window
- S4U requires storing the user's password in Task Scheduler
- S4U runs in a different security context (no access to user's encrypted store, mapped drives, etc.)
- This is a safe, minimal change with low blast radius

### Issue: skill-sync-monitor Set-ScheduledTask failure
The `skill-sync-monitor` task had `Compatibility: Vista` which caused `Set-ScheduledTask` to fail with "The parameter is incorrect." Fixed by exporting the task XML, adding `<Hidden>true</Hidden>`, and re-registering via `schtasks /Create /XML`.
