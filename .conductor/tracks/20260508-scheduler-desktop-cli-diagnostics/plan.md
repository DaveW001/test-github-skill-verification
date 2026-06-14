# Plan: Diagnose OpenCode Scheduler Desktop/CLI State Divergence

## Brief Restatement

**Goal/outcome:** Reconcile the conflict between OpenCode Desktop showing `opencode-scheduler` as installed/working and CLI/file inspection showing the scheduler missing from the expected global config/cache path.

**Constraints/non-goals:** This is read-only diagnostics. Do not modify OpenCode config, install/remove plugins, edit scheduler job files, change Windows scheduled tasks, edit email-triage code, or execute the existing remediation track.

**Definition of done:** Produce `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/diagnostic-report.md` and `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/handover.md` with evidence-backed guidance on whether to execute, revise, or abandon the existing restore track.

---

## Phase 0: Setup & Preconditions

Objective: Establish a read-only diagnostic workspace and confirm required paths before collecting evidence.

- [x] 0.1 Verify the diagnostic track directory exists.
  - Path: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics`
  - Command:
    ```powershell
    Test-Path "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics"
    ```
  - Expected validation: output is `True`.
  - Error recovery: if `False`, create it with `New-Item -ItemType Directory -Path "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics" -Force`.

- [x] 0.2 Create the diagnostics artifacts directory.
  - Path: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts`
  - Command:
    ```powershell
    New-Item -ItemType Directory -Path "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts" -Force | Out-Null
    ```
  - Expected validation: directory exists and command exits successfully.
  - Error recovery: if access is denied, stop and report the permission failure.

- [x] 0.3 Verify the global OpenCode config path.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"
    ```
  - Expected validation: output is `True`.
  - Error recovery: if `False`, record `global config missing` in the diagnostic report and continue alternate config discovery.

- [x] 0.4 Verify the hourly scheduler scope file path.
  - File: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json`
  - Command:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json"
    ```
  - Expected validation: output is `True`.
  - Error recovery: if `False`, record missing scheduler job definition; do not recreate it.

- [x] 0.5 Verify the existing remediation track path without executing it.
  - Path: `C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin`
  - Command:
    ```powershell
    Test-Path "C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin"
    ```
  - Expected validation: output is `True`.
  - Error recovery: if `False`, record that no restore track is available and continue diagnostics.

**Phase 0 exit criteria:** Primary paths have been checked, artifact directory exists, and no remediation has been performed.

---

## Phase 1: Implementation — Capture Global Config and Standard Cache Evidence

Objective: Establish what the expected CLI/global file-system view says about `opencode-scheduler`.

- [x] 1.1 Capture the global config plugin block.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    Get-Content "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -TotalCount 20 | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\global-config-plugin-block.txt" -Encoding utf8
    ```
  - Expected validation: artifact exists and contains the top-level `plugin` array.
  - Error recovery: if source file is missing, write `GLOBAL CONFIG MISSING` to the artifact file.

