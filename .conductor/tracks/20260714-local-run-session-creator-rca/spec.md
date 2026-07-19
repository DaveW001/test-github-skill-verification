# Spec: Local `opencode run` Session-Creation Failure RCA and Safe Recovery

## Goal

Restore reliable local, headless OpenCode runs without deleting or mutating the shared session database unnecessarily. Confirm whether the observed one-line-run failure is the known `session_message.seq` runtime/schema-version-skew defect, then upgrade and validate the canonical runtime before treating the supported `serve`/`--attach` path as an operational optimization.

## Evidence collected (2026-07-14)

- The active CLI (`opencode --version`) reports **1.15.10**, installed via npm at `C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.cmd` (shim invokes `node_modules\opencode-ai\bin\opencode.exe`).
- The OpenCode **Desktop** binary at `C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe` reports `FileVersion 1.17.19` (confirmed via `(Get-Item ...).VersionInfo.FileVersion`). 7 Desktop processes are running.
- The shared SQLite database is at `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`, **14.36 GB** on disk, in WAL mode (`.db-shm` and `.db-wal` present).
- A read-only `node:sqlite` probe (Node 24.12.0 built-in module, no install required) confirms the DB is in the post-`seq`-fix shape: 21 rows in `__drizzle_migrations` (latest `id=21` at epoch `1778520877000` = 2026-05-01), and the `session_message` table has 7 columns ending in `seq INTEGER NOT NULL` with no `dflt_value`. This matches the upstream `NOT NULL constraint failed: session_message.seq` failure pattern when a 1.15.x CLI writes against a 1.16+/1.17.x-migrated database.
- `opencode session list --max-count 1 --format json` succeeds, so the read path to the session store is functional. This is NOT proof of write-path health.
- `PRAGMA quick_check` on the live DB returns `ok` (measured 69 s on the 14.36 GB file). The DB is structurally sound.
- Official documentation describes `opencode run --attach http://localhost:<port>` as the supported way to reuse a headless `opencode serve` process and avoid repeated cold starts. The server exposes `POST /session` to create a session, `POST /session/:id/message` to send the prompt, `GET /global/health`, and `GET /doc`.
- GitHub issue [#31413](https://github.com/anomalyco/opencode/issues/31413) documents the same first-prompt failure for 1.15.x: `NOT NULL constraint failed: session_message.seq`. It attributes the issue to an old CLI writing against a newer migrated database schema and reports that upgrading the canonical runtime fixed it without a database reset.
- Upstream commit [8bc501b](https://github.com/anomalyco/opencode/commit/8bc501b5358128b10db2e34e380c62a41c90d702) fixes null/undefined `event.seq` handling in session-message insertion.
- Related issues remain open, including [#35116](https://github.com/anomalyco/opencode/issues/35116), [#31606](https://github.com/anomalyco/opencode/issues/31606), and [#28407](https://github.com/anomalyco/opencode/issues/28407). The Perplexity search client was available but its provider connection failed; GitHub CLI research was used as the fallback.
- The CLI exposes `--method {curl,npm,pnpm,bun,brew,choco,scoop}` for `opencode upgrade`. Given the npm shim, `--method npm` is the canonical path (verified in `opencode upgrade --help`). `--method bun` is available as a fallback (bun 1.3.4 is installed at `C:\Users\DaveWitkin\AppData\Local\Microsoft\WinGet\Packages\Oven-sh.Bun_Microsoft.Winget.Source_8wekyb3d8bbwe\bun.exe`).
- `opencode models` returns multiple `minimax` identifiers including `opencode/minimax-m2.5`, `opencode/minimax-m2.7`, `opencode/minimax-m3`, and `opencode-go/minimax-m3`. The plan must use an enumerated identifier, not a guessed one.

## Requirements

- [x] Capture one sanitized, reproducible local-run failure with debug logging before changing runtime or storage. Bounded by an explicit timeout to avoid hangs.
- [x] Identify every executable OpenCode binary on `PATH` and determine whether Desktop/server and CLI versions are mixed. Use `(Get-Item $binaryPath).VersionInfo.FileVersion` for a stable version read.
- [x] Read-only `node:sqlite` probe of the shared database (PRAGMA quick_check, `session_message` schema, `__drizzle_migrations` count and last 3 IDs, session/session_message row counts), then take a non-destructive backup via the SQLite `backup()` API. NEVER use `Copy-Item` on a live WAL-mode DB.
- [x] Upgrade the canonical OpenCode CLI using its detected npm install method; do not edit the SQLite schema or reset storage as a first-line fix.
- [x] Stop the running OpenCode Desktop processes (which hold the DB and can re-migrate the schema) before the upgrade; verify zero `OpenCode.exe` processes remain.
- [x] Validate a fresh standalone one-word `opencode run` smoke and a fresh `serve` plus `run --attach` path using an enumerated MiniMax model identifier. Verify the new session is listed in `opencode session list` after each smoke.
- [x] Confirm the resulting session and message records are persisted and that no duplicate/older binary remains the active command (post-upgrade version check in a fresh `pwsh` shell).
- [x] If upgrading does not fix the issue, produce a minimal, sanitized GitHub issue/update with version, binary path, error reference, schema evidence, and reproduction steps.

## Non-requirements

- [x] Do not delete `%USERPROFILE%\.local\share\opencode`, reset authentication, or alter `session_message`/its triggers as a first response.
- [x] Do not expose provider credentials, authentication files, or raw configuration values in logs, artifacts, or GitHub reports. Strip `Authorization: Bearer ...`, `x-api-key: ...`, and `password=...` lines from any captured log via `[regex]::Replace`.
- [x] Do not treat a successful `session list` operation as proof that session-message writes are healthy.
- [x] Do not claim that headless `serve` bypasses a broken shared-database write path; it is a supported reuse/cold-start optimization that must be tested after runtime compatibility is restored.
- [x] Do not assume the SQLite `sqlite3.exe` CLI is installed on the host (verified 2026-07-14: it is NOT on this Windows host). Use Node.js `node:sqlite` (Node 24.12.0 ships it built-in) instead.

## Acceptance criteria

- [x] A pre-change evidence log (`evidence-2026-07-14.md`) distinguishes session-list reads from session/message writes and contains the exact sanitized failure signature, the active CLI version (1.15.10), the Desktop version (1.17.19), and a hash-sanitized backup reference. Zero `Authorization` / `x-api-key` substrings remain in the log.
- [x] The active binary and database migration/schema state are recorded, with a verified `sqlite.backup()` snapshot retained at `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\opencode-pre-upgrade-2026-07-14-<ts>.db` (size > 1 GB, SHA256 hash recorded).
- [x] The active runtime is upgraded to a release that contains the upstream `seq` fix (or an explicitly justified newer stable release), confirmed by `opencode --version` in a fresh `pwsh` shell reporting a minor >= 16.
- [x] Both standalone and attached-server smoke tests return exit 0, the new session is listed in `opencode session list --max-count 5` with the smoke title, and no `session_message.seq` substring appears in either smoke log.
- [x] The MiniMax model probe uses an identifier actually returned by `opencode models`; no guessed provider/model string is used.
- [x] The plan, metadata, execution log, validation report, and Conductor ledgers (`tracks.md`, `tracks-ledger.md`) are synchronized at closeout, with date format `YYYY-MM-DD` consistent across both ledgers.
