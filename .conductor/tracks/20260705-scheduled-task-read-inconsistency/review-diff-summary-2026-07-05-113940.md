# Review Diff Summary - Scheduled Task Read Inconsistency

- **Track:** `20260705-scheduled-task-read-inconsistency`
- **Reviewer:** `opencode-go/minimax-m3` (Stage 2)
- **Review timestamp:** 2026-07-05-113940
- **Plan edited in place:** `C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\plan.md`
- **Plan backup:** `C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\plan.md.review-backup-2026-07-05-113940`

## High-Confidence Edits Applied (7)

All edits were applied via literal Python string replacement with unique anchors. Before/after content captured below; full pre-edit content preserved in the backup file above.

### Edit 1 - Task 0.2: try/catch wrapper for gsudo acceptance

**Why:** If gsudo is missing, elevation is silently denied, or the inner pwsh emits an error instead of JSON, `ConvertFrom-Json` throws and the acceptance check aborts with an unhandled exception rather than returning `$false`. The wrap lets the executor see a clean False and stop on blocker.

**Diff (logical):**
```diff
   - Authoritative acceptance check:
     ```powershell
-    $json = @''
+    $raw = @''
     <paste command JSON output here>
-    '@ | ConvertFrom-Json
-    ($json.GsudoAvailable -eq $true) -and ($json.IsAdmin -eq $true)
+    '@
+    try {
+      $json = $raw | ConvertFrom-Json -ErrorAction Stop
+      ($json.GsudoAvailable -eq $true) -and ($json.IsAdmin -eq $true)
+    } catch {
+      $false
+    }
     ```
-    Expected output: `True`.
+    Expected output: `True` (returns `$false` if gsudo is missing, elevation is denied, or the inner pwsh emits non-JSON output).
```

### Edit 2 - Task 1.3: BlobKey consistency check

**Why:** Old check verified `BlobKey.Contains(''TaskCache\Tasks\'')` but did not verify that `BlobKey` actually equals `'HKLM:\...\Tasks\' + $json.Id`. A logic bug in the inner script could return a non-matching BlobKey and still pass. Strengthened to assert exact `BlobKey == Tasks\ + Id` consistency.

**Diff (logical):**
```diff
-    ... ([string]$json.BlobKey).Contains(''TaskCache\Tasks\'')
+    ... ([string]$json.BlobKey).Contains(''TaskCache\Tasks\'') -and ([string]$json.BlobKey -eq (''HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks\'' + $json.Id))
```

### Edit 3 - Task 2.1: require placeholders to be replaced in root-cause-evidence.md

**Why:** The old acceptance check verified only that the four required headings and one bullet were present. Dry-run confirmed the check passed even with all `<True/False>`, `<GUID or blank>`, `<bytes>`, etc. placeholders still in the file. The executor could "succeed" without doing the substantive work. Added a `(-not $placeholdersLeft)` check that lists every placeholder token.

**Diff (logical):**
```diff
     $text = Get-Content -Raw -LiteralPath ''...root-cause-evidence.md''
+    $placeholdersLeft = $text.Contains(''<True/False>'') -or $text.Contains(''<GUID or blank>'') -or $text.Contains(''<path or blank>'') -or $text.Contains(''<number>'') -or $text.Contains(''<schema or blank>'') -or $text.Contains(''<OK/ERR details>'') -or $text.Contains(''<bytes>'') -or $text.Contains(''<OK/ERR summary>'')
+    (-not $placeholdersLeft) -and $text.Contains(''## Elevated TaskCache Evidence'') -and $text.Contains(''- Tasks GUID blob exists:'') -and $text.Contains(''## Interpretation'') -and $text.Contains(''- Recommended remediation:'')
     ```
