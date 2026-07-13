# Plan: Restore OpenCode Scheduler Plugin and Validate Scheduled Jobs

## Brief Restatement

**Goal/outcome:** Restore `opencode-scheduler` to the active OpenCode global plugin array and validate that existing scheduler job definitions, especially hourly email auto-sort, are loadable and operational.

**Constraints/non-goals:** Do not execute destructive task changes, do not redesign scheduled jobs, do not alter production email-triage code unless validation proves it is necessary, do not remove existing plugins, and do not execute broad cache clearing as a first response.

**Definition of done:** The active OpenCode config contains `opencode-scheduler` exactly once, the plugin installs/loads after OpenCode startup, scheduler scope files remain intact, the hourly email auto-sort task is present, manual script validation reaches app-only Graph auth or produces an actionable error, and a handover note records results and rollback steps.

---

## Phase 0: Setup & Preconditions

Objective: Capture the current state and create rollback artifacts before modifying any configuration.

- [x] 0.1 Verify the active OpenCode config file exists.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"
    ```
  - Authoritative acceptance check: command prints `True`.
  - Error recovery: if it prints `False`, stop and inspect `C:\Users\DaveWitkin\.config\opencode\` with:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.config\opencode" -Force
    ```
    Do not create a new config file unless the user explicitly approves.

- [x] 0.2 Create a timestamped backup directory if needed.
  - File/directory: `C:\Users\DaveWitkin\.config\opencode\backups\`
  - Command:
    ```powershell
    New-Item -ItemType Directory -Path "C:\Users\DaveWitkin\.config\opencode\backups" -Force | Out-Null
    ```
  - Authoritative acceptance check: command exits with code `0` and the directory exists.
  - Error recovery: if access is denied, ask the user to run the command with elevation only if the directory permissions require it.

- [x] 0.3 Back up the active OpenCode config.
  - Source file: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Backup file pattern: `C:\Users\DaveWitkin\.config\opencode\backups\opencode.jsonc.pre-scheduler-restore-YYYYMMDD-HHMMSS.bak`
  - Command:
    ```powershell
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"; Copy-Item "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" "C:\Users\DaveWitkin\.config\opencode\backups\opencode.jsonc.pre-scheduler-restore-$stamp.bak" -Force; Write-Output "Backup: C:\Users\DaveWitkin\.config\opencode\backups\opencode.jsonc.pre-scheduler-restore-$stamp.bak"
    ```
  - Authoritative acceptance check: output includes a `Backup:` path and that file exists.
  - Error recovery: if `Copy-Item` fails, stop; do not edit config without a backup.

- [x] 0.4 Snapshot current scheduler scope files.
  - Directory: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\`
  - Command:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\scheduler\scopes" -Recurse -Filter "*.json" | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
    ```
  - Authoritative acceptance check: output includes `email-triage-hourly-email-auto-sort.json`.
  - Error recovery: if the scopes directory is missing, stop and report that scheduler job definitions are absent; do not recreate them from memory.

- [x] 0.5 Snapshot current OpenCode scheduled tasks.
  - System artifact: Windows Task Scheduler tasks named `opencode-job-*`
  - Command:
    ```powershell
    Get-ScheduledTask | Where-Object { $_.TaskName -like "opencode-job-*" } | Select-Object TaskName, State | Format-Table -AutoSize
    ```
  - Authoritative acceptance check: output includes `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`.
  - Error recovery: if PowerShell quoting strips `$_` in the execution shell, write the command to `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\list-opencode-tasks.ps1` and run:
    ```powershell
    pwsh -ExecutionPolicy Bypass -File "C:\Users\DaveWitkin\AppData\Local\Temp\opencode\list-opencode-tasks.ps1"
    ```

