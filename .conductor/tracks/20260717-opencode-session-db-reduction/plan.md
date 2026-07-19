# Plan: Safely Reduce the Local OpenCode Session Database

## Restatement Before Execution
- **Goal/outcome:** safely reduce the physical footprint of the local OpenCode session SQLite database and report exact savings.
- **Constraints/non-goals:** preserve valuable sessions; never expose content or credentials; no storage reset, schema modification, direct row deletion, or unapproved retention decision; use supported session deletion plus reversible SQLite compaction.
- **Definition of done:** approved candidates are deleted through the CLI, protected sessions and schema remain intact, validated backup/rollback copies exist, integrity checks pass, and exact before/after allocated bytes are reported.

All commands run in PowerShell 7 from `C:\development\opencode`. Use `-LiteralPath` and quoted Windows paths. Every shell call must be bounded by the agent tool timeout and must be non-interactive. Checkbox states are `[ ]` pending, `[~]` in progress, and `[x]` complete.

## Authorization Boundary (Fail Closed)
- The current authorization permits **non-destructive preflight and metadata-only inventory only**. It does not authorize deletion, compaction, database replacement, rollback, or removal of recovery artifacts.
- Before generating a deletion-candidate manifest, obtain one explicit user decision that confirms all three policy inputs: (1) the cutoff (user-selected: 180 days), (2) that every unarchived session and its complete family remain protected, and (3) the complete keep list (an explicit empty keep list is valid). General cleanup authorization is not a substitute for this policy decision.
- Before any deletion, present the resulting candidate-manifest SHA-256 and require explicit approval of that **exact hash**. Approval of a policy, summary, prior manifest, or future manifest is invalid. Any manifest or database-state change invalidates approval and requires a new manifest and new approval.
- Until both gates are satisfied, stop after non-destructive inventory. Never invoke `opencode session delete`, `VACUUM INTO`, a live-file swap, restore, reset, schema statement, or direct SQLite data mutation.
- Console/chat/review/execution-log output is aggregate and human-readable only. Never emit message contents, credentials, tokens, session/family IDs, or raw JSON. Sensitive machine-readable artifacts remain local and are referenced only by fully qualified path.


**Policy Override Audit Note (2026-07-17):** The original plan proposed a 90-day retention cutoff. Per explicit user instruction during Stage 5 execution, the policy was overridden to 180 days. All inventory, manifest, and execution artifacts use the 180-day cutoff (-CutoffDays 180). This override yielded 0 deletion candidates (all 2,776 sessions protected). Command templates above are updated to reflect the executed policy.

## Phase 0 - Setup & Preconditions
**Objective:** establish a private, reproducible baseline and prevent concurrent writes before any mutable operation.

- [x] **0.0 Node version preflight for `node:sqlite`.**
  - Action: run `node --version` and parse the major version. Refuse to proceed unless the major is >= 24 (built-in `node:sqlite`) OR (major == 22 AND minor >= 5 AND `--experimental-sqlite` is enabled). Fail closed with a clear STOP message and the install/upgrade command. This prevents the inventory + backup + validation scripts from failing mid-execution with a confusing `Cannot find module 'node:sqlite'` after the writer-stop gate has been activated, which would leave the DB open and unlocked.
  - Command: `pwsh -NoProfile -Command "$v = (node --version) -replace 'v',''; $m = [int]($v -split '\.')[0]; $n = [int]($v -split '\.')[1]; if (($m -ge 24) -or (($m -eq 22) -and ($n -ge 5))) { 'node-sqlite-ok' } else { Write-Error 'Node version too old for node:sqlite'; exit 1 }"` must print exactly `node-sqlite-ok`.
  - **Authoritative acceptance check:** the command above must print `node-sqlite-ok`.
  - Diagnostic checks: `node --version`; `node -e "require('node:sqlite'); console.log('OK')"`.
  - Error recovery: if the preflight fails, STOP; do not stop the writer; ask the user to install Node 24+ or Node 22.5+ with the experimental flag and rerun from 0.0.