-    Expected output: `True`.
+    Expected output: `True`. The check fails if any `<...>` placeholder is left in the file; every value must be the actual elevated evidence (or `UNKNOWN - <reason>`).
```

### Edit 4 - Task 3.1: require Option 1/2/3 placeholder to be filled in

**Why:** Same template-vs-values gap. The `<Option 1/2/3>` placeholder in the approval text is decision-relevant. Added `(-not $text.Contains(''<Option 1/2/3>''))` and a `$chosenFilled` check that requires the actual option text.

**Diff (logical):**
```diff
     $text = Get-Content -Raw -LiteralPath $log
+    $chosenFilled = ($text.Contains(''Chosen remediation: Option 1'') -or $text.Contains(''Chosen remediation: Option 2'') -or $text.Contains(''Chosen remediation: Option 3''))
-    $text.Contains(''Exact registration-touch command proposed: ...'') -and ($text.Contains(''User approval decision: APPROVED'') -or $text.Contains(''User approval decision: DENIED''))
+    $text.Contains(''Exact registration-touch command proposed: ...'') -and $chosenFilled -and (-not $text.Contains(''<Option 1/2/3>'')) -and ($text.Contains(''User approval decision: APPROVED'') -or $text.Contains(''User approval decision: DENIED''))
```

### Edit 5 - Task 3.4: require reason placeholder to be filled in

**Why:** The `<approval denied / approval ambiguous / root cause uncertain / risk exceeds benefit>` placeholder is decision-relevant. Added `(-not $text.Contains(...))` and a `$reasonFilled` check.

**Diff (logical):**
```diff
     $text = Get-Content -Raw -LiteralPath ''...deferred-remediation.md''
+    $reasonFilled = ($text.Contains(''Reason: approval denied'') -or $text.Contains(''Reason: approval ambiguous'') -or $text.Contains(''Reason: root cause uncertain'') -or $text.Contains(''Reason: risk exceeds benefit''))
-    $text.Contains(''Remediation was not applied in this run.'') -and $text.Contains(''Accepted status: ...'') -and $text.Contains(''Confirm a fresh `...\logs\*_run.md` ...'')
+    $text.Contains(''Remediation was not applied in this run.'') -and (-not $text.Contains(''<approval denied / approval ambiguous / root cause uncertain / risk exceeds benefit>'')) -and $reasonFilled -and $text.Contains(''Accepted status: ...'') -and $text.Contains(''Confirm a fresh `...\logs\*_run.md` ...'')
```

### Edit 6 - Task 4.3: LastWriteTime vs remediation timestamp

**Why:** The old acceptance check only verified the file existed. A pre-remediation `*_run.md` would also pass, giving false-positive "hourly firing is healthy" evidence. Strengthened to compare `LastWriteTime` against either a captured remediation timestamp (preferred) or today's date (fallback). Also includes a Task 3.3 dependency note: the executor must append a `## Remediation Applied: <iso-timestamp>` section to the execution log so the new check can find the timestamp.

