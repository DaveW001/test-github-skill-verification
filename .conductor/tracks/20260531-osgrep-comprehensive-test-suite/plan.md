# Plan: OsGrep Comprehensive Test Suite

**Track ID**: 20260531-osgrep-comprehensive-test-suite
**Spec**: [spec.md](./spec.md)
**Created**: 2026-05-31
**Status**: Completed
**Priority**: High

---

## Objective

Execute all 44 test cases across 8 capability categories using the existing `osgrep_debug_wrapper.py` harness. Create a unified Python test runner, run every test with timestamped JSON logs, aggregate results into a pass/fail report, and verify OsGrep is healthy for continued production use.

---

## Legend

- **[BLOCKING]**: Must pass for GO. Failures here block the track.
- **[NON-BLOCKING]**: Should pass, but failure is documented (not blocking).
- `[x]` = completed, `[ ]` = pending, `[~]` = in progress

---

## Phase 0: Setup and Preconditions

**Objective**: Verify all prerequisites exist and create the test runner script.

- [x] 0.1 **Verify osgrep CLI is installed and functional.**
  Command: `osgrep --version`
  Expected: Output contains `0.5.16` or higher.
  Fallback: If not found, run `npm install -g osgrep` and retry.

- [x] 0.2 **Verify osgrep doctor reports all checks passed.**
  Command: `osgrep doctor`
  Expected: All lines contain `✅` (green check). No `❌` (red X) present.
  Fallback: If models missing, run `osgrep setup`. If index missing, proceed (will be created in Phase 2).

- [x] 0.3 **Verify debug wrapper script exists.**
  Command: `Test-Path "C:\development\opencode\scripts\utils\osgrep_debug_wrapper.py"`
  Expected: Returns `True`.
  Fallback: If missing, copy from a backup or re-clone the repo.

- [x] 0.4 **Verify process snapshot script exists.**
  Command: `Test-Path "C:\development\opencode\scripts\utils\osgrep_process_snapshot.ps1"`
  Expected: Returns `True`.
  Fallback: If missing, skip process snapshot tests (TC-G2) and note in report.

- [x] 0.5 **Create output directories.**
  Commands:
  ```
  New-Item -ItemType Directory -Force -Path "C:\development\opencode\logs\osgrep-test-suite" | Out-Null
  New-Item -ItemType Directory -Force -Path "C:\development\opencode\scripts\tests" | Out-Null
  ```
  Verification: `Test-Path "C:\development\opencode\logs\osgrep-test-suite"` returns `True`.

- [x] 0.6 **Verify the unified test runner script exists at ``C:\development\opencode\scripts\tests\osgrep_test_suite.py``.**
  This script was pre-created by the Planner agent. Verify it works:
  ```
  python scripts/tests/osgrep_test_suite.py --help
  ```
  Expected: Shows ``--report`` and ``--list`` options.
  Fallback: If missing or broken, recreate from Appendix A.
  Key capabilities:
  - ``--report``: scans ``logs/osgrep-debug/`` for ``result.json``, generates ``logs/osgrep-test-suite/report.md``
  - ``--list``: lists all available result.json files with status
  - Classifies tests as BLOCKING or NON-BLOCKING by matching label patterns
  - BLOCKING labels: tc-a1-version-check, tc-a2-doctor-check, tc-b1 through tc-b6, tc-c1 through tc-c4, tc-f1-mcp-guardrail, tc-f2-tool-path, tc-f3-forced-failure
  - NON-BLOCKING labels: tc-a3-model-verify, tc-c5 through tc-c12, tc-d1 through tc-d8, tc-e1 through tc-e9, tc-g1, tc-g2
  - Evaluates: exit_code 0 = PASS, timed_out = TIMEOUT, else FAIL (expected-failure labels always PASS)
  - Scans stderr for critical patterns: "Table 'chunks' already exists", "UnicodeDecodeError"
  - GO/NO-GO: GO only if ALL blocking tests PASS with no timeouts
  - Uses ``Path(__file__).resolve().parent.parent.parent`` for repo root
- [x] 0.7 **Kill any stale osgrep helper processes.**
  Command: `taskkill /F /T /IM osgrep-nodejs-helper.exe 2>$null; Write-Output "Cleanup done"`
  Verification: `Get-Process osgrep-nodejs-helper -ErrorAction SilentlyContinue` returns nothing.

- [x] 0.8 **Verify the repo has enough files for meaningful searches.**
  Command: ``Get-ChildItem -Recurse -File -Path "C:\development\opencode\scripts" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count``
  Expected: Returns a number > 0.
  Fallback: If ``scripts`` is empty, use the full repo root ``C:\development\opencode`` (will be slower).
  Command: `Get-ChildItem -Recurse -File -Path "C:\development\opencode\src" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count`
  Expected: Returns a number > 0.
  Fallback: If `src` is empty, use `C:\development\opencode\scripts` for search scope.

### Phase 0 Exit Criteria
### Reusable Verification Helper (PowerShell)

Use this function to check any test's result.json for exit_code 0:
`powershell
function Test-OsgrepResult {
    param([string])
     = Get-ChildItem "C:\development\opencode\logs\osgrep-debug" -Directory | Where-Object { .Name -like "**" } | Select-Object -First 1
    if (-not ) { Write-Output "MISSING: "; return 1 }
     = Get-Content "\result.json" -Raw | ConvertFrom-Json
    if (.exit_code -eq 0) { Write-Output "PASS:  (exit_code=0, s)" ; return 0 }
    if (.timed_out) { Write-Output "TIMEOUT: "; return 2 }
    Write-Output "FAIL:  (exit_code=)"; return 1
}
# Usage: Test-OsgrepResult "tc-a1-version-check"
- All 8 preconditions pass. Test runner script verified. Output directories exist. No stale processes.

---

## Phase 1: Health and Readiness Tests (TC-A1..A3)

**Objective**: Verify osgrep is installed, healthy, and models are present. All blocking.

- [x] 1.1 **[BLOCKING] TC-A1: Version check.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-a1-version-check --timeout 30 --cwd C:/development/opencode -- -- --version
  ```
  Verification: Check `logs/osgrep-debug/*-tc-a1-version-check/result.json`. `exit_code` is `0`, `stdout` contains version string matching `\d+\.\d+\.\d+`.