- [x] **0.1 Create the redacted inventory utility at `.conductor\tracks\20260717-opencode-session-db-reduction\inventory-session-db.ps1`.**
  - Action: write a PowerShell 7 script that uses `node:sqlite` only for read-only metadata queries. It must output `baseline.json`, `inventory.json`, and `candidate-manifest.json` in this track folder. Allowed output keys are opaque session ID, UTC timestamps, archive Boolean, parent ID, family ID, aggregate bytes, hashed project/directory grouping, and totals. It must enumerate table/column metadata first and stop if required mappings are ambiguous. It must never select, stringify, print, or log `event.data`, message/part data, titles, prompts, responses, environment values, or credential-like columns. Implement the 180-day archived-only family-closure policy (overridden from 90 per user instruction) from `spec.md`, accept `-KeepListPath`, and write the manifest in stable ID order with `cutoffUtc`, policy version, and its SHA-256 sidecar.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\inventory-session-db.ps1" -DbPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -OutputDirectory ".conductor\tracks\20260717-opencode-session-db-reduction" -CutoffDays 180 -KeepListPath ".conductor\tracks\20260717-opencode-session-db-reduction\keep-session-ids.txt" -WhatIf`
  - **Authoritative acceptance check (4 parts, ALL must pass):** Part A (static policy, no comment false-positives): `pwsh -NoProfile -Command "Get-Content -Raw -LiteralPath '.conductor\tracks\20260717-opencode-session-db-reduction\inventory-session-db.ps1' | Select-String -Pattern '(?im)^\s*(?!#|--)\s*(SELECT\s+\*|UPDATE|DELETE|INSERT|REPLACE|DROP\s+TABLE)\b' | ForEach-Object { exit 1 }"` must exit 0 (no executable SQL mutation statement, comment lines ignored). Part B (-WhatIf produces no output): after running `pwsh -NoProfile -File $scriptPath -DbPath $db -OutputDirectory $outDir -CutoffDays 180 -KeepListPath $keep -WhatIf`, `if (Test-Path -LiteralPath '.\candidate-manifest.json') { exit 1 }` must exit 0. Part C (verbose prints required parameters): `pwsh -NoProfile -File $scriptPath -DbPath $db -OutputDirectory $outDir -CutoffDays 180 -KeepListPath $keep -WhatIf -Verbose 2>&1 | Select-String -SimpleMatch -Pattern 'DbPath' | Should -Not -BeNullOrEmpty` AND `Select-String -SimpleMatch -Pattern 'KeepListPath'` must both match. Part D (script declares safety mechanisms): the script body must reference each of the literal substrings `cutoffUtc`, `policyVersion`, `manifestSha256`, `denyListColumns`, `attributionSql`, `family`, `length(`, `octet_length(`, `pragmamode=ro`, `node --version`; each `Select-String -SimpleMatch` must return >=1 hit. This replaces the old static "event.data is required" check - the new check requires the script to declare the safety mechanisms, not the dangerous column name itself. The authoritative output-file scan (content-leak check on `inventory.json`, `candidate-manifest.json`, `baseline.json`) is in task 0.2. Must print exactly `inventory-script-policy-ok` (run all 4 parts as one combined check; exit code from any part is the overall exit code).
  - Diagnostic checks: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\inventory-session-db.ps1" -DbPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -OutputDirectory ".conductor\tracks\20260717-opencode-session-db-reduction" -CutoffDays 180 -KeepListPath ".conductor\tracks\20260717-opencode-session-db-reduction\keep-session-ids.txt" -WhatIf`.
  - Error recovery: if schema mapping is uncertain or a forbidden field would be emitted, write no inventory, report only the table/column names involved, and stop for review. Do not weaken redaction.

