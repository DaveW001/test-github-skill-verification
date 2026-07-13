# Task Description Guidance

## What to Include

Aim to include:
- What it does
- Why it exists
- Expected benefit/impact
- Cadence (when/how often it runs)
- Where the operational docs live

## Bad Descriptions

- "Indexer"
- "Run script"
- "Auto backup"

## Good Descriptions

- "Indexes active development projects for semantic search. Runs daily at 7:30 AM to keep results current. See ~/.opencode/osgrep-indexer/README.md"

- "Daily database backup for production. Uploads encrypted Postgres dumps to S3 nightly at 2:00 AM; retains 7 days. See C:/docs/backup-procedure.md"

- "Weekly cleanup of temp files. Runs Saturdays at 3:00 PM; deletes items older than 30 days. See C:/docs/maintenance-guide.md"
