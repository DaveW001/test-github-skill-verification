# Plan

> **Target file:** `C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js`
> **File stats:** 23,556 lines, ESM (`"type": "module"` in package.json)
> **Problematic line:** Line 28 -- `var __require = import.meta.require;`
> **Root cause:** `import.meta.require` is a Bun-only API. Node.js does not support it, causing `TypeError: __require is not a function` at runtime.

---

## Phase 1 - Backup & Analysis

- [x] **1.1 Create the artifacts directory**
  - Run: `New-Item -ItemType Directory -Path "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts" -Force`
  - **Verify:** `Test-Path "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts"` returns `True`

- [x] **1.2 Create a timestamped backup of `dist/index.js`**
  - Run:
    ```powershell
    $ts = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item -LiteralPath "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" -Destination "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\index.js.backup-$ts"
    Write-Output "Backup created: index.js.backup-$ts"
    ```
  - **Verify:** Run `Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts"` and confirm the backup file exists with non-zero size.

- [x] **1.3 Confirm the exact line to patch**
  - Run: `Select-String -LiteralPath "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" -Pattern "var __require = import.meta.require"`
  - **Expected output:** Line 28 containing exactly `var __require = import.meta.require;`
  - **If not found:** STOP and report. The file may have been updated or the pattern differs. Search for `import.meta.require` as a broader fallback.

- [x] **1.4 Record the original file size for later comparison**
  - Run: `(Get-Item "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js").Length`
  - Write the byte count down for Phase 3 comparison.

---

## Phase 2 - Patch Application

- [x] **2.1 Replace the Bun-specific `import.meta.require` with the `createRequire` polyfill**
  - Use the `edit` tool (or `Write` if `edit` is unavailable) to perform an exact string replacement.
  - **oldString:**
    ```
    var __require = import.meta.require;
    ```
  - **newString:**
    ```
    import { createRequire as __createRequire } from "module";
    var __require = __createRequire(import.meta.url);
    ```
  - **Why this works:** ES module `import` declarations are hoisted by the JS engine regardless of where they appear in the file. The existing file already uses inline `import` statements at lines 16191+, so this pattern is consistent.
  - **Verify:** Re-run the search from task 1.3. It should now return ZERO matches for `import.meta.require`. Run `Select-String -LiteralPath "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" -Pattern "createRequire"` and confirm it returns the new line.

- [x] **2.2 Verify the patched file is syntactically valid**
  - Run: `node -e "import('file:///C:/Users/DaveWitkin/AppData/Roaming/npm/node_modules/@zenobius/opencode-skillful/dist/index.js').then(() => console.log('SYNTAX OK')).catch(e => console.error('SYNTAX ERROR:', e.message))"`
  - **Expected:** `SYNTAX OK` or a runtime error that is NOT a SyntaxError (runtime import errors are fine -- we are only checking syntax here).
  - **If SyntaxError:** The patch broke the file. Restore from backup:
    ```powershell
    $backup = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\index.js.backup-*" | Sort-Object Name -Descending | Select-Object -First 1
    Copy-Item -LiteralPath $backup.FullName -Destination "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" -Force
    ```
    Then STOP and report the syntax error.

---

## Phase 3 - Verification & Diff

- [x] **3.1 Confirm file size change is minimal**
  - Run: `(Get-Item "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js").Length`
  - **Expected:** The new file should be approximately the original size plus ~80 bytes (the polyfill line is longer than the original). Any change > 200 bytes indicates an unintended edit.

- [x] **3.2 Generate and save the diff**
  - Run:
    ```powershell
    $backup = Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\index.js.backup-*" | Sort-Object Name -Descending | Select-Object -First 1
    $original = $backup.FullName
    $patched = "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js"
    $diff = Compare-Object (Get-Content $original) (Get-Content $patched) | ForEach-Object { "$($_.SideIndicator) $($_.InputObject)" }
    $diff | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\patch-diff.txt"
    Write-Output "Diff saved. Lines changed: $($diff.Count)"
    ```
  - **Expected:** Approximately 3 lines of diff output showing the removal of the old line and addition of the two new lines.
  - **If more than 5 lines differ:** STOP. The patch may have corrupted the file. Review the diff and restore from backup if needed.