- [x] 1.2 **[BLOCKING] TC-A2: Doctor check.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-a2-doctor-check --timeout 30 --cwd C:/development/opencode -- -- doctor
  ```
  Verification: `exit_code` is `0`. `stdout` contains no `❌` and at least 5 `✅`. If any model is missing, mark as FAIL with note.

- [x] 1.3 **[BLOCKING] TC-A3: Model files verification.**
  Command:
  ```
  $modelDir = "$env:USERPROFILE\.osgrep\models"; if (Test-Path $modelDir) { Get-ChildItem -Recurse -Directory -Path $modelDir | Measure-Object | Select-Object -ExpandProperty Count } else { 0 }
  ```
  Expected: Returns > 0 (at least one model directory found).
  Fallback: If 0, run `osgrep setup` and retry once.

### Phase 1 Exit Criteria
- All 3 health tests pass. OsGrep confirmed installed, healthy, models present.


---

## Phase 2: Index Operations (TC-B1..B6)

**Objective**: Validate index commands work correctly across all flags. All blocking.

- [x] 2.1 **[BLOCKING] TC-B1: Index dry-run.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-b1-index-dry-run --timeout 120 --cwd C:/development/opencode -- -- index --dry-run
  ```
  Exit criteria: `exit_code` is `0`. No errors in `stderr`. Under 120s.
  Fallback: If timeout, add `--path C:/development/opencode/src`.

- [x] 2.2 **[BLOCKING] TC-B2: Full index (verbose, reset).**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-b2-index-verbose --timeout 300 --cwd C:/development/opencode -- -- index --verbose --reset
  ```
  Exit criteria: `exit_code` is `0`. `stdout` shows progress lines with filenames. No `Table 'chunks' already exists` in `stderr`.
  Fallback: If timeout > 300s, retry without `--verbose`.

- [x] 2.3 **[BLOCKING] TC-B3: Index with --path flag.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-b3-index-path --timeout 120 --cwd C:/development/opencode -- -- index --path C:/development/opencode/scripts
  ```
  Exit criteria: `exit_code` is `0`. Verify results by searching: `python scripts/utils/osgrep_debug_wrapper.py --label tc-b3-search-verify --timeout 30 --cwd C:/development/opencode -- -- search "debug_wrapper" C:/development/opencode/scripts` -- results should appear.

- [x] 2.4 **[BLOCKING] TC-B4: Index with --reset flag.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-b4-index-reset --timeout 300 --cwd C:/development/opencode -- -- index --reset --verbose
  ```
  Exit criteria: `exit_code` is `0`. `stderr` has no chunks table error. Run `osgrep list` after -- timestamps are current.

- [x] 2.5 **[BLOCKING] TC-B5: Search with --sync flag.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-b5-search-sync --timeout 120 --cwd C:/development/opencode -- -- search "auth token refresh" --sync
  ```
  Exit criteria: `exit_code` is `0`. `stdout` contains results. Under 120s.

- [x] 2.6 **[BLOCKING] TC-B6: List index contents.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-b6-list --timeout 30 --cwd C:/development/opencode -- -- list
  ```
  Exit criteria: `exit_code` is `0`. `stdout` shows `.osgrep` contents.

### Phase 2 Exit Criteria
- All 6 index tests pass. No `Table 'chunks' already exists` errors. Index is fresh and listable.

---

## Phase 3: Core Search Tests (TC-C1..C4)

**Objective**: Validate basic semantic search. All blocking.

- [x] 3.1 **[BLOCKING] TC-C1: Known-answer search.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c1-known-answer --timeout 60 --cwd C:/development/opencode -- -- search "osgrep_debug_wrapper" --max-count 10
  ```
  Exit criteria: `exit_code` is `0`. `stdout` contains `osgrep_debug_wrapper.py`. Not empty.
  Fallback: If no results, run `osgrep index --sync` and retry.

- [x] 3.2 **[BLOCKING] TC-C2: Search with --max-count flag.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c2-max-count --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --max-count 3
  ```
  Exit criteria: `exit_code` is `0`. Check results show at most 3 matches.

- [x] 3.3 **[BLOCKING] TC-C3: Search with --content flag.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c3-content --timeout 60 --cwd C:/development/opencode -- -- search "auth token refresh" --content --max-count 2
  ```
  Exit criteria: `exit_code` is `0`. Output shows multi-line code blocks (not one-liner snippets).

- [x] 3.4 **[BLOCKING] TC-C4: Search with --scores flag.**
  Command:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c4-scores --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --scores --max-count 3
  ```
  Exit criteria: `exit_code` is `0`. Output contains relevance score values.

### Phase 3 Exit Criteria
- All 4 core search tests pass. Known-answer query returns expected results.

---

## Phase 4: Search Flag Tests (TC-C5..C12)

**Objective**: Validate remaining search flags. Non-blocking.

- [x] 4.1 **[NON-BLOCKING] TC-C5: Search with --min-score.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c5-min-score --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --scores --min-score 0.3 --max-count 5
  ```
  Exit criteria: `exit_code` is `0`. Returns results with score >= 0.3.

