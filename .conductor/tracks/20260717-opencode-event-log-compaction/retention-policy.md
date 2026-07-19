# Retention Policy v1 - Phase 1.3 (Locked)

**Track:** 20260717-opencode-event-log-compaction
**Lock instant (policy definition):** T_lock = 2026-07-17T19:30:00Z
**Policy fingerprint (SHA-256 of canonical rules):** 07702f56721192e60dc55ba78818064f335208f70ddf689139f31271acf0d84b
**Bound rule:** at apply time (Phase 6) a fresh immutable evaluation instant `T_apply` is recorded in the manifest; the SAME policy fingerprint above and the manifest's `T_apply` are both re-verified immediately before apply. Any mismatch refuses apply.

## Canonical Policy JSON (the hashed input, single line, whitespace-stable)

```
{"version":1,"cutoffDays":90,"eligibility":"event_time < cutoff","equalityRetained":true,"cutoffFormula":"start_of_utc_day(T) - 90 calendar days","eventTimeSources":[{"rank":1,"name":"payload.time.created","appliesTo":["message.updated.1"],"field":"$.info.time.created","type":"DateTimeUtcFromMillis"},{"rank":2,"name":"projection.time_updated","appliesTo":["message","part"],"column":"time_updated","type":"epochMillisUTC"},{"rank":3,"name":"aggregateInactivity.session.time_updated","appliesTo":["session"],"column":"time_updated","type":"epochMillisUTC","rule":"retainAllIfSessionActive"}],"parsing":"ISO8601-or-epochMillis interpreted as UTC; no local timezone; naive/zoneless values retained","precedence":"lowestRankWins:payload-over-projection-over-aggregate","conflictRule":"fail-closed-retain","missingMalformedFutureOutOfRangeRule":"retain","allowlistedCompactableTypes":["message.updated.1","message.part.updated.1"],"latestRowRetained":true,"unknownEventRetained":true,"checkpointMarker":"event.compacted.1","checkpointBoundaryB":"supersededCandidateSeq","supersessionModel":"seq < latest.seq per (type,aggregate_id,entity_id)","projectionSafety":"deep-equal(strippedProjectedData, currentProjectionRow)","maxBatchRows":10000,"transaction":"immediate per batch","physicalReclamation":"VACUUM INTO new file + reversible coordinated DB/WAL/SHM swap; never in-place VACUUM","ageProxyForbidden":true}
```

## Immutable Evaluation Instant T and Cutoff

- `T` = one immutable UTC instant recorded in the manifest at apply (Phase 6.3). `T_lock` above is the policy-definition instant only.
- `cutoff = start_of_utc_day(T) - 90 calendar days` (90 full UTC days).
- **Eligibility:** `event_time < cutoff`. **Equality (`event_time == cutoff`) is RETAINED.**
- No rule uses `event.seq`, row order, or any sequence/order value as an age proxy (`ageProxyForbidden: true`). Sequence is used ONLY for supersession (which snapshot is newer), never for age.

## Timestamp Sources (allowed, schema-versioned) - precedence low rank wins

Confirmed from upstream source at head `04954f8b`:
- `event` and `event_sequence` tables have **NO timestamp columns** (schema.gen.ts: event@L80, event_sequence@L73 carry no `time_created`/`time_updated`).
- `message`, `part`, `session_message`, `session` tables carry `time_created`/`time_updated` (epoch millis, UTC, via the `Timestamps` helper).
- Message/part **payloads** carry `time.created` typed `DateTimeUtcFromMillis` (session-message.ts).

| Rank | Source | Applies to | Field / column | Type |
|---|---|---|---|---|
| 1 | payload `time.created` | `message.updated.1` | `$.info.time.created` | DateTimeUtcFromMillis |
| 2 | projection `time_updated` | `message`, `part` | `<table>.time_updated` | epoch millis UTC |
| 3 | aggregate inactivity `session.time_updated` | whole session | `session.time_updated` | epoch millis UTC (retain-all-if-active) |

For `message.part.updated.1`: use the part projection `part.time_updated` (rank 2); if absent/invalid, derive from the parent message `time.created`/`message.time_updated`; never rely on the part payload timestamp alone.

## Parsing / Timezone / Precedence / Conflict Rules (all fail-closed)

- Parse ISO-8601 or epoch-millis; interpret strictly as **UTC**. No local timezone conversion.
- **Precedence:** lowest rank wins (payload > projection > aggregate).
- **Aggregate inactivity (rank 3):** if `session.time_updated >= cutoff - 0` (session active within the retention window), ALL events of that session are retained regardless of other sources.
- **Conflict:** if two resolved sources disagree, **fail closed -> retain** the row.
- **Missing / malformed / naive (zoneless) / out-of-range / future-dated / conflicting values -> RETAIN.** Future timestamps (`event_time > T`) are retained (not eligible).
- A candidate is eligible ONLY when: supersession-eligible (`seq < latest.seq`) AND projection-safe (deep-equal) AND `event_time < cutoff` (resolved per above) AND `workspaceID IS NULL` AND `ownerID IS NULL`.

## Allowlist, Latest-row, Unknown-event, Checkpoint Boundary

- **Allowlisted compactable types (v1):** `message.updated.1`, `message.part.updated.1` only. Any other type is ineligible.
- **Latest-row retention:** the latest event (`MAX(seq)`) per `(type, aggregate_id, entity_id)` is always retained; only strictly-older superseded snapshots are candidates.
- **Unknown-event retention:** event types not in the allowlist are never selected (retained).
- **Checkpoint boundary B:** B = the superseded candidate's `seq`. The retained latest snapshot (`seq > B`) is the replay source; its projected form is proven deep-equal to the current projection. Checkpoint marker = `event.compacted.1` (durable v1, data `{aggregateID, supersededType, supersededBy}`). Protected/non-candidate events at or below B are never compacted solely because of their seq.
- **Row cap:** at most 10,000 candidate rewrites per immediate transaction/batch.

## Binding into Manifest / Apply (Phase 3.2 / 3.3 / 6)

- The manifest records `T_apply`, this policy fingerprint `07702f56721192e60dc55ba78818064f335208f70ddf689139f31271acf0d84b`, CLI/schema/checkpoint fingerprints, per-batch expected pre-state and deterministic post-state commitments, and an ordered immutable chain.
- Apply (Phase 6) refuses unless: exact manifest SHA-256 matches, valid next chain batch, no writers, supported ownership, `<= 10000`, and the recomputed policy fingerprint equals `07702f56721192e60dc55ba78818064f335208f70ddf689139f31271acf0d84b` with a fresh `T_apply`.

## Status

Semantics safely LOCKED from evidence. No hard blocker. Design decisions D1/D2/D3 (see architecture-note.md) are flagged for spec-owner awareness but do not block test writing.
