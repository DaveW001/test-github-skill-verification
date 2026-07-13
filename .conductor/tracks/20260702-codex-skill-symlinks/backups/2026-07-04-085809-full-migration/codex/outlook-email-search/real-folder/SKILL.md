---
name: outlook-email-search
description: Search Outlook email/messages using Microsoft Graph PowerShell. Use when the user asks to find a specific email, registration link, or thread.
tool_context:
  with_tools: [bash]
triggers:
  user_phrases:
    - search my email
    - find an email about
    - look in Outlook for
    - find the registration link
    - find the email thread
    - search my mailbox
---

# Outlook Email Search

Use this skill to retrieve and find mailbox messages and links.

## Default Behavior
This skill is READ-ONLY. Do not modify, move, archive, or reply to messages unless the user explicitly asks.

## Privacy Rules
Summarize relevant emails. Do not dump full private email bodies into the output unless specifically requested.

## Related Skills
- `outlook-inbox-triage`: Use when reviewing messages to decide next actions.
