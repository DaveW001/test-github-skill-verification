# OpenCode Desktop Performance: Skillful Isolation Plan

## Phase 0: Setup & Preconditions

Objective: Preserve the current working setup and establish a clean baseline before changing lazy skill discovery.

- [x] 0.1 Confirm the working directory exists.
  - Command: `Test-Path "C:\development\opencode"`
  - Expected output: `True`
  - Recovery: If output is `False`, stop and ask the user for the correct OpenCode repo path.

- [x] 0.2 Confirm the global OpenCode config exists.
  - Command: `Test-Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"`
  - Expected output: `True`
  - Recovery: If output is `False`, stop; do not create a new config file.

- [x] 0.3 Confirm the lazy skill config exists.
  - Command: `Test-Path "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json"`
  - Expected output: `True`
  - Recovery: If output is `False`, skip Skillful config inspection and record the missing file in `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md`.

- [x] 0.4 Create a timestamped backup folder.
  - Command: `$stamp = Get-Date -Format "yyyyMMdd-HHmmss"; New-Item -ItemType Directory -Force "C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\artifacts\$stamp" | Select-Object -ExpandProperty FullName`
  - Expected output: a path under `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\artifacts\`.
  - Recovery: If directory creation fails, stop and check write permissions under `C:\development\opencode`.

- [x] 0.5 Back up `opencode.jsonc`.
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Copy-Item "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" "$($latest.FullName)\opencode.jsonc.before-skillful-isolation"`
  - Expected output: no error; backup file exists.
  - Verify: `Test-Path "$($latest.FullName)\opencode.jsonc.before-skillful-isolation"` returns `True`.
  - Recovery: If copy fails, stop before editing config.

- [x] 0.6 Back up `.opencode-skillful.json`.
  - Command: `$latest = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\artifacts" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1; Copy-Item "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json" "$($latest.FullName)\.opencode-skillful.json.before-skillful-isolation"`
  - Expected output: no error; backup file exists.
  - Verify: `Test-Path "$($latest.FullName)\.opencode-skillful.json.before-skillful-isolation"` returns `True`.
  - Recovery: If the source file is missing, record that and continue to Phase 1.

- [x] 0.7 Record the current OpenCode CLI version.
  - Command: `opencode --version`
  - Expected output: a version string, for example `1.14.29`.
  - Recovery: If `opencode` is not found, record the failure and continue with Desktop-only validation.

Exit criteria: Required paths exist, backups are created, and the CLI version result is recorded.

## Phase 1: Validate MCP Disablement

Objective: Confirm the immediate MCP change removed the known prompt-discovery errors without breaking config parsing.

- [x] 1.1 Confirm all configured MCPs are disabled.
  - Command: `rg -n '"enabled": false|"control-chrome"|"slack"|"playwright"' "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"`
  - Expected output: `playwright`, `control-chrome`, and `slack` each appear near an `"enabled": false` entry.
  - Recovery: If any of the three MCPs is missing `"enabled": false`, edit only that MCP block in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` and add `"enabled": false`.

- [x] 1.2 Validate the effective OpenCode config parses.
  - Command: `opencode debug config`
  - Expected output: JSON-like effective config with no parse error; `mcp.playwright.enabled`, `mcp.control-chrome.enabled`, and `mcp.slack.enabled` are `false`.
  - Recovery: If parsing fails, restore `opencode.jsonc` from the Phase 0 backup and stop.

- [x] 1.3 Fully quit OpenCode Desktop.
  - Command: `Get-Process OpenCode -ErrorAction SilentlyContinue | Stop-Process`
  - Expected output: no error.
  - Recovery: If access is denied, close OpenCode Desktop manually and rerun `Get-Process OpenCode -ErrorAction SilentlyContinue`.

- [x] 1.4 Start OpenCode Desktop.
  - Command: `Start-Process "C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe"`
  - Expected output: OpenCode Desktop starts.
  - Recovery: If the path is missing, locate the executable with `Get-ChildItem "$env:LOCALAPPDATA\Programs" -Recurse -Filter "OpenCode.exe" -ErrorAction SilentlyContinue`.

- [x] 1.5 Capture the newest Desktop log path.
  - Command: `Get-ChildItem "C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 FullName,LastWriteTime,Length`
  - Expected output: one `.log` path with a recent timestamp.
  - Recovery: If no log exists, wait 30 seconds and rerun the command.

