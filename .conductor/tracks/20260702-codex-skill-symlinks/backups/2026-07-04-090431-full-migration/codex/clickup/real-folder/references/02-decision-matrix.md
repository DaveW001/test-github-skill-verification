# Decision Matrix

Use this as the first routing step.

| If user asks... | Do this (default) |
|---|---|
| Create meeting notes | Run `scripts/create_meeting_notes.py` (never `create_task.py`) |
| Create a regular task | Run `scripts/create_task.py` (defaults to Inbox unless list provided) |
| Update a task | Run `scripts/update_task.py` (preferred). `scripts/update_task_desc.py` is a compatibility alias. |
| Find a task by number | Use `scripts/task_numbering.py` or extract ID from URL |
| Get a task by URL | Extract task ID, then run `scripts/get_task.py <id>` |
| Prioritization report | Run `scripts/prioritize.py` (and Slack sender if required) |
| Templates | Run `scripts/templates.py` |
| Create/update fails (400/401/404) | Run targeted triage in `references/08-troubleshooting.md` before blaming token; verify ID type (list vs folder) |
| Git ops in clickup repo | Use `scripts/git_helper.py` wrappers |

General rules:
- Search first when duplicates are likely.
- Validate after creation for important tasks.
- If list/folder is ambiguous, resolve IDs first (use list IDs for task creation, not folder IDs).

Operational gotchas:
- Status values are space-specific. In this workspace the terminal status is commonly `done` (not `complete`). The wrappers normalize `complete`/`completed` -> `done`.
- If `CLICKUP_API_TOKEN` is set in the shell to a placeholder (e.g. `your_token`), it can override the real token from `.env`. The scripts sanitize placeholder values, but it's still best to unset the placeholder globally.
