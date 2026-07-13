# Gmail Draft Reply — Tool Reference

## Google MCP Tools Used

All tools are from the `mcp-google` MCP server, configured as `mcp.google` in `opencode.json`.

### get-email

Retrieve one email by messageId. Returns full message with headers, body (plain/html), attachments metadata.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `messageId` | string | yes | - | The ID from list-emails |
| `markAsRead` | boolean | no | true | Mark as read when retrieving |
| `format` | string | no | "full" | Message format |

### create-draft

Create unsent email draft. Returns draft id and message.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `to` | array of strings | yes | - | Recipient email address(es) |
| `subject` | string | yes | - | Email subject line |
| `body` | string | yes | - | Email body content |
| `cc` | array of strings | no | - | CC recipient addresses |
| `bcc` | array of strings | no | - | BCC recipient addresses |
| `isHtml` | boolean | no | false | Whether body is HTML |
| `replyToMessageId` | string | no | - | Message ID to reply to (for threading) |
| `threadId` | string | no | - | Thread ID to reply within |

**Example — New draft:**
```json
{
  "to": ["recipient@example.com"],
  "subject": "Re: Project update",
  "body": "Thanks for the update. Let me review and get back to you by Friday.",
  "isHtml": false
}
```

**Example — Reply draft (threaded):**
```json
{
  "to": ["sender@example.com"],
  "subject": "Re: Project update",
  "body": "<p>Thanks for the update. Let me review and get back to you by Friday.</p>",
  "isHtml": true,
  "replyToMessageId": "msg123abc",
  "threadId": "thread456def"
}
```

### update-draft

Modify an existing draft.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `draftId` | string | yes | - | Draft ID from create-draft response |
| `to` | array of strings | no | - | Updated recipients |
| `subject` | string | no | - | Updated subject |
| `body` | string | no | - | Updated body |
| `cc` | array of strings | no | - | Updated CC |
| `bcc` | array of strings | no | - | Updated BCC |
| `isHtml` | boolean | no | false | Whether body is HTML |

### send-draft

Send an existing draft.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `draftId` | string | yes | - | Draft ID to send |

### send-email

Send new email or reply directly (bypass draft). Returns sent message id and threadId.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `to` | array of strings | yes | - | Recipient addresses |
| `subject` | string | yes | - | Subject line |
| `body` | string | yes | - | Body content |
| `cc` | array of strings | no | - | CC addresses |
| `bcc` | array of strings | no | - | BCC addresses |
| `isHtml` | boolean | no | false | Whether body is HTML |
| `replyToMessageId` | string | no | - | Message ID to reply to |
| `threadId` | string | no | - | Thread ID for reply |

### list-emails

Used to find the original message when only subject/sender is known.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | no | - | Gmail search operators |
| `maxResults` | number | no | 20 | Max results |