- [x] 1.6 Check the newest log for disabled-MCP success.
  - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; rg -n "MCP error -32601|clientName=slack|clientName=control-chrome|failed to get prompts" $log.FullName`
  - Expected output: no matches after the restart timestamp.
  - Recovery: If matches remain after the restart timestamp, verify `enabled: false` in the effective config and record the exact matching lines in `execution-log.md`.

Exit criteria: Desktop starts, config parses, and the newest log no longer shows active `slack` or `control-chrome` prompt errors.

## Phase 2: Inspect Lazy Skill Discovery Configuration

Objective: Understand the Skillful setup before changing it.

- [x] 2.1 Read the lazy skill config.
  - Command: `Get-Content "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json"`
  - Expected output includes:
    ```json
    {
      "debug": false,
      "basePaths": [
        "C:\\Users\\DaveWitkin\\.opencode-lazy-vault"
      ],
      "promptRenderer": "xml"
    }
    ```
  - Recovery: If JSON is invalid, restore from backup or recreate only the shown minimal structure.

- [x] 2.2 Confirm the lazy vault exists.
  - Command: `Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault"`
  - Expected output: `True`
  - Recovery: If output is `False`, Skillful cannot operate; skip to Phase 4 and test without Skillful.

- [x] 2.3 Count top-level lazy vault skills.
  - Command: `Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory | Measure-Object | Select-Object -ExpandProperty Count`
  - Expected output: approximately `59` or higher.
  - Recovery: If count is unexpectedly low, inspect whether the vault was moved or junctioned.

- [x] 2.4 Identify duplicate `SKILL.md` names across known roots.
  - Command: `$roots = @("C:\Users\DaveWitkin\.opencode-lazy-vault","C:\Users\DaveWitkin\.agents\skills","C:\Users\DaveWitkin\.config\opencode\skill","C:\Users\DaveWitkin\.config\opencode\skills","C:\development\marketing\.opencode\skills","C:\development\playground\.opencode\skills"); Get-ChildItem $roots -Recurse -Filter SKILL.md -ErrorAction SilentlyContinue | Group-Object { Split-Path $_.DirectoryName -Leaf } | Where-Object Count -gt 1 | Select-Object Count,Name`
  - Expected output: duplicate names matching warnings in Desktop logs, such as `git-push`, `osgrep`, `perplexity-search`, or `imagegen`.
  - Recovery: If the command errors on a missing path, remove only the missing path from `$roots` and rerun.

- [x] 2.5 Record the duplicate summary in the execution log.
  - File to modify: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md`
  - Required content template:
    ```markdown
    ## Duplicate Skill Roots
    - Date: 2026-05-19
    - Roots inspected: <list roots>
    - Duplicate skill names: <paste concise table or summary>
    - Interpretation: <one paragraph>
    ```
  - Verification: `rg -n "Duplicate Skill Roots|Duplicate skill names" "C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md"` returns matches.
  - Recovery: If the file does not exist, create it with a `# Execution Log` heading.

Exit criteria: Skillful config, lazy vault existence, skill count, and duplicate roots are documented.

## Phase 3: A/B Test Without Skillful

Objective: Temporarily disable only `@zenobius/opencode-skillful` and compare Desktop responsiveness and logs.

- [x] 3.1 Remove only `@zenobius/opencode-skillful` from the plugin array.
  - File to modify: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Required edit: change this plugin array:
    ```jsonc
    "plugin": [
      "@zenobius/opencode-skillful",
      "oc-codex-multi-auth",
      "opencode-ignore@1.1.0",
      "opencode-mystatus",
      "@tarquinen/opencode-dcp@latest"
    ],
    ```
    to:
    ```jsonc
    "plugin": [
      "oc-codex-multi-auth",
      "opencode-ignore@1.1.0",
      "opencode-mystatus",
      "@tarquinen/opencode-dcp@latest"
    ],
    ```
  - Verification: `rg -n '@zenobius/opencode-skillful' "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"` returns no matches.
  - Recovery: If editing fails, restore the Phase 0 backup and stop.

