# Root Cause Evidence - Scheduled Task Read Inconsistency

> Elevated diagnostic run: 2026-07-05 (local) via gsudo v2.6.1, executor zai-coding-plan/glm-5.2.
> Target: `\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`

## Elevated TaskCache Evidence
- Tree key exists: True
- Tree Id GUID: {2672E99F-EAE1-44C0-BE42-00008616B728}
- Tasks GUID blob exists: True
- Blob Path: \OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort
- Blob Hash length: 32 bytes (present, non-zero)
- Blob Schema: 65539
- Blob Actions stream: present (106 chars decoded)

## Elevated API Behavior
- Get-ScheduledTask: OK - State = Ready
- Get-ScheduledTaskInfo: OK - LastRunTime=2026-07-05T12:00:01-04:00, NextRunTime=2026-07-05T12:15:00-04:00
- Export-ScheduledTask: OK - returns valid 1609-char `<Task version="1.3">` XML (UTF-16)
- schtasks /Query /V /FO LIST: OK

**All three previously-failing APIs now SUCCEED.** The read/export "The system cannot find the file specified" split behavior documented in the 2026-07-04 handoff is NO LONGER REPRODUCIBLE.

## On-Disk XML Evidence
- XML path: C:\Windows\System32\Tasks\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort
- XML root: <Task>
- XML length: 4230 bytes (2114 raw chars)
- LastWriteTime: 2026-06-16T17:03:52-04:00
- Action: `wscript.exe //B "C:\development\email-triage\scripts\run-hidden.vbs"` (VBS launcher wraps the ps1)
- Trigger: TimeTrigger, RepetitionInterval PT15M, Enabled=true

## Sibling Controls
- Sibling read checks: 3/3 OK (daily-failure-digest, daily-intake-scan, daily-review-queue-health) - no disturbance

## Firing Evidence (live, post-diagnostic)
- Newest run log `2026-07-05_12-00_run.md`: Exit code 0, Status: success (895B)
- 15-minute cadence confirmed (11:30, 11:45, 12:00 run logs all present)

## Interpretation
- Root-cause branch: **no current inconsistency**
  - Hypothesis C (missing/stale/mismatched `TaskCache\Tasks\{GUID}` blob) is REFUTED as a current condition.
  - The GUID blob exists, its Path matches the task URI, its Hash/Schema/Actions are populated, and all read/export APIs succeed.
  - The inconsistency reported as of 2026-07-04 (non-elevated reads inconclusive; APIs failing) is no longer present as of 2026-07-05 elevated re-probe. The most probable repair mechanism is that the Task Scheduler service rebuilt/synchronized the TaskCache from the on-disk XML (service restart, cache self-heal, or a prior session's action) between 2026-07-04 and 2026-07-05; the exact trigger is not determinable from available evidence and is not material - the current state is provably healthy.
  - Note: the prior non-elevated empty registry reads were confirmed (per handoff caveat) to be a permissions artifact, NOT proof of a missing blob - this is now definitively resolved by the elevated probe.
- Recommended remediation: **Option 3** - document and monitor; NO registration touch (no `schtasks /Create`, no delete/recreate). There is nothing to remediate: the target reads correctly, exports correctly, and fires correctly on its 15-minute cadence. A re-registration would carry needless blast radius against a task that is demonstrably healthy.
