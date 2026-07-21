# Test Report — 2026-07-20 Database Activation Safety Remediation

**Track:** 20260720-opencode-db-activation-safety
**Test Framework:** Pester 3.4.0
**Test File:** `tests\DatabaseActivationSafety.Tests.ps1`
**Fixture Creator:** `tests\create-fixtures.ts` (bun:sqlite)
**Test Utilities:** `tests\TestUtils.psm1`

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 50 |
| Passed | 50 |
| Failed | 0 |
| Skipped | 0 |
| Execution Time | ~5-9 seconds |
| Fixture Location | `%TEMP%\db-activation-test-*` |
| Live DB Access | NONE |
| Process Termination | NONE |

## Test Categories

### Fixture Safety (3 tests)
- Fixtures created in temp directory, never live DB
- All 10 expected fixture directories exist
- Valid manifest with sentinel values

### Fixture Integrity (8 tests)
- db-only: DB file, no WAL, no SHM
- db-wal-uncheckpointed: DB and WAL
- wal-no-shm: DB and WAL, no SHM
- db-wal-shm: all three files
- orphan-shm: DB and SHM, no WAL
- stale-wal: DB and mismatched WAL
- truncated-wal: DB and truncated WAL (100 bytes)
- corrupt-db: invalid SQLite header

### File Inventory (3 tests)
- Get-ActiveFileInventory reports correct presence flags
- Correct absence for db-only
- Get-FileHash256 returns consistent SHA-256 hashes

### Exclusive Handle Probe (4 tests)
- Returns true for unlocked file
- Returns true for nonexistent file
- Returns false for locked file (FileShare.None)
- Handle appearing after preflight is detected on re-check

### Named Mutex (3 tests)
- Acquire and release
- Cross-process contention (separate PowerShell process blocked)
- Re-acquisition after release

### Writer Detection (6 tests)
- No writers when process list empty
- Writers detected when processes exist
- Inaccessible process has CanClassify=false
- False-positive names not treated as writers
- Writer appearing after preflight detected on re-check
- Never calls Stop-Process

### Recovery Snapshot (3 tests)
- All present files copied with matching hashes
- db-only handled correctly
- Raw WAL bytes preserved (uncheckpointed sentinel)

### File.Replace Semantics (2 tests)
- Same-volume replacement succeeds
- Locked destination fails

### Partial Activation Recovery (3 tests)
- WAL displacement recovery restores original hashes
- SHM displacement recovery restores original hashes
- Main DB replacement failure recovery restores original hashes

### WhatIf Zero Mutation (2 tests)
- No files, directories, or mutations created
- No lock files or staging directories

### Journal and Reconciliation (3 tests)
- Journal records atomically published (temp -> Move-Item)
- Restart reconciliation detects incomplete state
- Hash-based reconciliation matches original

### Uncheckpointed WAL Sentinel (2 tests)
- WAL present and non-empty
- Recovery snapshot preserves WAL bytes

### Stale WAL Rejection (2 tests)
- Mismatched WAL detected
- Truncated WAL detected by size

### Full Activation Simulation (1 test)
- Sidecars displaced, File.Replace, verification, no stale sidecars

### Successful Restoration (2 tests)
- Coordinated DB/WAL/SHM restore with hash verification
- DB-only backup without stale sidecars

### No Premature Success (2 tests)
- Success only after verification
- Partial state does not report success

### Recovery Artifact Preservation (1 test)
- Recovery artifacts exist after snapshot creation

## Safety Properties Verified

1. **No live DB access:** All fixtures in temporary directories
2. **No process termination:** Stop-Process never called
3. **No force-kill behavior:** Removed from Activate-CompactedDb.ps1
4. **Named mutex:** Prevents concurrent maintenance
5. **Exclusive handle probes:** Before every transition
6. **Recovery on failure:** Byte-for-byte restoration or manual-intervention state
7. **WhatIf zero mutation:** No paths created
8. **No premature success:** Only after verification
9. **Recovery artifacts preserved:** Never deleted
10. **Private-copy verification:** SQLite never opens active path

## Fixture Safety Confirmation

All test fixtures are created in `%TEMP%\db-activation-test-*` directories:
- No fixture resolves to `C:\Users\DaveWitkin\.local\share\opencode\`
- No test reads from or writes to the live database directory
- All temporary directories are cleaned up after test run
- The test suite explicitly asserts fixture path != live DB path
