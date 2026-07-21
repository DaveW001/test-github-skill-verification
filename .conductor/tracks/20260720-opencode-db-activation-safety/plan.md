# Plan: OpenCode Database Activation Safety Remediation

## Status

  **State:** executed
  **Parent track:** `20260717 opencode event log compaction`
  **Progress:** 22/22
  **Safety boundary:** disposable fixtures only; no live OpenCode DB mutation

## Phase 0   Reconcile the Blocked State

  [x] **0.1 Correct the blocked state evidence before implementation.** Linked `validation report 20260720 200653Z.md` and `validation blockers 20260720 200653Z.md`; downgraded parent matrix rows 33/34 from `DONE` to `BLOCKED`; parent metadata/index/ledger now say `blocked remediation planned`. Promotion is allowed only from executed fixture evidence.
  [x] **0.2 Inventory every mutation entry point.** Trace `Activate CompactedDb.ps1`, `Switch ValidatedDatabase.ps1`, and `Restore OpenCodeDatabase.ps1`; identify every process, handle, copy, move, replace, remove, verification, and output branch.
  [x] **0.3 Freeze live operations.** Add a remediation notice to current skill/runbook surfaces: do not use activation or rollback against the live DB until this track is independently validated. Preserve both retained backups.

## Phase 1   Write RED Safety Tests

  [x] **1.1 Build disposable file set fixtures.** Create an intentional DB only backup; a valid DB+WAL set containing a committed, deliberately uncheckpointed sentinel transaction; valid WAL without SHM; DB+WAL+SHM; orphan SHM; stale/mismatched WAL; and truncated/corrupt WAL. Record raw hashes and assert fixtures never resolve to the live DB directory.
  [x] **1.2 Test bounded fail closed writer behavior.** Mock OpenCode and relevant bun processes, inaccessible metadata for candidate processes, inaccessible unrelated processes, false positive names, a writer appearing after initial preflight, and no writer cases. Assert detected/unknown candidate writers exit nonzero with zero false success and no `Stop Process` call.
  [x] **1.3 Test named mutex and handle refusal.** Hold the named maintenance mutex and then independently lock DB, WAL, and SHM, including locks acquired after initial preflight. Each case must refuse or recover and preserve the complete original hash/presence map.
  [x] **1.4 Test every partial activation transition.** Inject failures after recovery snapshot, WAL displacement, SHM displacement, main replacement, and activated DB verification. Assert byte for byte restoration or the explicit preserved artifact manual intervention state.
  [x] **1.5 Test every partial restoration transition.** Prove the uncheckpointed WAL sentinel survives private copy SQLite backup materialization. Exercise valid WAL without SHM, DB only backups, orphan SHM, stale/mismatched WAL, truncated/corrupt WAL, failed source materialization, failed replacement, and failed post restore verification.
  [x] **1.6 Test success, restart reconciliation, and dry run contracts.** Simulate child process termination at each crash boundary and reconcile using actual hashes/presence when the journal leads or lags the filesystem. Assert successful activation/restoration, literal ` WhatIf` zero mutation, no stale active sidecars, retained evidence, atomically published committed journal, and no premature success output.

