# Session Handoff: Scheduled-Task Read Inconsistency (email-triage hourly task)

> Focused follow-up to track `20260704-microsoft-graph-junction-repair` (Issue 2).
> This is a diagnostic + remediation task, NOT a functional outage. The task IS firing.

## Original Session

- Title: Conductor pipeline run - track `20260704-microsoft-graph-junction-repair`
- Repo: `C:\development\opencode`
- Watermark: 2026-07-04T20:35:51-04:00 (pipeline closed; validation verdict promoted to clean close after orchestrator bookkeeping normalization)
- Pipeline stages run: 1 Plan (gpt-5.5) -> 2 Review (minimax-m3, 92%) -> 3 Skipped (no B+C trigger) -> 4 Execute (glm-5.2, 17/17) -> 5 Validate (minimax-m3, "Close with minor follow-ups") -> 6 Skipped (no A+C trigger)
- Source track dir: `C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\`
- Source validation report: `.\tracks\20260704-microsoft-graph-junction-repair\validation-report-2026-07-04_183308.md`
- Parent handoff (broader, 3 issues): `C:\development\opencode\.opencode\handoffs\20260704-1715-scheduler-followups.md` (Issues 1 and 3 are RESOLVED; this doc deep-dives the remaining Issue 2)

## TL;DR / Recovered Goal

The hourly email-auto-sort scheduled task is **registered, enabled, and actually firing** (fresh `*_run.md` logs appear on schedule). But three read/export APIs consistently fail with **"The system cannot find the file specified"**:

- `Get-ScheduledTaskInfo -TaskName <name>`
- `Export-ScheduledTask -TaskName <name>`
- `schtasks /Query /TN <name> /V /FO LIST`

while `Get-ScheduledTask -TaskName <name>` succeeds and reports `State = Ready`.

This is a **Task Scheduler metadata/cache inconsistency**, not a functional failure and not an auth/junction problem (those were fixed in Issue 1). The new session's job is to **nail the exact root cause and propose/apply a safe remediation** (destructive task recreation needs explicit approval).

## The Task (exact identifiers)

- **TaskName:** `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
- **TaskPath:** `\OpenCode\`
- **URI:** `\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
- **Description:** "Hourly email auto-sort using Microsoft Graph API"
- **Action:** `MSFT_TaskExecAction` (invokes `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1` via a headless VBS launcher - see Issue 3a/`run-hidden.vbs`)
- **Trigger:** `MSFT_TaskTimeTrigger` (hourly; the job JSON cadence is `*/15 * * * *` per the scheduler plugin but the Windows task fires hourly)

## How the Issue Was Found

1. The prior pipeline (`20260508-restore-opencode-scheduler-plugin`) restored the opencode-scheduler plugin and validated all scheduled tasks.
2. During that validation, the executor noticed the read/export APIs failed for this one task. It was logged as a [LOW] diagnostic follow-up because the task was demonstrably firing (logs existed).
3. The `20260704-microsoft-graph-junction-repair` track picked it up as **Phase 3 - Scheduled-task diagnostic (non-destructive)**. The executor wrote two evidence artifacts and explicitly did NOT recreate the task (approval required).
4. **This session (orchestrator closeout)** re-ran the on-disk and registry probes first-hand and discovered a key fact that **refines the earlier hypothesis** (see Root Cause).

## Symptom (verified, reproducible)

| Command | Result |
|---|---|
| `Get-ScheduledTask -TaskName <name>` | SUCCEEDS - `State = Ready`, full `MSFT_ScheduledTask` object returned |
| `Get-ScheduledTaskInfo -TaskName <name>` | FAILS - "The system cannot find the file specified." |
| `Export-ScheduledTask -TaskName <name>` | FAILS - "The system cannot find the file specified." |
| `schtasks /Query /TN <name> /V /FO LIST` | FAILS - "ERROR: The system cannot find the file specified." |
| Does the task actually fire? | YES - newest `C:\development\email-triage\logs\*_run.md` updates on schedule (e.g. `2026-07-04_18-30_run.md`, `Connected via no-WAM wrapper`, Exit code 0) |

