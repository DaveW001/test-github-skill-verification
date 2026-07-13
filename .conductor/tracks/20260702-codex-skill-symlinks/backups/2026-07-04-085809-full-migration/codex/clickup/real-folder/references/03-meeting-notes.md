# Meeting Notes (Critical Workflow)

**Codex Desktop note:** run the `scripts/...` examples from the mounted skill root at `C:/Users/DaveWitkin/.codex/skills/clickup`. OpenCode Desktop/CLI should use the same relative paths from its own mounted skill root.

## Hard Rule

When creating meeting notes tasks, never use `scripts/create_task.py`.

Always use:
- `scripts/create_meeting_notes.py`

## Meeting Notes List

- List ID: `901107655225`

## Behavior

- No assignees (empty assignees list)
- Task title format: `YYYY-MM-DD - <Topic>`
- Uses `markdown_description` (not `description`)
- Auto-parses:
  - date
  - attendees
  - discussion summary
  - action items
- Auto-validates the created task

## Input Requirements

1. **Title Formatting**:
   - Do **NOT** include the date in the first line (title) of your notes.
   - The script automatically prepends the date to the task name.
   - ✅ Correct: `# Team Sync` → Task Name: `2025-01-23 Team Sync`
   - ❌ Incorrect: `# 2025-01-23 Team Sync` → Task Name: `2025-01-23 2025-01-23 Team Sync` (Duplicate)

2. **File Encoding**:
   - Ensure your file is saved as UTF-8.
   - The script explicitly handles UTF-8 to support emojis.

## Markdown Description Formatting Requirements

**CRITICAL: Follow these formatting rules when writing meeting notes:**

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

## Formatting Checklist

Before creating meeting notes, verify:
- [ ] Meeting title is NOT repeated in the description
- [ ] No blank lines between headers and their content
- [ ] No blank lines between consecutive headers
- [ ] Headers are formatted with `## ` (level 2)
- [ ] Lists use `- ` for bullets
- [ ] Content flows without unnecessary spacing

## Examples

From file (Recommended):

```bash
# Use the mounted skill root for your current app.
python scripts/create_meeting_notes.py --file "C:\path\to\notes.md"
```

Specify Date explicitly:

```bash
python scripts/create_meeting_notes.py --file "C:\path\to\notes.md" --date 2025-01-23
```

From direct text (less common):

```bash
python scripts/create_meeting_notes.py "# Meeting Title\n\nNotes here..."
```
