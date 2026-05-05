# Plan: Disable OpenCode Markdown Table Formatter Plugin

## Phase 0: Setup & Preconditions

Objective: Establish the exact active config file, confirm the target plugin is present, and create a rollback-safe backup before any edit.

- [x] 0.1 Confirm the active global OpenCode config file exists at `C:/Users/DaveWitkin/.config/opencode/opencode.jsonc`.
  - Command:
    ```powershell
    Test-Path "$env:USERPROFILE\.config\opencode\opencode.jsonc"
    ```
  - Expected validation: command prints `True`.
  - Error recovery: if it prints `False`, stop and inspect `docs/reference/opencode-configuration.md` lines 7-24 before editing anything; do not create a new config file.

- [x] 0.2 Confirm there is no project-level OpenCode config in the repository root that would override the global config.
  - Command:
    ```powershell
    Test-Path "C:\development\opencode\opencode.jsonc"; Test-Path "C:\development\opencode\opencode.json"
    ```
  - Expected validation: both commands print `False`.
  - Error recovery: if either prints `True`, stop and compare against `docs/reference/opencode-configuration.md` because config precedence may have changed.

- [x] 0.3 Confirm the target plugin is currently present in the active config.
  - Command:
    ```powershell
    Select-String -Path "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Pattern '@franlol/opencode-md-table-formatter@0\.0\.3'
    ```
  - Expected validation: output includes a line from `opencode.jsonc` containing `@franlol/opencode-md-table-formatter@0.0.3`.
  - Error recovery: if no match appears, skip Phase 1.1, still run Phase 2 documentation checks, and mark the plugin already disabled.

- [x] 0.4 Create a timestamped backup of the active config.
  - Command:
    ```powershell
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'; Copy-Item "$env:USERPROFILE\.config\opencode\opencode.jsonc" "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-disable-md-table-formatter-$stamp"; Write-Output "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-disable-md-table-formatter-$stamp"
    ```
  - Expected validation: command prints a path ending in `opencode.jsonc.backup-disable-md-table-formatter-<timestamp>`.
  - Error recovery: if copy fails with access denied, close running editors/OpenCode instances and retry; if it still fails due to permissions, ask the user to approve the equivalent `gsudo powershell -Command "Copy-Item ..."` command.

- [x] 0.5 Verify the backup file exists and contains the target plugin string.
  - Command:
    ```powershell
    $backup = Get-ChildItem "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-disable-md-table-formatter-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Test-Path $backup.FullName; Select-String -Path $backup.FullName -Pattern '@franlol/opencode-md-table-formatter@0\.0\.3'
    ```
  - Expected validation: first output is `True`; second output includes the plugin string.
  - Error recovery: if the backup exists but does not contain the string, delete only that just-created invalid backup and repeat task 0.4 after reconfirming task 0.3.

Phase-level exit criteria: active config path is confirmed, project override absence is confirmed, the target plugin state is known, and a valid rollback backup exists before implementation.

## Phase 1: Implementation — Disable the Plugin in Active Config

Objective: Remove exactly one plugin entry from the global OpenCode `plugin` array without changing unrelated settings.