- [x] **0.2 Capture writer/process state and exact baseline allocation.**
  - Action: ensure `keep-session-ids.txt` exists (empty is valid); stop and ask the user to close OpenCode Desktop/CLI/server sessions, then record process identities and exact `Length` values for `.db`, `-wal`, and `-shm` in `baseline.json`. Run the inventory utility only after no likely writer remains. Do not kill processes automatically.
  - Command: `$names=@('opencode','OpenCode'); $running=Get-Process -ErrorAction SilentlyContinue | Where-Object {$names -contains $_.ProcessName}; if($running){$running | Select-Object ProcessName,Id,StartTime; throw 'OpenCode writer may be active'}; if(-not (Test-Path -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\keep-session-ids.txt")){New-Item -ItemType File -Path ".conductor\tracks\20260717-opencode-session-db-reduction\keep-session-ids.txt" | Out-Null}; pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\inventory-session-db.ps1" -DbPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -OutputDirectory ".conductor\tracks\20260717-opencode-session-db-reduction" -CutoffDays 180 -KeepListPath ".conductor\tracks\20260717-opencode-session-db-reduction\keep-session-ids.txt"`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$b=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\baseline.json" | ConvertFrom-Json; if($b.dbBytes -le 0 -or $null -eq $b.walBytes -or $b.freelistCount -ne 0 -or $b.redactionPolicy -ne "metadata-only-v1"){exit 1}; "baseline-private-and-complete"'` must print exactly `baseline-private-and-complete`.
  - Diagnostic checks: `Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -match '^(opencode|OpenCode)$'} | Select-Object ProcessName,Id,StartTime`.
  - Error recovery: if a process exists or sizes change during inventory, stop, close the writer, discard generated inventory artifacts, and rerun this task from the start.

- [x] **0.3 Verify free-space capacity for rollback artifacts.**
  - Action: calculate required free bytes as current DB + WAL + 2 GiB margin for the fresh backup, plus current DB + WAL + 2 GiB margin for the compact candidate. Record the selected backup volume and capacity decision in `baseline.json`; do not infer that the old 14.343 GiB backup is current enough.
  - Command: single PowerShell block that derives the drive from the backup path (`$drive = ([System.IO.Path]::GetPathRoot((Resolve-Path -LiteralPath $backupDir).Path)).TrimEnd('\').TrimEnd(':')`), computes `$required = 2 * ($dbLength + $walLength) + 4GB` (one fresh backup at full size, one compact candidate at full size, plus 4 GB safety margin; the compact candidate is usually smaller, so this is a conservative upper bound), gets `$free = (Get-PSDrive -Name $drive).Free`, emits JSON `{ drive, dbBytes, walBytes, requiredBytes, freeBytes, sufficient }`, and exits 1 if `$free -lt $required`. The 2x + 4GB calculation now derives the drive from `-BackupDirectory` rather than hard-coding `C:` so a user-chosen alternate volume is verified correctly.
  - **Authoritative acceptance check:** the command above must exit `0` and its JSON must contain `"sufficient": true`.
  - Diagnostic checks: `Get-PSDrive -Name C | Select-Object Name,Free,Used`.
  - Error recovery: if insufficient, stop and ask the user for an alternate same-machine backup volume with enough capacity. Never delete sessions or old backups to manufacture space.

**Exit criteria:** no OpenCode writer is active; private baseline/inventory artifacts exist; policy mapping is unambiguous; capacity is sufficient.

## Phase 1 - Safety Backup and Candidate Approval
**Objective:** establish independently validated rollback and bind authorization to one immutable candidate set.

- [~] **1.1 Create and validate a fresh consistent SQLite backup.**
  - Action: create `backup-session-db.ps1` in the track folder. With writers stopped, use `node:sqlite` to run `PRAGMA wal_checkpoint(TRUNCATE)`, then the SQLite backup API to create `C:\Users\DaveWitkin\AppData\Local\Temp\opencode\opencode-pre-cleanup-<UTC timestamp>.db`. Run `PRAGMA quick_check` against the live DB and backup; record backup path, exact bytes, source/backup schema fingerprints, `user_version`, and SHA-256 in `backup-validation.json`. Never use plain `Copy-Item` on a live/WAL database.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\backup-session-db.ps1" -DbPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -BackupDirectory "C:\Users\DaveWitkin\AppData\Local\Temp\opencode" -ReportPath ".conductor\tracks\20260717-opencode-session-db-reduction\backup-validation.json"`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\backup-validation.json" | ConvertFrom-Json; if($r.sourceQuickCheck -ne "ok" -or $r.backupQuickCheck -ne "ok" -or $r.sourceSchemaSha256 -ne $r.backupSchemaSha256 -or -not (Test-Path -LiteralPath $r.backupPath)){exit 1}; "backup-valid"'` must print exactly `backup-valid`.
  - Diagnostic checks: `Get-FileHash -Algorithm SHA256 -LiteralPath ((Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\backup-validation.json" | ConvertFrom-Json).backupPath)`.
  - Error recovery: on checkpoint busy, integrity failure, hash/report mismatch, or backup API error, stop without deletion; close the remaining writer and retry once from task 0.2. A second failure requires user review.

