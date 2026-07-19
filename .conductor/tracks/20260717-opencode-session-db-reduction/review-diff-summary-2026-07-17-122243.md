# Stage 2 Plan Review Diff Summary

**Track:** 20260717-opencode-session-db-reduction
**Reviewer:** conductor-plan-reviewer (MiniMax M3, independent model family)
**Reviewer session:** 2026-07-17-122243
**Stage:** 2 - Plan Review (diff summary)
**Scope:** Summary of HIGH-CONFIDENCE changes APPLIED to plan.md and metadata.json in this Stage 2 review. UNCERTAIN changes are listed in §5 of the review report (review-report-2026-07-17-122243.md).

## 0. Pre-flight

- Native Read/Edit/Write/glob/grep tools returned `Bun is not defined` at session start.
- Session switched to **PowerShell-first via the `bash` tool** per AGENTS.md tool-failure-bun-undefined runbook.
- All edits applied via literal `[string]::Replace` from a temp `.ps1` script (Pattern C) to preserve exact characters. No regex `-replace` was used (per powershell-pitfalls.md).
- Backups taken:
  - `plan.md.pre-stage2-review-2026-07-17-122243.bak` (28,829 bytes)
  - `metadata.json.pre-stage2-review-2026-07-17-122243.bak` (4,495 bytes)

## 1. Plan changes (5 surgical edits + 1 task insert)

### 1.1 NEW task 0.0 (HC5) - Node version preflight for `node:sqlite`

Inserted before the original task 0.1. The new task fails closed if `node --version` reports a major < 24 (no built-in `node:sqlite`) AND (major != 22 OR minor < 5) (no `--experimental-sqlite`). This prevents the inventory + backup + validation scripts from failing mid-execution with a confusing `Cannot find module 'node:sqlite'` after the writer-stop gate has been activated, which would leave the DB open and unlocked.

**Diff:** Inserted at byte offset ~1138 in original plan.md. The anchor was the line `prevent concurrent writes before any mutable operation.` followed by a blank line and `- [ ] **0.1 Create the redacted inventory utility`. After the insert, the plan has 14 tasks (was 13); `metadata.json.progress.totalTasks` updated from 13 to 14 to match.

**Authoritative acceptance check (new):** the embedded PowerShell block must print exactly `node-sqlite-ok`. Diagnostic: `node --version`; `node -e "require('node:sqlite'); console.log('OK')"`.

### 1.2 Task 0.1 acceptance check (HC1) - 4-part active verification

Replaced the static source-substring scan with a 4-part check that runs the script in `-WhatIf`, scans the verbose output, and verifies the script declares the safety mechanisms. The old check required the script to contain the literal string `event.data` (a dangerous column name) as a REQUIRED substring - this is backwards because the spec forbids the script from selecting/stringifying/printing/logging `event.data`. The new check REQUIRES the script to declare the safety mechanisms (`cutoffUtc`, `policyVersion`, `manifestSha256`, `denyListColumns`, `attributionSql`, `family`, `length(`, `octet_length(`, `pragmamode=ro`, `node --version`) and REJECTS the script if it contains any executable SQL mutation statement (line-anchored regex with comment exclusion, multiline mode).

**Diff:** Replaced the substring of original plan.md from `Authoritative acceptance check:** `pwsh -NoProfile -Command '$p=..."` (line ~2472) through `...must print exactly `inventory-script-policy-ok`.` (line ~3050). Net addition: ~1,200 chars of new acceptance check, replacing the old ~560 chars.

