# Spec: ClickUp Skill Windows UTF-8 Encoding Fix

## Problem

On Windows, ClickUp skill Python scripts fail with `UnicodeEncodeError: 'charmap' codec can't encode character` when task names or descriptions contain Unicode characters (emojis, special characters). This happens because Windows default console encoding is `cp1252`, not UTF-8.

**Example failure:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f3a4' in position 15: character maps to <undefined>
```

## Goal

Make all ClickUp skill scripts handle Unicode output correctly on Windows by configuring UTF-8 encoding at the shared initialization layer, so that task names with emojis and descriptions with special characters work without errors.

## Scope

- **In scope:** The ClickUp skill scripts in the mounted skill root (`scripts/*.py`) and the shared `common.py` module.
- **Out of scope:** Scripts in the external `cursor-clickup-mcp` repo (those are not invoked directly by the skill workflow). Changes to ClickUp API behavior, task formatting, or other skill features.

## Constraints

- Do not break existing functionality on non-Windows platforms (macOS, Linux).
- Do not modify the ClickUp API client or external repo code.
- The fix must be in a single shared location -- not duplicated across every script.
- No new dependencies may be added.

## Definition of Done

1. `common.py` configures UTF-8 stdout/stderr on Windows before any script output occurs.
2. `create_task.py` succeeds with an emoji in the task name (smoke test).
3. `update_task.py` succeeds with Unicode in the description (smoke test).
4. All existing skill scripts still pass preflight (`python scripts/preflight.py`).
5. A troubleshooting note is added to `references/08-troubleshooting.md` documenting this issue and fix.

## Non-Goals

- Rewriting scripts to avoid Unicode entirely.
- Adding a wrapper script or batch file.
- Changing the ClickUp API token or auth flow.
