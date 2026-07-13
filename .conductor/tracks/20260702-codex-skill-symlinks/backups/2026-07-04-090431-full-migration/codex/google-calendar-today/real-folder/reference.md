# Google Calendar Today — Tool Reference

## Google MCP Tools Used

All tools are from the `mcp-google` MCP server, configured as `mcp.google` in `opencode.json`.

### list-calendars

List user calendars. Returns array of calendar objects with id, summary, accessRole, backgroundColor, primary.

**Parameters:** None required.

**Example:**
```json
{}
```

**Response shape:**
```json
[
  {
    "id": "dave.witkin@packagedagile.com",
    "summary": "Dave Witkin",
    "primary": true,
    "accessRole": "owner",
    "backgroundColor": "#9a9cff"
  }
]
```

### list-events

List calendar events. Returns array of event objects with id, summary, start, end, status, recurrence. Supports batch (up to 50 calendars).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `calendarId` | string | no | - | ID of a single calendar |
| `calendarIds` | array | no | - | Array of calendar IDs |
| `timeMin` | string | yes | - | Start time in ISO format with timezone (e.g., `2024-01-01T00:00:00Z`) |
| `timeMax` | string | yes | - | End time in ISO format with timezone (e.g., `2024-12-31T23:59:59Z`) |
| `timeZone` | string | no | UTC | Timezone for response |

**Example — Today's events:**
```json
{
  "calendarId": "primary",
  "timeMin": "2026-04-29T00:00:00Z",
  "timeMax": "2026-04-30T00:00:00Z",
  "timeZone": "America/New_York"
}
```

### get-freebusy

Check calendar availability. Returns busy time blocks per calendar.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timeMin` | string | yes | - | Start of interval (RFC3339) |
| `timeMax` | string | yes | - | End of interval (RFC3339) |
| `timeZone` | string | no | UTC | Timezone for response |
| `items` | array | yes | - | Calendar identifiers to check |
| `items[].id` | string | yes | - | Calendar or group identifier (usually email format) |

**Example:**
```json
{
  "timeMin": "2026-04-29T00:00:00Z",
  "timeMax": "2026-04-30T00:00:00Z",
  "timeZone": "America/New_York",
  "items": [
    { "id": "dave.witkin@packagedagile.com" }
  ]
}
```
