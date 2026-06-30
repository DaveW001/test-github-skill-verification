# Spec

## Goal
Resolve the **FATAL** server error `NOT NULL constraint failed: session_message.seq` that is blocking every `opencode run` scheduled job (and any session that triggers an agent/model switch), and resolve the **secondary, non-fatal** plugin load failure `Cannot find module '@anthropic-ai/tokenizer'` from `@tarquinen/opencode-dcp`. This track is the promised follow-up to `20260608-opencode-desktop-startup-freeze`, which deferred the "scheduled-run `session_message.seq` database write errors" with evidence.

## Incident Summary (live evidence, this machine, 2026-06-28)
- **Symptom:** Server log `C:\Users\DaveWitkin\.local\share\opencode\log\2026-06-28T170002.log` shows:
  - `INFO service=db ... opening database` then `count=20 mode=bundled applying migrations`
  - `ERROR service=plugin path=@tarquinen/opencode-dcp@latest ... error=Cannot find module '@anthropic-ai/tokenizer' ... failed to load plugin`  *(non-fatal)*
  - `ERROR service=server ref=err_0650c941 error=NOT NULL constraint failed: session_message.seq cause=SQLiteError: NOT NULL constraint failed: session_message.seq` with stack: `appendMessage <- session.next.agent.switched <- SessionPrompt.createUserMessage <- SessionPrompt.prompt <- SessionHttpApi.prompt`  *(FATAL — the blocker)*
- **User-reported ref `err_220bd60e` is the same error class** — these refs are random per-occurrence; the message, cause, and stack are identical.
- **Trigger on this host:** the hourly KB-ingest scheduled job (`opencode run --title "KB Ingest Hourly" ... @scheduled-job-best-practices`). The `@<agent>` reference fires `session.next.agent.switched`, which calls `appendMessage` without supplying `seq`.

