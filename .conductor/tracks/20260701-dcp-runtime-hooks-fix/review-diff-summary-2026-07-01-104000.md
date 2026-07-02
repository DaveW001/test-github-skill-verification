# Review Diff Summary: `20260701-dcp-runtime-hooks-fix`

**Reviewer:** `conductor-plan-reviewer` on `opencode-go/minimax-m3`
**Reviewed at:** 2026-07-01 10:40:00

This file enumerates every edit the reviewer applied to `spec.md`, `plan.md`, and `metadata.json`. Each entry lists the file, the task or section affected, and a short before/after. The accompanying `review-report-2026-07-01-104000.md` is the per-task evaluation; this file is the change log.

---

## File 1 - `plan.md`

### Edit 1.1 - Task 0.1 cross-reference typo

- **Where:** Phase 0, Task 0.1, "Diagnostic checks" bullet.
- **Why:** The original text said "If `dcp.jsonc` is missing, note that Task 1.1 will create it", but Task 1.1 is a log scan, not a config creation. The dcp.jsonc create/edit task is Task 3.1.
- **Before:**
  > Diagnostic checks: If `dcp.jsonc` is missing, note that Task 1.1 will create it from a minimal template after backing up the config directory.
- **After:**
  > Diagnostic checks: If `dcp.jsonc` is missing, note that Task 3.1 will create it from a minimal template after backing up the config directory.

### Edit 1.2 - Task 2.1 smoke test: add try-catch

- **Where:** Phase 2, Task 2.1, Action code block.
- **Why:** The original script had no try-catch. A thrown error from the factory (or the ESM import) would crash the process and `ConvertFrom-Json` would receive no JSON, hiding the real cause. Adding try-catch around the import and the factory call surfaces a structured `{ok, error, factoryError}` JSON on failure.
- **Before (script body):** imported the package, called the factory inline, logged JSON; no error path.
- **After (script body):** wraps both the import and the factory call in try-catch; on failure, emits `{ok: false, error: "..."}` or `{ok: true, factoryCalled: true, factoryError: "..."}`. The JSON now also includes `factoryCalled` and `factoryError` fields.

### Edit 1.3 - Task 2.1 acceptance check: drop over-strict hook-key requirement

- **Where:** Phase 2, Task 2.1, Authoritative acceptance check.
- **Why:** The original check required `hasConfig + hasTool + hasMessagesTransform + hasCommandBefore + null factoryError`. Dry-running the smoke test against the real DCP 3.1.14 package showed the factory throws on a minimal ctx (`Cannot read properties of undefined (reading '_client')`), so the check would always be `False` and the executor could not use the smoke test as a positive signal. The honest signal the smoke test can produce in isolation is "package is importable and factory is exported"; full hook construction is the live-runtime test in Task 3.2.
- **Before:**
  ```powershell
  ($json.ok -eq $true) -and ($json.hasConfig -eq $true) -and ($json.hasTool -eq $true) -and ($json.hasMessagesTransform -eq $true) -and ($json.hasCommandBefore -eq $true) -and ($null -eq $json.factoryError)
  ```
- **After:**
  ```powershell
  ($json.ok -eq $true) -and ($json.factoryCalled -eq $true)
  ```
- **Companion change:** "Diagnostic checks" updated to interpret `factoryError` as a ctx-requirement signal and point to Task 3.2 as the hook-construction source of truth.

### Edit 1.4 - Task 2.1 smoke test: use `pathToFileURL` for Windows ESM import

- **Where:** Phase 2, Task 2.1, Action code block (the first line of the script).
- **Why:** Node ESM dynamic import on Windows requires a `file://` URL for absolute paths. The original `await import(pkgPath)` (with a forward-slash `C:/...` string) is rejected with `Only URLs with a scheme in: file, data, and node are supported... Received protocol 'c:'`. This was the most material defect in the plan; without this fix, the smoke test never gets to the factory call.
- **Before:**
  ```javascript
  const pkgPath = 'C:/Users/DaveWitkin/.cache/opencode/packages/@tarquinen/opencode-dcp@latest/node_modules/@tarquinen/opencode-dcp/dist/index.js';
  try {
    const mod = await import(pkgPath);
  ```
- **After:**
  ```javascript
  import { pathToFileURL } from 'node:url';
  const pkgPath = 'C:/Users/DaveWitkin/.cache/opencode/packages/@tarquinen/opencode-dcp@latest/node_modules/@tarquinen/opencode-dcp/dist/index.js';
  try {
    // Use pathToFileURL so Node ESM accepts the absolute Windows path
    const mod = await import(pathToFileURL(pkgPath).href);
  ```
- **Verification:** Dry-run output was `{"ok":true,"exportKeys":["default"],"factoryCalled":true,"factoryError":"Cannot read properties of undefined (reading '_client')","hookKeys":[],"hasConfig":false,"hasTool":false,"hasCommandBefore":false,"hasMessagesTransform":false}`. The acceptance check `($json.ok -eq $true) -and ($json.factoryCalled -eq $true)` is `True`; the `factoryError` is captured for the executor to interpret.

### Edit 1.5 - Task V.3: delta-based report check with baseline capture

