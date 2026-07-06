# Plan: Codex Skill Architecture Repair and Automation Hardening

## Execution Rules

- Use PowerShell-first via bash if native tools fail with `Bun is not defined`.
- Do not kill OpenCode Desktop from the agent. If a quiet window is required, ask the user to close it manually or provide an external command for them to run.
- Back up before every removal.
- Remove junctions only with `cmd /c rmdir`. Never use PowerShell `Remove-Item` on a junction.
- Never create per-skill entries under `C:\Users\DaveWitkin\.codex\skills` while that root is a parent junction to the vault. Use `C:\Users\DaveWitkin\.opencode-lazy-vault\<name>` (the real path) instead.
- If a command resolves `C:\Users\DaveWitkin\.codex\skills\<name>`, remember this is an alias into the vault because of the parent junction. Mutating the alias mutates the vault.
- Each task must end with an explicit postcheck (the script or assertion object) before declaring success.

## Tasks

- [x] 1. Preflight and freeze assumptions.
  Run this PowerShell block (read-only) and write the JSON to `<track>/preflight-state.json`:

  ```powershell
  $vaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
  $codexRoot = 'C:\Users\DaveWitkin\.codex\skills'
  $nativeRoot = 'C:\Users\DaveWitkin\.config\opencode\skill'
  $pptxBackup = 'C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\2026-07-04-090412-pptx-repair\native\SKILL.md'

  $ci = Get-Item -LiteralPath $codexRoot
  $vi = Get-Item -LiteralPath $vaultRoot
  $ni = Get-Item -LiteralPath $nativeRoot

  $state = [pscustomobject]@{
      codexRoot         = $codexRoot
      codexIsReparse    = [bool]($ci.Attributes -band [IO.FileAttributes]::ReparsePoint)
      codexTarget       = $ci.Target
      codexTargetsVault = ($ci.Target -eq $vaultRoot)
      vaultRoot         = $vaultRoot
      vaultIsReparse    = [bool]($vi.Attributes -band [IO.FileAttributes]::ReparsePoint)
      nativeRoot        = $nativeRoot
      nativeIsReparse   = [bool]($ni.Attributes -band [IO.FileAttributes]::ReparsePoint)
      nlmSkill          = [pscustomobject]@{
          nativeExists  = (Test-Path -LiteralPath (Join-Path $nativeRoot 'nlm-skill'))
          vaultExists   = (Test-Path -LiteralPath (Join-Path $vaultRoot 'nlm-skill'))
          vaultHasSkill = (Test-Path -LiteralPath (Join-Path $vaultRoot 'nlm-skill\SKILL.md'))
          codexSeesSkill= (Test-Path -LiteralPath (Join-Path $codexRoot 'nlm-skill\SKILL.md'))
      }
      pptxBackupFile   = $pptxBackup
      pptxBackupExists = (Test-Path -LiteralPath $pptxBackup)
      pptxBackupSha    = if (Test-Path -LiteralPath $pptxBackup) { (Get-FileHash -LiteralPath $pptxBackup -Algorithm SHA256).Hash } else { $null }
      backupRootDir    = 'C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups'
      trackDir         = 'C:\development\opencode\.conductor\tracks\20260704-session-continuation-codex-skill-architecture-fix'
  }
  $state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $state.trackDir 'preflight-state.json') -Encoding utf8
  $state
  ```

  Acceptance:
  - `codexIsReparse` is `True`
  - `codexTargetsVault` is `True`
  - `nlmSkill.vaultHasSkill` and `nlmSkill.codexSeesSkill` are `True`
  - `pptxBackupExists` is `True`
  - `pptxBackupSha` is non-null and is recorded in `preflight-state.json`
  - If any of the above is false, STOP. Do not proceed to Task 2. Surface the preflight JSON in the chat.


