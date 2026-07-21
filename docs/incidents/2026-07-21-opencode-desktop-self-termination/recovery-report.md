# OpenCode Desktop self-termination: recovery report

Date: 2026-07-21  
Status: recovered and validated

## Outcome

OpenCode Desktop now opens and remains running. The harmful session was preserved in two readable/export forms, removed through the supported CLI, and scrubbed from active Desktop state. Four controlled launch checks completed without a renderer process loss or sidecar exit.

No event-log compaction was applied. The required read-only status and dry-run checks found zero eligible candidates, so a database mutation would provide no benefit.

## Root cause

The immediate cause was session `ses_08e6f52adffeqhDrwFlwAVN4wf`, titled **2026-07-17 Running kg-ck12-stub-enrichment pipeline**. Its workflow repeatedly ran:

```powershell
Get-Process -Name 'opencode*' | Stop-Process -Force
```

That wildcard matches OpenCode Desktop's own processes. When Desktop restored or resumed the session, the command killed the renderer and/or sidecar hosting the session, which presented as an application crash on open.

The enabling conditions were:

1. Global Bash permission was `allow`.
2. Several primary agents explicitly overrode Bash permission with `allow`.
3. Desktop persisted the offending session in active state, allowing it to be restored after relaunch.

The SQLite database itself was not corrupt. Integrity checks returned `ok` before and after session deletion. A known `ResizeObserver loop completed with undelivered notifications` renderer warning remained in each test log, but it did not terminate a process and was not the crash cause.

## Evidence preserved

- Readable discussion: `C:\development\opencode\docs\incidents\2026-07-21-opencode-desktop-self-termination\session-discussion-readable.md`
- Raw supported CLI export: `C:\Users\DaveWitkin\AppData\Local\Temp\opencode-recovery-20260721\ses_08e6f52adffeqhDrwFlwAVN4wf.raw.json`
- Raw export size: 13,840,611 bytes; 362 messages
- Readable export size: 27,929 bytes; 627 lines
- Readable export includes visible user and assistant text only. It excludes reasoning, tool traffic, patch payloads, step metadata, ignored text, and code blocks.

## Recovery actions

### 1. Backed up and verified the database

- Source: `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`
- Backup: `C:\Users\DaveWitkin\AppData\Local\Temp\opencode-recovery-20260721\opencode.db.pre-recovery-20260721`
- Backup size: 17,693,294,592 bytes
- SHA-256: `d62a48e061a33ddcba3269136c93c8ca334093586186cde09aafdbf3a9e8d838`
- Backup `PRAGMA quick_check`: `ok`
- Backup `user_version`: `0`

### 2. Isolated persisted Desktop state

The three active `.dat` files containing the session ID were backed up and moved aside before the first recovery launch. After supported session deletion, newly rebuilt state still contained a stale reference, so it was backed up and isolated a second time. The final rebuilt active state contains no occurrence of the deleted session ID.

Backup locations:

- `C:\Users\DaveWitkin\AppData\Local\Temp\opencode-recovery-20260721\desktop-state-before`
- `C:\Users\DaveWitkin\AppData\Local\Temp\opencode-recovery-20260721\desktop-state-post-delete-stale`

The isolated originals remain recoverable beside the active Desktop state with `.isolated-20260721` or `.isolated-post-delete-20260721` suffixes.

### 3. Added process-kill guardrails

Updated `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` so ordinary Bash remains allowed while destructive OpenCode process patterns are intercepted:

```json
{
  "*": "allow",
  "Stop-Process *": "ask",
  "Stop-Process -Force *": "deny",
  "Stop-Process -Name *": "deny",
  "taskkill *opencode*": "deny"
}
```

Removed the broad `bash: allow` override from these primary agent definitions so they inherit the global guardrail:

- `build.md`
- `01-planner.md`
- `boost.md`
- `conductor-pipeline-orchestrator.md`

Pre-change copies are in `C:\Users\DaveWitkin\AppData\Local\Temp\opencode-recovery-20260721\config-before`.

`opencode debug config` resolved successfully and confirmed the effective rules. Automated tests verify both the global deny patterns and inheritance by the primary agents.

### 4. Removed the harmful session through the supported interface

Command used:

```text
opencode session delete ses_08e6f52adffeqhDrwFlwAVN4wf
```

Read-only verification after deletion:

- Matching session rows: 0
- Matching message rows: 0
- Matching part rows: 0
- Total sessions: 3,056
- Live sessions: 2,437
- Live database `PRAGMA quick_check`: `ok`

### 5. Ran event-log compactor checks without mutation

Status:

- Events: 742,807
- Compactable events: 464,701
- Database size: 16.48 GiB
- Schema user version: 0

Dry run with a 14-day cutoff:

- Aggregates scanned: 957
- Candidates found: 0
- Eligible candidates: 0
- Estimated bytes reclaimed: 0
- Manifest hash: `d5a5d28e5e71f2cef2de5a189bb53d3277cfeb9ba06b05a903633b30af812bce`
- Schema fingerprint: `832ba3ff8ed21d94dd39fc6980375f27c150eb7e9322331006da5e6ff8ea4086`

No apply, activation, vacuum, or rollback operation was performed. The dry run supplied no eligible work, and activation also requires a separate exact-manifest-hash approval and validation gate.

## Validation results

Four controlled Desktop launches were observed for 25-35 seconds each:

| Launch | Result | Process loss | Sidecar exit | Renderer warning |
|---|---|---:|---:|---:|
| Initial state isolation | Stable | 0 | 0 | 1 |
| Post-deletion check 1 | Stable | 0 | 0 | 1 |
| Post-deletion check 2 | Stable | 0 | 0 | 1 |
| Final post-stale-state isolation | Stable | 0 | 0 | 1 |

Final validation also confirmed:

- No active Desktop `.dat` file contains the deleted session ID.
- No launch resumed the deleted session's `Stop-Process` workflow.
- No OpenCode process was left running after the controlled close.
- Guardrail and readable-export tests pass: 3 passed.

The controlled launches did still record a 404 for the deleted session. That follow-up stale-route issue is resolved below.

## Follow-up: stale deleted-session route

Later normal launches exposed `Session not found: ses_08e6f52adffeqhDrwFlwAVN4wf`. The session and its dependent rows were still correctly absent from SQLite. The remaining session ID was found in Chromium Local Storage (`Local Storage\leveldb\000036.log`) and browser Cache, not in the active OpenCode `.dat` state.

Desktop was closed through its exact owned process, and only the regenerable `Local Storage` and `Cache` directories were moved to:

`C:\Users\DaveWitkin\AppData\Local\Temp\opencode-recovery-20260721\stale-ui-state-20260721-1327`

After relaunch, Desktop remained responsive, the new Local Storage and Cache contained no deleted-session ID, and the new renderer log contained no session-not-found, fatal-renderer, process-gone, or sidecar-exit entry. A final read-only database check returned zero session/message/part rows and `PRAGMA quick_check: ok`.

Successful follow-up launch log: `C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\logs\20260721T172619`

## Follow-up plan

1. Use Desktop normally; do not restore either isolated state snapshot.
2. Retain the database backup, raw session export, and state/config backups until the recovery is accepted.
3. Keep the new process-kill guardrail tests in the repository and run them after permission/config changes.
4. Treat broad process-name termination as prohibited in OpenCode sessions. If a specific owned process must be stopped, target its exact captured PID and verify ownership first.
5. Do not run compactor apply/activation for this incident: the dry run found no candidates. Re-evaluate only as a separate maintenance task with a fresh backup and exact manifest approval.
