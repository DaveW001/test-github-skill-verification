# Google Calendar Schedule — Tool Reference

## Google MCP Tools Used

All tools are from the `mcp-google` MCP server, configured as `mcp.google` in `opencode.json`.

### list-calendars

List user calendars. Returns array with id, summary, accessRole, backgroundColor, primary.

**Parameters:** None required.

### list-events

List calendar events. Returns array of event objects with id, summary, start, end, status, recurrence.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `calendarId` | string | no | Single calendar ID |
| `calendarIds` | array | no | Array of calendar IDs (up to 50) |
| `timeMin` | string | yes | Start time ISO with tz |
| `timeMax` | string | yes | End time ISO with tz |
| `timeZone` | string | no | Timezone (IANA format) |

### search-events

Search events by text. Searches summary, description, location, attendees.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `calendarId` | string | yes | Calendar ID ('primary' for main) |
| `query` | string | yes | Free text search query |
| `timeMin` | string | no | Start boundary ISO with tz |
| `timeMax` | string | no | End boundary ISO with tz |

**Example — Find meeting with John:**
```json
{
  "calendarId": "primary",
  "query": "John"
}
```

### create-event

Create calendar event. Returns created event with id, htmlLink, start, end, status.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `calendarId` | string | yes | Calendar ID ('primary' for main) |
| `summary` | string | yes | Title of the event |
| `start` | string | yes | Start time ISO with tz |
| `end` | string | yes | End time ISO with tz |
| `timeZone` | string | yes | IANA timezone (e.g., America/New_York) |
| `description` | string | no | Description/notes |
| `location` | string | no | Location |
| `attendees` | array | no | Attendee objects with `email` field |
| `colorId` | string | no | Color ID (use list-colors for options) |
| `recurrence` | array | no | RRULE strings in RFC5545 format |

**Example — Simple meeting:**
```json
{
  "calendarId": "primary",
  "summary": "1:1 with Sarah",
  "start": "2026-04-29T14:00:00",
  "end": "2026-04-29T14:30:00",
  "timeZone": "America/New_York",
  "attendees": [{"email": "sarah@example.com"}],
  "location": "Zoom"
}
```

**Example — Recurring weekly:**
```json
{
  "calendarId": "primary",
  "summary": "Team Standup",
  "start": "2026-04-29T09:00:00",
  "end": "2026-04-29T09:30:00",
  "timeZone": "America/New_York",
  "recurrence": ["RRULE:FREQ=WEEKLY;COUNT=12"]
}
```

### update-event

Modify existing event. Returns updated event.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `calendarId` | string | yes | Calendar containing the event |
| `eventId` | string | yes | Event ID to update |
| `summary` | string | no | New title |
| `start` | string | no | New start time ISO with tz |
| `end` | string | no | New end time ISO with tz |
| `timeZone` | string | no | Timezone for start/end |
| `description` | string | no | New description |
| `location` | string | no | New location |
| `attendees` | array | no | New attendees (replaces existing) |
| `colorId` | string | no | New color ID |
| `recurrence` | array | no | New recurrence rules |
| `modificationScope` | string | no | 'single', 'all', or 'future' |
| `originalStartTime` | string | no | Required if scope is 'single' |

### delete-event

Remove event from calendar. Permanent deletion.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `calendarId` | string | yes | Calendar containing the event |
| `eventId` | string | yes | Event ID to delete |

### get-freebusy

Check calendar availability. Returns busy time blocks.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `timeMin` | string | yes | Start of interval (RFC3339) |
| `timeMax` | string | yes | End of interval (RFC3339) |
| `timeZone` | string | no | Response timezone |
| `items` | array | yes | Calendar identifiers |
| `items[].id` | string | yes | Calendar email/ID |

**Example — Find free slots this week:**
```json
{
  "timeMin": "2026-04-29T00:00:00Z",
  "timeMax": "2026-05-03T23:59:59Z",
  "timeZone": "America/New_York",
  "items": [{"id": "dave.witkin@packagedagile.com"}]
}
```

### list-colors

Get color palette for events and calendars. Returns event colors (1-11) and calendar colors.

**Parameters:** None required.