So the task runs, but you cannot read its run history (`LastRunTime`/`NextRunTime`) or export its XML definition through the normal APIs.

## Root Cause Analysis (the important part - read carefully)

### Hypothesis A (from the track artifacts) - NOW KNOWN TO BE INCOMPLETE/WRONG
The Phase 3 `scheduled-task-remediation-proposal.md` states: *"its backing task-definition file/metadata cannot be read / is missing, producing the file not specified error."* This assumed the on-disk task file was absent.

### Hypothesis B (first-hand finding from THIS session) - the file EXISTS
Direct enumeration of the on-disk task folder PROVES the task definition file is present:

```
Folder: C:\Windows\System32\Tasks\OpenCode\
File:   opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort
Size:   4230 bytes
LastWriteTime: 6/16/2026 5:03:52 PM
Attributes: Archive
```

It sits alongside 23 sibling opencode-job task files that all read fine. So **"missing on-disk file" is NOT the cause.**

### Hypothesis C (refined, most likely) - Registry TaskCache GUID-index desync
Windows Task Scheduler stores tasks in TWO places that must stay in sync:
- **On-disk XML:** `C:\Windows\System32\Tasks\OpenCode\<name>` (present - confirmed).
- **Registry cache:** `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\`
  - `Tree\OpenCode\<name>` - holds the `Id` (GUID) pointer + `SD` (security descriptor).
  - `Tasks\{GUID}` - holds the full definition blob (`Path`, `Hash`, `Schema`, actions/triggers, etc.).

The classic "file not found" on a task that enumerates as Ready happens when **`Tree\<name>` exists (so enumeration works and shows Ready) but the `Tasks\{GUID}` blob it points to is missing/stale/mismatched** (so loading the full definition for info/export fails). The Task Scheduler service can still FIRE such a task because the runtime execution path can use the on-disk XML + Tree entry, but the management APIs require the GUID-indexed blob.

### Registry probe results from this session (INCONCLUSIVE - need elevation)
Non-elevated reads of the TaskCache returned empty (likely access-restricted, NOT proof of absence):
- `HKLM:\...\Schedule\TaskCache\Tree\OpenCode` - `Test-Path` = True, but `Get-ChildItem`/`Get-ItemProperty` returned nothing visible.
- `HKLM:\...\Schedule\TaskCache\Tasks` GUID scan for any entry whose `Path` matches this task name - returned "No ... GUID entry references this task name."

**Do NOT treat the empty registry output as "registry entry missing."** Reading TaskCache typically requires administrator elevation; the empty result is most likely a permissions artifact. **The new session's first action must be to re-run these probes ELEVATED** (see How to Diagnose below).

## Severity Assessment

**LOW.** Reasons:
- The task is firing correctly; email auto-sort runs on schedule.
- This is a metadata/read inconsistency, not a functional failure.
- It only blocks: reading run history, exporting the task XML, and any tooling that calls `Get-ScheduledTaskInfo`/`Export-ScheduledTask`.

Risk of leaving it: you cannot audit LastRunTime/NextRunTime or back up this task's definition via export. It may also indicate latent scheduler DB corruption that could affect other tasks.

## In Scope

- Confirm the root cause with **elevated** registry + on-disk inspection (resolve the Hypothesis-C vs permissions question).
- Determine whether the registry `Tasks\{GUID}` blob is missing, stale, or hash-mismatched vs the on-disk XML.
- Decide and propose a safe remediation (options below).
- If remediation is destructive (task delete/recreate), STOP and get explicit approval first (Tier-1).
- Document the finding and the chosen remediation in a Conductor track.

## Out of Scope / Non-Goals

- Do NOT change the scheduler cadence or the `*/15 * * * *` job JSON.
- Do NOT modify email-triage production logic.
- Do NOT rotate the Graph cert (healthy).
- Do NOT delete or recreate the scheduled task without explicit approval.
- Do NOT touch the other 23 healthy opencode-job tasks.
- Issue 1 (junction) and Issue 3 (bookkeeping) are DONE - do not revisit.

## How to Diagnose (concrete commands for the new session)

**Run these ELEVATED** (gsudo or an admin PowerShell). All read-only unless noted.

```powershell
$n = 'opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort'

