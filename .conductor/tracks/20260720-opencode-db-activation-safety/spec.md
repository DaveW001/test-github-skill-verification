# OpenCode Database Activation Safety Remediation

## Objective

Eliminate the remaining safety blockers in the `opencode-event-log-compactor` skill by making database activation and restoration fail closed, recoverable after every partial DB/WAL/SHM transition, and demonstrably safe on disposable fixtures. Supersede the unsafe direct file-manipulation path in `Activate-CompactedDb.ps1` without touching the live OpenCode database or deleting existing recovery artifacts.

## Background

The capped Stage 8 validation for parent track `20260717-opencode-event-log-compaction` found four material gaps:

1. Forward activation offers to force-kill OpenCode/bun processes and then continue.
2. Activation and restoration do not perform an explicit open-handle/write-lock probe.
3. Ordered DB/WAL/SHM moves can fail partway without automatic, verified recovery.
4. Acceptance-evidence rows 33 and 34 claim these guarantees are complete when they are not.

Inspection also showed that the risk is duplicated across `Activate-CompactedDb.ps1`, `Switch-ValidatedDatabase.ps1`, and `Restore-OpenCodeDatabase.ps1`. The remediation therefore needs one canonical mutation path rather than a narrow patch to the wrapper.

## Scope

### In Scope

- Make `Activate-CompactedDb.ps1` a thin selector/orchestrator that never directly kills processes or mutates the active DB/WAL/SHM files.
- Route forward activation through a hardened `Switch-ValidatedDatabase.ps1` implementation.
- Route rollback through a hardened `Restore-OpenCodeDatabase.ps1` implementation.
- Add a maintenance-operation lock so two maintenance scripts cannot run concurrently.
- Fail closed if relevant OpenCode writers are detected, process inspection is inconclusive, an existing active file cannot be opened exclusively, or a mutation precondition changes.
- Create a verified recovery snapshot and an atomic operation journal before the first active-file mutation.
- Recover the original coordinated file set automatically after an injected or real partial failure; verify hashes and SQLite `quick_check` before reporting recovery success.
- Preserve every candidate, source backup, rollback set, recovery snapshot, displaced file, and failed-operation journal until explicit user acceptance.
- Add disposable-fixture tests for active writers, locked handles, each partial transition, verification failures, `-WhatIf`, successful activation, and successful restoration.
- Correct the parent acceptance matrix and current documentation to distinguish implemented, tested, deferred, and live-unrehearsed guarantees.

### Out of Scope

- Running activation or rollback against the live OpenCode database.
- Stopping or force-killing OpenCode, bun, scheduler, desktop, CLI, or server processes.
- Deleting either retained pre-compaction backup or any other recovery artifact.
- Re-running event compaction, `VACUUM`, or live application smoke tests.
- Claiming task 7.2 or 7.3 complete without their separately required live evidence.

## Required Design

### 1. One Canonical Mutation Path

`Activate-CompactedDb.ps1` may discover/select the candidate or rollback source and request confirmation, but it must delegate all active-file mutation to the hardened switch/restore scripts. It must contain no `Stop-Process`, no direct active DB/WAL/SHM `Move-Item`, `Copy-Item`, or `Remove-Item`, and no force-kill prompt.

### 2. Writer and Maintenance Gates

Before mutation, the canonical script must:

- acquire and hold a named OS mutex for the entire operation so `-WhatIf` does not need to create a lock file;
- enumerate OpenCode-related processes without mutating them;
- block on OpenCode CLI/Desktop/server/scheduler writers and relevant bun hosts;
- block if a candidate OpenCode/bun process is found but the metadata needed to classify it cannot be inspected safely; inaccessible unrelated processes are not blockers;
- report only process names and PIDs, not command-line secrets or content;
- never offer to terminate a process.

The process provider must be mockable so tests do not depend on the current OpenCode session. These gates provide bounded detection, not a mathematical guarantee that a non-cooperating writer cannot start after inspection. The implementation and documentation must say so explicitly.

### 3. Explicit Handle Probe