- [x] 4.2 **[NON-BLOCKING] TC-C6: Search with --compact.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c6-compact --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --compact --max-count 3
  ```
  Exit criteria: `exit_code` is `0`. Output is compact format.

- [x] 4.3 **[NON-BLOCKING] TC-C7: Search with --plain.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c7-plain --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --plain --max-count 3
  ```
  Exit criteria: `exit_code` is `0`. No ANSI escape codes in raw output.

- [x] 4.4 **[NON-BLOCKING] TC-C8: Search with --skeleton.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c8-skeleton --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --skeleton --max-count 3
  ```
  Exit criteria: `exit_code` is `0`. Output contains code structural elements.

- [x] 4.5 **[NON-BLOCKING] TC-C9: Search with --per-file.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c9-per-file --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --per-file 2 --max-count 10
  ```
  Exit criteria: `exit_code` is `0`. No more than 2 results per file.

- [x] 4.6 **[NON-BLOCKING] TC-C10: Search with --dry-run.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c10-dry-run --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --dry-run --max-count 5
  ```
  Exit criteria: `exit_code` is `0`. Output describes what would happen.

- [x] 4.7 **[NON-BLOCKING] TC-C11: Search in subdirectory.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c11-subdir --timeout 60 --cwd C:/development/opencode -- -- search "osgrep" C:/development/opencode/scripts
  ```
  Exit criteria: `exit_code` is `0`. All results are under `scripts/`.

- [x] 4.8 **[NON-BLOCKING] TC-C12: Search with --sync.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-c12-sync --timeout 120 --cwd C:/development/opencode -- -- search "conductor" --sync --max-count 5
  ```
  Exit criteria: `exit_code` is `0`. Completes under 120s.

### Phase 4 Exit Criteria
- At least 6 of 8 search flag tests pass. Failures documented.


---

## Phase 5: Symbols, Skeleton, and Trace Tests (TC-D1..D8)

**Objective**: Validate symbol listing, skeleton, trace. Non-blocking.

- [x] 5.1 **[NON-BLOCKING] TC-D1: List symbols.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d1-symbols --timeout 60 --cwd C:/development/opencode -- -- symbols --limit 10
  ```
  Exit: `exit_code` is `0`. Lists >= 5 symbols with file paths.

- [x] 5.2 **[NON-BLOCKING] TC-D2: Symbols with pattern filter.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d2-symbols-filter --timeout 60 --cwd C:/development/opencode -- -- symbols "osgrep" --limit 10
  ```
  Exit: `exit_code` is `0`. All symbols contain "osgrep".

- [x] 5.3 **[NON-BLOCKING] TC-D3: Symbols with custom --limit.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d3-symbols-limit --timeout 60 --cwd C:/development/opencode -- -- symbols --limit 3
  ```
  Exit: `exit_code` is `0`. Lists <= 3 symbols.

- [x] 5.4 **[NON-BLOCKING] TC-D4: Symbols with --path prefix.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d4-symbols-path --timeout 60 --cwd C:/development/opencode -- -- symbols --path scripts --limit 10
  ```
  Exit: `exit_code` is `0`. All paths start with `scripts/`.

- [x] 5.5 **[NON-BLOCKING] TC-D5: Skeleton for a file.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d5-skeleton-file --timeout 60 --cwd C:/development/opencode -- -- skeleton scripts/utils/osgrep_debug_wrapper.py
  ```
  Exit: `exit_code` is `0`. Shows function signatures.

- [x] 5.6 **[NON-BLOCKING] TC-D6: Skeleton for a symbol.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d6-skeleton-symbol --timeout 60 --cwd C:/development/opencode -- -- skeleton "main" --limit 3
  ```
  Exit: `exit_code` is `0`. Finds at least one definition for "main".

- [x] 5.7 **[NON-BLOCKING] TC-D7: Skeleton as JSON.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d7-skeleton-json --timeout 60 --cwd C:/development/opencode -- -- skeleton scripts/utils/osgrep_debug_wrapper.py --json --no-summary
  ```
  Exit: `exit_code` is `0`. Output contains valid JSON.

