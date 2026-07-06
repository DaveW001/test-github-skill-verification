# Decisions Resolved - 20260705-conductor-pipeline-tdd-doc-stages

Resolved: 2026-07-05
Resolved by: Orchestrator, per user instruction ("Option A - adopt all recommended defaults")

User authorized adoption of all seven recommended defaults from spec.md section 9 / plan.md Task 0.1. Answers recorded below; no item remains open.

## Decision 1 - Track-type discriminator mechanism
Answer: Option A - explicit `track_type` field in metadata.json (`code` | `bookkeeping`), declared by plan-creator. Default to `bookkeeping` (skip TDD) when the plan-creator cannot determine it.

## Decision 2 - Doc-writer position
Answer: After re-validation (Stage 9), as a true closeout step. Docs are the final deliverable, not part of the validated scope.

## Decision 3 - Context-isolation level
Answer: v1 prompt-level isolation. The test-writer is instructed to derive tests from the spec/acceptance criteria, not from reading implementation. Hard worktree-per-agent isolation is a future v2 enhancement pending platform support.

## Decision 4 - Doc-writer model
Answer: openai/gpt-5.5 (variant low). Good prose quality and differs from the glm-5.2 executor (diversity preserved).

## Decision 5 - Agent names
Answer: `conductor-test-writer`, `conductor-test-runner`, `conductor-doc-writer`. Consistent with the existing `conductor-*` naming convention.

## Decision 6 - Existing in-flight tracks
Answer: Let existing tracks finish on the current 6-stage path. The new 9-stage pipeline applies to new tracks only. No mid-flight migration.

## Decision 7 - Test-framework metadata field
Answer: Yes. metadata.json gains `test_framework` (e.g. `bun:test`, `vitest`, `pytest`) and `test_command` (e.g. `bun test`, `vitest run`) so agents do not re-detect the runner each run.

## Test-framework baseline for the opencode repo (plan Task 0.3)
Finding: This opencode fork has NO unit-test runner configured. package.json contains only `test:visual:*` playwright scripts. There is no `test`, `typecheck`, `build`, or `lint` script; no bunfig.toml; no vitest/jest config; zero `*.test.ts`/`*.spec.ts` files. Therefore `test_framework` = `none` and `test_command` = `n/a` for this repo. This is expected: this meta-track is bookkeeping scope and will not run through TDD stages itself. The metadata fields are informational defaults for future code-bearing tracks that DO have a test runner.