- [ ] **1.2 Present the immutable candidate manifest, run a DB-unchanged TOCTOU gate, and obtain explicit approval.**
  - **STATUS: DEFERRED.** Manifest has 0 candidates (all 2,776 sessions protected under 180-day policy). No approval required. Re-enter if policy changes or non-empty manifest is produced.
  - Action:
    1. **DB-unchanged gate (NEW - closes the window between inventory and approval):** with writers still stopped, re-run a lightweight inventory check: `node -e "const db=new (require('node:sqlite')).DatabaseSync(process.argv[1],{readOnly:true}); const r=db.prepare('SELECT COUNT(*) AS n, MAX(time_updated) AS last FROM session').get(); console.log(JSON.stringify(r))"` ` dbPath`. Compare the result to the `inventory.json.sessionCount` and `inventory.json.lastUpdatedAt`. If they differ, the DB changed since inventory - STOP and rerun from 0.1 (a new manifest with a new hash is required for approval).
    2. Report only cutoff, policy version, keep-list count, candidate session/family counts, estimated aggregate bytes, protected counts, and manifest SHA-256 to chat. Do not print IDs to chat; provide the fully qualified local manifest path for private review. The execution log and any chat output must NOT include session IDs, family IDs, or hash values that could be correlated to a specific session.
    3. Record approval in `approval.json` with the exact manifest hash, UTC timestamp, cutoff, literal `approvedByUser: true`, `dbUnchangedConfirmed: true` (the user re-confirms after seeing the TOCTOU gate output), and the manifest's `createdAt` value. The user creates this file (or via a user-driven prompt to the executor); the script must NOT self-authorize.
  - Command: `$m=".conductor\tracks\20260717-opencode-session-db-reduction\candidate-manifest.json"; $h=(Get-FileHash -Algorithm SHA256 -LiteralPath $m).Hash; $j=Get-Content -Raw -LiteralPath $m | ConvertFrom-Json; [pscustomobject]@{cutoffUtc=$j.cutoffUtc;policyVersion=$j.policyVersion;candidateSessions=$j.summary.candidateSessions;candidateFamilies=$j.summary.candidateFamilies;estimatedBytes=$j.summary.estimatedBytes;manifestSha256=$h} | ConvertTo-Json`
  - **Authoritative acceptance check:** a single PowerShell block that asserts `approvedByUser == $true`, the live-recomputed `manifestSha256` equals `approval.json.manifestSha256`, `cutoffUtc` and `policyVersion` match the manifest, `dbUnchangedConfirmed == $true` (TOCTOU gate re-confirmed by user), and `approval.json.approvedAt >= candidate-manifest.json.createdAt` (no time travel / stale approval). Must print exactly `exact-manifest-approved`.
  - Diagnostic checks: compare candidate summary counts with `inventory.json` without displaying IDs or content.
  - Error recovery: if the user changes cutoff/keep list or declines any family, regenerate inventory and manifest, invalidate/delete `approval.json`, create a new backup if the DB changed, and request approval of the new hash.

**Exit criteria:** a fresh validated backup exists and the exact unchanged candidate manifest has explicit user approval.

## Phase 2 - Application-Supported Deletion
**Objective:** remove only approved session families through the canonical OpenCode CLI with an auditable stop-on-error log.

