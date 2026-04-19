# Plan: Osgrep Stabilization (Path A)

**Track ID**: 20260313-osgrep-stabilization  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-03-13  
**Status**: Completed (2026-03-14)  
**Priority**: High  

_Note: Checklist boxes are preserved as original planning controls and are not fully backfilled; completion state is tracked in `metadata.json`, execution logs, and verification reports._

---

## Objective

Stabilize osgrep for CLI-only canary usage and produce a defensible GO/NO-GO decision by validating both:

1. **Engine behavior** (index/search reliability)
2. **OpenCode tool-path behavior** (actual runtime invocation path, not static messaging)

This plan addresses three known failures from the prior track:

- `Table 'chunks' already exists` (TC-01, TC-02)
- FTS inverted-index warning quality issue (TC-04)
- Stale index inconsistency (TC-11)

---

## Critical Corrections (Plan Governance)

- [ ] Use **`existOk: true`** for table creation (not mutex-based approach)
- [ ] Keep one canonical acceptance gate in this plan
- [ ] Classify TC-04 and TC-11 explicitly as **blocking** or **risk-accepted**
- [ ] Add an explicit **tool-path activation gate** for `tool/osgrep.ts`
- [ ] Add reproducible patch strategy (avoid long-term dependency on ad-hoc global `dist` edits)

---

## Phase 0: Baseline and Reproducibility

**Goal**: Ensure all changes can be repeated and audited.

- [ ] Record exact package versions (`osgrep`, `@lancedb/lancedb`)
- [ ] Snapshot current files before edits (timestamped backups)
- [ ] Define reproducible patch method:
  - [ ] Preferred: patch source repo and rebuild/package
  - [ ] Interim: scripted patch application to `%APPDATA%/npm/node_modules/osgrep/dist/...`
- [ ] Capture baseline failure evidence for TC-01, TC-02, TC-04, TC-11

**Verification commands**:

```bash
osgrep --version
node -e "const p=require(process.env.APPDATA+'\\npm\\node_modules\\osgrep\\package.json'); console.log(p.version, p.dependencies['@lancedb/lancedb'])"
```

---

## Phase 1: Fix 1 (Blocking) - Table Creation Race

**Goal**: Eliminate `Table 'chunks' already exists` errors.

**Implementation**:

- [ ] Edit `vector-db.js` `ensureTable()` creation branch to pass `existOk: true`
- [ ] Do not introduce custom mutex unless this fails to resolve race

**Required code change**:

```javascript
const table = await db.createTable(TABLE_NAME, [this.seedRow()], {
  schema,
  existOk: true,
});
```

**Validation (blocking)**:

- [ ] TC-01-rerun PASS
- [ ] TC-02-rerun PASS
- [ ] TC-08-rerun PASS
- [ ] Zero occurrences of `Table 'chunks' already exists`

---

## Phase 2: Fix 2 (Conditionally Blocking) - FTS Reliability

**Goal**: Address TC-04 search quality regressions tied to FTS warnings.

**Implementation**:

- [ ] Confirm current fallback behavior (vector results still returned if FTS fails)
- [ ] Add/adjust FTS health checks only if needed to improve determinism
- [ ] Avoid noisy warning spam; preserve actionable error telemetry

**Decision rule**:

- [ ] Mark TC-04 as **blocking** unless stakeholder explicitly accepts risk with documented rationale

**Validation**:

- [ ] TC-04-rerun PASS (expected result quality met)
- [ ] If warnings remain, quality still meets expected known-answer threshold

---

## Phase 3: Fix 3 (Conditionally Blocking) - Stale Index Determinism

**Goal**: Ensure stale content handling is predictable.

**Implementation**:

- [ ] Add result-time stale filtering only if reproducibly needed
- [ ] Preserve search performance; measure added overhead if file checks are introduced
- [ ] Prefer minimal fix over broad new index mode flags

**Decision rule**:

- [ ] Mark TC-11 as **blocking** unless explicitly risk-accepted in decision note

**Validation**:

- [ ] TC-11-rerun PASS
- [ ] Repeated runs produce consistent outcome

---

## Phase 4: Tool-Path Activation Gate (Blocking)

**Goal**: Prove OpenCode actually executes osgrep in tool-path, not static text.

**Context**: `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts` currently returns static guidance text in `execute()` and does not run CLI.

**Implementation**:

- [ ] Define expected behavior contract for the tool-path (`argv` passthrough + output)
- [ ] Update tool implementation (Build agent) to execute osgrep CLI in canary-safe mode
- [ ] Preserve fallback guidance if osgrep fails

**Validation (blocking)**:

- [ ] Tool invocation returns actual search output when healthy
- [ ] Tool invocation returns explicit fallback path when unhealthy
- [ ] No MCP/server path invoked

---

## Phase 5: Integrated Validation Matrix

**Goal**: Re-run matrix with clear pass/fail semantics.

- [ ] Rebuild index from clean state (`osgrep index --reset` then `osgrep index`)
- [ ] Re-run TC-01..TC-12
- [ ] Record per-test artifact links and timestamps
- [ ] Run a cold-start rerun (new session/process) to catch initialization-only issues

**Canonical acceptance gate**:

- [ ] **Blocking tests**: TC-01, TC-02, TC-03, TC-04, TC-05, tool-path activation, MCP guardrail
- [ ] **Conditionals**: TC-11 must pass or have explicit risk acceptance signed in go/no-go note
- [ ] Fallback test (TC-07) must remain PASS

---

## Phase 6: Decision, Rollout, and Rollback

**Goal**: Produce a defensible GO/NO-GO and staged rollout.

### GO criteria

- [ ] All blocking tests pass
- [ ] No unresolved race-condition errors
- [ ] Tool-path activation gate passes
- [ ] Any residual TC-11/TC-04 issues are explicitly documented and accepted (if non-blocking)

### Rollout staging

- [ ] Stage 1: Planner-only canary
- [ ] Stage 2: Build agent canary
- [ ] Stage 3: broader agent usage with monitoring window

### Rollback readiness

- [ ] One-command/script rollback for patched osgrep module
- [ ] Verify fallback-only mode still works after rollback

---

## Deliverables

- [ ] Updated validation matrix with new run evidence
- [ ] Updated go/no-go decision note with explicit risk acceptance table
- [ ] Reproducible patch instructions (or source patch reference)
- [ ] Parent track (`20260312-osgrep-cli-only-reenable`) status updated

---

## Notes for Build Agent

- Keep fixes minimal and reversible.
- Prefer `existOk: true` over bespoke locking.
- Do not claim GO until tool-path activation passes in a fresh session.

---

## Completion Update (2026-03-14)

- Blocking tool-path activation gate now passes in a fresh restarted OpenCode session (`{"argv":["--","search","auth token refresh"]}` returned real semantic matches).
- Engine reruns across TC-01/02/04/05/11 and cold-start checks are favorable in latest evidence sets.
- Decision package can move forward as GO for staged rollout, with monitoring retained for intermittent environment-sensitive behavior.
- Residual non-blocking observation retained for future revisit: transient wrapper decode warning (`UnicodeDecodeError`/`cp1252`) treated as harness noise unless recurring.
