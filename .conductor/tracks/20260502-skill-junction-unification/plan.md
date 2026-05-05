# Plan — Skill Junction Unification

This plan is written for a **Build agent** with access to `bash` (PowerShell on Windows), `Read`, `Write`, `Edit`, `Grep`, `Glob`.
All commands are PowerShell. Junction creation requires NO elevation.

> **Safety rule for Windows junctions:** Do **not** use `Remove-Item -Recurse` to remove junctions. Use `cmd /c rmdir "<junction-path>"` for junction paths so the link is removed without deleting target contents.

---

## Restatement

**Goal:** Establish `~/.opencode-lazy-vault/` as the single source of truth for all 54 skills by bridging the 4 always-on skills into the vault via junctions, then replacing Codex's 54 individual junctions (49 broken) and `.agents`' 4 junctions with single parent-level junctions to the vault.

**Constraints / Non-goals:**
- Do NOT modify any skill content (SKILL.md, reference files, scripts)
- Do NOT set up Antigravity (out of scope)
- Do NOT move skills between always-on and lazy tiers
- Do NOT change the `@zenobius/opencode-skillful` plugin itself
- The 4 always-on skills MUST stay physically in `~/.config/opencode/skill/` for OpenCode native scanning

**Definition of done:**
1. `skill_find "*"` returns all 54 skills after OpenCode restart
2. All 54 skill directories resolve through `~/.codex/skills/`
3. All 54 skill directories resolve through `~/.agents/skills/`
4. Zero broken junctions remain
5. `~/.opencode-skillful.json` has both basePaths configured

---

## Phase 0 — Setup & Preconditions

**Objective:** Verify the filesystem is in the expected state before making changes.

- [ ] **0.1** Verify the lazy vault exists and has exactly 50 skill folders
  ```powershell
  if (-not (Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault")) { Write-Output "MISSING: C:\Users\DaveWitkin\.opencode-lazy-vault"; exit 1 }
  $count = (Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory).Count
  Write-Output "Lazy vault skill count: $count"
  ```
  Expected: `50`.
  If not 50, **STOP** and report the actual count and list all folder names:
  ```powershell
  (Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory).Name | Sort-Object
  ```

- [ ] **0.2** Verify the 4 always-on skills exist in `~/.config/opencode/skill/`
  ```powershell
  if (-not (Test-Path "C:\Users\DaveWitkin\.config\opencode\skill")) { Write-Output "MISSING: C:\Users\DaveWitkin\.config\opencode\skill"; exit 1 }
  $expected = @("conductor","git-push","osgrep","perplexity-search") | Sort-Object
  $actual = (Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skill" -Directory).Name | Sort-Object
  if (Compare-Object $expected $actual) { Write-Output "MISMATCH: $($actual -join ', ')" } else { Write-Output "PASS: 4 always-on skills confirmed" }
  ```
  Expected: `PASS: 4 always-on skills confirmed`.

- [ ] **0.3** Verify the 4 always-on skills do NOT already exist in the lazy vault
  ```powershell
  @("conductor","git-push","osgrep","perplexity-search") | ForEach-Object {
    $p = "C:\Users\DaveWitkin\.opencode-lazy-vault\$_"
    if (Test-Path $p) { Write-Output "CONFLICT: $_ already exists in vault" }
  }
  ```
  Expected: no output (no conflicts).
  If any conflicts exist, **STOP** — do not overwrite.

- [ ] **0.4** Verify Codex skills directory exists and has junctions
  ```powershell
  if (-not (Test-Path "C:\Users\DaveWitkin\.codex\skills")) { Write-Output "MISSING: C:\Users\DaveWitkin\.codex\skills"; exit 1 }
  $jCount = (cmd /c "dir C:\Users\DaveWitkin\.codex\skills\ /AL /B 2>nul").Count
  Write-Output "Codex junction count: $jCount"
  ```
  Expected: approximately 54.
  If directory doesn't exist, **STOP** and report.

- [ ] **0.5** Verify `.agents/skills/` directory exists
  ```powershell
  if (-not (Test-Path "C:\Users\DaveWitkin\.agents\skills")) { Write-Output "MISSING: C:\Users\DaveWitkin\.agents\skills"; exit 1 }
  Write-Output "PASS: C:\Users\DaveWitkin\.agents\skills exists"
  ```
  Expected: `PASS: C:\Users\DaveWitkin\.agents\skills exists`.

