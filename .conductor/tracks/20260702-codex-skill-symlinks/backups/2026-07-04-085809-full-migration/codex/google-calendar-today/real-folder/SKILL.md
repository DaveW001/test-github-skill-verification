---
tool_context:
  with_tools: []
name: google-calendar-today
description: Show today's Google Calendar schedule with times, titles, locations, and conflicts. Use when the user asks about their Google calendar, Gmail calendar, or wants to see their Google schedule.
triggers:
  intent:
    - google calendar overview
    - google daily schedule
    - google upcoming meetings
  user_phrases:
    - what's on my google calendar
    - show my google calendar
    - what's on my gmail calendar today
    - check my google schedule
    - am I free on google calendar
  execution_layer: google-mcp
  priority: normal
  suggest_only: false
---

# Google Calendar Today

Show today's Google Calendar schedule in a clean, scannable format. Flag conflicts, back-to-back meetings, and upcoming events.

## Workflow

1. **List calendars** using `list-calendars` to find the primary calendar ID and any secondary calendars.
   - The primary calendar uses `calendarId: 'primary'`.
   - Note all calendar IDs for the events query.

2. **Fetch today's events** using `list-events`.
   - Calculate start/end in ISO format with timezone:
     ```
     start: today midnight → e.g. "2026-04-29T00:00:00Z"
     end: tomorrow midnight → e.g. "2026-04-30T00:00:00Z"
     ```
   - Pass `calendarIds` as an array if checking multiple calendars.
   - Use `timeZone: "America/New_York"` (or user's local tz).

3. **Check free/busy** if needed using `get-freebusy`.
   - Useful for finding open slots or confirming availability.
   - Pass calendar identifiers (email format).

4. **Format the output** as a clean schedule view:

```
📅 Google Calendar — Today (Wed, Apr 29)

  09:00–09:30  Team Standup          📍 Zoom
  10:00–11:00  Client Review         📍 Office
  ⚠️  CONFLICT: 11:00–12:00  overlaps with 11:15–12:00
  11:00–12:00  Design Sync           📍 Google Meet
  11:15–12:00  Vendor Call           📍 Phone
  14:00–15:00  1:1 with Sarah       
  ---
  5 events · 1 conflict · Next free: 12:00–14:00
```

5. **Flag conflicts** — any two events with overlapping time ranges.

6. **Show upcoming** — highlight the next event relative to current time.

## Event Fields to Display

- Start time – End time (local time)
- Summary (title)
- Location (if any)
- Attendees count (if > 1)
- Color indicator (optional)

## Time Calculation

Always convert to user's local timezone for display. Store/query in UTC or with explicit offset.

```
User's timezone: America/New_York (Eastern)
```

## Guardrails

- Do not create, modify, or delete events with this skill — use `google-calendar-schedule` for that.
- Do not expose attendee email addresses unless the user asks for them.
- If the calendar returns no events, say so clearly rather than showing empty sections.

## Related Skills

- **google-calendar-schedule** — Create, update, cancel Google Calendar events.
- **unified-calendar-today** — Combined view of both Outlook and Google calendars.
- **calendar-today** — Outlook-only calendar view.

For tool names and parameters, see [reference.md](reference.md).
