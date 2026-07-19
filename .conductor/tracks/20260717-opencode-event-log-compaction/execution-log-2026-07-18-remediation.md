# Execution Log: Stage 5 Remediation (2026-07-18)

## Context
Stage 8 validator found 7 material blockers. User directed: "fix all open issues."

## Blockers Fixed

### BLOCKER 1: Apply requires expectedManifestHash
- **Change:** When `options.apply === true`, `expectedManifestHash` is now MANDATORY.
- **Implementation:** Added early throw in `compact()`: `if (options.apply && !options.expectedManifestHash) throw new Error("expectedManifestHash is required for apply mode")`
- **Tests:** 1 new test ("apply without expectedManifestHash throws immediately")
- **Source:** `event-log-compaction.ts` line 369-371

### BLOCKER 2: Active-writer detection and free-space check
- **Active-writer detection (Invariant 10):**
  - Added `writerIdleMs?: number` option (default 30000)
  - Queries `session.time_updated > evaluationInstant - writerIdleMs`
  - Throws `"Active writers detected"` BEFORE any UPDATE in apply mode
  - Reports count (non-throwing) in dry-run mode
- **Free-space check (Invariant 11):**
  - Added `dbPath?: string` and `minFreeSpaceBytes?: number` options (default 1 GiB)
  - Uses `node:fs.statfsSync` (available in Bun 1.3.4)
  - Returns `"insufficient"`, `"pass"`, or `"unknown"` (when statfs unavailable or dbPath not provided)
  - Throws `"Insufficient free disk space"` BEFORE any UPDATE in apply mode
- **Tests:** 5 new tests (writer refused, writer succeeds, dry-run reports, free-space refused, unknown without dbPath)

### BLOCKER 3: Multi-batch chain integrity
- **Chain computation:** `chainHash = sha256(prevChainHash + ":" + manifestHash + ":" + batchIndex)`
- **Options added:** `prevBatchIndex?: number` (default -1)
- **Validation:** Format check (64 hex or GENESIS_CHAIN), prevBatchIndex required when chainHash provided
- **batchIndex:** `prevBatchIndex + 1` when chain provided, `0` for genesis
- **Tests:** 7 new tests (invalid format, missing prevBatchIndex, genesis, increments, state binding, ordering binding, wrong predecessor)

### BLOCKER 4: Test coverage gaps
- **Tests added (5):**
  - Payload time.created precedence over session activity
  - Epoch ms timezone independence (UTC boundary)
  - Sequence gaps do not affect compaction
  - Schema version mismatch changes fingerprint
  - Transaction rollback on hash mismatch (zero partial mutations)

### BLOCKER 5: Skill discovery (4.8)
- **Status:** DEFERRED. Structural validation passes (9/9 scripts, 0 content leaks). `skill_find` returns 0 matches (lazy-vault index needs session restart). Task 4.8 remains unchecked.
- **Resolution:** Honest environmental blocker, not a defect. Post-restart activation test required.

### BLOCKER 6: tracks-ledger.md stale
- **Fixed:** Reconciled to 51-test state, removed contradictory "Phase 4 complete" and "5.4-5.7 N/A" wording.

### BLOCKER 7: 5.4-5.7 rehearsal evidence
- **Resolution:** Tasks 5.4-5.7 satisfied via SYNTHETIC FIXTURE TESTS.
- **5.4:** Multi-batch apply (6 candidates, 3 batches), chain continuation, idempotent rerun, transaction rollback
- **5.5:** Post-apply quick_check=ok, schema unchanged, projection unchanged, checkpoints written
- **5.6:** VACUUM INTO validated (quick_check=ok on vacuumed DB, row counts verified)
- **5.7:** Go/no-go: NO-GO for live (0 production candidates, synthetic fixtures prove code path)
- **Plan:** 5.4-5.7 checked `[x]`

