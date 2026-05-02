# Plan: Upgrade oc-chatgpt-multi-auth to oc-codex-multi-auth

This plan is written for an execution agent that should not infer missing steps. Run the tasks in order. Do not edit cached plugin source files. Do not delete package cache or patch backup directories.

Checkbox states:
- `[ ]` Pending
- `[~]` In progress
- `[x]` Completed

## Phase 1 — Verify Config State

- [x] Verify `C:\Users\DaveWitkin\.config\opencode\opencode.json` references the new plugin.
  Command:
  ```powershell
  pwsh -NoProfile -Command '$cfg = Get-Content "C:\Users\DaveWitkin\.config\opencode\opencode.json" -Raw | ConvertFrom-Json; $cfg.plugin'
  ```
  Success criteria: output includes exactly `oc-codex-multi-auth`.
  Failure recovery: if output does not include `oc-codex-multi-auth`, stop and report the actual output.

- [x] Verify at least one config backup exists.
  Command:
  ```powershell
  pwsh -NoProfile -Command "Get-ChildItem 'C:\Users\DaveWitkin\.config\opencode' -Filter 'opencode.json.bak-2026-05-01_*' | Select-Object -ExpandProperty FullName"
  ```
  Success criteria: at least one backup file path is printed.
  Failure recovery: if no backup is printed, continue only after warning the user that rollback will require manual config editing.

- [x] Verify `C:\Users\DaveWitkin\.config\opencode\opencode.json` contains no `oc-chatgpt-multi-auth` references.
  Command:
  ```powershell
  pwsh -NoProfile -Command "Select-String -Path 'C:\Users\DaveWitkin\.config\opencode\opencode.json' -Pattern 'oc-chatgpt-multi-auth' -SimpleMatch"
  ```
  Success criteria: command prints no matches.
  Failure recovery: if a match is printed, stop and report the matching line before editing anything.

## Phase 2 — Configure Stream Stall Timeout

- [x] Use the User environment variable approach. Do not modify plugin source and do not add plugin config unless explicitly instructed later.
  Chosen setting: `CODEX_AUTH_STREAM_STALL_TIMEOUT_MS=120000`.
  Reason: v6.1.8 `config.js` reads this env var before falling back to plugin config or the 45,000ms default.
  Success criteria: this decision is understood before running the next task.

- [x] Set the User environment variable for future OpenCode sessions.
  Command:
  ```powershell
  pwsh -NoProfile -Command "[Environment]::SetEnvironmentVariable('CODEX_AUTH_STREAM_STALL_TIMEOUT_MS','120000','User')"
  ```
  Success criteria: command exits with code 0.
  Failure recovery: if the command fails with permissions or registry access errors, report the exact error and ask the user to approve running the same command from an elevated PowerShell session.

- [x] Verify the User environment variable is set to `120000`.
  Command:
  ```powershell
  pwsh -NoProfile -Command "[Environment]::GetEnvironmentVariable('CODEX_AUTH_STREAM_STALL_TIMEOUT_MS','User')"
  ```
  Success criteria: output is exactly `120000`.
  Failure recovery: if output is empty or different, rerun the previous task once, then verify again. If still wrong, stop and report both outputs.

- [x] Record the restart requirement before validation.
  Required note: already-running OpenCode sessions will not inherit the new User environment variable. OpenCode must be fully closed and restarted before validating plugin load or timeout behavior.
  Success criteria: do not proceed to Phase 3 until this note is acknowledged in the handoff to the user.

## Phase 3 — Restart OpenCode and Load New Plugin

- [x] Ask the user to fully exit and restart OpenCode.
  Message to user:
  ```text
  Please fully close this OpenCode session and start OpenCode again so it loads the new oc-codex-multi-auth plugin and the CODEX_AUTH_STREAM_STALL_TIMEOUT_MS=120000 User environment variable.
  ```
  Success criteria: user confirms OpenCode has been restarted.
  Failure recovery: if the user cannot restart immediately, pause this track before Phase 4. Do not mark validation complete before restart.

