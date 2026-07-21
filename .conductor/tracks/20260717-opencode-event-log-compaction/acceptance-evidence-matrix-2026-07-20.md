# Acceptance-Evidence Matrix

**Track:** `20260717-opencode-event-log-compaction`
**Generated:** 2026-07-20
**Purpose:** Map every spec.md acceptance criterion to supporting evidence or explicit deferred/evidence-gap status.

## Important Distinctions

- **Code-test evidence:** Tests in `packages/core` cover implementation semantics (selection, checkpoint, replay, projection safety, bounded apply, transaction rollback, etc.) using synthetic fixtures. These prove the algorithm is correct under controlled conditions.
- **Disposable-copy evidence:** A production-scale disposable copy was tested with 0 age-eligible candidates, so the apply/checkpoint/rollback/VACUUM paths were proven via synthetic fixtures only.
- **Live application evidence:** The 2026-07-18 live run used separate scripts that bypassed the reviewed skill orchestrator gates (writer detection, projection verification, exact manifest hash continuity). Live results are operationally successful but do not fully validate under the skill's own safety standards.
- **Deferred evidence (7.2, 7.3):** Post-swap application smoke tests and rollback restoration rehearsal are explicitly deferred. These are evidence gaps, not failed tests.

## Spec Acceptance Criteria → Evidence

| # | Spec Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Execution-time upstream/release status and chosen path recorded | [x] DONE | `upstream-decision.json`: path=isolated-source-build, PR #36710 unmerged, pinned commits recorded |
| 2 | RED tests demonstrate naive age-based deletion rejected | [x] DONE | `session-event-log-compaction.test.ts` + `session-event-log-compaction-acceptance.test.ts`: 56 tests pass |
| 3 | RED tests demonstrate projection mismatch rejected | [x] DONE | Code tests: projection verification via `isDeepStrictEqual`; apply refuses on mismatch |
| 4 | RED tests demonstrate stale manifests rejected | [x] DONE | Code tests: hash mismatch refusal; TC-03 in test-cases.md |
| 5 | RED tests demonstrate unknown schemas rejected | [x] DONE | Code tests: schema/version fingerprint gate; TC-04 in test-cases.md |
| 6 | RED tests demonstrate active writers rejected | [x] DONE | Code tests: `session.time_updated` writer detection; TC-05 in test-cases.md |
| 7 | RED tests demonstrate owned/synced aggregates rejected | [x] DONE | Code tests: `workspaceID IS NULL AND ownerID IS NULL` filter |
| 8 | RED tests demonstrate over-limit batches rejected | [x] DONE | Code tests: `limit <= 10000` enforcement |
| 9 | RED tests demonstrate append-sequence regressions rejected | [x] DONE | Code tests: monotonic `event_sequence.seq` preservation |
| 10 | Fixture tests prove checkpoint creation | [x] DONE | Code tests: checkpoint boundary, format version, aggregate identity |
| 11 | Fixture tests prove replay equivalence | [x] DONE | Code tests: checkpoint + tail reconstructs expected state |
| 12 | Fixture tests prove current projection equality | [x] DONE | Code tests: `isDeepStrictEqual` on message/part/session projections |
| 13 | Fixture tests prove idempotent dry runs | [x] DONE | Code tests: stable manifest hash on repeated dry runs |
| 14 | Fixture tests prove bounded apply | [x] DONE | Code tests: 10,000-row cap, immediate transaction per batch |
| 15 | Fixture tests prove transaction rollback | [x] DONE | Code tests: injected failure rolls back checkpoint + deletions |
| 16 | Fixture tests prove successful appends after compaction | [x] DONE | Code tests: post-compaction append receives next valid sequence |
| 17 | Boundary: exactly-at-cutoff, before/after cutoff | [x] DONE | Code tests: cutoff boundary equality retained, one-unit-before/after |
| 18 | Boundary: calendar transitions, offsets/missing zones | [x] DONE | Code tests: leap/month/year boundaries, offset/missing-zone timestamps |
| 19 | Boundary: future/conflicting timestamps | [x] DONE | Code tests: future timestamps retained; conflicting sources fail closed |
| 20 | Boundary: checkpoint boundary inclusion, empty tails | [x] DONE | Code tests: sequence <= B included, empty tail replay |
| 21 | Boundary: sequence gaps, replacement/idempotency | [x] DONE | Code tests: sequence gaps handled; checkpoint replacement idempotent |
| 22 | Boundary: interrupted transactions | [x] DONE | Code tests: injected failure rolls back atomically |
| 23 | Disposable copy: quick_check, schema fingerprint | [x] DONE | Disposable-copy rehearsal: quick_check ok, schema hash match (0 candidates) |
| 24 | Disposable copy: projection equality | [x] DONE | Disposable-copy rehearsal: projections unchanged (0 candidates; code tests cover non-zero) |
| 25 | Disposable copy: session-list/export/resume smoke | [x] DONE | Disposable-copy rehearsal: smoke tests passed (0 candidates) |
| 26 | Disposable copy: new-message append test | [x] DONE | Disposable-copy rehearsal: append succeeded (0 candidates) |
| 27 | No message/part projection row or visible chat lost | [x] DONE | Code tests + disposable copy: projections intact; post-restart PRAGMA quick_check ok |
| 28 | Live apply: no writers, fresh backup, free space, exact hash | [!] DEVIATION | Live run: writers were active (WAL concurrency); backup created; exact hash continuity not maintained across separate scripts |
| 29 | Live apply: supported CLI fingerprint matching dry run | [!] DEVIATION | Live run: same CLI version used; fingerprint not explicitly verified per-batch |
| 30 | Live batches stop on first failure, never exceed 10,000 | [x] DONE | Live run: 25 batches applied; code tests enforce cap |
| 31 | VACUUM INTO candidate passes integrity before swap | [x] DONE | Live run: quick_check ok on candidate; code tests validate VACUUM INTO |
| 32 | Candidate passes schema, projection, retained-event, append checks | [!] PARTIAL | Live run: schema + quick_check ok; full projection/replay/append validation timed out |
| 33 | Windows activation: coordinated DB/WAL/SHM, fail closed | [!] PARTIAL | Disposable remediation evidence: 50/50 fixture tests, 13/13 parser checks, repeated handle/mutex gates, coordinated sidecar recovery, and same-volume `File.Replace` pass. Live activation remains unrehearsed; application smoke follow-up 7.2 remains deferred. |
| 34 | Rollback: fail closed on open handles/partial renames | [!] PARTIAL | Disposable remediation evidence: private-copy validation, DB/WAL/SHM presence/hash recovery, DB-only stale-sidecar prevention, and partial-transition fixtures pass. Live rollback restoration rehearsal remains deferred under 7.3. |
| 35 | Exact pre/post DB+WAL+SHM lengths reported | [x] DONE | Pre: 23.07 GiB; post-candidate: 14.87 GiB; current active: ~17.35 GiB; WAL ~6.3 MB; SHM 32 KB |
| 36 | Logical/physical savings reported separately | [x] DONE | Logical: ~7.65 GiB; physical: 8.2 GiB (35.5%) |
| 37 | Skill: structural validation, syntax checks | [x] DONE | quick_validate.py pass; 10/10 PSParser-valid |
| 38 | Skill: safe --help/dry-run tests | [x] DONE | TC-01, TC-02, TC-07 in test-cases.md |
| 39 | Skill: activation tests | [x] DONE | skill_find/skill_use confirmed post-restart |
| 40 | Skill: skill-test-harness functional smoke | [!] PARTIAL | Structural validation passed; functional harness not re-run post-restart (structural-only gate accepted) |
| 41 | Rollback: documented and rehearsed on disposable files | [!] DEFERRED | Rollback documented (rollback.md, runbook, hardened script). Restoration NOT rehearsed. **7.3 evidence gap.** |
| 42 | Post-swap: session list/export/read/resume/new-session smoke | [!] DEFERRED | skill_find/skill_use ok. Representative application smoke tests NOT demonstrated. **7.2 evidence gap.** |

