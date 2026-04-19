# Spec: Osgrep Stabilization (Path A)

**Track ID**: 20260313-osgrep-stabilization  
**Created**: 2026-03-13  
**Updated**: 2026-03-14  
**Parent Track**: 20260312-osgrep-cli-only-reenable  
**Status**: Completed (Staged GO Recommended)  
**Priority**: High  
**Owner**: 01-Planner / Build

---

## Problem Statement

Prior canary validation for CLI-only osgrep re-enable failed gate tests with three reliability signals:

1. `Table 'chunks' already exists` (TC-01, TC-02)
2. FTS warning / quality degradation risk on large-repo queries (TC-04)
3. Stale-index inconsistency risk (TC-11)

A separate but critical gap also exists:

4. OpenCode osgrep tool-path currently returns static text and does not execute osgrep CLI in `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts`.

The objective is a defensible GO/NO-GO decision based on both engine behavior and tool-path behavior.

---

## Current Evidence (Updated)

Phase 0 baseline reruns executed on 2026-03-14:

- `TC-01` rerun (`tc01-pre-fix-20260313`) exited `0` with results and no `chunks` error.
- `TC-04` rerun (`tc04-pre-fix-20260313`) exited `0` with results and no FTS warning in stderr.

This indicates failures may be intermittent and environment-sensitive, not continuously reproducible.

Artifacts:

- `C:\development\opencode\logs\osgrep-debug\20260313-202047-tc01-pre-fix-20260313\result.json`
- `C:\development\opencode\logs\osgrep-debug\20260313-202059-tc04-pre-fix-20260313\result.json`

Finalization evidence on 2026-03-14 (fresh-session restart gate):

- Tool-path activation check with `{"argv":["--","search","auth token refresh"]}` returned real semantic results (not static guidance).
- Additional rerun evidence captured in:
  - `C:\development\opencode\logs\osgrep-debug\20260314-140738-tc03-rerun-20260314-final\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260314-140738-tc07-rerun-20260314-final\result.json`

---

## Root Cause Hypotheses

### H1: Table creation race (intermittent)

`ensureTable()` performs `openTable` then `createTable` in a catch branch. Concurrent callers can enter creation paths near-simultaneously.

### H2: FTS reliability variability

FTS may intermittently fail or degrade relevance on large repos; current code catches FTS failure and continues with vector results.

### H3: Stale index visibility lag

Stale entries are cleaned during sync lifecycle; transient mismatch windows can expose stale results depending on timing.

### H4: Tool-path disconnect

OpenCode tool implementation advertises osgrep but currently emits guidance text only, so enabling policy may not mean actual tool execution.

---

## Proposed Remediations

### R1 (Blocking): Idempotent table creation

In osgrep `vector-db.js`, set `existOk: true` in `createTable(...)` options.

Rationale:

- LanceDB `@lancedb/lancedb@^0.22.3` supports `existOk` -> `exist_ok` mode.
- Minimal reversible change.

### R2 (Conditionally Blocking): FTS quality guardrails

- Keep vector fallback behavior when FTS fails.
- Add deterministic quality checks against known-answer prompts.
- Avoid noisy warnings while preserving actionable diagnostics.

### R3 (Conditionally Blocking): Stale-result handling

- Add targeted stale filtering only if reproducibly needed.
- Prefer minimal performance impact.

### R4 (Blocking): Tool-path activation

- Update OpenCode osgrep tool contract so tool invocation executes CLI and returns real results.
- Preserve MCP prohibition and fallback path requirements.

---

## Blocking vs Conditional Criteria

**Blocking for GO**:

- Tool-path activation passes.
- TC-01..TC-05 pass.
- MCP guardrail test remains pass.
- No unresolved `Table 'chunks' already exists` recurrence during gate run.

**Conditional / risk-accepted**:

- TC-11 and residual TC-04 concerns may be accepted only with explicit decision note entries:
  - risk description
  - user impact
  - mitigation/fallback
  - owner and re-evaluation date

---

## Reproducibility Requirements

Do not rely long-term on ad-hoc edits in global `%APPDATA%` package directories without reproducible patch path.

Minimum reproducibility package:

1. Exact versions recorded (`osgrep`, `@lancedb/lancedb`).
2. Timestamped backups before local edits.
3. Scripted patch and rollback steps.
4. Preferred follow-up path: source-level fix + rebuild/package/publish workflow.

---

## Validation Requirements

Required validation for decision package:

1. Core matrix rerun (`TC-01..TC-12`) with timestamps and artifact links.
2. Cold-start rerun (fresh process/session) for initialization sensitivity.
3. Tool-path invocation proof (actual CLI output via tool).
4. Explicit fallback proof (forced failure -> grep/glob/read path).

---

## Decision Output Requirements

Final go/no-go must include:

- Pass/fail table for blocking criteria.
- Risk acceptance table for conditional criteria.
- Rollback trigger threshold and command path.
- Staged rollout plan (Planner -> Build -> broader agents).

---

## Notes

- This track remains planner-owned for architecture/documentation.
- Production code changes are implementation work for Build agent.
- As of 2026-03-14, blocking criteria are met and this track is ready to close with staged rollout and monitoring.
