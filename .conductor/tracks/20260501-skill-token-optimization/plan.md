# Plan

This plan is written for a low-context executor. Do not infer paths. Use the exact paths and commands shown here.

## Phase 1 — Proof of Concept

- [x] Back up the OpenCode config file.
  - Source: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Backup: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.bak-20260501-skillful-poc`
  - Command:
    ```powershell
    Copy-Item "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.bak-20260501-skillful-poc"
    ```
  - Verify:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.bak-20260501-skillful-poc"
    ```
  - Expected result: `True`.

- [x] Add `@zenobius/opencode-skillful` to the plugin array.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Add this plugin entry to the existing `plugin` array, or create the array if it does not exist:
    ```jsonc
    "@zenobius/opencode-skillful"
    ```
  - Verify:
    ```powershell
    Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern "@zenobius/opencode-skillful"
    ```
  - Expected result: exactly one match.
  - Failure recovery:
    ```powershell
    Copy-Item "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.bak-20260501-skillful-poc" "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Force
    ```

- [x] Create the lazy skill vault directory.
  - Directory: `C:\Users\DaveWitkin\.config\opencode\lazy-skills`
  - Command:
    ```powershell
    New-Item -ItemType Directory -Force -Path "C:\Users\DaveWitkin\.config\opencode\lazy-skills"
    ```
  - Verify:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\lazy-skills"
    ```
  - Expected result: `True`.

- [x] Create the opencode-skillful config file.
  - File: `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json`
  - Exact contents:
    ```json
    {
      "debug": false,
      "basePaths": ["C:\\Users\\DaveWitkin\\.config\\opencode\\lazy-skills"],
      "promptRenderer": "xml",
      "modelRenderers": {}
    }
    ```
  - Verify:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json"
    Select-String -Path "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json" -Pattern "lazy-skills"
    ```
  - Expected result: first command returns `True`; second command returns one match.

- [x] Move two low-risk test skills to the lazy vault.
  - Test skill 1 source: `C:\Users\DaveWitkin\.config\opencode\skill\youtube-shorts`
  - Test skill 1 destination: `C:\Users\DaveWitkin\.config\opencode\lazy-skills\youtube-shorts`
  - Test skill 2 source: `C:\Users\DaveWitkin\.config\opencode\skill\terminal-aliases`
  - Test skill 2 destination: `C:\Users\DaveWitkin\.config\opencode\lazy-skills\terminal-aliases`
  - Commands:
    ```powershell
    Move-Item "C:\Users\DaveWitkin\.config\opencode\skill\youtube-shorts" "C:\Users\DaveWitkin\.config\opencode\lazy-skills\youtube-shorts"
    Move-Item "C:\Users\DaveWitkin\.config\opencode\skill\terminal-aliases" "C:\Users\DaveWitkin\.config\opencode\lazy-skills\terminal-aliases"
    ```
  - Verify:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\lazy-skills\youtube-shorts\SKILL.md"
    Test-Path "C:\Users\DaveWitkin\.config\opencode\lazy-skills\terminal-aliases\SKILL.md"
    Test-Path "C:\Users\DaveWitkin\.config\opencode\skill\youtube-shorts"
    Test-Path "C:\Users\DaveWitkin\.config\opencode\skill\terminal-aliases"
    ```
  - Expected result: first two commands return `True`; last two commands return `False`.
  - Failure recovery:
    ```powershell
    Move-Item "C:\Users\DaveWitkin\.config\opencode\lazy-skills\youtube-shorts" "C:\Users\DaveWitkin\.config\opencode\skill\youtube-shorts"
    Move-Item "C:\Users\DaveWitkin\.config\opencode\lazy-skills\terminal-aliases" "C:\Users\DaveWitkin\.config\opencode\skill\terminal-aliases"
    ```

- [ ] Start a new OpenCode session and validate the proof of concept.
  - Manual action: fully exit the current OpenCode process, then start a new OpenCode session from `C:\development\opencode`.
  - Verify plugin tools exist: `skill_find`, `skill_use`, and `skill_resource` appear in the available tools.
  - Run:
    ```text
    skill_find "youtube"
    skill_use "youtube-shorts"
    skill({ name: "conductor" })
    ```
  - Expected results:
    - `skill_find "youtube"` returns `youtube-shorts`.
    - `skill_use "youtube-shorts"` loads the `youtube-shorts` skill content.
    - `skill({ name: "conductor" })` loads native Conductor content.
    - `youtube-shorts` and `terminal-aliases` no longer appear in native `<available_skills>`.

## Phase 2 — Bulk Migration

- [x] Review the migration inventory before moving skills.
  - File: `C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\migration-inventory.md`
  - Verify the `Keep Native` section contains exactly:
    ```text
    conductor
    git-push
    osgrep
    perplexity-search
    ```
  - Verify the `Move To Lazy Vault` section contains all other skill directory names and does not contain `.osgrep`.

- [x] Back up current skill directories before bulk migration.
  - Backup destination: `C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501`
  - Commands:
    ```powershell
    New-Item -ItemType Directory -Force -Path "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501"
    Compress-Archive -Path "C:\Users\DaveWitkin\.config\opencode\skill" -DestinationPath "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\skill.zip" -Force
    Compress-Archive -Path "C:\Users\DaveWitkin\.config\opencode\skills" -DestinationPath "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\skills.zip" -Force
    Compress-Archive -Path "C:\Users\DaveWitkin\.agents\skills" -DestinationPath "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\agents-skills.zip" -Force
    ```
  - Verify:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\skill.zip"
    Test-Path "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\skills.zip"
    Test-Path "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\agents-skills.zip"
    ```
  - Expected result: all three commands return `True`.

