# OpenCode Database Compaction — Next Steps

**Current state:** Logical compaction is complete. The physically smaller database is ready, but it has not yet been activated as `opencode.db`.

## 1. Close OpenCode

Close OpenCode and any OpenCode/bun processes that may use the database.

Optional verification:

```powershell
Get-Process -Name "opencode*", "bun*" -ErrorAction SilentlyContinue
```

The command should return no relevant OpenCode processes before activation.

## 2. Activate the compacted database

Open a new PowerShell window and paste:

```powershell
Set-Location -LiteralPath "C:\development\opencode-upstream"
& ".\Activate-CompactedDb.ps1"
```

When prompted, type `YES` to confirm the swap.

The script will:

- Verify the compacted database with `PRAGMA quick_check`.
- Move the current database aside as a rollback copy.
- Activate the compacted database.
- Remove stale `-wal` and `-shm` sidecar files.

## 3. Restart OpenCode

Start OpenCode normally after the script reports `SWAP COMPLETE`.

## 4. Validate the active database

After OpenCode has started, open PowerShell and paste:

```powershell
Set-Location -LiteralPath "C:\development\opencode-upstream"
& bun run phase6-runner.ts validate --db-path "C:\Users\DaveWitkin\.local\share\opencode\opencode.db"
```

Expected results:

- `quickCheck`: `ok`
- Database size: approximately `14.87 GiB`
- `compactedEvents`: approximately `242,484` or higher if new activity has occurred
- Messages, parts, and sessions remain readable

## 5. Confirm skill discovery

The skill index is rebuilt when OpenCode starts. In the new OpenCode session, run:

```text
skill_find "event log compaction"
```

Then load it with:

```text
skill_use "opencode-event-log-compactor"
```

Skill location:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor\
```

## 6. Rollback if necessary

Close OpenCode first, then run:

```powershell
Set-Location -LiteralPath "C:\development\opencode-upstream"
& ".\Activate-CompactedDb.ps1" -Rollback
```

Restart OpenCode after the rollback script reports success.

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

- 242,484 events compacted across 25 batches.
- 8.2 GiB physical savings: 23.07 GiB to 14.87 GiB.
- `quick_check` passed.
- Messages, parts, and sessions remained intact.
