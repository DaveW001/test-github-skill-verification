# Audit Correction — Invalid RED Classification

**Track ID:** 20260717-dcp-child-session-safety  
**Timestamp:** 20260717-195550  
**Stage:** 4 (RED — Test Writing)  
**Correction Type:** Invalid RED classification audit mismatch  

---

## Original Report Issue

**Initial Report:** `red-gate-report-20260717-194505.md`  
**Issue:** Classified module-not-found failures as valid RED.  
**Pipeline Policy Violation:** 
> "Valid RED must be expected behavioral/assertion failures only; syntax, dependency, discovery, harness, unrelated baseline, or setup failures are invalid RED."

Module-not-found errors are dependency/setup failures, not behavioral assertion failures.

---

## Correction Actions

1. **Rewrote all DCP tests** to use existing modules and assert behavioral gaps:
   - `session-state-registry.test.ts` — Tests existing state/persistence modules, asserts missing registry/revision/atomic-write/schema-versioning
   - `context-limit-enforcement.test.ts` — Tests existing config/state/logger, asserts missing enforcement/handoff/reentrancy/telemetry/transactional features
   - `active-model-limits.test.ts` — Tests existing config, asserts missing model keys in modelMaxLimits
   - `telemetry-events.test.ts` — Tests existing logger, asserts missing telemetry emission/redaction/event-types

2. **Preserved valid behavioral failures:**
   - OpenCode core Task 1.1 test (compress deny behavioral assertion) — unchanged
   - Conductor guardrail Task 1.5 test (MISSING_GUARDRAIL behavioral output) — unchanged

3. **Verified all tests load and execute successfully:**
   - No module-not-found errors
   - No syntax errors
   - No dependency failures
   - All failures are behavioral assertion failures

---

## Repair Pass Results

| Suite | Tests | Pass | Fail | RED Valid? |
|-------|-------|------|------|------------|
| OpenCode core (Task 1.1) | 5 | 4 | 1 | YES |
| DCP session-state-registry (Task 1.2) | 5 | 0 | 5 | YES |
| DCP context-limit-enforcement (Task 1.3) | 10 | 0 | 10 | YES |
| DCP active-model-limits (Task 1.4a) | 5 | 0 | 5 | YES |
| DCP telemetry-events (Task 1.4b) | 6 | 0 | 6 | YES |
| Conductor guardrail (Task 1.5) | 1 mode | — | — | YES |
| **TOTAL** | | **4** | **27** | |

---

## Lessons Learned

1. **Module-not-found is NOT valid RED** — It's a setup/dependency failure
2. **Behavioral assertions must test existing code** — Assert that behavior SHOULD be different, not that modules SHOULD exist
3. **Tests must load and execute successfully** — No import errors, no syntax errors
4. **Failures must be assertion failures** — `assert.ok()`, `assert.equal()`, `expect().toBe()` that fail because expected behavior is missing

---

## Superseded Reports

- **Superseded:** `red-gate-report-20260717-194505.md` (invalid RED classification)
- **Current:** `red-gate-report-20260717-195524.md` (valid behavioral RED)

---

## Orchestrator Action Required

**None.** Repair pass completed successfully. All tests now demonstrate valid behavioral RED.
