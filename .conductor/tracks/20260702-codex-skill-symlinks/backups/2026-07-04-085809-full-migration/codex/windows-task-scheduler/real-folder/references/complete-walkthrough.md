# Complete Walkthrough (Prompting Example)

```text
User: I want to create a new scheduled task.

Assistant: I can help. I need a few details:

1) Task name:
2) Description (what it does + why it exists):
3) Command/script to run:
4) Arguments (optional):
5) Working directory (optional):
6) Schedule (daily/weekly/every X days/weekdays/startup/logon) + time if applicable:
7) Run As account (current user/SYSTEM/service account):
8) Documentation path (optional):

User:
1) DatabaseBackup
2) Backs up production database to S3 for disaster recovery
3) C:/scripts/backup-database.ps1
4) -Environment prod
5) C:/scripts
6) Daily at 2:00 AM
7) SERVICE_ACCOUNT
8) C:/docs/backup-procedure.md

Assistant:
- Validate paths exist (script + working directory)
- Create action + trigger using ScheduledTasks
- Register the task with the description
- Verify: show task, trigger, and description
- Optional: run once manually for a smoke test
```
