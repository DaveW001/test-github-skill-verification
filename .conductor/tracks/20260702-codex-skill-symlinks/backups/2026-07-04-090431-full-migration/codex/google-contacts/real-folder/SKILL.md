---
tool_context:
  with_tools: []
name: google-contacts
description: Search, lookup, create, and update Google Contacts. Use when the user asks to find a contact, look up someone's email or phone, add a new contact, or update contact info in Google.
triggers:
  intent:
    - google contacts lookup
    - contact search
    - contact management
  user_phrases:
    - look up a contact
    - find someone's email
    - search my google contacts
    - add a new contact
    - update contact info
    - what's John's phone number
    - find contact for
  execution_layer: google-mcp
  priority: normal
  suggest_only: false
---

# Google Contacts

Search, lookup, create, and update Google Contacts using the Google MCP server.

## Workflow

### Searching Contacts

1. Use `list-contacts` with a `query` parameter for name-based search.
2. Limit fields with `personFields` to reduce response size (default covers most needs).
3. For exact lookup, use `get-contact` with the `resourceName`.

### Creating Contacts

1. Gather minimum required info: first name + last name.
2. Optionally add: email, phone, address, organization, notes.
3. Use `create-contact`.
4. The response includes the new `resourceName` for future operations.

### Updating Contacts

1. Find the contact first via `list-contacts` or `get-contact`.
2. Use `update-contact` with the `resourceName`.
3. **Must specify `updatePersonFields`** to indicate which fields are being changed.
4. Note: Updating arrays (emails, phones, addresses) replaces ALL existing values.

### Deleting Contacts

1. Find the contact first to get the `resourceName`.
2. Confirm with the user.
3. Use `delete-contact`.
4. **Permanent deletion** — not recoverable.

## Output Format

When displaying contacts, show:

```
👤 John Smith
   📧 john.smith@company.com
   📞 +1 (555) 123-4567
   🏢 Company Inc. — VP Engineering
   📍 123 Main St, New York, NY 10001
```

## Search Tips

- `list-contacts` search is name-based.
- For email/phone searches, fetch a broader list and filter locally.
- Use `pageSize` to control result count (default 100, max 2000).
- For large contact lists, use `pageToken` for pagination.

## Guardrails

- Always confirm before deleting a contact.
- When updating, warn that array fields (emails, phones) are fully replaced.
- Do not expose contact details for people the user didn't ask about.
- Google Contacts API may have rate limits — avoid bulk operations.

## Related Skills

- **gmail-inbox-triage** — Triage emails; may need contact lookup.
- **gmail-draft-reply** — Draft replies; may need contact details.

For tool names and parameters, see [reference.md](reference.md).