- [ ] **0.6** Read and record the current plugin config
  ```powershell
  Get-Content "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json"
  ```

- [ ] **0.7** Confirm Codex, `.agents`, and OpenCode processes are not running before junction replacement
  ```powershell
  $names = @("codex","antigravity","opencode")
  $running = Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName.ToLowerInvariant() }
  if ($running) { $running | Select-Object ProcessName,Id | Format-Table -AutoSize; Write-Output "STOP: Close these processes before continuing."; exit 1 }
  Write-Output "PASS: No codex/antigravity/opencode processes detected"
  ```
  Expected: `PASS: No codex/antigravity/opencode processes detected`.
  Record the output. Expected:
  ```json
  { "debug": false, "basePaths": ["C:\\Users\\DaveWitkin\\.opencode-lazy-vault"], "promptRenderer": "xml", "modelRenderers": {} }
  ```

**Phase 0 exit criteria:** All 7 checks pass. Skill counts match. No conflicts. Config recorded. No relevant processes are running.

---

## Phase 1 — Bridge Always-On Skills Into the Lazy Vault

**Objective:** Create junctions in the lazy vault that point to the 4 always-on skill directories in `~/.config/opencode/skill/`, so the vault becomes the complete set of all 54 skills.

- [ ] **1.1** Create junction: `lazy-vault/conductor` → `skill/conductor`
  ```powershell
  cmd /c "mklink /J `"C:\Users\DaveWitkin\.opencode-lazy-vault\conductor`" `"C:\Users\DaveWitkin\.config\opencode\skill\conductor`""
  ```
  Expected output: `Junction created for ...`.
  Verify:
  ```powershell
  Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\conductor\SKILL.md"
  ```
  Expected: `True`.

- [ ] **1.2** Create junction: `lazy-vault/git-push` → `skill/git-push`
  ```powershell
  cmd /c "mklink /J `"C:\Users\DaveWitkin\.opencode-lazy-vault\git-push`" `"C:\Users\DaveWitkin\.config\opencode\skill\git-push`""
  ```
  Expected: `Junction created for ...`.
  Verify: `Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\git-push\SKILL.md"` → `True`.

- [ ] **1.3** Create junction: `lazy-vault/osgrep` → `skill/osgrep`
  ```powershell
  cmd /c "mklink /J `"C:\Users\DaveWitkin\.opencode-lazy-vault\osgrep`" `"C:\Users\DaveWitkin\.config\opencode\skill\osgrep`""
  ```
  Expected: `Junction created for ...`.
  Verify: `Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\osgrep\SKILL.md"` → `True`.

- [ ] **1.4** Create junction: `lazy-vault/perplexity-search` → `skill/perplexity-search`
  ```powershell
  cmd /c "mklink /J `"C:\Users\DaveWitkin\.opencode-lazy-vault\perplexity-search`" `"C:\Users\DaveWitkin\.config\opencode\skill\perplexity-search`""
  ```
  Expected: `Junction created for ...`.
  Verify: `Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\perplexity-search\SKILL.md"` → `True`.

- [ ] **1.5** Verify the vault now has exactly 54 entries (50 real + 4 junctions)
  ```powershell
  $all = Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory
  Write-Output "Total vault entries: $($all.Count)"
  $junctions = $all | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }
  Write-Output "Junction entries: $($junctions.Count)"
  Write-Output "Junction names: $($junctions.Name -join ', ')"
  ```
  Expected: Total = 54, Junctions = 4, Junction names = `conductor, git-push, osgrep, perplexity-search`.

- [ ] **1.6** Verify all 54 entries resolve to a readable SKILL.md
  ```powershell
  $missing = Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory | Where-Object {
    -not (Test-Path "$($_.FullName)\SKILL.md")
  }
  if ($missing) { $missing | ForEach-Object { Write-Output "MISSING SKILL.md: $($_.Name)" } }
  else { Write-Output "PASS: All 54 entries have SKILL.md" }
  ```
  Expected: `PASS: All 54 entries have SKILL.md`.

**Phase 1 exit criteria:** Lazy vault has 54 entries. 4 are junctions pointing to `skill/`. All 54 resolve to valid SKILL.md files.