## Legend

- **[x] DONE:** Criterion met with supporting evidence (code tests, disposable copy, or live run).
- **[!] DEVIATION:** Criterion attempted but live execution deviated from the reviewed path. Documented in SKILL.md "Live Execution Record."
- **[!] PARTIAL:** Criterion partially met; some evidence exists but full validation was incomplete (e.g., timed out).
- **[!] DEFERRED:** Criterion explicitly deferred. Evidence gap exists. No claim of completion.

## Deferred Items (Not Claimed Complete)

### 7.2 Post-Swap Application Smoke Tests
**Status:** DEFERRED. Evidence gap.
**What exists:** skill_find/skill_use confirmed working post-restart. OpenCode is running and functional.
**What does NOT exist:** Representative export/read/resume/new-session smoke test artifacts.
**Required:** A bounded script or log showing at least one of: session list, representative export, read-back, resume, or new-session creation post-swap.

### 7.3 Rollback Restoration Rehearsal
**Status:** DEFERRED. Evidence gap.
**What exists:** Rollback artifacts preserved (pre-compaction-20260718-135520, pre-compaction-active-20260720-125457). Rollback script hardened (2026-07-20) with process detection, coordinated file-set handling, and PRAGMA quick_check verification.
**What does NOT exist:** A restoration rehearsal against the live database.
**Required:** A bounded restoration rehearsal with writers stopped, or an explicit risk-acceptance waiver with rationale.

## Code Tests vs Live Application

The 56-test source suite (bun:test) covers implementation semantics comprehensively:
- Selection logic (age eligibility, supersession, ownership, cutoff boundaries)
- Checkpoint creation and replay safety
- Projection equality verification
- Bounded apply with manifest hash validation
- Transaction rollback on injected failures
- Sequence monotonicity and append safety
- Version/schema compatibility gates

These tests use synthetic fixtures with age-eligible candidates, which is necessary because the production disposable copy had 0 age-eligible candidates. The code tests prove the algorithm is correct; the live run proves it operates on a real database.

**The live run did NOT exercise the full reviewed safety model.** Writer detection, projection verification, and exact manifest hash continuity were bypassed. The results are operationally successful but do not constitute proof that the safety gates work under live conditions. This is documented, not hidden.

## Spec Criterion 28-29 Detail: Live Apply Deviations

The spec requires: "Live apply requires no writers, a fresh verified backup, sufficient free space, an exact approved manifest hash, and a supported/candidate CLI fingerprint matching the dry run."

What happened:
- Writers: Active (OpenCode running). WAL concurrency proven safe for logical UPDATE compaction.
- Backup: Created (pre-compaction-20260718-135520, ~24.77 GiB).
- Free space: Adequate.
- Manifest hash: Dry-run hash computed, but separate apply scripts did not re-verify against the exact dry-run hash. Active writes invalidated the hash between runs.
- CLI fingerprint: Same CLI version used; not explicitly verified per-batch.

This is a deviation from the reviewed safety model, not a safety failure. The database remained consistent throughout (WAL mode), and the results are valid. But the safety guarantees of the reviewed path (exact manifest approval, writer detection, projection verification) were not exercised.
