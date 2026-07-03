---
name: enrich_meeting_notes
description: Enrich meeting notes with knowledge-graph context, stakeholders, organizations, decisions, actions, and ClickUp-ready summaries; use when creating, cleaning, enriching, or publishing meeting notes from transcripts or raw notes.
---
# Enrich Meeting Notes Skill

## Description
Orchestrates Microsoft Graph calendar/email lookup, KG attendee lookup, conflict detection, and structured Markdown output for meeting note enrichment. Use when the user asks to enrich, enhance, or flesh out meeting notes with context from calendar, email, and the knowledge graph.

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `raw_notes_path` | Yes | Absolute path to the raw meeting notes file (Markdown or plain text) |
| `meeting_date` | Yes | Date of the meeting in YYYY-MM-DD format |
| `known_subject` | Yes | Primary topic or project name for the meeting |
| `known_attendees` | No | Comma-separated list of expected attendee names (helps with disambiguation) |

## Dependency Skills

Before starting enrichment, load these skills using skill_use:

1. **Microsoft Graph** — skill_find "microsoft graph" then skill_use "microsoft_graph". Used for calendar event lookup and email search.
2. **Outlook Email Search** — skill_find "outlook email search" then skill_use "outlook_email_search". Used for finding related email threads.
3. **Knowledge Graph Query** — Use python scripts/query-graph.py and python scripts/search.py from the workspace. No skill load needed.

## Structured Lookup Phase

**MANDATORY:** Complete ALL lookup steps before composing any enriched notes. Do not begin drafting until every lookup is done.

### Step 1: Calendar Event Lookup

**Important:** Always collect calendar attendees before drafting enriched notes. The attendee list from the calendar event is the authoritative source for who was present.

Using the microsoft_graph skill, fetch the meeting event for meeting_date:

1. Load the skill: skill_use "microsoft_graph"
2. Search calendar events for the meeting date and subject
3. Record: meeting title, start/end time, location, organizer, full attendee list with email addresses
4. If no event found: note this as a gap and proceed to Step 2

### Step 2: Email Thread Lookup

Using the outlook_email_search skill, find related email conversations:

1. Load the skill: skill_use "outlook_email_search"
2. Search for emails matching known_subject within +/- 7 days of meeting_date
3. Search for emails from/to each known attendee
4. Record: email subjects, dates, key participants, any attachments or action items mentioned

### Step 3: KG Attendee Lookup

For each attendee identified in Steps 1-2, run knowledge graph lookups:

1. Exact lookup: ` python scripts/query-graph.py lookup --name "<Attendee Name>" --type Person --top 5 `
2. Broader search: ` python scripts/search.py "<Attendee Name> <Org>" --top 5 `
3. Record for each person: full name, role/title, organization, email, phone, manager, and any notes in the KG

### Step 4: Source Conflict Table

Build a comparison table of data from all sources:

| Field | Calendar | Email | KG | Raw Notes |
|-------|----------|-------|----|-----------|
| Attendee Name | ... | ... | ... | ... |
| Role/Title | ... | ... | ... | ... |
| Organization | ... | ... | ... | ... |
| Email | ... | ... | ... | ... |

Mark any discrepancies for surfacing in the output.

### Step 5: Draft Composition

Only after completing Steps 1-4, compose the enriched meeting notes using the output template below.

## Conflict Rules

1. **Prefer latest live source for current contact fields, but surface conflicts to the user.** Do not silently pick one source over another.
2. When calendar and email agree but KG disagrees, note the KG value as potentially stale and flag it in the Conflicts / Gaps section.
3. When sources give different names for the same person (e.g., nickname vs. legal name), list both and indicate which source uses which.
4. Never silently overwrite KG data. All suggested corrections must be surfaced to the user for approval.

## Output Template

Every enriched meeting notes output MUST follow this structure:

```markdown
# Enriched Meeting Notes: [Subject]
**Date:** YYYY-MM-DD
**Sources:** Calendar, Email, KG, Raw Notes

## Attendees

| Name | Role / Title | Organization | Email | Source |
|------|-------------|-------------|-------|--------|
| ... | ... | ... | ... | Calendar/KG/Email |

## Source Evidence

### Calendar
- Event: [title, time, location]
- Organizer: [name]
- Attendees listed: [names]

### Email Threads
- Thread 1: [subject, date range, participants]
- Thread 2: [subject, date range, participants]

### Knowledge Graph
- [Person Name]: [role, org, notes from KG]
- ...

## Conflicts / Gaps

| Field | Source A Value | Source B Value | Recommended | Action |
|-------|---------------|---------------|-------------|--------|
| ... | ... | ... | ... | Verify with contact / Update KG |

## Enriched Notes

[The full meeting notes with names expanded, roles added inline, acronyms resolved, and context from email/calendar woven in]

## Follow-Up Actions
- [ ] [Action item 1 — assigned to: Name]
- [ ] [Action item 2 — assigned to: Name]
- [ ] [Stale KG data to update — person: field]
```

## Fallbacks

When lookups return empty or incomplete results:

1. **Empty KG result for an attendee:**
   - Search email signatures in the email thread results for contact info (title, phone, org)
   - Search calendar attendee directory data for org affiliations
   - Mark the person as an ExternalPerson candidate for future KG ingestion
   - Note the gap in the Conflicts / Gaps table

2. **No calendar event found:**
   - Use known_subject and meeting_date to search emails for the meeting invite
   - Note the absence of calendar data in Source Evidence

3. **No matching email threads:**
   - Broaden search to +/- 14 days
   - Try partial subject matches
   - Note the absence of email evidence

4. **Multiple KG matches for a name:**
   - Present top 3 matches with disambiguation info (org, email, title)
   - Ask user to confirm the correct person
   - Do not guess

## Validation Checklist

After producing enriched notes, verify:

- [ ] All attendees have at least one source (Calendar, Email, KG, or marked as gap)
- [ ] Conflicts are documented in the Conflicts / Gaps table, not hidden
- [ ] Output follows the template structure with all required headings
- [ ] Every attendee has at least a name and one identifying detail (role, org, or email)
- [ ] Follow-Up Actions include any stale KG data that needs updating
- [ ] ExternalPerson candidate is noted for any person not found in KG
