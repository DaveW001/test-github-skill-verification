# Slack API Reference

Detailed reference for the Slack Web API methods used in this workspace.
Based on official Slack docs (docs.slack.dev) and our production usage in
`conductor-reporter` (Python) and `email-triage` (PowerShell).

## Authentication

All Slack Web API calls use a **Bearer token** in the `Authorization` header:

```
Authorization: Bearer xoxb-XXXXXXXXXXXXXXXXXXXXXXXX
```

### Token Types

| Prefix | Type | Use Case |
|--------|------|----------|
| `xoxb-` | Bot token | Most automation. Acts as the bot/app. **This is what we use.** |
| `xoxp-` | User token | Acts as the authenticated user. Used by the MCP slack-messaging skill. |
| `xoxo-` | App-level token | Socket Mode / Events API connections only |

This skill uses `xoxb-` (bot token). Messages appear as the bot/app, not a human.

### Required OAuth Scopes

| Scope | Purpose |
|-------|---------|
| `chat:write` | Send messages via `chat.postMessage` |
| `im:write` | Open DMs via `conversations.open` |
| `im:history` | Read DM history (optional) |
| `files:write` | Upload files via the new 3-step API |
| `chat:write.public` | Post to channels the bot hasn't joined |
| `chat:write.customize` | Override bot username/icon per message |

Configure scopes in the Slack App settings page (api.slack.com/apps).

---

## chat.postMessage

**Docs:** https://docs.slack.dev/reference/methods/chat.postMessage

Sends a message to a channel, DM, or thread.

### Request

```
POST https://slack.com/api/chat.postMessage
Content-Type: application/json
Authorization: Bearer {bot_token}
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel` | string | yes | Channel ID (`C...`), DM channel ID (`D...`), user ID (`U...`), or name (`#channel`) |
| `text` | string | recommended | Plain text fallback. Always include even with blocks - shown in notifications/previews. |
| `blocks` | array | no | Block Kit blocks (max 50, ~40,000 chars total). See Block Kit section. |
| `thread_ts` | string | no | Timestamp of parent message to reply in thread |
| `mrkdwn` | boolean | no | `true` (default) to render Slack mrkdwn formatting |
| `unfurl_links` | boolean | no | `false` to suppress link previews (default `true`) |
| `unfurl_media` | boolean | no | `false` to suppress media previews |
| `link_names` | boolean | no | `true` to convert `@username` and `#channel` into links |
| `username` | string | no | Override bot display name (requires `chat:write.customize`) |
| `icon_emoji` | string | no | Override bot icon with emoji (e.g. `:bell:`) |

### Response

```json
{
  "ok": true,
  "channel": "D02TRMSH535",
  "ts": "1700000000.000100",
  "message": {
    "text": "Hello!",
    "username": "Conductor Reporter",
    "type": "message",
    "subtype": "bot_message",
    "ts": "1700000000.000100"
  }
}
```

**Save `ts` and `channel`** from the response. You need both to:
- Reply in a thread (`thread_ts` = parent `ts`)
- Update the message (`chat.update`)
- Delete the message (`chat.delete`)

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `invalid_auth` | Token invalid or expired | Verify `xoxb-` prefix; run `auth.test` |
| `channel_not_found` | Invalid channel ID | Open DM first with `conversations.open` |
| `not_in_channel` | Bot not a member | Invite bot to channel |
| `missing_scope` | Token lacks `chat:write` | Add scope in app settings |
| `rate_limited` | Too many messages | Honor `Retry-After` header |
| `no_text` | Empty `text` and `blocks` | Provide at least one |

---

## auth.test

**Docs:** https://docs.slack.dev/reference/methods/auth.test

Validates a token and returns the authenticated identity. Use this to verify a
token works before sending messages.

### Request

```
GET https://slack.com/api/auth.test
Authorization: Bearer {bot_token}
```

### Response

```json
{
  "ok": true,
  "url": "https://workspace.slack.com/",
  "team": "Workspace Name",
  "user": "conductor-reporter",
  "team_id": "TXXXXXXXX",
  "user_id": "U02TRMSH535",
  "bot_id": "BXXXXXXXX"
}
```

---

## conversations.open

**Docs:** https://docs.slack.dev/reference/methods/conversations.open

Opens or resumes a direct message channel with one or more users. Required to
get the DM channel ID (`D...`) needed for file uploads.

### Request

```
POST https://slack.com/api/conversations.open
Content-Type: application/json
Authorization: Bearer {bot_token}
```

```json
{"users": "U02TRMSH535"}
```

### Response

```json
{
  "ok": true,
  "channel": {
    "id": "D02TRMSH535ABC",
    "user": "U02TRMSH535",
    "is_im": true
  }
}
```

Use `channel.id` (starts with `D`) for file uploads and message targeting.

---

## File Upload (New 3-Step API)

