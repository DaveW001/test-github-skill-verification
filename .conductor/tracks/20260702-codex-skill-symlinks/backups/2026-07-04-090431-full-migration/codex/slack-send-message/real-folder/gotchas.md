# Slack Messaging Gotchas

Non-obvious pitfalls, common errors, and tribal knowledge from real usage.

## 1. HTTP 200 Does NOT Mean Success

Slack's Web API **always returns HTTP 200**. The actual success/failure is in the
JSON body:

```json
{"ok": false, "error": "channel_not_found"}
```

**Always check `data.get("ok")` or `data["ok"]`, never just the HTTP status code.**

```python
response = requests.post(url, headers=headers, json=payload)
data = response.json()
if not data.get("ok"):
    raise Exception(f"Slack API error: {data.get('error')}")
```

## 2. Slack mrkdwn != Markdown

| What you want | Markdown | Slack mrkdwn |
|---------------|----------|--------------|
| Bold | `**text**` | `*text*` |
| Italic | `*text*` | `_text_` |
| Strikethrough | `~~text~~` | `~text~` |

**The most common mistake:** using `**bold**` (Markdown) instead of `*bold*` (Slack).
Slack will render `**text**` literally with visible asterisks.

## 3. `Retry-After` Is the Contract (Not a Suggestion)

When you get HTTP 429, the `Retry-After` header tells you exactly how many seconds
to wait. Ignoring it and retrying immediately makes things worse - Slack extends
your cooldown.

```python
if response.status_code == 429:
    wait = int(response.headers.get("Retry-After", 60))
    time.sleep(wait)  # Wait the EXACT amount
```

**Do NOT use a fixed backoff.** Read the header every time.

## 4. DM Channel IDs vs User IDs

- **User ID**: starts with `U` (e.g., `U02TRMSH535`) - identifies a person
- **DM Channel ID**: starts with `D` (e.g., `D02TRMSH535ABC`) - identifies the DM conversation

`chat.postMessage` accepts either for DMs. But `files.completeUploadExternal`
**requires** a `D` channel ID, not a `U` user ID. You must call
`conversations.open` first to get the `D` ID.

In `conductor-reporter`, this is handled by sending a minimal message first and
extracting the channel ID from the response:

```python
# Send to user ID, extract DM channel from response
r = requests.post(".../chat.postMessage", json={"channel": user_id, "text": "placeholder"})
dm_channel_id = r.json()["channel"]  # This is the D... ID
```

## 5. Notification Fatigue (Real Lesson)

**From `email-triage` (CHANGE-2026-06-12):** Sending a Slack message on every
successful script run created 5+ messages/day showing "Urgent=0 Errors=0".

**The fix:** Only notify when there's something actionable:
- Script failed (non-zero exit code)
- Errors detected during processing
- Anomalies that need human attention

**Rule:** Successful runs should log to files. Slack is for things that need
immediate attention.

## 6. `files.upload` Is Dead

As of **November 12, 2025**, `files.upload` no longer works. If you copy old code
from Stack Overflow or blogs, it will fail. You must use:

1. `files.getUploadURLExternal` (get URL + file_id)
2. POST file to URL
3. `files.completeUploadExternal` (finalize + share)

The new API **requires** the file size (`length`) upfront. Read the file bytes and
calculate `len(content)` before step 1.

## 7. `text` Fallback Is Mandatory

Even when sending rich `blocks` messages, always include the `text` field. It's
used in:
- Push notifications (mobile/desktop)
- Message previews
- Accessibility (screen readers)
- Clients that can't render blocks

Without `text`, your message may appear blank in notifications.

## 8. `unfurl_links: false` Suppresses Link Previews

By default, Slack generates large link preview cards. For notification messages
with URLs, set `unfurl_links: false` to keep messages clean and compact.

Both `conductor-reporter` and `email-triage` use `"unfurl_links": False`.

## 9. Bot Must Be in the Channel

For public channels, the bot must be invited (`/invite @botname`). For DMs,
`conversations.open` handles this automatically.

Error `not_in_channel` means the bot hasn't joined. Error `channel_not_found`
means the ID is wrong or the bot lacks access.

## 10. Token Security

- **Never** print, log, or echo the token value
- **Never** commit `.env` to git (add to `.gitignore`)
- Reference via `os.environ["SLACK_BOT_TOKEN"]` or `$env:SLACK_BOT_TOKEN`
- `.env.example` should show `xoxb-REDACTED` as placeholder only
- Tokens starting with `xoxb-` are long-lived unless token rotation is enabled

## 11. Rate Limit Tiers Differ by Method

A 429 on `chat.postMessage` does NOT affect `conversations.open`. Each method has
its own bucket. But all methods share a workspace-wide limit for burst protection.

If you're doing many operations, pace across methods:
- Open DM channel first (Tier 2, ~20/min)
- Then send messages (Tier 3, ~1/sec/channel)
- Upload files (Tier 2, ~20/min)

## 12. PowerShell Encoding Trap

When using `Invoke-RestMethod` in PowerShell, the body must be properly JSON-encoded:

```powershell
# WRONG - string interpolation issues
$body = "{""text"": ""$message""}"

# RIGHT - use ConvertTo-Json
$body = @{channel = $userId; text = $message; unfurl_links = $false} | ConvertTo-Json -Depth 10
```

Also use `-Depth 10` or higher for nested structures (blocks).