- [ ] After OpenCode restart, verify the new plugin package cache exists.
  Command:
  ```powershell
  pwsh -NoProfile -Command 'Get-ChildItem "C:\Users\DaveWitkin\.cache\opencode\packages" -Directory | Where-Object { $_.Name -like "oc-codex-multi-auth@*" } | Select-Object -ExpandProperty FullName'
  ```
  Success criteria: output includes a directory like `C:\Users\DaveWitkin\.cache\opencode\packages\oc-codex-multi-auth@6.1.8`.
  Failure recovery: if no directory appears, restart OpenCode one more time and rerun the command. If still absent, run:
  ```powershell
  pwsh -NoProfile -Command "npm view oc-codex-multi-auth version"
  ```
  Then report the npm output and stop.

- [ ] Verify no debug body dump remains in the new plugin source.
  Command:
  ```powershell
  pwsh -NoProfile -Command '$dirs = Get-ChildItem "C:\Users\DaveWitkin\.cache\opencode\packages" -Directory | Where-Object { $_.Name -like "oc-codex-multi-auth@*" }; foreach ($d in $dirs) { Get-ChildItem $d.FullName -Recurse -File | Select-String -Pattern "writeFileSync" -SimpleMatch }'
  ```
  Success criteria: command prints no matches.
  Failure recovery: if matches are printed, do not edit files; report the matching file paths and lines.

## Phase 4 — Validate Codex Tools and Models

- [ ] Use the OpenCode Codex account tool `codex-list` with no tag filter.
  Success criteria: all previously configured OAuth accounts are listed and no tool error is returned.
  Failure recovery: if the tool is unavailable, confirm OpenCode was restarted and that `C:\Users\DaveWitkin\.config\opencode\opencode.json` references `oc-codex-multi-auth`.

- [ ] Use the OpenCode Codex account tool `codex-status`.
  Success criteria: account status is returned without errors; no account shows an unrecoverable auth failure.
  Failure recovery: if refresh/auth errors appear, run `codex-health` next and report exact failing account labels.

- [ ] Use the OpenCode Codex account tool `codex-health`.
  Success criteria: refresh tokens validate successfully for configured accounts.
  Failure recovery: if any account fails, do not delete it; report the failing account index/label and ask the user whether to re-authenticate.

- [ ] Verify `C:\Users\DaveWitkin\.config\opencode\opencode.json` contains the required model keys.
  Command:
  ```powershell
  pwsh -NoProfile -Command '$models = (Get-Content "C:\Users\DaveWitkin\.config\opencode\opencode.json" -Raw | ConvertFrom-Json).provider.openai.models.PSObject.Properties.Name; $required = @("gpt-5.4-pro","gpt-5.4-mini","gpt-5.4-nano","gpt-5.5","gpt-5.5-fast","gpt-5.1-codex","gpt-5.1-codex-max","gpt-5.1-codex-mini","gpt-5-codex","gpt-5.1"); $missing = $required | Where-Object { $_ -notin $models }; if ($missing) { "MISSING: " + ($missing -join ", ") } else { "OK: all required models present" }'
  ```
  Success criteria: output is `OK: all required models present`.
  Failure recovery: if output starts with `MISSING:`, report the missing model keys and stop before marking the upgrade complete.

- [ ] Verify the timeout setting that new OpenCode sessions inherit is `120000`.
  Command:
  ```powershell
  pwsh -NoProfile -Command "[Environment]::GetEnvironmentVariable('CODEX_AUTH_STREAM_STALL_TIMEOUT_MS','User')"
  ```
  Success criteria: output is exactly `120000`.
  Failure recovery: if output is empty or different, return to Phase 2 and reset the User environment variable.

## Phase 5 — Cleanup and Documentation

- [ ] Verify rollback cache remains present and do not delete it.
  Command:
  ```powershell
  pwsh -NoProfile -Command "Test-Path 'C:\Users\DaveWitkin\.cache\opencode\packages\oc-chatgpt-multi-auth@5.4.4'"
  ```
  Success criteria: output is `True`.
  Failure recovery: if output is `False`, warn the user rollback to the old cached patched plugin may not be available.

