---
tool_context:
  with_tools: []
name: gmail-draft-reply
description: Draft human-sounding email replies in Dave Witkin's voice for Gmail. Use when the user asks to respond to a Gmail email, reply to a Google mail, or draft a Gmail message. Default behavior is create a draft (never send) and return the draft info for review.
triggers:
  intent:
    - gmail reply
    - gmail draft
    - google mail reply
  user_phrases:
    - reply to that gmail
    - draft a reply in gmail
    - respond to my gmail
    - write a gmail reply
    - draft a google mail response
  execution_layer: google-mcp
  priority: normal
  suggest_only: false
---

# Gmail Draft Reply

Create polished reply drafts that sound like Dave Witkin. Default to drafting only.

## Defaults

- Create a draft reply, do not send.
- Return the final draft text and draft ID.
- Keep the reply concise, direct, and professional unless the user asks for a different tone.
- If the user has not yet decided whether to reply or what they want the reply to accomplish, use `gmail-inbox-triage` first.

## Workflow

1. **Identify the target email** by subject, sender, or recency.
2. **Pull message context** from Gmail using `get-email`.
3. **Write one strong draft** in Dave's voice (see voice rules below).
4. **Create a draft** in Gmail using `create-draft`.
5. **Return:**
   - subject line,
   - body text,
   - draft ID,
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

## Voice Rules

If the user says "in my voice" but provides little else, default to:

- concise,
- friendly,
- direct,
- low-jargon,
- not overly formal.

## Scheduling Rule

- When the best next step is a meeting, include this default scheduling link in the draft:
  - `https://calendly.com/dwitkin/30min-phone`
- Preferred call-to-action text:
  - `If helpful, you can book time with me.`
- Preferred hyperlink anchor text:
  - `book time with me`

## Reply Threading

When replying to an existing email:
1. Get the original message via `get-email` to capture the `threadId` and `messageId`.
2. Pass `replyToMessageId` and `threadId` to `create-draft` for proper threading.
3. If the user wants to send immediately, use `send-email` with the same threading params instead.

## Related Skills

- **gmail-inbox-triage** — Interactive Gmail triage to decide which emails need replies. Use this first to identify what needs a response.
- **google-contacts** — Look up contact details for people mentioned in emails.

For tool names and parameters, see [reference.md](reference.md).
