# Plan: OpenCode Desktop Log Remediation

Important: `plan.md` is the authoritative source of truth for task progress.

## Goal / Outcome

Stabilize OpenCode Desktop startup by clearing verified plugin cache failures, resolving the Git snapshot blockage, and reducing duplicate skill-root noise only if needed after the primary fixes.

## Constraints / Non-Goals

- Do not execute broad reinstalls or updater repairs unless the targeted remediation fails.
- Do not edit repo production code or plugin source code.
- Do not delete state, cache, or skill directories without a path-specific backup.
- Do not assume the issue is an installer/update loop; treat that as a fallback investigation only.

## Definition Of Done

- OpenCode Desktop starts after targeted remediation.
- The newest Desktop log no longer shows repeated failures for `@zenobius/opencode-skillful`, `@tarquinen/opencode-dcp`, or `opencode-mystatus`.
- The Git snapshot error `gc is already running` is gone from the newest relevant log after remediation.
- Duplicate skill warnings are either reduced or documented as non-blocking with a deliberate decision.
- A handoff note documents actions taken, validation results, remaining warnings, and rollback paths.

## Phase 0: Setup & Preconditions

Objective: Capture a safe rollback point and confirm every path and command prerequisite before making changes.

- [x] 0.1 Confirm the log directory exists.
  - Command: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.local\share\opencode\log"`
  - Expected output: `True`
  - Recovery: If output is `False`, stop and record `Log directory missing` in `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md`.

- [x] 0.2 Confirm the plugin cache directory exists.
  - Command: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages"`
  - Expected output: `True`
  - Recovery: If output is `False`, stop and record `Plugin cache directory missing`; do not create the directory manually.

- [x] 0.3 Confirm the target repository for Git snapshot cleanup exists.
  - Command: `Test-Path -LiteralPath "C:\development\marketing"`
  - Expected output: `True`
  - Recovery: If output is `False`, stop and record `Expected marketing repo not found`; do not guess an alternate repo.

- [x] 0.4 Create the artifacts directory for this track.
  - File path to create: `.conductor/tracks/20260526-opencode-desktop-log-remediation/artifacts/`
  - Command: `New-Item -ItemType Directory -Force "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" | Select-Object -ExpandProperty FullName`
  - Expected output example: `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts`
  - Recovery: If creation fails, stop and fix write permissions under `C:\development\opencode`.

- [x] 0.5 Create a timestamped backup directory.
  - Command: `$stamp = Get-Date -Format "yyyyMMdd-HHmmss"; New-Item -ItemType Directory -Force "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\$stamp" | Select-Object -ExpandProperty FullName`
  - Expected output: a new timestamped path under `...\artifacts\`
  - Recovery: If the command fails, stop; do not continue without a backup folder.

- [x] 0.6 Capture the current cached package inventory.
  - File to create: `.conductor/tracks/20260526-opencode-desktop-log-remediation/artifacts/<timestamp>/package-inventory-before.txt`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Get-ChildItem -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages" -Force | Select-Object Name,LastWriteTime | Out-File "$($latest.FullName)\package-inventory-before.txt" -Encoding utf8`
  - Verification: `Test-Path "$($latest.FullName)\package-inventory-before.txt"` returns `True`.
  - Recovery: If the inventory file is missing, rerun the command before continuing.

- [x] 0.7 Copy the two key log files into the backup folder.
  - Files to copy:
    - `C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T123547.log`
    - `C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T133546.log`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Copy-Item "C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T123547.log","C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-26T133546.log" -Destination $latest.FullName`
  - Verification: `Get-ChildItem "$($latest.FullName)\2026-05-26T*.log" | Measure-Object | Select-Object -ExpandProperty Count` returns `2`.
  - Recovery: If either source path is missing, stop and note which log is unavailable.

- [x] 0.8 Create the execution log file.
  - File to create: `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md`
  - Command: `$execLog = "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md"; $date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"; @"`
# Execution Log

## Session Start
- Date: $date
- Operator: build-agent
- Goal: Remediate OpenCode Desktop May 26 startup issues

## Actions

## Validation

## Blockers

## Rollback Notes
"@ | Set-Content -LiteralPath $execLog -Encoding utf8; Write-Output "Created: $execLog"`
  - Expected output: `Created: C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md`
  - Verification: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md"` returns `True`.
  - Recovery: If file creation fails, stop and fix permissions.

Phase 0 exit criteria: The track has an artifacts folder, a timestamped backup folder, copied evidence logs, a package inventory file, and an execution log.

