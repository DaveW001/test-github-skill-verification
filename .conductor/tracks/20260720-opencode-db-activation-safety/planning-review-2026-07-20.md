# Planning Review — 2026-07-20

## Verdict

**ACCEPTED for Build handoff.**

## Review History

The first independent review rejected the initial draft because writer exclusion, WAL materialization, Windows replacement, crash reconciliation, raw-versus-logical verification, `-WhatIf`, and power-loss claims were underspecified.

The plan was revised to require:

- bounded rather than absolute writer/handle guarantees;
- repeated process, exclusive-handle, presence, length, and hash checks at each transition;
- a named mutex and literal zero-write `-WhatIf` behavior;
- private-copy SQLite backup materialization with a committed, uncheckpointed WAL sentinel;
- invalid WAL/SHM fixture coverage;
- same-volume `[System.IO.File]::Replace` with a retained displaced-main backup;
- separate raw hash evidence and private-copy logical verification;
- a hash/presence-driven crash/restart reconciliation table;
- no controller-level power-loss guarantee;
- `-Force` limited to human confirmation only;
- parser checks that explicitly fail on returned errors.

The second independent review found no critical, major, or minor planning issues and approved the artifacts as implementation-ready.

## Immediate Evidence Correction

Before Build handoff:

- parent acceptance rows 33 and 34 were changed from `DONE` to `BLOCKED`;
- parent metadata, `tracks.md`, and `tracks-ledger.md` were changed to `blocked-remediation-planned`;
- the parent terminal verdict was explicitly superseded by `validation-report-20260720-200653Z.md`;
- tasks 7.2 and 7.3 remain deferred.

## Safety Boundary

The Build agent must begin with RED disposable-fixture tests. It must not access the live OpenCode database, terminate OpenCode/bun processes, execute rollback or `VACUUM`, delete recovery artifacts, commit, or push without separate explicit authorization.