# 1. Confirm on-disk XML exists and inspect it
Get-ChildItem -LiteralPath "$env:SystemRoot\System32\Tasks\OpenCode\$n" | Select FullName, Length, LastWriteTime
Get-Content -Raw -LiteralPath "$env:SystemRoot\System32\Tasks\OpenCode\$n"   # the task XML

# 2. Compare: enumerate vs read/export (the split behavior)
Get-ScheduledTask -TaskName $n | Format-List *
Get-ScheduledTaskInfo -TaskName $n        # expect: fails "file not specified"
Export-ScheduledTask -TaskName $n          # expect: fails "file not specified"

# 3. Registry Tree entry -> read the GUID pointer
$treeKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\OpenCode\$n"
Get-ItemProperty -LiteralPath $treeKey     # look at: Id (GUID), SD

# 4. Registry GUID blob -> the thing info/export needs
$guid = (Get-ItemProperty -LiteralPath $treeKey).Id   # GUID like {xxxxxxxx-....}
$blobKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks\$guid"
Test-Path -LiteralPath $blobKey            # if False => root cause CONFIRMED (blob missing)
Get-ItemProperty -LiteralPath $blobKey     # Path, Hash, Schema, etc.

# 5. Cross-check a HEALTHY sibling task the same way (control)
$good = 'opencode-job-development-88876ee600f5-knowledge-base-ingest'
$goodTree = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\development\$good"
# (adjust the Tree path to match the good task's TaskPath)

# 6. Task Scheduler service event log for this task
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; ID=100,101,102,103,203,404} -MaxEvents 50 -ErrorAction SilentlyContinue |
  Where-Object { $_.Message -like "*email-triage*" } | Select TimeCreated, Id, LevelDisplayName, Message