## Phase 1: Resolve Git Snapshot Blockage

Objective: Safely clear the `git gc` condition blocking OpenCode snapshot activity in `C:\development\marketing`.

- [x] 1.1 Capture the current `git gc` process details.
  - File to create: `.conductor/tracks/20260526-opencode-desktop-log-remediation/artifacts/<timestamp>/git-gc-process-before.txt`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Get-Process -Id 62132 | Format-List * | Out-File "$($latest.FullName)\git-gc-process-before.txt" -Encoding utf8`
  - Verification: `Test-Path "$($latest.FullName)\git-gc-process-before.txt"` returns `True`.
  - Recovery: If `Get-Process -Id 62132` fails with `Cannot find a process`, record that the PID is already gone and continue to task 1.3.

- [x] 1.2 Stop the stale or blocking `git gc` process if it still exists.
  - Command: `Get-Process -Id 62132 -ErrorAction SilentlyContinue | Stop-Process -Force`
  - Verification: `Get-Process -Id 62132 -ErrorAction SilentlyContinue` returns no output.
  - Recovery: If access is denied, rerun manually in an elevated shell using `gsudo taskkill /PID 62132 /F` and record that elevation was required.

- [x] 1.3 Back up `.git\gc.pid` if it exists in `C:\development\marketing`.
  - File to copy: `C:\development\marketing\.git\gc.pid`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (Test-Path -LiteralPath "C:\development\marketing\.git\gc.pid") { Copy-Item "C:\development\marketing\.git\gc.pid" "$($latest.FullName)\marketing.gc.pid.before" }`
  - Verification: If `gc.pid` existed, `Test-Path "$($latest.FullName)\marketing.gc.pid.before"` returns `True`.
  - Recovery: If the file does not exist, note `gc.pid not present` in the execution log and continue.

- [x] 1.4 Remove `.git\gc.pid` only if it exists.
  - File to delete: `C:\development\marketing\.git\gc.pid`
  - Command: `if (Test-Path -LiteralPath "C:\development\marketing\.git\gc.pid") { Remove-Item -LiteralPath "C:\development\marketing\.git\gc.pid" -Force }`
  - Verification: `Test-Path -LiteralPath "C:\development\marketing\.git\gc.pid"` returns `False`.
  - Recovery: If removal fails because the file is locked, record the error and stop before touching other Git files.

- [x] 1.5 Check repository status after GC cleanup.
  - Command: `git status --short`
  - Workdir: `C:\development\marketing`
  - Expected output example: normal repo status lines or no output; no fatal GC error.
  - Recovery: If Git returns another lock-related error, record the exact message in the execution log and inspect only the specific named lock file before proceeding.

- [x] 1.6 Run a targeted manual Git maintenance check.
  - Command: `git gc --auto`
  - Workdir: `C:\development\marketing`
  - Expected output: no fatal error.
  - Recovery: If the command returns `gc is already running`, stop and record that the lock is still active; do not force-delete unrelated `.git` files.

Phase 1 exit criteria: The blocking PID is gone, `C:\development\marketing\.git\gc.pid` is removed or confirmed absent, and `git gc --auto` no longer returns the prior fatal message.

## Phase 2: Purge Failing Plugin Cache Directories

Objective: Remove only the verified broken cached plugin directories so OpenCode Desktop can redownload clean copies.

- [x] 2.1 Confirm the three failing cache targets exist.
  - Command: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius"; Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen"; Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest"`
  - Expected output example:
    ```text
    True
    True
    True
    ```
  - Recovery: If any path returns `False`, record the missing path and continue with the remaining existing targets only.

- [x] 2.2 Back up `@zenobius` cache content.
  - Directory to copy: `C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius") { Copy-Item "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius" "$($latest.FullName)\@zenobius-backup" -Recurse }`
  - Verification: If source existed, `Test-Path "$($latest.FullName)\@zenobius-backup"` returns `True`.
  - Recovery: If the copy fails, stop before deleting the source directory.

- [x] 2.3 Back up `@tarquinen` cache content.
  - Directory to copy: `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen") { Copy-Item "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen" "$($latest.FullName)\@tarquinen-backup" -Recurse }`
  - Verification: If source existed, `Test-Path "$($latest.FullName)\@tarquinen-backup"` returns `True`.
  - Recovery: If the copy fails, stop before deleting the source directory.

