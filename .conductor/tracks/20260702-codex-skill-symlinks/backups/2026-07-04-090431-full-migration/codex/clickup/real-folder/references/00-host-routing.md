# Host Routing

Use the mounted skill root for the app you are currently running.

## If / Then

- If you are in **Codex Desktop**, the skill is usually mounted at `C:/Users/DaveWitkin/.codex/skills/clickup`.
- If you are in **OpenCode Desktop or CLI**, the skill is usually mounted at `~/.config/opencode/skill/clickup`.
- If a command references `scripts/...`, run it from the mounted skill root for the current app.
- If a snippet needs an absolute path, use the mount path for the app you are in, not the other app's path.
- If you want a runtime check, run `python scripts/preflight.py`; it prints the detected skill root and host mount.

## Rule Of Thumb

- Prefer relative paths inside the skill: `scripts/preflight.py`, `scripts/create_task.py`, `scripts/get_task.py`.
- Prefer the mounted skill root over the external repo root when a command is about skill scripts.
- Only use the external repo root (`C:/development/cursor-clickup-mcp`) when the command is explicitly about the integration repo itself.
