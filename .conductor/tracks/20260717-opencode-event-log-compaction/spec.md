# Spec: Checkpointed OpenCode Event-Log Compaction

## Goal

Build and validate an OpenCode-aware, checkpointed event-log compaction capability that can remove provably superseded durable event snapshots older than 90 days while preserving current sessions, user prompts, assistant responses, projected message/part state, append safety, and rollback. Package the operational workflow as a reusable lazy-loaded OpenCode skill with fail-closed scripts for future runs.

## Background and Baseline

- Live database: `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` (about 19.185 GiB plus WAL during the investigation).
- `freelist_count = 0`; existing size is retained payload, not free-page slack.
- Approximate payload: `event.data` 16.612 GB decimal, `message.data` 2.282 GB, and `part.data` 1.074 GB.
- Dominant event payloads: `message.updated.1` 12.627 GB and `message.part.updated.1` 3.965 GB.
- A prior whole-session policy protected all 2,776 sessions, produced zero candidates, and performed no deletion or compaction.
- Upstream issues [#32005](https://github.com/anomalyco/opencode/issues/32005) and [#33356](https://github.com/anomalyco/opencode/issues/33356) confirm the same append-only full-snapshot growth.
- Open upstream PR [#36710](https://github.com/anomalyco/opencode/pull/36710), `fix(core): bound event log compaction`, is the reference design. As of 2026-07-17 it is not merged. It provides read-only status, dry-run-by-default bounded compaction, projection verification, an immediate transaction, append-safety tests, a 10,000-row cap, and rejection of workspace/sync-owned aggregates.

## Scope

### Source feature

Implement or adopt an upstream-compatible OpenCode CLI feature for event-log status, planning, and bounded apply. The implementation must live in an isolated OpenCode source checkout/fork unless equivalent functionality has been merged and released upstream. Never patch the installed executable or introduce a standalone raw-SQL cleaner for the live database.

### Reusable skill

Create `C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor\` with:

- concise `SKILL.md` and progressive-disclosure references;
- read-only status/inventory and dry-run manifest scripts;
- backup, apply-orchestrator, validation, compact-candidate/swap, rollback, and savings-measurement scripts;
- tests, safe examples, gotchas, and rollback documentation;
- structural validation and functional smoke-test evidence.

The skill scripts orchestrate the supported/new OpenCode CLI. They must not implement direct live-database event deletion themselves.

## Safety Invariants

1. **Projection preservation:** no v1 deletion of `message`, `part`, `session_message`, session metadata, prompts, responses, or other current-state projections.
2. **Supersession proof:** remove only event types and rows whose newer retained event or checkpoint provably reproduces the current projection.
3. **Checkpointed replay:** each compacted aggregate retains a versioned checkpoint plus the event tail required for replay and subsequent appends.
4. **Checkpoint boundary:** each checkpoint records aggregate identity, checkpoint format version, projector/schema version, and a boundary sequence `B`. Its state is the canonical projection after applying all projection-relevant events for the aggregate with sequence `<= B`, including retained non-supersedable events. Replay from that checkpoint applies retained tail events with sequence `> B`, in sequence order. Checkpoint creation/replacement and deletion of only the manifest-approved, allowlisted, provably superseded candidate rows with sequence `<= B` occur in the same immediate transaction. Protected or non-candidate events are not deleted merely because their sequence is `<= B`. The checkpoint representation must not reuse, decrement, or ambiguously consume `event_sequence.seq`.
5. **Sequence safety:** `event_sequence.seq` remains monotonic and is not rewound; a post-compaction append receives the next valid sequence.
6. **Age is validated:** event rows have no timestamp column. One immutable UTC evaluation instant `T` is recorded in the policy and manifest. The v1 cutoff is `start_of_utc_day(T) - 90 calendar days`; eligibility requires `event_time < cutoff`, so equality is retained. Only schema-versioned, explicitly allowlisted payload timestamp fields or a documented aggregate-inactivity derivation may supply `event_time`. The design must define parsing, timezone, source precedence, and conflict handling. Missing, malformed, future, out-of-range, or conflicting values are retained. Row order or sequence alone is not an age proxy.
7. **Owned/synced fail closed:** aggregates with `event_sequence.owner_id`, workspace ownership, active synchronization, or unknown ownership semantics are ineligible until marker-version negotiation exists.
8. **Bounded mutation:** apply is explicit, batch-limited to at most 10,000 rows per invocation, and enclosed in one immediate transaction per batch. A multi-batch manifest is an immutable ordered chain: each batch binds its expected pre-state and deterministic post-state commitment; only the immediately preceding approved batch may advance the chain.
9. **Exact approval:** every live apply is bound to a stable manifest and its exact SHA-256. Any database, policy, version, schema, manifest, or out-of-chain database change invalidates approval.
10. **No concurrent writers:** all OpenCode CLI/Desktop/server/scheduler writers are stopped before backup, apply, checkpoint, vacuum candidate, or swap.
11. **Rollback first:** a fresh consistent backup and adequate free-space gate must pass before live mutation.
12. **No content disclosure:** shared console/chat/log output contains aggregate counts, bytes, versions, artifact labels, and hashes only—never event payloads, prompts, responses, tool output, credentials, tokens, titles, sensitive/content-derived paths, or session IDs. Absolute local artifact paths may be communicated only through the private approval/handover channel.
13. **Physical reclamation is separate:** logical event deletion is followed only by `VACUUM INTO` a new validated file and a reversible coordinated DB/WAL/SHM file-set swap; never in-place `VACUUM`.

## Retention Policy v1

- Default cutoff: 90 full UTC days.
- Eligible rows: only explicitly allowlisted supersedable snapshot event types older than the cutoff, after checkpoint/projection verification.
- Retain:
  - the latest snapshot needed for each logical entity/event family;
  - all tail events with sequence strictly greater than checkpoint boundary `B`, plus every independently protected or non-candidate event regardless of whether its sequence is at, below, or above `B`;
  - lifecycle, permission, context-epoch, input-admission, interruption, agent/model switch, compaction, and unknown event types unless replay tests prove them supersedable;
  - every ambiguous, malformed, owned, synced, workspace-associated, or actively written aggregate.
- `message.part.updated.1` is not automatically eligible merely because it is large. Its entity identity, projection equivalence, and ordering semantics must be proven independently.
- A status report must distinguish estimated logical bytes from measured physical bytes.

## Version and Upstream Decision Gate

At execution time:

1. Check whether PR #36710 or an equivalent implementation has merged and is present in a released OpenCode version.
   Resolve mutable PR/branch references to exact head and base commit SHAs plus a fetched-diff hash. Any force-push, rebase, or head/base change invalidates prior design review.
2. If released, upgrade through the supported channel, validate command semantics/version fingerprint, and make the skill wrap that CLI.
3. If not released, use an isolated upstream source checkout/fork, rebase or implement the upstream-compatible design, run its full tests, and build a separately identified candidate binary.
4. Never apply an unreviewed source build to the live DB. The candidate must first pass fixtures and a disposable-copy rehearsal.

## Acceptance Criteria

- [ ] Execution-time upstream/release status and chosen path are recorded with immutable commit/version identifiers.
- [ ] RED tests demonstrate that naive age-based deletion, projection mismatch, stale manifests, unknown schemas, active writers, owned/synced aggregates, over-limit batches, and append-sequence regressions are rejected.
- [ ] Fixture tests prove checkpoint creation, replay equivalence, current projection equality, idempotent dry runs, bounded apply, transaction rollback, and successful appends after compaction.
- [ ] Boundary fixtures cover exactly-at-cutoff, before/after cutoff, calendar transitions, offsets/missing zones, future/conflicting timestamps, checkpoint boundary inclusion, empty tails, sequence gaps, replacement/idempotency, and interrupted transactions.
- [ ] A disposable copy of the real database passes `quick_check`, schema fingerprint, projection equality, session-list/export/resume smoke tests, and a new-message append test before and after compaction.
- [ ] No message/part projection row or visible high-level chat/response is lost in fixture or disposable-copy comparisons.
- [ ] Live apply requires no writers, a fresh verified backup, sufficient free space, an exact approved manifest hash, and a supported/candidate CLI fingerprint matching the dry run.
- [ ] Live batches stop on the first failure and never exceed 10,000 rows.
- [ ] A compact candidate created with `VACUUM INTO` passes integrity, schema, projection, retained-event, append, and application smoke checks before reversible swap.
- [ ] Windows activation and rollback treat the main DB plus WAL/SHM sidecars as a coordinated file set and fail closed on open handles or partial renames.
- [ ] Exact pre/post DB+WAL+SHM lengths and logical/physical savings are reported separately.
- [ ] The lazy-vault skill passes skill-creator structural validation, script syntax checks, safe `--help`/dry-run tests, activation tests, and the skill-test-harness functional smoke test.
- [ ] Rollback is documented and rehearsed on disposable files; recovery artifacts remain until explicit user acceptance.

## Non-Goals

- Deleting whole sessions.
- Truncating visible chat, prompts, assistant responses, or projection tables.
- Treating model-context `/compact` or `compaction.prune` as database event-log compaction.
- Editing the live DB with generic `opencode db` SQL or ad hoc scripts.
- Compacting synced/owned/workspace aggregates before a compatible checkpoint-marker protocol exists.
- Automatically scheduling destructive compaction in v1.
- Committing or pushing changes without a separate request.

## Definition of Done

The track is complete only when the source feature and reusable skill pass independent tests, a disposable-copy rehearsal proves projection/replay/append safety, any live run has explicit manifest approval and verified rollback, physical savings are measured after a validated reversible swap, and all Conductor artifacts agree. Planning completion alone does not authorize implementation or live mutation.

## References

- https://github.com/anomalyco/opencode/issues/32005
- https://github.com/anomalyco/opencode/issues/33356
- https://github.com/anomalyco/opencode/pull/36710