- [x] **2.1 Create the manifest-bound cleanup utility at `.conductor\tracks\20260717-opencode-session-db-reduction\delete-approved-sessions.ps1`.**
  - **NOTE:** Script created and statically validated (all acceptance checks pass). Execution deferred because manifest has 0 candidates.
  - Action: write a script accepting manifest, approval, expected CLI path/version, and log paths. It must recompute and compare the manifest hash, verify no OpenCode process other than its child CLI exists, process complete families in deterministic order, invoke `& $OpenCodePath session delete $sessionId` once per approved ID, stop on first nonzero exit, and append only ID/status/exit-code/timestamp to `deletion-log.jsonl`. It must support `-WhatIf`; it must contain no SQL mutation statement.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\delete-approved-sessions.ps1" -ManifestPath ".conductor\tracks\20260717-opencode-session-db-reduction\candidate-manifest.json" -ApprovalPath ".conductor\tracks\20260717-opencode-session-db-reduction\approval.json" -OpenCodePath ((Get-Command opencode).Source) -LogPath ".conductor\tracks\20260717-opencode-session-db-reduction\deletion-log.jsonl" -WhatIf`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command "$t = Get-Content -Raw -LiteralPath '.conductor\tracks\20260717-opencode-session-db-reduction\delete-approved-sessions.ps1'; if (-not ($t | Select-String -SimpleMatch -Pattern 'session delete' | Select-Object -First 1)) { exit 1 }; if (-not ($t | Select-String -SimpleMatch -Pattern 'manifestSha256' | Select-Object -First 1)) { exit 1 }; if (-not ($t | Select-String -SimpleMatch -Pattern 'WhatIf' | Select-Object -First 1)) { exit 1 }; $forbidden = ($t | Select-String -Pattern '(?im)^\s*(?!#|--)\s*(INSERT|UPDATE|DELETE|REPLACE|ALTER|DROP|TRUNCATE|CREATE|VACUUM)\b' | Select-Object -ExpandProperty Line); if ($forbidden) { exit 1 }; 'cli-only-delete-script-ok'"` must print exactly `cli-only-delete-script-ok`. The forbidden-SQL regex uses `(?im)^\s*(?!#|--)\s*...` to exclude comment lines starting with `#` or `--`, fixing the false-positive issue with comments that mention the forbidden patterns in a "do not do this" context. The required `session delete` / `manifestSha256` / `WhatIf` substrings are checked with `Select-String -SimpleMatch` so a comment-only occurrence does not pass; the script must reference them in actual code.
  - Diagnostic checks: run the `-WhatIf` command and compare planned invocation count with `candidate-manifest.json` summary.
  - Error recovery: if canonical CLI resolution/version differs from baseline or `-WhatIf` count differs, do not run live; fix mapping or regenerate/approve artifacts.

- [CANCELLED] **2.2 Apply the approved manifest through `opencode session delete`.**
  - **STATUS: CANCELLED.** Manifest contains 0 candidates. No deletion to apply. Re-enter if a future inventory produces candidates.
  - Action: rerun writer and manifest-hash gates, then execute without `-WhatIf`. Never retry a failed ID automatically. Preserve the partial log so validation can distinguish completed and pending families.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\delete-approved-sessions.ps1" -ManifestPath ".conductor\tracks\20260717-opencode-session-db-reduction\candidate-manifest.json" -ApprovalPath ".conductor\tracks\20260717-opencode-session-db-reduction\approval.json" -OpenCodePath ((Get-Command opencode).Source) -LogPath ".conductor\tracks\20260717-opencode-session-db-reduction\deletion-log.jsonl"`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$m=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\candidate-manifest.json" | ConvertFrom-Json; $l=Get-Content -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\deletion-log.jsonl" | ForEach-Object {$_ | ConvertFrom-Json}; if(@($l | Where-Object {$_.status -eq "deleted" -and $_.exitCode -eq 0}).Count -ne @($m.sessions).Count){exit 1}; "approved-cli-deletions-complete"'` must print exactly `approved-cli-deletions-complete`.
  - Diagnostic checks: summarize status counts from `deletion-log.jsonl`; do not print session IDs.
  - Error recovery: on first failure stop. Do not compact. Validate the live DB and protected set, then ask the user whether to restore the fresh backup or investigate/resume the remaining approved IDs.

**Exit criteria:** every and only approved session ID has one successful CLI deletion log entry.

## Phase 3 - Integrity Validation and Reversible Compaction
**Objective:** prove retention and schema safety before converting logical deletion into physical disk savings.

