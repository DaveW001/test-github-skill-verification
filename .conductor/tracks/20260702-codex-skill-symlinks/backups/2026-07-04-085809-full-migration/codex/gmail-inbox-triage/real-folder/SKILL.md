---
tool_context:
  with_tools: []
name: gmail-inbox-triage
description: Triage Gmail inbox messages and help decide what to do with each one. Use when the user wants to review Gmail email, sort read or unread messages, decide whether to respond, and be interviewed so replies can be written in the user's own voice.
triggers:
  intent:
    - gmail triage
    - gmail inbox review
    - google mail review
  user_phrases:
    - triage my gmail
    - check my gmail inbox
    - review my google mail
    - what's in my gmail
    - any gmail I need to respond to
  execution_layer: google-mcp
  priority: normal
  suggest_only: false
---

# Gmail Inbox Triage

Use this skill to help the user work through Gmail messages one at a time, decide what deserves a response, and gather the exact intent needed to draft a reply in the user's own voice.

## Configuration & Defaults

- **Batch Size (ADV-Friendly)**: Default to batches of **3 emails at a time**. Ask the user if they want to adjust this count when starting.
- Start with inbox review, not drafting.
- Treat both read and unread mail as triage candidates if the user asks for "anything in there" or similar.
- Prefer recent, relevant, actionable messages over promotional noise.
- Summarize first, present the batch, then interview, then process actions (draft, archive).
- Default to draft-only if the workflow moves into writing a response.

## What Good Looks Like

By the end of triage, each message should have:

- a one-line summary,
- an action label,
- any missing facts called out,
- the user's preferred reply stance,
- enough guidance to draft a short reply in the user's voice.

## Workflow

1. **Pull the relevant inbox slice.**
   - Use `list-emails` with Gmail search operators to pull recent inbox.
   - Default query: `in:inbox` with `maxResults: 15`.
   - Use targeted searches when the user gives a sender, subject, date, or account clue.
   - Gmail search operators: `from:`, `to:`, `subject:`, `is:unread`, `is:read`, `is:starred`, `has:attachment`, `after:`, `before:`, `larger:`, `smaller:`.

2. **Fetch full message content.**
   - `list-emails` returns only `id` and `threadId` (no content).
   - Call `get-email` for each message ID to get headers, body, and attachments.
   - Set `markAsRead: false` during triage to preserve unread state.

3. **Sort messages into rough buckets.**
   - `needs reply`
   - `needs review but likely no reply`
   - `ignore/archive`
   - `unclear, ask user`

4. **Present a SMALL BATCH triage list.**
   - Strict ADV Rule: Show a maximum of **3 emails** (or the configured batch size) at a time.
   - Show sender, subject, date, and a short plain-English summary.
   - Wait for the user to process this chunk before loading more.

5. **Interview the user on the current batch.**
   - Process the batch one email at a time.
   - For each email, clarify the action:
     - **Reply?** What outcome or tone do you want?
     - **Archive/Ignore?**
     - **Star for later?**

6. **Convert the user's answers into a response plan.**
   - Capture the stance in one sentence.
   - Note any open questions or missing facts.
   - Confirm when the response should be brief, warm, direct, deferential, or firm.

7. **Hand off to drafting.**
   - Hand off to `gmail-draft-reply` or draft directly using the same response plan.
   - Create a draft rather than sending unless the user explicitly asks to send.

## Interview Pattern

Use short, practical questions. Good defaults:

- `Do you want to reply, ignore it, or come back to it later?`
- `What do you want them to leave with after reading your reply?`
- `Should this sound warm, neutral, direct, or firm?`
- `Do you want to propose a next step or keep it lightweight?`
- `Anything you definitely do or do not want to say?`

If the message is straightforward, compress the interview to one question:

- `What do you want your reply to accomplish?`

## Action Labels

Use these labels during triage:

- `reply now`
- `draft later`
- `star for later`
- `no reply needed`
- `archive/ignore`
- `needs more context`

## Triage Heuristics

Prioritize messages that:

- came from a real person you know or are actively working with,
- ask a direct question,
- require a commitment, decision, or scheduling change,
- affect money, delivery, operations, or relationships,
- continue an existing thread where silence could create confusion.

Usually deprioritize messages that are:

- marketing blasts,
- automated alerts with no action requested,
- cold outreach with no relevance,
- status notifications that can be reviewed without replying.

## Voice Capture Rules

Before drafting, capture the user's voice preferences from the interview:

- level of warmth,
- desired brevity,
- whether to sound casual or polished,
- whether to be accommodating or boundary-setting,
- preferred sign-off style.

If the user says "in my voice" but provides little else, default to:

- concise,
- friendly,
- direct,
- low-jargon,
- not overly formal.

## Guardrails

- Do not send email automatically.
- Do not fabricate context that is missing from the message.
- If the email contains sensitive business, legal, financial, or contractual implications, surface the risk before drafting.
- If the message thread is ambiguous, fetch more context before advising on a reply.

## Output Format During Triage

When presenting triage results, keep each item compact:

- sender
- subject
- received date
- one-line summary
- recommended action
- one interview question for the user

## Related Skills

- **gmail-draft-reply** — Draft replies in Dave's voice for Gmail. Use after triage when a response is needed.
- **google-contacts** — Look up contact details for people mentioned in emails.

For tool names and parameters, see [reference.md](reference.md).
