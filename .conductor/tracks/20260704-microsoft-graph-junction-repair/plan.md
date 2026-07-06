# Plan: Microsoft Graph Junction Repair

## Restatement before tasks
Goal/outcome: repair the broken `microsoft-graph` lazy-vault junction first, verify email auto-sort Graph auth, then safely address vault-wide junctions, scheduled-task diagnostics, and bookkeeping.
Constraints/non-goals: no scheduler cadence/job JSON changes; no email-triage logic changes; no Graph cert rotation; no scheduled-task delete/recreate without approval; remove only `Junction` links; skip missing OneDrive sources; use `pwsh`.
Definition of done: wrapper reachable through lazy vault; newest email auto-sort run log shows Graph connection and no wrapper-missing error; systemic cohort preview/report complete; Issue 2 documented or fixed non-destructively; Issue 3 bookkeeping complete; Conductor artifacts synchronized.

Tool preflight: native file tools are reported failing, so use PowerShell via `bash` with explicit timeouts. Use `-LiteralPath`, no interactive/wait/watch/server commands.

## Phase 0 Setup & Preconditions
Objective: create evidence files and prove source paths before mutation.

- [x] Task 0.1 - Create execution log at `.conductor/tracks/20260704-microsoft-graph-junction-repair/execution-log-2026-07-04.md`.
  Command: `$p='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\execution-log-2026-07-04.md'; if(!(Test-Path -LiteralPath $p)){Set-Content -Encoding utf8 -LiteralPath $p -Value "# Execution Log`n`n## Actions`n"}`
  Authoritative acceptance check: `$t=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\execution-log-2026-07-04.md'; $t.Contains('## Actions')` Expected: `True`.
  Diagnostic checks: `Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\execution-log-2026-07-04.md'`.
  Error recovery: if track dir is missing, stop and report.

- [x] Task 0.2 - Snapshot lazy-vault state to `.conductor/tracks/20260704-microsoft-graph-junction-repair/lazy-vault-junction-snapshot-before.json`.
  Command: `$v='C:\Users\DaveWitkin\.opencode-lazy-vault'; $o='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-junction-snapshot-before.json'; Get-ChildItem -LiteralPath $v -Force|%{[pscustomobject]@{Name=$_.Name;FullName=$_.FullName;LinkType=$_.LinkType;Target=@($_.Target)}}|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath $o`
  Authoritative acceptance check: `$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-junction-snapshot-before.json'; $j.Contains('"Name": "microsoft-graph"') -and $j.Contains('"LinkType": "Junction"')` Expected: `True`.
  Diagnostic checks: `Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-junction-snapshot-before.json'|ConvertFrom-Json|? Name -eq 'microsoft-graph'|fl *`.
  Error recovery: if `microsoft-graph` is not a junction, stop; do not remove anything.

- [x] Task 0.3 - Confirm real source wrapper exists.
  Command: `$s='C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph'; $w=Join-Path $s 'scripts\connect-graph-no-wam.ps1'; [pscustomobject]@{SourceExists=Test-Path -LiteralPath $s -PathType Container; WrapperExists=Test-Path -LiteralPath $w -PathType Leaf}|ConvertTo-Json`
  Authoritative acceptance check: `$s='C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph'; $w=Join-Path $s 'scripts\connect-graph-no-wam.ps1'; ((Test-Path -LiteralPath $s -PathType Container) -and (Test-Path -LiteralPath $w -PathType Leaf))` Expected: `True`.
  Diagnostic checks: `Get-Item -LiteralPath 'C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1'|fl FullName,Length`.
  Error recovery: if source/wrapper missing, stop and log Tier-1 blocker.

Exit criteria: execution log and snapshot exist; real wrapper source confirmed.

## Phase 1 Implementation - Microsoft Graph acceptance gate
Objective: repair `microsoft-graph` and prove email auth progresses.

- [x] Task 1.1 - Guarded repair of `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph`.
  Command: `$p='C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph'; $s='C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph'; $i=Get-Item -LiteralPath $p -Force; if($i.LinkType -ne 'Junction'){throw 'Refusing non-junction'}; if(!(Test-Path -LiteralPath $s -PathType Container)){throw 'Missing source'}; Remove-Item -LiteralPath $p -Force; New-Item -ItemType Junction -Path $p -Target $s|Out-Null`
  Authoritative acceptance check: `$p='C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph'; $s='C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph'; $i=Get-Item -LiteralPath $p -Force; ($i.LinkType -eq 'Junction') -and (@($i.Target) -contains $s) -and (-not (@($i.Target) -contains $p))` Expected: `True`.
  Diagnostic checks: `Get-Item -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph' -Force|fl FullName,LinkType,Target`.
  Error recovery: on access denied, stop and request elevated shell; do not delete parent dirs.

