# P0/P1/P2 Fixes Report - 2026-07-06

Track: `20260705-conductor-pipeline-tdd-doc-stages`
Scope: Apply fixes/improvements proposed after Phase 4.2 smoke failure and peer-review architecture review.

## Backup

Pre-fix backup snapshot written to:

`C:\development\opencode\.conductor\tracks\20260705-conductor-pipeline-tdd-doc-stages\backups\2026-07-06-p0-p2-fixes\`

Backed up 11 global command/agent/skill files before overwriting.

## Files changed

- `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-alt.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-doc-writer.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`

## Fixes applied

### P0

1. `/conductor-pipeline` command entrypoint rewritten from stale six-stage wording to the canonical nine-stage flow.
2. Command now documents `track_type` branching:
   - `code`: `1 -> 2 -> 3 -> 4 -> 4b -> 5 -> 6 -> 7 -> 8 -> 9`
   - `bookkeeping`: `1 -> 2 -> 3 -> 5 -> 7 -> 8 -> 9`
3. Stale Stage 6 re-validation / Stage 4 execution labels normalized to Stage 8 / Stage 5 where targeted checks found them.
4. `conductor-track-validator-alt` identity updated from Stage 6 to Stage 8.
5. Stage 7 failure routing specified: bookkeeping-only stale artifacts, deliverable/code/test fixes, plan/spec flaws, and blockers now have explicit routes.

### P1

1. RED gate strengthened: valid RED requires newly-written acceptance tests to fail for expected behavioral/assertion reasons mapped to acceptance criteria.
2. Invalid RED causes are explicitly rejected: syntax errors, missing dependencies, harness/setup failures, unrelated pre-existing failures, malformed tests.
3. Premature green or invalid RED reopens Stage 4 once; if unresolved, stop instead of silently continuing.
4. Code tracks without a usable test framework now have explicit policy: user-approved scaffold, stop for decision, or explicit degraded non-TDD mode.
5. Stage 9 doc-safety rule added: semantic/public-contract doc changes require lightweight post-doc validation before final closeout.

### P2

1. Artifact inventory now includes RED-gate evidence, `test-run-report-<ts>.md`, and `doc-update-log-<ts>.md`.
2. Read-only test-runner clarified: source/tests/config read-only; track-report writes allowed only in the active track folder.
3. Stage 4 test-writer moved from `openai/gpt-5.5` to `opencode-go/qwen3.7-plus` for stronger independence from the Stage 1 planner.

## Verification checks

Static checks passed:

- command includes nine-stage/9-stage language.
- command includes `track_type` branching.
- `SKILL.md` has `Re-validation trigger (Stage 8)`.
- `SKILL.md` has valid RED-state language.
- `threshold-policy.md` has code-track-without-test-framework policy.
- `threshold-policy.md` has post-doc validation language.
- `stage-prompts.md` has read-only source/tests/config boundary.
- orchestrator has Stage 7 failure classification routing.
- validator-alt references Stage 8.
- test-writer frontmatter uses `model: opencode-go/qwen3.7-plus`.
- targeted stale-reference sweep found no old six-stage/Stage 6 re-validation/Stage 4 execution/proceed-regardless unsafe references.

## Operational note

These are OpenCode command/agent/skill config-time files. A running OpenCode session keeps already-loaded definitions. Restart OpenCode before rerunning Phase 4.2 smoke so the updated command and agent frontmatter are active.