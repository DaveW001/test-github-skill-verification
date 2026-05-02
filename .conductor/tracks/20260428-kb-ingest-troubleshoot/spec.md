# Spec

## Goal
Diagnose and fix the `opencode-job-development-...-knowledge-base-ingest` scheduled task so it successfully runs the hourly KB ingestion pipeline.

## Background
The KB ingest job runs hourly via Windows Task Scheduler. Every run fails with exit code `-2147024894` (0x80070002 / `ERROR_FILE_NOT_FOUND`). Manual testing of `opencode run` produces `Error: Session not found` regardless of flags, agent, or working directory. The job has produced zero new entity extractions since creation on 4/27.

### Known Facts
1. **Scheduled task config:** `opencode run --agent general --title "KB Ingest Hourly" -- "Run the knowledge base hourly ingestion..."`
2. **`--agent general`** triggers a warning: `agent "general" is a subagent, not a primary agent. Falling back to default agent`
3. **Every `opencode run` invocation fails** with `Error: Session not found` — even without `--agent`, `--title`, or a message
4. **OpenCode process is running** (PID 30676, the TUI app) — the DB is likely locked
5. **OpenCode version:** 1.14.25
6. **`opencode.json` has `ms365` MCP still configured** despite the 3/15 cleanup track (it was only removed from the project-level config, not the global `AppData\Roaming\opencode\opencode.json`)
7. **Ingest log** shows all files stuck at `ready_for_extraction` with 0 entities created; PDF keeps failing on `doc-to-markdown` dependency

### Root Cause Hypotheses (ordered by likelihood)
1. **DB lock:** The running OpenCode TUI holds a write lock on `opencode.db`, preventing `opencode run` from creating a new session
2. **`opencode run` regression in v1.14.x:** The `Session not found` error on every invocation suggests a CLI bug
3. **`general` agent doesn't exist as a primary agent:** The `--agent general` flag may cause argument parsing to fail silently

## Requirements
- [ ] Identify the exact cause of `Error: Session not found`
- [ ] Fix `opencode run` so it works in non-interactive / scheduled mode
- [ ] Verify the KB ingest pipeline runs end-to-end successfully
- [ ] Confirm `general` agent is either created as a primary agent or the job uses the correct agent name
- [ ] Update the scheduled task with the corrected invocation
- [ ] Clean up the `ms365` MCP entry from global `opencode.json` (leftover from 3/15 cleanup)

## Non-Requirements
- [ ] Modifying the knowledge graph schema or ingestion scripts
- [ ] Changing the KB ingest job's schedule or cadence
- [ ] Updating the scheduler registry (will be handled by the sync task)

## Acceptance Criteria
- [ ] `opencode run` successfully creates a new session and executes a simple message
- [ ] The KB ingest scheduled task completes with exit code 0
- [ ] The ingest log shows at least one successful extraction after the fix
- [ ] The `ms365` MCP is removed from global `opencode.json`
- [ ] All tasks in plan.md marked [x]