- [x] **3.1 Validate post-deletion integrity, schema, protected presence, and candidate absence.**
  - **NOTE:** Script created and tested. Execution deferred because no deletions occurred.
  - Action: create `validate-session-db.ps1` to run `quick_check`, compare schema SHA-256 and `user_version` to baseline, query opaque IDs only, verify every protected/retained ID remains and every successfully deleted ID is absent, and write `post-delete-validation.json`. Do not compact on any mismatch.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\validate-session-db.ps1" -DbPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -BaselinePath ".conductor\tracks\20260717-opencode-session-db-reduction\baseline.json" -InventoryPath ".conductor\tracks\20260717-opencode-session-db-reduction\inventory.json" -ManifestPath ".conductor\tracks\20260717-opencode-session-db-reduction\candidate-manifest.json" -DeletionLogPath ".conductor\tracks\20260717-opencode-session-db-reduction\deletion-log.jsonl" -ReportPath ".conductor\tracks\20260717-opencode-session-db-reduction\post-delete-validation.json"`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\post-delete-validation.json" | ConvertFrom-Json; if($r.quickCheck -ne "ok" -or $r.schemaMatches -ne $true -or $r.protectedMissing -ne 0 -or $r.deletedStillPresent -ne 0){exit 1}; "post-delete-valid"'` must print exactly `post-delete-valid`.
  - Diagnostic checks: report only aggregate missing/present counts and freelist/page counts.
  - Error recovery: if integrity/schema/retention fails, stop all writers, preserve evidence, restore from the fresh backup using the rollback task, and do not compact.

- [x] **3.2 Create and validate a compact database candidate without replacing the live file.**
  - **NOTE:** Script created and tested. Execution deferred because no deletions occurred.
  - Action: create `compact-session-db.ps1`. With writers stopped, checkpoint WAL and execute SQLite `VACUUM INTO` to a never-existing file on the same volume, using a safely SQL-quoted absolute path. Validate candidate `quick_check`, schema hash, `user_version`, protected/candidate state, and exact length. Refuse overwrite.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\compact-session-db.ps1" -SourceDb "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -CandidateDb "C:\Users\DaveWitkin\.local\share\opencode\opencode.db.compact-20260717" -ValidationReport ".conductor\tracks\20260717-opencode-session-db-reduction\compact-validation.json" -BaselinePath ".conductor\tracks\20260717-opencode-session-db-reduction\baseline.json" -InventoryPath ".conductor\tracks\20260717-opencode-session-db-reduction\inventory.json" -ManifestPath ".conductor\tracks\20260717-opencode-session-db-reduction\candidate-manifest.json"`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\compact-validation.json" | ConvertFrom-Json; if($r.quickCheck -ne "ok" -or $r.schemaMatches -ne $true -or $r.retentionMatches -ne $true -or -not (Test-Path -LiteralPath $r.candidatePath)){exit 1}; "compact-candidate-valid"'` must print exactly `compact-candidate-valid`.
  - Diagnostic checks: compare source and candidate exact lengths; zero/negative estimated saving is not corruption but should be reported before deciding whether to swap.
  - Error recovery: delete only the invalid compact candidate, never the source/backup; investigate and recreate once. A second failure stops for user review.

