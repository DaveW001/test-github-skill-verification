# Plan: GLM 5.2 Non-Thinking Variant

## Track Info
- **Track ID**: 20260622-glm-52-non-thinking-variant
- **Created**: 2026-06-22
- **Status**: Active
- **Modifies**: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` (single file)
- **Restarts OpenCode**: NO - user's responsibility

## Restate
- **Goal:** Add a `none` reasoning variant to GLM 5.2 in `opencode.jsonc` so thinking can be toggled off via Ctrl+T.
- **Constraints:** No agent file changes. No global `model`/`small_model` changes. No new provider alias. No OpenCode restart.
- **Definition of Done:** `opencode.jsonc` has a `provider.zai-coding-plan.models.glm-5.2.variants.none` block with `thinking: { type: "disabled" }`; all other config values byte-identical; JSONC parses; backup exists; metadata + tracks files updated; execution log written.

## Editing Convention
- Prefer the `edit` tool with exact `oldString`/`newString` below.
- If `Bun is not defined` occurs on `edit`/`read`/`write`, fall back to PowerShell:
  ```powershell
  $path = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  $c = Get-Content $path -Raw
  $c = $c.Replace('<OLD_LITERAL>', '<NEW_LITERAL>')
  [System.IO.File]::WriteAllText($path, $c, [System.Text.UTF8Encoding]::new($false))
  ```
- **NEVER** use `ConvertFrom-Json` then `ConvertTo-Json` round-trip on `.jsonc` files (it strips all comments and reformats the file - destructive). Phase 3.1 provides a JSONC-safe parser.

---

## Phase 0 - Preconditions & Baseline

**Objective:** Confirm the file exists, snapshot current provider structure, and confirm the insertion point matches the planned edit pattern.

- [x] **0.1 Verify `opencode.jsonc` exists and is readable**

  Run:
  ```powershell
  $cfg = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  Test-Path $cfg
  ```

  **Expected output:** `True`

  **Error recovery:** If `False`, STOP. Verify path with `$env:USERPROFILE` and `Get-ChildItem $env:USERPROFILE\.config\opencode\`.

- [x] **0.2 Snapshot current provider block boundaries**

  Run:
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw
  $c -split "`n" | Select-String -Pattern '^    "[^"]+":\s*\{$' | ForEach-Object { Write-Host $_.Line.Trim() }
  ```

  **Expected output:** 6 lines (one per existing provider):
  ```
  "google": {
  "openai": {
  "moonshot": {
  "openrouter": {
  "go-dave": {
  "go-tiberius": {
  ```

  **Error recovery:** If the count is not 6 or any provider is missing, STOP. The plan assumes this is the current state. Re-evaluate whether the edit pattern in Phase 2.1 still applies.

**Phase 0 Exit Criteria:** `opencode.jsonc` exists; 6 provider blocks; insertion-point pattern (close of `go-tiberius` immediately followed by close of `provider`) is at the expected position.

---

## Phase 1 - Backup

**Objective:** Create a timestamped backup that captures the exact pre-change state.

- [x] **1.1 Create timestamped backup and verify byte-identity**

  Run:
  ```powershell
  $ts = Get-Date -Format "yyyyMMdd-HHmmss"
  $src = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  $dst = "$src.backup-$ts"
  Copy-Item $src $dst
  Write-Host "Backup: $dst"
  Write-Host "Size matches: $((Get-Item $src).Length -eq (Get-Item $dst).Length)"
  ```

  **Expected output:**
  ```
  Backup: C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.backup-YYYYMMDD-HHMMSS
  Size matches: True
  ```

  **Error recovery:** If `Size matches: False`, delete the backup and retry. If a `backup-$ts` file already exists for this same timestamp, redo with a fresh timestamp (e.g. add `-1`).

**Phase 1 Exit Criteria:** A `opencode.jsonc.backup-YYYYMMDD-HHMMSS` file exists with byte-identical size to source.

---

## Phase 2 - Edit

**Objective:** Insert the `zai-coding-plan` block as a sibling of `go-tiberius` inside the `provider` object.

- [x] **2.1 Insert the `zai-coding-plan` block after `go-tiberius`**

  **File:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

  **oldString** (the close of `go-tiberius` immediately followed by the close of `provider`):
  ```
      }
    },
  ```

  **newString** (same close of `go-tiberius` but now with a trailing comma, then the new block, then close of `provider`):
  ```
      },
      "zai-coding-plan": {
        "models": {
          "glm-5.2": {
            "variants": {
              "none": {
                "thinking": { "type": "disabled" }
              }
            }
          }
        }
      }
    },
  ```

  **Why this exact location:** `go-tiberius` is the last provider block in the file. The new block is inserted as its sibling, between `go-tiberius`'s closing `}` and the `"provider"` object's closing `},`.

  **PowerShell fallback** (if `Bun is not defined` on the `edit` tool):
  ```powershell
  $path = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  $c = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
  $old = "    }`n  },"
  $new = "    },`n    `"zai-coding-plan`": {`n      `"models`": {`n        `"glm-5.2`": {`n          `"variants`": {`n            `"none`": {`n              `"thinking`": { `"type`": `"disabled`" }`n            }`n          }`n        }`n      }`n    }`n  },"
  if (-not $c.Contains($old)) { Write-Host "ERROR: oldString not found in file"; exit 1 }
  $c = $c.Replace($old, $new)
  [System.IO.File]::WriteAllText($path, $c, [System.Text.UTF8Encoding]::new($false))
  ```

  **Verify:**
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw
  $c.Contains('"zai-coding-plan": {')
  $c.Contains('"glm-5.2": {')
  $c.Contains('"none": {')
  $c.Contains('"thinking": { "type": "disabled" }')
  ```

  **Expected:** All four print `True`.

  **Error recovery:** If any check returns `False`, the edit was not applied as expected. Inspect with `Select-String -Path $cfg -Pattern 'zai-coding-plan'` to see what landed. If the file is malformed, restore from the Phase 1 backup and retry.

