---
name: email-routing-config
description: Manage email routing configuration — override rules, allowlists, and blocklists. Use when the user asks to route a sender to a specific folder, mark something as not junk, block a sender, or change how emails are sorted.
triggers:
  intent:
    - email routing configuration
    - sender routing override
    - triage rule management
  user_phrases:
    - route this to later
    - route rippling to later
    - mark this sender as not junk
    - add to safe senders
    - block this sender
    - put this in junk
    - always route X to Y
    - this should go to inbox today
    - never mark X as junk
    - this sender is junk
    - move X to blocklist
  tool_context:
    with_tools: [read, edit, write]
  priority: high
  suggest_only: false
compatibility: OpenCode skills system; manages JSON config files consumed by email-auto-sorter.
---

# Email Routing Config

This skill lets the agent manage email routing rules interactively. When a user says "route Rippling to Later" or "mark this sender as not junk", this skill tells the agent exactly which file to edit and how.

## Config Files

There are three config files, each with a distinct purpose:

| File | Location | Purpose |
|------|----------|---------|
| **Routing overrides** | `C:/development/email-triage/config/routing-overrides.json` | Force a sender/domain to a specific folder (bypasses heuristics) |
| **Allowlist** | `C:/development/email-quarantine/config/do-not-block.json` | Prevent a sender/domain from being junked |
| **Blocklist** | `C:/development/email-quarantine/config/junk-indicators.json` | Mark a sender/domain as known junk |

Important distinction: `do-not-block.json` means **safe from Junk only**. It does not mean important, urgent, or today-worthy. Use `routing-overrides.json` when the user wants a specific folder.

## Decision Tree

When the user makes a routing request, follow this decision tree:

### "Route X to [folder]" or "Always put X in [folder]"
1. Edit `C:/development/email-triage/config/routing-overrides.json`.
2. Add an object to the `overrides` array:
   ```json
   {
     "matchType": "email" or "domain",
     "matchValue": "lowercase value",
     "targetFolder": "one of the valid values below",
     "category": "newsletter | automated-notification | product-update | event-marketing | vendor-fyi | government-market-intel | other",
     "reason": "why this override exists"
   }
   ```
3. Valid `targetFolder` values (strict — no others accepted):
   - `Inbox Urgent`
   - `Inbox Today`
   - `Inbox Later`
   - `Inbox Junk`
4. Use `"matchType": "email"` for a specific address, `"matchType": "domain"` for all addresses at a domain.
5. Update `generatedOn` to current timestamp.
6. Add a `category` when the rule fits a known pattern: newsletter, automated-notification, product-update, event-marketing, vendor-fyi, government-market-intel, receipt, platform-notification, or other.
7. Overrides win over everything (allowlist, blocklist, heuristics). No need to also edit do-not-block.json.

### "Mark as not junk" / "Don't junk this sender"
1. Edit `C:/development/email-quarantine/config/do-not-block.json`.
2. Add the email address to the `emails` array AND/OR the domain to the `domains` array.
3. Keep entries lowercase, one per line, alphabetically sorted within the array.
4. This prevents junking but does NOT control which non-junk folder (Urgent/Today/Later) the email lands in. For folder control, use routing overrides instead.

### "Block this sender" / "This is junk"
1. Edit `C:/development/email-quarantine/config/junk-indicators.json`.
2. Add the email address to the `emails` array AND/OR the domain to the `domains` array.
3. Keep entries lowercase, one per line.
4. Update `generatedOn` to current timestamp.

### "This should be urgent/today"
1. Prefer a narrow email-level override in `routing-overrides.json` unless the whole domain is truly urgent/today-worthy.
2. Only use `Inbox Urgent` for known human senders who need Dave's same-day or <2-hour action.
3. Never make automated senders, newsletters, event marketing, cold outreach, or product updates Urgent/Today unless the user explicitly insists.

## Editing Rules

- Always read the file before editing.
- Preserve the existing JSON structure and formatting.
- Keep entries lowercase.
- No duplicates within an array.
- Normalize lookup values to lowercase before comparing.
- For `routing-overrides.json`: add new entries at the end of the `overrides` array.
- For `do-not-block.json` and `junk-indicators.json`: insert in alphabetical order within the array.

## Validation

After editing any config file:
1. Confirm the JSON is valid (no trailing commas, proper brackets).
2. Confirm the edit is in the correct file for the user's intent.
3. Briefly state the effect: "Rippling emails will now route to Inbox Later on the next auto-sort run."

## Related Skills

- **email-auto-sorter** — Consumes these config files to route emails. Run after config changes to apply immediately.
- **outlook-inbox-triage** — Interactive triage where misclassifications are discovered and corrected.
- **email-draft-reply** — Draft replies in Dave's voice.
- **email-to-clickup** — Convert an email into a ClickUp task and archive it.
