# Troubleshooting: Create/Update Failures (Targeted)

**Codex Desktop note:** the commands below can be run as-is from the mounted skill root. If you are in OpenCode Desktop/CLI, use the same relative commands from that app's mounted skill root.

Use this only when ClickUp task create/update fails. Keep this flow short and deterministic.

## UnicodeEncodeError on Windows (Emoji/Special Characters)

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f3a4' in position 15: character maps to <undefined>
```

**Cause:**
Windows default console encoding is `cp1252`, which cannot represent emojis or many Unicode characters. Python's `sys.stdout` inherits this encoding.

**Fix:**
The skill's `common.py` module now configures UTF-8 encoding for stdout/stderr on Windows. This fix is applied automatically when any skill script runs.

**If the error persists:**
1. Verify `common.py` contains the `sys.stdout.reconfigure(encoding='utf-8')` block near the top.
2. Check that the script imports `common.py` before any `click.echo()` or `print()` calls.
3. As a workaround, set the environment variable before running: `='utf-8'`
4. Avoid emojis in task names as a last resort.

## Problem Pattern We Hit

- Symptom: `401 Unauthorized` on task creation to a "Marketing" destination.
- Initial assumption: bad API token.
- Actual root cause: used **Marketing folder ID** (`2906846`) as if it were a **list ID**.
- Fix: resolve and use **Marketing list ID** (`3985253`).

## Another Common 401 Pattern (Env Token Overrides Real Token)

- Symptom: `401 Unauthorized` on env-only checks (or ad-hoc scripts that don't load dotenv).
- Initial assumption: ClickUp is down or token in `.env` is wrong.
- Actual root cause: the shell has `CLICKUP_API_TOKEN` set to a placeholder value (e.g., `yourtoken`) which overrides `.env` loading.
- Fix: remove/replace the placeholder env var, or explicitly load the token from `C:\development\cursor-clickup-mcp\.env` for the current run.

Note: the ClickUp client used by this skill will prefer `C:\development\.env.mcp` and will override placeholder env tokens when loading dotenv. It's still best to unset placeholder env vars to avoid confusion.

## Common 400 Pattern (Invalid Status)

- Symptom: `400 Bad Request` when updating a task status (often when using `--status complete`).
- Root cause: status values are space-specific; in this workspace the terminal status is `done`.
- Fix: use `--status done` (the wrappers also normalize `complete`/`completed` -> `done`).

## Why This Is Easy to Misdiagnose

- Preflight may show warnings about placeholder env tokens in the shell.
- ClickUp errors can be ambiguous when resource type is wrong (folder vs list), especially if endpoint expects list IDs.
- A 401 does not always mean token is wrong; it can be wrong resource scope/type.

## 3-Step Fast Triage (Progressive Disclosure)

### Step 1: Prove token is valid (do not guess)

Run a simple authenticated read.

Preferred (uses the same token-resolution behavior as the skill scripts; prefers `C:\development\.env.mcp`):

```bash
python - <<'PY'
import sys, requests
from pathlib import Path
skill_root = Path(r"C:\Users\DaveWitkin\.codex\skills\clickup")
if not skill_root.exists():
    skill_root = Path.home() / ".config" / "opencode" / "skill" / "clickup"
sys.path.insert(0, str(skill_root / "scripts"))
import common
common.setup_path()
from clickup_client import ClickUpClient

c = ClickUpClient()
r = requests.get("https://api.clickup.com/api/v2/user", headers={"Authorization": c.api_token}, timeout=20)
print(r.status_code)
PY
```

Legacy (uses `clickup_api.py` token loading; kept for compatibility):

```bash
python -c "import sys,requests; sys.path.insert(0,'C:/development/cursor-clickup-mcp'); import clickup_api as c; r=requests.get('https://api.clickup.com/api/v2/team', headers={'Authorization':c.API_TOKEN,'Content-Type':'application/json'}, timeout=20); print(r.status_code)"
```

Interpretation:
- `200`: token is valid -> move to ID/type checks.
- `401`: token/auth issue -> stop and fix credentials.

If you get `401`, do *one more* check before escalating:
- Inspect whether `CLICKUP_API_TOKEN` is set in the shell and looks like a placeholder (very short, contains `yourtoken`). If yes, unset it and retry Step 1.

### Step 2: Verify destination is a list ID

If user gave a folder-like destination (e.g., "Marketing"), resolve lists under folder:

```bash
python -c "import sys,requests; sys.path.insert(0,'C:/development/cursor-clickup-mcp'); import clickup_api as c; r=requests.get('https://api.clickup.com/api/v2/folder/2906846/list', headers={'Authorization':c.API_TOKEN,'Content-Type':'application/json'}, timeout=30); print(r.status_code); print([(x.get('name'),x.get('id')) for x in r.json().get('lists',[])])"
```

Then select correct list ID (for Marketing list, `3985253`).

### Step 3: Retry create with resolved list ID

Use `scripts/create_task.py --list-id <resolved_list_id> ...` and validate with `scripts/get_task.py <task_id>`.

## Decision Rule for Agents

When create/update fails:
1. Validate token via `/team` first.
2. Validate resource type (list vs folder) second.
3. Only report "token issue" if `/team` auth check fails.
4. If `/team` passes, report likely ID/type mismatch and self-recover by resolving IDs.

## Minimal User Escalation

Ask user only if both are true:
- token check passes, and
- multiple possible list IDs match destination semantics.

Otherwise resolve and proceed automatically.
