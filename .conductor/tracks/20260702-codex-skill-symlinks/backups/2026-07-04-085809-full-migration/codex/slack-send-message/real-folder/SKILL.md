---
name: slack-send-message
description: "Send Slack messages and files programmatically from Python or PowerShell scripts using a bot token (xoxb-) and the Slack Web API (chat.postMessage, file uploads). Use when building automation, notifications, or scripts that post to Slack DMs/channels. Covers auth, formatting, rate-limit handling, the new file upload API, and notification hygiene. NOT for interactive MCP-based messaging (use the slack-messaging skill instead)."
triggers:
  user_phrases:
    - send a slack message
    - post to slack from a script
    - slack notification
    - slack bot token
    - slack dm
    - send a slack alert
    - upload a file to slack
    - slack webhook
    - notify slack
  file_context:
    extensions: [py, ps1, sh, ts, js]
  error_context:
    - slack api error
    - slack rate limit
    - 429 too many requests
---

# Slack Send Message

Send Slack messages and files from scripts (Python / PowerShell) using a bot token
(`xoxb-`) and the Slack Web API. This skill captures how this workspace actually
sends Slack notifications and augments it with upstream best practices.

## When to Use This vs Other Slack Skills

| Situation | Use |
|-----------|-----|
| Writing a script/automation that posts to Slack | **This skill** |
| Agent interactively reading/searching/posting via MCP tools | `slack-messaging` (MCP skill) |
| One-way alert to a fixed channel (simplest) | Incoming Webhook (see reference.md) |

## Decision Tree

1. **Need to send a message?** -> Use `chat.postMessage` with bot token.
2. **Need to send a file?** -> Use the new 3-step upload API (see File Upload).
3. **Need a simple one-way alert?** -> Incoming Webhook (no token, single URL).
4. **Need to update an existing message?** -> Save the `ts` + `channel` from the
   first post, then use `chat.update`.
5. **Need to reply in a thread?** -> Save the `ts`, pass `thread_ts` on the next post.

## Prerequisites

### Token & Credentials

- **Bot token**: `SLACK_BOT_TOKEN` (starts with `xoxb-`) - required
- **Target user ID**: `SLACK_USER_ID` = `U02TRMSH535` (Dave Witkin DM)
- **Location**: `.env` file in each repo, or environment variable
- **Required OAuth scopes**: `chat:write` (send messages), `im:write` (open DMs),
  `files:write` (upload files)

> **Never log, echo, print, or commit the token value.** Reference it from
> environment variables only. The `.env.example` shows key names with a
> `xoxb-REDACTED` placeholder.

### Install Dependencies

```bash
# Python
pip install requests python-dotenv

# PowerShell - no extra packages needed (uses Invoke-RestMethod)
```

## Quick Start

### Send a DM (Python)

```python
import os, requests
from dotenv import load_dotenv
load_dotenv()

token = os.environ["SLACK_BOT_TOKEN"]
r = requests.post("https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"channel": os.environ["SLACK_USER_ID"], "text": "Hello from a script!",
          "unfurl_links": False},
    timeout=30)
print("Sent" if r.json().get("ok") else f"Error: {r.json().get('error')}")
```

### Send a DM (PowerShell)

```powershell
$token   = $env:SLACK_BOT_TOKEN
$payload = @{
    channel      = $env:SLACK_USER_ID
    text         = "Hello from PowerShell!"
    unfurl_links = $false
} | ConvertTo-Json
Invoke-RestMethod -Uri "https://slack.com/api/chat.postMessage" `
    -Method Post `
    -Headers @{Authorization = "Bearer $token"; "Content-Type" = "application/json"} `
    -Body $payload
```

## Core Workflows

### 1. Send a Message (`chat.postMessage`)

| Parameter | Required | Description |
|-----------|----------|-------------|
| `channel` | yes | Channel ID (`C...`), user ID (`U...`) for DM, or name (`#general`) |
| `text` | yes* | Plain text or Slack mrkdwn. Always include even when using `blocks`. |
| `blocks` | no | Block Kit array (max 50 blocks, ~40,000 chars). See reference.md. |
| `thread_ts` | no | Parent message timestamp to reply in a thread |
| `unfurl_links` | no | `false` to suppress link previews (default `true`) |
| `link_names` | no | `true` to convert `@username` mentions into links |

*The `text` field is the fallback shown in push notifications and previews. Always
include it, even when sending `blocks`.

### 2. Verify Token (`auth.test`)

```
GET https://slack.com/api/auth.test
Authorization: Bearer {token}
```

Returns the authenticated user, team, and user_id. Use this to verify a token works
before sending messages.

### 3. Open a DM Channel (`conversations.open`)