- [x] **3.3 Verify no other `import.meta.require` references remain**
  - Run: `Select-String -LiteralPath "C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js" -Pattern "import\.meta\.require"`
  - **Expected:** Zero matches. Any remaining `import.meta.require` will cause the same crash.

---

## Phase 4 - Documentation

- [x] **4.1 Write re-application instructions to `artifacts/reapply-instructions.md`**
  - Create file at: `C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\reapply-instructions.md`
  - Content should include:
    1. The exact `oldString` and `newString` for the edit (from task 2.1)
    2. The target file path
    3. A warning that `npm update -g @zenobius/opencode-skillful` will overwrite the patch
    4. Steps to re-apply: backup, edit, verify
  - **Verify:** File exists and contains the string `createRequire`.

- [x] **4.2 Update `metadata.json` with completion status**
  - File: `C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\metadata.json`
  - Update these fields:
    - `"status": "active"` to `"status": "completed"`
    - `"completed": null` to `"completed": "<today's date, e.g., 2026-05-26>"`
    - `"completedTasks": 0` to match the actual count of checked tasks
    - `"percentage": 0` to `"percentage": 100`
  - **Verify:** `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\metadata.json" -Pattern '"status": "completed"'` returns a match.

- [x] **4.3 Update `tracks-ledger.md` with track status**
  - File: `C:\development\opencode\.conductor\tracks-ledger.md`
  - Find the row for track `20260526-skillful-local-patch` and update:
    - Status column: `active` to `completed`
    - Completed date: add today's date
  - **Verify:** The row contains `completed` in the status column.
  - **If the track row does not exist:** Append a new row with all relevant fields.

---

## Phase 5 - Completion Validation

- [x] **5.1 Verify all plan tasks are checked `[x]`**
  - Re-read `plan.md` and confirm every `- [ ]` has been changed to `- [x]`.
  - **If any remain unchecked:** Resolve or explicitly cancel them with a note.

- [x] **5.2 Verify `metadata.json` is synchronized**
  - Re-read `metadata.json` and confirm:
    - `"status": "completed"`
    - `"completed"` is a date string (not null)
    - `"completedTasks"` equals the total number of tasks
    - `"percentage": 100`

- [x] **5.3 Verify `tracks-ledger.md` row matches**
  - Re-read `tracks-ledger.md` and confirm the `20260526-skillful-local-patch` row shows `completed` and has a completed date.

- [x] **5.4 Create execution log**
  - Create file: `C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\execution-log.md`
  - Include: tasks completed, any deviations from plan, skipped items, and validation results.

- [x] **5.5 Final artifact integrity check**
  - Confirm these files exist and are non-empty:
    1. `artifacts/index.js.backup-*` (timestamped backup)
    2. `artifacts/patch-diff.txt` (the diff)
    3. `artifacts/reapply-instructions.md` (re-application guide)
    4. `artifacts/execution-log.md` (this log)
  - Run: `Get-ChildItem "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts" | Format-Table Name, Length`

---

## Task Safety Rules

### Collision Guard (Required for Any Rename/Move Task)

When a task involves renaming or moving files, include a pre-execution check in the task instructions:

```markdown
#### Pre-execution check
- Before executing, verify the target path does NOT already exist.
- If target exists: stop and report the collision. Do NOT overwrite.
- Resolve by either: (a) asking user to choose, (b) merging content, or
  (c) deleting the duplicate if confirmed redundant.
```

### Edit Safety for Structured Files (Required for Bulk Edits)

When editing files with 3+ items sharing identical structural patterns (review queues,
ledgers, audit reports), prefer rewriting the entire file over individual `oldString`
edits. See `knowledge-graph-maintainer` skill reference:
`references/edit-safety-for-structured-files.md`.