## Phase 2   Implement the Canonical Safety Path

  [x] **2.1 Remove force kill behavior.** Delete the forward path `Read Host "Force kill?"` and `Stop Process  Force` behavior. Writer detection must only report bounded process metadata and exit nonzero.
  [x] **2.2 Make `Activate CompactedDb.ps1` a thin wrapper.** Keep bounded source discovery/confirmation, then delegate forward activation to `Switch ValidatedDatabase.ps1` and rollback to `Restore OpenCodeDatabase.ps1`; remove direct active DB/WAL/SHM mutation.
  [x] **2.3 Add bounded writer, mutex, and repeated handle gates.** Hold a named mutex; classify only candidate OpenCode/bun processes; repeat process inspection, exclusive probes, and expected presence/length/hash checks before every sidecar move and main replacement; fail or recover on any change. Document the residual non cooperating writer race.
  [x] **2.4 Add verified staging, raw recovery snapshots, and private verification copies.** Preserve/hash raw DB/WAL/SHM without opening it, validate only a separate canonical name copy, stage incoming DB in the active directory, and publish privacy safe journal records after durable close/flush where supported.
  [x] **2.5 Implement the concrete Windows replacement and reconciliation protocol.** Prohibit copy overwrite of the canonical DB. Displace sidecars under the journal, then use same volume `[System.IO.File]::Replace` for the staged main with a retained displaced main backup. On failure or unresolved startup journal, reconcile actual hashes/presence against original and incoming maps; restore/verify or enter the explicit manual intervention state.
  [x] **2.6 Implement coordinated rollback materialization.** Copy rollback DB/WAL/optional SHM into a private canonical name directory, use pinned SQLite backup API/CLI `.backup` to create a standalone DB that includes committed WAL frames, verify sentinel/schema/`quick_check`, then invoke the canonical switch protocol. Treat SHM as reconstructible coordination state, reject invalid source combinations, and never open retained originals in place.

## Phase 3   Validate the Implementation

  [x] **3.1 Run parser and static safety checks.** Initialize parser token/error variables for each `.ps1`, parse it, and fail on any returned error. Verify `Activate CompactedDb.ps1` contains no `Stop Process` and no direct active set mutation; every write is guarded by `ShouldProcess`; ` Force` cannot bypass safety; and mutation entry points support ` WhatIf`.
  [x] **3.2 Run the complete disposable fixture suite.** Require zero failures for process gates, lock probes, every injected partial transition, recovery verification, successful activation/restoration, and ` WhatIf`.
  [x] **3.3 Run structural and privacy validation.** Run skill `quick_validate.py`, JSON parsing, sensitive pattern scans, and `git diff   check`; confirm no test or output contains payloads, credentials, session IDs, or raw command lines.

## Phase 4   Correct Evidence and Closeout

  [x] **4.1 Update operational documentation.** Synchronize `SKILL.md`, `references/rollback.md`, `references/safety gates.md`, test cases, and `next steps runbook.md` with the actual gates, journal states, recovery limits, and manual intervention behavior.
  [x] **4.2 Correct the parent acceptance matrix.** Rows 33/34 are now `[!] PARTIAL` based on executed disposable-fixture evidence only; live application smoke and live rollback rehearsal (7.2/7.3) remain deferred.
  [x] **4.3 Record execution and test evidence.** Create dated execution, test, and audit correction logs with exact commands, fixture only paths, fault points, pass/fail counts, deviations, and confirmation that live files were untouched.
  [x] **4.4 Independently validate and reconcile ledgers.** Obtain a fresh independent closeout verdict; upsert both track rows in `tracks.md` and `tracks ledger.md`; synchronize metadata and parent blocker status without rewriting historical reports.

## Verification Commands

The Build agent must finalize exact commands after confirming the local test harness. At minimum:

```powershell
# Parse every skill PowerShell script.
Get ChildItem <skill>\scripts\*.ps1 | ForEach Object {
  $tokens = $null
  $errors = $null
  [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
  if ($errors.Count  gt 0) { throw "Parser errors in $($_.FullName): $($errors.Message  join '; ')" }
}

# Run the dedicated disposable fixture Pester suite.
Invoke Pester <skill>\tests\DatabaseActivationSafety.Tests.ps1  EnableExit

# Structural validation and repository hygiene.
python <skill creator>\scripts\quick_validate.py <skill>
git diff   check
```

No verification command may use the live OpenCode DB path.

## Stop Rules

  Stop immediately if a test resolves to the live DB directory.
  Stop if process inspection is unavailable and the implementation would guess that no writer exists.
  Stop if any fixture failure leaves a state not explained by its journal.
  Stop if recovery artifacts would be deleted or overwritten.
  Stop after the first failed independent validation; return to implementation with the exact evidence rather than weakening acceptance criteria.




