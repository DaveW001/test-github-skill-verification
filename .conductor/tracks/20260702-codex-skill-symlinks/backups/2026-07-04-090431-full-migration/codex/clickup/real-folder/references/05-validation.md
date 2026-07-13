# Validation

**Codex Desktop note:** the validation commands below are relative to the mounted skill root. Keep the `scripts/...` paths the same and run them from `C:/Users/DaveWitkin/.codex/skills/clickup` in Codex Desktop or from the OpenCode-mounted skill root in OpenCode.

## Always Validate After Creation (Recommended)

After creating a task, verify it was created correctly:

```bash
python scripts/get_task.py <task_id>
```

Verify at least:
- list/folder
- due date
- priority
- assignees

If anything is wrong, update it immediately via `scripts/update_task.py` (or the alias `scripts/update_task_desc.py`).

Note: task status values are space-specific. In this workspace, use `--status done` (not `complete`).

## Package QA (Parent Task + Subtasks)

When you create a "work package" (one parent task with many subtasks), do a second validation pass that checks:
- The parent exists in the intended list
- The expected number of subtasks exist
- All subtasks have:
  - correct parent
  - assignee(s)
  - due dates
  - no obvious duplicates (same name twice)

### Quick Manual Checks

1) Parent task:

```bash
python scripts/get_task.py <parent_task_id>
```

2) In ClickUp UI:
- Confirm the Subtasks section shows the expected tasks
- Spot-check 2-3 subtasks for assignee and due date

### Fast API Check (Recommended)

Use this snippet to validate the package in one shot. It reads the API token from `C:\development\cursor-clickup-mcp\.env`.

```bash
PYTHONIOENCODING=utf-8 python - <<'PY'
from dotenv import dotenv_values
import requests
from collections import Counter

env = dotenv_values(r"C:\\development\\cursor-clickup-mcp\\.env")
token = env.get("CLICKUP_API_TOKEN")
assert token, "Missing CLICKUP_API_TOKEN"

parent_id = "<parent_task_id>"
expected_list_id = "<list_id_or_blank>"  # optional
expected_subtask_count = None  # set to an int if you know it
expected_assignee = 80264  # Dave Witkin

base = "https://api.clickup.com/api/v2"
headers = {"Authorization": token}

parent = requests.get(
    f"{base}/task/{parent_id}",
    headers=headers,
    params={"include_subtasks": "true"},
).json()

subs = parent.get("subtasks", []) or []
print("parent_name", parent.get("name"))
print("parent_url", parent.get("url"))
print("subtask_count", len(subs))

if expected_list_id:
    actual_list = (parent.get("list") or {}).get("id")
    print("parent_list_id", actual_list)
    assert actual_list == expected_list_id, "Parent task is in wrong list"

if expected_subtask_count is not None:
    assert len(subs) == expected_subtask_count, "Unexpected subtask count"

missing_due = [s for s in subs if not s.get("due_date")]
bad_assignee = [
    s for s in subs
    if expected_assignee not in [a.get("id") for a in (s.get("assignees") or [])]
]
dupes = [name for name, c in Counter([s.get("name") for s in subs]).items() if c > 1]

print("missing_due", len(missing_due))
print("bad_assignee", len(bad_assignee))
print("duplicate_names", dupes)

assert not missing_due, "One or more subtasks missing due dates"
assert not bad_assignee, "One or more subtasks missing expected assignee"
assert not dupes, "Duplicate subtask names detected"

print("OK: package validation passed")
PY
```

Notes:
- If you see duplicates, do not delete automatically. Confirm in ClickUp UI first; then delete only the clearly accidental duplicates.
- If the parent is correct but subtasks are missing, the most common cause is creating tasks in the list without the `parent` field.
