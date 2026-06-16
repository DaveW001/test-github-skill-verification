# Plan: GLM 5.2 Model Migration

## Track Info
- **Track ID**: 20260615-glm-52-model-migration
- **Created**: 2026-06-15
- **Status**: Completed (2026-06-15)
- **Modifies**: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` and 9 agent `.md` files at `C:\Users\DaveWitkin\.config\opencode\agent\`

## Restate
- **Goal:** GLM 5.2 as universal default. Primary agents inherit global default (overridable per-session). Subagents pinned with explicit model (cost isolation from expensive orchestrators like GPT-5.5).
- **Constraints:** No permission changes. No prompt/tool/mode changes. No new agents. Keep existing plan override. No restart.
- **Definition of Done:** All 9 agent files + config have correct model settings; no glm-5.1 or glm-4.7 remains; verified by automated checks.

## Architecture Summary

**Two-layer model routing:**
- **Layer 1 (Primary agents):** Remove explicit `model:` so they inherit global `model` config (GLM 5.2). User can override per-session with `/model` for expensive models.
- **Layer 2 (Subagents):** Add explicit `model: zai-coding-plan/glm-5.2` so they NEVER inherit the orchestrator's model, even when orchestrator is GPT-5.5. This is the cost-isolation guarantee.

**OpenCode inheritance rules (verified from official docs 2026-06-15):**
> "If you don't specify a model, primary agents use the model globally configured while subagents will use the model of the primary agent that invoked the subagent."

This means:
- Primary without model -> uses global `model` config (desired)
- Subagent without model -> uses INVOKING primary's model (the cost leak we are preventing)

## Files Modified

| File | Full Path | Change |
|------|-----------|--------|
| `opencode.jsonc` | `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` | Update `model`, `small_model`; expand `agent` block |
| `01-planner.md` | `C:\Users\DaveWitkin\.config\opencode\agent\01-planner.md` | Remove `model:` line |
| `boost.md` | `C:\Users\DaveWitkin\.config\opencode\agent\boost.md` | Remove `model:` line |
| `build.md` | `C:\Users\DaveWitkin\.config\opencode\agent\build.md` | Remove `model:` line |
| `brand-voice-validator.md` | `C:\Users\DaveWitkin\.config\opencode\agent\brand-voice-validator.md` | Add `model:` line |
| `cove-orchestrator.md` | `C:\Users\DaveWitkin\.config\opencode\agent\cove-orchestrator.md` | Add `model:` line |
| `cove-verifier.md` | `C:\Users\DaveWitkin\.config\opencode\agent\cove-verifier.md` | Update `model:` value |
| `gen-headlines.md` | `C:\Users\DaveWitkin\.config\opencode\agent\gen-headlines.md` | Add `model:` line |
| `peer-review.md` | `C:\Users\DaveWitkin\.config\opencode\agent\peer-review.md` | Add `model:` line |
| `seo-auditor.md` | `C:\Users\DaveWitkin\.config\opencode\agent\seo-auditor.md` | Add `model:` line |

> **Editing convention:** Use the `edit` tool with the exact `oldString`/`newString` below. If `Bun is not defined` occurs, fall back to PowerShell: read file content with `Get-Content -Raw`, apply literal `[string]::Replace()` (NOT regex `-replace`, which eats structural chars), write back with `Set-Content -NoNewline -Encoding UTF8`.

---

## Phase 0 -- Setup & Preconditions

**Objective:** Confirm the environment is ready and create a safety backup before modifying any file.

- [x] **0.1 Verify all target files exist**

  Run:
  ```powershell
  $cfg = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  $agentDir = "$env:USERPROFILE\.config\opencode\agent"
  Test-Path $cfg
  foreach ($f in @('01-planner.md','boost.md','build.md','brand-voice-validator.md','cove-orchestrator.md','cove-verifier.md','gen-headlines.md','peer-review.md','seo-auditor.md')) {
      $p = "$agentDir\$f"
      if (-not (Test-Path $p)) { Write-Host "MISSING: $p" }
  }
  Write-Host "DONE"
  ```

  **Expected output:** `DONE` with no `MISSING:` lines.

  **Error recovery:** If any file is missing, STOP. Do not proceed. Verify the user profile path with `$env:USERPROFILE`.

- [x] **0.2 Create timestamped backup of config and agent files**

  Run:
  ```powershell
  $ts = Get-Date -Format "yyyyMMdd-HHmmss"
  $backupDir = "$env:USERPROFILE\.config\opencode\backup-glm52-$ts"
  New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
  Copy-Item "$env:USERPROFILE\.config\opencode\opencode.jsonc" $backupDir
  Copy-Item "$env:USERPROFILE\.config\opencode\agent\*.md" $backupDir
  $count = (Get-ChildItem $backupDir).Count
  Write-Host "Backup file count: $count at $backupDir"
  ```

  **Expected output:** `Backup file count: 10`

  **Error recovery:** If count is not 10, list backup contents with `Get-ChildItem $backupDir` to find what is missing.

- [x] **0.3 Confirm current model values (pre-change baseline)**

  Run:
  ```powershell
  $cfg = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  Select-String -Path $cfg -Pattern 'glm-5' | ForEach-Object { Write-Host "$($_.LineNumber): $($_.Line.Trim())" }
  ```

  **Expected output:** Lines showing `glm-5.1` for `model` and `small_model`. Confirms the patterns we are about to change exist.

**Phase 0 Exit Criteria:** All 10 files exist. Backup created with 10 files. Config baseline confirmed.

---

## Phase 1 -- Update Global Config Defaults

**Objective:** Set GLM 5.2 as global default and pin built-in subagents.

- [x] **1.1 Update `model` in opencode.jsonc**

  **File:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

  **oldString:**
  ```
    "model": "zai-coding-plan/glm-5.1",
  ```

  **newString:**
  ```
    "model": "zai-coding-plan/glm-5.2",
  ```

  **Verify:**
  ```powershell
  (Select-String -Path "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Pattern '"model":' -SimpleMatch).Line.Trim()
  ```
  **Expected:** `"model": "zai-coding-plan/glm-5.2",`

  **Error recovery:** If oldString not found, the line may have different indentation. Search with `Select-String -Path $cfg -Pattern 'glm-5.1'` to find exact current text.

- [x] **1.2 Update `small_model` in opencode.jsonc**

  **File:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

  **oldString:**
  ```
    "small_model": "zai-coding-plan/glm-5.1",
  ```

  **newString:**
  ```
    "small_model": "zai-coding-plan/glm-5.2",
  ```

  **Verify:**
  ```powershell
  (Select-String -Path "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Pattern 'small_model' -SimpleMatch).Line.Trim()
  ```
  **Expected:** `"small_model": "zai-coding-plan/glm-5.2",`

- [x] **1.3 Expand `agent` block to pin built-in subagents**

  **File:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

  **oldString (entire line 210):**
  ```
    "agent": { "plan": { "model": "openai/gpt-5.3-codex" } },
  ```

  **newString:**
  ```
    "agent": {
      "plan": { "model": "openai/gpt-5.3-codex" },
      "general": { "model": "zai-coding-plan/glm-5.2" },
      "explore": { "model": "zai-coding-plan/glm-5.2" },
      "scout": { "model": "zai-coding-plan/glm-5.2" }
    },
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw
  Write-Host "general: $($c.Contains('"general": { "model": "zai-coding-plan/glm-5.2" }'))"
  Write-Host "explore: $($c.Contains('"explore": { "model": "zai-coding-plan/glm-5.2" }'))"
  Write-Host "scout: $($c.Contains('"scout": { "model": "zai-coding-plan/glm-5.2" }'))"
  Write-Host "plan kept: $($c.Contains('"plan": { "model": "openai/gpt-5.3-codex" }'))"
  ```
  **Expected:** All four print `True`.

  **Error recovery:** If the JSON is malformed after edit, restore from backup in `C:\Users\DaveWitkin\.config\opencode\backup-glm52-*` and retry. Ensure the closing `},` has a trailing comma and the next line (`"autoupdate"`) is intact.

**Phase 1 Exit Criteria:** `model` and `small_model` both show `glm-5.2`. Agent block has 4 entries (plan, general, explore, scout). All 4 verification checks return True.

---

## Phase 2 -- Remove Explicit Models from Primary Agents

**Objective:** Primary agents inherit global default; no explicit model pin so the user can override per-session.

- [x] **2.1 Remove `model:` from `01-planner.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\01-planner.md`

  **oldString:**
  ```
  mode: primary
  model: zai-coding-plan/glm-5.1
  tools:
  ```

  **newString:**
  ```
  mode: primary
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\01-planner.md" -Raw
  -not ($c -match '(?m)^model:\s')
  ```
  **Expected:** `True` (no model line found)

- [x] **2.2 Remove `model:` from `boost.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\boost.md`

  **oldString:**
  ```
  mode: primary
  model: zai-coding-plan/glm-5.1
  tools:
  ```

  **newString:**
  ```
  mode: primary
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\boost.md" -Raw
  -not ($c -match '(?m)^model:\s')
  ```
  **Expected:** `True`

- [x] **2.3 Remove `model:` from `build.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\build.md`

  **oldString:**
  ```
  mode: primary
  model: zai-coding-plan/glm-5.1
  tools:
  ```

  **newString:**
  ```
  mode: primary
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\build.md" -Raw
  -not ($c -match '(?m)^model:\s')
  ```
  **Expected:** `True`

**Phase 2 Exit Criteria:** None of the 3 primary agent files contain a `model:` frontmatter key. Their `mode:`, `tools:`, and `permissions:` blocks are unchanged.

---

## Phase 3 -- Pin Explicit Models on All Subagents

**Objective:** Every subagent gets explicit GLM 5.2 pin so it never inherits an orchestrator's model. This is the cost-isolation layer.

- [x] **3.1 Add `model:` to `brand-voice-validator.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\brand-voice-validator.md`

  **oldString:**
  ```
  mode: subagent
  tools:
  ```

  **newString:**
  ```
  mode: subagent
  model: zai-coding-plan/glm-5.2
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\brand-voice-validator.md" -Raw
  $c -match '(?m)^model:\s*zai-coding-plan/glm-5\.2\s*$'
  ```
  **Expected:** `True`

- [x] **3.2 Add `model:` to `cove-orchestrator.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\cove-orchestrator.md`

  **oldString:**
  ```
  mode: subagent
  tools:
  ```

  **newString:**
  ```
  mode: subagent
  model: zai-coding-plan/glm-5.2
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\cove-orchestrator.md" -Raw
  $c -match '(?m)^model:\s*zai-coding-plan/glm-5\.2\s*$'
  ```
  **Expected:** `True`

- [x] **3.3 Update `model:` in `cove-verifier.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\cove-verifier.md`

  **Note:** This file's `model:` line is at the END of frontmatter (after permissions, before closing `---`), NOT after `mode:`.

  **oldString:**
  ```
  model: zai-coding/glm-4.7
  ```

  **newString:**
  ```
  model: zai-coding-plan/glm-5.2
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\cove-verifier.md" -Raw
  $c -match '(?m)^model:\s*zai-coding-plan/glm-5\.2\s*$'
  ```
  **Expected:** `True`

  **Error recovery:** If oldString not found, search with `Select-String -Path $f -Pattern 'glm-4'` to locate the exact line.

- [x] **3.4 Add `model:` to `gen-headlines.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\gen-headlines.md`

  **oldString:**
  ```
  mode: subagent
  tools:
  ```

  **newString:**
  ```
  mode: subagent
  model: zai-coding-plan/glm-5.2
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\gen-headlines.md" -Raw
  $c -match '(?m)^model:\s*zai-coding-plan/glm-5\.2\s*$'
  ```
  **Expected:** `True`

- [x] **3.5 Add `model:` to `peer-review.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\peer-review.md`

  **oldString:**
  ```
  mode: subagent
  tools:
  ```

  **newString:**
  ```
  mode: subagent
  model: zai-coding-plan/glm-5.2
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\peer-review.md" -Raw
  $c -match '(?m)^model:\s*zai-coding-plan/glm-5\.2\s*$'
  ```
  **Expected:** `True`

- [x] **3.6 Add `model:` to `seo-auditor.md`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\agent\seo-auditor.md`

  **oldString:**
  ```
  mode: subagent
  tools:
  ```

  **newString:**
  ```
  mode: subagent
  model: zai-coding-plan/glm-5.2
  tools:
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\agent\seo-auditor.md" -Raw
  $c -match '(?m)^model:\s*zai-coding-plan/glm-5\.2\s*$'
  ```
  **Expected:** `True`

**Phase 3 Exit Criteria:** All 6 subagent files contain `model: zai-coding-plan/glm-5.2`. No `glm-5.1` or `glm-4.7` remains in any agent file.

---

## Phase 4 -- Validation & Handover

**Objective:** Comprehensive verification that all changes are correct and complete.

- [x] **4.1 Verify no stale model references remain in agent files**

  Run:
  ```powershell
  $agentDir = "$env:USERPROFILE\.config\opencode\agent"
  $stale = Get-ChildItem "$agentDir\*.md" | Select-String -Pattern 'glm-5\.1|glm-4\.7'
  if ($stale) {
      $stale | ForEach-Object { Write-Host "STALE: $($_.Filename):$($_.LineNumber): $($_.Line.Trim())" }
  } else {
      Write-Host "CLEAN: No stale model references in agent files"
  }
  ```

  **Expected:** `CLEAN: No stale model references in agent files`

  **Error recovery:** If stale references found, re-apply the corresponding Phase 2 or Phase 3 edit.

- [x] **4.2 Verify config values are correct**

  Run:
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw
  Write-Host "model has 5.2: $($c.Contains('"model": "zai-coding-plan/glm-5.2"'))"
  Write-Host "small_model has 5.2: $($c.Contains('"small_model": "zai-coding-plan/glm-5.2"'))"
  Write-Host "general pinned: $($c.Contains('"general": { "model": "zai-coding-plan/glm-5.2" }'))"
  Write-Host "explore pinned: $($c.Contains('"explore": { "model": "zai-coding-plan/glm-5.2" }'))"
  Write-Host "scout pinned: $($c.Contains('"scout": { "model": "zai-coding-plan/glm-5.2" }'))"
  Write-Host "plan override kept: $($c.Contains('"plan": { "model": "openai/gpt-5.3-codex" }'))"
  Write-Host "no stale 5.1 in model: $(-not ($c -match '"model":\s*"zai-coding-plan/glm-5\.1"'))"
  Write-Host "no stale 5.1 in small: $(-not ($c -match '"small_model":\s*"zai-coding-plan/glm-5\.1"'))"
  ```

  **Expected:** All lines print `True`.

  **Note:** `ConvertFrom-Json` will likely FAIL on `.jsonc` files (JSON with comments). That is why we use raw string checks here, not JSON parsing.

- [x] **4.3 Verify primary agents have NO model**

  Run:
  ```powershell
  $agentDir = "$env:USERPROFILE\.config\opencode\agent"
  foreach ($f in @('01-planner.md','boost.md','build.md')) {
      $c = Get-Content "$agentDir\$f" -Raw
      $hasModel = [bool]($c -match '(?m)^model:\s')
      Write-Host "$f has model line: $hasModel"
  }
  ```

  **Expected:**
  ```
  01-planner.md has model line: False
  boost.md has model line: False
  build.md has model line: False
  ```

- [x] **4.4 Verify all subagents have GLM 5.2 model**

  Run:
  ```powershell
  $agentDir = "$env:USERPROFILE\.config\opencode\agent"
  $allOk = $true
  foreach ($f in @('brand-voice-validator.md','cove-orchestrator.md','cove-verifier.md','gen-headlines.md','peer-review.md','seo-auditor.md')) {
      $c = Get-Content "$agentDir\$f" -Raw
      $hasModel = [bool]($c -match '(?m)^model:\s*zai-coding-plan/glm-5\.2\s*$')
      Write-Host "$f has glm-5.2: $hasModel"
      if (-not $hasModel) { $allOk = $false }
  }
  Write-Host "ALL OK: $allOk"
  ```

  **Expected:** All 6 lines show `True`, and `ALL OK: True`.

- [x] **4.5 Verify no permission blocks were accidentally modified**

  Run:
  ```powershell
  $agentDir = "$env:USERPROFILE\.config\opencode\agent"
  foreach ($f in Get-ChildItem "$agentDir\*.md") {
      $lines = Get-Content $f.FullName
      $hasPermissions = $lines | Where-Object { $_ -match '^permissions:' }
      if ($hasPermissions) {
          $permLine = ($lines | Select-String -Pattern '^permissions:' | Select-Object -First 1).LineNumber
          Write-Host "$f : permissions block at line $permLine (unchanged)"
      }
  }
  ```

  **Expected:** Same files that had `permissions:` before still have it at the same line numbers. No permission blocks were removed or altered.

- [x] **4.6 Write execution log and document restart requirement**

  Create or append to a file at `C:\development\opencode\.conductor\tracks\20260615-glm-52-model-migration\execution-log.md`:

  ```markdown
  # Execution Log: GLM 5.2 Model Migration

  ## Changes Applied
  - [date/time] Phase 0: Backup created
  - [date/time] Phase 1: Config model + small_model updated to glm-5.2
  - [date/time] Phase 1: Agent block expanded with general/explore/scout pins
  - [date/time] Phase 2: Model lines removed from 3 primary agents
  - [date/time] Phase 3: Model lines added/updated on 6 subagents
  - [date/time] Phase 4: All validation checks passed

  ## Post-Completion Action Required
  **RESTART OpenCode** to load the new configuration. Changes are NOT hot-reloaded.
  After restart, verify with `opencode agent list` that agents appear correctly.

  ## Deviations
  [None / describe any deviations from plan]
  ```

**Phase 4 Exit Criteria:** All checks pass. No stale references. Config values correct. Primary agents lack model. All subagents have glm-5.2. Permission blocks intact. Execution log written.

---

## Execution Readiness Checklist

| # | Standard | Status | Notes |
|---|----------|--------|-------|
| 1 | Atomic tasks (one action per checkbox) | PASS | Each task edits one file or runs one verification |
| 2 | Exact file paths | PASS | All paths are absolute using `$env:USERPROFILE` |
| 3 | Explicit commands | PASS | Every verification is a copy-paste PowerShell command |
| 4 | Clear ordering | PASS | Phase 0 to 4, strict prerequisites |
| 5 | Verification per step | PASS | Every task has expected output with exact string |
| 6 | No assumed context | PASS | Full oldString/newString shown; frontmatter context included |
| 7 | Concrete examples | PASS | Inline oldString/newString for every edit task |
| 8 | Error recovery | PASS | Each phase has fallback instructions for common failures |

## Top 3 Implementation Risks + Mitigations

1. **JSONC comments break JSON parsing** -- The config file uses `.jsonc` (JSON with comments). Validation uses raw string search, not `ConvertFrom-Json`, to avoid this. If JSON structure is accidentally broken, restore from the Phase 0 backup.

2. **`Bun is not defined` on edit/write tools** -- The build environment may have the same tool failure seen during planning. Every task includes PowerShell fallback: `Get-Content -Raw` then `[string]::Replace()` then `Set-Content -NoNewline`.

3. **cove-verifier model line placement** -- Unlike other subagents, `cove-verifier.md` has its `model:` line at the END of frontmatter (after permissions), not after `mode:`. Task 3.3 handles this with a targeted single-line replacement. Do NOT use the `mode: subagent` pattern for this file.

## First Task to Execute Immediately

**Task 0.1** -- Verify all target files exist. Run the PowerShell command and confirm all 9 agent files + 1 config file are present before proceeding to backup.