To resolve a user ID (`U...`) to a DM channel ID (`D...`) - needed for file uploads:

```
POST https://slack.com/api/conversations.open
{"users": "U02TRMSH535"}
```

Returns `channel.id` (starts with `D`). Use this channel ID for file uploads.

### 4. Upload a File (New 3-Step API)

> **`files.upload` is sunset** (November 2025). All apps must use the new flow.

**Step 1** - Get an upload URL:
```
POST https://slack.com/api/files.getUploadURLExternal
filename={name}&length={size_in_bytes}
```
Returns `upload_url` and `file_id`.

**Step 2** - POST the file to `upload_url`:
```
POST {upload_url}
Body: multipart/form-data, field "file" = file content
```
Expect HTTP 200.

**Step 3** - Complete the upload:
```
POST https://slack.com/api/files.completeUploadExternal
{"files": [{"id": "{file_id}", "title": "{name}"}], "channel_id": "{D_channel_id}", "initial_comment": "Optional caption"}
```

Full reference implementation: [scripts/send-slack-message.py](scripts/send-slack-message.py)

## Formatting Messages (Slack mrkdwn)

Slack does NOT use standard Markdown. Use Slack's mrkdwn:

| Formatting | Syntax | Result |
|------------|--------|--------|
| **Bold** | `*text*` | **text** |
| _Italic_ | `_text_` | _text_ |
| `Code` | `` `text` `` | `text` |
| Strikethrough | `~text~` | ~~text~~ |
| Block quote | `>` text | indented quote |
| Bulleted list | `- item` or `\u2022 item` | bullet |
| Numbered list | `1. item` | numbered |

> **Gotcha**: In Slack, `*` is bold (not `_` like Markdown). This trips up
> developers coming from standard Markdown. See [gotchas.md](gotchas.md).

### Message Length

- Slack DM/channel messages have practical limits. Keep summary messages short
  (~2000 chars). Truncate longer content and upload the full version as a file.
- Block Kit: max 50 blocks, ~40,000 characters total.

## Rate Limits & Retries

| Method | Tier | Limit |
|--------|------|-------|
| `chat.postMessage` | Tier 3 | ~1 msg/sec per channel, ~50/min per channel |
| `conversations.open` | Tier 2 | ~20 req/min |
| `files.getUploadURLExternal` | Tier 2 | ~20 req/min |

### Handling HTTP 429 (Rate Limited)

When you exceed a limit, Slack returns **HTTP 429** with a `Retry-After` header
(integer seconds). This is the contract - wait exactly that long before retrying.

```python
import time
if response.status_code == 429:
    wait = int(response.headers.get("Retry-After", 60))
    time.sleep(wait)
    # retry the request
```

**Best practices** (from upstream docs):
- Always honor `Retry-After` - never retry immediately
- Use exponential backoff with jitter for transient (5xx) errors
- Batch: consolidate multiple alerts into one message
- Deduplicate: post once, update a count with `chat.update`
- Update, don't repost: use `chat.update` for status messages
- Queue: for high volume, put a queue between events and Slack

## Notification Hygiene (Lessons Learned)

From our `email-triage` experience: sending a Slack message on every successful run
causes **notification fatigue**. Fix:

- **Notify only on errors/anomalies** - not on every successful run
- **Consolidate** - one summary message beats many individual messages
- **Thread updates** - reply in a thread instead of new messages
- **Log to files** - successful runs write to log files, not Slack

## Reference Implementations in Our Repos

| Repo | Language | What it sends |
|------|----------|---------------|
| `conductor-reporter` | Python | Weekly Conductor track reports (DM + file upload) |
| `email-triage` | PowerShell | Error alerts only (notification fatigue fix applied) |

Both use the same `SLACK_BOT_TOKEN` + `SLACK_USER_ID` pattern.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `invalid_auth` | Token expired or wrong prefix | Verify token starts with `xoxb-`; run `auth.test` |
| `channel_not_found` | Wrong channel ID or bot not a member | Use `conversations.open` first for DMs |
| `not_in_channel` | Bot hasn't joined the channel | Invite bot to channel, or use DM (user ID) |
| `missing_scope` | Token lacks required OAuth scope | Add `chat:write`, `im:write`, or `files:write` |
| HTTP 429 | Rate limited | Read `Retry-After` header, sleep, retry |
| `HTTP 200` but `ok: false` | API-level error (not HTTP error) | Always check `data["ok"]`, not just status code |

## External References

For detailed API docs, rate-limit tables, Block Kit reference, and the full file
upload migration guide, see [reference.md](reference.md).

For common pitfalls, gotchas, and tribal knowledge, see [gotchas.md](gotchas.md).