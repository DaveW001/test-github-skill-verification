# Architecture Note - Phase 1.2 - Upstream Reference Algorithm Review

**Track:** 20260717-opencode-event-log-compaction
**Pinned upstream reference (immutable, from upstream-decision.json):**
- repo `anomalyco/opencode`, PR #36710 (OPEN, unmerged)
- head `04954f8bde41730251c7516f45d34b975b1d45f5` | base `5bdfcaac3c7772fac3a6ab2370a64e9e7975a572` (branch `dev`)
- fetched-diff SHA-256 `34db7a06bebf1a8195177fe7d57865840138528e339c98c92b530b75821b2f1c`
- Files reviewed (local temp copies, content not reproduced here): `packages/core/src/session/event-log-compaction.ts` (238 lines), `packages/core/test/session-event-log-compaction.test.ts` (156 lines), `packages/schema/src/event.ts`, `packages/schema/src/durable-event-manifest.ts`, `packages/core/src/database/schema.gen.ts`, `packages/schema/src/session-message.ts`, `packages/opencode/src/cli/cmd/db.ts`.

## Upstream Algorithm (as implemented at head)

**Compactable event policies (exactly two):**
| type | entity-id JSON path | projection table | fields stripped for comparison |
|---|---|---|---|
| `message.updated.1` | `$.info.id` | `message` | `id`, `sessionID` |
| `message.part.updated.1` | `$.part.id` | `part` | `id`, `messageID`, `sessionID` |

**Selection:** for each policy, the latest event is `MAX(seq)` per `(type, aggregate_id, entity_id)` where `entity_id = json_extract(data, path)`. A **candidate** is any event of the same type with `event.seq < latest.seq` for the same logical entity (i.e. a superseded snapshot). Ordered by `aggregate_id, seq`; fetched `LIMIT N+1` to detect `hasMore`.

**Projection safety (`safe`):** `projectedData` = the LATEST retained snapshot's `info`/`part` with the strip-fields removed; compared via `require("util").isDeepStrictEqual` to the CURRENT projection row's `data`. Equality means the retained latest snapshot already reproduces the current projection, so shrinking the older superseded snapshot loses no projection state.

**Eligibility:** `safe(candidate) AND candidate.workspaceID === null AND candidate.ownerID === null`. Workspace- or sync-owned (`event_sequence.owner_id`) aggregates are dry-run-only (no marker-version negotiation for sync).

**Mutation (apply):** a single `db.transaction({ behavior: "immediate" })`. For each eligible candidate: `UPDATE event SET type = "event.compacted.1", data = checkpoint(candidate) WHERE id = ? AND type = ?`. This is an **in-place rewrite** of the superseded event row into a tiny marker; `seq` is never touched. `checkpoint = { aggregateID, supersededType, supersededBy }`. Bytes reclaimed = `old_bytes - len(checkpoint_json)` (logical only; physical reclamation is separate).

**Limits / scope:** `DEFAULT_LIMIT=1000`, `MAX_LIMIT=10_000` (validate throws above 10k). Scope is mutually exclusive: exactly one of `aggregateID` (single session) or `all`. `apply` is opt-in (default = dry run: `rewritten=0`).

**Report fields:** `dryRun, candidates, rewritten, projectionMismatches, compatibilityRejected, malformed, payloadBytesReclaimed, hasMore, continuation, byType`. `continuation` is a stateless re-run command `opencode db compact-events --session <id>|--all --apply --limit N` (it exposes the aggregate/session id in the command string).

**CLI:** `opencode db compact-events (--session <id> | --all) [--apply] [--limit N]`; `opencode db ...` status path reports counts + `recommended`.

**Checkpoint marker schema (`event.ts`):** `Event.Compacted` -> type `event.compacted`, durable `{ version: 1, aggregate: "aggregateID" }`, data `{ aggregateID, supersededType, supersededBy }`. Versioned type string = `event.compacted.1`.

## Mutation -> Tested-Invariant Trace

| Mutation (what changes) | Invariant preserved | Upstream test evidence |
|---|---|---|
| Rewrite superseded `event.type`+`data` to `event.compacted.1` | Projection rows untouched; latest snapshot retained | L74 projection unchanged after apply; L71 rewritten=1 |
| `seq` never modified | `event_sequence.seq` monotonic | L72 compacted seq order `[0,1]` preserved |
| Eligibility excludes workspace/owner rows | Owned/synced fail closed | L143 compatibilityRejected>0, candidates=0 |
| `safe()` deep-equal gate | No projection loss | L61 projection `{agent:"after"}` retained |
| `limit <= 10000` | Bounded mutation | L152 limit-validation error |
| Dry-run default (`apply` opt-in) | No mutation unless explicit | L60 dry run rewritten=0 |
| Append after compaction | Next append projects correctly | L133 appended message projection ok |
| Idempotent re-run | Re-application is a no-op | L108 idempotent candidates=0 rewritten=0 |