- [x] Move every remaining skill listed under `Move To Lazy Vault` in `migration-inventory.md`.
  - Source root: `C:\Users\DaveWitkin\.config\opencode\skill`
  - Destination root: `C:\Users\DaveWitkin\.config\opencode\lazy-skills`
  - Do not move: `conductor`, `osgrep`, `git-push`, `perplexity-search`, or `.osgrep`.
  - For each listed skill `<skill-name>` that still exists in the source root, run:
    ```powershell
    Move-Item "C:\Users\DaveWitkin\.config\opencode\skill\<skill-name>" "C:\Users\DaveWitkin\.config\opencode\lazy-skills\<skill-name>"
    ```
  - If `<skill-name>` is already present in the lazy vault from Phase 1, do not move it again.
  - Verify each moved skill:
    ```powershell
    Test-Path "C:\Users\DaveWitkin\.config\opencode\lazy-skills\<skill-name>\SKILL.md"
    Test-Path "C:\Users\DaveWitkin\.config\opencode\skill\<skill-name>"
    ```
  - Expected result: vault `SKILL.md` returns `True`; source path returns `False`.

- [x] Verify every lazy-loaded skill has a `SKILL.md`.
  - Command:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\lazy-skills" -Directory | ForEach-Object {
      $skillFile = Join-Path $_.FullName "SKILL.md"
      if (-not (Test-Path $skillFile)) { Write-Error "Missing SKILL.md: $($_.FullName)" }
    }
    ```
  - Expected result: no errors.

- [x] Reduce the mirror directory to native skills only.
  - Directory: `C:\Users\DaveWitkin\.config\opencode\skills`
  - Keep only: `conductor`, `osgrep`, `git-push`, `perplexity-search`.
  - Command:
    ```powershell
    $keep = @("conductor", "osgrep", "git-push", "perplexity-search")
    Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skills" -Force | Where-Object { $keep -notcontains $_.Name } | Remove-Item -Recurse -Force
    ```
  - Verify:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skills" -Force | Select-Object -ExpandProperty Name
    ```
  - Expected result: only the 4 native skills are listed.

