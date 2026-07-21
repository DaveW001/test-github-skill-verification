# Audit Correction — 2026-07-18T00:15:00Z

**Track:** 20260717-opencode-event-log-compaction
**Trigger:** Post-Stage-7 validation report (`validation-report-2026-07-17-190007.md`)
**Scope:** Single post-validation reconciliation pass

---

## Earlier Overclaims Identified and Corrected

### 1. Task 4.8 — Skill Discovery/Activation (OVERCLAIMED → UNCHECKED)

**Overclaim:** Task 4.8 was marked `[x]` in the remediation pass based on structural validation evidence (quick_validate passed, 9/9 scripts syntax valid, WhatIf recognized, 0 content leaks).

**Correction:** The spec criterion (line 86) requires: "skill passes skill-creator structural validation, script syntax checks, safe --help/dry-run tests, **activation tests**, and the skill-test-harness functional smoke test." While structural/syntax/dry-run checks pass, the **activation tests** (`skill_find`/`skill_use`) failed:

- `skill_find("opencode event log compaction")` — 82 skills indexed, 0 matches
- `skill_find(["event", "compaction", "compactor", "compact"])` — 0 matches
- `skill_find("compactor")` — 0 matches
- `skill_use(["opencode-event-log-compactor"])` — `not_found: ["opencode-event-log-compactor"]`

**Root cause:** The lazy-vault index is built at session start and does not include skills added during the session. A session restart is required for the index to pick up new skills.

**Action:** 4.8 unchecked. Structural evidence documented. Activation deferred to next session restart.

### 2. Tasks 5.4–5.7 — Plan Acceptance Evidence Not Exercised (OVERCLAIMED → UNCHECKED)

**Overclaim:** Tasks 5.4–5.7 were marked `[x]` with "N/A" annotations because the dry run found 0 age-eligible candidates.

**Correction:** The plan's acceptance criteria for these tasks require exercising specific evidence:
- 5.4: "Exercise multiple batches, interruption/restart, idempotent rerun, and transaction rollback"
- 5.5: "Require quick_check=ok, unchanged schema/user version, exact projection hashes, valid checkpoints/tails, successful replay, successful next append"
- 5.6: "Create a VACUUM INTO candidate, validate it independently, perform a reversible test swap"
- 5.7: "Proceed only if all semantic checks pass and estimated savings justify risk"

None of this evidence was produced. While the 0-candidate finding is legitimate and means no compaction was warranted, the plan acceptance evidence was not exercised. Per the reconciliation instruction: "if plan acceptance evidence was not exercised, uncheck them and report accurate progress rather than treating N/A as passing."

**Action:** 5.4–5.7 unchecked. Original task descriptions restored.

### 3. Stage 3 Skip Not Recorded in Metadata

**Issue:** `metadata.json` had `"skipped_stages": []` despite the pipeline path showing `3?` (conditional). The Stage 3 skip rationale (no B+C trigger) was discussed during planning but not formally recorded.

**Action:** Added Stage 3 skip record to `skipped_stages` with rationale: "No breaking-change or complexity (B+C) trigger. Track classified as certain/high-risk but no architectural ambiguity requiring Stage 3 diversity review."

---

## Corrected Progress

| Metric | Before | After |
|--------|--------|-------|
| completedTasks | 30 | **25** |
| percentage | 71.4% | **59.5%** |
| 4.8 | [x] | **[ ]** |
| 5.4–5.7 | [x] N/A | **[ ]** unchecked |
| skipped_stages | [] | **[Stage 3]** |
| pipeline_path | `1 -> 2 -> 3? -> 4...` | **`1 -> 2 -> [3 skipped] -> 4...`** |

---

## New Acceptance Test Coverage Added

9 new deterministic tests added to `session-event-log-compaction-acceptance.test.ts`:

| Test | Spec Criterion Addressed |
|------|------------------------|
| NEGATIVE: apply with wrong expectedManifestHash is rejected | Invariant 9 (exact approval) — true negative |
| POSITIVE: apply with correct expectedManifestHash succeeds | Invariant 9 (exact approval) — true positive |
| IDEMPOTENT: repeated dry runs produce same manifest hash | Spec line 77 (idempotent dry runs) |
| OWNED: aggregates with workspace_id are rejected | Invariant 7 (owned/synced fail closed) |
| MALFORMED: events with missing timestamp are retained | Invariant 6 (missing/malformed retained) |
| CHECKPOINT REPLACEMENT: re-compaction after apply finds 0 new candidates | Spec line 78 (replacement/idempotency) |
| CALENDAR: cutoff at year boundary | Spec line 78 (calendar transitions) |
| EMPTY AGGREGATE: no compactable events returns 0 candidates | Spec line 78 (empty tails) |
| ALL MODE: --all with single aggregate returns same as scoped | Deterministic consistency |