- [x] 5.8 **[NON-BLOCKING] TC-D8: Trace a symbol.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-d8-trace --timeout 60 --cwd C:/development/opencode -- -- trace "main"
  ```
  Exit: `exit_code` is `0`. Output shows call graph info.

### Phase 5 Exit Criteria
- At least 6 of 8 tests pass.

---

## Phase 6: Reliability and Edge Case Tests (TC-E1..E9)

**Objective**: Stress-test under concurrent, stale, and edge conditions. Non-blocking.

- [x] 6.1 **[NON-BLOCKING] TC-E1: Sequential queries (simulates concurrency).**
  Run two searches back-to-back. If Start-Job is available, try concurrent first; otherwise run sequentially.
  Step 1 - Query A:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e1-concurrent-a --timeout 90 --cwd C:/development/opencode -- -- search "conductor track" --max-count 5
  ```
  Step 2 - Query B:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e1-concurrent-b --timeout 90 --cwd C:/development/opencode -- -- search "auth token" --max-count 5
  ```
  Verification for each:
  ```
  Test-OsgrepResult "tc-e1-concurrent-a"
  Test-OsgrepResult "tc-e1-concurrent-b"
  ```
  Exit: Both exit_code 0, neither timed out.
  Note: True concurrency via Start-Job is optional. Sequential execution validates the same code paths without Windows job-hang risk.
  Commands:
  ```
  Start-Job -Name "osgrep-concurrent-a" -ScriptBlock { Set-Location C:\development\opencode; python scripts/utils/osgrep_debug_wrapper.py --label tc-e1-concurrent-a --timeout 90 --cwd C:/development/opencode -- -- search "conductor track" --max-count 5 }
  Start-Job -Name "osgrep-concurrent-b" -ScriptBlock { Set-Location C:\development\opencode; python scripts/utils/osgrep_debug_wrapper.py --label tc-e1-concurrent-b --timeout 90 --cwd C:/development/opencode -- -- search "auth token" --max-count 5 }
  Wait-Job -Name "osgrep-concurrent-a", "osgrep-concurrent-b" | Out-Null
  Get-Job -Name "osgrep-concurrent-a" | Receive-Job
  Get-Job -Name "osgrep-concurrent-b" | Receive-Job
  ```
  Exit: Both exit_code 0, neither timed out.
  Fallback: If Start-Job hangs, run sequentially and note limitation.

- [x] 6.2 **[NON-BLOCKING] TC-E2: Query during active index.**
  Step 1 - Start index in background (if Start-Job works):
  ```
  Start-Job -Name "osgrep-index-bg" -ScriptBlock { Set-Location C:\development\opencode; osgrep index --path C:/development/opencode/scripts --verbose --reset }
  Start-Sleep -Seconds 3
  ```
  Step 2 - Run search while indexing:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e2-query-during-index --timeout 120 --cwd C:/development/opencode -- -- search "conductor" --max-count 5
  ```
  Step 3 - Wait for background job:
  ```
  Wait-Job -Name "osgrep-index-bg" -ErrorAction SilentlyContinue | Out-Null
  ```
  Fallback (if Start-Job fails): Run index first, then search immediately after.
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e2-index-first --timeout 120 --cwd C:/development/opencode -- -- index --path C:/development/opencode/scripts --reset
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e2-query-after-index --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --max-count 5
  ```
  Verification:
  ```
  Test-OsgrepResult "tc-e2-query-during-index"
  ```
  Exit: Search completes without hang.
  Commands:
  ```
  Start-Job -Name "osgrep-index-bg" -ScriptBlock { Set-Location C:\development\opencode; osgrep index --path C:/development/opencode/scripts --verbose --reset }
  Start-Sleep -Seconds 3
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e2-query-during-index --timeout 120 --cwd C:/development/opencode -- -- search "conductor" --max-count 5
  Wait-Job -Name "osgrep-index-bg" | Out-Null
  ```
  Exit: Search completes without hang.

- [x] 6.3 **[NON-BLOCKING] TC-E3: Stale index query.**
  Step 1 - Create marker file:
  ```
  $marker = "STALE_TEST_MARKER_$(Get-Random)"; Set-Content -Path "C:\development\opencode\temp_stale_test.py" -Value "# $marker"
  ```
  Step 2 - Sync index to include marker:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e3a-index-stale --timeout 120 --cwd C:/development/opencode -- -- index --sync
  ```
  Step 3 - Search for marker (should find it):
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e3b-search-fresh --timeout 60 --cwd C:/development/opencode -- -- search "$marker" --max-count 3
  ```
  Step 4 - Delete marker file:
  ```
  Remove-Item "C:\development\opencode\temp_stale_test.py"
  ```
  Step 5 - Search again (stale index may still find it):
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e3c-search-after-delete --timeout 60 --cwd C:/development/opencode -- -- search "$marker" --max-count 3
  ```
  Verification:
  ```
  Test-OsgrepResult "tc-e3a-index-stale"
  Test-OsgrepResult "tc-e3b-search-fresh"
  Test-OsgrepResult "tc-e3c-search-after-delete"
  ```
  Exit: Step 3 finds marker in stdout. Step 5 behavior (found/not-found) documented in report.
  Steps:
  1. `$marker = "STALE_TEST_MARKER_$(Get-Random)"; Set-Content -Path "C:\development\opencode\temp_stale_test.py" -Value "# $marker"`
  2. `python scripts/utils/osgrep_debug_wrapper.py --label tc-e3a-index-stale --timeout 120 --cwd C:/development/opencode -- -- index --sync`
  3. `python scripts/utils/osgrep_debug_wrapper.py --label tc-e3b-search-fresh --timeout 60 --cwd C:/development/opencode -- -- search "$marker" --max-count 3`
  4. `Remove-Item "C:\development\opencode\temp_stale_test.py"`
  5. `python scripts/utils/osgrep_debug_wrapper.py --label tc-e3c-search-after-delete --timeout 60 --cwd C:/development/opencode -- -- search "$marker" --max-count 3`
  Exit: Step 3 finds marker. Step 5 behavior documented.

- [x] 6.4 **[NON-BLOCKING] TC-E4: Path with spaces.**
  Step 1 - Create directory with spaces and test file:
  ```
  $spacedDir = "C:\development\opencode\osgrep test space"; New-Item -ItemType Directory -Force -Path $spacedDir | Out-Null; Set-Content -Path "$spacedDir\sample.py" -Value "def spaces_test_function():`n    return 'spaces work'"
  ```
  Step 2 - Index from spaced directory:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e4a-spaced-index --timeout 60 --cwd "$spacedDir" -- -- index
  ```
  Step 3 - Search from spaced directory:
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e4b-spaced-search --timeout 60 --cwd "$spacedDir" -- -- search "spaces_test_function"
  ```
  Step 4 - Cleanup:
  ```
  Remove-Item -Recurse -Force "$spacedDir"
  ```
  Verification:
  ```
  Test-OsgrepResult "tc-e4a-spaced-index"
  Test-OsgrepResult "tc-e4b-spaced-search"
  ```
  Exit: Both exit_code 0. Step 3 stdout contains ``spaces_test_function``.
  Steps:
  1. `$spacedDir = "C:\development\opencode\osgrep test space"; New-Item -ItemType Directory -Force -Path $spacedDir | Out-Null; Set-Content -Path "$spacedDir\sample.py" -Value "def spaces_test_function():`n    return 'spaces work'"`
  2. `python scripts/utils/osgrep_debug_wrapper.py --label tc-e4a-spaced-index --timeout 60 --cwd "$spacedDir" -- -- index`
  3. `python scripts/utils/osgrep_debug_wrapper.py --label tc-e4b-spaced-search --timeout 60 --cwd "$spacedDir" -- -- search "spaces_test_function"`
  4. `Remove-Item -Recurse -Force "$spacedDir"`
  Exit: Both exit 0. Search finds expected function.

- [x] 6.5 **[NON-BLOCKING] TC-E5: Non-existent CWD.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e5-nonexistent-cwd --timeout 30 --cwd C:/development/opencode/does-not-exist-qwerty -- -- search "test"
  ```
  Exit: Wrapper handles gracefully, creates result.json with error info. No hang.