- [x] 3.2 Validate config after removing Skillful.
  - Command: `opencode debug config`
  - Expected output: config prints without parse errors; `plugin_origins` does not include `@zenobius/opencode-skillful`.
  - Recovery: If parsing fails, restore `opencode.jsonc` from the Phase 0 backup and stop.

- [x] 3.3 Restart Desktop after removing Skillful.
  - Command: `Get-Process OpenCode -ErrorAction SilentlyContinue | Stop-Process; Start-Sleep -Seconds 3; Start-Process "C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe"`
  - Expected output: OpenCode Desktop starts.
  - Recovery: If Desktop does not start, restore the Phase 0 backup and restart Desktop.

- [x] 3.4 Check the newest log for Skillful activity.
  - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; rg -n "OpencodeSkillful|SkillRegistryController|MaxListenersExceededWarning|duplicate skill name" $log.FullName`
  - Expected output: no `OpencodeSkillful` or `SkillRegistryController` matches after the restart timestamp.
  - Recovery: If matches remain, verify the effective config no longer includes the plugin and ensure Desktop was fully restarted.

- [x] 3.5 Run a GUI smoke test.
  - Manual action: In OpenCode Desktop, open a fresh chat and send `Reply with exactly: Skillful disabled smoke test passed`.
  - Expected result: A model replies with exactly `Skillful disabled smoke test passed`, and the UI remains responsive for at least 2 minutes.
  - Recovery: If the UI slows again, capture the newest log and continue to Phase 5 with a recommendation to investigate non-Skillful Desktop state or reinstall.

- [x] 3.6 Record A/B result in the execution log.
  - File to modify: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md`
  - Required content template:
    ```markdown
    ## Skillful Disabled A/B Result
    - Date: 2026-05-19
    - Config parse: pass/fail
    - Desktop startup: pass/fail
    - GUI smoke test: pass/fail
    - Log result: <no Skillful churn / Skillful churn remained>
    - User-perceived responsiveness: <better / unchanged / worse>
    ```
  - Verification: `rg -n "Skillful Disabled A/B Result" "C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md"` returns a match.
  - Recovery: If the log file cannot be written, save the same section under the newest artifact folder as `skillful-disabled-result.md`.

Exit criteria: Desktop behavior with Skillful disabled is validated and documented.

## Phase 4: Decide Keep, Reconfigure, Or Disable Skillful

Objective: Make a reversible recommendation based on the A/B result.

- [ ] 4.1 If Desktop is faster without Skillful, choose temporary disablement.
  - File to leave modified: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Expected state: `@zenobius/opencode-skillful` is absent from the plugin array.
  - Verification: `rg -n '@zenobius/opencode-skillful' "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"` returns no matches.
  - Recovery: If the user needs lazy skills immediately, restore the plugin and proceed to task 4.3 instead.

- [x] 4.2 If Desktop is unchanged without Skillful, restore Skillful.
  - File to modify: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Required edit: add `"@zenobius/opencode-skillful",` as the first item in the `plugin` array.
  - Verification: `opencode debug config` succeeds and `plugin_origins` includes `@zenobius/opencode-skillful`.
  - Recovery: If config parse fails, restore from Phase 0 backup.

- [ ] 4.3 If Skillful is kept, reduce duplicate native skill roots.
  - Manual decision required before editing: choose authoritative roots for always-on skills.
  - Candidate authoritative root: `C:\Users\DaveWitkin\.opencode-lazy-vault`
  - Do not delete or rename these paths without explicit user approval:
    - `C:\Users\DaveWitkin\.agents\skills`
    - `C:\Users\DaveWitkin\.config\opencode\skill`
    - `C:\Users\DaveWitkin\.config\opencode\skills`
  - Verification: A documented user decision exists in `execution-log.md`.
  - Recovery: If no decision is available, leave paths unchanged.

