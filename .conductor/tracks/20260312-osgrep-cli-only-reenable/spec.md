# Spec: Osgrep CLI-Only Re-Enablement

**Track ID**: 20260312-osgrep-cli-only-reenable
**Created**: 2026-03-12
**Status**: Active
**Priority**: High

## Problem Statement

Osgrep is currently disabled in OpenCode guidance and config to avoid unreliable behavior tied to MCP/service startup on Windows. The team now wants to re-enable osgrep for normal OpenCode automation, but only through direct CLI-style usage, with explicit validation that agents are actually using it and not silently bypassing it.

## Goal

Re-enable osgrep for OpenCode automation using a strict CLI-only operating mode, validate real usage across representative prompts, and keep a fast rollback path if reliability degrades.

## Definitions

- **CLI-only**: direct osgrep command invocation (for example: `osgrep search`, `osgrep trace`, `osgrep index`) in local process execution flow.
- **MCP/service mode**: `osgrep mcp` server lifecycle path.
- **Fallback path**: `grep` + `glob` + targeted `Read` if osgrep times out or fails.

## Scope

### In Scope
- Re-enable osgrep usage in active OpenCode policy and agent guidance for CLI-only workflows.
- Update OpenCode configuration and permissions required for automated osgrep use.
- Keep MCP/service-mode usage explicitly disabled and out of normal workflows.
- Validate that osgrep is actually invoked by agents in real prompt flows.
- Define canary checks, failure thresholds, and rollback criteria.

### Out of Scope
- Re-enabling `osgrep mcp`.
- Bridge/server orchestration work.
- Upstream osgrep source changes.
- Broad historical documentation cleanup outside active guidance.

## Requirements

1. OpenCode guidance must clearly state: osgrep is allowed for CLI-only search; MCP remains disallowed.
2. Config must permit osgrep where required for agent/tool usage.
3. A validation matrix must prove actual invocation across at least five representative prompts.
4. Validation must include at least one large repo context and one path-with-spaces context.
5. Fallback behavior must be documented for timeout/failure cases (fallback to grep/glob/read).
6. Rollback must be one-step and documented (policy + config switch).
7. Timeout/failure policy must be explicit: 30-second per-invocation timeout, then fallback.
8. Rollback trigger threshold must be explicit: >20% osgrep failure/timeout rate across 10 or more tracked invocations.
9. Re-enable rollout must be staged (Planner -> Build -> all applicable agents) instead of one-shot global enablement.

## Validation Test Cases

### Core Usage Proof
1. **Code-path discovery prompt**: "find code path for auth token refresh"
   - Expected: osgrep invoked before grep/glob fallback.
2. **Cross-file impact prompt**: "find where feature flag X is read and written"
   - Expected: osgrep invoked and results referenced.
3. **Refactor-scoping prompt**: "locate all call sites of function Y and related interfaces"
   - Expected: osgrep invoked with semantic intent.

### Reliability/Edge Coverage
4. **Large repo prompt**: semantic query in `C:\development\opencode`.
   - Expected: osgrep completes within defined timeout budget.
5. **Spaced-path prompt**: semantic query in a path containing spaces.
   - Expected: osgrep executes without path parsing regressions.

### Safety Checks
6. **MCP guardrail check**
   - Expected: no `osgrep mcp` invocation in normal automation path.
7. **Failure fallback check**
   - Expected: on forced osgrep failure, flow continues via grep/glob/read with explicit note.

### Concurrency and Data-State Checks
8. **Concurrent queries check**
   - Expected: two semantic queries can execute in one session without hang.
9. **Query-during-index check**
   - Expected: query behavior remains stable while index activity exists.
10. **Known-answer check**
   - Expected: prompt with known repo answer returns non-empty, relevant results.
11. **Stale-index check**
   - Expected: query against stale index either succeeds or degrades cleanly with explicit fallback.
12. **Large-result-set check**
   - Expected: query returning broad match scope completes within timeout budget.

## Success Criteria

1. Active docs/config are aligned to CLI-only enablement.
2. Validation evidence shows osgrep invoked in at least 5/5 core prompts.
3. No MCP/service-mode use appears in validation evidence.
4. Failure fallback and rollback procedures are documented and tested once.
5. A short decision note records go/no-go with evidence links.
6. Staged rollout gates are completed in order with no blocking reliability regressions.

## Dependencies

- `.conductor/tracks/20260311-osgrep-disable-and-root-cause/spec.md`
- `.conductor/tracks/20260311-osgrep-disable-and-root-cause/plan.md`
- `docs/troubleshooting/active/osgrep-intermittent-hang-disablement-2026-03-11.md`
- `docs/troubleshooting/active/osgrep-cli-only-re-enable-checklist.md`

## Risks

1. Prompt-routing may still favor grep/glob despite osgrep being enabled.
2. Intermittent hangs may reappear under normal agent automation load.
3. Policy drift across docs/config may produce inconsistent behavior.

## Recommendation

Run this as a controlled re-enable canary track (not an in-place edit of the old disablement track), so we keep a clean before/after audit trail, explicit pass/fail criteria, and a reversible rollout.