## Root Cause — Primary (FATAL): version skew (pre-fix runtime vs. seq-requiring schema)
- **Installed:** `opencode-ai@1.15.10` (PATH resolves to `C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1`; standalone copy at `C:\Users\DaveWitkin\AppData\Local\opencode\opencode.exe`).
- **Latest release:** `v1.17.11` (anomalyco/opencode == sst/opencode, in sync, released 2026-06-25).
- **The fix:** upstream commit [`8bc501b`](https://github.com/anomalyco/opencode/commit/8bc501b5358128b10db2e34e380c62a41c90d702) `fix(core): guard against null event.seq when inserting session_messages` (2026-06-08). It changed all `event.seq === undefined` guards to `event.seq == null` (catches both `null` and `undefined`) across `packages/core/src/session.ts`, `packages/core/src/session/input.ts`, `packages/core/src/session/projector.ts`, `packages/opencode/src/event-v2-bridge.ts`. Related PR #31419.
- **Why it fails on 1.15.10:** the `session_message` schema on this DB defines `seq INTEGER NOT NULL` with **no DEFAULT** and a `UNIQUE(session_id, seq)` index. The 1.15.x `appendMessage` path used by `session.next.agent.switched` / `session.next.model.switched` does not populate `seq`, so SQLite rejects the insert and the session dies. Fixed runtimes (1.16.x+) populate `seq`; later `dev` schema removes the column entirely.
- **This is a documented upstream bug cluster:** anomalyco/opencode issues [#31204](https://github.com/anomalyco/opencode/issues/31204) (agent.switched — canonical), [#31412](https://github.com/anomalyco/opencode/issues/31412) / [#31413](https://github.com/anomalyco/opencode/issues/31413) (`opencode run` + HTTP), [#31606](https://github.com/anomalyco/opencode/issues/31606) (model.switched, still open), [#31072](https://github.com/anomalyco/opencode/issues/31072) (related seq race).

## DB State (read-only probe of a copy — no mutations performed)
- `PRAGMA integrity_check` => **`ok`**. The database is **not corrupt**.
- `session_message.seq`: exists, `NOT NULL`, `dflt_value = NULL` (no default). Indexes present: `session_message_session_seq_idx` UNIQUE `(session_id, seq)`, plus `session_message_session_type_seq_idx`, `session_message_session_time_created_id_idx`, `session_message_time_created_idx`.
- **0 rows with NULL seq** — existing data is intact; the failure is purely at INSERT (the new row never lands).
- Source-of-truth tables intact: `event` = 21,416 rows, `message` = 49,626 rows, `session` = 1,800 rows. **This is NOT the migration-#30963 data-wipe scenario** (that one emptied `session_message`/`event`, making `MAX(seq)+1 = NULL`).
- Drizzle journal: 21 migrations applied, latest `20260511173437_session-metadata`. The fix commit is a **code** change, not a migration, so upgrading the runtime is sufficient — **no DB wipe, no re-projection, no migration rollback required.**

## Root Cause — Secondary (non-fatal): DCP plugin missing transitive dep
- `@tarquinen/opencode-dcp` (Dynamic Context Pruning; user has active `~/.config/opencode/dcp.jsonc`) is cached at `~/.cache/opencode/packages/@tarquinen/opencode-dcp@latest` pinned to **3.1.13**.
- Its `dist/index.js` imports `@anthropic-ai/tokenizer`, but that package is **absent from the plugin's `node_modules`** (confirmed: `Test-Path ...\node_modules\@anthropic-ai\tokenizer` => False).
- `@anthropic-ai/tokenizer` still exists on npm (**v0.0.4**, modified 2026-06-04). A newer DCP **3.1.14** (2026-06-25) exists; `@latest` will resolve to it once the stale cache entry is cleared.

## Requirements
- [ ] Upgrade the opencode runtime to a release that contains fix `8bc501b` (>= 1.16.x; target latest `v1.17.11`) so `session_message.seq` is populated on the `agent.switched`/`model.switched` paths.
- [ ] Confirm scheduled `opencode run` jobs (KB ingest) complete without `NOT NULL constraint failed: session_message.seq` after upgrade.
- [ ] Restore the DCP plugin to a loading state (no `@anthropic-ai/tokenizer` error) so token-aware pruning still works.
- [ ] Perform all mutations only after a timestamped backup of `opencode.db` and only when no opencode process (incl. scheduler) is running.
- [ ] Leave existing session/message/event history intact (no destructive DB operations).

## Non-Requirements
- [ ] Do NOT delete or recreate `opencode.db` (integrity is `ok`, source-of-truth intact).
- [ ] Do NOT attempt to manually patch opencode source/bundles — the fix is upstream and shipped; upgrade instead.
- [ ] Do NOT modify calendar/scheduler definitions beyond what is needed to safely stop the job during the upgrade window.
- [ ] DCP plugin fix is non-blocking; it can be deferred if the upgrade window must be minimal.

## Acceptance Criteria
- [ ] **AC-1 - Runtime upgraded (npm-global copy, which is the one on PATH).** `C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-precheck-20260628.txt` shows pre-fix `1.15.10`; post-fix `opencode --version` (from plain PowerShell per Phase 0) starts with `1.17.` AND `npm ls -g opencode-ai` shows `1.17.x` The standalone copy at `C:\Users\DaveWitkin\AppData\Local\opencode\opencode.exe` is NOT on PATH (verified during planning) and is intentionally left at its current version; its version is recorded in the precheck file for completeness but is not an acceptance gate.  Verify with: `(Get-Content 'C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-precheck-20260628.txt' -Raw) -match '1\.15\.10'` AND `opencode --version` starts with `1.17.`.
- [ ] **AC-2 - seq fix proven by a new session.** `seq-fix-probe-20260628.json` (probe from Phase 3.1) returns exit code 0 with the string `PING` in the output.  Verify with: `(Select-String -Path 'C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-probe-20260628.json' -Pattern 'PING' -SimpleMatch) -ne $null`.
- [ ] **AC-3 - DB evidence: new probe session_message rows have non-null seq.** Phase 3.3 python probe prints `session_id=ses_... total=N nonnull_seq=N` followed by `OK` for the new probe session.  Verify by re-running the Phase 3.3 command against a fresh DB copy; both `total` and `nonnull_seq` must be equal and >= 1.
- [ ] **AC-4 - Post-fix logs are error-free.** `C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-final-validated.txt` exists and contains the literal `OK: N post-fix log files scanned, zero errors` (Phase 6.1).  Verify with: `Select-String -Path 'C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-final-validated.txt' -Pattern 'zero errors' -SimpleMatch`.
- [ ] **AC-5 - DCP plugin loads with tokenizer present.** `Test-Path 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@anthropic-ai\tokenizer'` returns `True`, AND the most recent log under `C:\Users\DaveWitkin\.local\share\opencode\log` contains `service=plugin path=@tarquinen/opencode-dcp` with NO following `failed to load plugin` on the same run.
- [ ] **AC-6 - DB integrity preserved.** `C:\Users\DaveWitkin\.local\share\opencode\opencode.db.bak-YYYYMMDD-HHMMSS` exists with non-zero size and SHA256 captured (Phase 1.3), AND post-upgrade `PRAGMA integrity_check` on a temp copy returns `ok` (Phase 5.2).
- [ ] **AC-7 - Scheduler restored.** `Get-ScheduledTask -TaskName '\OpenCode\opencode-job-development-88876ee600f5-knowledge-base-ingest' | Select-Object -ExpandProperty State` returns `Ready` (Phase 5.1).
- [ ] **AC-8 - Track artifacts closed.** `C:\development\opencode\.conductor\tracks\20260628-opencode-session-message-seq-fatal\metadata.json` shows `status: completed`, `progress.percentage: 100`; `C:\development\opencode\.conductor\tracks.md` row for this track shows `complete` and today's date; `execution-log.md` has a `## YYYY-MM-DD - Execution Complete (Build agent)` section.

## Evidence Sources
- Live server log: `C:\Users\DaveWitkin\.local\share\opencode\log\2026-06-28T170002.log`
- Rolling server log: `C:\Users\DaveWitkin\.local\share\opencode\log\opencode.log`
- Database: `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` (+ `.db-wal`, `.db-shm`)
- DCP cache: `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest`
- Upstream research: `.conductor/tracks/20260628-opencode-session-message-seq-fatal/upstream-github-findings.md`
- Prior/related track: `.conductor/tracks/20260608-opencode-desktop-startup-freeze/spec.md`

## Resolved separately
The secondary DCP plugin @anthropic-ai/tokenizer load failure (Phase 4 of this track) was resolved by dedicated track 20260629-dcp-complete-outage-fix. When executing THIS track, Phase 4 (DCP) can be treated as already-done.

