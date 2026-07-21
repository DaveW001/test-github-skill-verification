# Audit Correction Addendum: Stage 8 Remediation

**Track:** `20260717-opencode-event-log-compaction`
**Generated:** 2026-07-20T16:04:24Z
**Source:** Stage 8 remediation pass addressing validation-report-20260720-195430Z.md findings

## Corrections Applied

### 1. Script Count (9→10)

**Finding:** Current skill has 10 PowerShell scripts; test-cases.md and SKILL.md file inventory said 9.
**Correction:** Updated test-cases.md TC-06 to say "All 10 scripts". Updated SKILL.md file inventory to list all 10 scripts with purposes. Added reconciliation notes explaining the 9→10 history.
**Historical claims preserved:** Plan.md task checkboxes and execution logs retain original "9/9" claims where already reconciled (task 4.8 has explicit 2026-07-20 reconciliation note).

### 2. Ledger Event-Count Disclaimer

**Finding:** tracks-ledger.md published "25 batches / 242,484 events compacted" as current fact without disclaimer.
**Correction:** Updated to "25 batches / 242,484 events (user-reported operational total; not fully machine-verifiable from parseable artifacts; authoritative artifact-specific counts: 9 batches/89,223 events + 14 batches/133,259 events)".
**Already handled:** metadata.json phase6.notes and next-steps-runbook.md already had appropriate disclaimers.

### 3. Stage 9 Artifact Supersession

**Finding:** doc-update-log-2026-07-17-202017.md and post-doc-validation-2026-07-17-202017.md retained pre-live claims without supersession notes.
**Correction:** Appended dated supersession notes to both artifacts. Notes document the pre-live state, point to 2026-07-20 reconciliation artifacts, and clarify that historical body claims are preserved as accurate pre-live records.

### 4. Rollback Script Safety

**Finding:** Activate-CompactedDb.ps1 -Rollback lacked process detection, coordinated file-set handling, and post-restore validation.
**Correction:** Hardened rollback section with:
- OpenCode/bun process detection (fails closed if any found)
- Coordinated DB/WAL/SHM file-set handling
- PRAGMA quick_check verification after restore
- Displaced-files preservation in timestamped emergency directory
- Updated help text documenting all behavior
**Syntax validation:** 10/10 scripts pass PSParser tokenization after changes.

### 5. Acceptance-Evidence Matrix

**Finding:** No comprehensive mapping of spec acceptance criteria to evidence status.
**Correction:** Created acceptance-evidence-matrix-2026-07-20.md mapping all 42 criteria:
- 36 DONE with evidence
- 3 DEVIATION (documented)
- 1 PARTIAL (timed out)
- 2 DEFERRED (7.2, 7.3 - explicitly NOT claimed complete)
**Key distinction:** Code tests cover implementation semantics; live application/rollback evidence is deferred.

## Verification

All corrections were verified with:
- PowerShell PSParser tokenization (10/10 valid)
- quick_validate.py (Skill is valid!)
- metadata.json JSON parsing and consistency check
- Plan checkbox count verification (40 [x] / 2 [~] / 42 total)
- tracks.md and tracks-ledger.md status/count consistency
- Privacy scan (0 findings)
- git diff --check (CLEAN)

## No Rollback DBs Touched

This remediation pass did not access, modify, or delete any rollback database files. All changes were documentation, bookkeeping, or script help/safety-comment updates.
