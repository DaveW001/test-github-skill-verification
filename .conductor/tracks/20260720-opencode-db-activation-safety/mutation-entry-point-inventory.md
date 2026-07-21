# Mutation Entry Point Inventory

**Generated:** 2026-07-20  
**Track:** 20260720-opencode-db-activation-safety

## Entry Points Identified

### 1. Activate-CompactedDb.ps1 — Forward Activation Path (lines ~70-100)

| Line(s) | Operation | Risk |
|---------|-----------|------|
| ~78 | Read-Host "Force kill?" | Interactive prompt offers force-kill |
| ~79 | Stop-Process -Force | **Kills OpenCode/bun processes** |
| ~88 | Move-Item $activeDb | Moves active DB without handle probe |
| ~89 | Copy-Item $compacted -> $activeDb | Copy-overwrite of canonical DB (not File.Replace) |
| ~90 | Remove-Item $activeWal, $activeShm | Removes sidecars without coordination |

**Status:** UNSAFE — all 5 operations must be removed or hardened.

### 2. Activate-CompactedDb.ps1 — Rollback Path (lines ~20-60)

| Line(s) | Operation | Risk |
|---------|-----------|------|
| ~24-30 | Get-Process writer detection | Process-name only, no handle probe |
| ~46-52 | Move-Item active DB/WAL/SHM to failedDir | No handle probe before move, no recovery on partial failure |
| ~55-58 | Copy-Item backup DB/WAL/SHM to active | Copy-overwrite, not File.Replace; no hash verification |
| ~60-61 | Remove-Item stale sidecars | No coordination with main replacement |
| ~64 | sqlite3 quick_check on active path | Opens active path directly (should use private copy) |

**Status:** PARTIALLY SAFE — writer detection exists but lacks handle probe and recovery.

### 3. Switch-ValidatedDatabase.ps1

| Line(s) | Operation | Risk |
|---------|-----------|------|
| ~31-33 | Get-Process writer detection | Process-name only |
| ~44-48 | Move-Item DB to rollback dir | No handle probe, no recovery on partial failure |
| ~50-54 | Move-Item WAL/SHM | No handle probe |
| ~56 | Copy-Item candidate to DB path | Copy-overwrite, not File.Replace |
| ~58-59 | Remove-Item stale sidecars | No coordination |
| ~62 | sqlite3 quick_check on active path | Opens active path directly |

**Status:** PARTIALLY SAFE — has ShouldProcess but lacks handle probe, recovery, and proper replacement.

### 4. Restore-OpenCodeDatabase.ps1

| Line(s) | Operation | Risk |
|---------|-----------|------|
| ~33-35 | Get-Process writer detection | Process-name only |
| ~42-48 | Move-Item active set to emergency dir | No handle probe |
| ~52-56 | Copy-Item rollback set to active | Copy-overwrite, no hash verification |
| ~60-62 | Remove-Item stale sidecars | No coordination |
| ~65 | sqlite3 quick_check on active path | Opens active path directly |

**Status:** PARTIALLY SAFE — has ShouldProcess but lacks handle probe, recovery, and proper verification.

## Summary

- **4 entry points** total across 3 scripts
- **11 distinct mutation operations** (Move-Item, Copy-Item, Remove-Item, Stop-Process)
- **0 handle probes** before any mutation
- **0 recovery mechanisms** for partial failures
- **0 hash verifications** before/after replacement
- **1 force-kill path** (Activate forward mode)
- **4 direct SQLite opens** on active paths (should use private copies)