- [x] 6.6 **[NON-BLOCKING] TC-E6: Empty search pattern.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e6-empty-pattern --timeout 30 --cwd C:/development/opencode -- -- search ""
  ```
  Exit: Process exits (not hang), result.json generated.

- [x] 6.7 **[NON-BLOCKING] TC-E7: Very long search pattern.**
  ```
  $longPattern = "a" * 500; python scripts/utils/osgrep_debug_wrapper.py --label tc-e7-long-pattern --timeout 60 --cwd C:/development/opencode -- -- search $longPattern --max-count 3
  ```
  Exit: Completes without crash.

- [x] 6.8 **[NON-BLOCKING] TC-E8: Timing baseline.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-e8-timing --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --max-count 10
  ```
  Exit: `exit_code` is `0`. Record `duration_seconds` for regression baseline (< 30s expected).

- [x] 6.9 **[NON-BLOCKING] TC-E9: Cold-start query.**
  ```
  taskkill /F /T /IM osgrep-nodejs-helper.exe 2>$null; python scripts/utils/osgrep_debug_wrapper.py --label tc-e9-cold-start --timeout 120 --cwd C:/development/opencode -- -- search "conductor" --max-count 5
  ```
  Exit: `exit_code` is `0`. Under 120s cold start.

### Phase 6 Exit Criteria
- At least 7 of 9 reliability tests pass. No hangs or crashes.

---

## Phase 7: Guardrails and Tool-Path Tests (TC-F1..F3)

**Objective**: Verify MCP guardrail, tool-path activation, fallback. All blocking.

- [x] 7.1 **[BLOCKING] TC-F1: MCP guardrail.**
  Command: `osgrep mcp --help 2>&1 | Select-Object -First 10`
  Exit: Does not hang. Shows help or starts with clear indication.
  Note: Full tool-path MCP guardrail test (tool response to `{"argv":["mcp"]}`) requires an OpenCode session.

- [x] 7.2 **[CONDITIONAL BLOCKING] TC-F2: Tool-path activation.**
  **IMPORTANT**: This test CANNOT run from CLI-only. It requires an OpenCode session to invoke the osgrep tool.
  If running from CLI-only: Skip this test, mark as CONDITIONAL BLOCKING, and add note to report: "TC-F2 requires OpenCode session for verification."
  In an OpenCode session, invoke the osgrep tool with:
  ```json
  {"argv": ["--", "search", "conductor", "--max-count", "3"]}
  ```
  Expected: Response contains ACTUAL search results (file paths with matches). NOT static guidance text.
  PASS: Response has file paths and match content.
  FAIL: Response is ONLY static guidance text.
  CLI-only fallback: Mark as SKIPPED (CONDITIONAL) in report. Re-verify in next OpenCode session.
  This MUST be tested in an OpenCode session. Invoke the osgrep tool:
  ```json
  {"argv": ["--", "search", "conductor", "--max-count", "3"]}
  ```
  Expected: Response contains ACTUAL search results (file paths with matches). NOT static guidance text.
  PASS: Response has file paths and match content.
  FAIL: Response is ONLY static guidance text.
  If running from CLI-only: mark as CONDITIONAL BLOCKING with note to re-verify in OpenCode.