Immediately before mutation, probe every existing active DB/WAL/SHM path using an exclusive `FileShare.None` open and close. Repeat process inspection, the exclusive probe, and the expected presence/length/hash check immediately before each sidecar displacement and main replacement. Any failure blocks or enters recovery. This does not eliminate the time-of-check/time-of-use race with a newly starting non-cooperating writer; the filesystem operation itself must use fail-on-open-handle semantics, and every subsequent transition must be journaled, checked, and recoverable. Acceptance claims are limited to detectable writers/handles and tested race outcomes.

### 4. Pre-Mutation Recovery Snapshot

Before moving or replacing an active file:

- inventory the exact active DB/WAL/SHM set;
- copy that set into a unique operation recovery directory;
- record lengths and SHA-256 hashes;
- preserve and hash the raw snapshot without opening it through SQLite;
- create a second private verification copy with the canonical basename and matching sidecars, then run logical checks on that copy so SQLite cannot mutate the raw evidence;
- stage the incoming validated standalone DB in the active database directory;
- verify the staged file's hash and `quick_check`;
- write an operation journal with no sensitive payloads.

No source or recovery file may be deleted as part of success cleanup.

### 5. Journaled State Machine

Persist each journal record by writing a temporary file, closing it, requesting a durable flush, and publishing it with same-directory `File.Replace`/rename. This makes each record atomically published but does not make the multi-file operation atomic. At minimum record:

`preflight-passed -> recovery-snapshot-verified -> sidecars-displaced -> main-replaced -> activated-verified -> committed`

and failure outcomes:

`recovery-started -> original-restored-and-verified` or `recovery-incomplete-manual-intervention-required`.

The journal must include an opaque operation ID, mode, file-presence booleans, lengths, hashes, timestamps, and completed step names. It must not include event payloads, prompts, responses, session IDs, credentials, or raw command lines.

On every invocation, discover unresolved journals before accepting a new operation. Reconcile the journal against actual path presence and SHA-256 values; never trust the last journal label alone.

| Observed crash/restart state | Required action |
|---|---|
| Temporary journal exists but published journal does not | Preserve it; derive state from file hashes and refuse a new operation until reconciled. |
| Raw recovery snapshot is incomplete or unverified | Perform no active-file mutation; fail closed. |
| Sidecar is displaced but main hash is still original | Restore missing sidecars from the raw snapshot, verify the original presence/hash map, and mark recovered failure. |
| Main hash is incoming but journal has not advanced | Treat replacement as completed; either verify and commit or restore the complete original raw set. |
| Main path is absent or has an unknown hash | Preserve every file and enter `recovery-incomplete-manual-intervention-required`; do not overwrite unknown data. |
| Restored set matches original raw hashes | Mark recovered failure only after a private-copy logical verification passes. |
| Any path conflicts with both original and incoming hashes | Preserve all files, refuse automatic overwrite, and require manual intervention. |

Tests may simulate process termination at each boundary, but the docs must not claim guaranteed survival of physical power loss. Windows flush and rename APIs cannot prove controller-level durability. The supported claim is deterministic restart reconciliation from durably closed files when the expected files and hashes remain available.

### 6. Recoverable Activation

Use a same-directory staged candidate so replacement is same-volume. The selected Windows primitive is `[System.IO.File]::Replace(stagedCandidate, activeDb, displacedMainBackup, $true)`: the destination must already exist, all paths must be on the same volume, and copy-overwrite of the canonical DB is prohibited. Move active WAL/SHM sidecars into the recovery directory first, with a repeated process/handle/hash gate before each move. Then repeat the gate for the main DB and call `File.Replace`, which must fail when Windows denies replacement because of an open handle. Preserve both the raw recovery snapshot and the displaced-main backup.

After replacement, verify that the active main has the incoming hash and verify a private copy through SQLite before reporting success. Any exception, unknown hash, newly created sidecar, or failed verification must trigger reconciliation. Recovery is successful only when the original raw file-presence map and DB/WAL/SHM hashes are restored before SQLite opens the active paths and a separate private verification copy returns `quick_check=ok`. SHM remains part of the retained raw evidence/presence contract but is treated as reconstructible SQLite coordination state for logical validation.

If automatic recovery itself fails, preserve all files and the journal, emit a distinct nonzero failure, and provide bounded manual-recovery guidance. Never report activation, rollback, or recovery success from a partial state.

### 7. Recoverable Restoration

