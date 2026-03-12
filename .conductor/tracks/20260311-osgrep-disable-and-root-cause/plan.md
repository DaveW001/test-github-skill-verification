# Plan: Disable Osgrep and Find Root Cause

**Track ID**: 20260311-osgrep-disable-and-root-cause
**Created**: 2026-03-11
**Status**: Active

## Phase 1: Disable Default Usage
- [x] Update global agent guidance to stop using osgrep by default
- [x] Update active agent docs that still instruct osgrep-first behavior
- [x] Capture the disablement decision in troubleshooting documentation

## Phase 2: Consolidate What We Already Know
- [x] Review recent local hang and unwanted-folder investigations
- [x] Review current osgrep configuration and prior bridge history
- [x] Gather external research on Windows Node/MCP hanging patterns

## Phase 3: Add Observability
- [x] Add a reproducible wrapper or debug command that logs cwd, argv, env subset, parent pid, child pid, and timestamps for every osgrep invocation
- [x] Capture stdout, stderr, exit code, and timeout events to a dedicated log file
- [x] Record worker process trees and runtime snapshots during a hang
- [x] Add database-path snapshots for `.osgrep`, LMDB, and LanceDB state

## Phase 4: Controlled Reproduction Matrix
- [x] Compare direct CLI vs MCP/server invocation on the same repo
- [x] Test clean repo vs large repo vs repo with existing `.osgrep` state
- [x] Test search vs index vs trace style commands separately
- [x] Test with antivirus exclusions and with stale worker cleanup before launch
- [x] Test invalid-path and quoted-path inputs to check cwd/path handling regressions

## Phase 5: Root Cause and Fix Path
- [x] Narrow the primary failure mode with evidence
- [x] Decide whether the fix belongs in local wrapper/config, OpenCode integration, or upstream osgrep
- [x] Draft upstream issue or local patch plan with reproduction steps and logs

## Phase 6: Post-Build Consistency and Quality Fixes
- [x] Resolve osgrep policy conflicts in active guidance (keep disabled-by-default direction)
- [x] Replace hardcoded local absolute paths in global standards with portable repo-relative references
- [x] Strengthen `scripts/validate-prompt-patterns.py` with content-quality checks
- [x] Tighten remaining `osgrep` vs `perplexity-search` trigger phrase ambiguity

## Validation

The track is ready to close when we have a repeatable reproduction, captured logs, and a clear fix owner/path.

## Current Findings

- Direct CLI behavior is healthy in current tests: `index`, semantic search, and `trace` all completed in small, large, and spaced-path repos.
- MCP-style startup (`osgrep mcp`) consistently failed to exit or become ready within the 10 second window in both the small repro repo and the main `opencode` repo.
- During timed-out MCP runs, stderr consistently showed only sync logs: `Scheduling initial sync`, `Starting file sync`, `Sync complete`.
- Timed-out MCP startup required Windows process-tree kill behavior; simple parent termination was not enough for reliable cleanup.
- Current evidence points more strongly at MCP/server lifecycle behavior than at basic indexing, search, trace, or path-with-spaces handling.
- Documentation is now being normalized around one central current-status doc and a CLI-only next-step plan.
- Additional Phase 4/5 execution details and fix-owner decisions were captured in `.conductor/tracks/20260311-osgrep-disable-and-root-cause/PHASE4-5-RESULTS-2026-03-12.md`.
