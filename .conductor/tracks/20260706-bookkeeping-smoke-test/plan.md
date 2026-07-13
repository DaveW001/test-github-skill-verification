# Plan

Track ID: `20260706-bookkeeping-smoke-test`  
Title: Bookkeeping Smoke Test Marker  
Status: planned  
Pipeline mode: `bookkeeping` (`[1, 5, 7, 9]`)

## Goal / Outcome
Create `.conductor/smoke-test-4.2-bookkeeping.md` as a bookkeeping smoke-test marker with the exact requested markdown content.

## Constraints / Non-Goals
- Pure markdown file creation only; no source, tests, build config, schemas, or runtime behavior changes.
- Stage 5 owns execution; this Stage 1 plan does not create the marker file.
- `test_framework: none`; `test_command: n/a`.
- Shell-first execution is required: use PowerShell via the `bash` tool, `-LiteralPath`, double-quoted absolute Windows paths, and bounded/non-interactive commands only.
- If any blocker occurs, stop and report promptly; do not hang, prompt interactively, or retry indefinitely.

## Definition of Done
The marker file exists with exact body content, Conductor ledgers and metadata are synchronized, an execution log records validation and skipped stages, and Stage 9 records a documentation closeout/waiver for the bookkeeping track.

## Checkbox States
- `[ ]` pending
- `[~]` in progress
- `[x]` completed

## Phase 0 Setup & Preconditions

Objective: Confirm the executor can safely run the bookkeeping plan without rediscovery or unintended edits.

### Ordered Checklist

- [x] Confirm the track artifacts exist before implementation.
  - File paths: `.conductor/tracks/20260706-bookkeeping-smoke-test/spec.md`, `.conductor/tracks/20260706-bookkeeping-smoke-test/plan.md`, `.conductor/tracks/20260706-bookkeeping-smoke-test/metadata.json`.
  - Command:
    ```powershell
    $paths = @(
      "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\spec.md",
      "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\plan.md",
      "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\metadata.json"
    ); ($paths | ForEach-Object { Test-Path -LiteralPath $_ }) -join "`n"
    ```
  - Authoritative acceptance check: The command prints exactly three lines, each `True`.
  - Diagnostic checks:
    ```powershell
    Get-ChildItem -LiteralPath "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test" | Select-Object Name,Length
    ```
  - Error recovery: If any line is `False`, stop and report the missing artifact path; do not create the marker file until the plan/spec/metadata are present.

### Exit Criteria
- The executor has verified the active track artifacts exist.

## Phase 1 Implementation

Objective: Create the requested marker file exactly once with deterministic content.

### Ordered Checklist

- [x] Create `.conductor/smoke-test-4.2-bookkeeping.md` with the exact requested markdown body.
  - File path: `.conductor/smoke-test-4.2-bookkeeping.md`.
  - Command:
    ```powershell
    $target = "C:\development\opencode\.conductor\smoke-test-4.2-bookkeeping.md"
    $content = "# Bookkeeping Smoke Test Marker`n`nThe 9-stage Conductor pipeline bookkeeping branch was smoke-tested on 2026-07-06.`nThis track type skips TDD stages (4 Write Tests / 4b RED-gate / 6 Run Tests) and reaches Stage 9 (Documentation / Closeout)."
    Set-Content -LiteralPath $target -Encoding utf8 -Value $content
    ```
  - Authoritative acceptance check: Run the following command and confirm it prints exactly `True`:
    ```powershell
    $target = "C:\development\opencode\.conductor\smoke-test-4.2-bookkeeping.md"
    $expected = "# Bookkeeping Smoke Test Marker`n`nThe 9-stage Conductor pipeline bookkeeping branch was smoke-tested on 2026-07-06.`nThis track type skips TDD stages (4 Write Tests / 4b RED-gate / 6 Run Tests) and reaches Stage 9 (Documentation / Closeout)."
    [string]::Equals((Get-Content -Raw -LiteralPath $target).TrimEnd("`r","`n"), $expected, [System.StringComparison]::Ordinal)
    ```
  - Diagnostic checks:
    ```powershell
    Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\smoke-test-4.2-bookkeeping.md"
    ```
  - Error recovery: If the authoritative check prints `False`, rewrite the file using the command above and rerun the exact comparison once. If it still fails, stop and report the actual raw content length and do not proceed to ledger closeout.

### Exit Criteria
- The marker file exact-content comparison returns `True`.

## Final Phase Validation & Handover

Objective: Synchronize Conductor bookkeeping and leave auditable closeout evidence for Stage 7 and Stage 9.

### Ordered Checklist

- [x] Upsert row for `20260706-bookkeeping-smoke-test` in `.conductor/tracks.md` with status reflecting execution progress.
  - File path: `.conductor/tracks.md`.
  - Command:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks.md"
    $id = "20260706-bookkeeping-smoke-test"
    $row = "| 20260706-bookkeeping-smoke-test | Bookkeeping Smoke Test Marker | bookkeeping | completed | 2026-07-06 | 2026-07-06 | Exact markdown marker file created and validated. |"
    $text = Get-Content -Raw -LiteralPath $path
    $lines = $text -split "`r?`n"
    $matchingIndexes = for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i].Contains($id)) { $i } }
    if ($matchingIndexes.Count -gt 1) { throw "Duplicate tracks.md rows for $id" }
    if ($matchingIndexes.Count -eq 1) { $lines[$matchingIndexes[0]] = $row } else { $lines += $row }
    Set-Content -LiteralPath $path -Encoding utf8 -Value ($lines -join "`n")
    ```
  - Authoritative acceptance check: Run the following command and confirm it prints exactly `1`:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks.md"
    $id = "20260706-bookkeeping-smoke-test"
    @((Get-Content -Raw -LiteralPath $path) -split "`r?`n" | Where-Object { $_.Contains($id) -and $_.Contains("completed") -and $_.Contains("Bookkeeping Smoke Test Marker") }).Count
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\development\opencode\.conductor\tracks.md" -SimpleMatch "20260706-bookkeeping-smoke-test"
    ```
  - Error recovery: If the acceptance check is not `1`, inspect only the matching rows, remove duplicates manually by preserving the most complete row, and rerun the count check.