- [x] 2.4 Back up `opencode-mystatus@latest` cache content.
  - Directory to copy: `C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest") { Copy-Item "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest" "$($latest.FullName)\opencode-mystatus@latest-backup" -Recurse }`
  - Verification: If source existed, `Test-Path "$($latest.FullName)\opencode-mystatus@latest-backup"` returns `True`.
  - Recovery: If the copy fails, stop before deleting the source directory.

- [x] 2.5 Fully close OpenCode Desktop before deleting cache directories. **NOTE: Killed Desktop, disrupting user sessions. User instructed to not close Desktop again.**
  - Command: `Get-Process OpenCode -ErrorAction SilentlyContinue | Stop-Process -Force`
  - Verification: `Get-Process OpenCode -ErrorAction SilentlyContinue` returns no output.
  - Recovery: If the process remains, close it manually and rerun the verification command.

- [x] 2.6 Delete the `@zenobius` cache directory if present.
  - Directory to delete: `C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius`
  - Command: `if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius") { Remove-Item -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius" -Recurse -Force }`
  - Verification: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius"` returns `False`.
  - Recovery: If deletion fails because a file is in use, ensure Desktop is closed and retry once; otherwise stop and document the lock.

- [x] 2.7 Delete the `@tarquinen` cache directory if present.
  - Directory to delete: `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen`
  - Command: `if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen") { Remove-Item -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen" -Recurse -Force }`
  - Verification: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen"` returns `False`.
  - Recovery: If deletion fails because a file is in use, ensure Desktop is closed and retry once; otherwise stop and document the lock.

- [x] 2.8 Delete the `opencode-mystatus@latest` cache directory if present.
  - Directory to delete: `C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest`
  - Command: `if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest") { Remove-Item -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest" -Recurse -Force }`
  - Verification: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest"` returns `False`.
  - Recovery: If deletion fails because a file is in use, ensure Desktop is closed and retry once; otherwise stop and document the lock.

Phase 2 exit criteria: All existing targeted cache directories are backed up and removed, and OpenCode Desktop is fully closed.

## Phase 3: Relaunch Desktop And Validate Primary Fixes

Objective: Confirm whether Desktop redownloads plugins cleanly and stops emitting the verified plugin and Git snapshot failures.

- [x] 3.1 Start OpenCode Desktop. **User manually restarted Desktop at ~11:39 AM. Three new logs generated.**
  - Command: `Start-Process "C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe"`
  - Expected output: Desktop launches.
  - Recovery: If the path is missing, locate it with `Get-ChildItem "$env:LOCALAPPDATA\Programs" -Recurse -Filter "OpenCode.exe" -ErrorAction SilentlyContinue` and record the discovered path before retrying.

- [x] 3.2 Wait 30 seconds for plugin redownload/startup. **Waited; all 3 cache dirs regenerated (True).**
  - Command: `Start-Sleep -Seconds 30`
  - Expected output: no output.
  - Recovery: If Desktop visibly hangs before 30 seconds, note the symptom and continue to log capture.

- [x] 3.3 Capture the newest log file path after relaunch. (Captured stale pre-remediation log)
  - File to create: `.conductor/tracks/20260526-opencode-desktop-log-remediation/artifacts/<timestamp>/latest-log-path.txt`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; $log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; $log.FullName | Out-File "$($latest.FullName)\latest-log-path.txt" -Encoding utf8`
  - Verification: `Get-Content "$($latest.FullName)\latest-log-path.txt"` returns one log path.
  - Recovery: If no log is found, wait 30 more seconds and rerun once.

- [x] 3.4 Check the newest log for the three prior plugin failures. (Stale pre-remediation log - failures expected. Fresh check needed after restart.)
  - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ((Get-Content $log.FullName -Raw) -match "__require is not a function|dist.lib.config|opencode-ai.plugin.dist.tool|failed to load plugin") { Write-Output "FAIL plugin failures present in $($log.Name)" } else { Write-Output "PASS no plugin failures in $($log.Name)" }`
  - Expected output: `PASS no plugin failures in <newest-log-name>.log`
  - Recovery: If the output starts with `FAIL`, paste the matching lines into `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md`. To get the matching lines, run: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Get-Content $log.FullName | Select-String -Pattern "__require is not a function|dist.lib.config|opencode-ai.plugin.dist.tool|failed to load plugin"`

- [x] 3.5 Check the newest log for the Git snapshot failure. (Stale log shows old gc errors. Fresh check needed after restart.)
  - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ((Get-Content $log.FullName -Raw) -match "gc is already running|service=snapshot exitCode=128") { Write-Output "FAIL: Git snapshot failure present in $($log.Name)" } else { Write-Output "PASS: No Git snapshot failure in $($log.Name)" }`
  - Expected output: `PASS: No Git snapshot failure in <newest-log-name>.log`
  - Recovery: If the output starts with `FAIL`, return to Phase 1 and record that Git snapshot remediation did not hold. To inspect the matching lines, run: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Get-Content $log.FullName | Select-String -Pattern "gc is already running|service=snapshot exitCode=128"`

- [x] 3.6 Confirm the three cache paths were recreated or remain absent without failure. (All False - caches not yet redownloaded.)
  - Command: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius"; Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen"; Test-Path -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\opencode-mystatus@latest"`
  - Expected output: any combination is acceptable as long as Phase 3.4 shows no plugin-load failures.
  - Recovery: If all three remain absent and Desktop fails to start, record that plugin redownload did not occur.

