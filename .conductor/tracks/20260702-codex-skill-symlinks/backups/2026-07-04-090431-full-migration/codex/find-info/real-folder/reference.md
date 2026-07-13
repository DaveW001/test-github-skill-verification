# find-info Reference

## Decision Principle

Do not hard-code "email first" for every search. Classify the artifact type, then route to the highest-probability source. Every search runs as a traceable loop: clarify target, classify artifact type, check access, search the highest-likelihood source, record evidence, stop dead-end tools quickly, and hand off source-backed findings.

## Lessons from the Digital.AI Webinar Search

- Outlook/email found the agenda quickly because the invitation was in the inbox.
- Slack and the knowledge base produced useful context for decisions and people.
- ClickUp and OneDrive attempts created avoidable friction because auth/config was not verified first.
- The lesson: always run an auth/access preflight before committing to a source.

## Stop Rule for Bad Tool Calls

1. If a tool returns an auth or config error, make one corrected retry (e.g., reload skill, re-authenticate, check path).
2. If the corrected retry fails, record the failed source in the search ledger and move to the next source.
3. If the failed source is essential to the request, ask one targeted question instead of guessing.
4. Never retry the same failing tool more than twice total.

## Ambiguous Sender Language

When the user says "I sent it," "they sent it," or "it was shared," the word "it" is ambiguous. Trigger both email and Slack/DM search before low-probability repositories like OneDrive or SharePoint.

## Source-Specific Notes

### Outlook/email
- Best for: agendas, invitations, attachments, registration links, "sent over" artifacts.
- Preflight: load the Outlook email search skill; verify Microsoft Graph access.
- If Graph auth fails: do not retry more than once; move to Slack/DM.

### Slack/DM
- Best for: recent conversations, shared links, "who said what," explicitly shared links.
- Preflight: verify channel or DM scope if known; otherwise search broad terms first, then narrow.
- If channel scope unknown: search broad terms, then ask user to narrow.

### Knowledge Base
- Best for: decisions, risks, people, orgs, Army C2/CC2 context.
- Preflight: use known graph paths under `C:\development\02-Kx-to-process\knowledge-base\`.
- If entity not found: expand search to Slack/email for meeting context.

### ClickUp
- Best for: task status, owner, due date, action items.
- Preflight: verify `cup` CLI or API access before searching.
- If auth fails: do not keep retrying; move to Slack for status questions.

### OneDrive/SharePoint
- Best for: local file paths, exported artifacts, shared documents.
- Preflight: prefer known shared links; use local sync search only with path-safe scripts.
- If local sync path unknown: ask user for the sync folder location.
