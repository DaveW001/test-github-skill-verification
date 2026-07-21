# Stage 8 Validation Blockers

**Track:** `20260717-opencode-event-log-compaction`  
**Generated:** 20260720-200653Z  
**Reason:** Material issue remains after the single permitted remediation/re-validation pass.

## Exact Blockers

1. `C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor\scripts\Activate-CompactedDb.ps1` is not uniformly fail closed: forward activation offers `Stop-Process -Force` and continues after an interactive confirmation instead of refusing while OpenCode/writer processes are active.
2. The script does not explicitly detect open file handles/write locks and has no recovery transaction/try-catch for a failure partway through the DB/WAL/SHM move sequence. Process-name detection alone does not prove the spec's open-handle criterion.
3. `acceptance-evidence-matrix-2026-07-20.md` rows 33 and 34 are marked `[x] DONE`, overclaiming fail-closed activation and open-handle/partial-rename guarantees. They must be implemented and tested, or labeled PARTIAL/DEFERRED with precise limits.
4. Current rollback/runbook wording must distinguish verified rollback process gating and coordinated set handling from the still-unverified open-handle and partial-move guarantees.

## Capped-Pass Stop

No second remediation loop is authorized. Preserve `closed-with-deferred-followups` bookkeeping as an intended target state, but do not issue terminal closeout until these blockers are resolved and independently validated in a new operator-authorized cycle.
