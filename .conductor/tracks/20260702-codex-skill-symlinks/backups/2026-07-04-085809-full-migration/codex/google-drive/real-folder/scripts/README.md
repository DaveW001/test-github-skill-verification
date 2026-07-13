# Google Drive Python Scripts

Helper scripts for batch Google Drive and Google Docs operations. These scripts wrap the `gws` CLI via `subprocess` and do not implement OAuth directly.

## Dependencies

- Python 3.10+
- `gws` CLI installed (`~/.cargo/bin/gws.exe`)
- Google API Python client (for future direct-API use): `pip install google-api-python-client google-auth google-auth-oauthlib`

## Auth

All scripts inherit auth from the `gws` CLI. Check auth status first:

```bash
gws auth status
```

If auth is not configured, run:

```bash
gws auth login
```

## Scripts

### drive-list.py

List Google Drive files.

```bash
# Search by name
python drive-list.py --query "name contains 'report'" --output files.json

# List with custom page size
python drive-list.py --page-size 50 --output all-files.json

# Dry run (show command without executing)
python drive-list.py --query "name contains 'report'" --dry-run
```

### drive-download.py

Download a file from Google Drive by its file ID.

```bash
# Download a file
python drive-download.py --file-id FILE_ID --output ./downloaded-file

# Dry run
python drive-download.py --file-id FILE_ID --output ./downloaded-file --dry-run
```

### docs-export.py

Export a Google Doc as JSON (v1 — full markdown conversion is a future enhancement).

```bash
# Export to file
python docs-export.py --document-id DOC_ID --output doc.json

# Print to stdout
python docs-export.py --document-id DOC_ID

# Dry run
python docs-export.py --document-id DOC_ID --output doc.json --dry-run
```


### calendar-list.py

List Google Calendar events for a date range.

```bash
# List events for the next 7 days
python calendar-list.py --days 7 --output events.json

# List events for a specific calendar
python calendar-list.py --calendar-id "primary" --days 30 --output month.json

# Dry run
python calendar-list.py --days 7 --dry-run
```

### gmail-triage.py

Triage Gmail messages with optional search query.

```bash
# Triage 20 most recent messages
python gmail-triage.py --max 20 --output triage.json

# Triage unread messages only
python gmail-triage.py --query "is:unread" --max 10

# Dry run
python gmail-triage.py --max 10 --dry-run
```
