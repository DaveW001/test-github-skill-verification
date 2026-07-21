# Audit Correction Addendum: 2026-07-20T20:00:00Z

## Purpose
Second dated addendum to address findings from `validation-report-20260720-190009Z.md` (Stage 7 validation, 2026-07-20). Classify evidence gaps, add supersession notes to historical logs, and ensure no current bookkeeping claims unsupported safety gates as passed.

**Supersedes:** `audit-correction-2026-07-20.md` for scope of 7.2/7.3 classification and compaction-result.json handling. The prior audit correction remains valid for the corrections it applied; this addendum extends it.

**Validator report citation:** `validation-report-20260720-190009Z.md` -- verdict "Not ready to close."

---

## 1. Classification of 7.2 and 7.3: Evidence Gaps / Deferred, NOT Passed

Tasks 7.2 and 7.3 are **evidence gaps**, not passed gates. They are deferred pending specific evidence that does not exist in the current artifact set.

### 7.2 - Post-swap application smoke tests
- **Status:** Evidence gap / deferred.
- **What exists:** `skill_find` and `skill_use` confirmed working post-restart. OpenCode is running and functional (DB counts increasing).
- **What does NOT exist:** Representative export/read/resume/new-session smoke test artifacts. No script or log demonstrates a session list query, a representative export, a read-back, a resume, or creation of a new test session/message after the swap.
- **Why not passed:** The validator report (finding 6) explicitly states: "There is no evidence of representative export/read/resume/new-session testing after restart." skill_find/skill_use alone is insufficient for the plan's acceptance criteria.
- **Required evidence:** A bounded script or log showing at least one of: session list, representative export, read-back, resume, or new-session creation post-swap, without exposing content in logs.

### 7.3 - Rollback file/state checks and restoration rehearsal
- **Status:** Evidence gap / deferred.
- **What exists:** Rollback artifact files confirmed to exist: `pre-compaction-20260718-135520` (~24.77 GB) and `pre-compaction-active-20260720-125457` (~24.77 GB). Both retained per plan.
- **What does NOT exist:** A restoration rehearsal. No script or log demonstrates stopping writers, moving the active DB aside, restoring the rollback set, reopening, and validating.
- **Why not passed:** The validator report (finding 6) explicitly states: "The full `phase6-runner validate` timeout is correctly recorded as a timeout, not a pass." The file-existence check is necessary but not sufficient for the plan's "rehearse rollback" acceptance criterion.
- **Required evidence:** A bounded restoration rehearsal with writers stopped, or an explicit waiver with rationale.

---

## 2. Distinguishing Targeted PRAGMA quick_check from Full phase6-runner Validation

Current bookkeeping references `quick_check: ok` in the `phase6` metadata block. This is accurate but requires scope clarification:

- **Targeted PRAGMA quick_check:** A read-only `PRAGMA quick_check` and `PRAGMA journal_mode`/`PRAGMA user_version` query run against the live DB after restart. This passed (ok, wal, 0). It detects basic SQLite structural corruption. This is what the metadata `phase6.quickCheck: "ok"` represents.
- **Full phase6-runner validation:** The `phase6-runner.ts validate` command, which checks projection integrity, checkpoint/tail reconstruction, replay equivalence, sequence invariants, and append safety. This **timed out** during post-restart validation and was NOT completed. The execution log (`execution-log-2026-07-20-reconciliation.md`) and validator report both record this as a timeout, not a pass.

**Current bookkeeping does NOT claim the full phase6-runner validation passed.** The `closeout_verdict` in metadata.json correctly notes "phase6-runner full post-restart validate timed out; targeted read-only check passed." This addendum confirms that characterization is accurate and not misleading.

---

## 3. compaction-result.json: Non-Authoritative

**File:** `C:\development\opencode-upstream\compaction-result.json`

The validator report (finding 4) states: "compaction-result.json is not valid whole-file JSON: it starts with plaintext log output and contains a trailing JSON fragment. It cannot be treated as a machine-readable JSON artifact without a corrected copy or explicit format relabeling."