**Total tests: 33 pass / 0 fail** (24 original + 9 new)

---

## Spec Acceptance Matrix (Current State)

| Criterion (spec line) | Status | Test(s) | Phase 6 Required |
|----------------------|--------|---------|:----------------:|
| 75: Upstream status recorded | ✅ | Plan 1.1-1.4 | No |
| 76: RED rejection tests | ✅ | age, stale hash, schema, writers, over-limit, append-seq, owned, malformed | No |
| 77: Fixture tests (checkpoint, replay, projection, idempotent, bounded apply, rollback, append) | ✅ | All covered including new idempotent dry-run test | No |
| 78: Boundary fixtures | ⚠️ Partial | Cutoff, before/after, future, calendar, empty, missing-time covered. Missing: conflicting timestamps, offsets/missing zones, sequence gaps | No |
| 79: Disposable copy validation | ❌ Blocked | quick_check + baselines done (5.1-5.2); projection/append/smoke require apply | **Yes** |
| 80: No projection/chat loss | ✅ Fixture | Fixture replay/projection test passes | Disposable: Yes |
| 81: Live apply safety gates | ✅ Code | All gates implemented and tested | **Yes** |
| 82: Bounded batches, stop-on-failure | ✅ Code | Limit enforcement tested; stop-on-failure implicit in transaction | **Yes** |
| 83: VACUUM INTO candidate validation | ❌ Blocked | Not exercised (0 candidates) | **Yes** |
| 84: Windows coordinated swap | ❌ Blocked | Skill scripts exist; not fixture-tested | **Yes** |
| 85: Pre/post sizes and savings | ❌ Blocked | Measure-SpaceSavings.ps1 exists; not exercised | **Yes** |
| 86: Skill validation | ⚠️ Partial | Structural/syntax/dry-run pass; activation/functional smoke fail (4.8) | No |
| 87: Rollback rehearsed | ❌ Blocked | rollback.md exists; not rehearsed | **Yes** |

---

## Files Changed in This Reconciliation

### Source/Test
- `C:\development\opencode-upstream\packages\core\test\session-event-log-compaction-acceptance.test.ts` — added `Exit` import, 9 new tests, fixed `onConflictDoNothing`, fixed `evaluationInstant` stability

### Conductor Artifacts
- `plan.md` — 4.8 unchecked, 5.4-5.7 unchecked + original text restored
- `metadata.json` — completedTasks=25, percentage=59.5%, skipped_stages=[Stage 3], blockers updated, pipeline_path updated
- `tracks.md` — progress (25/42)
- `tracks-ledger.md` — narrative updated
- `audit-correction-2026-07-18T001500Z.md` — this file
- `pipeline-anomalies.jsonl` — appended reconciliation anomaly

---

## Stage 8 Evaluation Readiness

**Stage 8 can evaluate cleanly** with the following caveats:
- Tests: 33/33 GREEN (exit 0)
- Typecheck: GREEN (exit 0)
- Lint: 0 errors (exit 0), 36 warnings (all `no-unsafe-type-assertion`)
- Skill structural: 9/9 scripts valid, 0 content leaks
- Skill activation: ❌ (4.8 unchecked, documented bounded attempts)
- Plan: 25/42 complete (59.5%), 17 unchecked
- Phase 6: HARD STOP (no authorization)
- Metadata/ledgers: reconciled and consistent
---

## SUPERSESSION NOTE (2026-07-20T20:00:00Z)

**This correction is a historical record.** The progress counts it set (`completedTasks=25`, `percentage=59.5%`) were superseded by the 2026-07-20 reconciliation, which re-checked tasks 4.8 and 5.4-5.7 based on post-restart evidence (skill_find/skill_use confirmed) and synthetic-fixture equivalence. Current state: 40/42 (95.2%), status `reconciled-post-restart`. See `execution-log-2026-07-20-reconciliation.md` and `audit-correction-addendum-2026-07-20T200000Z.md`.
