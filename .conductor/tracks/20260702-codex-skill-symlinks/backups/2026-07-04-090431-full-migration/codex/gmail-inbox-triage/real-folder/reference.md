# Gmail Inbox Triage — Tool Reference

## Google MCP Tools Used

All tools are from the `mcp-google` MCP server, configured as `mcp.google` in `opencode.json`.

### list-emails

Search emails in Gmail. Returns array with `id` and `threadId` only (no content/labels).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | no | - | Gmail search operators (see below) |
| `maxResults` | number | no | 20 | Max emails to return (max 500) |
| `pageToken` | string | no | - | Pagination token |
| `includeSpamTrash` | boolean | no | false | Include SPAM and TRASH |
| `labelIds` | array | no | - | Filter by specific label IDs |

**Gmail Search Operators:**
- `from:email@domain.com` — sender filter
- `to:email` — recipient filter
- `subject:text` — subject filter
- `is:unread` / `is:read` — read status
- `is:starred` / `is:important` — importance
- `has:attachment` — has attachments
- `in:inbox` / `in:sent` — location
- `after:2024/1/1` / `before:2024/12/31` — date range
- `larger:1M` / `smaller:5M` — size filter
- Combine with spaces for AND, `OR` for alternatives

**Example:**
```json
{
  "query": "in:inbox is:unread",
  "maxResults": 15
}
```

### get-email

Retrieve one email by messageId. Returns full message with headers, body (plain/html), attachments metadata.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `messageId` | string | yes | - | The ID from list-emails |
| `markAsRead` | boolean | no | true | Mark as read when retrieving |
| `format` | string | no | "full" | Message format |

**Example:**
```json
{
  "messageId": "abc123xyz",
  "markAsRead": false
}
```

### update-email

Modify single email labels/status. Returns updated message with new labelIds.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `messageId` | string | yes | - | Message ID from list-emails |
| `addLabelIds` | array | no | - | Labels to add: UNREAD, STARRED, IMPORTANT, INBOX, SPAM, TRASH |
| `removeLabelIds` | array | no | - | Labels to remove: UNREAD, STARRED, IMPORTANT, INBOX |
| `markAsRead` | boolean | no | false | Shortcut: remove UNREAD label |
| `markAsUnread` | boolean | no | false | Shortcut: add UNREAD label |
| `star` | boolean | no | false | Star the email |
| `unstar` | boolean | no | false | Unstar the email |
| `archive` | boolean | no | false | Remove from inbox |
| `unarchive` | boolean | no | false | Add to inbox |

**Example — Archive an email:**
```json
{
  "messageId": "abc123xyz",
  "archive": true
}
```

**Example — Star for later:**
```json
{
  "messageId": "abc123xyz",
  "star": true,
  "removeLabelIds": ["UNREAD"]
}
```

### list-labels

List all Gmail labels. Returns array of label objects with id, name, type.

**Example:**
```json
{}
```

### batch-update-emails

Update multiple emails at once. Same parameters as update-email but accepts arrays of messageIds.

**Example — Mark multiple as read:**
```json
{
  "messageIds": ["id1", "id2", "id3"],
  "markAsRead": true
}
```