- [x] **2.2 Confirm file size grew by ~150-250 bytes**

  Run:
  ```powershell
  $src = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  $bak = Get-ChildItem "$src.backup-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $delta = (Get-Item $src).Length - $bak.Length
  Write-Host "Size delta: $delta bytes (expected: ~180)"
  ```

  **Expected output:** `Size delta:` is between 150 and 250 bytes (the inserted block plus the trailing comma on the previous `go-tiberius` line).

  **Error recovery:** If the delta is negative (file shrank) or wildly off (>500 bytes), something is wrong. Diff against backup with `Compare-Object (Get-Content $src) (Get-Content $bak.FullName)` and revert if needed.

**Phase 2 Exit Criteria:** The new block is present, file size grew by the expected amount.

---

## Phase 3 - JSONC Syntax Validation

**Objective:** Prove the file is still valid JSONC (parses as JSON after comment-stripping).

- [x] **3.1 Parse JSONC and confirm no errors**

  Save this PowerShell function to a temp script and run it (or paste into a PowerShell session):
  ```powershell
  $script = @'
  function Test-JsonC {
      param([string]$Path)
      $raw = [System.IO.File]::ReadAllText($Path)
      # Strip /* ... */ block comments
      $noBlock = [regex]::Replace($raw, '/\*[\s\S]*?\*/', '')
      # Strip // line comments (but not inside strings)
      $sb = New-Object System.Text.StringBuilder
      $inString = $false
      $escape = $false
      for ($i = 0; $i -lt $noBlock.Length; $i++) {
          $ch = $noBlock[$i]
          if ($escape) { [void]$sb.Append($ch); $escape = $false; continue }
          if ($ch -eq '\') { [void]$sb.Append($ch); $escape = $true; continue }
          if ($ch -eq '"') { $inString = -not $inString; [void]$sb.Append($ch); continue }
          if (-not $inString -and $ch -eq '/' -and $i + 1 -lt $noBlock.Length -and $noBlock[$i+1] -eq '/') {
              while ($i -lt $noBlock.Length -and $noBlock[$i] -ne "`n") { $i++ }
              if ($i -lt $noBlock.Length) { [void]$sb.Append("`n") }
              continue
          }
          [void]$sb.Append($ch)
      }
      $stripped = $sb.ToString()
      try {
          # Use System.Text.Json.JsonDocument instead of ConvertFrom-Json.
          # ConvertFrom-Json fails on .jsonc files that have keys with different casing
          # (e.g. "Retro" vs "retro") because PowerShell converts to a case-insensitive
          # hashtable. JsonDocument parses the JSON literally without that quirk.
          $null = [System.Text.Json.JsonDocument]::Parse($stripped)
          return $true
      } catch {
          Write-Host "JSONC parse error: $($_.Exception.Message)"
          return $false
      }
  }
  Test-JsonC "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  '@
  $tmp = Join-Path $env:TEMP "test-jsonc.ps1"
  [System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))
  & pwsh -NoProfile -File $tmp
  ```

  **Expected output:** `True`

  **Error recovery:** If `False`, the file is malformed. The `JSONC parse error:` line will give a position hint. Restore from the Phase 1 backup and retry Phase 2.

  **Note:** This script handles JSONC correctly:
  - Strips `/* ... */` block comments
  - Strips `// ...` line comments (without touching `//` inside JSON strings like URLs)
  - Respects `\"` escapes inside strings