- [x] 1.2 Count scheduler references in the global config.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    $count = 0; if (Test-Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc") { $count = ((Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern 'opencode-scheduler' -AllMatches).Matches | Measure-Object).Count }; "global opencode.jsonc scheduler references: $count" | Tee-Object "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\global-config-scheduler-count.txt"
    ```
  - Expected validation: artifact records a numeric count.
  - Error recovery: if `Select-String` fails, record the exception text in the artifact.

- [x] 1.3 Check the standard OpenCode plugin cache for scheduler.
  - Path: `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler`
  - Command:
    ```powershell
    $exists = Test-Path "C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler"; "standard cache opencode-scheduler exists: $exists" | Tee-Object "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\standard-cache-scheduler-exists.txt"
    ```
  - Expected validation: artifact says `True` or `False`.
  - Error recovery: if cache parent is missing, record `standard cache parent missing` and continue.

- [x] 1.4 Capture scheduler package metadata from standard cache if present.
  - File: `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler\package.json`
  - Command:
    ```powershell
    if (Test-Path "C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler\package.json") { Get-Content "C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler\package.json" -Raw | ConvertFrom-Json | Select-Object name, version | Format-List | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\standard-cache-scheduler-package.txt" -Encoding utf8 } else { "standard cache package.json missing" | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\standard-cache-scheduler-package.txt" -Encoding utf8 }
    ```
  - Expected validation: artifact contains package name/version or the missing-file message.
  - Error recovery: if JSON parsing fails, copy the raw package file content into the artifact and record `parse failed`.

**Phase 1 exit criteria:** Artifacts prove whether scheduler is present in the expected global config and standard plugin cache.

---

## Phase 2: Implementation — Discover Desktop/Alternate Config and Cache Sources

Objective: Identify where OpenCode Desktop may be finding `opencode-scheduler` if not from the expected global config/cache.

- [x] 2.1 Search known OpenCode config files for scheduler references.
  - Directory: `C:\Users\DaveWitkin\.config\opencode`
  - Command:
    ```powershell
    $result = Select-String -Path "C:\Users\DaveWitkin\.config\opencode\*.json*" -Pattern 'opencode-scheduler' -ErrorAction SilentlyContinue | Select-Object Path, LineNumber, Line | Format-List; if (-not $result) { "No scheduler references found in config directory" }; $result | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\config-dir-scheduler-references.txt" -Encoding utf8
    ```
  - Expected validation: artifact exists; it may show only backup-file references or a "No scheduler references found" message.
  - Error recovery: if locked files cause errors, the `-ErrorAction SilentlyContinue` will suppress them; the artifact will still be created. If the glob matches no files, the artifact will contain the "No scheduler references found" message.

- [x] 2.2 List likely OpenCode Desktop user-data directories.
  - Directories: `C:\Users\DaveWitkin\AppData\Roaming`, `C:\Users\DaveWitkin\AppData\Local`
  - Command:
    ```powershell
    pwsh -ExecutionPolicy Bypass -NoProfile -Command "Get-ChildItem 'C:\Users\DaveWitkin\AppData\Roaming','C:\Users\DaveWitkin\AppData\Local' -Directory -ErrorAction SilentlyContinue | Where-Object { `$_.Name -match 'opencode|open-code|OpenCode' } | Select-Object FullName | Format-Table -AutoSize | Out-File 'C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\desktop-candidate-dirs.txt' -Encoding utf8"
    ```
  - Expected validation: artifact exists and lists candidate directories or is empty.
  - Error recovery: if access is denied, record the access-denied path and continue. If the `pwsh` wrapper fails, write the command to `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\list-desktop-dirs.ps1` and run it with `pwsh -ExecutionPolicy Bypass -File`.

- [x] 2.3 Search candidate Desktop directories for scheduler references.
  - Output file: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\desktop-scheduler-references.txt`
  - Command:
    ```powershell
    pwsh -ExecutionPolicy Bypass -NoProfile -Command "$dirs = Get-ChildItem 'C:\Users\DaveWitkin\AppData\Roaming','C:\Users\DaveWitkin\AppData\Local' -Directory -ErrorAction SilentlyContinue | Where-Object { `$_.Name -match 'opencode|open-code|OpenCode' }; foreach (`$d in $dirs) { Get-ChildItem `$d.FullName -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern 'opencode-scheduler' -ErrorAction SilentlyContinue | Select-Object Path, LineNumber, Line } | Format-List | Out-File 'C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\desktop-scheduler-references.txt' -Encoding utf8"
    ```
  - Expected validation: artifact exists and either lists references or is empty.
  - Error recovery: if search exceeds 120 seconds, stop it and rerun only against directories listed in `desktop-candidate-dirs.txt` that include `OpenCode` in the name. If the `pwsh` wrapper fails, write the command to `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\search-desktop-scheduler.ps1` and run it with `pwsh -ExecutionPolicy Bypass -File`.

- [x] 2.4 Search package caches for `opencode-scheduler` directories.
  - Directories: `C:\Users\DaveWitkin\.cache`, `C:\Users\DaveWitkin\AppData\Local`, `C:\Users\DaveWitkin\AppData\Roaming`
  - Command:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.cache","C:\Users\DaveWitkin\AppData\Local","C:\Users\DaveWitkin\AppData\Roaming" -Recurse -Directory -Filter "opencode-scheduler" -ErrorAction SilentlyContinue | Select-Object FullName, LastWriteTime | Format-Table -AutoSize | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\scheduler-package-directories.txt" -Encoding utf8
    ```
  - Expected validation: artifact exists and lists zero or more package directories.
  - Error recovery: if the command is too slow, rerun only under `C:\Users\DaveWitkin\.cache` with this exact command:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.cache" -Recurse -Directory -Filter "opencode-scheduler" -ErrorAction SilentlyContinue | Select-Object FullName, LastWriteTime | Format-Table -AutoSize | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\scheduler-package-directories.txt" -Encoding utf8; "timeout: searched .cache only" | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\scheduler-package-directories.txt" -Encoding utf8 -Append
    ```

- [x] 2.5 Capture OpenCode-related environment variables.
  - Output file: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\opencode-env-vars.txt`
  - Command:
    ```powershell
    pwsh -ExecutionPolicy Bypass -NoProfile -Command "Get-ChildItem Env: | Where-Object { `$_.Name -match 'OPENCODE|OPEN_CODE|XDG|APPDATA|LOCALAPPDATA|BUN' } | Sort-Object Name | Format-Table -AutoSize | Out-File 'C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\opencode-env-vars.txt' -Encoding utf8"
    ```
  - Expected validation: artifact exists and includes `APPDATA` and `LOCALAPPDATA` if available.
  - Error recovery: if no values are found, write `No matching environment variables found` to the artifact. If the `pwsh` wrapper fails, write the command to `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\capture-env-vars.ps1` and run it with `pwsh -ExecutionPolicy Bypass -File`.

**Phase 2 exit criteria:** Artifacts identify whether Desktop has an alternate config/cache source or whether the scheduler source remains unknown.

---

## Phase 3: Implementation — Validate Scheduler Job Definitions

Objective: Confirm scheduler scope files exist and contain the expected hourly email auto-sort definition.

- [x] 3.1 List all scheduler scope JSON files.
  - Directory: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes`
  - Command:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\scheduler\scopes" -Recurse -Filter "*.json" -ErrorAction SilentlyContinue | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\scheduler-scope-json-files.txt" -Encoding utf8
    ```
  - Expected validation: artifact includes `email-triage-hourly-email-auto-sort.json`.
  - Error recovery: if directory is missing, record `scheduler scopes directory missing` and skip tasks 3.2-3.3.

- [x] 3.2 Parse the hourly email auto-sort job JSON.
  - File: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json`
  - Command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json"; $out = "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-job-summary.txt"; if (Test-Path $path) { try { $job = Get-Content $path -Raw | ConvertFrom-Json; $job | Select-Object scopeId, slug, name, schedule, source, workdir | Format-List | Out-File $out -Encoding utf8; $job.run.command | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-job-command.txt" -Encoding utf8 } catch { "JSON parse error: $($_.Exception.Message)" | Out-File $out -Encoding utf8 } } else { "hourly job json missing" | Out-File $out -Encoding utf8 }
    ```
  - Expected validation: summary shows schedule `0 */1 * * *`; command references `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`.
  - Error recovery: if parsing fails, the try/catch will write the exact parser error into `hourly-job-summary.txt`.

- [x] 3.3 Validate the hourly email auto-sort target script exists.
  - File: `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
  - Command:
    ```powershell
    "hourly script exists: $(Test-Path 'C:\development\email-triage\scripts\hourly-email-auto-sort.ps1')" | Tee-Object "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-script-exists.txt"
    ```
  - Expected validation: artifact says `hourly script exists: True`.
  - Error recovery: if `False`, record that the scheduler job points to a missing script.