- [x] Task 1.2 - Verify wrapper reachable through lazy vault.
  Command: `Test-Path -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1' -PathType Leaf`
  Authoritative acceptance check: `Test-Path -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1' -PathType Leaf` Expected: `True`.
  Diagnostic checks: `Get-Item -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1'|fl FullName,Length`.
  Error recovery: if false, inspect target and stop; do not edit email-triage logic.

- [x] Task 1.3 - Run email auto-sort with PowerShell 7 and verify newest log.
  Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File 'C:\development\email-triage\scripts\hourly-email-auto-sort.ps1'; $n=Get-ChildItem -LiteralPath 'C:\development\email-triage\logs' -Filter '*_run.md'|sort LastWriteTime -Descending|select -First 1; $n.FullName`
  Authoritative acceptance check: `$n=Get-ChildItem -LiteralPath 'C:\development\email-triage\logs' -Filter '*_run.md'|sort LastWriteTime -Descending|select -First 1; $t=Get-Content -Raw -LiteralPath $n.FullName; (($t.Contains('Connected via no-WAM wrapper') -or $t.Contains('Connected to Microsoft Graph')) -and (-not $t.Contains('No-WAM Graph auth wrapper not found')) -and (-not $t.Contains('FATAL: Graph auth failed')))` Expected: `True`.
  Diagnostic checks: `$n=Get-ChildItem -LiteralPath 'C:\development\email-triage\logs' -Filter '*_run.md'|sort LastWriteTime -Descending|select -First 1; Select-String -LiteralPath $n.FullName -SimpleMatch 'Authentication','Graph','No-WAM Graph auth wrapper not found'`.
  Error recovery: if a new non-wrapper error appears, log exact exit/log and stop before systemic repair.

Exit criteria: junction target and wrapper pass; auto-sort reaches Graph auth/connects.

## Phase 2 Implementation - Systemic vault cohort
Objective: dry-run, guarded repair, and report skipped entries.

- [x] Task 2.1 - Generate preview `.conductor/tracks/20260704-microsoft-graph-junction-repair/lazy-vault-repair-preview.json`.
  Command: `$v='C:\Users\DaveWitkin\.opencode-lazy-vault'; $r='C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault'; $o='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-preview.json'; Get-ChildItem -LiteralPath $v -Force|%{$e=Join-Path $r $_.Name; $t=@($_.Target); [pscustomobject]@{Name=$_.Name;Path=$_.FullName;LinkType=$_.LinkType;CurrentTarget=$t;ExpectedTarget=$e;IsSelfReferential=($t -contains $_.FullName);ExpectedSourceExists=(Test-Path -LiteralPath $e -PathType Container);Action=$(if($_.LinkType -eq 'Junction' -and ($t -contains $_.FullName) -and (Test-Path -LiteralPath $e -PathType Container)){'repair'}elseif($_.LinkType -eq 'Junction' -and ($t -contains $_.FullName)){'skip-missing-source'}else{'skip-not-self-referential-junction'})}}|ConvertTo-Json -Depth 6|Set-Content -Encoding utf8 -LiteralPath $o`
  Authoritative acceptance check: `$x=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-preview.json'|ConvertFrom-Json; (($x|? Name -eq 'microsoft-graph').ExpectedSourceExists -eq $true)` Expected: `True`.
  Diagnostic checks: `$x=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-preview.json'|ConvertFrom-Json; $x|Group-Object Action|ft Count,Name`.
  Error recovery: if JSON parse fails, do not mutate; fix preview first.

- [x] Task 2.2 - Apply repairs only for preview rows with `Action` = `repair`.
  Command: `$x=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-preview.json'|ConvertFrom-Json; foreach($row in @($x|? Action -eq 'repair')){$i=Get-Item -LiteralPath $row.Path -Force; if($i.LinkType -ne 'Junction'){throw "Refusing $($row.Path)"}; if(-not(@($i.Target)-contains $row.Path)){continue}; if(!(Test-Path -LiteralPath $row.ExpectedTarget -PathType Container)){throw "Missing $($row.ExpectedTarget)"}; Remove-Item -LiteralPath $row.Path -Force; New-Item -ItemType Junction -Path $row.Path -Target $row.ExpectedTarget|Out-Null}`
  Authoritative acceptance check: `$x=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-preview.json'|ConvertFrom-Json; $f=foreach($row in @($x|? Action -eq 'repair')){$i=Get-Item -LiteralPath $row.Path -Force; if(($i.LinkType -ne 'Junction') -or (-not(@($i.Target)-contains $row.ExpectedTarget)) -or (@($i.Target)-contains $row.Path)){$row.Name}}; @($f).Count -eq 0` Expected: `True`.
  Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault' -Force|?{$_.LinkType -eq 'Junction' -and (@($_.Target)-contains $_.FullName)}|select Name,Target`.
  Error recovery: stop on any guard failure; record repaired/skipped rows.

