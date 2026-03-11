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
- [ ] Compare direct CLI vs MCP/server invocation on the same repo
- [ ] Test clean repo vs large repo vs repo with existing `.osgrep` state
- [ ] Test search vs index vs trace style commands separately
- [ ] Test with antivirus exclusions and with stale worker cleanup before launch
- [ ] Test invalid-path and quoted-path inputs to check cwd/path handling regressions

## Phase 5: Root Cause and Fix Path
- [ ] Narrow the primary failure mode with evidence
- [ ] Decide whether the fix belongs in local wrapper/config, OpenCode integration, or upstream osgrep
- [ ] Draft upstream issue or local patch plan with reproduction steps and logs

## Phase 6: Post-Build Consistency and Quality Fixes
- [ ] Resolve osgrep policy conflicts in active guidance (keep disabled-by-default direction)
- [ ] Replace hardcoded local absolute paths in global standards with portable repo-relative references
- [ ] Strengthen `scripts/validate-prompt-patterns.py` with content-quality checks
- [ ] Tighten remaining `osgrep` vs `perplexity-search` trigger phrase ambiguity

## Validation

The track is ready to close when we have a repeatable reproduction, captured logs, and a clear fix owner/path.