- [x] Reduce the agent skill symlink directory to native skills only.
  - Directory: `C:\Users\DaveWitkin\.agents\skills`
  - Keep only: `conductor`, `osgrep`, `git-push`, `perplexity-search`.
  - Command:
    ```powershell
    $keep = @("conductor", "osgrep", "git-push", "perplexity-search")
    Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Force | Where-Object { $keep -notcontains $_.Name } | Remove-Item -Recurse -Force
    ```
  - Verify remaining entries:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Force | Select-Object Name, LinkType, Target
    ```
  - Expected result: only the 4 native skill entries remain, and any symlink targets resolve.

- [x] Verify final directory state after bulk migration.
  - Native skill command:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skill" -Directory | Where-Object { $_.Name -ne ".osgrep" } | Select-Object -ExpandProperty Name | Sort-Object
    ```
  - Expected native result:
    ```text
    conductor
    git-push
    osgrep
    perplexity-search
    ```
  - Lazy count command:
    ```powershell
    (Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\lazy-skills" -Directory).Count
    ```
  - Expected result: count equals the number of skills in `migration-inventory.md` under `Move To Lazy Vault`.
  - Broken symlink check:
    ```powershell
    Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Force | ForEach-Object {
      if ($_.LinkType -and $_.Target -and -not (Test-Path $_.Target)) {
        Write-Error "Broken symlink: $($_.FullName) -> $($_.Target)"
      }
    }
    ```
  - Expected result: no errors.

## Phase 3 — Configuration and Documentation

- [x] Finalize `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json`.
  - Exact contents:
    ```json
    {
      "debug": false,
      "basePaths": ["C:\\Users\\DaveWitkin\\.config\\opencode\\lazy-skills"],
      "promptRenderer": "xml",
      "modelRenderers": {}
    }
    ```
  - Verify:
    ```powershell
    Select-String -Path "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json" -Pattern "C:\\\\Users\\\\DaveWitkin\\\\.config\\\\opencode\\\\lazy-skills"
    ```
  - Expected result: one match.

- [x] Verify `opencode.jsonc` contains the skillful plugin and do not make unrelated config edits.
  - File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - Command:
    ```powershell
    Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern "@zenobius/opencode-skillful"
    ```
  - Expected result: one match.
  - If a broken config path explicitly references a moved skill directory, document the exact before/after snippet in `C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\migration-notes.md` before editing.

- [x] Update global agent instructions with lazy skill usage.
  - File: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
  - Add this section near existing Skills guidance:
    ```md
    ### Lazy-Loaded Skills

    Most skills are stored outside native OpenCode skill scanning to reduce system prompt overhead.

    Always-available native skills:
    - `conductor`
    - `osgrep`
    - `git-push`
    - `perplexity-search`

    For any other skill, use the lazy-loading workflow:
    1. Search for the skill: `skill_find "<keyword>"`
    2. Load the selected skill: `skill_use "<skill-name>"`
    3. If the loaded skill references additional docs, use: `skill_resource "<resource-path>"`

    Example: for a meeting scheduling request, run `skill_find "calendar"`, then load the correct calendar skill with `skill_use`.
    ```
  - Verify:
    ```powershell
    Select-String -Path "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" -Pattern "Lazy-Loaded Skills"
    ```
  - Expected result: one match.

## Phase 4 — Validation and Measurement

- [ ] Start a fresh OpenCode session from repository root.
  - Working directory: `C:\development\opencode`
  - Manual action: close all existing OpenCode sessions, then open a new session in `C:\development\opencode`.
  - Verify: the new session starts without plugin/config errors and exposes `skill_find`, `skill_use`, and `skill_resource`.

- [x] Create validation results file.
  - File: `C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\validation-results.md`
  - Required skeleton:
    ```md
    # Validation Results

    ## Native Skills After Migration
    - conductor
    - git-push
    - osgrep
    - perplexity-search

    ## Token Reduction
    - Before: ~5,926 tokens
    - After: TBD
    - Reduction: TBD
    - Pass/Fail: TBD

    ## Native Skill Tests

    ## Lazy Skill Tests

    ## Resource Tests

    ## Edge Case Tests

    ## Backup Retention
    ```
  - Verify:
    ```powershell
    Test-Path "C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\validation-results.md"
    ```

