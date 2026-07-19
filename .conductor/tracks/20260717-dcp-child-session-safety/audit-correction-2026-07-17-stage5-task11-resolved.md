# Audit Correction - Task 1.1 Blocker Resolved (Stage 5)

**Track ID:** 20260717-dcp-child-session-safety
**Date:** 2026-07-17 (Stage 5 resume)
**Supersedes:** "Blocker 1" in `execution-log-2026-07-17.md` (initial Stage 5 child) which flagged the original Task 1.1 test as unsatisfiable.

## Resolution

The prior blocker arose because the ORIGINAL Task 1.1 test hardcoded a `compress:deny` rule in-test and asserted it absent. That test has been replaced via a behavior-preserving testability refactor plus a corrected adversarial test:

1. **Production helper extracted (behavior-preserving refactor).** `C:\development\opencode-core-dcp-fix\packages\opencode\src\agent\subagent-permissions.ts` now exports `buildChildSessionPermission(...)`. `src/tool/task.ts` calls it (call site at lines 139-144) and the legacy buggy behavior (blanket-deny of every `experimental.primary_tools` entry, including `compress`) was preserved verbatim through the extraction.
2. **Corrected adversarial test.** `packages/opencode/test/agent/child-compression-eligibility.test.ts` imports `buildChildSessionPermission` directly and exercises the REAL production helper (no in-test logic duplication). The default-eligibility case is the single valid RED pending the Task 2.1 policy change.

## Orchestrator independent verification (pre-Stage-5)

- Targeted Task 1.1 suite: **5 pass / 1 expected failure only** (valid RED).
- `test/tool/task.test.ts` + `test/agent/plan-mode-subagent-bypass.test.ts`: **25 pass / 0 fail**.
- `bun run typecheck`: **exit 0** (opencode package).

## Stage 5 (this child) GREEN result for Task 1.1 / Task 2.1

After implementing Task 2.1 (gate the primary-tools blanket-deny behind opt-in `forceChildToolDeny`, default false = eligible; preserve explicit parent/subagent denies as hard ceilings):

- `test/agent/child-compression-eligibility.test.ts`: **6 pass / 0 fail**.
- `test/agent/child-compression-compatibility.test.ts` (additive, Task 2.2): **3 pass / 0 fail** (proves eligible, explicit-deny, and compatibility-deny).
- `test/tool/task.test.ts` + `test/agent/plan-mode-subagent-bypass.test.ts`: **25 pass / 0 fail** (no regression; the one task.test.ts assertion that encoded the old bug was updated to the new eligible policy).
- opencode package `bun run typecheck`: **exit 0**.

## Note on enterprise typecheck

`bun run typecheck` at the repo root reports a failure in `@opencode-ai/enterprise` (`src/custom-elements.d.ts` TS1128). This is **pre-existing and unrelated** to this track's edits (which are confined to `packages/opencode/src/agent` and `packages/opencode/src/tool`). The `@opencode-ai/opencode` package typechecks clean (exit 0).

## Verdict

Task 1.1 blocker RESOLVED. Phase 2 (Task 2.1 GREEN) complete and verified. Phase 2 Task 2.2 policy documentation + compatibility validation complete via closest-deterministic checks (schema/config-doc regen of the generated `experimental` type deferred).