> `files.upload` was **sunset November 12, 2025**. All apps must use this flow.
> Source: https://docs.slack.dev/changelog/2024-04-a-better-way-to-upload-files-is-here-to-stay

### Step 1: Get Upload URL (`files.getUploadURLExternal`)

**Docs:** https://docs.slack.dev/reference/methods/files.getUploadURLExternal

```
POST https://slack.com/api/files.getUploadURLExternal
Content-Type: application/x-www-form-urlencoded
Authorization: Bearer {bot_token}

filename={filename}&length={file_size_bytes}
```

Optional: `alt_text` (image description), `snippet_type` (syntax highlight: `python`, `json`, etc.)

### Response

```json
{
  "ok": true,
  "upload_url": "https://files.slack.com/upload/v1/...",
  "file_id": "FXXXXXXXXXX"
}
```

### Step 2: Upload File to URL

POST the raw file bytes (or multipart form) to the `upload_url`:

```
POST {upload_url}
Content-Type: multipart/form-data

file: <file bytes>
```

Expect HTTP 200 on success. No JSON body - just the status code.

### Step 3: Complete Upload (`files.completeUploadExternal`)

**Docs:** https://docs.slack.dev/reference/methods/files.completeUploadExternal

```
POST https://slack.com/api/files.completeUploadExternal
Content-Type: application/json
Authorization: Bearer {bot_token}
```

```json
{
  "files": [{"id": "FXXXXXXXXXX", "title": "report.md"}],
  "channel_id": "D02TRMSH535ABC",
  "initial_comment": "Full detailed report attached"
}
```

`channel_id` and `initial_comment` are optional. Without `channel_id`, the file
is private (only visible to the uploader). `initial_comment` adds a caption.

---

## chat.update

**Docs:** https://docs.slack.dev/reference/methods/chat.update

Updates an existing message. Use this to edit status messages instead of reposting.

```
POST https://slack.com/api/chat.update
Content-Type: application/json
Authorization: Bearer {bot_token}
```

```json
{
  "channel": "D02TRMSH535ABC",
  "ts": "1700000000.000100",
  "text": "Updated: All systems operational"
}
```

---

## chat.delete

**Docs:** https://docs.slack.dev/reference/methods/chat.delete

Deletes a message.

```json
{"channel": "D02TRMSH535ABC", "ts": "1700000000.000100"}
```

---

## Block Kit Reference

**Docs:** https://docs.slack.dev/block-kit

Block Kit is Slack's structured layout system for rich messages. Passed as a
`blocks` array in `chat.postMessage`.

### Common Block Types

| Type | Use Case |
|------|----------|
| `section` | Text block (supports mrkdwn or plain_text) |
| `divider` | Horizontal rule |
| `header` | Bold header text |
| `context` | Small secondary text (metadata, timestamps) |
| `actions` | Interactive buttons |
| `image` | Inline image |
| `input` | Form fields (in modals) |

### Section Block Example

```json
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "*New Alert*\nService: checkout-api\nStatus: *DOWN*"
  }
}
```

### Limits

- Maximum 50 blocks per message
- Total payload ~40,000 characters
- Always include `text` fallback (used in notifications when blocks can't render)

---

## Rate Limits (Full Detail)

**Docs:** https://docs.slack.dev/apis/web-api/rate-limits

Slack rate-limits per method, per workspace, using a tier system:

| Tier | Approx. Limit | Methods |
|------|---------------|---------|
| Tier 1 | ~1 req/min | `users.list`, `channels.history` |
| Tier 2 | ~20 req/min | `conversations.list`, `conversations.open` |
| Tier 3 | ~50 req/min per channel | `chat.postMessage` (~1/sec/channel) |
| Tier 4 | ~100 req/min | `users.info`, `users.lookupByEmail` |

### 429 Response Handling

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

The `Retry-After` header is in **seconds**. Wait exactly that long, then retry.
Do NOT retry immediately - this extends your cooldown.

### Burst Handling

- `chat.postMessage` allows short bursts above 1/sec, then throttles
- 429 applies per-method, per-workspace, per-minute
- A 429 on `chat.postMessage` does NOT affect other methods

---

## Incoming Webhooks (Simple Alternative)

**Docs:** https://docs.slack.dev/messaging/sending-messages-with-webhooks

For simple one-way alerts to a fixed channel. No token needed - just a URL.

### Setup

1. Create a Slack app, add an Incoming Webhook to a channel
2. You get a URL like `https://hooks.slack.com/services/T.../B.../...`
3. POST JSON to that URL:

```
POST https://hooks.slack.com/services/...
Content-Type: application/json

{"text": "Simple alert!"}
```

### Limitations

- Fixed to one channel per webhook
- Cannot reply in threads or update messages
- Cannot upload files
- Cannot target DMs dynamically

Use this only for the simplest alerts. For anything more, use `chat.postMessage`
with a bot token.