**Phase 3 exit criteria:** Scheduler scope inventory and hourly job definition evidence are captured.

---

## Phase 4: Implementation — Validate Windows Scheduled Task Runtime Evidence

Objective: Determine whether the hourly task is registered cleanly and whether it has recent successful or failed executions.

- [x] 4.1 Capture the hourly task registration state.
  - Task name: `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
  - Command:
    ```powershell
    Get-ScheduledTask -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" -ErrorAction SilentlyContinue | Select-Object TaskPath, TaskName, State | Format-List | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-task-registration.txt" -Encoding utf8
    ```
  - Expected validation: artifact includes task name and state, usually `Ready`.
  - Error recovery: if artifact is empty, write `hourly scheduled task not found` to the artifact.

- [x] 4.2 Capture hourly task info and preserve inconsistencies.
  - Task name: `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
  - Command:
    ```powershell
    try { Get-ScheduledTaskInfo -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" -ErrorAction Stop | Select-Object LastRunTime, LastTaskResult, NextRunTime, NumberOfMissedRuns | Format-List | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-task-info.txt" -Encoding utf8 } catch { "Get-ScheduledTaskInfo failed: $($_.Exception.Message)" | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-task-info.txt" -Encoding utf8 }
    ```
  - Expected validation: artifact contains timing metadata or the exact failure message.
  - Error recovery: no remediation; preserve the failure as diagnostic evidence.

