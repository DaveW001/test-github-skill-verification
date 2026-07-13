---
tool_context:
  with_tools: [bash]
name: outlook-inbox-triage
description: Triage Outlook inbox messages and help decide what to do with each one before drafting any reply. Use when the user wants to review inbox email, sort read or unread messages, decide whether to respond, and be interviewed so replies can be written in the user's own voice.
compatibility: OpenCode skills system; optimized for Microsoft Outlook Email connector workflows.
triggers:
  intent:
    - inbox triage
    - email response planning
    - unread review
    - message-by-message reply decisions
  user_phrases:
    - help me triage my inbox
    - go through my Outlook email
    - help me decide how to respond
    - interview me about these emails
    - sort read and unread emails
    - figure out what needs a reply
    - search my inbox before triage
    - find messages to triage
  execution_layer: graph-powershell
  cmdlets: [Get-MgUserMessage, New-MgUserMessageReply]
  priority: high
  suggest_only: true
---

# Outlook Inbox Triage

Use this skill to help the user work through Outlook email one message at a time, decide what deserves a response, and gather the exact intent needed to draft a reply in the user's own voice.

## Graph PowerShell Execution

See [reference.md](reference.md) for PowerShell cmdlets and syntax.

## Configuration & Defaults

- **Batch Size (ADV-Friendly)**: Default to batches of **3 emails at a time**. Ask the user if they want to adjust this count when starting.
- Start with inbox review, not drafting.
- Treat both read and unread mail as triage candidates if the user asks for "anything in there" or similar.
- Prefer recent, relevant, actionable messages over promotional noise.
- Summarize first, present the batch, then interview, then process actions (draft, ClickUp, archive).
- Default to draft-only if the workflow moves into writing a response.

## What Good Looks Like

By the end of triage, each message should have:

- a one-line summary,
- an action label,
- any missing facts called out,
- the user's preferred reply stance,
- enough guidance to draft a short reply in the user's voice.

## Workflow

1. Pull the relevant inbox slice.
   - Use recent inbox listing when the user wants a broad review.
   - Use targeted search when the user gives a sender, subject, date, or account clue.
   - If the first search misses likely messages, widen with partial sender names, domains, or subject fragments.

2. Sort messages into rough buckets.
   - `needs reply`
   - `needs review but likely no reply`
   - `ignore/archive`
   - `unclear, ask user`

3. Present a SMALL BATCH triage list.
   - Strict ADV Rule: DO NOT overwhelm the user with a giant list. Show a maximum of **3 emails** (or the configured batch size) at a time.
   - Show sender, subject, date, and a short plain-English summary.
   - Wait for the user to process this chunk before loading more.

4. Interview the user on the current batch.
   - Process the batch one email at a time.
   - For each email, clarify the action:
     - **Reply?** What outcome or tone do you want?
     - **Send to ClickUp?** Convert it into a task for deeper work.
     - **Archive/Ignore?**
   - Once the batch is done, ask: *"Great job. Want to tackle another 3, or are we done for now?"*

5. Convert the user's answers into a response plan.
   - Capture the stance in one sentence.
   - Note any open questions or missing facts.
   - Confirm when the response should be brief, warm, direct, deferential, or firm.

6. Hand off to drafting.
   - Once the user is ready, hand off to `email-draft-reply` or draft directly using the same response plan.
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
- `send to clickup` (triggers handoff to `email-to-clickup` skill)
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
- If there are multiple possible recipient addresses in a thread, note the safest current address before drafting.

## Output Format During Triage

When presenting triage results, keep each item compact:

- sender
- subject
- received date
- one-line summary
- recommended action
- one interview question for the user

## Handoff

After the user answers the interview question for a message, be ready to move into drafting with a minimal transition:

- `Here’s the response plan: ...`
- `If that matches what you want, I’ll draft the reply.`

For extra examples and patterns, see [reference.md](reference.md).

## Related Skills

- **email-draft-reply** — Draft replies in Dave's voice. Use after triage when a response is needed.
- **email-auto-sorter** — Headless automatic sorting of unread email into priority folders. Use for bulk cleanup without manual review.
- **email-to-clickup** — Convert an email into a ClickUp task and archive it. Use for emails that require deeper work.
- **outlook-email-search** — Search and retrieve specific emails. Use for standalone email search and retrieval requests before triage.
