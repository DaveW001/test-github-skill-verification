# P2.1 - Standalone smoke test result

| Field | Value |
| --- | --- |
| CLI version | 1.18.1 (post-upgrade) |
| Model id (enumerated from `opencode models`) | `opencode-go/minimax-m3` |
| Prompt | `echo` |
| Title | `rca-smoke-2026-07-14` |
| Exit code | 0 (no timeout; completed within the 90s ceiling) |
| New session id | `ses_09c8eda17ffe9nlF2g3m55gWrV` |
| MiniMax response | yes (tokens total 9564, input 9389, output 61, cost 0.00289674 USD) |

## Authoritative acceptance checks

- BEFORE session count (read-only `node:sqlite`) = 2706 ; AFTER = 2707 -> delta **+1 (>= 1)** PASS.
- The smoke session is the FIRST entry in `opencode session list --max-count 5 --format json` with `title` = `rca-smoke-2026-07-14` PASS.
- Smoke log `session_message.seq` substring hits = **0** PASS.
- Smoke log "Session not found" hits = **0** (the pre-upgrade nested-execution error did NOT recur with 1.18.1).

## Plan check adaptation (documented)

The plan's before/after count used `opencode session list --max-count 1000 --format json`, which CAPS at 1000 rows; with 2706+ sessions both before and after would read 1000, giving a false 0 delta. Substituted the accurate read-only `SELECT COUNT(*) FROM session` as the baseline (closest deterministic check); the title-in-`session list --max-count 5` check is unchanged and is the more reliable signal.

## Write-path confirmation (track core goal)

- The smoke session has **2 rows in the core `message` table** (user prompt + assistant reply); `message` total = 72690. The core write path is healthy.
- The `session_message` projection (the table carrying the `seq INTEGER NOT NULL` column at the center of the original failure) stayed at 404 rows (0 rows for the smoke session). This confirms the 1.18.1 runtime no longer hits the null-`seq` insert failure that blocked 1.15.x. End-to-end `opencode run` now creates a session, persists messages, and returns a model response.

## Raw smoke stdout (sanitized)

Retained at `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\rca-p2p1\smoke-stdout.log`. Contains `sessionID`, a `text` part, and a `step_finish` part with token/cost accounting. Zero secret header substrings (Bearer-auth / api-key / password = 0 hits).