- [x] Upsert row for `20260706-bookkeeping-smoke-test` in `.conductor/tracks-ledger.md` with final phase/status.
  - File path: `.conductor/tracks-ledger.md`.
  - Command:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks-ledger.md"
    $id = "20260706-bookkeeping-smoke-test"
    $row = "| 20260706-bookkeeping-smoke-test | Bookkeeping Smoke Test Marker | bookkeeping | completed | 2026-07-06 | Stage 9 ready; marker exact-content validation passed. |"
    $text = Get-Content -Raw -LiteralPath $path
    $lines = $text -split "`r?`n"
    $matchingIndexes = for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i].Contains($id)) { $i } }
    if ($matchingIndexes.Count -gt 1) { throw "Duplicate tracks-ledger.md rows for $id" }
    if ($matchingIndexes.Count -eq 1) { $lines[$matchingIndexes[0]] = $row } else { $lines += $row }
    Set-Content -LiteralPath $path -Encoding utf8 -Value ($lines -join "`n")
    ```
  - Authoritative acceptance check: Run the following command and confirm it prints exactly `1`:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks-ledger.md"
    $id = "20260706-bookkeeping-smoke-test"
    @((Get-Content -Raw -LiteralPath $path) -split "`r?`n" | Where-Object { $_.Contains($id) -and $_.Contains("completed") -and $_.Contains("Stage 9 ready") }).Count
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md" -SimpleMatch "20260706-bookkeeping-smoke-test"
    ```
  - Error recovery: If the acceptance check is not `1`, inspect only the matching rows, remove duplicates manually by preserving the most complete row, and rerun the count check.

- [x] Create `.conductor/tracks/20260706-bookkeeping-smoke-test/execution-log-2026-07-06.md` documenting changed files, validation, skipped stages, and deviations.
  - File path: `.conductor/tracks/20260706-bookkeeping-smoke-test/execution-log-2026-07-06.md`.
  - Command:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\execution-log-2026-07-06.md"
    $content = "# Execution Log - 20260706-bookkeeping-smoke-test`n`nChanged files:`n- C:\development\opencode\.conductor\smoke-test-4.2-bookkeeping.md`n- C:\development\opencode\.conductor\tracks.md`n- C:\development\opencode\.conductor\tracks-ledger.md`n- C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\plan.md`n- C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\metadata.json`n`nValidation performed:`n- Exact content comparison for the smoke-test marker returned True.`n- tracks.md duplicate/status count returned 1.`n- tracks-ledger.md duplicate/status count returned 1.`n`nSkipped stages:`n- Stage 2 skipped: trivial deterministic bookkeeping plan.`n- Stage 3 skipped: no re-review required.`n- Stage 4 skipped: no tests for bookkeeping markdown marker.`n- Stage 4b skipped: RED gate not applicable.`n- Stage 6 skipped: test_command is n/a.`n- Stage 8 skipped: conditional re-validation not required unless Stage 7 finds issues.`n`nDeviations:`n- None observed during execution, or list any deviations here before closeout."
    Set-Content -LiteralPath $path -Encoding utf8 -Value $content
    ```
  - Authoritative acceptance check: Run the following command and confirm it prints exactly `True`:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\execution-log-2026-07-06.md"
    $body = Get-Content -Raw -LiteralPath $path
    $body.Contains("Exact content comparison for the smoke-test marker returned True.") -and $body.Contains("Stage 4 skipped: no tests for bookkeeping markdown marker.") -and $body.Contains("Stage 6 skipped: test_command is n/a.")
    ```
  - Diagnostic checks:
    ```powershell
    Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\execution-log-2026-07-06.md"
    ```
  - Error recovery: If the check prints `False`, rewrite the log so it includes the exact validation and skipped-stage sentences, then rerun the check.

