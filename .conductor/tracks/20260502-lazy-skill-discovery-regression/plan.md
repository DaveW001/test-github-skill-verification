# Plan — Lazy Skill Discovery Regression

This plan is written for a **Build agent** (bash, Read, Write, Edit, Grep, Glob).
***Do not attempt `skill_find` or `skill_use`*** — these are OpenCode runtime tools unavailable to bash.
Phases 0—3 are Build-executable. Phase 4 is Planner/Human validation after OpenCode restart.

---

## Phase 0 — Config & Filesystem Baseline

- [x] 0.1 Confirm plugin entry exists in `opencode.jsonc`
  Execute:
  ```powershell
  Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern "@zenobius/opencode-skillful"
  ```
  Expected: exactly 1 match showing `"@zenobius/opencode-skillful"` (line near top of plugins array).

- [x] 0.2 Confirm `.opencode-skillful.json` config file exists
  Execute:
  ```powershell
  Test-Path "C:\Users\DaveWitkin\.config\opencode-skillful\.opencode-skillful.json"
  ```
  Expected: `True`.

- [x] 0.3 Read skillful config and confirm `basePaths`
  Execute:
  ```powershell
  Get-Content "C:\Users\DaveWitkin\.config\opencode-skillful\.opencode-skillful.json" | ConvertFrom-Json | Select-Object -ExpandProperty basePaths
  ```
  Expected output: `C:\Users\DaveWitkin\.opencode-lazy-vault`

- [x] 0.4 Confirm lazy vault directory exists and has ≥ 45 skill folders
  Execute:
  ```powershell
  (Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory).Count
  ```
  Expected: ≥ 45.

- [x] 0.5 Confirm the two critical Outlook skills exist in the lazy vault
  Execute:
  ```powershell
  Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\outlook-email-search\SKILL.md"
  Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\outlook-inbox-triage\SKILL.md"
  ```
  Expected: `True` for both.

- [x] 0.6 Confirm no project-level config shadows the global plugin config
  Execute:
  ```powershell
  Test-Path "C:\development\opencode\.opencode-skillful.json"
  ```
  Expected: `False` (should not exist — would shadow global config).

- [x] 0.7 Verify only 4 core skills are in native skill directories
  Execute:
  ```powershell
  $ok = @("conductor", "git-push", "osgrep", "perplexity-search")
  $a = (Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skill" -Directory).Name | Sort-Object
  $b = (Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skills" -Directory).Name | Sort-Object
  $agents = (Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Directory -ErrorAction SilentlyContinue).Name | Sort-Object
  Write-Output "skill/  : $($a -join ', ')"
  Write-Output "skills/ : $($b -join ', ')"
  Write-Output "agents/ : $($agents -join ', ')"
  ```
  Expected: all three directories contain only `conductor, git-push, osgrep, perplexity-search` (or are empty). If any lazy skill name (e.g., `outlook-email-search`, `calendar-today`) appears in these directories, a prior operation leaked skills back to the native location, defeating lazy loading. **STOP** and report the leaked skills before continuing.

  Failure recovery (if leaked skills found, move them to lazy vault):
  Do NOT move blindly. Report the leaked folder names and let the Planner decide.

- [x] 0.8 Confirm every lazy skill SKILL.md has `name:` and `description:` in frontmatter
  Execute:
  ```powershell
  Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault\*\SKILL.md" | ForEach-Object {
      $raw = Get-Content $_.FullName -Raw
      $hasName = $raw -match '(?ms)^---\n.*?^name:\s*\S+'
      $hasDesc = $raw -match '(?ms)^---\n.*?^description:\s*\S+'
      if (-not $hasName -or -not $hasDesc) {
          Write-Output "MISSING: $($_.Directory.Name)"
      }
  }
  ```
  Expected: no output (all skills have valid frontmatter with name + description). If any skills are flagged, **STOP** and report them.

**Phase 0 exit criteria:** All 8 checks pass. No leaked skills in native dirs. No missing frontmatter fields.

---

## Phase 1 — Plugin Installation Verification & Reinstall

- [x] 1.1 Check if the plugin is findable via npm (may be empty if OpenCode manages installation)
  Execute (run both independently):
  ```powershell
  npm ls @zenobius/opencode-skillful
  ```
  ```powershell
  npm list -g @zenobius/opencode-skillful --depth=0
  ```
  At the default working directory.
  Expected: Either a version is listed OR `(empty)` (both are acceptable — OpenCode installs plugins through its own mechanism).

- [x] 1.2 Check latest published version on npm
  Execute:
  ```powershell
  npm view @zenobius/opencode-skillful version
  ```
  Expected: a version string (e.g., `1.2.5`). Record this value.

- [x] 1.3 Reinstall the plugin globally to ensure latest clean install
  Execute (replace `<VERSION>` with the version from 1.2):
  ```powershell
  npm install -g @zenobius/opencode-skillful@<VERSION>
  ```
  If 1.1 already shows this version installed locally, skip this step.
  Verify:
  ```powershell
  npm list -g @zenobius/opencode-skillful --depth=0
  ```
  Expected: version `<VERSION>` listed.

