# Smoke Test Report - 2026-07-05

Track: `20260705-conductor-pipeline-tdd-doc-stages`
Smoke target: Phase 4.2 bookkeeping route smoke
Requested by user after OpenCode restart.

## Result

**FAIL / BLOCKED before synthetic run.**

The restarted session now recognizes all three new agents, including the GLM-backed doc-writer:

| Agent | Observed model | Recognition |
|---|---:|---|
| `conductor-test-writer` | `gpt-5.5` | PASS |
| `conductor-test-runner` | `opencode-go/minimax-m3` | PASS |
| `conductor-doc-writer` | `zai-coding-plan/glm-5.1` | PASS |

However, the user-facing slash-command entrypoint is stale:

`C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`

It still says:

- `Run the six-stage Conductor pipeline...`
- `execute all six stages...`
- `Evaluate ... A+C re-validation threshold after Stage 5`

Expected for this smoke test:

- 9-stage pipeline entrypoint
- Track-type branching via `metadata.track_type`
- Bookkeeping route: `1 -> 2 -> 3 -> 5 -> 7 -> 8 -> 9`
- Skip code-only stages: Stage 4 test-writer, RED gate 4b, Stage 6 test-runner

Actual state:

- The orchestrator agent body has the expected 9-stage branching text.
- The slash-command entrypoint still instructs the old 6-stage flow.

## Why the smoke test stops here

Phase 4.2 is intended to prove that the pipeline, as invoked, correctly classifies a bookkeeping track and skips TDD stages. Because the primary command entrypoint still instructs the old 6-stage pipeline, a real smoke run through the command would not validate the new architecture and could route incorrectly.

This is a control-plane failure, not an agent-recognition failure.

## Verdict

Phase 4.2 remains unchecked. Do not run the synthetic bookkeeping smoke track until the stale command entrypoint is updated to the 9-stage flow.

## Required fix before rerun

P0: Update `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md` from the old six-stage instructions to the canonical 9-stage pipeline with `track_type` branching and corrected threshold timing.