- [x] 7.3 **[BLOCKING] TC-F3: Fallback behavior.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-f3-forced-failure --timeout 30 --cwd C:/development/opencode/xyznonexistent987 -- -- search "test"
  ```
  Then: `rg -l "conductor" C:\development\opencode 2>$null`
  Exit: Wrapper creates result.json with error info. Grep returns results.

### Phase 7 Exit Criteria
- TC-F1 and TC-F3 pass. TC-F2 is CONDITIONAL BLOCKING: pass in OpenCode, or SKIPPED in CLI-only with note to re-verify.


---

## Phase 8: Tooling Validation Tests (TC-G1..G3)

**Objective**: Validate test harness tooling. Non-blocking.

- [x] 8.1 **[NON-BLOCKING] TC-G1: Debug wrapper baseline.**
  ```
  python scripts/utils/osgrep_debug_wrapper.py --label tc-g1-wrapper-baseline --timeout 30 --cwd C:/development/opencode -- -- search "test" --max-count 1
  ```
  Exit: result.json has all fields: label, started, cwd, command, exit_code, stdout, stderr, timed_out, duration_seconds, finished.

- [x] 8.2 **[NON-BLOCKING] TC-G2: Process snapshot script.**
  ```
  powershell -ExecutionPolicy Bypass -File "C:\development\opencode\scripts\utils\osgrep_process_snapshot.ps1" -Label "tc-g2" -OutputDir "C:\development\opencode\logs\osgrep-test-suite" -TargetCwd "C:\development\opencode"
  ```
  Exit: Three files created: processes-*.txt, process-tree-*.txt, db-paths-*.txt.

- [x] 8.3 **[NON-BLOCKING] TC-G3: Log directory health.**
  ```
  Get-ChildItem -LiteralPath "C:\development\opencode\logs\osgrep-debug" -Recurse -File -Filter "result.json" | Measure-Object | Select-Object -ExpandProperty Count
  ```
  Exit: Returns count of > 0 result.json files. Informational only.

### Phase 8 Exit Criteria
- Wrapper produces valid JSON. Process snapshot functional. Log structure verified.

---

## Phase 9: Results Aggregation and Report

**Objective**: Aggregate all test results into a pass/fail report.

- [x] 9.1 **Run the test aggregator script.**
  Command: `python C:\development\opencode\scripts\tests\osgrep_test_suite.py --report`
  Expected: Scans `logs/osgrep-debug/` for result.json files and generates `logs/osgrep-test-suite/report.md`.
  Fallback: Manually count result directories: `Get-ChildItem "C:\development\opencode\logs\osgrep-debug" -Directory | Where-Object { $_.Name -like "*tc-*" } | Measure-Object | Select-Object -ExpandProperty Count`

- [x] 9.2 **Count blocking test results.**
  From report.md: ALL 15 unconditional blocking tests (TC-A1..A3, TC-B1..B6, TC-C1..C4, TC-F1, TC-F3) should PASS. TC-F2 is CONDITIONAL BLOCKING - pass in OpenCode or SKIPPED in CLI-only.

- [x] 9.3 **Count non-blocking test results.**
  From report.md: at least 22 of 28 non-blocking tests should pass (>= 78%).

- [x] 9.4 **Check for critical error patterns.**
  Scan blocking test stderr for: `Table 'chunks' already exists`, `UnicodeDecodeError`. Report matches.

- [x] 9.5 **Verify final report has all sections.**
  Expected sections in report.md: Summary, Blocking Tests table, Non-Blocking Tests table, Critical Error Patterns, Recommendations. GO/NO-GO recommendation stated.

### Phase 9 Exit Criteria
- report.md generated and complete. All 16 blocking tests PASS. GO/NO-GO stated.

---

## Phase 10: Validation and Handover

**Objective**: Final validation, cleanup, and track closure.

- [x] 10.1 **Verify report.md exists and is substantive.**
  Command: `Test-Path "C:\development\opencode\logs\osgrep-test-suite\report.md"` returns True.
  Read first 30 lines: `Get-Content "C:\development\opencode\logs\osgrep-test-suite\report.md" -TotalCount 30`

- [x] 10.2 **Verify all blocking test log directories exist.**
  Command:
  ```
  @("tc-a1-version-check","tc-a2-doctor-check","tc-b1-index-dry-run","tc-b2-index-verbose","tc-b3-index-path","tc-b4-index-reset","tc-b5-search-sync","tc-b6-list","tc-c1-known-answer","tc-c2-max-count","tc-c3-content","tc-c4-scores","tc-f1-mcp-guardrail","tc-f2-tool-path","tc-f3-forced-failure") | ForEach-Object { $found = Get-ChildItem "C:\development\opencode\logs\osgrep-debug" -Directory | Where-Object { $_.Name -like "*$_*" }; Write-Output "$_ : $(if($found){'FOUND'}else{'MISSING'})" }
  ```
  Expected: All 16 show FOUND.

- [x] 10.3 **Clean up temp files.**
  ```
  Remove-Item -LiteralPath "C:\development\opencode\temp_stale_test.py" -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath "C:\development\opencode\osgrep test space" -Recurse -Force -ErrorAction SilentlyContinue
  ```

- [x] 10.4 **Update metadata.json with test results.**
  Edit `C:\development\opencode\.conductor\tracks\20260531-osgrep-comprehensive-test-suite\metadata.json`:
  - Update `testSummary` with actual pass/fail/timeout counts.
  - Update `status` to `"completed"` (if all blocking pass) or `"active"`.
  - Update `completed` date if completed.
  - Update `tasks.total` and `tasks.completed`.

- [x] 10.5 **Write execution log.**
  Create `C:\development\opencode\.conductor\tracks\20260531-osgrep-comprehensive-test-suite\artifacts\execution-log.md` with: date, executing agent, result summary, deviations, errors.

- [x] 10.6 **Update tracks ledger.**
  Edit `C:\development\opencode\.conductor\tracks-ledger.md`. Add to Active (or Completed) section:
  `- [20260531-osgrep-comprehensive-test-suite](./tracks/20260531-osgrep-comprehensive-test-suite/spec.md): Execute comprehensive 44-test suite for OsGrep CLI-only canary mode. (Phase: <current_phase>)`

- [x] 10.7 **Update tracks index.**
  Edit `C:\development\opencode\.conductor\tracks.md`. Add row:
  `| 20260531-osgrep-comprehensive-test-suite | OsGrep Comprehensive Test Suite | <status> | <completed_date> | C:\development\opencode\.conductor\tracks\20260531-osgrep-comprehensive-test-suite |`

### Phase 10 Exit Criteria
- Report verified. All blocking logs exist. Temp files cleaned. Metadata, ledger, tracks index updated. Execution log written.

---

## Execution Readiness Checklist

| # | Standard | Status | Notes |
|---|----------|--------|-------|
| 1 | **Atomic tasks** -- One action per checkbox | PASS | E1-E4 split into explicit sequential steps |
| 2 | **Exact file paths** -- Full absolute paths in every command | PASS | All paths are absolute Windows paths |
| 3 | **Explicit commands** -- Verbatim PowerShell and Python commands | PASS | All commands copy-paste ready |
| 4 | **Clear ordering** -- Phases 0 to 10 in strict dependency order | PASS | Index before search, tests before aggregation |
| 5 | **Verification per step** -- Every task has exit criteria or verification | PASS | Test-OsgrepResult helper added for result.json checks |
| 6 | **No assumed context** -- All paths, commands, expectations explicit | PASS | Fallback paths documented for each task |
| 7 | **Concrete examples** -- All 44 test commands are copy-paste ready in appendix | PASS | Appendix B now includes TC-E1 through TC-E4 and TC-F2 |
| 8 | **Error recovery** -- Fallback instructions for timeouts, missing files, empty results | PASS | Start-Job fallback, index scope reduction, TC-F2 conditional skip |

## Top 3 Implementation Risks

| # | Risk | Mitigation |
|---|------|------------|
| 1 | **Index --reset takes > 300s** on the full opencode repo (~2000+ files with conductor artifacts). | Reduce scope: retry with ``--path C:/development/opencode/scripts``. Skip ``--verbose``. |
| 2 | **TC-F2 tool-path test cannot run from CLI.** Tool-path activation requires an OpenCode session to invoke the osgrep tool. | TC-F2 marked CONDITIONAL BLOCKING. Skip in CLI-only, re-verify in OpenCode session. |
| 3 | **Concurrent tests (TC-E1, TC-E2) hang on Windows.** PowerShell Start-Job may behave differently from subprocess concurrency. | E1 runs sequentially by default. E2 has Start-Job fallback to sequential. |

## First Task the Build Agent Should Execute Immediately

**Task 0.1**: Run `osgrep --version` to confirm the CLI is installed and accessible. If this fails, install with `npm install -g osgrep`. Once confirmed, proceed to 0.2.

---

## Appendix A: Test Runner Script (Pre-Created)

The test runner script has been pre-created at ``C:\development\opencode\scripts\tests\osgrep_test_suite.py``.

Location: ``C:\development\opencode\scripts\tests\osgrep_test_suite.py``
Verify: ``python scripts/tests/osgrep_test_suite.py --help``

Capabilities:
- ``--report``: Scans ``logs/osgrep-debug/`` for ``result.json`` files, generates ``logs/osgrep-test-suite/report.md``
- ``--list``: Lists all available result.json files with PASS/FAIL/TIMEOUT status
- Repo root: ``Path(__file__).resolve().parent.parent.parent``
- BLOCKING labels: tc-a1, tc-a2, tc-b1-b6, tc-c1-c4, tc-f1, tc-f2, tc-f3
- NON-BLOCKING labels: tc-a3, tc-c5-c12, tc-d1-d8, tc-e1-e9, tc-g1, tc-g2
- Expected-failure labels (tc-e5, tc-e6, tc-f3) always evaluate to PASS
- Evaluates: exit_code 0 = PASS, timed_out = TIMEOUT, else FAIL
- Scans stderr for: "Table 'chunks' already exists", "UnicodeDecodeError"
- GO/NO-GO: GO only if all blocking tests PASS with no timeouts
- Report sections: Summary, Blocking Tests table, Non-Blocking Tests table, Critical Error Patterns, Recommendations



## Appendix B: All Test Commands (Copy-Paste Ready)

### Phase 1: Health
```
python scripts/utils/osgrep_debug_wrapper.py --label tc-a1-version-check --timeout 30 --cwd C:/development/opencode -- -- --version
python scripts/utils/osgrep_debug_wrapper.py --label tc-a2-doctor-check --timeout 30 --cwd C:/development/opencode -- -- doctor
```

### Phase 2: Index
```
python scripts/utils/osgrep_debug_wrapper.py --label tc-b1-index-dry-run --timeout 120 --cwd C:/development/opencode -- -- index --dry-run
python scripts/utils/osgrep_debug_wrapper.py --label tc-b2-index-verbose --timeout 300 --cwd C:/development/opencode -- -- index --verbose --reset
python scripts/utils/osgrep_debug_wrapper.py --label tc-b3-index-path --timeout 120 --cwd C:/development/opencode -- -- index --path C:/development/opencode/scripts
python scripts/utils/osgrep_debug_wrapper.py --label tc-b4-index-reset --timeout 300 --cwd C:/development/opencode -- -- index --reset --verbose
python scripts/utils/osgrep_debug_wrapper.py --label tc-b5-search-sync --timeout 120 --cwd C:/development/opencode -- -- search "auth token refresh" --sync
python scripts/utils/osgrep_debug_wrapper.py --label tc-b6-list --timeout 30 --cwd C:/development/opencode -- -- list
```

### Phase 3: Core Search
```
python scripts/utils/osgrep_debug_wrapper.py --label tc-c1-known-answer --timeout 60 --cwd C:/development/opencode -- -- search "osgrep_debug_wrapper" --max-count 10
python scripts/utils/osgrep_debug_wrapper.py --label tc-c2-max-count --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --max-count 3
python scripts/utils/osgrep_debug_wrapper.py --label tc-c3-content --timeout 60 --cwd C:/development/opencode -- -- search "auth token refresh" --content --max-count 2
python scripts/utils/osgrep_debug_wrapper.py --label tc-c4-scores --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --scores --max-count 3
```

### Phase 4: Search Flags
```
python scripts/utils/osgrep_debug_wrapper.py --label tc-c5-min-score --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --scores --min-score 0.3 --max-count 5
python scripts/utils/osgrep_debug_wrapper.py --label tc-c6-compact --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --compact --max-count 3
python scripts/utils/osgrep_debug_wrapper.py --label tc-c7-plain --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --plain --max-count 3
python scripts/utils/osgrep_debug_wrapper.py --label tc-c8-skeleton --timeout 60 --cwd C:/development/opencode -- -- search "conductor track" --skeleton --max-count 3
python scripts/utils/osgrep_debug_wrapper.py --label tc-c9-per-file --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --per-file 2 --max-count 10
python scripts/utils/osgrep_debug_wrapper.py --label tc-c10-dry-run --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --dry-run --max-count 5
python scripts/utils/osgrep_debug_wrapper.py --label tc-c11-subdir --timeout 60 --cwd C:/development/opencode -- -- search "osgrep" C:/development/opencode/scripts
python scripts/utils/osgrep_debug_wrapper.py --label tc-c12-sync --timeout 120 --cwd C:/development/opencode -- -- search "conductor" --sync --max-count 5
```

### Phase 5: Symbols, Skeleton, Trace
```
python scripts/utils/osgrep_debug_wrapper.py --label tc-d1-symbols --timeout 60 --cwd C:/development/opencode -- -- symbols --limit 10
python scripts/utils/osgrep_debug_wrapper.py --label tc-d2-symbols-filter --timeout 60 --cwd C:/development/opencode -- -- symbols "osgrep" --limit 10
python scripts/utils/osgrep_debug_wrapper.py --label tc-d3-symbols-limit --timeout 60 --cwd C:/development/opencode -- -- symbols --limit 3
python scripts/utils/osgrep_debug_wrapper.py --label tc-d4-symbols-path --timeout 60 --cwd C:/development/opencode -- -- symbols --path scripts --limit 10
python scripts/utils/osgrep_debug_wrapper.py --label tc-d5-skeleton-file --timeout 60 --cwd C:/development/opencode -- -- skeleton scripts/utils/osgrep_debug_wrapper.py
python scripts/utils/osgrep_debug_wrapper.py --label tc-d6-skeleton-symbol --timeout 60 --cwd C:/development/opencode -- -- skeleton "main" --limit 3
python scripts/utils/osgrep_debug_wrapper.py --label tc-d7-skeleton-json --timeout 60 --cwd C:/development/opencode -- -- skeleton scripts/utils/osgrep_debug_wrapper.py --json --no-summary
python scripts/utils/osgrep_debug_wrapper.py --label tc-d8-trace --timeout 60 --cwd C:/development/opencode -- -- trace "main"
```

### Phase 6: Reliability (sequential)
```
# TC-E1: Sequential queries
python scripts/utils/osgrep_debug_wrapper.py --label tc-e1-concurrent-a --timeout 90 --cwd C:/development/opencode -- -- search "conductor track" --max-count 5
python scripts/utils/osgrep_debug_wrapper.py --label tc-e1-concurrent-b --timeout 90 --cwd C:/development/opencode -- -- search "auth token" --max-count 5