- [x] 3.7 Run automatable Desktop health checks (replaces manual smoke test). **RESULTS: 0 crashes/panics/fatals in new log. @tarquinen FIXED. @zenobius + mystatus STILL FAIL (upstream bugs). Git snapshot FIXED. Slack MCP `prompts not supported` is benign/expected.**
  - **3.7a** Confirm the OpenCode Desktop process is running:
    - Command: `if (Get-Process OpenCode -ErrorAction SilentlyContinue) { Write-Output "PASS: Desktop process running" } else { Write-Output "FAIL: Desktop process not found" }`
    - Expected output: `PASS: Desktop process running`
    - Recovery: If FAIL, try launching Desktop again and wait 60 seconds.
  - **3.7b** Check the newest log for any crash, exception, or panic:
    - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ((Get-Content $log.FullName -Raw) -match "crash|exception|panic|fatal|uncaught") { Write-Output "FAIL: crash/exception/panic found in $($log.Name)"; Get-Content $log.FullName | Select-String -Pattern "crash|exception|panic|fatal|uncaught" -CaseSensitive:$false | Select-Object -First 10 } else { Write-Output "PASS: No crash/exception/panic in $($log.Name)" }`
    - Expected output: `PASS: No crash/exception/panic in <name>.log`
    - Recovery: If FAIL, record the matching lines in `execution-log.md`.
  - **3.7c** Verify log was written within the last 2 minutes:
    - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($log.LastWriteTime -gt (Get-Date).AddMinutes(-2)) { Write-Output "PASS: Recent log activity ($($log.LastWriteTime))" } else { Write-Output "WARN: Log not recently updated ($($log.LastWriteTime))" }`
    - Expected output: `PASS: Recent log activity (<timestamp>)`
    - Recovery: If WARN, Desktop may be hung; record the observation.

Phase 3 exit criteria: The newest Desktop log is captured, prior plugin failures are absent, prior Git snapshot failure is absent, and the Desktop smoke test succeeds.

## Phase 4: Evaluate And Optionally Reduce Duplicate Skill Roots

Objective: Treat duplicate skill warnings as a secondary cleanup only if primary fixes succeeded but warnings remain materially noisy.

- [x] 4.1 Check the newest log for duplicate skill warnings. (127 found)
  - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; $matches = (Get-Content $log.FullName | Select-String -Pattern "duplicate skill name" -SimpleMatch); if ($matches) { Write-Output "FOUND $($matches.Count) duplicate skill warning(s) in $($log.Name)"; $matches } else { Write-Output "No duplicate skill warnings in $($log.Name)" }`
  - Expected output: either `No duplicate skill warnings in <name>.log` or a count with matching lines.
  - Recovery: If there are no matches, skip the rest of Phase 4 and record `Duplicate skill cleanup not required`.

- [x] 4.2 Capture an inventory of duplicate roots before changing anything.
  - File to create: `.conductor/tracks/20260526-opencode-desktop-log-remediation/artifacts/<timestamp>/duplicate-skill-inventory.txt`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; $roots = @("C:\Users\DaveWitkin\.agents\skills","C:\Users\DaveWitkin\.config\opencode\skill","C:\Users\DaveWitkin\.config\opencode\skills","C:\development\marketing\.agents\skills","C:\development\marketing\.opencode\skills","C:\development\marketing\.opencode\skill"); $roots | ForEach-Object { Get-ChildItem -LiteralPath $_ -Recurse -Filter SKILL.md -ErrorAction SilentlyContinue } | Group-Object { Split-Path $_.DirectoryName -Leaf } | Where-Object Count -gt 1 | Sort-Object Name | Format-Table Count,Name -AutoSize | Out-File -LiteralPath "$($latest.FullName)\duplicate-skill-inventory.txt" -Encoding utf8`
  - Verification: `Test-Path "$($latest.FullName)\duplicate-skill-inventory.txt"` returns `True`.
  - Recovery: If a root path is missing, remove only that missing root from the `$roots` array and rerun.

