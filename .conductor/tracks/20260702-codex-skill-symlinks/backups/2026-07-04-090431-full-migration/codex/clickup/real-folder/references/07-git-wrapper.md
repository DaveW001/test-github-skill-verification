# Git Operations (ClickUp Repo)

**Codex Desktop note:** run these from the mounted skill root and keep the `scripts/...` path relative. OpenCode Desktop/CLI uses the same pattern from its mounted skill root.

When working inside the ClickUp integration repo, use the provided wrapper to avoid git pager hangs:

```bash
python scripts/git_helper.py push -m "Commit message"
```