- [ ] Verify local patch backup directories remain present and do not delete them.
  Command:
  ```powershell
  pwsh -NoProfile -Command 'Get-ChildItem "C:\Users\DaveWitkin\.cache\opencode\packages\oc-chatgpt-multi-auth@5.4.4" -Directory | Where-Object { $_.Name -like "codex-*-backup-*" } | Select-Object -ExpandProperty Name'
  ```
  Success criteria: output includes both `codex-silent-failure-backup-20260429-124515` and `codex-arguments-calllike-backup-20260429-145809`.
  Failure recovery: if either name is missing, warn the user that patch history is incomplete, but do not recreate or delete directories.

- [ ] Add a supersession note to `C:\development\opencode\.conductor\tracks\20260429-openai-silent-failure\spec.md` after Phase 4 validation passes.
  Append this exact section at the end of the file:
  ```md
  ## Supersession Note

  Superseded on 2026-05-01 by track 20260501-codex-multi-auth-upgrade. The local runtime patches documented here were reconciled against upstream oc-codex-multi-auth@6.1.8. The stream stall timeout is now preserved via CODEX_AUTH_STREAM_STALL_TIMEOUT_MS=120000 rather than source patching.
  ```
  Verification command:
  ```powershell
  pwsh -NoProfile -Command "Select-String -Path 'C:\development\opencode\.conductor\tracks\20260429-openai-silent-failure\spec.md' -Pattern 'Superseded on 2026-05-01 by track 20260501-codex-multi-auth-upgrade'"
  ```
  Success criteria: one matching line is printed.
  Failure recovery: if no matching line is printed, append the section once. Do not duplicate it if it already exists.

- [ ] Update `C:\development\opencode\.conductor\tracks\20260501-codex-multi-auth-upgrade\metadata.json` after all validation tasks pass.
  Required changes:
  - Set `"status": "completed"`
  - Set `"completed": "2026-05-01"`
  - Set `"progress.completedTasks"` equal to `"progress.totalTasks"`
  - Set `"progress.percentage": 100`
  Verification command:
  ```powershell
  pwsh -NoProfile -Command '$m = Get-Content "C:\development\opencode\.conductor\tracks\20260501-codex-multi-auth-upgrade\metadata.json" -Raw | ConvertFrom-Json; $m.status; $m.completed; $m.progress.percentage'
  ```
  Success criteria: outputs `completed`, `2026-05-01`, and `100`.

- [ ] Update `C:\development\opencode\.conductor\tracks-ledger.md` after all validation tasks pass.
  Required change: move `20260501-codex-multi-auth-upgrade` from `## Active Tracks` to `## Completed Tracks` and include `(Completed: 2026-05-01)`.
  Verification command:
  ```powershell
  pwsh -NoProfile -Command "Select-String -Path 'C:\development\opencode\.conductor\tracks-ledger.md' -Pattern '20260501-codex-multi-auth-upgrade.*Completed: 2026-05-01'"
  ```
  Success criteria: one matching line is printed under `## Completed Tracks`.

## Rollback Plan

Use rollback only if Phase 3 or Phase 4 fails after the listed recovery steps.

1. Restore the previous plugin name in `C:\Users\DaveWitkin\.config\opencode\opencode.json`.
   Manual JSON target:
   ```json
   "plugin": [
     "oc-chatgpt-multi-auth"
   ]
   ```
2. Restart OpenCode.
3. Verify rollback cache exists:
   ```powershell
   pwsh -NoProfile -Command "Test-Path 'C:\Users\DaveWitkin\.cache\opencode\packages\oc-chatgpt-multi-auth@5.4.4'"
   ```
4. Report that rollback is complete and leave all backup directories untouched.

## Notes for the Build Agent

- The plugin is installed by OpenCode at startup, not by npm directly.
- The `opencode.json` config's `"plugin"` array tells OpenCode which npm package to fetch and cache locally.
- The `npx oc-codex-multi-auth@latest` run already updated `C:\Users\DaveWitkin\.config\opencode\opencode.json` to reference the new package name.
- The actual package swap happens on next OpenCode restart.
- `codex-list`, `codex-status`, and `codex-health` are OpenCode tools, not shell commands.
- Do not edit the new plugin's cached source code in `C:\Users\DaveWitkin\.cache\opencode\packages\oc-codex-multi-auth@*`.
- The timeout function checks `CODEX_AUTH_STREAM_STALL_TIMEOUT_MS` first, then plugin config, then `45_000`.
