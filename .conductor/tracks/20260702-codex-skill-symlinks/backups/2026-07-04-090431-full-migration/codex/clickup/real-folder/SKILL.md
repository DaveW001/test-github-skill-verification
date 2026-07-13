---
name: clickup
description: Create, update, search, and prioritize ClickUp tasks. Use when the user asks to create a ClickUp task, update a task, add meeting notes, generate a prioritization report, or references task numbering like "task 01".
triggers:
  intent:
    - clickup task management
    - clickup meeting notes capture
    - prioritization reporting
  user_phrases:
    - create clickup task
    - update clickup
    - add meeting notes
  file_context:
    extensions: [md, txt, csv]
    paths: [docs/**, notes/**]
  tool_context:
    before_tools: [bash, read]
    with_tools: [bash]
  error_context:
    - action items not captured
    - task tracking requested
  priority: medium
  suggest_only: true
compatibility: Requires Python and a local ClickUp integration repo + .env with ClickUp credentials (never print or commit tokens)
---

# ClickUp

Manage ClickUp tasks from the current host app using the bundled scripts in this skill.

## Host App Routing

- If you are running in **Codex Desktop**, use the mounted skill root at `C:/Users/DaveWitkin/.codex/skills/clickup`.
- If you are running in **OpenCode Desktop or CLI**, use the mounted skill root at `~/.config/opencode/skill/clickup`.
- In either case, run commands from the mounted skill root and keep script paths relative, for example `python scripts/preflight.py`.
- Do not hardcode one app's mount path into reusable commands unless the command is explicitly app-specific.

## Quick Configuration Reference

Use these values when creating tasks (no need to ask the user):

| Setting | Value |
|---------|-------|
| **Workspace ID** | `59530` |
| **Dave's User ID** | `80264` |
| **Inbox List ID** | `3984798` (default for new tasks) |
| **Meeting Notes List ID** | `901107655225` |
| **Business Development List ID** | `901103985125` |

## External Dependency (IMPORTANT)

This skill requires an external repository: **cursor-clickup-mcp**

### What is it?
The `cursor-clickup-mcp` repository contains:
- Core ClickUp API client (`clickup_api.py`)
- ClickUp client wrapper (`clickup_client.py`)
- Date utilities and helper functions
- Additional ClickUp management scripts

### Where should it be?
**Default location:** `C:/development/cursor-clickup-mcp`

**Alternative locations** (auto-discovered):
- `~/cursor-clickup-mcp`
- `~/development/cursor-clickup-mcp`
- `C:/dev/cursor-clickup-mcp`
- `/mnt/c/development/cursor-clickup-mcp` (WSL)
- `/Users/$USER/development/cursor-clickup-mcp` (Mac)

### How to configure the path

**Option 1: Edit config.yaml** (Recommended)
```yaml
# Edit the config file in the mounted skill root for your host app
external_repo:
  path: "C:/your/custom/path/cursor-clickup-mcp"
```

**Option 2: Environment Variable**
```bash
export CLICKUP_REPO_PATH="C:/your/custom/path/cursor-clickup-mcp"
```

**Option 3: Auto-discovery**
The skill will automatically search for the repo in common locations and update the config file.

### What if it's not found?

The skill will show an error message like:
```
❌ External cursor-clickup-mcp repository not found!

Expected locations:
  - Primary: C:/development/cursor-clickup-mcp
  - Or in fallback paths (see config.yaml)

To fix:
  1. Ensure cursor-clickup-mcp exists at one of the expected locations
  2. Or update the mounted skill root's `config.yaml` with the correct path
  3. Or set the repo path in your environment: CLICKUP_REPO_PATH
```

## Safety Policy (Non-Negotiable)

- Never print, paste, or log API tokens.
- Never commit `.env` files.
- If you need confirmation (list choice, due date intent), ask before creating tasks.

## Preflight

Before doing anything, read `references/01-preflight.md`.

The preflight check will:
1. ✅ Verify external repo exists and is accessible
2. ✅ Check required files are present
3. ✅ Test imports of critical modules
4. ✅ Verify ClickUp API credentials are configured

## Decision Tree

Start with `references/02-decision-matrix.md`.

## Core Workflows
**IMPORTANT**: Always run preflight checks before any ClickUp operation.

- Preflight (REQUIRED): `references/01-preflight.md`
- Host routing: `references/00-host-routing.md`
- Meeting notes (critical): `references/03-meeting-notes.md`
- Due dates: `references/04-due-dates.md`
- Validation: `references/05-validation.md`
- IDs and lists: `references/06-ids-and-lists.md`
- Git wrapper: `references/07-git-wrapper.md`
- Troubleshooting (targeted): `references/08-troubleshooting.md`

## Where to Find More Information

The `references/` folder contains detailed documentation for every ClickUp operation:

| File | What's Inside | When to Read |
|------|---------------|--------------|
| `references/00-host-routing.md` | Which skill root to use in Codex Desktop vs OpenCode Desktop/CLI | Before any command path is chosen |
| `references/01-preflight.md` | Environment setup, .env file locations, required variables (CLICKUP_API_TOKEN, CLICKUP_WORKSPACE_ID, CLICKUP_USER_ID, SLACK_WEBHOOK_URL) | **Before ANY ClickUp operation** |
| `references/02-decision-matrix.md` | Routing guide - which script to use for each request type | When deciding how to handle a user request |
| `references/03-meeting-notes.md` | Detailed workflow for creating meeting notes tasks | When user asks for meeting notes |
| `references/04-due-dates.md` | How to handle due dates, relative dates, and scheduling | When a task needs a due date |
| `references/05-validation.md` | How to validate task creation and updates | After creating important tasks |
| `references/06-ids-and-lists.md` | All list IDs, folder IDs, and workspace configuration | When you need specific list/folder IDs |
| `references/07-git-wrapper.md` | Git operations within the ClickUp repo | When doing git ops in the skill repo |
| `references/08-troubleshooting.md` | Fast diagnosis for 400/401/404 create-task failures and folder-vs-list mistakes | Only when create/update fails |

**Scripts location:** the mounted skill root for the current host app, then `scripts/`

**Config location:** the mounted skill root for the current host app, then `config.yaml`

## Activation Examples (Expected Behavior)

- "Create a ClickUp task: ..." -> run preflight, then `scripts/create_task.py`, then validate via `scripts/get_task.py`
- "Add meeting notes for today" -> run preflight, then `scripts/create_meeting_notes.py` (never `create_task.py`)
- "Update task 01" -> resolve ID via `scripts/task_numbering.py`, then update via `scripts/update_task.py`
- "Send me the prioritization report" -> run `scripts/prioritize.py` (and Slack sender if required)

## Markdown Formatting in Task Descriptions

All task descriptions support **Markdown formatting**. The skill automatically uses ClickUp's `markdown_description` field to ensure proper rendering.

**Supported formatting:**
- `**bold**` → **bold**
- `*italic*` or `_italic_` → *italic*
- `## Heading` → Heading
- `- bullet` → • bullet
- `[link](url)` → clickable link
- `` `code` `` → `code`

**Example:**
```bash
python scripts/create_task.py \
  --name "Test Task" \
  --description "## Key Points
- Point one
- Point two

**Bold text** and _italic text_"
```

## Notes

- Prefer scripts over writing new code. Only write temporary scripts as a last resort.
- Keep paths in docs portable (forward slashes).
- **Default behavior:** Tasks are automatically assigned to Dave (80264) and placed in Inbox (3984798) unless specified otherwise.
- **Path resolution:** The skill uses smart path resolution to find the external repo. See the mounted skill root's `config.yaml` for details.
