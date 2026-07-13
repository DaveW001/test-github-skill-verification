---
name: google-drive-reference
description: Comprehensive gws CLI command reference for Google Drive and Google Docs operations.
---

# Google Drive & Docs — Command Reference

Complete copy-paste-ready command examples for the `gws` CLI covering Google Drive, Google Docs, Google Calendar, Google Contacts, and Gmail operations. For Outlook/Microsoft operations, see the `outlook-inbox-triage` and `calendar-schedule` skills instead.

## Drive Files Commands

List files (first 10):
```bash
gws drive files list --params '{"pageSize": 10}' --format table
```

List all files (paginated, JSON output):
```bash
gws drive files list --params '{"pageSize": 50}' --page-all --format json
```

Search by name:
```bash
gws drive files list --params '{"q": "name contains \"search-term\""}' --format table
```

List only Google Docs:
```bash
gws drive files list --params '{"q": "mimeType = \"application/vnd.google-apps.document\""}' --format table
```

Get file metadata:
```bash
gws drive files get --params '{"fileId": "FILE_ID"}' --format json
```

Download a file:
```bash
gws drive files get --params '{"fileId": "FILE_ID"}' --output "./output-file"
```

List file permissions:
```bash
gws drive permissions list --params '{"fileId": "FILE_ID"}' --format table
```

## Drive Upload Commands

Upload a file to root Drive:
```bash
gws drive +upload --upload "./local-file.pdf" --params '{"name": "uploaded-file.pdf"}'
```

Upload with explicit MIME type:
```bash
gws drive +upload --upload "./local-file.pdf" --upload-content-type "application/pdf" --params '{"name": "uploaded-file.pdf"}'
```

Upload to a specific folder:
```bash
gws drive +upload --upload "./local-file.pdf" --params '{"name": "uploaded-file.pdf", "parents": ["FOLDER_ID"]}'
```

## Drive Folders and Shared Drives

List all folders:
```bash
gws drive files list --params '{"q": "mimeType = \"application/vnd.google-apps.folder\""}' --format table
```

List files inside a specific folder:
```bash
gws drive files list --params '{"q": "\"FOLDER_ID\" in parents"}' --format table
```

List shared drives:
```bash
gws drive drives list --format table
```

List files in a shared drive:
```bash
gws drive files list --params '{"driveId": "DRIVE_ID", "includeItemsFromAllDrives": true, "supportsAllDrives": true}' --format table
```

## Google Docs Commands

Get document content as JSON:
```bash
gws docs documents get --params '{"documentId": "DOC_ID"}' --format json
```

Write text into a document (append at position 1):
```bash
gws docs +write --params '{"documentId": "DOC_ID"}' --json '{"requests": [{"insertText": {"location": {"index": 1}, "text": "Hello World"}}]}'
```

## Drive Query Syntax Reference

| Query | Description |
|---|---|
| `name contains 'filename'` | Match files whose name contains a substring |
| `mimeType = 'application/vnd.google-apps.document'` | Filter by MIME type (Docs, Sheets, etc.) |
| `'FOLDER_ID' in parents` | List files inside a folder |
| `modifiedTime > '2026-01-01T00:00:00'` | Filter by modification date |
| `starred = true` | Only starred files |
| `trashed = false` | Exclude trashed files (default in most queries) |
| `sharedWithMe = true` | Files shared with the authenticated user |


## Calendar Commands

List events (next 10):
```bash
gws calendar events list --params '{"calendarId": "primary", "maxResults": 10}' --format table
```

List events for a specific date range:
```bash
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2026-05-11T00:00:00Z", "timeMax": "2026-05-12T00:00:00Z", "singleEvents": true}' --format table
```

Get a specific event:
```bash
gws calendar events get --params '{"calendarId": "primary", "eventId": "EVENT_ID"}' --format json
```

Create an event:
```bash
gws calendar +insert --summary "Meeting" --start "2026-05-12T10:00:00" --end "2026-05-12T11:00:00"
```

Show upcoming agenda:
```bash
gws calendar +agenda
```

Show agenda with specific timezone:
```bash
gws calendar +agenda --timezone "America/New_York"
```

List all calendars:
```bash
gws calendar calendars list --format json
```


## People Commands

Get your own profile:
```bash
gws people people get --params '{"resourceName": "people/me", "personFields": "names,emailAddresses"}' --format json
```

List your contacts:
```bash
gws people connections list --params '{"resourceName": "people/me", "pageSize": 10, "personFields": "names,emailAddresses"}' --format json
```

List other contacts (auto-complete suggestions):
```bash
gws people otherContacts list --params '{"pageSize": 10, "readMask": "names,emailAddresses"}' --format json
```


## Gmail Commands

List recent messages:
```bash
gws gmail users messages list --params '{"userId": "me", "maxResults": 5}' --format json
```

Get a specific message (metadata only):
```bash
gws gmail users messages get --params '{"userId": "me", "id": "MESSAGE_ID", "format": "metadata"}' --format json
```

List threads:
```bash
gws gmail users threads list --params '{"userId": "me", "maxResults": 5}' --format json
```

List labels:
```bash
gws gmail users labels list --params '{"userId": "me"}' --format json
```

Send an email:
```bash
gws gmail +send --to "recipient@example.com" --subject "Hello" --body "Message text"
```

Reply to a message:
```bash
gws gmail +reply --message-id "MESSAGE_ID" --body "Thanks!"
```

Triage unread inbox:
```bash
gws gmail +triage --max 10
```


## Gmail Query Syntax Reference

Use Gmail search queries with the `q` parameter in `gws gmail users messages list`:

```bash
gws gmail users messages list --params '{"userId": "me", "q": "is:unread"}' --format json
```

| Query | Description |
|---|---|
| `is:unread` | Unread messages |
| `from:sender@example.com` | Messages from a specific sender |
| `to:recipient@example.com` | Messages to a specific recipient |
| `subject:"meeting notes"` | Messages with a subject containing text |
| `after:2026/05/01` | Messages received after a date |
| `before:2026/05/31` | Messages received before a date |
| `has:attachment` | Messages with attachments |
| `in:inbox` | Messages in the inbox |
| `label:important` | Messages with a specific label |
