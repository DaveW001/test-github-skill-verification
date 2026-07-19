# Spec: Safely Reduce the Local OpenCode Session Database

## Goal / Outcome
Reduce the disk footprint of `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` by deleting only explicitly approved sessions through the supported `opencode session delete <sessionID>` command, then performing rollback-safe SQLite compaction, while preserving valuable sessions and reporting exact before/after space savings.

## Established Baseline
- Live database: 19.185 GiB plus a 0.550 GiB WAL.
- Pre-upgrade backup: 14.343 GiB at `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\opencode-pre-upgrade-2026-07-14-20260714213156.db`.
- `PRAGMA freelist_count` is 0 before cleanup.
- `event.data` accounts for about 16.61 GB; `message.updated.1` accounts for about 12.63 GB.
- Thirty-six message aggregates account for about 11.15 GB.
- This is event-sourced duplication, so deleting rows directly from `event` is prohibited.

## Constraints / Non-Goals
- Protect valuable user data; a fresh verified safety backup is mandatory. The older pre-upgrade backup is additional evidence, not the rollback source for this cleanup.
- Never print, log, or export message text, event payloads, titles, prompts, responses, credentials, tokens, environment values, or other content fields.
- Candidate selection uses non-content metadata only: opaque session ID, timestamps, archive state, parent/child relationship, and aggregate byte counts. Project/directory values, if needed for grouping, must be SHA-256 hashed before output.
- Do not delete or reset the OpenCode storage directory.
- Do not modify the SQLite schema, migrations, indexes, triggers, or application source.
- Do not directly `DELETE`/`UPDATE` session, message, part, event, or projection rows. Session deletion must use `opencode session delete <sessionID>`.
- Do not run cleanup while any OpenCode CLI, Desktop, server, scheduler, or other writer is using the database.
- Do not select sessions merely because they are large. Size is prioritization evidence only; age/archive/relationship policy and user approval control deletion.
- Do not execute deletion or compaction until the user approves the exact candidate manifest and its summary counts/bytes.

## Explicit Selection Policy
1. **Protected by default:** every session updated in the most recent 180 days; every unarchived session; every session explicitly placed on a keep list; and every ancestor or descendant of a protected session.
2. **Eligible candidate:** a session is eligible only when it is archived, was last updated at least 180 full UTC days before the inventory cutoff, is not on the keep list, and no member of its complete parent/child family is protected.
3. **Family atomicity:** candidates are presented as complete session families. A family is either retained or approved together, preventing broken continuation history.
4. **Prioritization:** sort eligible families by attributed database bytes descending, then oldest update timestamp, without reading or outputting content.
5. **Approval gate:** produce an immutable SHA-256 candidate manifest containing only approved metadata. Stop and ask the user to approve the manifest hash, cutoff, keep-list handling, candidate count, family count, and estimated reclaimable bytes. General authorization to make changes does not waive this deletion gate.
6. **Ambiguity rule:** if archive semantics, relationship closure, byte attribution, CLI/database version alignment, or any candidate mapping is uncertain, protect the affected session and stop rather than guess.


**Policy Override Audit Note (2026-07-17):** The original spec proposed a 90-day retention cutoff. Per explicit user instruction during execution, the policy was overridden to 180 days. All inventory, manifest, and execution artifacts use the 180-day cutoff. This override is preserved in baseline.json, inventory.json, candidate-manifest.json, and all execution logs.

## Requirements
- [ ] Record a metadata-only baseline and confirm no OpenCode writer is active.
- [ ] Verify sufficient free space for a fresh backup and compacted replacement before creating either artifact.
- [ ] Create a fresh consistent SQLite backup with the SQLite backup API after a WAL checkpoint; validate it with `quick_check` and record its SHA-256 hash.
- [ ] Produce a redacted inventory and candidate manifest that satisfy the selection policy and leak no content.
- [ ] Require approval of the exact manifest hash before deletion.
- [ ] Delete approved sessions only through the installed canonical `opencode session delete` command, one family at a time, stopping on the first failure.
- [ ] Validate database integrity and retained/protected session presence after deletion.
- [ ] Compact via `VACUUM INTO` to a new file, validate the new file, and perform a reversible same-volume swap while all writers remain stopped; never vacuum or overwrite the only good copy in place.
- [ ] Preserve the pre-compaction database and fresh safety backup until final user acceptance.
- [ ] Measure exact allocated bytes (`Length`) for DB/WAL/SHM before cleanup and after checkpoint/swap, and report byte and GiB savings without claiming logical deletion bytes as physical savings.

## Acceptance Criteria
- [ ] The inventory artifacts contain no message/event content or credential values and include only the allowed metadata fields.
- [ ] A user-approved manifest hash exactly matches the manifest used by the cleanup command.
- [ ] The fresh backup and compacted candidate each return `quick_check = ok` before destructive progression.
- [ ] Every deletion invocation is `opencode session delete <sessionID>` against an ID from the approved manifest; no direct row deletion occurs.
- [ ] All protected and retained session IDs remain queryable after cleanup, and every approved candidate ID is absent.
- [ ] The final DB schema fingerprint and `PRAGMA user_version` match the pre-cleanup baseline.
- [ ] The final report gives pre/post DB, WAL, and SHM lengths in exact bytes and GiB plus exact net bytes/GiB saved.
- [ ] Rollback instructions have been dry-run through file/state checks and retain both the fresh backup and pre-compaction original.

## Definition of Done
Cleanup is done only after an approved manifest has been applied through the supported CLI, integrity and retention checks pass, a validated compact database has been reversibly swapped into place, exact positive or zero savings are reported, rollback artifacts remain available, and all Conductor completion-gate records agree. Any failed gate leaves the original/restorable database in place and the track incomplete.

## Approvals and Open Ambiguities
- Existing authorization covers planning and eventual guarded changes, but the exact deletion manifest requires a separate explicit approval because selection is irreversible at the application level.
- User input required before execution: confirm or change the 180-day cutoff; provide keep-list session IDs (if any); confirm whether all unarchived sessions must remain protected; and approve the generated manifest hash.
- If available disk space cannot hold both a fresh backup and compacted candidate with a 2 GiB safety margin, the executor must stop and ask for an alternate backup volume; it must not delete data to create room.