- [x] 2. Repair `pptx-to-pdf-converter` vault entry.
  Required preconditions (must all be true from Task 1): `codexIsReparse`, `codexTargetsVault`, `pptxBackupExists`.

  Step 2.1 - Snapshot the existing self-referential junction metadata to a track-local backup so even if removal fails we have a record of the original target:
  ```powershell
  $vaultPptx = 'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter'
  $snapDir   = 'C:\development\opencode\.conductor\tracks\20260704-session-continuation-codex-skill-architecture-fix\backups\pptx-junction-snapshot'
  New-Item -ItemType Directory -Force -LiteralPath $snapDir | Out-Null
  $v = Get-Item -LiteralPath $vaultPptx
  [pscustomobject]@{
      Path = $v.FullName
      IsReparse = [bool]($v.Attributes -band [IO.FileAttributes]::ReparsePoint)
      Target = $v.Target
      CapturedAt = (Get-Date).ToString('o')
  } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $snapDir 'junction-metadata.json') -Encoding utf8
  ```

  Step 2.2 - Remove the junction with `cmd /c rmdir` (NEVER `Remove-Item` on a junction):
  ```powershell
  cmd /c rmdir "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter"
  if (Test-Path -LiteralPath $vaultPptx) { throw "Junction removal failed: $vaultPptx still exists" }
  ```

  Step 2.3 - Create a real directory and copy the backup CONTENTS (not the backup directory itself). The backup folder is `2026-07-04-090412-pptx-repair\native\` containing `SKILL.md` and `scripts\`. Use top-level enumeration so we copy children, not the parent dir:
  ```powershell
  $backupNative = 'C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\2026-07-04-090412-pptx-repair\native'
  New-Item -ItemType Directory -Force -LiteralPath $vaultPptx | Out-Null
  Get-ChildItem -LiteralPath $backupNative -Force | ForEach-Object {
      Copy-Item -LiteralPath $_.FullName -Destination $vaultPptx -Recurse -Force
  }
  ```

  Step 2.4 - Postchecks. ALL must be true:
  ```powershell
  $newV = Get-Item -LiteralPath $vaultPptx
  $pptxSkill = Join-Path $vaultPptx 'SKILL.md'
  $pptxScript= Join-Path $vaultPptx 'scripts\convert_pptx_to_pdf.py'
  $assert = [pscustomobject]@{
      VaultPathExists             = (Test-Path -LiteralPath $vaultPptx)
      VaultIsNotReparse           = -not [bool]($newV.Attributes -band [IO.FileAttributes]::ReparsePoint)
      VaultHasSkillMd             = (Test-Path -LiteralPath $pptxSkill)
      VaultHasConverterScript     = (Test-Path -LiteralPath $pptxScript)
      VaultSkillHashMatchesBackup = (Get-FileHash -LiteralPath $pptxSkill -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath (Join-Path $backupNative 'SKILL.md') -Algorithm SHA256).Hash
      CodexAliasSeesSkill         = (Test-Path -LiteralPath "C:\Users\DaveWitkin\.codex\skills\pptx-to-pdf-converter\SKILL.md")
      CodexAliasIsNotReparse      = -not [bool]((Get-Item -LiteralPath "C:\Users\DaveWitkin\.codex\skills\pptx-to-pdf-converter").Attributes -band [IO.FileAttributes]::ReparsePoint)
  }
  $assert
  ```
  If ANY field is `False` (or `$null`), STOP and surface the postcheck object. Do not proceed.

- [x] 3. Validate `nlm-skill` final state.
  Run:
  ```powershell
  $nlmVault  = 'C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill'
  $nlmNative = 'C:\Users\DaveWitkin\.config\opencode\skill\nlm-skill'
  $nlmCodex  = 'C:\Users\DaveWitkin\.codex\skills\nlm-skill'
  $assert = [pscustomobject]@{
      VaultExists           = (Test-Path -LiteralPath $nlmVault)
      VaultIsNotReparse     = -not [bool]((Get-Item -LiteralPath $nlmVault).Attributes -band [IO.FileAttributes]::ReparsePoint)
      VaultHasSkillMd       = (Test-Path -LiteralPath (Join-Path $nlmVault 'SKILL.md'))
      CodexAliasHasSkill    = (Test-Path -LiteralPath (Join-Path $nlmCodex 'SKILL.md'))
      CodexAliasIsNotReparse= -not [bool]((Get-Item -LiteralPath $nlmCodex).Attributes -band [IO.FileAttributes]::ReparsePoint)
      NativeAbsent          = -not (Test-Path -LiteralPath $nlmNative)
  }
  $assert
  ```
  Acceptance: all 6 fields must be `True`. If any is `False`, STOP.

  Do not create any per-skill entry under `C:\Users\DaveWitkin\.codex\skills\nlm-skill` because the Codex root is already a parent junction to the vault. Asserting `CodexAliasIsNotReparse = True` proves that no per-skill Codex child junction was created (a real folder has no ReparsePoint flag).

- [x] 4. Validate Codex visibility through the parent junction.
  Confirm the alias path sees the same real SKILL.md as the vault path, and confirm there is no per-skill Codex child reparse point:
  ```powershell
  $vaultSkillHash = (Get-FileHash -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill\SKILL.md' -Algorithm SHA256).Hash
  $codexSkillHash = (Get-FileHash -LiteralPath 'C:\Users\DaveWitkin\.codex\skills\nlm-skill\SKILL.md' -Algorithm SHA256).Hash
  $vaultPptxHash  = (Get-FileHash -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter\SKILL.md' -Algorithm SHA256).Hash
  $codexPptxHash  = (Get-FileHash -LiteralPath 'C:\Users\DaveWitkin\.codex\skills\pptx-to-pdf-converter\SKILL.md' -Algorithm SHA256).Hash
  $assert = [pscustomobject]@{
      NlmAliasesMatch     = ($vaultSkillHash -eq $codexSkillHash)
      PptxAliasesMatch    = ($vaultPptxHash -eq $codexPptxHash)
      NlmCodexNotReparse  = -not [bool]((Get-Item -LiteralPath 'C:\Users\DaveWitkin\.codex\skills\nlm-skill').Attributes -band [IO.FileAttributes]::ReparsePoint)
      PptxCodexNotReparse = -not [bool]((Get-Item -LiteralPath 'C:\Users\DaveWitkin\.codex\skills\pptx-to-pdf-converter').Attributes -band [IO.FileAttributes]::ReparsePoint)
  }
  $assert
  ```
  Acceptance: all 4 fields must be `True`. The "not reparse" assertions prove the Codex paths are real-folder aliases (vault contents) and NOT per-skill Codex child junctions.


- [x] 5. Detect and remediate any self-referential vault junctions.
  This task MUST cover BOTH `pptx-to-pdf-converter` AND `image-to-html-reconstruction`. The latter was discovered in this review and is NOT covered by the spec/plan as written; the previous session had no backup for it.

  Step 5a - Scan. List every reparse-point child of the vault whose target equals its own full path:
  ```powershell
  $vaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
  $selfrefs = @(Get-ChildItem -LiteralPath $vaultRoot -Directory -Force |
      Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } |
      ForEach-Object {
          $t = (Get-Item -LiteralPath $_.FullName).Target
          if ($t -eq $_.FullName) {
              [pscustomobject]@{ Name = $_.Name; Path = $_.FullName; Target = $t }
          }
      })
  $selfrefs | Format-Table -AutoSize
  $trackDir = 'C:\development\opencode\.conductor\tracks\20260704-session-continuation-codex-skill-architecture-fix'
  $selfrefs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $trackDir 'selfref-junctions.json') -Encoding utf8
  ```

  Step 5b - For each self-ref junction whose SKILL.md is recoverable from a known backup (pptx-to-pdf-converter is the only known case):
  - Verify a backup with SKILL.md exists under `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\<stamped-pptx-repair>\native\SKILL.md` (already confirmed in this review: 4671-byte file at the 090412 and 090431 paths).
  - Apply the same removal-and-restore sequence as Task 2, but parameterize on the skill name. Skip if Task 2 already remediated `pptx-to-pdf-converter`.

  Step 5c - For each self-ref junction whose SKILL.md is NOT in any known backup (`image-to-html-reconstruction` falls here):
  - Snapshot the junction metadata to `<track>/backups/<skill>-junction-snapshot/junction-metadata.json`.
  - Remove the self-referential junction with `cmd /c rmdir "<vault>\<skill>"` (safe - a self-referential junction resolves to itself, so the skill is functionally absent either way; removing the junction just makes the absence explicit).
  - Add a line to `<track>/backups/skills-not-restored.md` recording: skill name, the fact that no backup existed, the snapshot path, and the removal timestamp.
  - Do NOT create any replacement folder. The skill is documented as out-of-scope-for-restore.

  Acceptance:
  - `selfref-junctions.json` contains zero entries after Step 5a is re-run.
  - The vault has no child reparse point whose target equals its own path.
  - `skills-not-restored.md` exists and lists `image-to-html-reconstruction` (and any other no-backup self-refs discovered in 5a).
  - `pptx-to-pdf-converter` is now a real vault folder (covered by Task 2 if it runs first, or by 5b otherwise).

- [x] 6. Patch or disable the two flawed scripts.
  Both scripts currently treat `C:\Users\DaveWitkin\.codex\skills` as an independent parent and create/repoint children under it. Under the clarified architecture, `CodexRoot` is a parent junction to `VaultRoot`, so any `mklink /j` or `New-Item -ItemType Junction` under `CodexRoot` mutates the vault.

  Add the following preflight function to BOTH scripts, immediately after the existing helper functions and BEFORE any `New-Item`, `Remove-Item`, `cmd /c mklink`, or `cmd /c rmdir` calls:

  ```powershell
  function Assert-CodexRootIsNotParentJunction {
      param(
          [string]$CodexRoot,
          [string]$VaultRoot
      )
      if (-not (Test-Path -LiteralPath $CodexRoot)) { return }
      $it = Get-Item -LiteralPath $CodexRoot
      $isReparse = [bool]($it.Attributes -band [IO.FileAttributes]::ReparsePoint)
      if (-not $isReparse) { return }
      $target = $it.Target
      if ($target -is [array]) { $target = $target[0] }
      $normalizedTarget = ($target -replace '\\$','').Trim()
      $normalizedVault  = ($VaultRoot -replace '\\$','').Trim()
      if ($normalizedTarget -eq $normalizedVault) {
          throw "ABORT: CodexRoot is a parent junction to VaultRoot. Path '$CodexRoot' -> '$target'. This script must not create/repoint/delete children under CodexRoot. Manage canonical state under VaultRoot / NativeRoot instead."
      }
  }
  ```

  Call it once, near the top of the script body, after `$ErrorActionPreference='Stop'`:
  ```powershell
  Assert-CodexRootIsNotParentJunction -CodexRoot $CodexRoot -VaultRoot $VaultRoot
  ```

  Then remove (or comment-out with a clear deprecation note) every line that calls `NewJunction $codexPath <target>`, `New-Item -ItemType Junction -Path $codexPath ...`, `cmd /c mklink /j "$codexPath" ...`, `RemoveJunction $codexPath`, or `Remove-Item -LiteralPath $codexPath -Recurse -Force`. The Codex child layer is architecturally wrong and must be removed from these scripts.

  If the above patch is too invasive (e.g., would break the existing reports, the rollback flow, or the `Inventory` output), rename the script to `*.disabled.ps1` and add a top-of-file guard that throws with the same message as the function above.

  Files in scope:
  - `C:\development\_shared-scripts\codex-skill-migration-executor.ps1`
  - `C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1`

  Verification:
  - `Select-String -LiteralPath 'C:\development\_shared-scripts\codex-skill-migration-executor.ps1' -SimpleMatch 'mklink /j "$codexPath"'` returns zero matches.
  - `Select-String -LiteralPath 'C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1' -SimpleMatch 'mklink /j "$codexPath"'` returns zero matches.
  - `Select-String -LiteralPath 'C:\development\_shared-scripts\codex-skill-migration-executor.ps1' -SimpleMatch 'Assert-CodexRootIsNotParentJunction'` returns at least 1 match.
  - `Select-String -LiteralPath 'C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1' -SimpleMatch 'Assert-CodexRootIsNotParentJunction'` returns at least 1 match.
  - Run each script in dry-run mode (no `-Apply`) and confirm no `Apply=true` actions are emitted for any `Codex` child path. Specifically: `powershell -NoProfile -ExecutionPolicy Bypass -File C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1` and check the report JSON Actions array.


- [x] 7. Patch `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`.
  The root bug is in `Check 3: Junction Consistency`. The current text instructs the agent to create per-skill Codex child junctions:
  ```
  New-Item -ItemType Junction -Path "<codex-skills>\<name>" -Target "<canonical>\<name>" -Force
  ```
  Under the clarified architecture, `<codex-skills>` resolves through a parent junction to the vault, so this call would mutate the vault and can produce a self-referential junction.

  Replace Check 3 (Junction Consistency) in the validator with:
  ```
  ## Check 3: Junction Consistency

  Preflight: if `C:\Users\DaveWitkin\.codex\skills` is a reparse point whose target equals `C:\Users\DaveWitkin\.opencode-lazy-vault`, then `C:\Users\DaveWitkin\.codex\skills\<name>` is already an alias of the vault child. Do NOT create per-skill Codex child junctions - doing so mutates the vault and can produce self-referential junctions.

  Pseudocode (PowerShell):
  ```powershell
  $codexRoot = 'C:\Users\DaveWitkin\.codex\skills'
  $vaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
  $isCodexParentJunction = $false
  if (Test-Path -LiteralPath $codexRoot) {
      $ci = Get-Item -LiteralPath $codexRoot
      $ct = $ci.Target
      if ($ct -is [array]) { $ct = $ct[0] }
      $isCodexParentJunction = ([bool]($ci.Attributes -band [IO.FileAttributes]::ReparsePoint)) -and ($ct -eq $vaultRoot)
  }
  if ($isCodexParentJunction) {
      # Skip Codex child junction creation; the parent junction already exposes every vault child.
      # Do not emit any JUNCTION_CREATED|<name>|codex rows.
  } else {
      # Legacy path: Codex is a real directory, ensure a child junction per canonical skill.
      foreach ($name in $canonicalNames) {
          if (-not (Test-Path -LiteralPath (Join-Path $codexRoot $name))) {
              New-Item -ItemType Junction -Path (Join-Path $codexRoot $name) -Target (Join-Path $canonicalRoot $name) -Force
          }
      }
  }
  # Agents surface is independent of the Codex parent junction; existing agents logic is preserved.
  ```

  Update the "Action: AUTO-FIX" line to:
  **Action: AUTO-FIX (Codex surface) only when Codex is NOT a parent junction. Otherwise skip. Agents surface: unchanged.**
  ```

  Also: update the "Paths (constants)" section to add `Vault: C:\Users\DaveWitkin\.opencode-lazy-vault\` and the "Preflight" section to add:
  ```
  - Verify whether `C:\Users\DaveWitkin\.codex\skills` is a parent junction to the vault. If yes, set `$isCodexParentJunction=$true` and skip per-skill Codex child junction creation throughout the run.
  ```

  Verification (after editing):
  - `Select-String -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md' -SimpleMatch 'isCodexParentJunction'` returns >= 1 match.
  - `Select-String -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md' -SimpleMatch 'Do NOT create per-skill Codex child junctions'` returns >= 1 match.
  - `Select-String -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md' -SimpleMatch '-Path "<codex-skills>\<name>"'` returns zero matches (the old dangerous form is gone).

