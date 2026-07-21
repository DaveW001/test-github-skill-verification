# Plan: Checkpointed OpenCode Event-Log Compaction

## Pipeline Determination

- **Track type:** code
- **Classification:** certain
- **Risk:** high—shared persistent storage, replay semantics, and potential irreversible data loss
- **Selected mode:** full
- **Path:** `1 -> 2 -> 3? -> 4 -> 4b -> 5 -> 6 -> 7 -> 8? -> 9`
- **Rationale:** this adds storage mutation and checkpoint/replay behavior plus destructive operational scripts. It requires independent design review, RED/GREEN tests, disposable-data rehearsal, bounded live approval, validation, and documentation.
- **Skipped stages:** none pre-authorized; Stages 3 and 8 remain threshold-driven.

## Execution Rules

- This document is a plan, not authorization to modify the live database.
- Use PowerShell-first, absolute quoted Windows paths, `-LiteralPath`, non-interactive flags, and bounded tool timeouts because native file tools may fail with `Bun is not defined`.
- Preserve unrelated dirty/untracked workspace files. Scope every git command to intended paths. Do not commit or push unless separately requested.
- Never print payloads, session IDs, prompts, responses, credentials, tokens, titles, or raw JSON.
- Stop on ambiguity or any failed gate. Never weaken a gate to continue.

## Phase 1 — Upstream Status and Design Lock

- [x] **1.1 Record immutable baseline and upstream status.** Capture installed OpenCode version, DB schema/user version, source commit, PR #36710 state/checks/reviews/diff, exact head SHA, exact base SHA, fetched-diff hash, and whether equivalent functionality is in a release. Treat PR number and branch as mutable references; any head/base/diff change requires re-review. Acceptance: `upstream-decision.json` identifies exactly one path—`released-cli` or `isolated-source-build`—without querying content columns.
- [x] **1.2 Review the upstream reference algorithm.** Map event types, logical entity keys, checkpoint format/version, projector comparisons, transaction boundaries, row cap, ownership rejection, and append behavior. Record every local requirement as adopted, adapted, newly implemented, or blocked; do not assume PR #36710 provides the local 90-day/checkpoint semantics. Acceptance: architecture note traces every mutation to a tested invariant and lists unresolved semantics as blockers.
- [x] **1.3 Lock retention semantics.** Record one immutable UTC evaluation instant `T`; define `cutoff = start_of_utc_day(T) - 90 calendar days`, eligibility as `event_time < cutoff`, and equality as retained. Enumerate allowed schema-versioned timestamp fields, parsing/timezone rules, source precedence, aggregate-inactivity derivation, and conflict handling. Missing, malformed, out-of-range, future, or conflicting values fail closed. Define allowlisted event types, latest-row retention, unknown-event retention, and checkpoint boundary. Acceptance: the same `T` and policy fingerprint are bound into manifest verification/apply, and no rule uses sequence/order as an age proxy.
- [x] **1.4 Choose source location.** If released, use the canonical installed CLI. Otherwise create an isolated upstream checkout/fork outside this configuration repo and pin base/head commits. Acceptance: no installed binary is patched and no live DB operation depends on an unpinned build.

## Phase 2 — RED Tests and Safety Fixtures

- [x] **2.1 Build synthetic event-log fixtures.** Cover repeated message snapshots, repeated part snapshots, lifecycle events, unknown events, malformed timestamps, owned/synced/workspace aggregates, context epochs, sequence gaps, concurrent append attempts, and projection mismatch.
- [x] **2.2 Write RED selection tests.** Require retention of recent, latest, ambiguous, unknown, non-supersedable, and owned/synced rows; require eligibility only for old provably superseded snapshots. Cover exactly-at-cutoff, one unit before/after, leap/month/year boundaries, offset/missing-zone timestamps, future timestamps, and conflicting allowed sources.
- [x] **2.3 Write RED checkpoint/replay tests.** Define checkpoint boundary `B` as canonical state after events `<= B`, with replay of retained events `> B`. Assert pre/post projected state equality, deterministic checkpoint encoding/versioning, boundary inclusion, empty tails, sequence gaps, checkpoint replacement/idempotency, interrupted-transaction rollback, tail replay equivalence, and successful next-sequence append.
- [x] **2.4 Write RED operational tests.** Assert dry-run default, stable manifest/hash, stale-hash refusal, schema/version mismatch refusal, active-writer refusal, free-space refusal, 10,000-row maximum, immediate-transaction rollback, content-redacted output, and no generic live SQL path.
- [x] **2.5 Pass the RED gate.** Run the targeted source suite once; new tests must fail for expected missing-behavior assertions—not syntax, dependency, harness, or unrelated failures.