---

## Phase 2 — Update Plugin Config to Include Both basePaths

**Objective:** Add `~/.config/opencode/skill/` to the plugin's `basePaths` so `skill_find`/`skill_use` can discover the always-on skills as well as the vault skills.

- [ ] **2.1** Edit `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json`
  Current content:
  ```json
  { "debug": false, "basePaths": ["C:\\Users\\DaveWitkin\\.opencode-lazy-vault"], "promptRenderer": "xml", "modelRenderers": {} }
  ```
  Replace with:
  ```json
  {
    "debug": false,
    "basePaths": [
      "C:\\Users\\DaveWitkin\\.opencode-lazy-vault",
      "C:\\Users\\DaveWitkin\\.config\\opencode\\skill"
    ],
    "promptRenderer": "xml",
    "modelRenderers": {}
  }
  ```
  Use the Write tool to overwrite the file. Preserve exact JSON formatting.

- [ ] **2.2** Verify the new config
  ```powershell
  $cfg = Get-Content "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json" | ConvertFrom-Json
  Write-Output "basePaths count: $($cfg.basePaths.Count)"
  Write-Output "Path 1: $($cfg.basePaths[0])"
  Write-Output "Path 2: $($cfg.basePaths[1])"
  ```
  Expected:
  ```
  basePaths count: 2
  Path 1: C:\Users\DaveWitkin\.opencode-lazy-vault
  Path 2: C:\Users\DaveWitkin\.config\opencode\skill
  ```

**Phase 2 exit criteria:** Plugin config has 2 basePaths. JSON is valid.

---

## Phase 3 — Replace Codex Individual Junctions With Single Parent Junction

**Objective:** Remove all 54 individual skill junctions from `~/.codex/skills/`, then create one parent-level junction pointing to the lazy vault.

> ⚠️ **Order matters:** Must delete the directory AFTER removing junction contents, because the directory itself becomes a junction.

- [ ] **3.1** List and record all current Codex junctions (for rollback reference)
  ```powershell
  cmd /c "dir C:\Users\DaveWitkin\.codex\skills\ /AL /B 2>nul" > "$env:TEMP\codex-junction-names-backup.txt"
  Get-ChildItem "C:\Users\DaveWitkin\.codex\skills" -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } | ForEach-Object {
    [PSCustomObject]@{ Name = $_.Name; FullName = $_.FullName; Target = ($_.Target -join ';') }
  } | ConvertTo-Json -Depth 3 | Set-Content "$env:TEMP\codex-junction-targets-backup.json"
  Write-Output "Saved names to $env:TEMP\codex-junction-names-backup.txt"
  Write-Output "Saved targets to $env:TEMP\codex-junction-targets-backup.json"
  Get-Content "$env:TEMP\codex-junction-names-backup.txt"
  ```
  Expected: list of ~54 skill names and two backup files created. Save both files for rollback.