- [x] 0.6 Confirm `opencode-scheduler` is currently absent before editing.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern 'opencode-scheduler' -SimpleMatch
    ```
  - Authoritative acceptance check: no matches are printed.
  - Error recovery: if one match is printed, do not add another entry; skip to Phase 2 validation and check why the plugin is not loading.

**Phase 0 exit criteria:** Config file exists, a timestamped backup exists, scheduler scope files were listed, current scheduled tasks were listed, and the initial scheduler plugin absence/presence is known.

---

## Phase 1: Implementation — Restore Plugin Entry

Objective: Add `opencode-scheduler` to the active global OpenCode plugin array exactly once while preserving all existing plugins.

- [x] 1.1 Edit `opencode.jsonc` to add `opencode-scheduler` in the top-level `plugin` array.
  - File to modify: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Required final structure example:
    ```jsonc
    {
      "$schema": "https://opencode.ai/config.json",
      "plugin": [
        "@zenobius/opencode-skillful",
        "oc-codex-multi-auth",
        "opencode-ignore@1.1.0",
        "@tarquinen/opencode-dcp@latest",
        "@ramtinj95/opencode-tokenscope@latest",
        "opencode-scheduler"
      ],
      "permission": {
    ```
  - Authoritative acceptance check: existing plugin order is preserved, current plugins remain intact, and `opencode-scheduler` is appended once. Do not reintroduce removed plugins such as `opencode-snippets@1.8.0` or `opencode-mystatus`; preserve `@ramtinj95/opencode-tokenscope@latest`.
  - Error recovery: if the file content differs from the example, add the new string as the last item in the existing top-level `plugin` array and ensure the previous item has a trailing comma.

- [x] 1.2 Validate `opencode-scheduler` appears exactly once.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    $matches = Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern '"opencode-scheduler"' -AllMatches; $count = ($matches.Matches | Measure-Object).Count; Write-Output "opencode-scheduler count: $count"
    ```
  - Authoritative acceptance check: output is `opencode-scheduler count: 1`.
  - Error recovery: if count is `0`, repeat task 1.1; if count is greater than `1`, remove duplicate entries and rerun this validation.

- [x] 1.3 Validate config parses as JSONC-compatible JSON after comment stripping.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    node -e "const fs=require('fs'); const p='C:/Users/DaveWitkin/.config/opencode/opencode.jsonc'; let s=fs.readFileSync(p,'utf8').replace(/\/\*[\s\S]*?\*\//g,'').replace(/^\s*\/\/.*$/mg,''); JSON.parse(s); console.log('JSONC parse OK')"
    ```
  - Authoritative acceptance check: output is `JSONC parse OK`.
  - Error recovery: if `node` is not available, use Bun:
    ```powershell
    bun -e "const fs=require('fs'); const p='C:/Users/DaveWitkin/.config/opencode/opencode.jsonc'; let s=fs.readFileSync(p,'utf8').replace(/\/\*[\s\S]*?\*\//g,'').replace(/^\s*\/\/.*$/mg,''); JSON.parse(s); console.log('JSONC parse OK')"
    ```
    If parsing fails, restore from backup and reapply the plugin entry more carefully.

**Phase 1 exit criteria:** `opencode.jsonc` contains `opencode-scheduler` exactly once and parses successfully.

---

## Phase 2: Implementation — Trigger Plugin Install/Load

Objective: Start OpenCode once so the npm plugin can be installed/loaded, then verify the scheduler plugin cache exists.

- [x] 2.1 Start an OpenCode non-interactive command to trigger plugin installation.
  - Working directory: `C:\development\opencode`
  - Command:
    ```powershell
    opencode --version
    ```
  - Authoritative acceptance check: command exits successfully and prints an OpenCode version.
  - Error recovery: if `opencode` is not recognized, run:
    ```powershell
    where.exe opencode
    ```
    If no path is returned, stop and report that OpenCode CLI is unavailable in PATH.

- [x] 2.2 Verify the scheduler plugin is installed in the OpenCode cache.
  - Directory: `C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler\node_modules\opencode-scheduler`
  - Command:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler\node_modules\opencode-scheduler"
    ```
  - Authoritative acceptance check: command prints `True`.
  - Error recovery: if it prints `False`, run OpenCode once in a minimal prompt to force plugin bootstrap:
    ```powershell
    opencode run "Say ready" --format text
    ```
    Then rerun the `Test-Path` command. If still `False`, capture the OpenCode output and stop for plugin install troubleshooting.

- [x] 2.3 Verify the installed scheduler package has package metadata.
  - File: `C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler\node_modules\opencode-scheduler\package.json`
  - Command:
    ```powershell
    Get-Content "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler\node_modules\opencode-scheduler\package.json" -Raw | ConvertFrom-Json | Select-Object name, version
    ```
  - Authoritative acceptance check: output includes `name` equal to `opencode-scheduler` and a non-empty `version`.
  - Error recovery: if the file is missing or invalid, remove only the scheduler cache folder and rerun task 2.1:
    ```powershell
    Remove-Item "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler\node_modules\opencode-scheduler" -Recurse -Force
    opencode --version
    ```

**Phase 2 exit criteria:** OpenCode runs successfully and the scheduler plugin cache directory/package metadata exist.

---

## Phase 3: Implementation — Validate Scheduler Definitions and Windows Tasks

Objective: Confirm existing job definitions and task registrations survived plugin restoration without destructive changes.

- [x] 3.1 Validate the hourly email auto-sort scheduler scope file still exists.
  - File: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json`
  - Command:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json"
    ```
  - Authoritative acceptance check: command prints `True`.
  - Error recovery: if it prints `False`, stop and do not recreate from memory; report missing scheduler scope file.

- [x] 3.2 Validate the hourly email auto-sort job JSON parses and has the expected command.
  - File: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json`
  - Command:
    ```powershell
    $job = Get-Content "C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\email-triage-0fff020d966c\jobs\email-triage-hourly-email-auto-sort.json" -Raw | ConvertFrom-Json; $job.schedule; $job.run.command
    ```
  - Authoritative acceptance check: first output line is the current registered schedule `*/15 * * * *`; second output line is the current wrapper command `wscript //B "C:\development\email-triage\scripts\run-hidden.vbs"`. If the desired target is to change cadence back to hourly or bypass the wrapper, stop and ask the user before changing the job JSON.
  - Error recovery: if JSON parsing fails, restore the job file from the most recent scheduler backup if one exists; otherwise stop and ask for approval before editing scheduler job JSON.

- [x] 3.3 Validate the hourly email auto-sort Windows scheduled task exists.
  - Task name: `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
  - Command:
    ```powershell
    Get-ScheduledTask -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Select-Object TaskName, State
    ```
  - Authoritative acceptance check: output includes the task name and `State` is `Ready`.
  - Error recovery: if task is not found, do not manually create it yet; first run OpenCode with the scheduler plugin loaded and inspect whether the plugin offers a registry sync mechanism. If no sync mechanism is available, document the missing task in handover.

- [x] 3.4 Capture detailed hourly task timing metadata.
  - Task name: `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
  - Command:
    ```powershell
    Get-ScheduledTaskInfo -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Select-Object LastRunTime, LastTaskResult, NextRunTime, NumberOfMissedRuns | Format-List
    ```
  - Authoritative acceptance check: output shows concrete task metadata. `NextRunTime` should be populated after scheduler/plugin restoration or after Windows Task Scheduler recalculates the trigger. KNOWN ISSUE (verified during this review on 2026-07-04): `Get-ScheduledTaskInfo` for the hourly task may return `The system cannot find the file specified.` even when `Get-ScheduledTask` reports the task as `Ready` (state-only query succeeds, info query fails). When that happens, accept the validation if the state is `Ready` and capture the metadata-fetch failure in the handover as a follow-up; do not block Phase 3 on it.
  - Error recovery: if `Get-ScheduledTaskInfo` says the file cannot be found while `Get-ScheduledTask` shows the task, export the task XML for diagnosis:
    ```powershell
    Export-ScheduledTask -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Out-File "C:\Users\DaveWitkin\AppData\Local\Temp\opencode\hourly-email-auto-sort-task.xml" -Encoding utf8
    ```
    Record this inconsistency in handover.

- [x] 3.5 List all OpenCode scheduled tasks after plugin restoration.
  - System artifact: Windows Task Scheduler tasks named `opencode-job-*`
  - Command:
    ```powershell
    Get-ScheduledTask | Where-Object { $_.TaskName -like "opencode-job-*" } | Sort-Object TaskName | Select-Object TaskName, State | Format-Table -AutoSize
    ```
  - Authoritative acceptance check: output includes at least the hourly email auto-sort task plus existing global/development tasks.
  - Error recovery: if shell quoting breaks `$_`, put the command in `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\list-opencode-tasks.ps1` and run it with `pwsh -ExecutionPolicy Bypass -File`.

**Phase 3 exit criteria:** Hourly scheduler JSON exists and parses, the hourly task exists, task metadata has been captured, and all `opencode-job-*` tasks have been listed.

---

## Phase 4: Implementation — Validate Hourly Email Auto-Sort Runtime Readiness

Objective: Verify the hourly email auto-sort script is ready to run headlessly with app-only Graph auth, without changing production behavior unexpectedly.

- [x] 4.1 Validate the hourly email auto-sort script exists.
  - File: `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
  - Command:
    ```powershell
    Test-Path "C:\development\email-triage\scripts\hourly-email-auto-sort.ps1"
    ```
  - Authoritative acceptance check: command prints `True`.
  - Error recovery: if it prints `False`, stop and report that the scheduler job points to a missing script.

- [x] 4.2 Validate the no-WAM Graph auth wrapper exists.
  - File: `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1`
  - Command:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
    ```
  - Authoritative acceptance check: command prints `True`.
  - Error recovery: if it prints `False`, stop and restore or locate the `microsoft-graph` lazy skill before testing auto-sort.

- [x] 4.3 Validate the script references app-only/no-WAM auth rather than delegated auth.
  - File: `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
  - Command:
    ```powershell
    Select-String -Path "C:\development\email-triage\scripts\hourly-email-auto-sort.ps1" -Pattern 'Connect-GraphNoWam|Connect-MgGraph -ClientId|CertificateThumbprint|CertThumbprint' | Select-Object LineNumber, Line
    ```
  - Authoritative acceptance check: output includes `Connect-GraphNoWam` and a certificate/thumbprint reference; output does not show the old delegated pattern `Connect-MgGraph -ClientId ... -Scopes` in the active auth path.
  - Error recovery: if only delegated auth is present, do not rewrite the script in this track without user approval; create a follow-up defect because this plan assumes auth was already fixed.

- [x] 4.4 Run a manual foreground dry-run of the hourly email auto-sort script.
  - Working directory: `C:\development\email-triage`
  - Command:
    ```powershell
    pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\development\email-triage\scripts\hourly-email-auto-sort.ps1"
    ```
  - Authoritative acceptance check: script reaches `## Authentication` and either logs successful no-WAM/app-only connection or completes with an exit code that maps to a documented non-auth condition.
  - Error recovery: if output includes `Graph auth failed`, capture the exact message and validate certificate presence:
    ```powershell
    Get-Item "Cert:\CurrentUser\My\764A4240264B0F302BE55247A9BC4AB1FBD5C357" | Select-Object Subject, Thumbprint, NotAfter, HasPrivateKey
    ```
    If certificate is missing/expired/no private key, stop and document an auth dependency failure.

- [x] 4.5 Inspect the newest email-triage log after manual run.
  - Directory: `C:\development\email-triage\logs`
  - Command:
    ```powershell
    Get-ChildItem "C:\development\email-triage\logs" -Filter "*_run.md" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object { Write-Output $_.FullName; Get-Content $_.FullName -Tail 40 }
    ```
  - Authoritative acceptance check: newest run log (`<timestamp>_run.md`) contains authentication status and no old `writing to a listener` auth failure. NOTE (verified 2026-07-04): the script writes Markdown run logs named `YYYY-MM-DD_HH-mm_run.md`, not `*.log` files, so the filter must use `*_run.md`.
  - Error recovery: if no log exists, check script output and exit code; document that runtime logging is missing as a follow-up issue.

**Phase 4 exit criteria:** The script path, auth wrapper, auth pattern, and manual runtime behavior have been validated with concrete output.

---

## Final Phase: Validation & Handover

Objective: Confirm the remediation is complete, document what changed, and leave an audit trail for the next session.

- [x] 5.1 Reconfirm the plugin entry remains exactly once.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    $count = ((Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern '"opencode-scheduler"' -AllMatches).Matches | Measure-Object).Count; Write-Output "opencode-scheduler count: $count"
    ```
  - Authoritative acceptance check: output is `opencode-scheduler count: 1`.
  - Error recovery: if count differs, fix the plugin array before handover.

- [x] 5.2 Reconfirm the scheduler plugin cache exists.
  - Directory: `C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler\node_modules\opencode-scheduler`
  - Command:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler\node_modules\opencode-scheduler"
    ```
  - Authoritative acceptance check: command prints `True`.
  - Error recovery: if `False`, rerun Phase 2 or document plugin install failure.

- [x] 5.3 Reconfirm the hourly task exists and capture final metadata.
  - Task name: `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
  - Command:
    ```powershell
    Get-ScheduledTask -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Select-Object TaskName, State; Get-ScheduledTaskInfo -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Select-Object LastRunTime, LastTaskResult, NextRunTime, NumberOfMissedRuns | Format-List
    ```
  - Authoritative acceptance check: task exists, state is `Ready`, and timing metadata is captured.
  - Error recovery: if task metadata cannot be read, export task XML and include the export path in handover.

- [x] 5.4 Create execution handover note.
  - File to create: `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/handover.md` (execution handover). Preserve the existing read-only analysis handover as `analysis-handover.md`; do not overwrite it.
  - Required template:
    ```markdown
    # Handover: Restore OpenCode Scheduler Plugin

    ## Summary
    - Changed: <brief list>
    - Not changed: <brief list>

    ## Commands Run
    - `<command>` -> `<result>`

    ## Validation Results
    - Config plugin count: <value>
    - Plugin cache exists: <True/False>
    - Hourly task state: <value>
    - Hourly task LastRunTime/NextRunTime: <values>
    - Email auto-sort manual run: <result>

    ## Rollback Path
    - Backup file: `<full backup path>`
    - Restore command: `Copy-Item "<backup>" "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Force`

    ## Follow-Up Items
    - <item or None>
    ```
  - Authoritative acceptance check: file exists and includes the backup path, commands run, and validation results.
  - Error recovery: if any validation failed, do not mark the track complete; document blockers in this handover file.

- [x] 5.5 Update track metadata status.
  - File to modify: `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/metadata.json`
  - Required final status if all validation passes:
    ```json
    {
      "status": "completed",
      "phase": "handover",
      "completedAt": "<ISO-8601 timestamp>"
    }
    ```
  - Authoritative acceptance check: metadata remains valid JSON.
  - Error recovery: if validation is blocked, set `status` to `blocked` and include a `blockers` array with exact failure messages.

**Final phase exit criteria:** Config, plugin cache, scheduler task, email auto-sort readiness, handover, and metadata are all validated or documented as blocked with exact recovery instructions.

---

## Execution Readiness Checklist

- [x] Atomic tasks — each checkbox contains one clear action.
- [x] Exact file paths — every task names precise files/directories/tasks.
- [x] Explicit commands — terminal commands are written verbatim.
- [x] Clear ordering — phases and tasks are strictly ordered from backup to edit to validation to handover.
- [x] Verification per step — every task includes expected validation output or state.
- [x] No assumed context — starting state, paths, and commands are included inline.
- [x] Concrete examples — config structure and handover templates are included.
- [x] Error recovery — each task includes fallback/stop instructions for common failures.

## Top 3 Implementation Risks + Mitigations

1. **Risk:** Adding the plugin breaks OpenCode startup due to plugin incompatibility or package install failure.
   - **Mitigation:** Create a timestamped config backup first; validate with `opencode --version`; rollback by restoring the backup if startup fails repeatedly.

2. **Risk:** Windows scheduled task registration exists but has inconsistent metadata (`Get-ScheduledTaskInfo` cannot read it).
   - **Mitigation:** Validate task existence separately from task info; export task XML for diagnosis; do not delete/recreate tasks without approval.

3. **Risk:** Hourly email auto-sort runtime still fails due to Graph certificate/permission drift even though scheduler is restored.
   - **Mitigation:** Validate no-WAM wrapper path, certificate thumbprint, manual script run, and newest logs; document exact auth/permission failure if encountered.

## First Task the Build Agent Should Execute Immediately

Start with **Task 0.1**:

```powershell
Test-Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"
```

Expected output: `True`.






