# ClickUp Meeting Notes Guide

**Purpose:** Quick reference for creating meeting notes tasks in ClickUp with proper formatting and custom fields.

**Codex Desktop note:** use relative paths from the mounted skill root (`C:/Users/DaveWitkin/.codex/skills/clickup`). For OpenCode Desktop/CLI, use the same relative commands from that app's mounted skill root.

## Quick Reference

### Meeting Notes List
- **List ID:** 901107655225
- **List Name:** Meeting Notes

### Custom Field IDs
- **Meeting Date:** `19408341-d116-45fc-b30e-8a3a2bbbadbf` (type: date)
- **Follow Up:** `9ddd4ccd-5461-4105-af17-d106f64ceb7f` (type: drop_down)
  - Yes: `904d53a4-615f-4876-9d39-3d3ac2f66fc6`
  - No: `a3767735-31ae-4bde-9509-2e4aec952a1f`
- **Attendees:** `824ed3e1-4b33-4d24-b216-77a4fca891d7` (type: text)
- **Discussion Summary:** `18f5efa8-1bfc-404b-9534-18f488015ec0` (type: text)
- **Action Items & Next Steps:** `40406b46-b70b-4c38-9b85-3fd5bb6a715a` (type: text)
- **Meeting Type:** `0b9b84de-8f14-4b34-8293-e4187262e224` (type: drop_down)
- **Account Name:** `c28f4030-3e32-4df3-a1e3-8d35d3eb5040` (type: drop_down)

## Formatting Rules

### Use `markdown_description` Field
- **Always** use `markdown_description` for task content, NOT `description`
- This ensures headings, bold, bullets render correctly

### Markdown Description Content Formatting (CRITICAL)

**Follow these rules when writing meeting notes markdown content:**

1. **Do NOT repeat the meeting title in the markdown description**
   - The task title already contains the meeting name, date, and attendees
   - Example: If task title is "2026-01-22 Packaged Agile - 30 Minutes (Dave, Brad) with Peter Lanik Notes", do NOT include that text again in the description
   - Start directly with the content (e.g., "🕞 Started at..." or "## Key Points")

2. **Do NOT add extra line feeds between headers and bullets**
   - ❌ Wrong:
     ```
     ## Key Points

     - Point one
     - Point two
     ```
   - ✅ Right:
     ```
     ## Key Points
     - Point one
     - Point two
     ```

3. **Do NOT add extra line feeds between header lines**
   - ❌ Wrong:
     ```
     ## Key Points
     - Point one

     ## Action Items
     - Action one
     ```
   - ✅ Right:
     ```
     ## Key Points
     - Point one
     ## Action Items
     - Action one
     ```

### Custom Field Value Formats
- **Date fields:** Unix timestamp in milliseconds (date-only: start of day)
- **Drop_down fields:** Use option ID string, not display name

### Task Name Format
- Use format: `YYYY-MM-DD - <Topic>`

### Follow Up Rule
- Set to **Yes** if action items present
- Set to **No** if no action items

## Formatting Checklist

Before creating meeting notes, verify:
- [ ] Meeting title is NOT repeated in the markdown description
- [ ] No blank lines between headers and their content
- [ ] No blank lines between consecutive headers
- [ ] Headers are formatted with `## ` (level 2)
- [ ] Lists use `- ` for bullets
- [ ] Content flows without unnecessary spacing

## Full Documentation

For complete workflow, validation steps, and examples, see:
**`C:\development\cursor-clickup-mcp\docs\guides\documents\doc-to-meeting-task.md`**

## Quick Commands

### Create Meeting Notes Task (Recommended)
Use the skill's automated script to parse notes, create the task, and validate it.

```bash
python scripts/create_meeting_notes.py "path\to\notes.md"
```

**Features:**
- Auto-parses Date, Attendees, and Action Items
- Sets `markdown_description` correctly
- Sets all custom fields (Meeting Date, Follow Up, Attendees, Discussion Summary, Action Items)
- Validates task creation via API
- Supports dry-run mode to preview before creating

### Get Custom Fields for a List
```bash
python -X utf8 "C:\development\cursor-clickup-mcp\scripts\get_list_custom_fields.py" <LIST_ID>
```

### Manual Creation (Advanced)
If you need to create a task manually via Python:
```python
from datetime import datetime
import sys
sys.path.append(r'C:/development/cursor-clickup-mcp/scripts')
from clickup_client import ClickUpClient
import requests

client = ClickUpClient()

# Description (use markdown_description)
desc = """## Key Points
- Point 1
- Point 2

## Action Items
- Action 1
"""

# Meeting Date (date-only, no time)
ts = int(datetime(2026, 1, 8).timestamp()) * 1000

data = {
    "markdown_description": desc,
    "custom_fields": [
        {"id": "19408341-d116-45fc-b30e-8a3a2bbbadbf", "value": ts},
        {"id": "9ddd4ccd-5461-4105-af17-d106f64ceb7f", "value": "a3767735-31ae-4bde-9509-2e4aec952a1f"}
    ]
}

resp = requests.put(f"{API_URL}/task/<TASK_ID>", headers=client.headers, json=data)
print(resp.json().get('url', 'updated'))
```

## Validation After Creation

**ALWAYS validate task via API after creation:**
1. Use `get_task` to retrieve the task you just created
2. Verify:
   - Name matches expected format
   - Custom fields populated correctly
   - Description uses `markdown_description`
3. Only then report success to user with clickable URL