- [ ] Measure native skill count and token reduction.
  - Inspect the fresh session `<available_skills>` block.
  - Expected native skills: `conductor`, `git-push`, `osgrep`, `perplexity-search`.
  - Expected absent examples: `calendar-today`, `email-draft-reply`, `thinking-partner`, `image-to-html-reconstruction`.
  - Record before/after token estimate in `validation-results.md`.
  - Pass condition: after estimate is less than `1,200` tokens and reduction is at least `80%`.

- [x] Test all 4 native skills load with the native `skill` tool.
  - Run:
    ```text
    skill({ name: "conductor" })
    skill({ name: "osgrep" })
    skill({ name: "git-push" })
    skill({ name: "perplexity-search" })
    ```
  - Expected result: each command returns corresponding skill content and none return “skill not found”.
  - Record pass/fail in `validation-results.md`.

- [ ] Test lazy skill discovery and loading for representative skills.
  - Run:
    ```text
    skill_find "calendar"
    skill_use "calendar-today"
    skill_find "clickup"
    skill_use "clickup-cli"
    skill_find "email"
    skill_use "email-draft-reply"
    skill_find "frontend"
    skill_use "frontend-design"
    skill_find "notebook"
    skill_use "notebooklm-cli"
    ```
  - Expected result: each `skill_find` returns relevant matches and each `skill_use` loads the named skill content.
  - Record pass/fail in `validation-results.md`.

- [ ] Test `skill_resource` with a lazy-loaded skill reference file.
  - Use a lazy-loaded skill that lists reference files, such as `notebooklm-cli` or `thinking-partner`.
  - Run `skill_resource` for one reference path shown by the loaded skill.
  - Expected result: referenced file content is returned without a path error.
  - Record exact skill name, resource path, and pass/fail in `validation-results.md`.

- [ ] Test lazy-loading error behavior.
  - Run:
    ```text
    skill_find "definitely-not-a-real-skill-xyz"
    skill_use "definitely-not-a-real-skill-xyz"
    skill_use "calendar-today"
    skill_use "clickup-cli"
    ```
  - Expected results:
    - Non-existent search returns no matches or a clear not-found message.
    - Non-existent load returns a clear error and does not crash the session.
    - Multiple valid `skill_use` calls succeed in the same session.
  - Record pass/fail in `validation-results.md`.

## Phase 5 — Cleanup and Rollback Prep

- [ ] Keep migration backup for at least 7 days after successful validation.
  - Backup directory: `C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501`
  - Do not delete this backup during initial migration.
  - Add backup location and earliest deletion date to `validation-results.md`.

- [ ] Verify rollback document exists.
  - File: `C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\rollback.md`
  - Verify:
    ```powershell
    Test-Path "C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\rollback.md"
    ```
  - Expected result: `True`.

- [ ] Update track metadata after validation passes.
  - File: `C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\metadata.json`
  - Set `status` to `completed` and `phase` to `complete` while preserving all other fields.
  - Verify:
    ```powershell
    Select-String -Path "C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\metadata.json" -Pattern '"status": "completed"'
    ```

- [ ] Update the Conductor tracks ledger.
  - File: `C:\development\opencode\.conductor\tracks-ledger.md`
  - Locate `20260501-skill-token-optimization`.
  - Change status from active/in-progress to completed.
  - Add completion note:
    ```text
    Completed skill token optimization migration using @zenobius/opencode-skillful; native skill prompt reduced to 4 core skills; lazy skills remain available through skill_find/skill_use.
    ```
  - Verify:
    ```powershell
    Select-String -Path "C:\development\opencode\.conductor\tracks-ledger.md" -Pattern "20260501-skill-token-optimization"
    ```

## Checkbox States

- [ ] Pending
- [~] In Progress
- [x] Completed

Important: `plan.md` is the authoritative source of truth for task progress.