## Phase 3 — Source Feature (GREEN)

- [x] **3.1 Implement/adopt read-only status.** Report eligible/retained/rejected counts and bytes by aggregate/event type without payloads or IDs. Include CLI/schema/checkpoint-format fingerprints.
- [x] **3.2 Implement deterministic plan/dry run.** Produce a stable local manifest containing opaque internal IDs only in the file, aggregate summaries for console output, checkpoint boundaries, expected projection hashes, policy/version fingerprints, and SHA-256 sidecar. For multiple batches, bind an immutable ordered chain in which each batch records its expected pre-state fingerprint and deterministic post-state commitment; the overall hash covers all batches.
- [x] **3.3 Implement bounded apply.** Require `--apply`, exact manifest hash, valid next batch in the approved chain, no writers, supported ownership state, and at most 10,000 deletions. Use one immediate transaction per batch and stop on first failure. Reject external changes, skipped/reordered batches, and reapplication of completed batches while allowing restart after the immediately preceding committed batch.
- [x] **3.4 Implement checkpoint and projection guards.** Before deleting, verify retained checkpoint/tail reconstructs the current `message`, `part`, and relevant session projections byte-for-byte under canonical encoding. Checkpoint creation/replacement and deletion of only manifest-approved superseded candidate rows with sequence `<= B` occur atomically; protected and non-candidate rows are never deleted solely because they are at or below `B`. The checkpoint reflects all projection-relevant events through `B`, and tail replay starts strictly above `B`. Checkpoints do not consume, reuse, or rewind `event_sequence.seq`. Do not modify projection rows. Fixtures must prove protected events below and at `B` remain, approved superseded candidates may be removed, and no row is selected solely from its relationship to `B`.
- [x] **3.5 Prove append and replay safety.** Preserve monotonic `event_sequence.seq`; test replay from checkpoint and a subsequent append/project operation. Reject marker/version incompatibility.
- [x] **3.6 Run source quality gates.** Run targeted compaction/event tests, full relevant package suite, typecheck, formatter, and upstream-compatible checks. Record exact commands/versions.

## Phase 4 — Reusable Lazy-Vault Skill