- [x] 1.4 Check for npm installation errors
  Execute:
  ```powershell
  npm doctor
  ```
  Expected: no critical errors. If `npm doctor` fails, run `npm cache clean --force` and retry 1.3.

- [x] 1.5 Emit restart instruction block for the user
  Write the following to the console output (do not put in a file — output inline):
  ```
  ============================================================
  ACTION REQUIRED — RESTART OPENCODE
  The @zenobius/opencode-skillful plugin has been reinstalled.
  OpenCode must be fully restarted for the plugin to register.

  1. Close ALL OpenCode windows and processes.
  2. Reopen OpenCode in this workspace:
     C:\development\opencode
  3. After restart, the Planner agent will run the Phase 4
     validation checks below.
  ============================================================
  ```

**Phase 1 exit criteria:** Plugin reinstalled cleanly. Restart instruction emitted.

---

## Phase 2 — Documentation Fixes (Path Staleness)

The file `C:\development\opencode\docs\reference\lazy-loaded-skills.md` references the old vault path `lazy-skills` in 5 locations. The actual vault path is `.opencode-lazy-vault`. Fix all 5.

- [x] 2.1 Fix line 18 — Lazy Vault path in Key Directories section
  File: `C:\development\opencode\docs\reference\lazy-loaded-skills.md`
  Old: `* **Lazy Vault (\`C:\Users\DaveWitkin\.config\opencode\lazy-skills\`):**`
  New: `* **Lazy Vault (\`C:\Users\DaveWitkin\.opencode-lazy-vault\`):**`

- [x] 2.2 Fix line 31 — basePaths example in Configuration Files section
  File: `C:\development\opencode\docs\reference\lazy-loaded-skills.md`
  Old (lines 28-35):
  ```
    ```json
    {
      "debug": false,
      "basePaths": ["C:\\Users\\DaveWitkin\\.config\\opencode\\lazy-skills"],
      "promptRenderer": "xml",
      "modelRenderers": {}
    }
    ```
  ```
  New:
  ```
    ```json
    {
      "debug": false,
      "basePaths": ["C:\\Users\\DaveWitkin\\.opencode-lazy-vault"],
      "promptRenderer": "xml",
      "modelRenderers": {}
    }
    ```
  ```

- [x] 2.3 Fix line 62 — Troubleshooting table: System prompt row
  File: `C:\development\opencode\docs\reference\lazy-loaded-skills.md`
  Old: `instead of the \`lazy-skills\` vault. Move them to the lazy vault.`
  New: `instead of the \`.opencode-lazy-vault\` vault. Move them to the lazy vault.`

- [x] 2.4 Fix line 63 — Troubleshooting table: skill_find row
  File: `C:\development\opencode\docs\reference\lazy-loaded-skills.md`
  Old: `absolute Windows path for \`lazy-skills\` (with properly escaped backslashes).`
  New: `absolute Windows path for \`.opencode-lazy-vault\` (with properly escaped backslashes).`

- [x] 2.5 Fix line 71 — Rollback Procedure step 3
  File: `C:\development\opencode\docs\reference\lazy-loaded-skills.md`
  Old: `lazy-skills/`
  New: `.opencode-lazy-vault/`

- [x] 2.6 Verify zero remaining references to old path
  Execute:
  ```powershell
  Select-String -Path "C:\development\opencode\docs\reference\lazy-loaded-skills.md" -Pattern "lazy-skills"
  ```
  Expected: 0 matches (no output).

- [x] 2.7 If Phase 0.1—0.6 revealed any other stale-path references in the opencode workspace, fix them now
  Execute:
  ```powershell
  Select-String -Path "C:\development\opencode\docs" -Pattern "lazy-skills" -Recurse
  ```
  Expected: 0 matches across all docs after fixes above. If any remain, report them.

**Phase 2 exit criteria:** All references to `lazy-skills` replaced with `.opencode-lazy-vault`. Zero grep matches.

---

## Phase 3 — Guardrail Checks (Token-Optimization Preservation)

These checks confirm the lazy-load architecture is intact and skills haven't leaked back to native injection.

- [x] 3.1 Re-verify native skill directories still contain only 4 core skills
  Execute:
  ```powershell
  $ok = @("conductor", "git-push", "osgrep", "perplexity-search") | Sort-Object
  $a = (Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skill" -Directory).Name | Sort-Object
  if (($a -join ',') -ne ($ok -join ',')) { Write-Output "FAIL: skill/ has: $($a -join ', ')" } else { Write-Output "PASS" }
  ```
  ```powershell
  $ok = @("conductor", "git-push", "osgrep", "perplexity-search") | Sort-Object
  $b = (Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skills" -Directory).Name | Sort-Object
  if (($b -join ',') -ne ($ok -join ',')) { Write-Output "FAIL: skills/ has: $($b -join ', ')" } else { Write-Output "PASS" }
  ```
  Expected: `PASS` for both.