- [x] 4.4 Update the troubleshooting documentation.
  - File to modify: `C:\development\opencode\docs\troubleshooting\active\opencode-desktop-white-window-startup.md`
  - Required addition:
    ```markdown
    ## Performance Follow-Up: MCP And Skillful Isolation
    - On 2026-05-19, `control-chrome`, `slack`, and `playwright` MCPs were disabled during Desktop slowdown troubleshooting.
    - If Desktop slows after startup, inspect logs for `OpencodeSkillful`, `duplicate skill name`, `MCP error -32601`, and `MaxListenersExceededWarning`.
    - Use the conductor plan at `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\plan.md`.
    ```
  - Verification: `rg -n "Performance Follow-Up: MCP And Skillful Isolation" "C:\development\opencode\docs\troubleshooting\active\opencode-desktop-white-window-startup.md"` returns a match.
  - Recovery: If the file is missing, create `C:\development\opencode\docs\troubleshooting\active\opencode-desktop-performance-slowdown.md` with the same section.

Exit criteria: The recommendation is documented, and config state matches that recommendation.

## Final Phase: Validation & Handover

Objective: Confirm the final state is stable and hand off exact rollback instructions.

- [x] 5.1 Run final config validation.
  - Command: `opencode debug config`
  - Expected output: config prints without parse errors.
  - Recovery: If parsing fails, restore `opencode.jsonc` from the Phase 0 backup.

- [x] 5.2 Run a CLI model smoke test.
  - Command: `opencode run -m opencode-go/glm-5.1 "Reply with exactly: CLI performance smoke passed"`
  - Expected output: `CLI performance smoke passed`
  - Recovery: If provider auth fails, verify Windows user-level `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` exist without printing their values.

- [x] 5.3 Run a Desktop smoke test.
  - Manual action: Open Desktop, select `opencode-go/glm-5.1` or `opencode-go/deepseek-v4-pro`, and send `Reply with exactly: Desktop performance smoke passed`.
  - Expected result: response returns, and the UI remains responsive for at least 2 minutes.
  - Recovery: If the UI freezes, capture the newest Desktop log and include it in `artifacts`.

- [x] 5.4 Capture the final log summary.
  - Command: `$log = Get-ChildItem "C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1; rg -n "OpencodeSkillful|MCP error -32601|MaxListenersExceededWarning|duplicate skill name|service=llm|ERROR|WARN" $log.FullName`
  - Expected output: no MCP prompt errors; Skillful-related lines only if Skillful was intentionally restored.
  - Recovery: If warnings remain, classify each warning as accepted, actionable, or unresolved in `execution-log.md`.

- [x] 5.5 Write the final handover note.
  - File to modify: `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md`
  - Required content template:
    ```markdown
    ## Final Handover
    - Final config state: <MCPs disabled, Skillful enabled/disabled>
    - Validation completed: <commands and GUI test>
    - Remaining warnings: <none/list>
    - Rollback: restore `opencode.jsonc` from `<backup path>`
    - Recommendation: <keep/reconfigure/disable Skillful; reinstall yes/no>
    ```
  - Verification: `rg -n "Final Handover|Final config state|Rollback" "C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md"` returns matches.
  - Recovery: If the execution log cannot be edited, write `final-handover.md` in the newest artifact folder.

Exit criteria: CLI and Desktop smoke tests pass, logs are summarized, and rollback instructions are documented.

## Execution Readiness Checklist

- [x] Atomic tasks: each checkbox contains one primary action.
- [x] Exact file paths: every file edit names a full path.
- [x] Explicit commands: every command task includes a verbatim PowerShell command.
- [x] Clear ordering: tasks proceed from backup to validation to isolation to handover.
- [x] Verification per step: every task includes expected output or a verification command.
- [x] No assumed context: paths, symptoms, and target files are fully specified.
- [x] Concrete examples: required JSONC and Markdown snippets are included.
- [x] Error recovery: each task includes fallback instructions.

## Top 3 Implementation Risks + Mitigations

1. Risk: Removing Skillful hides lazy-loaded skills the user relies on.
   - Mitigation: Make a timestamped backup first and document the one-line plugin restore step.

2. Risk: Duplicate skill folders are junctions, and deleting them could remove shared content.
   - Mitigation: Do not delete or rename skill roots in this plan; only inventory duplicates and require explicit user approval before root cleanup.

3. Risk: Desktop appears faster due to a fresh restart rather than Skillful disablement.
   - Mitigation: Compare logs after both MCP disablement and Skillful disablement, and require a 2-minute GUI responsiveness observation.

## First Task The Build Agent Should Execute Immediately

Run:

```powershell
Test-Path "C:\development\opencode"
```

Expected output:

```text
True
```
