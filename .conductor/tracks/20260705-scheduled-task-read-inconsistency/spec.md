# Scheduled Task Read Inconsistency - Spec

## Goal / Outcome
Nail the exact root cause of a Windows Task Scheduler metadata/read inconsistency for `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`, then propose and, only after explicit Tier-1 approval, apply the safest remediation that restores normal metadata reads while preserving the working hourly email-triage automation.

## Scope
- Diagnose only `\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`.
- Confirm/refute Hypothesis C with elevated evidence from `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\OpenCode\<name>` and `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks\{GUID}`.
- Compare TaskCache state with `C:\Windows\System32\Tasks\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`.
- Prefer Option 1 remediation: back up the on-disk XML, then re-register from that XML with `schtasks /Create /TN <name> /XML <file> /F`, only after explicit Tier-1 approval.
- If remediation cannot be safely applied in-run, document Option 3 monitoring as acceptable because severity is LOW.

## Constraints / Non-Goals
- Native file tools are broken; execution must be PowerShell-first through the `bash` tool using PowerShell 7.
- Use absolute Windows paths and `-LiteralPath` for PowerShell file operations.
- Bound every shell/network command with explicit timeouts or non-interactive flags; forbid `Read-Host`, `Wait-Process`/`-Wait`, `tail -f`, `Start-Process -Wait`, and uncapped servers.
- Do not delete/recreate, re-register, or otherwise touch task registration without explicit Tier-1 user approval.
- Do not change scheduler cadence or the `*/15 * * * *` job JSON.
- Do not modify email-triage production logic.
- Do not rotate the Microsoft Graph certificate.
- Do not touch the other 23 healthy `opencode-job` tasks except read-only spot checks.
- Do not duplicate existing evidence artifacts; reference them by path.

## Definition of Done
- Elevated diagnostics document whether the Tree entry exists, what GUID it points to, and whether `Tasks\{GUID}` is present, missing, stale, or hash/path mismatched.
- Root cause is documented with elevated evidence and interpretation.
- If approval is granted and remediation is applied, `Get-ScheduledTaskInfo`, `Export-ScheduledTask`, and `schtasks /Query /TN ... /V /FO LIST` all succeed for the target task.
- If the next hourly tick can be observed in-run, a fresh `C:\development\email-triage\logs\*_run.md` log appears after remediation; otherwise this is recorded as a follow-up verification.
- One or two sibling `opencode-job` scheduled tasks are spot-checked read-only and remain healthy.
- If approval is not granted or remediation is deferred, the track records the recommended option, exact approval needed, and follow-up checks.

## Severity
LOW. The scheduled task is firing correctly and email auto-sort is functional; the issue blocks metadata reads, export, and run-history auditing.

## Target Task Details
- TaskName: `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
- TaskPath: `\OpenCode\`
- URI: `\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
- Action: invokes `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1` via headless VBS launcher.
- Trigger: hourly.
- Known on-disk XML path: `C:\Windows\System32\Tasks\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`

## Leading Hypothesis
Hypothesis C: Windows Task Scheduler TaskCache is desynchronized. `TaskCache\Tree\OpenCode\<name>` may exist, allowing enumeration and Ready state, while the pointed `TaskCache\Tasks\{GUID}` blob may be missing, stale, or mismatched, causing `Get-ScheduledTaskInfo`, `Export-ScheduledTask`, and `schtasks /Query /V` to fail with “The system cannot find the file specified.” Prior non-elevated TaskCache reads were inconclusive and must not be treated as proof of absence.

## Existing Evidence References
- `C:\development\opencode\.opencode\handoffs\20260704-2035-scheduled-task-read-inconsistency.md`
- `C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-diagnostics.md`
- `C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\scheduled-task-remediation-proposal.md`
- `C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\execution-log-2026-07-04.md`
- `C:\development\opencode\.conductor\tracks\20260704-microsoft-graph-junction-repair\plan.md`