- [x] Task 2.3 - Write `.conductor/tracks/20260704-microsoft-graph-junction-repair/lazy-vault-repair-report.md`.
  Command: `$x=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-preview.json'|ConvertFrom-Json; $o='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-report.md'; $l=@('# Lazy-Vault Repair Report','','Repaired only rows whose preview action was `repair`. Skipped rows were not guessed.','','## Recurrence hypothesis','OpenCode desktop or lazy-vault reconciliation may be re-pointing vault junctions to their own local paths.','','## Skipped entries'); foreach($r in @($x|? Action -ne 'repair')){$l+="- $($r.Name): $($r.Action)"}; Set-Content -Encoding utf8 -LiteralPath $o -Value $l`
  Authoritative acceptance check: `$t=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-report.md'; $t.Contains('Repaired only rows whose preview action was `repair`. Skipped rows were not guessed.') -and $t.Contains('OpenCode desktop or lazy-vault reconciliation may be re-pointing vault junctions to their own local paths.')` Expected: `True`.
  Diagnostic checks: `Select-String -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-report.md' -SimpleMatch 'skip-missing-source','skip-not-self-referential-junction'`.
  Error recovery: if no skipped rows, still write the summary and hypothesis.

Exit criteria: preview exists; eligible repairs pass; report documents skips and recurrence hypothesis.

## Phase 3 Implementation - Scheduled-task diagnostic
Objective: collect evidence without destructive task changes.