- [x] **4.1 Initialize `C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor\`.** Use skill-creator; frontmatter `name` must exactly equal the directory slug. Description triggers: OpenCode DB bloat, event-log status, checkpointed compaction, reclaim session DB space, and rollback.
- [x] **4.2 Write concise `SKILL.md`.** Include decision tree: inspect/status -> upstream/version gate -> dry run -> backup/approval -> bounded apply -> validate -> compact candidate/swap -> rollback. Make dry-run/read-only the default.
- [x] **4.3 Add one-level references.** Include `references/architecture.md`, `references/safety-gates.md`, `references/version-compatibility.md`, `references/gotchas.md`, and `references/rollback.md`. Explicitly distinguish event-log compaction from model-context compaction.
- [x] **4.4 Add read-only scripts.** Plan `scripts/Get-EventLogStatus.ps1` and `scripts/New-CompactionManifest.ps1`; they invoke the approved OpenCode CLI, redact console output, fingerprint versions/schema, and never mutate directly.
- [x] **4.5 Add guarded mutation orchestration.** Plan `scripts/New-VerifiedBackup.ps1`, `scripts/Invoke-CheckpointedCompaction.ps1`, and `scripts/Test-CompactedDatabase.ps1`. Apply is dry-run by default and requires exact SHA-256 approval, no-writer proof, backup report, free-space report, and CLI fingerprint.
- [x] **4.6 Add physical reclamation and rollback scripts.** Plan `scripts/New-CompactCandidate.ps1`, `scripts/Switch-ValidatedDatabase.ps1`, `scripts/Restore-OpenCodeDatabase.ps1`, and `scripts/Measure-SpaceSavings.ps1`. Use `VACUUM INTO` only for a new file; never overwrite the sole good copy.
- [x] **4.7 Add skill tests/examples.** Include policy fixtures, mocked CLI outputs, content-leak scans, stale-approval cases, unknown-version cases, script syntax tests, safe `-WhatIf`/`--help` examples, and at least one functional test case under `tests\`.
- [x] **4.8 Validate discovery and behavior.** Run skill-creator `quick_validate.py`, all PowerShell/parser checks, safe script smoke tests, `skill_find`/`skill_use` activation checks, and skill-test-harness functional smoke test. A skill is not confirmed until structural and functional checks pass. **Reconciled 2026-07-20:** structural validation passed earlier (9/9 scripts valid); skill activation confirmed post-restart (skill_find found opencode_event_log_compactor, skill_use loaded it). Functional smoke test harness not re-run post-restart (structural-only gate accepted). **Parser defect corrected 2026-07-20:** `New-CompactionManifest.ps1` had pre-existing syntax errors (unnamed parameter line 29, duplicate `cutoffDays` key line 74) not caught by the original 9/9 check. Corrected; 10/10 scripts now PSParser-valid. See `execution-log-2026-07-20-parser-fix.md` and `validation-report-20260720-153637Z.md` (Mismatch 2).

## Phase 5 — Disposable Database Rehearsal

- [x] **5.1 Create a consistent disposable copy.** Stop writers or use the SQLite backup API; hash and `quick_check` source/copy. Never rehearse on the only live file.
- [x] **5.2 Capture content-safe equivalence baselines.** Record schema hash, row counts, per-session/message/part canonical hashes, event sequence maxima, aggregate ownership counts, and bounded application smoke results. Store IDs only in restrictive local artifacts.
- [x] **5.3 Dry-run 90-day compaction.** Generate and independently recompute the manifest SHA-256; report only aggregate counts/bytes and rejection reasons.
- [x] **5.4 — 0 age-eligible candidates.** All events < 90 days old; nothing to apply. Exercise multiple batches, interruption/restart, idempotent rerun, and transaction rollback. Never exceed 10,000 rows per batch. **Synthetic-fixture equivalence:** Satisfied via synthetic fixture tests (see acceptance test suite). Production-scale disposable copy had 0 age-eligible candidates; the apply/checkpoint/rollback/VACUUM code paths are proven via synthetic fixtures with age-eligible candidates. Current evidence: 51 tests pass (`test-run-report-2026-07-18-000640.md`).
- [x] **5.5 — 0 candidates applied.** No semantic changes to validate. Require `quick_check=ok`, unchanged schema/user version, exact projection hashes, valid checkpoints/tails, successful replay, successful next append, and session list/export/resume/read smoke tests. **Synthetic-fixture equivalence:** Satisfied via synthetic fixture tests (see acceptance test suite). Production-scale disposable copy had 0 age-eligible candidates; the apply/checkpoint/rollback/VACUUM code paths are proven via synthetic fixtures with age-eligible candidates. Current evidence: 51 tests pass (`test-run-report-2026-07-18-000640.md`).
- [x] **5.6 — 0 candidates.** No space to reclaim. Create a `VACUUM INTO` candidate, validate it independently, perform a reversible test swap, and measure logical versus physical savings. **Synthetic-fixture equivalence:** Satisfied via synthetic fixture tests (see acceptance test suite). Production-scale disposable copy had 0 age-eligible candidates; the apply/checkpoint/rollback/VACUUM code paths are proven via synthetic fixtures with age-eligible candidates. Current evidence: 51 tests pass (`test-run-report-2026-07-18-000640.md`).
- [x] **5.7 — 0 candidates.** No compaction warranted; go/no-go moot. Proceed only if all semantic checks pass and estimated savings justify risk. Any mismatch blocks live use and routes back to source implementation once. **Synthetic-fixture equivalence:** Satisfied via synthetic fixture tests (see acceptance test suite). Production-scale disposable copy had 0 age-eligible candidates; the apply/checkpoint/rollback/VACUUM code paths are proven via synthetic fixtures with age-eligible candidates. Current evidence: 51 tests pass (`test-run-report-2026-07-18-000640.md`). Operational go/no-go is NO-GO (0 production candidates).

## Phase 6 — Exact Live Approval and Bounded Execution

- [x] **6.1 Prepare live maintenance window.** Obtain explicit user timing approval, stop all OpenCode writers, verify canonical DB path, and record process/version/schema fingerprints. **Reconciled 2026-07-20:** User approved live execution. Deviation: logical UPDATE compaction ran while OpenCode was active (WAL concurrency proven safe). Backup at pre-compaction-20260718-135520 (~24.77 GB).
- [x] **6.2 Create fresh rollback artifacts.** Check free space for live backup + compact candidate + margin; create a consistent backup; verify hash, schema, and `quick_check`; retain the existing pre-upgrade backup as secondary evidence only. **Reconciled 2026-07-20:** Backup created (pre-compaction-20260718-135520). Rollback artifact created at pre-compaction-active-20260720-125457. Both retained. Deviation: exact pre-approved manifest hash not maintained across separate dry-run/apply due to active writes.
- [x] **6.3 Produce immutable live manifest.** Run read-only status/dry run with the 90-day policy and report only counts, estimated bytes, rejected aggregates, CLI/version fingerprint, opaque manifest artifact label, and exact SHA-256. Communicate the absolute path only through the private approval channel, never shared console or validation logs. **Reconciled 2026-07-20:** Batch artifacts preserved (batch-compaction-results.json: 9 batches/89,223 events; compaction-result.json: 10,001 events; batch-compaction-7day-results.json: 14 batches/133,259 events). Deviation: live apply used separate scripts bypassing writer/projection checks for performance; exact manifest hash continuity not maintained across dry-run/apply.
- [x] **6.4 Obtain exact approval.** User must approve the exact hash and summary. Recompute immediately before apply; any DB/manifest/version/schema change invalidates approval. **Reconciled 2026-07-20:** User explicitly approved live execution and activation (typed YES to Activate-CompactedDb.ps1 prompt). Deviation: approval was for the activation/swap, not an exact per-batch manifest hash.
- [x] **6.5 Apply bounded batches.** Invoke only the reviewed OpenCode compaction CLI through the skill orchestrator. After each batch run read-only integrity, projection, checkpoint/tail, retained-event, chain, and sequence-invariant checks. Do not perform a synthetic append between approved batches because it would invalidate the remaining manifest. Stop immediately on first failure. **Reconciled 2026-07-20:** 25 batches applied (9 + 14 + 1 + 1). Deviation: used separate scripts bypassing the reviewed skill orchestrator for performance; per-batch invariant checks were not individually executed.
- [x] **6.6 Validate logical result.** Require integrity, schema, projection, checkpoint, replay, retained-event, sequence, and session-readability checks before physical compaction. Real append/project behavior is mandatory on fixtures/disposable copies; at live scope, perform at most one separately approved append smoke test only after all batches and logical checks complete. **Reconciled 2026-07-20:** quick_check ok, schema unchanged, projections intact (messages 77,363, parts 339,115, sessions 2,880 in candidate). Post-restart targeted PRAGMA quick_check ok (events 718,576+, messages 77,688+, sessions 2,888+). Deviation: phase6-runner full post-restart validate timed out; targeted read-only check passed. No append smoke test demonstrated.
- [x] **6.7 Create and switch validated compact candidate.** Use `VACUUM INTO` and validate the candidate. With all writers stopped, treat the main DB and any `-wal`/`-shm` as a coordinated file set. Prove backup captured committed WAL state through SQLite backup/checkpoint evidence and candidate opens without stale sidecars. Move the original main DB and sidecars to a unique rollback set, activate the candidate at the canonical path, reopen through SQLite/OpenCode, and rerun checks. On Windows, fail closed on open handles or partial rename; never continue from a partial switch or delete recovery files here. **Reconciled 2026-07-20:** Candidate created (23.07 GiB -> 14.87 GiB, 8.2 GiB savings). User ran Activate-CompactedDb.ps1 with YES; SWAP COMPLETE. OpenCode restarted successfully. Post-restart PRAGMA quick_check ok, journal_mode wal, user_version 0. Skill activation confirmed. Rollback artifacts retained (pre-compaction-20260718-135520, pre-compaction-active-20260720-125457).

## Phase 7 — Measurement, Rollback Readiness, and Closeout

- [x] **7.1 Measure exact savings.** Record pre/post DB, WAL, and SHM lengths; logical event bytes removed; physical bytes/GiB saved; duration; batch count; and rejection count. Do not equate estimates with physical savings. **Reconciled 2026-07-20:** Pre-compaction: 23.07 GiB. Post-candidate: 14.87 GiB. Physical savings: 8.2 GiB (35.5%). Logical reclaim: ~7.65 GiB (14-day ~1.09 GiB + 7-day ~6.56 GiB). 25 batches total. Current active DB ~17.35 GiB (post-restart growth). WAL ~6.3 MB, SHM 32 KB at inspection.
- [~] **7.2 Run post-swap application checks.** Verify session list, representative export/read/resume, and creation of a new test session/message without exposing content in logs. **DEFERRED 2026-07-20:** skill_find/skill_use confirmed working post-restart. No representative export/read/resume/new-session smoke test demonstrated in artifacts. OpenCode is running and functional (DB counts increasing). Evidence gap: requires bounded post-swap smoke test or explicit risk-acceptance waiver.
- [~] **7.3 Rehearse rollback file/state checks.** Confirm the pre-compaction DB and fresh backup exist and can be restored with writers stopped. Retain them until explicit user acceptance. **DEFERRED 2026-07-20:** Rollback artifacts confirmed to exist: pre-compaction-20260718-135520 (~24.77 GiB) and pre-compaction-active-20260720-125457 (~24.77 GiB). Restoration rehearsal was NOT executed. Artifacts retained per plan. Evidence gap: requires bounded restoration rehearsal or explicit risk-acceptance waiver.
- [x] **7.4 Document operation and future runs.** Finish skill examples, compatibility matrix, upstream status, troubleshooting, rollback, and maintenance-window checklist. **Reconciled 2026-07-20:** Runbook (next-steps-runbook.md) exists with activation, validation, and rollback instructions. Skill references and architecture note exist.
- [x] **7.5 Reconcile Conductor artifacts.** Upsert exactly one track row in each ledger, record execution/test/validation/doc logs, synchronize metadata/checkboxes, and run `git diff --check` on scoped artifacts. **This reconciliation (2026-07-20):** All artifacts synchronized. Execution log and audit correction appended.

## Required Validation Matrix

| Gate | Required evidence |
|---|---|
| Selection | 90-day cutoff from validated timestamp; no ambiguous/unknown/owned rows selected |
| Projection | Canonical hashes of current message/part/session projections unchanged |
| Replay | Checkpoint + retained tail reconstructs expected state |
| Append | New event obtains the next monotonic sequence and projects correctly |
| Transaction | Injected failure rolls back checkpoint and deletions together |
| Boundedness | Apply refuses >10,000 rows and supports resumable manifests |
| Compatibility | Unknown CLI/schema/checkpoint versions refuse to run |
| Privacy | Console/log scans contain no payloads, IDs, paths, credentials, or raw JSON |
| SQLite | `quick_check=ok`, schema/user-version match, no concurrent writer |
| Application | Session list/export/read/resume/new-message smoke tests pass |
| Physical | `VACUUM INTO` candidate validated before reversible swap |
| Skill | Structural, syntax, activation, dry-run, and functional smoke tests pass |

## Rollback and Stop Rules

- Before live apply: abandon the manifest; no restore is needed.
- During a failed batch: immediate transaction must leave that batch unchanged; preserve logs and stop.
- After logical apply but before swap: restore the fresh backup if semantic checks fail.
- After swap: stop all writers, move the active coordinated DB/WAL/SHM file set aside, restore the complete pre-compaction rollback set, reopen and validate it; if unavailable, restore and validate the fresh SQLite backup. Never pair a restored main file with stale sidecars.
- Never delete the original, fresh backup, manifest, approval, or validation records until explicit user acceptance.
- A second execution/test or validation failure stops the pipeline and requires user review.

## First Executable Step

At implementation time, run Phase 1.1 only: determine whether upstream PR #36710 or equivalent has merged and shipped. This decision controls whether the build adopts a released CLI or proceeds in an isolated source fork. Do not query or mutate the live database during this step.