- [x] 4.3 Export hourly scheduled task XML if registration exists.
  - Output file: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-task.xml`
  - Command:
    ```powershell
    if (Get-ScheduledTask -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" -ErrorAction SilentlyContinue) { Export-ScheduledTask -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-task.xml" -Encoding utf8 } else { "hourly task not found; XML not exported" | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-task.xml" -Encoding utf8 }
    ```
  - Expected validation: artifact exists and contains `<Task` if the task exists.
  - Error recovery: if export fails, write the exception message into `hourly-task.xml`.

- [x] 4.4 Capture all `opencode-job-*` task registration states.
  - Output file: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\all-opencode-tasks.txt`
  - Command:
    ```powershell
    pwsh -ExecutionPolicy Bypass -NoProfile -Command "Get-ScheduledTask | Where-Object { `$_.TaskName -like 'opencode-job-*' } | Sort-Object TaskName | Select-Object TaskName, State | Format-Table -AutoSize | Out-File 'C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\all-opencode-tasks.txt' -Encoding utf8"
    ```
  - Expected validation: artifact lists zero or more tasks; if scheduler jobs exist, it should include hourly email auto-sort.
  - Error recovery: if shell quoting strips `$_`, write the command to `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\list-opencode-tasks.ps1` and run it with `pwsh -ExecutionPolicy Bypass -File`.

- [x] 4.5 Capture recent Task Scheduler operational events for the hourly task.
  - Event log: `Microsoft-Windows-TaskScheduler/Operational`
  - Command:
    ```powershell
    pwsh -ExecutionPolicy Bypass -NoProfile -Command "$task = 'opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort'; Get-WinEvent -LogName 'Microsoft-Windows-TaskScheduler/Operational' -MaxEvents 300 -ErrorAction SilentlyContinue | Where-Object { `$_.Message -like \"*$task*\" } | Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-List | Out-File 'C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\hourly-task-events.txt' -Encoding utf8"
    ```
  - Expected validation: artifact exists; it may be empty if logging is disabled or no events exist.
  - Error recovery: if access is denied or log is disabled, record the exact message in the artifact. If the `pwsh` wrapper fails, write the command to `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\capture-task-events.ps1` and run it with `pwsh -ExecutionPolicy Bypass -File`.

- [x] 4.6 Capture recent email auto-sort logs without running the script.
  - Directory: `C:\development\email-triage\logs`
  - Command:
    ```powershell
    if (Test-Path "C:\development\email-triage\logs") { Get-ChildItem "C:\development\email-triage\logs" -Filter "*.log" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5 FullName, LastWriteTime, Length | Format-Table -AutoSize | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\recent-email-triage-logs.txt" -Encoding utf8 } else { "email-triage logs directory missing" | Out-File "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\recent-email-triage-logs.txt" -Encoding utf8 }
    ```
  - Expected validation: artifact lists recent log files or states that no logs directory exists.
  - Error recovery: do not create the logs directory during diagnostics.

**Phase 4 exit criteria:** Task registration, task info, task XML, event history, and email-triage log evidence are captured.

---

## Phase 5: Implementation — Synthesize Decision Report

Objective: Convert evidence into a clear decision about whether to execute, revise, or avoid the existing restore track.

- [x] 5.1 Create the diagnostic report file.
  - File to create: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\diagnostic-report.md`
  - Required template:
    ```markdown
    # Diagnostic Report: OpenCode Scheduler Desktop/CLI Divergence

    ## Executive Decision
    Decision: <Execute restore track as written | Revise restore track | Do not execute plugin remediation | More research required>

    ## Evidence Summary
    - Desktop UI evidence: User screenshot shows `opencode-scheduler` listed as loaded.
    - Global config evidence: <count and artifact reference>
    - Standard cache evidence: <exists True/False and artifact reference>
    - Alternate config/cache evidence: <summary and artifact reference>
    - Scheduler scope evidence: <summary and artifact reference>
    - Windows task evidence: <summary and artifact reference>
    - Recent runtime evidence: <summary and artifact reference>

    ## Reconciliation
    <Explain why Desktop and CLI evidence agree or conflict.>

    ## Recommendation
    <Concrete next action.>
    ```
  - Expected validation: file exists and includes `## Executive Decision`.
  - Error recovery: if evidence is incomplete, set `Decision: More research required` and list missing artifacts.

- [x] 5.2 Apply diagnostic decision rules in the report.
  - File to update: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\diagnostic-report.md`
  - Decision rules:
    ```text
    A. Scheduler absent from all persisted locations but visible in Desktop -> find Desktop effective config/cache before remediation.
    B. Scheduler present in Desktop-specific config/cache but absent from global config -> revise restore track for config-source reconciliation.
    C. Scheduler present in effective config/cache -> do not execute plugin remediation; focus on task/runtime issue.
    D. Scheduler healthy but hourly job lacks recent success -> create or execute a task-runtime diagnostic/fix track.
    ```
  - Expected validation: report contains one selected rule and explains rejected alternatives.
  - Error recovery: if multiple rules appear true, select `Revise restore track` and document ambiguity.

**Phase 5 exit criteria:** The diagnostic report gives a clear evidence-backed recommendation.

---

## Final Phase: Validation & Handover

Objective: Verify artifacts are complete and prepare handoff for the next agent or user decision.

- [x] 6.1 Verify required diagnostic artifacts exist.
  - Directory: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts`
  - Command:
    ```powershell
    $required = 'global-config-plugin-block.txt','global-config-scheduler-count.txt','standard-cache-scheduler-exists.txt','standard-cache-scheduler-package.txt','config-dir-scheduler-references.txt','desktop-candidate-dirs.txt','desktop-scheduler-references.txt','scheduler-package-directories.txt','opencode-env-vars.txt','scheduler-scope-json-files.txt','hourly-job-summary.txt','hourly-job-command.txt','hourly-script-exists.txt','hourly-task-registration.txt','hourly-task-info.txt','hourly-task.xml','all-opencode-tasks.txt','hourly-task-events.txt','recent-email-triage-logs.txt'; foreach ($r in $required) { $p = "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\$r"; [PSCustomObject]@{Artifact=$r; Exists=(Test-Path $p)} } | Format-Table -AutoSize | Tee-Object "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\artifacts\artifact-completeness.txt"
    ```
  - Expected validation: `artifact-completeness.txt` exists and all rows show `Exists True` unless a phase was intentionally skipped with explanation.
  - Error recovery: rerun missing artifact tasks before final handover.

- [x] 6.2 Verify the diagnostic report has a decision.
  - File: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\diagnostic-report.md`
  - Command:
    ```powershell
    Select-String -Path "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\diagnostic-report.md" -Pattern '^Decision:'
    ```
  - Expected validation: output contains one `Decision:` line.
  - Error recovery: if no decision line exists, update the report before handover.

- [x] 6.3 Create the handover note.
  - File to create: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\handover.md`
  - Required template:
    ```markdown
    # Handover: Scheduler Desktop/CLI Diagnostics

    ## Summary
    - Decision: <decision from diagnostic-report.md>
    - Primary finding: <one sentence>

    ## Artifacts
    - Diagnostic report: `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/diagnostic-report.md`
    - Artifact directory: `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/artifacts/`

    ## Recommended Next Action
    <execute existing restore track | revise restore track | create runtime-fix track | no action>

    ## Blockers or Ambiguities
    - <item or None>
    ```
  - Expected validation: file exists and references `diagnostic-report.md`.
  - Error recovery: if report is incomplete, write `Handover blocked: diagnostic report incomplete` and list missing sections.

- [x] 6.4 Update diagnostic track metadata to completed or blocked.
  - File to modify: `C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\metadata.json`
  - Command to update status:
    ```powershell
    $meta = Get-Content "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\metadata.json" -Raw | ConvertFrom-Json; $meta.status = "completed"; $meta.phase = "done"; $meta | ConvertTo-Json -Depth 5 | Set-Content "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\metadata.json" -Encoding utf8
    ```
  - Command for validation after update:
    ```powershell
    Get-Content "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics\metadata.json" -Raw | ConvertFrom-Json | Select-Object id,status,phase
    ```
  - Expected validation: JSON parses and status is `completed` or `blocked`.
  - Error recovery: if JSON parsing fails, restore valid JSON before ending the session.

**Final phase exit criteria:** Required artifacts exist, diagnostic report has a decision, handover exists, and metadata reflects completed or blocked status.

---

## Execution Readiness Checklist

- [x] Atomic tasks — each checkbox contains one clear diagnostic action.
- [x] Exact file paths — all files, directories, and task names are specified precisely.
- [x] Explicit commands — every task includes verbatim PowerShell commands.
- [x] Clear ordering — evidence is gathered before synthesis and handover.
- [x] Verification per step — every task includes expected output or artifact checks.
- [x] No assumed context — the Desktop/CLI conflict and all relevant paths are restated.
- [x] Concrete examples — report and handover templates are included inline.
- [x] Error recovery — each task includes fallback or stop instructions; tasks using `$_` are wrapped in `pwsh -ExecutionPolicy Bypass -NoProfile -Command` with `.ps1` file fallbacks.

## Top 3 Implementation Risks + Mitigations

1. **Risk:** Desktop's effective config/cache path is not discoverable from normal user directories.
   - **Mitigation:** Preserve negative evidence, capture environment variables, and recommend targeted Desktop runtime inspection rather than guessing.

2. **Risk:** PowerShell quoting strips `$_` in inline commands.
   - **Mitigation:** Use the documented fallback of writing affected commands to a `.ps1` file under `C:\Users\DaveWitkin\AppData\Local\Temp\opencode` and executing with `pwsh -ExecutionPolicy Bypass -File`.

3. **Risk:** Diagnostics are mistaken for remediation.
   - **Mitigation:** The constraints explicitly prohibit modification, and every task writes evidence artifacts only.

## First Task the Build Agent Should Execute Immediately

Start with **Task 0.1**:

```powershell
Test-Path "C:\development\opencode\.conductor\tracks\20260508-scheduler-desktop-cli-diagnostics"
```

Expected output: `True`.