**Phase 3 Exit Criteria:** `Test-JsonC` returns `True`.

---

## Phase 4 - Structural Verification

**Objective:** Confirm the new block has correct nesting and no other config values were modified.

- [x] **4.1 Verify exact nesting path (provider > zai-coding-plan > models > glm-5.2 > variants > none > thinking > type: disabled)**

  Run:
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw
  $checks = @(
    '"zai-coding-plan": {',
    '"models": {',
    '"glm-5.2": {',
    '"variants": {',
    '"none": {',
    '"thinking": { "type": "disabled" }'
  )
  $pos = -1
  $ok = $true
  foreach ($needle in $checks) {
    $newPos = $c.IndexOf($needle, $pos + 1)
    if ($newPos -lt 0) { Write-Host "MISSING: $needle"; $ok = $false; break }
    $pos = $newPos
  }
  Write-Host "Nested path OK: $ok"
  ```

  **Expected:** `Nested path OK: True`

- [x] **4.2 Verify all 6 built-in provider blocks are still present and unchanged**

  Run:
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw
  foreach ($p in @('google','openai','moonshot','openrouter','go-dave','go-tiberius')) {
      $present = $c -match ('(?m)^    "' + $p + '":\s*\{$')
      Write-Host "$p : $present"
  }
  ```

  **Expected:** All 6 lines print `True`.

- [x] **4.3 Verify global model and small_model are unchanged**

  Run:
  ```powershell
  $c = Get-Content "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Raw
  $c.Contains('"model": "zai-coding-plan/glm-5.2"')
  $c.Contains('"small_model": "zai-coding-plan/glm-5.2"')
  ```

  **Expected:** Both print `True`.

- [x] **4.4 Diff against backup to confirm only the intended block changed**

  Run:
  ```powershell
  $src = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
  $bak = Get-ChildItem "$src.backup-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $diff = Compare-Object (Get-Content $bak.FullName) (Get-Content $src)
  $added = @($diff | Where-Object SideIndicator -eq '=>')
  $removed = @($diff | Where-Object SideIndicator -eq '<=')
  Write-Host "Lines added: $($added.Count)"
  Write-Host "Lines removed: $($removed.Count)"
  Write-Host "---ADDED LINES---"
  $added | ForEach-Object { Write-Host "  + $($_.InputObject)" }
  ```

  **Expected output:**
  - `Lines added: 12` (11 lines for the new block + 1 trailing comma on the previous `go-tiberius` close)
  - `Lines removed: 0`
  - The added lines show ONLY the new `zai-coding-plan` block and the `},` modification.

  **Error recovery:** If `Lines removed > 0` or unexpected lines are added, the edit touched more than intended. Restore from the backup and retry.

**Phase 4 Exit Criteria:** Nesting correct, 6 built-in providers preserved, model/small_model preserved, diff shows only the intended insertion.

---

## Phase 5 - Optional Intent Test (OpenCode CLI)

**Objective:** If the `opencode` CLI is available in PATH, prove that the config loads without parse errors (smoke test for the full intent chain).

- [x] **5.1 Attempt to load config via `opencode` CLI (skip silently if not in PATH)**

  Run:
  ```powershell
  $oc = Get-Command opencode -ErrorAction SilentlyContinue
  if ($null -eq $oc) {
      Write-Host "SKIP: opencode CLI not in PATH; user will validate on restart"
  } else {
      $out = & opencode --version 2>&1
      Write-Host "opencode --version: $out"
  }
  ```

  **Expected:** If `opencode` is in PATH, prints a version line. If not in PATH, prints `SKIP:`.

  **Note:** This is a smoke test that proves the config does not break CLI startup. It does NOT prove the variant override works at request time - that requires a live model call, which is the user's responsibility post-restart.

**Phase 5 Exit Criteria:** Either a version string is printed (CLI loads config) or the SKIP line is printed (CLI not in PATH).

---

## Phase 6 - Completion Validation

**Objective:** Mark all plan tasks complete, update metadata and tracks, write execution log.

- [x] **6.1 Mark all plan checkboxes `[x]`**

  Edit `C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\plan.md` and replace every `- [ ]` with `- [x]` in the task list sections (do NOT touch the legend at the bottom or the "Checkbox states" lines).

  **Verify:**
  ```powershell
  $p = "C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\plan.md"
  $unchecked = (Select-String -Path $p -Pattern '^- \[ \]' | Measure-Object).Count
  Write-Host "Unchecked task count: $unchecked"
  ```

  **Expected:** `Unchecked task count: 0`

