# Plan

## Phase 1 - Diagnosis
- [ ] Reproduce the `Session not found` error with verbose logging (`--print-logs --log-level DEBUG`)
- [ ] Check if `opencode run` works when the TUI is NOT running (kill OpenCode process, retry)
- [ ] Check if `opencode run` works with `--attach` flag pointing to the running server
- [ ] Review OpenCode 1.14.25 release notes / changelog for `opencode run` changes
- [ ] Confirm whether `general` agent exists as a primary agent or subagent (check `~/.config/opencode/` and `C:\development\.opencode\agents\`)

## Phase 2 - Fix
- [ ] If DB lock is the cause: either use `--attach` to connect to the running server, or stop the TUI before scheduled runs
- [ ] If agent name is the cause: create a `general` primary agent definition or update the task to use the correct agent
- [ ] If CLI bug: check for opencode update or file an issue; apply workaround
- [ ] Remove `ms365` MCP from `C:\Users\DaveWitkin\AppData\Roaming\opencode\opencode.json`

## Phase 3 - Verification
- [ ] Run `opencode run` manually with the fixed invocation — confirm success
- [ ] Run the KB ingest job manually via Task Scheduler — confirm exit code 0
- [ ] Wait for one automatic hourly run and verify in ingest-log.md
- [ ] Update the scheduled task in Windows Task Scheduler with the corrected command
- [ ] Update this track's metadata.json to completed

## Phase 4 - Cleanup
- [ ] Confirm scheduler-registry-sync picks up the changes (or manually update `C:\development\_shared-scripts\scheduler-registry.md`)
- [ ] Archive this track in the conductor ledger

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.
