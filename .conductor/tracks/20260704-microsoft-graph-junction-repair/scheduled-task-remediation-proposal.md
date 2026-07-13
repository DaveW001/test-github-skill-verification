# Scheduled Task Remediation Proposal

## Evidence (from scheduled-task-diagnostics.md)
- `Get-ScheduledTask` returns the task with State=Ready under path `\OpenCode\`.
- `Get-ScheduledTaskInfo` and `Export-ScheduledTask` both fail with: "The system cannot find the file specified."
- This indicates an inconsistent registration: the task is enumerated but its on-disk metadata is missing/inaccessible.

## Root cause finding
The scheduled task is registered in the scheduler enum but its backing task-definition file/metadata cannot be read, producing the "file not specified" error for info/export calls. This is documented here before any remediation.

## Safe remediation proposal
do not delete or recreate the task without explicit user approval.

## Approval required before destructive task changes: yes