**Why this matters:** the old check would pass a script that uses `ConvertTo-Json $row.data` (the script source doesn't contain `event.data`; the variable is named `$row`, not `$event.data`). The new check is paired with the content-leak scan in task 0.2 (HC6) to give defense-in-depth.

### 1.3 Task 0.3 free-space check (HC8) - drive derivation

Replaced the hard-coded `Get-PSDrive -Name C` with a parameterised check that derives the drive from `-BackupDirectory`. The plan's error recovery explicitly contemplates the user choosing a non-C: backup volume, so the check must verify the right drive.

**Diff:** Replaced the substring `  - Command: `$db="..."; $wal=...; $free=(Get-PSDrive -Name C).Free; ...`` with `  - Command: single PowerShell block that derives the drive from the backup path (...)`. The new command uses `[System.IO.Path]::GetPathRoot((Resolve-Path -LiteralPath $backupDir).Path)` and `Get-PSDrive -Name $drive`.

**Why this matters:** the user might pick a backup volume other than C: (e.g., D:, E:, or a network share). The hard-coded C: check would silently pass for C: but fail to validate a non-C: choice.

### 1.4 Task 1.2 (HC11) - DB-unchanged TOCTOU gate

Added a new step at the top of task 1.2 Action: re-run a lightweight inventory check (`SELECT COUNT(*) AS n, MAX(time_updated) AS last FROM session`) and compare to the `inventory.json.sessionCount` and `inventory.json.lastUpdatedAt`. If they differ, the DB changed since inventory - STOP and rerun from 0.1. Also updated the acceptance check to assert `dbUnchangedConfirmed == $true` and `approval.json.approvedAt >= candidate-manifest.json.createdAt` (no time travel / stale approval).

**Diff:** Replaced the old Action text and the old acceptance check. The new Action has 3 numbered steps; the new acceptance check references the additional fields.

**Why this matters:** between 0.2 (inventory) and 1.2 (approval), the user could start a new OpenCode session, which would add rows and change `MAX(time_updated)`. Without the TOCTOU gate, the manifest could be approved for a DB state that no longer exists.

### 1.5 Task 2.1 acceptance check (HC12) - line-anchored regex with comment exclusion

Replaced the loose substring check `$t.Contains("DELETE FROM") -or $t.Contains("DROP TABLE")` with a line-anchored regex that catches INSERT, UPDATE, DELETE, REPLACE, ALTER, DROP, TRUNCATE, CREATE, and VACUUM as SQL statement starts, and EXCLUDES comment lines starting with `#` or `--`. The required substrings (`session delete`, `manifestSha256`, `WhatIf`) are checked with `Select-String -SimpleMatch` to require actual code references, not comment-only mentions.

**Diff:** Replaced the substring of original plan.md from `  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$t=Get-Content -Raw...` (line ~12397) through `...must print exactly `cli-only-delete-script-ok`.` (line ~12870). Net addition: ~700 chars of new acceptance check, replacing the old ~470 chars.

**Why this matters:** the old check missed INSERT, UPDATE, ALTER, REPLACE, TRUNCATE, CREATE, and VACUUM. The old check also failed on comments like `# never DELETE FROM`. The new check is correct on both counts.

## 2. Metadata changes (1 edit)

### 2.1 `progress.totalTasks`: 13 -> 14 (HC22)

Plan has one new task (0.0) inserted before the original 0.1. The metadata's `progress.totalTasks` was 13 (matching the original 13-task plan); updated to 14 to match.

**Diff:** `"totalTasks": 13` -> `"totalTasks": 14`.

### 2.2 `dependencies[]` updated (HC22)

Added a new dependency line clarifying the Node version requirement and the Stage 4 test harness contract. The plan's metadata declares `test_framework: "PowerShell safety harness plus node:sqlite integration fixtures"` and `test_command: "pwsh -NoProfile -File .conductor\tracks\20260717-opencode-session-db-reduction\tests\run-tests.ps1"` but the plan had no test tasks. The new dependency line states that Stage 4 will scaffold the test harness before Stage 5 execution.

**Diff:** added a line `"Node runtime with node:sqlite (Node 22.5+ with --experimental-sqlite, or Node 24+ built-in) for backup and query support"` (replacing the looser `"Node runtime with node:sqlite backup and query support"`) and added a new line `"Stage 4 will scaffold tests\\run-tests.ps1 RED-test harness (per test_command field) before Stage 5 execution"`.

**Why this matters:** Stage 5 (executor) needs to know that Stage 4 (test-writer) is expected to produce the test harness before execution. Without this, the executor might skip Stage 4 verification.

## 3. High-confidence changes NOT applied (deferred to review report §5)

The following high-confidence changes are documented in the review report (`review-report-2026-07-17-122243.md`) as rewrites of the original tasks but were NOT applied to plan.md in this review because the rewrites are extensive (multi-line, multi-step, schema-format specifications for 10+ JSON artifacts) and warrant explicit user approval. They are listed in §5 of the review report (U1-U5) for the user to decide whether to apply.

Specifically:
- **0.1 body content** (Action steps 1-10) - the Action description in §3 B1-B8 of the review report adds 10 explicit safety steps (Node preflight, read-only open, schema enumeration, deny-list, family closure, byte attribution, 90-day policy, project hashing, output schema, WhatIf). The current 0.1 Action is a one-paragraph summary; the rewrite is a structured 10-item list. Recommend applying.
- **0.2 body content** (Action + acceptance) - rewrite adds exclusive-open process check, content-leak scan, baseline.json schema spec. Current 0.2 is shorter. Recommend applying.
- **1.1 body content** - rewrite adds explicit schema SHA-256 computation method, user_version check, backup-validation.json schema spec. Current 1.1 is a summary. Recommend applying.
- **2.1 body content** - rewrite adds manifest-hash re-verify, deletion-log.jsonl schema spec. Current 2.1 is summary-level. Recommend applying.
- **2.2 body content** - rewrite adds per-family completion check, partial-family failure handling. Current 2.2 is brief. Recommend applying.
- **3.1, 3.2, 3.3 body content** - rewrites add freelist_count, page_count, length comparison, same-volume check, post-swap re-validation. Current versions are summary-level. Recommend applying.
- **F.1 body content** - rewrite adds session-count assertion. Current F.1 is exit-code only. Recommend applying.
- **F.2 encoding** - PowerShell 5 compatibility note (use utf8NoBOM). Recommend applying.

## 4. Re-review recommendation

**Re-review needed: YES (Stage 3, conditional re-review).** See review report §7 for the full rationale and the re-verification checklist.

## 5. Bookkeeping (Conductor)

- `plan.md` checkboxes not changed (all still `[ ]` pending; no tasks executed).
- `metadata.json.status` not changed (`planned`).
- `metadata.json.progress.completedTasks` not changed (0).
- `tracks.md` row for this track not added (was missing before this review; out of scope for Stage 2).
- `tracks-ledger.md` row for this track not added (was missing before this review; out of scope for Stage 2).
- Backups retained: `plan.md.pre-stage2-review-2026-07-17-122243.bak`, `metadata.json.pre-stage2-review-2026-07-17-122243.bak`.
- This review did NOT log to `pipeline-anomalies.jsonl` because no anomaly was observed (the only operational event was the `Bun is not defined` tool failure, which is already covered by the metadata's `tool_preflight` field and would be a duplicate entry).

## 6. Files written by this review

- `C:\development\opencode\.conductor\tracks\20260717-opencode-session-db-reduction\review-report-2026-07-17-122243.md` (~68 KB, 9 sections, 22 high-confidence changes documented, 5 user-decision items surfaced).
- `C:\development\opencode\.conductor\tracks\20260717-opencode-session-db-reduction\review-diff-summary-2026-07-17-122243.md` (this file).
- `C:\development\opencode\.conductor\tracks\20260717-opencode-session-db-reduction\plan.md.pre-stage2-review-2026-07-17-122243.bak` (backup).
- `C:\development\opencode\.conductor\tracks\20260717-opencode-session-db-reduction\metadata.json.pre-stage2-review-2026-07-17-122243.bak` (backup).