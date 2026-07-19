# P2.2 - Supported headless serve + --attach smoke result

| Field | Value |
| --- | --- |
| CLI version | 1.18.1 |
| Loopback port | 4096 (first free in 4096..4105) |
| Server PID | 61784 |
| Server health signal | "opencode server listening on http://127.0.0.1:4096" + port bound (adapted) |
| Attach URL | http://127.0.0.1:4096 |
| Model id | opencode-go/minimax-m3 |
| Attached run exit code | 0 (within the 90s ceiling) |
| Attach session id | ses_09c88ec9fffeJqbzZdwJw1dmOT |
| Assistant reply | "echo\n\nReady when you are. What would you like to plan or build?" (tokens total 14097, cost 0.00426024 USD) |
| Clean shutdown | listener on 4096 gone after Stop-Process -Id 61784 (PORT_STILL_LISTENING_COUNT=0) |

## Authoritative acceptance checks

- Attached smoke exit code = 0 PASS.
- New attach session persisted: DB row exists (`id=ses_09c88ec9fffeJqbzZdwJw1dmOT`, title="Quick test message"); `message` rows for that session = 2 (user + assistant); `session` total 2707 -> 2708 (delta +1) PASS. Listed in `opencode session list --max-count 5`: see below.
- Attach smoke log `session_message.seq` hits = 0 PASS; "Session not found" hits = 0.
- Listener on port 4096 gone after shutdown (count = 0) PASS.

## Plan check adaptations (documented deviations)

1. **Health probe** (P2.2 step 3/4): the plan required raw `Invoke-WebRequest http://127.0.0.1:$port/global/health` to return 200 and `/doc` to return 200. In 1.18.1 the headless server **requires authentication** for HTTP endpoints: `/doc` returns **401 Unauthorized** and `/global/health` does not return 200 to an unauthenticated client (the plan's error-recovery would have wrongly STOPPED here as a false negative). Substituted health signal = the server's own "listening" log line + a bound loopback port (`Get-NetTCPConnection -State Listen -LocalPort 4096`). The authenticated `--attach` client is what actually exercises the server and it succeeded.
2. **Server request log** (P2.2 acceptance): the plan required `Select-String 'POST /session'` in the serve stdout to return >=1 hit. The 1.18.1 server does **not** emit per-request log lines to stdout (serve stdout contained only the single "listening" line; serve stderr was empty). Substituted evidence = the authenticated attached run returned exit 0 and a new persisted session+messages, which proves the server accepted and serviced the session/message write. This is the closest deterministic check.

These adaptations preserve the plan's intent (prove the supported `serve`/`--attach` path creates and persists a session end-to-end) without the false negatives introduced by the newer authenticated-server model.

ATTACH_SESSION_IN_LIST_TOP5 (recorded at execution): see execution log.

ATTACH_SESSION_IN_LIST_TOP5 = True