A rollback source containing DB/WAL/SHM must never be opened in place. Copy it into a private directory while preserving the canonical basename relationship (`opencode.db`, `opencode.db-wal`, and optional `opencode.db-shm`). Open only that private copy with SQLite and use SQLite's backup API; the `sqlite3` CLI `.backup` command is acceptable only when its executable/version, exit code, and output DB are checked. This must include committed frames visible only through WAL. Verify `quick_check`, schema identity, and known sentinel rows on the standalone result before invoking the canonical switch engine. A verified DB-only backup may be staged directly. SHM may be absent and reconstructed in the private copy; orphan SHM, stale/mismatched WAL, truncated/corrupt WAL, and unknown source combinations fail closed. Stale active sidecars must never be paired with a restored main file.

### 8. Testability

Wrap filesystem transitions and process enumeration behind small script-local functions so Pester can mock them. Tests must inject a failure after every mutating transition and prove either:

- the pre-operation active set is restored byte-for-byte and passes `quick_check`; or
- the script fails with `recovery-incomplete-manual-intervention-required`, preserves all available artifacts, and never reports success.

All tests must use temporary disposable SQLite fixtures. WAL fixtures must include a known transaction committed into WAL but deliberately not checkpointed; the standalone materialized DB must contain that sentinel. Cover valid WAL without SHM, orphan SHM, stale/mismatched WAL, truncated/corrupt WAL, and intentional DB-only backup. Tests must never default to or discover the live OpenCode database.

`-WhatIf` is a read-only planning path. `ShouldProcess` must guard every write, including directories, staging files, snapshots, journal temporaries, sidecar displacement, replacement, and cleanup. `-WhatIf` must not acquire a file-backed lock or create any path. The restore `-Force` parameter may suppress only a final human overwrite confirmation after all gates pass; it must never bypass writer, handle, hash, source, journal, recovery, or `ShouldProcess` gates.

## Acceptance Criteria

1. `Activate-CompactedDb.ps1` contains no force-kill behavior and no direct active-set mutation.
2. All activation and restore entry points block on detected or unclassifiable relevant writers.
3. A named maintenance mutex is held throughout each mutation operation.
4. Locked DB, WAL, and SHM fixtures, including a handle appearing after initial preflight, cause refusal or verified recovery with no false success.
5. Recovery snapshot and journal are verified before the first active-file mutation.
6. Injected failures and child-process termination after each transition reconcile from actual hashes/presence, restore the original raw fixture set byte-for-byte, or produce the explicit preserved-artifact manual-recovery state.
7. Successful activation and restore fixtures pass `quick_check` and leave no stale active sidecars.
8. `-WhatIf` causes zero filesystem mutation, including no lock file, directory, staging file, snapshot, or journal creation.
9. No success message is emitted before post-activation verification and journal commit.
10. Recovery artifacts are never automatically deleted.
11. PowerShell parser checks and Pester safety tests pass for every affected script.
12. Skill docs accurately explain process detection, handle-probe limitations, journal/recovery behavior, and live-rehearsal deferrals.
13. Parent matrix rows 33 and 34 are not `DONE` until fixture evidence exists; 7.2 and 7.3 remain deferred unless independently executed.
14. No live DB access, OpenCode shutdown, rollback, `VACUUM`, backup deletion, commit, or push occurs during this remediation track without separate explicit authorization.

## Risks and Mitigations

- **TOCTOU after handle probe:** repeat process/handle/hash gates at every boundary, use fail-on-open-handle primitives, detect unknown/new files, and limit claims to tested detectable conditions.
- **Power loss cannot be fully proven:** durably close/flush evidence where supported, reconcile unresolved journals from actual hashes/presence, and avoid any claim of controller-level power-loss atomicity.
- **Rollback source has committed WAL state:** materialize the coordinated source set through SQLite into a standalone staged DB before activation.
- **Recovery operation also encounters a lock:** preserve all artifacts, mark the journal manual-intervention-required, and fail without cleanup.
- **Process-name false positives:** classify using bounded metadata, but fail closed when classification is unavailable rather than guessing safe.
- **Documentation overclaim:** evidence matrix states must be derived from executed fixture tests, with live rehearsal tracked separately.

## Handoff

Implementation belongs to the Build agent. The Build agent must begin with RED disposable-fixture tests and must not run any script against `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`.
