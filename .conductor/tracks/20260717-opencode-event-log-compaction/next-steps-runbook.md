# OpenCode Database Compaction - Next Steps

**Current state:** Logical compaction is complete. The physically smaller database was activated on 2026-07-20. OpenCode is running with the compacted database.

## What Was Done (2026-07-18/20)

### Logical Compaction (2026-07-18)
- 14-day compaction: 9 batches, 89,223 events (batch-compaction-results.json)
- 7-day compaction: 14 batches, 133,259 events (batch-compaction-7day-results.json)
- Single-run artifact: 10,001 events (compaction-result.json, non-authoritative/malformed)
- **Reported total:** 25 batches / 242,484 events (not independently verified from machine-readable artifacts)
- **Physical savings:** 23.07 GiB -> 14.87 GiB (8.2 GiB, 35.5%)

### Activation (2026-07-20)
- User closed OpenCode, confirmed YES to Activate-CompactedDb.ps1
- Swap completed: candidate activated at canonical path
- OpenCode restarted successfully
- Post-restart targeted PRAGMA quick_check: ok (journal_mode wal, user_version 0)
- Skill activation confirmed (skill_find/skill_use)

### Deviations from Reviewed Path
- Logical UPDATE compaction ran while OpenCode was active (WAL concurrency)
- Separate temporary scripts were used, not the reviewed exact-hash apply path
- Writer detection and projection checks were bypassed for performance
- Exact manifest hash continuity not maintained across separate dry-run/apply scripts
- Full phase6-runner post-restart validation timed out; only targeted PRAGMA check passed

## Remaining Follow-ups

### 7.2 - Post-swap application smoke tests (DEFERRED)
**Status:** Evidence gap / deferred.
**What exists:** skill_find/skill_use confirmed working. OpenCode is running and functional.
**What does NOT exist:** Representative export/read/resume/new-session smoke test artifacts.
**Required evidence:** A bounded script or log showing at least one of: session list, representative export, read-back, resume, or new-session creation post-swap.

### 7.3 - Rollback restoration rehearsal (DEFERRED)
**Status:** Evidence gap / deferred.
**What exists:** Rollback artifacts confirmed to exist:
- `C:\Users\DaveWitkin\.local\share\opencode\opencode.db.pre-compaction-20260718-135520` (~24.77 GiB)
- `C:\Users\DaveWitkin\.local\share\opencode\opencode.db.pre-compaction-active-20260720-125457` (~24.77 GiB)
**What does NOT exist:** A restoration rehearsal.
**Required evidence:** A bounded restoration rehearsal with writers stopped, or an explicit waiver with rationale.

## If You Need to Rollback

Close OpenCode first, then run:

```powershell
& "C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor\scripts\Activate-CompactedDb.ps1" -Rollback
```

The rollback script:
- **Fails closed** if any OpenCode or bun processes are detected running
- Restores the pre-compaction backup as a **coordinated DB/WAL/SHM set**
- Verifies the restored database with `PRAGMA quick_check`
- Preserves displaced active files in a timestamped emergency directory

Restart OpenCode after the rollback script reports success.

**Note:** Rollback restoration has NOT been rehearsed. Test on a disposable copy before relying on it.

## If You Need to Run Compaction Again

1. Check status (always safe):
```powershell
cd C:\development\opencode-upstream
bun run phase6-runner.ts status
```

2. Dry run (always safe):
```powershell
bun run phase6-runner.ts dry-run --cutoff-days 14
```

3. Apply with approved hash (writer check and projection check ON by default):
```powershell
bun run phase6-runner.ts apply --cutoff-days 14 --hash <manifestHash>
```

**Important:** The manifest hash is invalidated by ANY DB write. Recompute immediately before apply. See the skill's SKILL.md for full safety guidance.

## Important paths

| Item | Path |
|---|---|
| Active database | `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` |
| Compacted database | `C:\Users\DaveWitkin\.local\share\opencode\opencode.db.compacted-final-7day-20260718-193249` |
| Original backup | `C:\Users\DaveWitkin\.local\share\opencode\opencode.db.pre-compaction-20260718-135520` |
| Activation script | `C:\development\opencode-upstream\Activate-CompactedDb.ps1` |
| Validation runner | `C:\development\opencode-upstream\phase6-runner.ts` |
| Skill | `C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor\` |

## Results already achieved

- 242,484 events compacted across 25 batches (reported total; see deviations above).
- 8.2 GiB physical savings: 23.07 GiB to 14.87 GiB.
- `quick_check` passed (targeted PRAGMA check, not full validation).
- Messages, parts, and sessions remained readable.
- Skill activation confirmed post-restart.