- [x] 1.1 Remove only the exact `@franlol/opencode-md-table-formatter@0.0.3` entry from `C:/Users/DaveWitkin/.config/opencode/opencode.jsonc`.
  - Required edit: change this snippet:
    ```jsonc
        "opencode-mystatus",
        "@franlol/opencode-md-table-formatter@0.0.3",
        "@tarquinen/opencode-dcp@latest"
    ```
    to this snippet:
    ```jsonc
        "opencode-mystatus",
        "@tarquinen/opencode-dcp@latest"
    ```
  - Command option for a build agent using PowerShell:
    ```powershell
    $path = "$env:USERPROFILE\.config\opencode\opencode.jsonc"; $text = Get-Content $path -Raw; $old = "    \"@franlol/opencode-md-table-formatter@0.0.3\",`r`n"; if (-not $text.Contains($old)) { $old = "    \"@franlol/opencode-md-table-formatter@0.0.3\",`n" }; if (-not $text.Contains($old)) { throw "Target plugin line not found exactly; stop and edit manually." }; $text = $text.Replace($old, ""); Set-Content -Path $path -Value $text -NoNewline
    ```
  - Expected validation: command completes with no output and no exception.
  - Error recovery: if `Target plugin line not found exactly` appears, do not run a broad regex replacement; open the first 15 lines of the file and manually remove only the exact plugin array entry.

- [x] 1.2 Verify the target plugin string is absent from the active config.
  - Command:
    ```powershell
    if (Select-String -Path "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Pattern '@franlol/opencode-md-table-formatter@0\.0\.3' -Quiet) { throw 'Plugin still present' } else { 'Plugin disabled in active config' }
    ```
  - Expected validation: output is `Plugin disabled in active config`.
  - Error recovery: if `Plugin still present` appears, repeat task 1.1 using a manual single-line edit only.

- [x] 1.3 Validate OpenCode can parse the edited config.
  - Command:
    ```powershell
    opencode debug config 2>$null | Select-String -Pattern '"plugin"|md-table-formatter'
    ```
  - Expected validation: command exits successfully; no parse error appears; `md-table-formatter` does not appear.
  - Error recovery: if `opencode` is not recognized, run `where.exe opencode`; if missing, validate JSONC syntax with `node -e "const fs=require('fs'); const {parse}=require('jsonc-parser'); const p=process.env.USERPROFILE+'/.config/opencode/opencode.jsonc'; parse(fs.readFileSync(p,'utf8')); console.log('jsonc parse ok')"` from `C:/Users/DaveWitkin/.config/opencode`; if parse fails, restore the backup from Phase 0.4.

- [x] 1.4 Confirm no package removal is required from `C:/Users/DaveWitkin/.config/opencode/package.json`.
  - Command:
    ```powershell
    Select-String -Path "$env:USERPROFILE\.config\opencode\package.json" -Pattern '@franlol/opencode-md-table-formatter|md-table-formatter' -Quiet
    ```
  - Expected validation: command prints `False` or produces no truthy output when run interactively.
  - Error recovery: if it prints `True`, stop and ask for approval before uninstalling or editing package files; package removal is not part of this track unless independently discovered and approved.

Phase-level exit criteria: active config no longer references the markdown table formatter plugin, config parsing succeeds, and no package cleanup is needed without further approval.

## Phase 2: Implementation — Update Repository Documentation

Objective: Align repo documentation with the new active OpenCode plugin set.

- [x] 2.1 Update `docs/reference/opencode-configuration.md` line 36 summary from `Plugins: 7 plugins ... md-table-formatter ...` to a 6-plugin summary without the table formatter.
  - Required replacement example:
    ```markdown
    - **Plugins:** 6 plugins (snippets, skillful, multi-auth, ignore, mystatus, dcp)
    ```
  - Command:
    ```powershell
    Select-String -Path "C:\development\opencode\docs\reference\opencode-configuration.md" -Pattern 'Plugins:'
    ```
  - Expected validation after edit: plugin summary says `6 plugins` and does not include `md-table-formatter`.
  - Error recovery: if the line has drifted, edit only the bullet under `## Active Config Files` > `opencode.jsonc (Main)`; do not rewrite unrelated documentation sections.

- [x] 2.2 Remove the active-plugin bullet for `@franlol/opencode-md-table-formatter@0.0.3` from `docs/reference/opencode-configuration.md`.
  - Required deletion:
    ```markdown
      - `@franlol/opencode-md-table-formatter@0.0.3` — Markdown table formatting
    ```
  - Command:
    ```powershell
    Select-String -Path "C:\development\opencode\docs\reference\opencode-configuration.md" -Pattern 'md-table-formatter|Markdown table formatting'
    ```
  - Expected validation after edit: no match appears in the active plugin list.
  - Error recovery: if the string appears only in historical notes, do not delete history; update wording to make clear it is retired, not active.

- [x] 2.3 Verify the plugin count documentation matches the active config count.
  - Command:
    ```powershell
    $cfg = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw; $pluginCount = ([regex]::Matches($cfg, '"(?:opencode-|@zenobius/|oc-|@tarquinen/)')).Count; Select-String -Path "C:\development\opencode\docs\reference\opencode-configuration.md" -Pattern 'Plugins:\*\* 6 plugins'; Write-Output "approx_plugin_token_count=$pluginCount"
    ```
  - Expected validation: documentation match appears and approximate token count is `6`.
  - Error recovery: if count is not 6, manually inspect only the top `plugin` array in `opencode.jsonc` and reconcile the documentation to that array.

Phase-level exit criteria: repository reference documentation no longer describes the markdown table formatter as an active OpenCode plugin and reflects six active plugins.

## Final Phase: Validation & Handover

Objective: Prove the change is safe, record rollback steps, and prepare a concise handover for the user or next agent.

- [x] 3.1 Run final active config absence check.
  - Command:
    ```powershell
    Select-String -Path "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Pattern '@franlol/opencode-md-table-formatter|md-table-formatter'
    ```
  - Expected validation: no output.
  - Error recovery: if output appears in the active config, return to Phase 1.1.

- [x] 3.2 Run final OpenCode config parse check.
  - Command:
    ```powershell
    opencode debug config 2>$null | Select-String -Pattern 'md-table-formatter|error|Error'
    ```
  - Expected validation: no `md-table-formatter` output and no error output.
  - Error recovery: if parse errors appear, restore the latest backup with the rollback command in task 3.4 and re-run this check.

- [x] 3.3 Run final documentation check.
  - Command:
    ```powershell
    Select-String -Path "C:\development\opencode\docs\reference\opencode-configuration.md" -Pattern 'md-table-formatter|Markdown table formatting|Plugins:\*\* 7 plugins'
    ```
  - Expected validation: no output.
  - Error recovery: if output appears in an active-config section, update that section; if output appears in a historical note, ensure wording explicitly says retired/previously active.

- [x] 3.4 Record rollback command in the handover note or final response.
  - Command to record:
    ```powershell
    $latest = Get-ChildItem "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-disable-md-table-formatter-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Copy-Item $latest.FullName "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Force; opencode debug config 2>$null | Select-String -Pattern 'md-table-formatter|error|Error'
    ```
  - Expected validation: handover includes the exact rollback command and backup naming pattern.
  - Error recovery: if no backup exists, do not claim rollback is available; go back to Phase 0.4 before making any further edits.

- [x] 3.5 Update Conductor metadata for `.conductor/tracks/20260502-disable-md-table-formatter-plugin/metadata.json` after execution.
  - Required fields after successful execution:
    ```json
    {
      "status": "completed",
      "phase": "complete",
      "progress": {
        "totalTasks": 17,
        "completedTasks": 17,
        "percentage": 100
      }
    }
    ```
  - Expected validation: metadata status and progress reflect actual task completion.
  - Error recovery: if execution stops early, set `status` to `blocked` or `active`, keep incomplete tasks unchecked, and record the blocker in `blocking`.

Phase-level exit criteria: active config and docs pass final checks, rollback is documented, and Conductor reflects execution status.

## Execution Readiness Checklist

- [x] Atomic tasks — each checkbox contains one clear action.
- [x] Exact file paths — every task names precise full paths or repo-relative documentation paths.
- [x] Explicit commands — each task includes verbatim PowerShell commands.
- [x] Clear ordering — phases and tasks are ordered by prerequisite dependency.
- [x] Verification per step — each task includes expected validation output.
- [x] No assumed context — target config path, docs path, and plugin string are embedded in the plan.
- [x] Concrete examples — exact before/after config snippets are included.
- [x] Error recovery — every task includes fallback or stop conditions.

## Top 3 Implementation Risks + Mitigations

1. Risk: Removing the wrong plugin or corrupting JSONC syntax.
   - Mitigation: create a timestamped backup first, remove only the exact line, and run `opencode debug config` immediately after the edit.
2. Risk: Documentation says the plugin is disabled while a higher-precedence config still enables it.
   - Mitigation: Phase 0.2 explicitly checks for project-level `opencode.jsonc` and `opencode.json` before editing.
3. Risk: OpenCode CLI is unavailable in the build agent shell.
   - Mitigation: use `where.exe opencode` for diagnosis and `jsonc-parser` from the config directory as a syntax-validation fallback.

## First Task the Build Agent Should Execute Immediately

Execute Phase 0 task 0.1:

```powershell
Test-Path "$env:USERPROFILE\.config\opencode\opencode.jsonc"
```

Expected output: `True`.
