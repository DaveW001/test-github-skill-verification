# Spec: Disable Osgrep and Find Root Cause

**Track ID**: 20260311-osgrep-disable-and-root-cause
**Created**: 2026-03-11
**Status**: Active
**Priority**: High

## Problem Statement

Osgrep is intermittently hanging across sessions. The failure pattern is frequent enough that it is no longer safe to keep recommending or invoking it by default. Existing historical fixes addressed specific integration issues, but the current cross-session hang pattern remains unresolved.

## Goal

Disable routine osgrep usage in OpenCode guidance, document the current failure pattern, and drive a structured root-cause investigation with reproducible evidence.

## Scope

### In Scope
- Disable osgrep-first guidance in active OpenCode instructions and agent docs.
- Document the current symptom pattern, known prior issues, and likely hypotheses.
- Define an investigation plan covering logging, reproduction, and isolation.
- Gather current external research relevant to Windows Node/MCP hang behavior.
- Resolve post-build consistency issues tied to osgrep disablement, standards portability, and validation quality.

### Out of Scope
- Patching osgrep source in this track.
- Re-enabling osgrep before a repeatable fix is identified and verified.
- Broad documentation cleanup of historical archives and backups.

## Requirements

1. Default agent behavior must stop recommending osgrep.
2. A troubleshooting note must capture the current disablement decision and investigation path.
3. The investigation plan must include concrete logging and reproduction steps.
4. The track must reference prior local osgrep incidents so the work does not restart from zero.
5. Post-build issues must be tracked with explicit severity and fix actions.

## Success Criteria

1. Active guidance no longer instructs agents to use osgrep by default.
2. A current troubleshooting note exists with hypotheses and logging strategy.
3. A conductor track exists with actionable phases and validation criteria.
4. The next debugging session can collect evidence instead of starting with guesswork.
5. Post-build issues are captured in a single backlog with actionable remediation tasks.

## Risks

1. The hang remains intermittent and difficult to reproduce on demand.
2. Multiple overlapping failure modes exist (CLI, MCP, path handling, DB locking, worker lifecycle).
3. Prior historical assumptions may bias the investigation toward the wrong subsystem.

## Dependencies

- `docs/troubleshooting/active/osgrep-desktop-hang-2026-03-09.md`
- `docs/troubleshooting/active/osgrep-unwanted-folder-creation-SUMMARY.md`
- `docs/reference/osgrep-configuration.md`

## Recommendation

Treat this as an observability and controlled-reproduction problem first. Add logging at the process, filesystem, and invocation boundary before attempting any more architecture changes.