- [x] 3.2 Verify lazy vault still has ≥ 45 skill folders (no mass deletion)
- [x] 3.3 Verify `opencode.jsonc` plugin array still contains the plugin
- [x] 3.4 Verify `.opencode-skillful.json` basePath still correct
- [x] 3.5 Produce a final state report
  Execute:
  ```powershell
  Write-Output "=== STATE REPORT ==="
  Write-Output "Plugin in config: $(Select-String -Path 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc' -Pattern '@zenobius/opencode-skillful' -Quiet)"
  Write-Output "Skillful config exists: $(Test-Path 'C:\Users\DaveWitkin\.config\opencode-skillful\.opencode-skillful.json')"
  Write-Output "Lazy vault dirs: $((Get-ChildItem 'C:\Users\DaveWitkin\.opencode-lazy-vault' -Directory).Count)"
  Write-Output "Native skill/ dirs: $((Get-ChildItem 'C:\Users\DaveWitkin\.config\opencode\skill' -Directory).Name -join ', ')"
  Write-Output "Stale 'lazy-skills' refs in docs: $(Select-String -Path 'C:\development\opencode\docs\reference\lazy-loaded-skills.md' -Pattern 'lazy-skills' | Measure-Object | Select-Object -ExpandProperty Count)"
  Write-Output "npm plugin: $(npm list -g @zenobius/opencode-skillful --depth=0 2>&1)"
  Write-Output "===================="
  ```
  Expected: all values look healthy (True, ≥45, 4 core skills only, 0 stale refs, plugin version present).

**Phase 3 exit criteria:** All guardrail checks pass. State report shows healthy config.

---

## Phase 4 — Post-Restart Validation (Planner / Human)

> **⚠️ This phase is NOT executable by a Build agent.** The following checks require a live OpenCode session with `skill_find` and `skill_use` tools active. Execute these after fully restarting OpenCode.

- [x] 4.1 Restart OpenCode completely (close all windows, reopen in this workspace).
  **DONE** — Three restarts required total. Third restart (after config path fix) succeeded.

- [x] 4.2 In the restarted session, run each of these and record the output:
  ```
  skill_find "*"
  skill_find "outlook"
  skill_find "email"
  ```
  **RESULTS:**
  - `skill_find "*"` → 48 skills discovered (49 total, 1 rejected — microsoft-graph)
  - `skill_find "outlook"` → 6 matches (outlook_email_search, outlook_inbox_triage, calendar_schedule, calendar_today, email_draft_reply, unified_calendar_today)
  - `skill_find "email"` → 9 matches (email_auto_sorter, email_draft_reply, email_routing_config, email_to_clickup, outlook_email_search, gmail_draft_reply, gmail_inbox_triage, google_contacts, outlook_inbox_triage)

- [x] 4.3 Expected results:
  - `skill_find "*"` → ✅ 48 skills (was 4 before fix)
  - `skill_find "outlook"` → ✅ Returns outlook_email_search, outlook_inbox_triage, and related skills
  - `skill_find "email"` → ✅ Returns all email skills including outlook_email_search

- [x] 4.4 Verify individual skill loads:
  ```
  skill_use "outlook_email_search"
  skill_use "outlook_inbox_triage"
  ```
  **NOTE:** skill names use underscores in skill_use, NOT hyphens (the SKILL.md `name:` field normalizes to underscores).
  Both loaded successfully. ✅

- [x] 4.5 Verify token guardrail — check the system prompt at the next message:
  ✅ The `<available_skills>` block lists only 4 native core skills:
  - `conductor`, `git-push`, `osgrep`, `perplexity-search`
  Lazy skills appear only after `skill_use` loads them. Guardrail confirmed.

- [x] 4.6 If skill_find still shows only 4 skills, check OpenCode logs for plugin errors:
  **ROOT CAUSE FOUND:** Config was at `~/.config/opencode/.opencode-skillful.json` but the plugin's bunfig loader searches `~/.config/opencode-skillful/`, `~/.config/` directly, and `~/` — NOT `~/.config/opencode/`.
  **FIX:** Moved config to `C:\Users\DaveWitkin\.config\opencode-skillful\.opencode-skillful.json`.
  After restart with correct config location: 48 skills discovered.

- [x] 4.7 Update track metadata:
  Phase set to `"validation"`.
  Track marked complete.

**Additional fix:** microsoft-graph SKILL.md had no YAML frontmatter (was plain markdown). Added `name` and `description` fields. Takes effect on next restart (currently still 1 rejected).

**Phase 4 exit criteria:** All `skill_find` and `skill_use` checks pass. Token guardrail confirmed. Track status updated to complete.

---

## Rollback Procedure (if plugin must be removed)

If the plugin installation caused a regression and must be rolled back:

| Step | Command | Expected |
|------|---------|----------|
| 1. Revert plugin config | `npm uninstall -g @zenobius/opencode-skillful` | Plugin removed from global npm |
| 2. Delete skillful config | `Remove-Item "C:\Users\DaveWitkin\.config\opencode-skillful\.opencode-skillful.json"` | Config file deleted |
| 3. Remove plugin from opencode.jsonc | Edit `opencode.jsonc`, delete `"@zenobius/opencode-skillful"` from plugin array | Plugin entry removed |
| 4. Restart OpenCode | Close and reopen | System prompt should now show no leftover plugin errors |