- [CANCELLED] **3.3 Perform a reversible same-volume database swap.**
  - **STATUS: CANCELLED.** No deletions occurred (0 candidates), so no compaction or swap is needed. Re-enter if deletion is later performed.
  - Action: with writers stopped, rename live DB to `opencode.db.pre-compact-<UTC timestamp>`, rename the validated candidate to `opencode.db`, and remove stale zero-length WAL/SHM only after checkpoint. Do not overwrite any path and do not delete the original. Immediately rerun full validation against the new live path.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\swap-validated-db.ps1" -LiveDb "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -CandidateDb ((Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\compact-validation.json" | ConvertFrom-Json).candidatePath) -ValidationReport ".conductor\tracks\20260717-opencode-session-db-reduction\compact-validation.json" -SwapReport ".conductor\tracks\20260717-opencode-session-db-reduction\swap-report.json"`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\swap-report.json" | ConvertFrom-Json; if($r.postSwapQuickCheck -ne "ok" -or -not (Test-Path -LiteralPath $r.preCompactPath) -or -not (Test-Path -LiteralPath $r.livePath)){exit 1}; "reversible-swap-valid"'` must print exactly `reversible-swap-valid`.
  - Diagnostic checks: verify live and pre-compact file hashes differ and all expected paths are on the same volume.
  - Error recovery: if either rename fails, reverse any completed rename immediately while writers remain stopped. If post-swap validation fails, move the compact DB aside and rename the pre-compact DB back to `opencode.db`; retain the fresh backup.

**Exit criteria:** the compact validated DB is live; both fresh backup and pre-compaction original remain; schema/integrity/retention checks pass.

## Final Phase - Validation & Handover
**Objective:** measure actual savings, prove application readability, document rollback, and synchronize the track without discarding recovery artifacts.

- [CANCELLED] **F.1 Measure exact physical space savings and perform a bounded application smoke read.**
  - **STATUS: CANCELLED.** No deletions or compaction occurred. No space savings to measure. Re-enter if cleanup is later resumed.
  - Action: create `space-savings.json` and `space-savings.md` from exact pre/post DB/WAL/SHM lengths. Compute `savedBytes = preTotalBytes - postTotalBytes` and GiB using division by `1GB`; report negative values honestly. Run `opencode session list --max-count 1 --format json` with the canonical binary and capture only exit code/count, not session fields.
  - Command: `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\measure-space-savings.ps1" -BaselinePath ".conductor\tracks\20260717-opencode-session-db-reduction\baseline.json" -DbPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -JsonReport ".conductor\tracks\20260717-opencode-session-db-reduction\space-savings.json" -MarkdownReport ".conductor\tracks\20260717-opencode-session-db-reduction\space-savings.md" -OpenCodePath ((Get-Command opencode).Source)`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\space-savings.json" | ConvertFrom-Json; if($r.savedBytes -ne ($r.preTotalBytes-$r.postTotalBytes) -or $r.applicationSmokeExitCode -ne 0){exit 1}; "savings-exact-and-readable"'` must print exactly `savings-exact-and-readable`.
  - Diagnostic checks: `Get-Item -LiteralPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" | Select-Object FullName,Length`.
  - Error recovery: if smoke read fails, stop writers and roll back to pre-compaction DB; do not delete any recovery file. If savings are nonpositive but validation passes, report zero/negative savings and ask whether to retain or revert.

- [CANCELLED] **F.2 Write and verify the rollback/handover record.**
  - **STATUS: CANCELLED.** No swap performed. No handover record needed. Re-enter if compaction/swap is later performed.
  - Action: create `handover.md` with exact backup path/hash, pre-compaction path/hash, manifest hash, validation report paths, no-writer prerequisite, rollback rename sequence, and a rule not to delete recovery artifacts until explicit user acceptance. Include no session IDs or content.
  - Command: `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\swap-report.json" | ConvertFrom-Json; $b=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\backup-validation.json" | ConvertFrom-Json; @("Stop all OpenCode writers before rollback.","Move the current compact database aside; do not delete it.","Rename the pre-compaction database back to opencode.db.","Run PRAGMA quick_check and an application smoke read.","Fresh backup: $($b.backupPath)","Pre-compaction database: $($r.preCompactPath)") | Set-Content -Encoding utf8 -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\handover.md"'`
  - **Authoritative acceptance check:** `pwsh -NoProfile -Command '$t=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\handover.md"; $required=@("Stop all OpenCode writers before rollback.","Move the current compact database aside; do not delete it.","Rename the pre-compaction database back to opencode.db.","Run PRAGMA quick_check and an application smoke read.","Fresh backup:","Pre-compaction database:"); if(($required | Where-Object {-not $t.Contains($_)}).Count){exit 1}; "handover-complete"'` must print exactly `handover-complete`.
  - Diagnostic checks: verify every path named in `handover.md` exists without printing hashes or IDs to public output.
  - Error recovery: if any recovery artifact is absent, do not close; restore/recreate it when safe or explicitly mark the track blocked.

- [x] **F.3 Upsert the track rows and synchronize completion metadata/logs.**
  - Action: upsert exactly one row for `20260717-opencode-session-db-reduction` in `.conductor\tracks.md` and `.conductor\tracks-ledger.md`; update `metadata.json`, checkboxes, and `execution-log-2026-07-17.md`. Record actual pipeline stages, approvals, deviations, validation commands, artifact paths, exact savings, and Stage 9 waiver/readiness. Do not duplicate rows.
  - Command: `pwsh -NoProfile -Command '$id="20260717-opencode-session-db-reduction"; foreach($p in @(".conductor\tracks.md",".conductor\tracks-ledger.md")){if((Select-String -LiteralPath $p -SimpleMatch $id).Count -ne 1){throw "$p must contain exactly one track row"}}; $m=Get-Content -Raw -LiteralPath ".conductor\tracks\$id\metadata.json" | ConvertFrom-Json; if($m.status -ne "complete" -or $m.progress.percentage -ne 100){throw "metadata incomplete"}; "conductor-synchronized"'`
  - **Authoritative acceptance check:** the command above must print exactly `conductor-synchronized`.
  - Diagnostic checks: `git status --short -- ".conductor/tracks/20260717-opencode-session-db-reduction" ".conductor/tracks.md" ".conductor/tracks-ledger.md"`.
  - Error recovery: update existing rows in place; if formats differ, preserve their format and stop rather than append a guessed duplicate.

**Exit criteria:** exact savings and smoke-read evidence exist; rollback is actionable; all non-deferred tasks and Conductor artifacts agree; recovery copies remain pending user acceptance.

## Deterministic End-to-End Verification Commands
Run in this order after execution:
1. `pwsh -NoProfile -File ".conductor\tracks\20260717-opencode-session-db-reduction\validate-session-db.ps1" -DbPath "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" -BaselinePath ".conductor\tracks\20260717-opencode-session-db-reduction\baseline.json" -InventoryPath ".conductor\tracks\20260717-opencode-session-db-reduction\inventory.json" -ManifestPath ".conductor\tracks\20260717-opencode-session-db-reduction\candidate-manifest.json" -DeletionLogPath ".conductor\tracks\20260717-opencode-session-db-reduction\deletion-log.jsonl" -ReportPath ".conductor\tracks\20260717-opencode-session-db-reduction\final-validation.json"`
2. `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\final-validation.json" | ConvertFrom-Json; if($r.quickCheck -ne "ok" -or -not $r.schemaMatches -or $r.protectedMissing -or $r.deletedStillPresent){exit 1}'`
3. `opencode session list --max-count 1 --format json *> $null; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}`
4. `pwsh -NoProfile -Command '$r=Get-Content -Raw -LiteralPath ".conductor\tracks\20260717-opencode-session-db-reduction\space-savings.json" | ConvertFrom-Json; if($r.savedBytes -ne ($r.preTotalBytes-$r.postTotalBytes)){exit 1}; $r | Select-Object preTotalBytes,postTotalBytes,savedBytes,savedGiB | ConvertTo-Json'`

## Execution-Readiness Checklist
- [ ] User has confirmed the 180-day cutoff, unarchived-session protection, and any keep-list IDs.
- [ ] Native file tools are known broken with `Bun is not defined`; executor uses PowerShell-first via bounded `bash`, `-LiteralPath`, and quoted paths.
- [ ] No OpenCode writer is active.
- [ ] Free-space gate passes.
- [ ] Canonical `opencode` binary path/version is captured.
- [ ] Inventory redaction and family closure are verified.
- [ ] Fresh backup passes integrity/schema/hash checks.
- [ ] Exact manifest hash has explicit approval.
- [ ] Rollback paths are collision-free and on suitable volumes.

## Top 3 Risks and Mitigations
1. **Irreversible loss of valuable sessions:** protect recent/unarchived/keep-listed related families, require exact manifest-hash approval, and retain a fresh validated backup plus pre-compaction original.
2. **Corruption or inconsistent backup from concurrent writers/WAL:** require all writers stopped, checkpoint, use SQLite backup/VACUUM INTO APIs, validate `quick_check` and schema before every progression.
3. **Privacy leak through inventory/logging:** whitelist non-content fields, hash path grouping, prohibit payload/title selection, report aggregate counts only, and stop on unknown schema mapping.

## First Task to Execute
Task **0.0**: verify the runtime can load `node:sqlite`. Then create and statically validate the metadata-only inventory utility. Do not query the live database until its field whitelist and forbidden-content checks pass. Do not generate a deletion-candidate manifest until the user confirms the cutoff, unarchived-family protection, and complete keep list.

## Pipeline Determination
- **Track type:** `code` (execution creates and runs safety-critical automation scripts against shared user storage).
- **Classification/risk:** `certain`, high data-loss risk.
- **Recommended mode:** `full`.
- **Recommended path:** `1 -> 2 -> 3? -> 4 -> 4b -> 5 -> 6 -> 7 -> 8? -> 9`.
- **Rationale:** retention/deletion, SQLite storage, rollback, and custom automation have high failure cost and need independent review, RED safety tests, execution, test running, and validation. Conditional re-review/re-validation remain threshold-driven.




