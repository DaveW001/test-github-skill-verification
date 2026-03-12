# Spec: Disable Osgrep and Find Root Cause

**Track ID**: 20260311-osgrep-disable-and-root-cause
**Created**: 2026-03-11
**Status**: Active
**Priority**: High

## Problem Statement

OpenCode-side osgrep usage has been unreliable enough that it is no longer safe to keep recommending or invoking it by default. Earlier discussion blurred together standalone CLI behavior and MCP/integration behavior. Current evidence suggests the strongest reproducible issue is MCP/service-mode startup, while direct CLI commands look healthier.

## Goal

Disable routine osgrep usage in OpenCode guidance, document what actually happened, preserve the investigation trail, and define a safer CLI-only next step if osgrep is retried later.

## Scope

### In Scope
- Disable osgrep-first guidance in active OpenCode instructions and agent docs.
- Document the current symptom pattern, known prior issues, and likely hypotheses.
- Define an investigation plan covering logging, reproduction, and isolation.
- Gather current external research relevant to Windows Node/MCP hang behavior.
- Resolve post-build consistency issues tied to osgrep disablement, standards portability, and validation quality.
- Clarify that MCP is not required for normal osgrep usage and should not be assumed as the default future path.

### Out of Scope
- Patching osgrep source in this track.
- Re-enabling osgrep before a repeatable fix is identified and verified.
- Broad documentation cleanup of historical archives and backups.

## Requirements

1. Default agent behavior must stop recommending osgrep.
2. A troubleshooting note must capture the current disablement decision, what was tried, and what was learned.
3. The investigation plan must include concrete logging and reproduction steps.
4. The track must reference prior local osgrep incidents so the work does not restart from zero.
5. Post-build issues must be tracked with explicit severity and fix actions.
6. The docs must clearly separate CLI usage from MCP/integration behavior.

## Success Criteria

1. Active guidance no longer instructs agents to use osgrep by default.
2. A current troubleshooting note exists with hypotheses, logging strategy, and a CLI-only next-step plan.
3. A conductor track exists with actionable phases and validation criteria.
4. The next debugging session can collect evidence instead of starting with guesswork.
5. Post-build issues are captured in a single backlog with actionable remediation tasks.
6. Related docs point to one central current-status document.

## Post-Build Fix Completion (2026-03-12)

- Completed policy-alignment updates so active guidance remains disabled-by-default for osgrep usage.
- Completed portability updates by replacing hardcoded local prompt-pattern paths with repo-relative paths in global standards docs.
- Completed validator hardening by adding `scripts/validate-prompt-patterns.py` quality checks for variables, section completeness, and title/filename consistency.
- Completed trigger-ambiguity tightening by changing overlap phrases to `find code path for` (osgrep) and `find web sources for` (perplexity-search).

## Phase 4/5 Completion (2026-03-12)

- Completed stale-worker cleanup, invalid-cwd, and spaced-path CLI regression checks with wrapper logs under `logs/osgrep-debug/`.
- Recorded antivirus exclusion visibility constraint in non-admin shell; retained as environmental note, not a blocker to CLI evidence.
- Narrowed primary failure mode to MCP/service startup lifecycle behavior on Windows while CLI runs remained successful in controlled tests.
- Added local fix-path artifacts (`scripts/utils/osgrep_debug_wrapper.py` and `scripts/utils/osgrep_process_snapshot.ps1`) and documented upstream issue expectations in the Phase 4/5 results file.

## Risks

1. The hang remains intermittent and difficult to reproduce on demand.
2. Multiple overlapping failure modes may still exist, even if MCP is currently the strongest suspect.
3. Prior historical assumptions may bias the investigation toward the wrong subsystem.

## Dependencies

- `docs/troubleshooting/active/osgrep-unwanted-folder-creation-SUMMARY.md`
- `docs/reference/osgrep-configuration.md`
- `docs/troubleshooting/active/osgrep-intermittent-hang-disablement-2026-03-11.md`

## Recommendation

Treat this as an observability and controlled-reproduction problem first. Preserve the current disablement, keep the docs aligned around one current-status record, and if osgrep is retried later, start with CLI-only experiments before revisiting MCP or bridge ideas.