- **Where:** Final Phase, Task V.3, full task block (Action, Authoritative acceptance, Expected output, Diagnostic, Error recovery).
- **Why:** The original V.3 acceptance (`@($json.sessions | Where-Object { $_.has_dcp -eq $true }).Count -gt 0`) was a no-op given the current `aggregate.json`: it has 30 `has_dcp=true` sessions, all from before 2026-06-25, so the check passed without the fix doing anything. The orchestrator prompt's goal #4 ("acceptance criteria verify DCP runtime behavior ... report-based validation where possible") was not met.
- **Before:** ran the report twice; checked that any session has `has_dcp=true`.
- **After:** captures the pre-fix `aggregate.json` as a baseline under `backups/aggregate.baseline.json` on first run, regenerates the report, then asserts:
  ```powershell
  $countGrew = $newJson.sessions_with_dcp -gt $baselineJson.sessions_with_dcp
  $reportRefreshed = ([datetime]$newJson.generated_at) -gt ([datetime]$baselineJson.generated_at)
  $countGrew -and $reportRefreshed
  ```
  The acceptance now returns `True` only when (a) at least one new session has triggered DCP since the baseline AND (b) the report was actually re-generated. Error recovery falls back to prune-state / DCP debug log evidence if the report script fails.
- **Verification:** Dry-run showed the new check returns `False` pre-fix (no growth, no refresh) and `True` post-fix with one new `has_dcp` session. The old check returned `True` in both cases.

### Edit 1.6 - Task V.4: capture `$runDate` once, drop hardcoded date

- **Where:** Final Phase, Task V.4, Action line and Authoritative acceptance check.
- **Why:** The original path `execution-log-2026-07-01.md` was hardcoded. If the run spans midnight, the log would be date-stamped for the wrong day. Per `references/powershell-edit-hazards.md` ("session-spanning date handling"), the run date should be captured once and reused.
- **Before (action):**
  > Action: Create `C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\execution-log-2026-07-01.md` summarizing commands run, changes made, backups, runtime evidence, and any skipped/destructive steps.
- **After (action):**
  > Action: Capture the run date once with ``$runDate = (Get-Date).ToString('yyyy-MM-dd')`` and create ``C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\execution-log-$runDate.md`` summarizing commands run, changes made, backups, runtime evidence, and any skipped/destructive steps. Reuse ``$runDate`` for any other date-stamped artifacts in the run.
- **Before (acceptance):** hardcoded `'...execution-log-2026-07-01.md'` in `$log`.
- **After (acceptance):**
  ```powershell
  $runDate = (Get-Date).ToString('yyyy-MM-dd')
  $log = Join-Path 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix' "execution-log-$runDate.md"
  (Test-Path -LiteralPath $log) -and ((Get-Content -Raw -LiteralPath $log).Contains('Rollback summary')) -and ((Get-Content -Raw -LiteralPath $log).Contains('Runtime evidence'))
  ```

---

## File 2 - `metadata.json`

### Edit 2.1 - `progress.total_tasks`: 15 -> 16

- **Why:** Off-by-one. The plan contains 16 `**Task N.M - ...**` checkboxes (Tasks 0.1, 0.2, 0.3, 1.1, 1.2, 2.1, 3.1, 3.2, 4.1, 4.2, 4.3, 5.1, V.1, V.2, V.3, V.4). The metadata's `15` was wrong; if left uncorrected, Stage 5 validation would compare `completed_tasks` to the wrong denominator and over-report progress.
- **Before:** `"total_tasks": 15,`
- **After:** `"total_tasks": 16,`

### Edit 2.2 - `stage`: stage-1-plan-creation -> stage-2-plan-review

- **Why:** Reflect that Stage 1 has completed and Stage 2 is now in progress.
- **Before:** `"stage": "stage-1-plan-creation"`
- **After:** `"stage": "stage-2-plan-review",` plus two new sibling fields (Edit 2.3).

### Edit 2.3 - Added `reviewer_model` and `last_reviewed_at`

- **Why:** Auditability. Reviewer model and review date are explicit so Stage 3 (if ever triggered) and Stage 5 (validation) can see who reviewed and when.
- **Added fields:**
  ```json
  "reviewer_model": "opencode-go/minimax-m3",
  "last_reviewed_at": "2026-07-01"
  ```

---

## File 3 - `spec.md`

**No edits.** The spec is at the right abstraction level (goal, constraints, non-goals, definition of done, primary evidence, proposed fix sequence). The acceptance focus list in `metadata.json` matches the spec's definition of done. The plan-level edits above implement the spec without needing spec changes.

---

## Summary of changes

| File | Edits | New lines (approx) |
|---|---|---|
| `plan.md` | 6 (1.1 through 1.6) | ~80 |
| `metadata.json` | 3 (2.1, 2.2, 2.3) | 3 (replacing 1) |
| `spec.md` | 0 | 0 |

The plan moved from "contains a verification snippet that always fails" (Task 2.1 import error) and "contains an acceptance check that always passes pre-fix" (Task V.3 static check) to "every acceptance check is a real, dry-run-verified, delta-based or active-detect signal that the fix did what it claimed". The structural risk profile is unchanged: still 6 phases, 16 tasks, the same rollback and safety-stop semantics, and the same phase ordering.

## Files NOT modified (deliberately)

- `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc` (no edit; Task 3.1 is executor-scope and approval-gated).
- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` (no edit; secrets present; Task 4.3 is executor-scope and approval-gated).
- `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\*` (no edit; cache is executor-scope).
- `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\artifacts\aggregate.json` (no edit; baseline is captured by V.3, not pre-seeded by reviewer).
- The 7 running `OpenCode.exe` processes (no kill, no restart, no upgrade; user-approval-gated by Task 0.3).