- [x] 8. Update documentation.
  Create or update the runbook `C:\development\opencode\docs\runbooks\codex-skill-architecture.md` (create the directory if it does not exist) with the following sections:

  - "Architecture (verified 2026-07-04)":
    - `C:\Users\DaveWitkin\.codex\skills` is a directory junction to `C:\Users\DaveWitkin\.opencode-lazy-vault`. The two paths are the SAME folder.
    - Lazy-loaded skills are real folders under `C:\Users\DaveWitkin\.opencode-lazy-vault\<skill>`.
    - A small always-on set stays under `C:\Users\DaveWitkin\.config\opencode\skill\<skill>` and is exposed in the vault as a per-skill junction.
    - The Codex root must NEVER have per-skill child junctions created under it directly, because that mutates the vault.

  - "Allowed operations":
    - Add a real folder to the vault: create `C:\Users\DaveWitkin\.opencode-lazy-vault\<name>\`.
    - Add an always-on skill: create the real folder under `C:\Users\DaveWitkin\.config\opencode\skill\<name>\`, then `cmd /c mklink /j "C:\Users\DaveWitkin\.opencode-lazy-vault\<name>" "C:\Users\DaveWitkin\.config\opencode\skill\<name>"`.
    - Remove a vault entry that is a junction: `cmd /c rmdir "<path>"` (NEVER `Remove-Item` on a junction).

  - "Forbidden operations":
    - `New-Item -ItemType Junction -Path "C:\Users\DaveWitkin\.codex\skills\<name>" ...`
    - `cmd /c mklink /j "C:\Users\DaveWitkin\.codex\skills\<name>" ...`
    - `Remove-Item` on any junction.

  - "What if I find a self-referential junction (target == own path)":
    1. Snapshot the junction metadata to a track backup folder.
    2. If a backup with SKILL.md exists in `C:\development\opencode\.conductor\tracks\<source-track>\backups\`, restore from it.
    3. Otherwise, remove the junction (`cmd /c rmdir`) and document the skill as not-restored.

  Mark the previously-written assumption that "Codex is a normal skills directory" as stale.

  Also: add a one-line note to `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md` referencing this runbook (e.g., `See C:\development\opencode\docs\runbooks\codex-skill-architecture.md for the architecture this validator must respect.`).

  Verification:
  - `Test-Path -LiteralPath 'C:\development\opencode\docs\runbooks\codex-skill-architecture.md'` returns True.
  - `Select-String -LiteralPath 'C:\development\opencode\docs\runbooks\codex-skill-architecture.md' -SimpleMatch 'parent junction'` returns >= 1 match.


- [x] 9. Final validation and closeout.
  Step 9.1 - Re-run the three spec validation blocks (Parent architecture, Target skills final state, Self-referential vault junction check) and write all three outputs to `<track>/validation-report-2026-07-04.md` as separate fenced code blocks. The preflight-state.json from Task 1 should be referenced.

  Step 9.2 - Add a final "Acceptance Criteria" section to the report. For each of the 9 spec acceptance criteria, mark `PASS` or `FAIL` with the exact line of evidence:
  1. Codex parent junction -> `codexIsReparse=True, codexTargetsVault=True`
  2. nlm-skill real vault folder with SKILL.md -> `nlmSkill.vaultHasSkill=True, nlmSkill.vaultIsNotReparse=True`
  3. pptx-to-pdf-converter real vault folder with SKILL.md -> from Task 2 postcheck
  4. nlm-skill/pptx-to-pdf-converter absent from native -> from Tasks 3 + 9 re-run
  5. Always-on native set -> from Task 9 spec check
  6. No self-ref junctions in vault -> from Task 5a
  7. Flawed scripts disabled/patched -> Task 6 verifications
  8. skill-health-validator.md updated -> Task 7 verifications
  9. Final validation report records commands, outputs, backups, deviations -> this report

  Step 9.3 - Update `metadata.json`:
  - Set `status` to one of: `complete`, `complete-with-followup`, `blocked`, based on the report.
  - If `complete-with-followup`, add a `followups` array enumerating each `image-to-html-reconstruction`-style skill that is documented in `<track>/backups/skills-not-restored.md`.
  - If `blocked`, add a `blockingReason` field.

  Step 9.4 - Append one CSV line to `C:\development\opencode\.conductor\tracks\ledgers\tracks-ledger.md` (create the directory and file if missing) in the format: `2026-07-04 | 20260704-session-continuation-codex-skill-architecture-fix | <status> | 9 tasks | <P>/<F> acceptance | <link to validation-report-2026-07-04.md>`.

  Acceptance: `Test-Path -LiteralPath '<track>/validation-report-2026-07-04.md'` returns True and the report contains the "Acceptance Criteria" section with all 9 entries marked.

## Handoff Prompt

Continue this work using the Conductor track at `C:\development\opencode\.conductor\tracks\20260704-session-continuation-codex-skill-architecture-fix`.

The first task is to repair `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter` from backup while preserving the discovered architecture that `C:\Users\DaveWitkin\.codex\skills` is a parent junction to `C:\Users\DaveWitkin\.opencode-lazy-vault`. The second self-referential junction `image-to-html-reconstruction` discovered during Stage 2 review has no backup anywhere and must be safely removed (junction only, no replacement folder) with documentation in `<track>/backups/skills-not-restored.md`.

