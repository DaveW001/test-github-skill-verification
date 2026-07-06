# Peer Review Report - 2026-07-05

Track: `20260705-conductor-pipeline-tdd-doc-stages`
Reviewer: `peer-review`
Scope: architecture, logic, structure, and missing considerations for the 9-stage Conductor pipeline.

## Verdict

**Do not accept as operationally complete yet.**

The architecture is promising, but important control-plane artifacts remain stale or under-specified.

## Strengths

- Strong separation of RED test authoring, GREEN implementation, independent test running, validation, and documentation closeout.
- `track_type` branching is necessary and appropriate for bookkeeping vs code-bearing tracks.
- Retry caps reduce infinite loops.
- Tool-call self-bounding and anomaly logging address prior stall/failure modes.
- Executor/validator diversity is preserved.

## P0 Findings

1. **Slash-command entrypoint is stale.**
   - File: `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`
   - It still says six-stage pipeline, execute all six stages, and evaluate A+C after Stage 5.
   - Impact: the user-facing entrypoint can drive old routing and skip or misorder the new TDD/docs stages.

2. **Stage numbering/fallback references are inconsistent across references.**
   - Examples cited by peer review: `SKILL.md`, `threshold-policy.md`, `conductor-track-validator-alt.md`, and some fallback wording still refer to old Stage 4/5/6 semantics.
   - Impact: agents may apply threshold/fallback rules to the wrong stage.

3. **Stage 7 failure -> fix -> Stage 8 re-validation route is under-specified.**
   - Need exact routing for validation failures, bookkeeping-only stale artifacts, plan flaws, and code/test failures.

## P1 Findings

1. **RED-state gate is too weak.**
   - It must prove newly written acceptance tests fail for expected behavioral/assertion reasons, not just any nonzero test-suite exit.
   - Premature green after reopen cap should stop or ask the user, not proceed silently.

2. **Stage 9 mutates docs after validation with no post-doc validation.**
   - Need either a lightweight doc-validation gate or strict constraints that docs cannot change user-facing contract/setup meaning.

3. **Code track with no test framework is unresolved.**
   - Need formal policy: scaffold test framework, stop for user approval, or route to degraded non-TDD mode.

## P2 Findings

1. Artifact inventory should include `test-run-report-<ts>.md`, `doc-update-log-<ts>.md`, and RED-gate evidence.
2. Read-only verifier behavior is prompt-enforced despite `bash: allow`; constrain report-writing paths explicitly.
3. Consider moving Stage 4 test-writer to a different model family than Stage 1 planner for stronger adversarial test design.

## Recommendation

Fix the P0 control-plane issues before relying on the pipeline operationally or rerunning Phase 4.2. Then rerun bookkeeping smoke. Defer code-track and RED-gate smoke tests until a repo with a real test framework is available.