# Anomaly Summary - 20260703-write-permission-fix - 2026-07-03

Total anomalies for this track: 3

## Entries

| ts | stage | subagent | type | severity | detail |
|---|---|---|---|---|---|
| 07/03/2026 00:00:00 | stage-1 | conductor-plan-creator | permission-prompt | info | write tool was unlisted - fix in progress |
| 07/03/2026 17:56:50 | stage-4 | conductor-track-executor | tool-error | warn | native file tools reported broken (Bun is not defined); session shell-first via bash for whole run |
| 07/03/2026 17:56:50 | stage-4 | conductor-track-executor | deviation | info | Phase 2.1 plan anchor showed 8-space indent but opencode.jsonc uses 4-space; used correct 4-space literal anchor (1 match) per plan intent, 2.2 check passed |

## Source
`C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` (FIFO archive cap 5000)