- [x] **6.2 Update `metadata.json` progress and status**

  Edit `C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\metadata.json` with these exact field changes:
  - Set `status` to `"complete"`
  - Set `completed` to `"2026-06-22"`
  - Set `progress.totalTasks` to `17`
  - Set `progress.completedTasks` to `17`
  - Set `progress.percentage` to `100`

  **Verify:**
  ```powershell
  $m = Get-Content "C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\metadata.json" -Raw | ConvertFrom-Json
  Write-Host "status: $($m.status)"
  Write-Host "completed: $($m.completed)"
  Write-Host "progress.percentage: $($m.progress.percentage)"
  Write-Host "progress.completedTasks: $($m.progress.completedTasks) / totalTasks: $($m.progress.totalTasks)"
  ```

  **Expected:**
  ```
  status: complete
  completed: 2026-06-22
  progress.percentage: 100
  progress.completedTasks: 17 / totalTasks: 17
  ```

- [x] **6.3 Update `tracks.md` row**

  Edit `C:\development\opencode\.conductor\tracks.md`:
  - Find the row for `20260622-glm-52-non-thinking-variant`
  - Change `Status` from `active` to `complete`
  - Add `2026-06-22` in the `Completed` column (currently empty)

  Current row (last line of the file):
  ```
  | 20260622-glm-52-non-thinking-variant | GLM 5.2 Non-Thinking Variant | active | | C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant |
  ```

  Updated row:
  ```
  | 20260622-glm-52-non-thinking-variant | GLM 5.2 Non-Thinking Variant | complete | 2026-06-22 | C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant |
  ```

  **Verify:**
  ```powershell
  $t = Get-Content "C:\development\opencode\.conductor\tracks.md" -Raw
  $t.Contains('| 20260622-glm-52-non-thinking-variant | GLM 5.2 Non-Thinking Variant | complete | 2026-06-22 |')
  ```

  **Expected:** `True`

- [x] **6.4 Move `tracks-ledger.md` entry from Active to Completed**

  Edit `C:\development\opencode\.conductor\tracks-ledger.md`:
  - In the "Active Tracks" section, find the line starting with `- [20260622-glm-52-non-thinking-variant`
  - **Move** it to the "Completed Tracks" section (alphabetical order: insert after the most recent `dcp-token-savings-analysis` entry, before the next entry)
  - Replace the `(Phase: ready-for-build)` tag with `(Completed: 2026-06-22)`

  Current active line:
  ```
  - [20260622-glm-52-non-thinking-variant](./tracks/20260622-glm-52-non-thinking-variant/spec.md): Add a 'none' reasoning variant to GLM 5.2 so thinking can be toggled off via Ctrl+T. Config variants merge with built-in {high, max}, yielding {high, max, none}. Variant overrides hardcoded forced thinking at request time (highest merge precedence). Single model, no alias. (Phase: ready-for-build)
  ```

  Updated completed line:
  ```
  - [20260622-glm-52-non-thinking-variant](./tracks/20260622-glm-52-non-thinking-variant/spec.md): Add a 'none' reasoning variant to GLM 5.2 so thinking can be toggled off via Ctrl+T. Config variants merge with built-in {high, max}, yielding {high, max, none}. Variant overrides hardcoded forced thinking at request time (highest merge precedence). Single model, no alias. (Completed: 2026-06-22)
  ```

  **Verify:**
  ```powershell
  $l = Get-Content "C:\development\opencode\.conductor\tracks-ledger.md" -Raw
  $l.Contains('(Completed: 2026-06-22)')
  $l -notmatch '- \[20260622-glm-52-non-thinking-variant.*Phase:'
  ```

  **Expected:** Both print `True`.

  **Error recovery:** If the line is in both Active and Completed sections, delete the Active copy.