# TC-E2: Query during index (sequential fallback)
python scripts/utils/osgrep_debug_wrapper.py --label tc-e2-index-first --timeout 120 --cwd C:/development/opencode -- -- index --path C:/development/opencode/scripts --reset
python scripts/utils/osgrep_debug_wrapper.py --label tc-e2-query-after-index --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --max-count 5

# TC-E3: Stale index (run steps in order, create marker file first)
python scripts/utils/osgrep_debug_wrapper.py --label tc-e3a-index-stale --timeout 120 --cwd C:/development/opencode -- -- index --sync
python scripts/utils/osgrep_debug_wrapper.py --label tc-e3b-search-fresh --timeout 60 --cwd C:/development/opencode -- -- search "STALE_TEST_MARKER" --max-count 3
python scripts/utils/osgrep_debug_wrapper.py --label tc-e3c-search-after-delete --timeout 60 --cwd C:/development/opencode -- -- search "STALE_TEST_MARKER" --max-count 3

# TC-E4: Path with spaces (create dir+file first, then run these)
python scripts/utils/osgrep_debug_wrapper.py --label tc-e4a-spaced-index --timeout 60 --cwd "C:\development\opencode\osgrep test space" -- -- index
python scripts/utils/osgrep_debug_wrapper.py --label tc-e4b-spaced-search --timeout 60 --cwd "C:\development\opencode\osgrep test space" -- -- search "spaces_test_function"

