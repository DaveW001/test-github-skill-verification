---
tool_context:
  with_tools: []
name: google-calendar-schedule
description: Schedule, update, and cancel Google Calendar events using natural language. Use when the user says "schedule a meeting on Google", "set up a Google call", "move my Google calendar 3pm to 4pm", or "cancel the Google meeting with X".
triggers:
  intent:
    - google calendar scheduling
    - google calendar event management
    - google meeting setup
  user_phrases:
    - schedule a meeting on google calendar
    - add an event to my google calendar
    - set up a call on google
    - move my google 3pm to 4pm
    - cancel the google meeting
    - find me a free slot on google
    - reschedule the google calendar event
  execution_layer: google-mcp
  priority: normal
  suggest_only: false
---

# Google Calendar Schedule

Create, update, and cancel Google Calendar events using natural language. Find free slots and manage scheduling.

## Workflow

### Creating Events

1. **Gather event details** from the user's request:
   - Title/summary
   - Date and time (start + end, or start + duration)
   - Attendees (email addresses)
   - Location
   - Description/notes
   - Recurrence (if applicable)

2. **Check availability** using `get-freebusy` if the user asks to find a free slot.
   - Query a range of time (e.g., a full day or week).
   - Identify open windows.
   - Present 2-3 options to the user.

3. **Create the event** using `create-event`.

4. **Confirm** with the user:
   - Title, time, location
   - Attendees invited
   - Whether to send invites (default: yes for events with attendees)

### Updating Events

1. **Find the event** using `search-events` or `list-events`.
2. **Confirm what to change** — time, title, location, attendees, etc.
3. **Update** using `update-event`.
4. For recurring events, ask: "This instance only, all future, or the entire series?"
   - Use `modificationScope: "single"`, `"future"`, or `"all"`.

### Canceling Events

1. **Find the event** using `search-events` or `list-events`.
2. **Confirm** with the user before deleting.
3. **Delete** using `delete-event`.
   - Note: This is permanent deletion, not "cancel and notify".
   - For a softer cancel, update the event status or description instead.

## Natural Language Parsing

Convert user phrases to event parameters:

| User says | Interpretation |
|-----------|---------------|
| "Schedule a 30-min call with Sarah tomorrow at 3pm" | Create event, duration 30min, tomorrow 3:00-3:30pm, attendee: Sarah |
| "Block off Friday morning for focus time" | Create event, all morning (9-12), no attendees |
| "Move my 2pm to 3pm" | Find event at 2pm, update start to 3pm |
| "Cancel my meeting with John" | Search events for "John", delete |
| "Find me an hour this week" | get-freebusy for this week, find 1-hour gaps |
| "Set up a weekly standup Mon/Wed/Fri at 9am" | Create recurring event with RRULE |

## Recurrence Rules (RFC5545)

Common patterns:
- Daily: `["RRULE:FREQ=DAILY;COUNT=10"]`
- Weekly: `["RRULE:FREQ=WEEKLY;COUNT=5"]`
- Weekly specific days: `["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=15"]`
- Monthly: `["RRULE:FREQ=MONTHLY;COUNT=6"]`
- No end date (use sparingly): `["RRULE:FREQ=WEEKLY"]`

## Time Handling

- Always specify timezone: `America/New_York` (Eastern) unless user specifies otherwise.
- ISO format with offset or Z: `"2026-04-29T15:00:00Z"` or `"2026-04-29T15:00:00-04:00"`.
- The `timeZone` parameter is required when creating events.

## Guardrails

- Always confirm before creating events with 3+ attendees.
- Always confirm before deleting events.
- Do not modify events on calendars where `accessRole` is `reader` or `freeBusyReader`.
- When uncertain about the time, ask the user rather than guessing.

## Related Skills

- **google-calendar-today** — View today's Google Calendar schedule.
- **unified-calendar-today** — Combined view of both Outlook and Google calendars.
- **calendar-schedule** — Outlook-only calendar scheduling.

For tool names and parameters, see [reference.md](reference.md).
