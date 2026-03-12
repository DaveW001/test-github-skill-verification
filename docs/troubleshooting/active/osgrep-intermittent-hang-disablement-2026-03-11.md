# Troubleshooting: Osgrep Current Status, Disablement, and Investigation

**Date**: 2026-03-11
**Component**: osgrep (CLI usage vs OpenCode integration policy)
**Status**: Active Investigation

## Read This First

This is the central status doc for osgrep in this repo.

Current position:
- direct `osgrep` CLI commands are not the main problem in current testing
- `osgrep mcp` is not required for the intended OpenCode workflow
- OpenCode-side osgrep usage remains disabled for now to avoid repeated hangs and confusion
- if osgrep is revisited later, the next experiment should be CLI-only, not MCP or bridge based

## What Is Disabled Right Now

- OpenCode's built-in osgrep usage is disabled in local config and agent guidance
- the custom `osgrep` tool currently returns a disabled notice instead of launching osgrep automatically
- the `osgrep` skill now documents the disablement instead of recommending activation
- the scheduled `osgrep-auto-indexer` job has been converted to a harmless no-op while the investigation is active

This disablement is about OpenCode workflow safety, not a blanket statement that the standalone CLI is unusable.

## What We Thought vs What We Learned

### Earlier Assumption

We were acting as if "osgrep is hanging in general" and treating MCP/server behavior as part of the default intended workflow.

### Current Understanding

- the intended future direction should be CLI-only if osgrep is reintroduced
- MCP is not required for normal osgrep usage
- the strongest reproducible failures we found are in `osgrep mcp`, not in direct CLI commands
- earlier documentation overstated MCP as the active or necessary path

## Current Conclusion

Right now the most accurate summary is:

1. Direct CLI behavior looks healthy in current tests.
2. MCP/service-mode behavior is the most suspicious path.
3. Since MCP is not required, future re-enablement work should be CLI-only first.
4. OpenCode osgrep automation stays disabled until we deliberately reintroduce a CLI-only flow.

## Known Local Evidence

### 1. Historical Desktop Hang Report

Prior local notes referenced a desktop hang investigation, but the exact active file path should be revalidated before relying on it.

Observed in the historical summary:
- `osgrep index` ran for a very long time
- worker processes appeared idle
- cleanup did not obviously reveal `.osgrep` corruption

### 2. Unwanted Folder Creation Bug

Reference: `docs/troubleshooting/active/osgrep-unwanted-folder-creation-SUMMARY.md`

Observed:
- osgrep created directories from string inputs
- `.osgrep/` workspaces were created in invalid locations
- this was documented as an MCP/integration-specific failure mode

### 3. Integration History

Reference: `docs/reference/osgrep-configuration.md`

Observed:
- bridge mode was abandoned after instability and bad working-directory side effects
- later documentation treated `osgrep mcp` as the normal OpenCode path
- current investigation suggests we should not assume MCP is necessary at all

## Most Likely Hypotheses

This is still a hypothesis list, not a confirmed root cause:

1. **MCP/server lifecycle issue**
   - child workers are spawned but one or more never progress or never exit cleanly

2. **Stale lock or index-state issue**
   - LMDB, LanceDB, or related `.osgrep` state is left in a condition that blocks future runs

3. **Path or cwd handling bug**
   - the wrong working directory or a malformed path reaches osgrep during startup or command dispatch

4. **stdio or subprocess deadlock**
   - a parent/child process pipe fills or waits indefinitely during startup, indexing, or worker communication

5. **Windows-only environmental interference**
   - antivirus, file locking, or process cleanup behavior causes intermittent stalls under heavy indexing work

## Investigation Strategy

Focus on observability and on separating CLI behavior from optional integration behavior.

### Logging to Capture

For each osgrep invocation, log:
- timestamp start/end
- command and args
- working directory
- parent pid and child pid
- stdout/stderr capture
- exit code or timeout
- repo path and `.osgrep` path

During a hang, also capture:
- full process tree
- worker process runtimes
- open handles or file locks if available
- `.osgrep`, LMDB, and LanceDB file timestamps

### Debugging Tools Added

- `scripts/utils/osgrep_debug_wrapper.py` runs osgrep with structured logging and timeout handling
- `scripts/utils/osgrep_process_snapshot.ps1` captures Windows process snapshots and `.osgrep` database-path metadata on timeout

Example usage:

```bash
python scripts/utils/osgrep_debug_wrapper.py --label index-test -- -- index
python scripts/utils/osgrep_debug_wrapper.py --cwd C:/development/opencode --label search-test -- "where do requests enter the server"
```

### Reproduction Matrix

Run the same scripted checks across:
- direct CLI vs MCP startup
- clean repo vs existing indexed repo
- `index` vs search/query vs `trace`
- normal repo paths vs paths with spaces
- post-cleanup state vs stale-worker state

## Reproduction Progress (2026-03-11)

### Direct CLI Runs

Successful direct CLI runs were captured with the debug wrapper:

- small repo index
- small repo search
- small repo trace
- large repo search
- large repo index
- spaced-path repo index
- spaced-path repo search

Observed result:
- direct CLI looked healthy in current tests
- index/search/trace completed successfully
- a path containing spaces did not reproduce the failure

### MCP Startup Runs

Timed-out MCP startup runs were captured in both small and large repos.

Observed behavior:
- both runs timed out after about 11-12 seconds
- stderr contained only sync lifecycle messages
- no ready signal or clean exit was observed
- Windows process-tree termination was needed for cleanup

### Current Interpretation

Current evidence suggests the highest-probability issue is in MCP/server startup lifecycle on Windows rather than in base CLI indexing/search behavior.

This does not rule out secondary issues in locks or worker cleanup, but it narrows the immediate investigation target.

## CLI-Only Next Step Plan

If osgrep is reintroduced later, use this order:

1. Re-enable only a direct CLI wrapper path.
2. Keep MCP and bridge paths disabled.
3. Start with explicit commands like `index`, `search`, and `trace` in a controlled repo.
4. Require debug-wrapper logs for the first round of reintroduced usage.
5. Only consider wider rollout after multiple clean CLI-only sessions.

## What We Have Tried

- historical bridge-based integration
- historical `osgrep mcp`-based OpenCode integration
- full disablement of active OpenCode osgrep usage
- structured logging via wrapper and timeout snapshots
- direct CLI tests in small, large, and spaced-path repos
- MCP startup tests in small and large repos

## What We Are Trying Now

- freeze the current state in docs so future troubleshooting starts from facts
- keep osgrep disabled inside OpenCode for now
- favor a future CLI-only trial over any MCP-based reintegration

## Practical Next Steps

1. Keep OpenCode osgrep automation disabled.
2. Preserve the CLI debug wrapper and logs as the starting point for future work.
3. Treat CLI-only reintroduction as the next safe experiment if osgrep is retried.
4. Avoid MCP/bridge reintroduction unless there is a specific reason and a separate test plan.
5. If future CLI-only trials fail, resume root-cause work from the saved logs and notes here.

## External Research Notes

Recent web research points to several Windows-relevant failure classes that match the observed pattern:
- child process stdio deadlocks
- orphaned worker processes
- file watcher or heavy I/O edge cases
- mandatory file locking around local databases
- cwd/path resolution bugs during subprocess startup

These do not prove osgrep is hitting one of them, but they are the right buckets to test first.

## Related Docs

- investigation track: `.conductor/tracks/20260311-osgrep-disable-and-root-cause/`
- historical config reference: `docs/reference/osgrep-configuration.md`
- historical MCP-specific bug summary: `docs/troubleshooting/active/osgrep-unwanted-folder-creation-SUMMARY.md`
