# Plan: Scheduler Headless Hardening

This plan is written for execution by an agent with no assumed project context. Execute tasks in order. Do not skip backup or verification steps. Do not force-run tasks with side effects unless the task explicitly permits it or the user approves it.

## Phase 1 - Track Setup and Inventory

- [x] Create task inventory JSON at `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\task-inventory.json` by running:

  ```powershell
  Get-ScheduledTask -TaskPath "\OpenCode\" |
    Sort-Object TaskName |
    ForEach-Object {
      $a = $_.Actions[0]
      [PSCustomObject]@{
        TaskName = $_.TaskName
        State = $_.State
        Hidden = $_.Settings.Hidden
        LogonType = $_.Principal.LogonType
        RunAs = $_.Principal.UserId
        Execute = $a.Execute
        Arguments = $a.Arguments
        WorkingDirectory = $a.WorkingDirectory
      }
    } | ConvertTo-Json -Depth 4 |
    Set-Content -Path "C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\task-inventory.json" -Encoding UTF8
  ```

  Verify:
  ```powershell
  Test-Path "C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\task-inventory.json"
  ```
  Expected: `True`.

- [x] Create task inventory Markdown at `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\task-inventory.md` with a table containing these exact columns:

  ```md
  | TaskName | State | Hidden | LogonType | Execute | Arguments | Classification | Rationale |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  ```

  Use the JSON file from the previous task as the data source. Verify: `task-inventory.md` lists all 10 `\OpenCode\` tasks.

- [x] Classify every row in `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\task-inventory.md` using these exact rules:

  - `Already migrated`: `Execute` equals `wscript.exe`.
  - `Migrate to wscript`: `Execute` equals `powershell.exe` AND `Arguments` contains at least one of:
    - `opencode-run-safe.ps1`
    - `opencode run`
    - `--command`
  - `Keep as-is`: task is already `Hidden=True` and runs a direct non-OpenCode script such as:
    - `Update-OsgrepIndex.ps1`
    - `Sync-SchedulerRegistry.ps1`
    - `hourly-email-auto-sort.ps1`
    - `monitor-proxy.ps1`
    - `start-proxy-quiet.ps1`

  Verify: every row has non-empty `Classification` and `Rationale` values. If any task does not match these rules, stop and ask the user before modifying it.

## Phase 2 - Backup and Apply Task Action Hardening

- [x] Create backup directory `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\backups` by running:

  ```powershell
  New-Item -ItemType Directory -Path "C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\backups" -Force | Out-Null
  ```

  Verify:
  ```powershell
  Test-Path "C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\backups"
  ```
  Expected: `True`.

- [x] Export rollback XML for each task classified `Migrate to wscript` by running:

  ```powershell
  $BackupDir = "C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\backups"

  Get-ScheduledTask -TaskPath "\OpenCode\" |
    Where-Object {
      $_.Actions[0].Execute -eq "powershell.exe" -and
      $_.Actions[0].Arguments -match "opencode-run-safe\.ps1|opencode run|--command"
    } |
    ForEach-Object {
      Export-ScheduledTask -TaskPath "\OpenCode\" -TaskName $_.TaskName |
        Set-Content -Path (Join-Path $BackupDir "$($_.TaskName).xml") -Encoding Unicode
    }
  ```

  Verify: one `.xml` backup exists in `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\backups` for each task classified `Migrate to wscript`. If the count does not match, stop and record the mismatch in the execution log.

- [x] For each task classified `Migrate to wscript`, record its current action before changing it by appending a row to `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\execution-log-2026-05-01.md` using this table format:

  ```md
  | TaskName | Before Execute | Before Arguments | After Execute | After Arguments | Result | Notes |
  | --- | --- | --- | --- | --- | --- | --- |
  ```

  Verify: the execution log contains one `Before` row for every task classified `Migrate to wscript`.

- [x] Update each `Migrate to wscript` task action to the headless launcher pattern:

  - Execute: `wscript.exe`
  - Arguments pattern:

    ```text
    //B "C:\development\_shared-scripts\launch-hidden.vbs" "powershell.exe" "-NoProfile" "-ExecutionPolicy" "Bypass" "-WindowStyle" "Hidden" "-File" "<ORIGINAL_SCRIPT_PATH>" <REMAINING_ORIGINAL_ARGUMENTS>
    ```

  Preserve the original PowerShell script path and all original arguments after `-File`. Use `Set-ScheduledTask` where possible.

  If `Set-ScheduledTask` fails with `The parameter is incorrect` or HRESULT `0x80070057`, use this fallback:
  1. Export the task XML.
  2. Edit `<Command>` to `wscript.exe`.
  3. Edit `<Arguments>` to the headless launcher arguments.
  4. Re-register with `schtasks /Create /TN "\OpenCode\<TASK_NAME>" /XML <XML_PATH> /F`.

  Verify after each task:
  ```powershell
  (Get-ScheduledTask -TaskPath "\OpenCode\" -TaskName "<TASK_NAME>").Actions |
    Format-List Execute,Arguments
  ```
  Expected: `Execute` is `wscript.exe`.

- [x] After each task action update, verify `Hidden=True` is still preserved:

  ```powershell
  Get-ScheduledTask -TaskPath "\OpenCode\" -TaskName "<TASK_NAME>" |
    Select-Object TaskName,@{Name="Hidden";Expression={$_.Settings.Hidden}}
  ```

  Expected: `Hidden` equals `True`. If `Hidden` is `False`, set it back to `True` using:

  ```powershell
  $task = Get-ScheduledTask -TaskPath "\OpenCode\" -TaskName "<TASK_NAME>"
  $task.Settings.Hidden = $true
  Set-ScheduledTask -InputObject $task
  ```

- [x] Append the final before/after action table to `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\execution-log-2026-05-01.md` with one completed row for every migrated task:

  ```md
  | TaskName | Before Execute | Before Arguments | After Execute | After Arguments | Result | Notes |
  | --- | --- | --- | --- | --- | --- | --- |
  ```

  Verify: every task classified `Migrate to wscript` has a completed row with `Result` equal to `Migrated` or an issue note explaining why it was not migrated.

## Phase 3 - Registry and Validation

- [x] Regenerate scheduler registry by running:

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File "C:\development\_shared-scripts\Sync-SchedulerRegistry.ps1"
  ```

  Verify:
  - `C:\development\_shared-scripts\scheduler-registry.md` exists.
  - It contains the `Hidden` column.
  - All OpenCode task rows show `Hidden` as `True`.

- [x] Verify all OpenCode task actions after migration by running:

  ```powershell
  Get-ScheduledTask -TaskPath "\OpenCode\" |
    Sort-Object TaskName |
    ForEach-Object {
      $a = $_.Actions[0]
      [PSCustomObject]@{
        TaskName = $_.TaskName
        Hidden = $_.Settings.Hidden
        Execute = $a.Execute
        Arguments = $a.Arguments
      }
    } | Format-Table -AutoSize
  ```

  Expected:
  - All rows have `Hidden=True`.
  - Rows classified `Already migrated` or `Migrate to wscript` have `Execute=wscript.exe`.
  - Rows classified `Keep as-is` retain their original action.

- [x] Force-run only these safe representative tasks unless the user approves more:

  - `opencode-job-development-88876ee600f5-knowledge-base-ingest`
  - `opencode-job-development-88876ee600f5-skill-health-validator`

  Run each with:

  ```powershell
  Start-ScheduledTask -TaskPath "\OpenCode\" -TaskName "<TASK_NAME>"
  Start-Sleep -Seconds 30
  schtasks /query /FO LIST /V /TN "\OpenCode\<TASK_NAME>" |
    Select-String -Pattern "Status|Last Run Time|Last Result"
  ```

  Expected:
  - `Status: Ready` or the task returns to Ready after completion.
  - `Last Result: 0`, unless the task has a known non-zero operational code documented in the execution log.

  Do not force-run disabled tasks, monthly report tasks, Slack/reporting tasks, or email-moving tasks without user approval.

- [x] Ask the user to watch the screen, then force-run `knowledge-base-ingest` for visible-popup validation:

  ```powershell
  Start-ScheduledTask -TaskPath "\OpenCode\" -TaskName "opencode-job-development-88876ee600f5-knowledge-base-ingest"
  ```

  Ask exactly: `Did any console or terminal window visibly pop up?`

  Record the answer in `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\execution-log-2026-05-01.md`.

  Pass condition: user says no visible window appeared.

## Phase 4 - Documentation and Skill Hardening

- [x] Create `C:\development\_shared-scripts\docs\scheduler-headless-runbook.md` with these exact sections:

  1. `# Scheduler Headless Runbook`
  2. `## Problem`
     - Explain why `-WindowStyle Hidden` is insufficient.
     - Explain why `Settings.Hidden=True` is necessary but insufficient for child console processes.
  3. `## Required Pattern`
     - Show exact `wscript.exe` action pattern.
  4. `## Task Creation Checklist`
     - `Hidden=True`
     - `wscript.exe //B launch-hidden.vbs`
     - rollback XML exported
     - force-run validation
  5. `## Migration Procedure`
     - backup command
     - update action command
     - verify command
  6. `## Error Recovery`
     - If `Set-ScheduledTask` fails with `0x80070057`, use XML export/edit/re-register.
     - If task fails after migration, restore from XML backup.
  7. `## Known Good Example`
     - Include `knowledge-base-ingest` before/after action.

  Verify: the file exists and contains all seven headings.

- [x] Update `C:\Users\DaveWitkin\.config\opencode\skill\windows-task-scheduler\SKILL.md` by adding this new section after `## Core Workflow: Create a New Task`:

  ```md
  ## Headless-by-Default Policy for Windows Tasks

  When creating or modifying scheduled tasks that run console-capable tools, PowerShell scripts, CLI apps, or `opencode run`, default to the headless-safe launcher pattern:

  - Set task `Settings.Hidden = True`.
  - Use `wscript.exe` as the task action executable.
  - Use `C:\development\_shared-scripts\launch-hidden.vbs` with `//B` to launch PowerShell or the target script hidden.
  - Do not rely on `powershell.exe -WindowStyle Hidden` alone for tasks that may spawn child console processes.
  - Before modifying an existing task, export rollback XML.
  - After creation/modification, force-run the task and ask the user whether any visible window appeared.

  Standard action pattern:

  Execute:
  `wscript.exe`

  Arguments:
  `//B "C:\development\_shared-scripts\launch-hidden.vbs" "powershell.exe" "-NoProfile" "-ExecutionPolicy" "Bypass" "-WindowStyle" "Hidden" "-File" "<SCRIPT_PATH>"`
  ```

  Verify:
  ```powershell
  Select-String -Path "C:\Users\DaveWitkin\.config\opencode\skill\windows-task-scheduler\SKILL.md" -Pattern "Headless-by-Default Policy"
  ```
  Expected: one match.

## Phase 5 - Conductor Finalization

- [x] Write `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\execution-log-2026-05-01.md` with these sections:

  - `## Summary`
  - `## Inventory Results`
  - `## Tasks Migrated`
  - `## Tasks Kept As-Is`
  - `## Validation Results`
  - `## Issues and Recoveries`
  - `## Files Modified`

  Verify: the file exists and each heading is present.

- [x] Update `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\metadata.json`:

  - Set `progress.completedTasks` to the number of completed plan checkboxes.
  - Set `progress.percentage` to the rounded percentage.
  - Keep `status` as `active` until all validation and documentation tasks are complete.
  - Add completed deliverables to `keyOutcomes`.

  Verify JSON parses successfully:
  ```powershell
  Get-Content "C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\metadata.json" -Raw | ConvertFrom-Json
  ```

- [x] Mark the track complete only after all plan checkboxes are `[x]`. Then update `C:\development\opencode\.conductor\tracks\20260501-scheduler-headless-hardening\metadata.json`:

  - `status`: `completed`
  - `completed`: `2026-05-01`
  - `progress.completedTasks`: total task count
  - `progress.percentage`: `100`

  Move the track entry in `C:\development\opencode\.conductor\tracks-ledger.md` from `## Active Tracks` to `## Completed Tracks`.

  Verify:
  - `metadata.json` says `"status": "completed"`.
  - `tracks-ledger.md` contains this track under `## Completed Tracks`.