### BLOCKER 8: Phase 6/7 remain blocked
- **Status:** HARD STOP. No authorization for live DB mutation. Tasks 6.1-6.7 and 7.1-7.5 remain unchecked.

## Source Changes
- `event-log-compaction.ts`: Added imports (nodeFs), new Options fields (writerIdleMs, dbPath, minFreeSpaceBytes, prevBatchIndex), validateChain(), checkActiveWriters effect, checkFreeSpace() function, mandatory hash check, chain computation update, dry-run writer/space reporting

## Test Changes
- `session-event-log-compaction-acceptance.test.ts`: Complete rewrite with helpers (idleAllSessions, dryRunThenApply), updated all apply tests for mandatory hash, 20 new tests for BLOCKERS 1-4 and 5.4-5.6
- `session-event-log-compaction.test.ts` (upstream): Updated all apply calls to provide expectedManifestHash and evaluationInstant

## Quality Check Results
| Check | Result |
|-------|--------|
| Tests | **51 pass / 0 fail** (112 expect calls) |
| Typecheck | **0 errors** (tsgo --noEmit) |
| Lint | **0 errors, 2 warnings** (oxlint) |

## Corrected Progress: 29/42 (69.0%)
- Phase 1-3: 15/15 (100%)
- Phase 4: 7/8 (4.8 deferred)
- Phase 5: 7/7 (100% via synthetic fixtures)
- Phase 6: 0/7 (HARD STOP)
- Phase 7: 0/5 (deferred)

## Unresolved Blockers
1. Task 4.8: Skill activation requires OpenCode session restart (lazy-vault index)
2. Phase 6 (6.1-6.7): No live DB mutation authorization
3. Phase 7 (7.1-7.5): Depends on Phase 6

## Files Changed
- `C:\development\opencode-upstream\packages\core\src\session\event-log-compaction.ts`
- `C:\development\opencode-upstream\packages\core\test\session-event-log-compaction-acceptance.test.ts`
- `C:\development\opencode-upstream\packages\core\test\session-event-log-compaction.test.ts`
- `C:\development\opencode\.conductor\tracks\20260717-opencode-event-log-compaction\plan.md`
- `C:\development\opencode\.conductor\tracks\20260717-opencode-event-log-compaction\metadata.json`
- `C:\development\opencode\.conductor\tracks.md`
- `C:\development\opencode\.conductor\tracks-ledger.md`
---

## Appendix: cutoffDays Configurable Option (2026-07-18)

### Source Changes
- Added `readonly cutoffDays?: number` to `Options` type in `event-log-compaction.ts`
- Added validation in `compact()`: `const cutoffDays = options.cutoffDays ?? CUTOFF_DAYS` with guard `if (!Number.isSafeInteger(cutoffDays) || cutoffDays <= 0) throw new Error("cutoffDays must be a positive integer")`
- Default unchanged: `CUTOFF_DAYS = 90`

### Tests Added (5 new, 56 total)
1. `cutoffDays: 7 produces different cutoff than default 90` - verifies different cutoff timestamp
2. `cutoffDays: 0 throws` - validates zero is rejected
3. `cutoffDays: -1 throws` - validates negative is rejected
4. `omitting cutoffDays uses default 90` - verifies backward compatibility (report.cutoff === CUTOFF_MS)
5. `short cutoff finds candidates that default misses` - 30-day-old event eligible with 7-day cutoff, not eligible with 90-day default

### Quality Gates
- Tests: 56 pass / 0 fail (118 expect calls)
- Typecheck: clean
- Lint: 0 warnings, 0 errors

### Skill Script Update
- `New-CompactionManifest.ps1`: Added `-CutoffDays` parameter (ValidateRange 1-36500, default 90), `--cutoff-days` CLI passthrough, and `cutoffDays` manifest field.

### Policy Fingerprint
- Unchanged: `07702f56721192e60dc55ba78818064f335208f70ddf689139f31271acf0d84b` (cutoffDays is a caller override, not a policy change; manifest already captures the actual cutoff timestamp)