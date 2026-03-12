# Osgrep CLI-Only Re-enable Checklist

**Status:** Active Draft  
**Last Updated:** 2026-03-12

This checklist is for a future re-enable attempt using direct CLI only.
Do not re-enable MCP/bridge paths as part of this checklist.

## Preconditions

- [ ] Disabled-by-default policy is still in effect for normal workflows.
- [ ] `osgrep --help` and `osgrep doctor` both pass locally.
- [ ] `scripts/utils/osgrep_debug_wrapper.py` exists and runs.
- [ ] `scripts/utils/osgrep_process_snapshot.ps1` exists for timeout snapshots.

## Reproduction Coverage

- [ ] Run direct CLI checks in a small repo (`index`, search, `trace`).
- [ ] Run the same checks in a large repo.
- [ ] Run checks in a path containing spaces.
- [ ] Run invalid-path and quoted-path cases and capture expected failure behavior.
- [ ] Validate stale worker cleanup path before launch (`--cleanup-stale`).

## Windows Environment Checks

- [ ] Record Defender exclusion status for the test path.
- [ ] Record whether behavior changes with/without exclusions (if feasible).

## Evidence Capture

- [ ] Save wrapper logs under `logs/osgrep-debug/` for every run.
- [ ] For any timeout, verify snapshot files were generated.
- [ ] Summarize outcomes in the active conductor track before any policy change.

## Exit Criteria

- [ ] Direct CLI runs are repeatably successful across small/large/spaced-path repos.
- [ ] No unexplained timeouts in controlled CLI-only runs.
- [ ] Remaining failures are isolated to MCP/service-mode path (if any).
- [ ] Track owner has a documented fix path and validation plan.