## Local Requirement Mapping (adopted / adapted / new / blocked)

| Spec requirement | Status | Notes |
|---|---|---|
| Compactable types & logical keys (`$.info.id`, `$.part.id`) | **ADOPTED** | policies[] verbatim |
| Supersession proof + projection comparison | **ADOPTED** | `safe()` deep-equal vs projection row |
| Canonical projection encoding for hashing | **ADAPTED** | upstream uses runtime deep-equal; LOCAL must define a stable canonical JSON for manifest hashes (Phase 3.2) |
| Checkpoint format/version `event.compacted.1` | **ADOPTED** | durable v1 marker |
| Boundary B = superseded candidate seq; tail = latest retained (seq > B) | **ADAPTED** | reference-checkpoint interpretation (see decisions) |
| Immediate transaction per batch | **ADOPTED** | `behavior:"immediate"` |
| Row cap 10,000 | **ADOPTED** | `MAX_LIMIT` |
| Ownership/workspace/sync rejection | **ADOPTED** | workspaceID/ownerID filter |
| Append safety / seq monotonic | **ADOPTED** | seq untouched; append tested |
| Dry-run default | **ADOPTED** | `apply` opt-in |
| Malformed-JSON detection | **ADOPTED** | `malformed()` count |
| Latest-row retention (MAX seq kept) | **ADOPTED** | candidates are `seq < latest.seq` only |
| Unknown-event retention | **ADOPTED** | only the two policies are ever selected |
| Multi-batch immutable ordered chain (pre/post-state commitments) | **NEW** | upstream only has a stateless continuation command; chain binding is local (Phase 3.2/3.3) |
| Exact SHA-256 manifest + approval | **NEW** | upstream has no manifest/hash; local skill/ops layer |
| 90-day cutoff (`event_time < cutoff`, equality retained) | **NEW** | upstream has NO age filter; purely seq-supersession. Source locked in retention-policy.md |
| Allowed timestamp fields + tz/precedence/conflict fail-closed | **NEW** | local policy (Phase 1.3) |
| Content redaction (no IDs/payloads in shared output) | **ADAPTED** | report is aggregate-only, but `continuation` leaks `--session <id>`; LOCAL must redact aggregateID to private channel only |
| Physical reclamation (`VACUUM INTO` + reversible swap) | **NEW** | out of upstream scope; local skill/ops layer (Phase 4.6/5.6/6.7) |

## Locked Design Decisions (evidence-grounded)

1. **Rewrite = logical deletion.** Upstream rewrites superseded events to `event.compacted.1` markers rather than deleting rows. This is consistent with spec Invariant 13 ("physical reclamation is separate"): the large payload content is logically removed (reclaimed bytes), projections are never touched, and physical space is reclaimed later only via `VACUUM INTO` into a new validated file. Rationale: upstream names the primitive "Compacted"/"checkpoint", and rewrite preserves a reversible tombstone (safer rollback than blind delete). **No spec Non-Goal is violated** (no projection truncation, no generic raw-SQL path - this is the supported CLI).

2. **Reference-checkpoint model.** Spec Invariant 4 describes a projection-state checkpoint with a replay tail. Upstream implements a *reference* checkpoint: the marker records `{aggregateID, supersededType, supersededBy}` (a pointer to the retained latest event), and the retained latest snapshot (seq = MAX > B) is the replay source whose projected form is proven byte-equivalent to the current projection. Mapping: checkpoint-format-version = `event.compacted.1` (v1); boundary B = superseded candidate seq; "state after events <= B" = the retained latest snapshot's projection (verified, not re-stored); "tail > B" = the latest retained snapshot. This is the proven, upstream-compatible interpretation. Adopting it avoids inventing a novel value-stored projection checkpoint.

## Items Flagged for Spec-Owner Awareness (not hard blockers)

- **D1 (rewrite-vs-delete):** spec text occasionally says "deletion"; implementation rewrites. Resolved as logical deletion (Decision 1). Confirm acceptable.
- **D2 (checkpoint model):** reference-checkpoint adoption vs literal projection-state checkpoint (Decision 2). Confirm acceptable; otherwise a larger NEW build is required.
- **D3 (part timestamp reliability):** `message.updated.1` payload has a reliable `time.created`; `message.part.updated.1` part timestamp is confirmed via projection `part.time_updated` and parent-message `time.created` fallbacks, with fail-closed retention. No data dependency on the part payload alone.

None of D1-D3 block safe test writing; all are locked with rationale and consistent with upstream evidence.

## Conclusion

Every mutation traces to a tested invariant. The upstream provides a proven, bounded, projection-safe compaction primitive. The LOCAL additions are: (a) a NEW 90-day age filter with fail-closed timestamp resolution (Phase 1.3), (b) a NEW manifest/hash/ordered-chain/exact-approval layer, and (c) a NEW physical-reclamation + skill/ops layer. Two evidence-grounded design decisions (D1, D2) are locked and flagged for awareness.
