# Spec

## Goal
Recover OpenCode Desktop startup on Dave's Windows machine without losing useful OpenCode history, and identify whether the root cause is Desktop state, one malformed/oversized session, an OpenCode database migration issue, or scheduled-job writes.

## Current Assessment
OpenCode Desktop is not failing to spawn the sidecar. In the 2026-06-08 08:45:11 local run, `main.log` shows the sidecar starts and reports ready at `http://127.0.0.1:53109`. The failure is in the renderer: `window.log` reports `renderer unresponsive` with stack samples in `constructMessageRows`, `MessageTimeline`, and `loadMessages`.

The persisted Desktop state points startup at `C:\development\02-Kx-to-process`, with last session `ses_158d41ed8ffeZTg8Fa0jZwqAJG` titled `2026-06-08 Run kg-review-queue-phase2-bulk-approval`. Read-only SQLite inspection found that this session contains 49 messages and 206 parts. Its first user message is about 25 MB and contains summary diffs; one assistant message has a 2.3 MB patch part. This matches the renderer stack: startup reloads a large diff-heavy session and freezes while constructing message rows.

The SQLite file itself is not obviously corrupt: `pragma integrity_check` returned `ok`. However, server logs from earlier scheduled OpenCode runs repeatedly show `NOT NULL constraint failed: session_message.seq`, which means there is also a separate write-path or migration compatibility problem affecting scheduled `opencode run` jobs.

## Constraints
- Do not delete or rewrite `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` without a timestamped backup.
- Do not mutate calendar data or scheduled jobs without explicit approval.
- Prefer reversible Desktop state changes before database-level changes.
- Preserve Dave's project/session history where feasible.
- Keep all commands Windows PowerShell-compatible.

## Non-Goals
- Do not patch OpenCode source code unless state isolation proves the app has an unavoidable product bug.
- Do not force Git garbage collection while another Git process is active.
- Do not remove plugins as the first recovery action; plugin warnings are secondary unless isolation proves otherwise.

## Definition of Done
- Desktop starts cleanly and remains responsive for at least 60 seconds.
- The app can open a safe project and create a new session.
- The problematic startup path is isolated and documented.
- If a mutation was required, rollback commands and backups are recorded.
- The scheduled-job SQLite error is either fixed or captured as a follow-up track with evidence.

## Evidence Sources
- Debug zip: `C:\Users\DaveWitkin\Downloads\opencode-debug-20260608T124539.zip`
- Extracted inspection path used in this diagnosis: `%TEMP%\opencode-debug-20260608T124539`
- Desktop logs: `%TEMP%\opencode-debug-20260608T124539\desktop\20260608T124511`
- Server logs: `%TEMP%\opencode-debug-20260608T124539\server-1`
- Desktop state: `C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\opencode.global.dat`
- OpenCode database: `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`