```

Interpretation:
- If step 4 `Test-Path` = **False** -> Hypothesis C confirmed: GUID blob missing. Remediation = recreate task or rebuild registry blob.
- If step 4 blob exists but `Hash`/`Path` mismatches the on-disk XML -> stale/mismatched blob. Remediation = re-register.
- If all registry reads are empty even elevated -> deeper Task Scheduler store corruption; consider `schtasks` re-registration.

## Proposed Remediation Options (safe -> destructive)

### Option 1 (preferred, least invasive) - Re-register from the on-disk XML
Re-import the existing on-disk XML via `Register-ScheduledTask -Xml` (after unregistering) OR `schtasks /Create /TN <name> /XML <file> /F`. This rewrites both the on-disk file and the registry cache from a known-good XML. **Re-export the on-disk XML first as a backup.** Still touches the task registration -> get approval, but it preserves the exact definition.

```powershell
# Backup first
Copy-Item "$env:SystemRoot\System32\Tasks\OpenCode\$n" "C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\$n.xml.bak"
# Re-register from the on-disk XML
schtasks /Create /TN $n /XML "$env:SystemRoot\System32\Tasks\OpenCode\$n" /F
# Verify the split behavior is gone
Get-ScheduledTaskInfo -TaskName $n
Export-ScheduledTask -TaskName $n
```

### Option 2 - Delete and recreate from a freshly-generated definition
Use the opencode-scheduler plugin to regenerate the task, or manually rebuild from `run-hidden.vbs` + the job JSON. Higher blast radius; only if Option 1 fails.

### Option 3 - Leave as-is, document
If root cause is benign and recreation risks more than it fixes, document and monitor. Acceptable given severity is LOW.

**All three require the new session to decide; destructive options need explicit user approval (Tier-1 stop).**

## Validation / Acceptance

- `Get-ScheduledTaskInfo -TaskName <name>` returns concrete `LastRunTime` / `NextRunTime` (no error).
- `Export-ScheduledTask -TaskName <name>` returns valid task XML.
- `schtasks /Query /TN <name> /V /FO LIST` succeeds.
- The task still fires on schedule afterward (a new `*_run.md` log appears at the next hourly tick).
- No other opencode-job task is disturbed (spot-check 1-2 siblings still read fine).
- Root cause documented with the elevated registry evidence (GUID blob present/missing, hash match/mismatch).

## Work Already Done (evidence artifacts)

- `C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-diagnostics.md` - Phase 3.1 output (Get-ScheduledTask success + the three failing APIs + empty on-disk recursive search).
- `C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-remediation-proposal.md` - Phase 3.2 output (Hypothesis A note + "approval required").
- Execution log Phase 3: `.\tracks\20260704-microsoft-graph-junction-repair\execution-log-2026-07-04.md` lines 25-27, 68, 72.
- Plan Phase 3 (Tasks 3.1, 3.2, checked off): `.\tracks\20260704-microsoft-graph-junction-repair\plan.md` lines 79-105.
- **This session's first-hand on-disk + registry probe** (non-elevated): confirms the file EXISTS (refines Hypothesis A); registry reads inconclusive (need elevation).

## Recommended Approach for the New Session

1. **Open a Conductor track** e.g. `C:\development\opencode\.conductor\tracks\20260704-scheduled-task-read-inconsistency\` (spec.md + plan.md + metadata.json) - this is a real, multi-step diagnostic + remediation, not a one-liner.
2. **Run the elevated diagnostics** (How to Diagnose above) FIRST. The single most important unknown is the state of the registry `Tasks\{GUID}` blob for this task - that confirms or refutes Hypothesis C.
3. Based on the finding, pick Option 1/2/3. **Stop and surface for approval before any delete/recreate** (Tier-1).
4. Validate against the acceptance checks above (esp. that the task still fires afterward).
5. If you re-register, back up the on-disk XML first and confirm no sibling task is affected.

## Environment Notes

- **File tools were failing this session** ("Bun is not defined"). The new session should probe a file op at start; if it still fails, go PowerShell-first via the `bash` tool (cmdlet map: Read -> `Get-Content -Raw -LiteralPath`, Write -> `Set-Content -Encoding utf8NoBOM -LiteralPath`, Edit -> `[string]::Replace()` as an INSTANCE method `$x.Replace('a','b')` - NOT the static `[string]::Replace()`, which does not exist).
- **Admin elevation:** TaskCache registry reads and `schtasks` re-registration need an elevated shell. Use `gsudo` if available (see `references\admin-elevation-gsudo.md`).
- Probe shell with `pwsh` (PowerShell 7), not Windows PowerShell 5.1.

## Next Steps

1. Re-run the registry/on-disk probes ELEVATED to resolve the Hypothesis-C vs permissions question.
2. Create the Conductor track and lock the root-cause finding.
3. Choose a remediation option; get approval if destructive.
4. Apply + validate (task reads fine AND still fires).

## Verdict

CONTINUE - independent diagnostic/fix ready for a fresh session. Low severity (task fires), but the metadata inconsistency blocks run-history auditing and task export, and may signal latent scheduler-store corruption. No successor session has resolved it.

## Handoff Artifact

- This file: `C:\development\opencode\.opencode\handoffs\20260704-2035-scheduled-task-read-inconsistency.md`

## New-Session Bootstrap

Start the new session with:

> Continue this work using the handoff doc at `C:\development\opencode\.opencode\handoffs\20260704-2035-scheduled-task-read-inconsistency.md`. The hourly email-triage scheduled task (`opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`) fires correctly but `Get-ScheduledTaskInfo`/`Export-ScheduledTask`/`schtasks /Query` all fail with "The system cannot find the file specified." First step: run the ELEVATED registry probes in the doc to confirm whether the `TaskCache\Tasks\{GUID}` blob is missing/stale (Hypothesis C) - the on-disk XML definitely EXISTS, so "missing file" is not the cause. Create a Conductor track, diagnose, and propose a safe remediation; get explicit approval before any task delete/recreate.