**Current bookkeeping treatment:**
- The file is **non-authoritative** for machine-readable evidence. It contains a trailing JSON fragment with valid fields (`status`, `cutoffDays`, `candidatesApplied`, etc.) but the file as a whole is not parseable JSON.
- **Authoritative batch artifacts:** `batch-compaction-results.json` (9 batches, 89,223 events, 14-day) and `batch-compaction-7day-results.json` (14 batches, 133,259 events, 7-day) are valid JSON and are the authoritative machine-readable evidence.
- The single-run 10,001-event batch evidenced in `compaction-result.json` is corroborated by the plaintext log portion but cannot be independently verified from a machine-readable artifact.
- **Do not claim JSON parse success for compaction-result.json.** Historical references to it in `execution-log-2026-07-20-reconciliation.md` and `audit-correction-2026-07-20.md` correctly note it as an artifact but should not be read as claiming whole-file JSON validity.

---

## 4. Supersession Notes for Historical Logs

### execution-log-2026-07-18-phase6.md
**Status:** Historical record, superseded for safety-gate claims.

This log states "exact manifest hash approval" and "no writer shutdown needed." These statements conflict with the reconciliation and validator findings:
- Exact manifest hash continuity was NOT maintained across separate dry-run/apply scripts due to active writes (reconciliation deviation 3).
- "No writer shutdown needed" is accurate for the logical compaction phase (WAL concurrency proven safe) but the log does not distinguish this from the physical swap requirement (which DOES require stopped writers). The validator report (finding 2) notes this ambiguity.

**For current bookkeeping, refer to:**
- `execution-log-2026-07-20-reconciliation.md` (reconciled deviations)
- `audit-correction-2026-07-20.md` (prior corrections)
- This addendum (evidence gap classification)
- `validation-report-20260720-190009Z.md` (validator findings)

The historical log is preserved as-is for audit trail integrity. Do not edit it.

### audit-correction-2026-07-18T001500Z.md
**Status:** Historical correction, superseded for progress counts.

This earlier correction set `completedTasks=25` and `percentage=59.5%`. The 2026-07-20 reconciliation re-checked tasks 4.8 and 5.4-5.7 based on post-restart evidence and synthetic-fixture equivalence, restoring them to `[x]`. Current state: 40/42 (95.2%). The earlier correction remains valid for the overclaims it identified; the reconciliation updated the counts based on new evidence.

---

## 5. Current Accurate State (Post-Addendum)

| Item | Status | Source |
|------|--------|--------|
| Plan checkboxes | 40 `[x]` / 2 `[ ]` (7.2, 7.3) / 42 total | plan.md verified |
| metadata.json completedTasks | 40 | metadata.json |
| metadata.json status | reconciled-post-restart | metadata.json |
| metadata.json progress | 95.2 | metadata.json |
| tracks.md row | reconciled-post-restart, 2026-07-20 (40/42) | tracks.md verified |
| tracks-ledger.md entry | reconciled-post-restart, 40/42, deviations noted | tracks-ledger.md verified |
| 7.2 | Evidence gap / deferred | This addendum |
| 7.3 | Evidence gap / deferred | This addendum |
| phase6-runner full validation | Timed out (NOT passed) | Reconciliation + validator |
| PRAGMA quick_check | ok (targeted, not full validation) | Reconciliation |
| compaction-result.json | Non-authoritative (not valid whole-file JSON) | Validator finding 4 |
| batch-compaction-results.json | Authoritative (9 batches, valid JSON) | Validator |
| batch-compaction-7day-results.json | Authoritative (14 batches, valid JSON) | Validator |
| 4.8 skill activation | Complete (post-restart skill_find/skill_use) | Reconciliation |
| Rollback artifacts | Exist but NOT rehearsed | This addendum |
| Application smoke tests | NOT demonstrated | This addendum |

---

## 6. Blockers / Follow-ups (Current)

1. **FOLLOW-UP (7.2):** Post-swap application smoke tests not demonstrated (export/read/resume/new-session). Evidence gap.
2. **FOLLOW-UP (7.3):** Rollback restoration rehearsal not executed. Artifacts retained. Evidence gap.
3. **FOLLOW-UP:** Exact manifest hash continuity not maintained across separate dry-run/apply scripts due to active writes.
4. **FOLLOW-UP:** Live apply bypassed reviewed skill orchestrator gates (writer/projection checks) for performance.
5. **FOLLOW-UP:** compaction-result.json is not valid whole-file JSON; single-run 10,001-event batch not independently verifiable from machine-readable artifact.
6. **FOLLOW-UP:** Full phase6-runner post-restart validation timed out; targeted PRAGMA check passed but does not cover projection/replay/append invariants.

---

## Files Changed (This Addendum)

- `C:\development\opencode\.conductor\tracks\20260717-opencode-event-log-compaction\audit-correction-addendum-2026-07-20T200000Z.md` (this file)