# TC-E5: Non-existent CWD
python scripts/utils/osgrep_debug_wrapper.py --label tc-e5-nonexistent-cwd --timeout 30 --cwd C:/development/opencode/does-not-exist-qwerty -- -- search "test"

# TC-E6: Empty pattern
python scripts/utils/osgrep_debug_wrapper.py --label tc-e6-empty-pattern --timeout 30 --cwd C:/development/opencode -- -- search ""

# TC-E7: Long pattern
python scripts/utils/osgrep_debug_wrapper.py --label tc-e7-long-pattern --timeout 60 --cwd C:/development/opencode -- -- search "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" --max-count 3

# TC-E8: Timing baseline
python scripts/utils/osgrep_debug_wrapper.py --label tc-e8-timing --timeout 60 --cwd C:/development/opencode -- -- search "conductor" --max-count 10

# TC-E9: Cold start
taskkill /F /T /IM osgrep-nodejs-helper.exe 2>$null; python scripts/utils/osgrep_debug_wrapper.py --label tc-e9-cold-start --timeout 120 --cwd C:/development/opencode -- -- search "conductor" --max-count 5
```

### Phase 7: Guardrails
```
# TC-F1: MCP guardrail (CLI check)
osgrep mcp --help 2>&1 | Select-Object -First 10

# TC-F2: Tool-path activation (CLI-only: SKIP, mark CONDITIONAL)
# Requires OpenCode session. Invoke: {"argv": ["--", "search", "conductor", "--max-count", "3"]}

# TC-F3: Forced failure / fallback
python scripts/utils/osgrep_debug_wrapper.py --label tc-f3-forced-failure --timeout 30 --cwd C:/development/opencode/xyznonexistent987 -- -- search "test"
```
### Phase 8: Tooling
```
python scripts/utils/osgrep_debug_wrapper.py --label tc-g1-wrapper-baseline --timeout 30 --cwd C:/development/opencode -- -- search "test" --max-count 1
powershell -ExecutionPolicy Bypass -File "C:\development\opencode\scripts\utils\osgrep_process_snapshot.ps1" -Label "tc-g2" -OutputDir "C:\development\opencode\logs\osgrep-test-suite" -TargetCwd "C:\development\opencode"
```

### Phase 9: Aggregation
```
python C:\development\opencode\scripts\tests\osgrep_test_suite.py --report
```

---

*End of plan. Total: 52 tasks across 10 phases + 2 appendices.*