- [x] **6.5 Write execution log**

  Create `C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\execution-log-2026-06-22.md` with the content below. Capture the actual backup path printed by Phase 1.1 and the actual byte-delta from Phase 2.2 to fill in the placeholders.

  ```markdown
  # Execution Log: GLM 5.2 Non-Thinking Variant

  ## Summary
  Added a `none` reasoning variant to GLM 5.2 in `opencode.jsonc` so thinking can be toggled off via Ctrl+T. Single model `zai-coding-plan/glm-5.2`, no alias.

  ## Changes Applied
  - Phase 0: Preconditions confirmed; 6 provider blocks present.
  - Phase 1: Timestamped backup created at `<PATH>`.
  - Phase 2: `zai-coding-plan` block inserted as sibling of `go-tiberius` inside `provider`. File size delta: `<N>` bytes.
  - Phase 3: JSONC parses (Test-JsonC: True).
  - Phase 4: All structural checks pass; diff confirms only the intended block changed.
  - Phase 5: opencode CLI: `<loaded version, or skipped (not in PATH)>`.
  - Phase 6: Tracks files updated; metadata set to complete.

  ## Insertion Point
  Lines 207-208 of `opencode.jsonc` (close of `go-tiberius` immediately followed by close of `provider` block).

  ## Diff Summary
  - Added 11 lines for the new `zai-coding-plan` block.
  - Added a trailing comma to the line closing `go-tiberius`.
  - No lines removed; no other modifications.

  ## Post-Completion Action Required
  **RESTART OpenCode** to load the new configuration. Changes are NOT hot-reloaded. After restart, verify:
  1. Ctrl+T menu shows three variants for GLM-5.2: `none`, `high`, `max`.
  2. Selecting `none` produces API requests with `thinking: { type: "disabled" }` (verify via DevTools network tab or proxy log).

  ## Deviations
  [None / describe any deviations from the plan]
  ```

  **Verify:**
  ```powershell
  $log = "C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\execution-log-2026-06-22.md"
  Test-Path $log
  ```

  **Expected:** `True`

- [x] **6.6 Mark all spec.md Build-Agent acceptance criteria `[x]`**

  Edit `C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\spec.md` and replace `- [ ]` with `- [x]` in the "Build-Agent Verification" section ONLY. Do NOT modify the "User Verification" section (those are still pending user verification post-restart).

  **Verify:**
  ```powershell
  $s = "C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\spec.md"
  $content = Get-Content $s -Raw
  # Extract the Build-Agent section: from "### Build-Agent Verification" to "### User Verification"
  $ba = $content.Substring($content.IndexOf('### Build-Agent Verification'), $content.IndexOf('### User Verification') - $content.IndexOf('### Build-Agent Verification'))
  $uncheckedInBA = ([regex]::Matches($ba, '- \[ \]')).Count
  Write-Host "Unchecked build-agent criteria: $uncheckedInBA"
  ```

  **Expected:** `Unchecked build-agent criteria: 0`

**Phase 6 Exit Criteria:** All plan checkboxes marked complete; metadata.json status=complete and progress=100; tracks.md and tracks-ledger.md updated; execution log written; spec.md build-agent acceptance criteria checked.

---

## Execution Readiness Checklist

| # | Standard | Status |
|---|----------|--------|
| 1 | Atomic tasks (one action per checkbox) | PASS |
| 2 | Exact file paths (absolute, $env:USERPROFILE) | PASS |
| 3 | Explicit PowerShell commands for every action | PASS |
| 4 | Clear ordering (Phase 0 -> 6, strict prereqs) | PASS |
| 5 | Deterministic verification per step (with expected output) | PASS |
| 6 | No assumed context (oldString/newString shown verbatim) | PASS |
| 7 | Concrete examples (JSONC parser, diff output, expected lines) | PASS |
| 8 | Error recovery (every phase has fallback instructions) | PASS |
| 9 | Intent test (Phase 5 opencode CLI load + user-side Ctrl+T post-restart) | PASS |

## Top 3 Implementation Risks + Mitigations

1. **JSONC comments break standard JSON parsing** - Phase 3.1 provides a custom `Test-JsonC` PowerShell function that correctly strips `//` and `/* */` comments without disturbing `//` inside JSON strings. **NEVER** use `ConvertFrom-Json` then `ConvertTo-Json` round-trip on the file (it strips all comments destructively).

2. **Edit tool may return `Bun is not defined`** - Phase 2.1 includes a PowerShell `[System.IO.File]::WriteAllText()` fallback using `Get-Content -Raw`-style read-then-replace. If the `edit` tool fails, run the PowerShell block instead.

3. **`oldString` may match multiple positions if file structure changes** - The chosen oldString `    }\n  },` is specific to the go-tiberius-to-provider-close boundary, but a positional match elsewhere is theoretically possible. Phase 0.2 confirms the expected structure, and Phase 4.4 re-runs the full diff to catch any unexpected matches.

## First Task to Execute Immediately

**Task 0.1** - Run `Test-Path "$env:USERPROFILE\.config\opencode\opencode.jsonc"` and confirm `True` before proceeding to Phase 0.2 / backup / edit.