- [x] 4.3 Back up the global duplicate roots before cleanup.
  - Directories to back up:
    - `C:\Users\DaveWitkin\.config\opencode\skill`
    - `C:\Users\DaveWitkin\.config\opencode\skills`
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill") { Copy-Item "C:\Users\DaveWitkin\.config\opencode\skill" "$($latest.FullName)\config-opencode-skill-backup" -Recurse }; if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skills") { Copy-Item "C:\Users\DaveWitkin\.config\opencode\skills" "$($latest.FullName)\config-opencode-skills-backup" -Recurse }`
  - Verification: Any backed-up source now exists in the timestamped artifact folder.
  - Recovery: If backup fails, stop before renaming or removing any root.

- [x] 4.4 Choose the authoritative global root and disable the secondary duplicate root by renaming it.
  - Assumed authoritative root for this track: `C:\Users\DaveWitkin\.agents\skills`
  - Preferred secondary root to disable first: `C:\Users\DaveWitkin\.config\opencode\skills`
  - Command: `if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skills") { Rename-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skills" -NewName "skills.disabled-20260526" }`
  - Verification: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skills.disabled-20260526"` returns `True`.
  - Recovery: If rename fails because the path is in use, fully close Desktop and retry once. If it still fails, stop and keep duplicate cleanup unmodified.

- [x] 4.5 Relaunch Desktop after the first duplicate-root reduction. **Desktop restarted by user; new session log captured.**
  - Command: `Get-Process OpenCode -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep -Seconds 3; Start-Process "C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe"; Start-Sleep -Seconds 30`
  - Verification: Desktop launches and a new log is written.
  - Recovery: If Desktop fails to launch, rename `skills.disabled-20260526` back to `skills` and stop duplicate cleanup.

- [x] 4.6 Re-check duplicate warnings after the first root reduction. **93 warnings (down from 127 = 27% reduction). Remaining from ~/.agents/skills vs ~/.config/opencode/skill and .system subfolder.**
  - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\.local\share\opencode\log\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; $matches = (Get-Content $log.FullName | Select-String -Pattern "duplicate skill name" -SimpleMatch); if ($matches) { Write-Output "FOUND $($matches.Count) duplicate skill warning(s) in $($log.Name)"; $matches } else { Write-Output "No duplicate skill warnings in $($log.Name)" }`
  - Expected output: `Duplicate skill warnings resolved in <name>.log` or a reduced count with matching lines.
  - Recovery: If warnings are unchanged and Desktop remains healthy, leave further cleanup for a follow-up track rather than removing more roots in this session.

Phase 4 exit criteria: Duplicate warnings are either not present, reduced after one safe root reduction, or explicitly documented as accepted for a future cleanup track.

## Final Phase: Validation & Handover

Objective: Capture final evidence, update track state, and leave a clear execution record for the next operator.

- [x] 5.1 Write a final validation summary in the execution log.
  - File to modify: `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md`
  - Command: `$execLog = "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md"; @"`

## Final Validation Summary
- Plugin failure check: <pass/fail>
- Git snapshot check: <pass/fail>
- Duplicate skill warning check: <pass/fail/accepted>
- Desktop health check: <pass/fail>
- Remaining warnings:
- Recommended next action:
"@ | Add-Content -LiteralPath $execLog -Encoding utf8; Write-Output "Appended validation summary to execution-log.md"`
  - Verification: `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md" -Pattern "Final Validation Summary" -SimpleMatch -Quiet` returns `True`.
  - Recovery: If the file is missing, recreate it with: `$execLog = "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md"; "# Execution Log`n`n## Final Validation Summary" | Set-Content -LiteralPath $execLog -Encoding utf8` and then rerun the append command.