- [x] Task 3.1 - Write `.conductor/tracks/20260704-microsoft-graph-junction-repair/scheduled-task-diagnostics.md`.
  Command: |
    `$n='opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort';
    `$o='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-diagnostics.md';
    `$s=@('# Scheduled Task Diagnostics','## Get-ScheduledTask',(Get-ScheduledTask -TaskName $n|fl *|Out-String),'## Get-ScheduledTaskInfo');
    try{`$s+=(Get-ScheduledTaskInfo -TaskName $n|fl *|Out-String)}catch{`$s+=$_.Exception.Message};
    `$s+='## Export-ScheduledTask';
    try{`$s+=(Export-ScheduledTask -TaskName $n|Out-String)}catch{`$s+=$_.Exception.Message};
    `$s+='## schtasks query';
    `$s+=(& schtasks /Query /TN $n /V /FO LIST 2>&1|Out-String);
    `$s+='## On-disk task files';
    `$s+=(Get-ChildItem -LiteralPath "$env:SystemRoot\System32\Tasks" -Recurse -Filter '*email-triage*' -ErrorAction SilentlyContinue|?{$_.Name -like '*email-triage*' -or $_.FullName -like '*OpenCode*'}|select FullName,Length,LastWriteTime|fl|Out-String);
    Set-Content -Encoding utf8 -LiteralPath $o -Value $s
  Authoritative acceptance check: `$t=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-diagnostics.md'; $t.Contains('## Get-ScheduledTask') -and $t.Contains('## Get-ScheduledTaskInfo') -and $t.Contains('## Export-ScheduledTask') -and $t.Contains('## schtasks query') -and $t.Contains('## On-disk task files')` Expected: `True`.
  Diagnostic checks: `Select-String -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-diagnostics.md' -SimpleMatch 'The system cannot find the file specified','Last Run Time','Next Run Time'`.
  Error recovery: if `System32\Tasks` is denied, record the denial and continue.

- [x] Task 3.2 - Write `.conductor/tracks/20260704-microsoft-graph-junction-repair/scheduled-task-remediation-proposal.md`.
  Command: `$o='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-remediation-proposal.md'; Set-Content -Encoding utf8 -LiteralPath $o -Value @('# Scheduled Task Remediation Proposal','','Root cause finding: document exact evidence from scheduled-task-diagnostics.md before remediation.','Safe remediation proposal: do not delete or recreate the task without explicit user approval.','Approval required before destructive task changes: yes')`
  Authoritative acceptance check: `$t=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-remediation-proposal.md'; $t.Contains('do not delete or recreate the task without explicit user approval') -and $t.Contains('Approval required before destructive task changes: yes')` Expected: `True`.
  Diagnostic checks: `Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-remediation-proposal.md'`.
  Error recovery: if inconclusive, say so and leave task unchanged.

Exit criteria: diagnostics/proposal exist; scheduled task not deleted/recreated.

## Phase 4 Implementation - Bookkeeping
Objective: fix source-track notes and metadata only.

- [x] Task 4.1 - Replace `powershell -NoProfile -ExecutionPolicy Bypass -File` with `pwsh -NoProfile -ExecutionPolicy Bypass -File` in `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/plan.md`.
  Command: `$p='C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\plan.md'; $t=Get-Content -Raw -LiteralPath $p; if(!$t.Contains('powershell -NoProfile -ExecutionPolicy Bypass -File')){throw 'literal missing'}; $new=$t.Replace('powershell -NoProfile -ExecutionPolicy Bypass -File','pwsh -NoProfile -ExecutionPolicy Bypass -File'); if($new -eq $t){throw 'replace made no change'}; Set-Content -Encoding utf8 -LiteralPath $p -Value $new`
  Authoritative acceptance check: `$t=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\plan.md'; $t.Contains('pwsh -NoProfile -ExecutionPolicy Bypass -File') -and (-not $t.Contains('powershell -NoProfile -ExecutionPolicy Bypass -File'))` Expected: `True`.
  Diagnostic checks: `Select-String -LiteralPath 'C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\plan.md' -SimpleMatch 'powershell -NoProfile','pwsh -NoProfile'`.
  Error recovery: if literal appears in more than one location, count matches first and ask before broad replace.

- [x] Task 4.2 - Confirm `C:\development\email-triage\scripts\run-hidden.vbs` resolves `pwsh`.
  Command: `$v=Get-Content -Raw -LiteralPath 'C:\development\email-triage\scripts\run-hidden.vbs'; $c=Get-Command pwsh -ErrorAction Stop; [pscustomobject]@{VbsMentionsPwsh=$v.Contains('pwsh');PwshPath=$c.Source;PwshVersion=$c.Version.ToString()}|ConvertTo-Json`
  Authoritative acceptance check: `$v=Get-Content -Raw -LiteralPath 'C:\development\email-triage\scripts\run-hidden.vbs'; $c=Get-Command pwsh -ErrorAction SilentlyContinue; $v.Contains('pwsh') -and ($null -ne $c)` Expected: `True`.
  Diagnostic checks: `Get-Command pwsh|fl Source,Version; Select-String -LiteralPath 'C:\development\email-triage\scripts\run-hidden.vbs' -SimpleMatch 'pwsh'`.
  Error recovery: if `pwsh` missing, stop and report; do not rewrite launcher.

- [x] Task 4.3 - Verify and backfill `.conductor/tracks/20260508-restore-opencode-scheduler-plugin/metadata.json`.
  Command: `$p='C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\metadata.json'; $j=Get-Content -Raw -LiteralPath $p|ConvertFrom-Json; $changed=$false; if([string]::IsNullOrEmpty([string]$j.executorModel)){$j.executorModel='zai-coding-plan/glm-5.2'; $changed=$true}; if($null -eq $j.completedAt){$j.completedAt=(Get-Date -Date '2026-07-04T18:50:00-04:00').ToString('o'); $changed=$true}; if($changed){$j|ConvertTo-Json -Depth 10|Set-Content -Encoding utf8 -LiteralPath $p}`
  Authoritative acceptance check: `$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\metadata.json'|ConvertFrom-Json; (-not [string]::IsNullOrEmpty([string]$j.executorModel)) -and ($null -ne $j.completedAt)` Expected: `True`.
  Diagnostic checks: `Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\metadata.json'|ConvertFrom-Json|select executorModel,completedAt,status`.
  Error recovery: if JSON parse fails, restore from backup/git before retry; never overwrite existing non-empty values.

Exit criteria: wording, `pwsh` availability, and metadata fields verified.

## Final Phase Validation & Handover
Objective: prove deliverables and Conductor bookkeeping.

- [x] Task 5.1 - Consolidated deliverable verification.
  Command: `$mg='C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph'; $src='C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph'; $w=Join-Path $mg 'scripts\connect-graph-no-wam.ps1'; $n=Get-ChildItem -LiteralPath 'C:\development\email-triage\logs' -Filter '*_run.md'|sort LastWriteTime -Descending|select -First 1; $rt=Get-Content -Raw -LiteralPath $n.FullName; [pscustomobject]@{TargetOk=@((Get-Item -LiteralPath $mg -Force).Target)-contains $src;Wrapper=Test-Path -LiteralPath $w -PathType Leaf;NoWrapperError=(-not $rt.Contains('No-WAM Graph auth wrapper not found'))}|ConvertTo-Json`
  Authoritative acceptance check: `$mg='C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph'; $src='C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph'; $w=Join-Path $mg 'scripts\connect-graph-no-wam.ps1'; $n=Get-ChildItem -LiteralPath 'C:\development\email-triage\logs' -Filter '*_run.md'|sort LastWriteTime -Descending|select -First 1; $rt=Get-Content -Raw -LiteralPath $n.FullName; (@((Get-Item -LiteralPath $mg -Force).Target)-contains $src) -and (Test-Path -LiteralPath $w -PathType Leaf) -and (-not $rt.Contains('No-WAM Graph auth wrapper not found')) -and (($rt.Contains('Connected via no-WAM wrapper') -or $rt.Contains('Connected to Microsoft Graph'))) -and (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\lazy-vault-repair-report.md') -and (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-remediation-proposal.md')` Expected: `True`.
  Diagnostic checks: `Get-Item -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph' -Force|fl FullName,LinkType,Target`.
  Error recovery: if latest log stale/missing, rerun Task 1.3 once with timeout, then stop with evidence.

- [x] Task 5.2 - Synchronize metadata and ledgers.
  Command: `$m='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\metadata.json'; $j=Get-Content -Raw -LiteralPath $m|ConvertFrom-Json; $j.status='completed'; $j.completed_tasks=$j.total_checkbox_count; $j.executor_model='zai-coding-plan/glm-5.2'; $j.executed_at=(Get-Date).ToString('s'); $j|ConvertTo-Json -Depth 10|Set-Content -Encoding utf8 -LiteralPath $m; # upsert one row in tracks.md and tracks-ledger.md preserving existing shape (Stage 1 already added the rows; verify the marker row still exists in both files and clean any pre-existing git conflict markers)
  Authoritative acceptance check: `$m=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\metadata.json'|ConvertFrom-Json; $tr=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks.md'; $le=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks-ledger.md'; ($m.status -eq 'completed') -and $tr.Contains('| 20260704-microsoft-graph-junction-repair |') -and $le.Contains('| 20260704-microsoft-graph-junction-repair |')` Expected: `True`.
  Diagnostic checks: `Select-String -LiteralPath 'C:\development\opencode\.conductor\tracks.md','C:\development\opencode\.conductor\tracks-ledger.md' -SimpleMatch '20260704-microsoft-graph-junction-repair'`.
  Error recovery: if table formats differ, preserve the format and avoid duplicate rows.

- [x] Task 5.3 - Write `.conductor/tracks/20260704-microsoft-graph-junction-repair/handover-summary.md`.
  Command: `$o='C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\handover-summary.md'; Set-Content -Encoding utf8 -LiteralPath $o -Value @('# Handover Summary','','Final status: completed','Email auto-sort newest run log does not contain `No-WAM Graph auth wrapper not found`.')`
  Authoritative acceptance check: `$t=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\handover-summary.md'; $t.Contains('Final status: completed') -and $t.Contains('Email auto-sort newest run log does not contain `No-WAM Graph auth wrapper not found`.')` Expected: `True`.
  Diagnostic checks: `Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\handover-summary.md'`.
  Error recovery: if blocked, write `Final status: blocked` and list blockers.

Exit criteria: consolidated verification true, metadata/ledgers updated once, summary written.

## Execution-readiness checklist
- [x] Absolute paths are supplied.
- [x] Microsoft Graph repair occurs before systemic repair.
- [x] `LinkType -eq 'Junction'` guard precedes every removal.
- [x] Dry-run preview precedes systemic mutation.
- [x] Missing sources are skipped/reported.
- [x] Email-triage uses `pwsh`.
- [x] Scheduled task is not deleted/recreated without approval.
- [x] Bookkeeping is synchronized.

## Top 3 risks + mitigations
1. Deleting real content: guard on `LinkType` exactly `Junction`.
2. OneDrive source unavailable: `Test-Path` source before repair; skip missing.
3. New auth error after repair: stop with newest log evidence; do not change production logic.

## First task to execute
Task 0.1 - Create execution log.







