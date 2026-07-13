---
tool_context:
  with_tools: [bash]
name: calendar-schedule
description: Schedule, update, and cancel Outlook calendar events using natural language. Use when the user says "schedule a meeting", "set up a call", "move my 3pm to 4pm", or "cancel the meeting with X".
triggers:
  intent:
    - calendar scheduling
    - meeting creation
    - event management
  user_phrases:
    - schedule a meeting
    - set up a call with
    - book time with
    - move my 3pm to 4pm
    - cancel the meeting with
    - reschedule tomorrow's call
    - create a recurring event
    - find a time to meet
  execution_layer: graph-powershell
  cmdlets: [Get-MgUserCalendarView, New-MgUserEvent, Update-MgUserEvent, Remove-MgUserEvent, Invoke-MgGraphRequest]
  priority: normal
  suggest_only: false
---

# Calendar Schedule

Create, update, and cancel Outlook calendar events. Support natural language scheduling like "schedule 30min with Sarah tomorrow at 2pm".

## Graph PowerShell Execution

See [reference.md](reference.md) for PowerShell cmdlets and syntax.

## Workflow

### Creating Events

1. **Parse the request** — extract: who, when, duration, purpose, location preference.
2. **Resolve time** — handle natural language:
   - "tomorrow at 2pm" → calculate actual date/time
   - "next Tuesday" → calculate actual date
   - "30min" → default duration if not specified
   - Default duration: 30 minutes
3. **Check availability** (optional) — if the time might conflict, run `getSchedule` first.
4. **Confirm with user** — show: title, time, duration, attendees, location. Ask: "Create this?"
5. **Create the event** using `New-MgUserEvent -BodyParameter`.
6. **Return confirmation** — show the event title, time, and `WebLink`.

### Updating Events

1. **Find the event** — search today's or upcoming events to locate the right one.
2. **Confirm what to change** — time, title, attendees, location.
3. **Apply the update** using `Update-MgUserEvent -BodyParameter`.
4. **Confirm the change** — show before/after comparison.

### Canceling Events

1. **Find the event** — same as update.
2. **Confirm cancellation** — always ask before deleting: "Cancel '[Event Title]' at [time]?"
3. **Delete** using `Remove-MgUserEvent`.
4. **Confirm** — "Event canceled."

### Finding Available Slots

1. **Parse the request** — date range, duration, preferred time window.
2. **Call `getSchedule`** for the target date window.
3. **Decode availability** — `0` = free, find contiguous free blocks matching requested duration.
4. **Present top 3 options** — sorted by proximity to preferred time.
5. **Ask user to pick** — then create the event.

## Default Values

| Parameter | Default |
|-----------|---------|
| Duration | 30 minutes |
| Timezone | Eastern Standard Time |
| Location | "Virtual" |
| Body | Auto-generated: "Scheduled via OpenCode" |
| Attendees | Only those explicitly mentioned |

## Natural Language Examples

| User says | Parsed as |
|-----------|-----------|
| "schedule 30min with sarah@example.com tomorrow at 2pm" | 30min event, tomorrow 2:00-2:30, sarah@example.com |
| "book time with me and john@acme.com next tuesday morning" | 30min event, next Tue 09:00-09:30, john@acme.com |
| "move my 3pm to 4pm" | Find today's 3pm event, update to 4:00 (same duration) |
| "cancel the meeting with acme" | Search for events with "acme", confirm, delete |

## Execution Best Practices

- **Always write PowerShell scripts to a temp file** and execute with `powershell -NoProfile -ExecutionPolicy Bypass -File "<path>.ps1"` — never pass complex hashtables inline through bash, as variable expansion and escaping conflicts between bash and PowerShell ($, @, backticks) will cause failures.
- **Temp file location**: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\`
- When attendees are mentioned by name only (no email), note them in the output so the user can add them manually in Outlook.

## Guardrails

- **Always confirm before creating/canceling** — never silently create or delete events.
- **Never modify recurring series** — only modify individual instances (future enhancement).
- **Respect business hours** — don't schedule before 8am or after 6pm unless user explicitly asks.
- **Default to Calendly for external scheduling** — if the user asks to "send someone my availability", suggest the Calendly link (`https://calendly.com/dwitkin/30min-phone`) rather than creating an event.
- Do not auto-add attendees not explicitly mentioned by the user.

## Related Skills

- **calendar-today** — View today's schedule without modifying anything. Use for "what's on my calendar".
- **email-draft-reply** — When scheduling via email, draft a reply with the meeting details or Calendly link.
- **outlook-inbox-triage** — When triage surfaces meeting-related emails that need scheduling.