- [ ] **3.2** Remove only the individual junction links inside `C:\Users\DaveWitkin\.codex\skills\`
  ```powershell
  Get-ChildItem "C:\Users\DaveWitkin\.codex\skills" -Force | ForEach-Object {
    if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) {
      cmd /c "rmdir `"$($_.FullName)`""
    } else {
      Write-Output "NON-JUNCTION FOUND, NOT REMOVED: $($_.FullName)"
    }
  }
  ```
  Verify empty:
  ```powershell
  (Get-ChildItem "C:\Users\DaveWitkin\.codex\skills" -Force).Count
  ```
  Expected: `0`.

- [ ] **3.3** Remove the now-empty `~/.codex/skills/` directory itself
  ```powershell
  cmd /c "rmdir `"C:\Users\DaveWitkin\.codex\skills`""
  ```
  Verify removed:
  ```powershell
  Test-Path "C:\Users\DaveWitkin\.codex\skills"
  ```
  Expected: `False`.

- [ ] **3.4** Create single parent junction: `~/.codex/skills/` → `~/.opencode-lazy-vault/`
  ```powershell
  cmd /c "mklink /J `"C:\Users\DaveWitkin\.codex\skills`" `"C:\Users\DaveWitkin\.opencode-lazy-vault`""
  ```
  Expected: `Junction created for C:\Users\DaveWitkin\.codex\skills <<===>> C:\Users\DaveWitkin\.opencode-lazy-vault`.

- [ ] **3.5** Verify the junction resolves and all 54 skills are visible
  ```powershell
  $dirs = (Get-ChildItem "C:\Users\DaveWitkin\.codex\skills" -Directory).Name | Sort-Object
  Write-Output "Codex sees $($dirs.Count) skills"
  # Spot-check 4 always-on + 4 lazy
  @("conductor","git-push","osgrep","perplexity-search","outlook-email-search","calendar-today","image-generator","youtube-shorts") | ForEach-Object {
    if ($dirs -contains $_) { Write-Output "  OK: $_" } else { Write-Output "  MISSING: $_" }
  }
  ```
  Expected: `Codex sees 54 skills` and all 8 spot-checks show `OK`.

- [ ] **3.6** Verify junction attribute
  ```powershell
  $item = Get-Item "C:\Users\DaveWitkin\.codex\skills"
  $item.Attributes
  ```
  Expected: includes `ReparsePoint` or `Directory` with junction indicator.

**Phase 3 exit criteria:** `~/.codex/skills/` is a single junction to the vault. All 54 skills visible through it. Original junction backup saved.

---

## Phase 4 — Replace `.agents` Individual Junctions With Single Parent Junction

**Objective:** Same pattern as Phase 3 but for `~/.agents/skills/`.

- [ ] **4.1** Record current `.agents` junctions (for rollback)
  ```powershell
  cmd /c "dir C:\Users\DaveWitkin\.agents\skills\ /AL /B 2>nul" > "$env:TEMP\agents-junction-names-backup.txt"
  Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } | ForEach-Object {
    [PSCustomObject]@{ Name = $_.Name; FullName = $_.FullName; Target = ($_.Target -join ';') }
  } | ConvertTo-Json -Depth 3 | Set-Content "$env:TEMP\agents-junction-targets-backup.json"
  Write-Output "Saved names to $env:TEMP\agents-junction-names-backup.txt"
  Write-Output "Saved targets to $env:TEMP\agents-junction-targets-backup.json"
  Get-Content "$env:TEMP\agents-junction-names-backup.txt"
  ```
  Expected: `conductor`, `git-push`, `osgrep`, `perplexity-search` (4 entries).

- [ ] **4.2** Remove only the individual junction links inside `C:\Users\DaveWitkin\.agents\skills\`
  ```powershell
  Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Force | ForEach-Object {
    if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) {
      cmd /c "rmdir `"$($_.FullName)`""
    } else {
      Write-Output "NON-JUNCTION FOUND, NOT REMOVED: $($_.FullName)"
    }
  }
  (Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Force).Count
  ```
  Expected: `0`. If any `NON-JUNCTION FOUND` line appears, **STOP** and report it.

- [ ] **4.3** Remove the now-empty directory
  ```powershell
  cmd /c "rmdir `"C:\Users\DaveWitkin\.agents\skills`""
  Test-Path "C:\Users\DaveWitkin\.agents\skills"
  ```
  Expected: `False`.

- [ ] **4.4** Create single parent junction: `~/.agents/skills/` → `~/.opencode-lazy-vault/`
  ```powershell
  cmd /c "mklink /J `"C:\Users\DaveWitkin\.agents\skills`" `"C:\Users\DaveWitkin\.opencode-lazy-vault`""
  Test-Path "C:\Users\DaveWitkin\.agents\skills\conductor\SKILL.md"
  ```
  Expected: `Junction created for ...` and `True`.

- [ ] **4.5** Verify all 54 skills visible
  ```powershell
  $dirs = (Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Directory).Name | Sort-Object
  Write-Output ".agents sees $($dirs.Count) skills"
  ```
  Expected: `.agents sees 54 skills`.

**Phase 4 exit criteria:** `~/.agents/skills/` is a single junction to the vault. All 54 skills visible.

---

## Phase 5 — Update OpenCode System Prompt `available_skills` References

**Objective:** The OpenCode system prompt (in `opencode.jsonc`) references skill locations. Verify these references still resolve correctly after the junction changes.

- [ ] **5.1** Check that the `skills/` → `skill/` compatibility junction still works
  ```powershell
  Test-Path "C:\Users\DaveWitkin\.config\opencode\skills"
  ```
  Expected: `True` (the junction from `skills` → `skill` should still exist).

- [ ] **5.2** Verify the 4 always-on skills still resolve through the compatibility junction
  ```powershell
  @("conductor","git-push","osgrep","perplexity-search") | ForEach-Object {
    $ok = Test-Path "C:\Users\DaveWitkin\.config\opencode\skills\$_\SKILL.md"
    Write-Output "$_`: $ok"
  }
  ```
  Expected: all 4 show `True`.

- [ ] **5.3** Verify the always-on skills still resolve through the original `skill/` path
  ```powershell
  @("conductor","git-push","osgrep","perplexity-search") | ForEach-Object {
    $ok = Test-Path "C:\Users\DaveWitkin\.config\opencode\skill\$_\SKILL.md"
    Write-Output "$_`: $ok"
  }
  ```
  Expected: all 4 show `True`.

**Phase 5 exit criteria:** All skill resolution paths confirmed working.

---

## Phase 6 — Validation & Handover

**Objective:** Confirm the entire re-architecture works end-to-end. Run all checks before handing back to the user for OpenCode restart validation.

- [ ] **6.1** Comprehensive junction health check — zero broken junctions
  ```powershell
  $broken = @()
  Get-ChildItem "C:\Users\DaveWitkin\.codex\skills" -Directory | ForEach-Object {
    if (-not (Test-Path "$($_.FullName)\SKILL.md")) { $broken += $_.Name }
  }
  if ($broken.Count -eq 0) { Write-Output "PASS: Zero broken junctions in Codex" }
  else { Write-Output "BROKEN: $($broken -join ', ')" }
  ```
  Expected: `PASS: Zero broken junctions in Codex`.

- [ ] **6.2** Same check for `.agents`
  ```powershell
  $broken = @()
  Get-ChildItem "C:\Users\DaveWitkin\.agents\skills" -Directory | ForEach-Object {
    if (-not (Test-Path "$($_.FullName)\SKILL.md")) { $broken += $_.Name }
  }
  if ($broken.Count -eq 0) { Write-Output "PASS: Zero broken junctions in .agents" }
  else { Write-Output "BROKEN: $($broken -join ', ')" }
  ```
  Expected: `PASS: Zero broken junctions in .agents`.

- [ ] **6.3** Verify lazy vault complete set
  ```powershell
  $vaultCount = (Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory).Count
  Write-Output "Vault entries: $vaultCount"
  ```
  Expected: `54`.

- [ ] **6.4** Verify original always-on skills untouched
  ```powershell
  $skillCount = (Get-ChildItem "C:\Users\DaveWitkin\.config\opencode\skill" -Directory).Count
  Write-Output "Always-on skills: $skillCount"
  ```
  Expected: `4`. The originals must still be here.

- [ ] **6.5** Verify plugin config is valid JSON with 2 basePaths
  ```powershell
  try { $j = Get-Content "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json" | ConvertFrom-Json; Write-Output "JSON valid. basePaths: $($j.basePaths.Count)" } catch { Write-Output "INVALID JSON" }
  ```
  Expected: `JSON valid. basePaths: 2`.

- [ ] **6.6** Produce final state report
  ```powershell
  $brokenCodex = @()
  Get-ChildItem "C:\Users\DaveWitkin\.codex\skills" -Directory | ForEach-Object {
    if (-not (Test-Path "$($_.FullName)\SKILL.md")) { $brokenCodex += $_.Name }
  }
  Write-Output "========== SKILL JUNCTION UNIFICATION — STATE REPORT =========="
  Write-Output "Vault entries:           $((Get-ChildItem 'C:\Users\DaveWitkin\.opencode-lazy-vault' -Directory).Count)"
  Write-Output "Always-on in skill/:     $((Get-ChildItem 'C:\Users\DaveWitkin\.config\opencode\skill' -Directory).Count)"
  Write-Output "Codex skills visible:    $((Get-ChildItem 'C:\Users\DaveWitkin\.codex\skills' -Directory).Count)"
  Write-Output ".agents skills visible:  $((Get-ChildItem 'C:\Users\DaveWitkin\.agents\skills' -Directory).Count)"
  Write-Output "Codex is junction:       $((Get-Item 'C:\Users\DaveWitkin\.codex\skills').Attributes -match 'ReparsePoint')"
  Write-Output ".agents is junction:     $((Get-Item 'C:\Users\DaveWitkin\.agents\skills').Attributes -match 'ReparsePoint')"
  Write-Output "Plugin basePaths count:  $((Get-Content 'C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json' | ConvertFrom-Json).basePaths.Count)"
  Write-Output "Broken Codex junctions:  $($brokenCodex.Count)"
  Write-Output "==============================================================="
  ```
  Expected:
  ```
  Vault entries:           54
  Always-on in skill/:     4
  Codex skills visible:    54
  .agents skills visible:  54
  Codex is junction:       True
  .agents is junction:     True
  Plugin basePaths count:  2
  Broken Codex junctions:  0
  ```

- [ ] **6.7** Emit restart instruction for the user
  Output this message to the console (do not write to a file):
  ```
  ============================================================
  ACTION REQUIRED — RESTART OPENCODE
  The skill junction unification is complete:
  • ~/.codex/skills/ → junction → ~/.opencode-lazy-vault/ (54 skills)
  • ~/.agents/skills/ → junction → ~/.opencode-lazy-vault/ (54 skills)
  • 4 always-on skills bridged into vault via junctions
  • Plugin basePaths updated to include both locations
  
  1. Close ALL OpenCode windows and processes.
  2. Reopen OpenCode.
  3. Run: skill_find "*" — should return 54 skills.
  4. Verify <available_skills> still shows only 4 always-on skills.
  ============================================================
  ```

**Phase 6 exit criteria:** State report shows all green. Zero broken junctions. Restart instruction emitted.

---

## Rollback Procedure

If the changes must be reverted:

| Step | Command | Purpose |
|------|---------|---------|
| 1. Remove vault junctions | `cmd /c "rmdir \"C:\Users\DaveWitkin\.opencode-lazy-vault\conductor\""` (repeat for git-push, osgrep, perplexity-search) | Removes the 4 bridge junction links from vault without deleting their targets |
| 2. Revert plugin config | Restore original `.opencode-skillful.json` with single basePath | Plugin only scans vault again |
| 3. Restore Codex junctions | Delete parent junction with `cmd /c "rmdir \"C:\Users\DaveWitkin\.codex\skills\""`; recreate directory with `New-Item -ItemType Directory "C:\Users\DaveWitkin\.codex\skills"`; recreate individual junctions from `$env:TEMP\codex-junction-targets-backup.json` using `mklink /J` | Restores original 54 individual junctions |
| 4. Restore `.agents` junctions | Same pattern as step 3 using `$env:TEMP\agents-junction-targets-backup.json` | Restores original 4 individual junctions |

---

## Execution Readiness Checklist

| Standard | Status |
|----------|--------|
| 1. Atomic tasks (one action per checkbox) | ✅ Pass |
| 2. Exact file paths | ✅ Pass — all paths fully qualified |
| 3. Explicit commands | ✅ Pass — every task has verbatim PowerShell |
| 4. Clear ordering | ✅ Pass — phases 0→6, prerequisites first |
| 5. Verification per step | ✅ Pass — every task has expected output |
| 6. No assumed context | ✅ Pass — no prior session knowledge required |
| 7. Concrete examples | ✅ Pass — expected outputs shown inline |
| 8. Error recovery | ✅ Pass — STOP conditions and rollback procedure documented |

## Top 3 Implementation Risks + Mitigations

| # | Risk | Mitigation |
|---|------|-----------|
| 1 | Junction creation fails due to name collision (skill already exists in vault) | Phase 0.3 pre-checks for conflicts; STOP before any writes |
| 2 | Codex or `.agents` directory can't be deleted (locked by running process) | Ensure Codex and agents are not running during Phase 3/4; retry after closing |
| 3 | Plugin `basePaths` addition changes behavior unexpectedly (e.g., always-on skills appear twice in `skill_find`) | Phase 2.2 validates config; rollback step 2 reverts single basePath |

## First Task the Build Agent Should Execute Immediately

**Task 0.1** — Verify the lazy vault exists and has exactly 50 skill folders:
```powershell
$count = (Get-ChildItem "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory).Count
Write-Output "Lazy vault skill count: $count"
```
