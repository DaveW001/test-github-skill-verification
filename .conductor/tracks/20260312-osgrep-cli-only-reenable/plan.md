# Plan: Osgrep CLI-Only Re-Enablement

**Track ID**: 20260312-osgrep-cli-only-reenable
**Created**: 2026-03-12
**Status**: Active
**Priority**: High
**Owner**: Build

## Phase 0: Pre-Flight Environment Validation
- [ ] Verify osgrep CLI responsiveness (`osgrep --help` and basic command readiness).
- [ ] Check for stale osgrep worker processes and clear them before canary runs.
- [ ] Verify debug wrapper is operational (`python scripts/utils/osgrep_debug_wrapper.py --help`).
- [ ] Capture baseline environment state (repo, cwd behavior, known index state).
- [ ] Dry-run rollback procedure before making enablement changes.

## Phase 1: Re-Enablement Design and Guardrails
- [x] Confirm exact policy language for CLI-only enablement across active guidance.
- [x] Define hard guardrail: MCP/service mode remains disabled for routine use.
- [x] Lock timeout budget at 30 seconds per invocation, then fallback to grep/glob/read.
- [x] Lock rollback trigger threshold at >20% failures/timeouts across 10+ tracked invocations.
- [x] Define staged rollout gates (Planner only -> Build -> all applicable agents).

## Phase 2: Policy and Config Changes
- [x] Update `AGENTS.md` to allow CLI-only osgrep usage and preserve MCP restriction.
- [x] Update agent docs that currently blanket-disable osgrep.
- [x] Update OpenCode config permissions required to allow osgrep usage.
- [x] Ensure custom osgrep tool/skill messaging reflects CLI-only enabled state.
- [x] Update `skill/osgrep/SKILL.md` to match CLI-only enabled policy and MCP restriction.
- [x] Document rollback switch locations (files/keys to flip back).

## Phase 3: Validation Harness Setup
- [x] Create a prompt suite file with fixed test prompts and expected behavior.
- [x] Define evidence capture format (tool call trace, timestamps, pass/fail, notes).
- [x] Define per-test timeout and retry policy.
- [x] Add a run log location under `.conductor/tracks/20260312-osgrep-cli-only-reenable/artifacts/`.
- [x] Add known-answer prompts with expected non-empty target results for anti-silent-failure checks.

## Phase 4: Execute Validation Matrix
- [x] Run core usage prompts (3 semantic scenarios).
- [x] Run reliability prompts (large repo + spaced-path repo).
- [x] Run safety checks (no MCP usage, fallback on forced failure).
- [x] Run concurrency checks (dual query and query-during-index).
- [x] Run stale-index and large-result-set checks.
- [x] Record evidence for each case and summarize pass/fail.

## Phase 5: Go/No-Go Decision
- [ ] Compare results against success criteria.
- [ ] Produce decision note: keep enabled, keep enabled with constraints, or rollback.
- [ ] If rollback needed, execute documented rollback and re-validate fallback behavior.
- [ ] Update troubleshooting current-status doc with final decision and next actions.

## Phase 6: Post-Enable Monitoring and Communications
- [ ] Define short-term monitoring window (1 week) and extended window (1 month).
- [ ] Define reliability watch metrics (timeout count, failure rate, fallback frequency).
- [ ] Record escalation path if reliability degrades.
- [ ] Publish enablement decision and operating constraints to active guidance docs.

## Validation Criteria

The track is complete when:
- 5/5 required CLI-only usage tests pass with explicit osgrep invocation evidence.
- 0 MCP/service-mode invocations appear in validation runs.
- Failure fallback is demonstrated at least once.
- Known-answer test verifies non-empty relevant results at least once.
- Rollback procedure is validated as reversible and low-friction.