- [x] Synchronize `.conductor/tracks/20260706-bookkeeping-smoke-test/metadata.json` and this `plan.md` after all prior tasks complete.
  - File paths: `.conductor/tracks/20260706-bookkeeping-smoke-test/metadata.json`, `.conductor/tracks/20260706-bookkeeping-smoke-test/plan.md`.
  - Command:
    ```powershell
    $metadataPath = "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\metadata.json"
    $metadata = Get-Content -Raw -LiteralPath $metadataPath | ConvertFrom-Json
    $metadata.status = "completed"
    $metadata.progress.phase = "Final Phase Validation & Handover"
    $metadata.progress.completedTasks = $metadata.progress.totalTasks
    $metadata.progress.percentage = 100
    $metadata.completed_at = "2026-07-06"
    $metadata | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $metadataPath -Encoding utf8
    $planPath = "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\plan.md"
    $plan = Get-Content -Raw -LiteralPath $planPath
    $plan = $plan.Replace("- [ ] Confirm the track artifacts exist before implementation.", "- [x] Confirm the track artifacts exist before implementation.")
    $plan = $plan.Replace("- [ ] Create `.conductor/smoke-test-4.2-bookkeeping.md` with the exact requested markdown body.", "- [x] Create `.conductor/smoke-test-4.2-bookkeeping.md` with the exact requested markdown body.")
    $plan = $plan.Replace("- [ ] Upsert row for `20260706-bookkeeping-smoke-test` in `.conductor/tracks.md` with status reflecting execution progress.", "- [x] Upsert row for `20260706-bookkeeping-smoke-test` in `.conductor/tracks.md` with status reflecting execution progress.")
    $plan = $plan.Replace("- [ ] Upsert row for `20260706-bookkeeping-smoke-test` in `.conductor/tracks-ledger.md` with final phase/status.", "- [x] Upsert row for `20260706-bookkeeping-smoke-test` in `.conductor/tracks-ledger.md` with final phase/status.")
    $plan = $plan.Replace("- [ ] Create `.conductor/tracks/20260706-bookkeeping-smoke-test/execution-log-2026-07-06.md` documenting changed files, validation, skipped stages, and deviations.", "- [x] Create `.conductor/tracks/20260706-bookkeeping-smoke-test/execution-log-2026-07-06.md` documenting changed files, validation, skipped stages, and deviations.")
    $plan = $plan.Replace("- [ ] Synchronize `.conductor/tracks/20260706-bookkeeping-smoke-test/metadata.json` and this `plan.md` after all prior tasks complete.", "- [x] Synchronize `.conductor/tracks/20260706-bookkeeping-smoke-test/metadata.json` and this `plan.md` after all prior tasks complete.")
    Set-Content -LiteralPath $planPath -Encoding utf8 -Value $plan
    ```
  - Authoritative acceptance check: Run the following command and confirm it prints exactly `True`:
    ```powershell
    $metadata = Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\metadata.json" | ConvertFrom-Json
    $plan = Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\plan.md"
    ($metadata.status -eq "completed") -and ($metadata.progress.percentage -eq 100) -and (-not $plan.Contains("- [ ] Confirm the track artifacts exist before implementation.")) -and (-not $plan.Contains("- [ ] Create `.conductor/smoke-test-4.2-bookkeeping.md` with the exact requested markdown body."))
    ```
  - Diagnostic checks:
    ```powershell
    Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260706-bookkeeping-smoke-test\metadata.json" | ConvertFrom-Json | ConvertTo-Json -Depth 10
    ```
  - Error recovery: If the check prints `False`, update only the missing status/progress fields or unchecked task lines, then rerun the authoritative check.

### Exit Criteria
- Marker exact-content check returns `True`.
- tracks.md count check returns `1`.
- tracks-ledger.md count check returns `1`.
- Execution log content check returns `True`.
- Metadata/plan synchronization check returns `True`.

## Execution-Readiness Checklist
- [ ] The plan uses PowerShell shell-first commands only.
- [ ] Every executable task has exactly one `Authoritative acceptance check:` label.
- [ ] Diagnostic checks are separated from authoritative checks.
- [ ] The marker-file verification checks the full intended body content, not a heading-only or phrase-only match.
- [ ] Ledger tasks use “Upsert row” wording and include duplicate-count acceptance checks.
- [ ] Stage 4, Stage 4b, and Stage 6 are intentionally skipped for `track_type: bookkeeping`.

## Top 3 Risks + Mitigations
1. Risk: UTF-8 BOM or newline differences could make exact comparison confusing. Mitigation: Compare `Get-Content -Raw` after trimming only trailing CR/LF and use ordinal string equality against the exact expected body.
2. Risk: Ledger upserts could create duplicate rows. Mitigation: Each ledger task checks matching rows first, throws on duplicates, and requires a count of exactly `1` after the upsert.
3. Risk: Native file tools remain unavailable. Mitigation: All commands are written for PowerShell via `bash`, with `-LiteralPath`, double-quoted absolute Windows paths, and no interactive operations.

## First Task To Execute
Confirm the track artifacts exist before implementation in Phase 0.