**Diff (logical):**
```diff
-    ([string]$json.FullName).Contains(''C:\development\email-triage\logs\'') -and ([string]$json.FullName).Contains(''_run.md'') -and ($json.Length -gt 0)
+    $exists = ([string]$json.FullName).Contains(''C:\development\email-triage\logs\'') -and ([string]$json.FullName).Contains(''_run.md'') -and ($json.Length -gt 0)
+    # Compare last-write time against the remediation timestamp captured in Task 3.3.
+    # Task 3.3 must append a `## Remediation Applied: <iso-timestamp>` section to the execution log.
+    $remediationStamp = $null
+    $log = "C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\execution-log-$(Get-Date -Format ''yyyy-MM-dd'').md"
+    if (Test-Path -LiteralPath $log) {
+      $logText = Get-Content -Raw -LiteralPath $log
+      $stampMatch = [regex]::Match($logText, ''## Remediation Applied:\s*([0-9T:\-\.]+)'')
+      if ($stampMatch.Success) { try { $remediationStamp = [datetime]::Parse($stampMatch.Groups[1].Value) } catch {} }
+    }
+    $recentEnough = $false
+    if ($json.LastWriteTime) {
+      $logTime = [datetime]::Parse($json.LastWriteTime)
+      if ($remediationStamp) { $recentEnough = ($logTime -ge $remediationStamp) }
+      else { $recentEnough = ($logTime.Date -eq (Get-Date).Date) }
+    }
+    $exists -and $recentEnough
```

**Dry-run result:** The new logic was simulated against four scenarios. All four produced the expected outcome:
- post-remediation log + stamp: `True`
- pre-remediation log + stamp: `False`
- same-day log + no stamp: `True`
- old-day log + no stamp: `False`

### Edit 7 - Task 4.4: require placeholders to be filled in handover-summary.md

**Why:** Same template-vs-values gap. The `<Resolved / Deferred / Blocked>`, `<Evidence-backed root cause ...>`, `<Option 1 applied / ...>`, `<OK/ERR>`, `<observed/deferred>`, `<None or exact timed follow-up>` placeholders are all required content. Added `(-not $placeholdersLeft)` check.

**Diff (logical):**
```diff
     $text = Get-Content -Raw -LiteralPath ''...handover-summary.md''
+    $placeholdersLeft = $text.Contains(''<Resolved / Deferred / Blocked>'') -or $text.Contains(''<Evidence-backed root cause from root-cause-evidence.md>'') -or $text.Contains(''<Option 1 applied / Option 2 not attempted / Option 3 monitor / blocked waiting for approval>'') -or $text.Contains(''<OK/ERR>'') -or $text.Contains(''<observed/deferred>'') -or $text.Contains(''<None or exact timed follow-up>'')
-    $text.Contains(''## Final Status'') -and $text.Contains(''## Root Cause'') -and $text.Contains(''## Validation Results'') -and $text.Contains(''- Hourly firing evidence:'')
+    (-not $placeholdersLeft) -and $text.Contains(''## Final Status'') -and $text.Contains(''## Root Cause'') -and $text.Contains(''## Validation Results'') -and $text.Contains(''- Hourly firing evidence:'')
```

## Uncertain Items Surfaced to User (NOT applied)

1. **Switch all acceptance checks from `<paste command JSON output here>` template to a file-based JSON pattern.** Each task would write its JSON to a temp file, and the acceptance check would parse the file. Touches every task. **Not applied.**
2. **Add explicit Stage 4 closeout sync tasks (metadata.json, tracks.md, tracks-ledger.md).** The Stage 4 executor closeout checklist covers this. Low value-add. **Not applied.**
3. **Define "Tier-1 approval" in the spec body rather than just referencing threshold-policy.md.** The spec currently says "Tier-1" without defining it. Could be added to the spec for self-containment. **Surfaced.**

## Files Created by This Review

- `C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\review-report-2026-07-05-113940.md` (the review)
- `C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\review-diff-summary-2026-07-05-113940.md` (this file)
- `C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\plan.md.review-backup-2026-07-05-113940` (pre-edit plan snapshot, for diff/rollback)

## Verification Performed

- All 7 edits applied successfully (count of oldString matches was 1 for each; replace was literal).
- 14 post-edit assertions in plan.md verified to contain the new content (Python `in` checks against the live file).
- The new Task 4.3 acceptance logic was simulated in Python against 4 scenarios and produced the expected True/False outcomes.
- gsudo availability (v2.6.1) and the temp backup directory were confirmed to exist.
- The `<paste command JSON output here>` template pattern and the `gsudo pwsh -NoLogo -NoProfile -NonInteractive -Command "..."` backtick-dollar escape pattern were traced for correctness in Tasks 0.2, 1.1, 1.2, 1.3, 1.4, 1.5, 3.2, 3.3.
- The `Get-WinEvent` pattern in Task 1.5 was traced for null-Message safety (theoretical risk, not changed).

## Anomaly Logged

- One `info` JSONL line appended to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl`.
