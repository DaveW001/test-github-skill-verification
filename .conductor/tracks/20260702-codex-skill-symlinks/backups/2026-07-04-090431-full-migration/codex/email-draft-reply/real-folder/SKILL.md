---
tool_context:
  with_tools: [bash]
name: email-draft-reply
description: Draft human-sounding email replies in Dave Witkin's voice using Microsoft 365 context. Use when the user asks to respond to an email, reply to an email, or draft an email. Default behavior is create a draft (never send) and return the Outlook draft link for review.
triggers:
  intent:
    - email reply drafting
    - write in my voice
  user_phrases:
    - reply to this email
    - draft a response
    - write this in my voice
    - respond to this thread
  execution_layer: graph-powershell
  cmdlets: [Get-MgUserMessage, New-MgUserMessageReply, New-MgUserMessage]
  priority: high
  suggest_only: true
---

# Email Draft Reply

Create polished reply drafts that sound like Dave Witkin. Default to drafting only.

## Graph PowerShell Execution

See [reference.md](reference.md) for PowerShell cmdlets and syntax.

## Defaults

- Create a draft reply, do not send.
- Return the final draft text and the clickable Outlook draft link.
- Keep the reply concise, direct, and professional unless the user asks for a different tone.
- If the user has not yet decided whether to reply or what they want the reply to accomplish, use `outlook-inbox-triage` first.

## Workflow

1. Identify the target email by subject, sender, or recency.
2. Pull message context from Outlook tools.
3. Write one strong draft in Dave's voice (see `voice-guide.md`).
4. Create a draft in Outlook.
5. Return:
   - subject line,
   - body text,
   - draft link (`webLink`),
   - confirmation that it is draft-only.

## Guardrails

- Never send unless the user explicitly says to send now.
- If facts are unclear, ask one targeted question or keep wording neutral.
- Avoid over-promising or legal/financial commitments not requested by the user.

## Draft Style

- Open with brief acknowledgement.
- State action or request clearly in plain language.
- Keep paragraphs short.
- End with explicit confirmation request when resolution is needed.

## Scheduling Rule

- When the best next step is a meeting, include this default scheduling link in the draft:
  - `https://calendly.com/dwitkin/30min-phone`
- Preferred call-to-action text:
  - `If helpful, you can book time with me.`
- Preferred hyperlink anchor text:
  - `book time with me`
- Hyperlink format preference:
  - Rich text/HTML clients: make `book time with me` clickable to `https://calendly.com/dwitkin/30min-phone`.
  - Plain text clients: append the raw URL after the sentence.

For detailed voice patterns and examples, see `voice-guide.md`.

## Related Skills

- **outlook-inbox-triage** — Interactive inbox triage to decide which emails need replies. Use this first to identify what needs a response.
- **email-auto-sorter** — Headless automatic sorting of unread email into priority folders. Use for bulk cleanup without manual review.
- **email-to-clickup** — Convert an email into a ClickUp task. Use for emails that require deeper work beyond a reply.