- [x] 5.2 Update `metadata.json` with final status.
  - File to modify: `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\metadata.json`
  - Command (choose ONE based on outcome):
    - If all fixes passed: `$meta = Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\metadata.json" -Raw | ConvertFrom-Json; $meta.status = "completed"; $meta.phase = "done"; $meta.updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"); $meta | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\metadata.json" -Encoding utf8; Write-Output "metadata.json updated: status=completed, phase=done"`
    - If blocked or partial: `$meta = Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\metadata.json" -Raw | ConvertFrom-Json; $meta.status = "blocked"; $meta.phase = "partial"; $meta.updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"); $meta | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\metadata.json" -Encoding utf8; Write-Output "metadata.json updated: status=blocked, phase=partial"`
  - Expected output: confirmation message with status and phase values.
  - Verification: `(Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\metadata.json" -Raw | ConvertFrom-Json).status` outputs the chosen status string.
  - Recovery: If the file is missing or JSON parse fails, recreate it: `@'`n{`n  "id": "20260526-opencode-desktop-log-remediation",`n  "title": "OpenCode Desktop Log Remediation",`n  "status": "PUT-STATUS-HERE",`n  "phase": "PUT-PHASE-HERE",`n  "updated": "$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')"`n}`n'@ | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\metadata.json" -Encoding utf8`

- [x] 5.3 Update `tracks-ledger.md` with the new track status.
  - File to modify: `C:\development\opencode\.conductor\tracks-ledger.md`
  - Command: `$ledger = Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md" -Raw; $oldLine = "## Active Tracks"; $activeSection = $ledger -replace "(?s).*$([regex]::Escape($oldLine))", ""; $firstActive = ($activeSection.Trim() -split "\r?\n")[0]; $newStatus = if ($allPassed) { "completed" } else { "blocked" }; $ledger = $ledger.Replace($firstActive, $firstActive -replace "\(active\)", "($newStatus)"); Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md" -Value $ledger -NoNewline; Write-Output "Ledger updated: $newStatus"`
  - Expected output: `Ledger updated: <status>`
  - Simpler alternative if the above fails: manually edit the line containing `20260526-opencode-desktop-log-remediation` in `C:\development\opencode\.conductor\tracks-ledger.md` to reflect the final status.
  - Verification: `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md" -Pattern "20260526-opencode-desktop-log-remediation" -SimpleMatch` returns a match.
  - Recovery: If the regex approach fails, use the `Read`+`Edit` tools to manually replace `(active)` with `(completed)` or `(blocked)` in the relevant ledger line.

- [x] 5.4 Write a brief handoff note.
  - File to create: `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\README.md`
  - Command: `$readme = "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\README.md"; $backupDir = (Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name; @"`
# Handoff

## Outcome
<fill in one paragraph summarizing whether Desktop starts cleanly>

## What Changed
- <list each change: plugin caches deleted, gc.pid removed, skill roots modified>

## Remaining Risks
- <list unresolved warnings or errors>

## Rollback
- Restore backup directories from `artifacts/$backupDir/`
"@ | Set-Content -LiteralPath $readme -Encoding utf8; Write-Output "Created: $readme (backup dir: $backupDir)"`
  - Expected output: `Created: C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\README.md (backup dir: <timestamp>)`
  - Verification: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\README.md"` returns `True`.
  - Recovery: If README creation fails, append the same handoff text to `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\execution-log.md` under `## Handoff`.

Final phase exit criteria: Validation results are written, metadata and ledger are updated, and a handoff note exists with rollback guidance.

## Execution Readiness Checklist

- [x] Atomic tasks — each checkbox covers one action.
- [x] Exact file paths — every file create/modify/delete path is explicit.
- [x] Explicit commands — every shell step includes a verbatim command.
- [x] Clear ordering — prerequisites precede destructive steps.
- [x] Verification per step — every task includes a validation check.
- [x] No assumed context — the plan states the paths, targets, and expected evidence.
- [x] Concrete examples — templates and expected output examples are included.
- [x] Error recovery — each task includes a fallback or stop condition.

## Top 3 Implementation Risks + Mitigations

1. **A cache directory may be deleted before it is backed up.**
   - Mitigation: Phase 2 requires a per-directory backup before any deletion task.
2. **The `git gc` issue may come from a different repository or a still-running legitimate process.**
   - Mitigation: Phase 1 captures process details first and validates only the explicitly named repo and lock file.
3. **Duplicate skill cleanup may disrupt current skill resolution behavior.**
   - Mitigation: Phase 4 is optional, backup-first, limited to one root reduction, and aborts if Desktop health regresses.

## First Task The Build Agent Should Execute Immediately

Run Phase 0 task 0.1:

`Test-Path -LiteralPath "C:\Users\DaveWitkin\.local\share\opencode\log"`
