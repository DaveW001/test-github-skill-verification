# README for C:\\Users\\DaveWitkin\\.opencode-lazy-vault\\README.md
# Canonical copy kept in this repo; deploy by dropping the leading '#' header
# comment lines and writing the remainder to the vault root README.md.

# Lazy-vault skill library

**This directory is the live runtime root for OpenCode and Codex skills and IS version-controlled.**

## Backup and version control

- Every folder/file here is mirrored daily to **https://github.com/DaveW001/opencode-skills** (private).
- Driver: `C:\\development\\01-knowledge-base\\07_scripts_and_utilities\\sync-opencode-skills.ps1`, run by scheduled task `opencode-skills-weekly-backup` (name is legacy; it runs daily at 02:00).
- Script logs: `C:\\development\\opencode-skills-sync-logs\\`. A durable clone lives at `C:\\development\\opencode-skills-sync\\`.
- Sync failures send a Slack DM alert. A sync run only claims success after verifying the remote tip matches local HEAD.

**You do NOT need to run `git` in this directory** (it is not a git repo by design; the mirror script does the git work). After editing any skill, the change reaches GitHub by the next 02:00 run. If the change is urgent, run the sync script manually:

```powershell
& 'C:\\development\\01-knowledge-base\\07_scripts_and_utilities\\sync-opencode-skills.ps1'
```

## Recovery

To restore a skill or the whole vault, clone the backup repo and copy entries back into this directory. History, diffs, and per-file timestamps are in the repo.

## Conventions

- New skills are real folders directly under this root (not junctions). See `C:\\development\\opencode\\docs\\runbooks\\codex-skill-architecture.md`.
- Symlinked entries (agent-creator, conductor, conductor-pipeline, git-push, opencode-scheduler, osgrep, perplexity-search, skill-discovery, ...) resolve into the backup as copied content, so the backup is self-contained.
- Secrets are excluded from the backup via the repo `.gitignore`; never commit `.env` files here expecting them to sync.

## Backup repo layout

- `*/` - individual skills, each with a `SKILL.md` entrypoint
- `_archived_skills/` - superseded or merged skills kept for reference
- `.system/` - OpenAI-bundled system skills (imagegen, openai-docs, skill-creator, etc.)
- Excluded by `.gitignore`: `.env` secrets (only `.env.example` tracked), `__pycache__/`, `*.pyc`, `*.bak`/`*.backup-*`, IDE files.
- Note: at sync time this vault README overwrites the backup repo's root README (same filename, -Force copy). Keep this file as the single source of truth.
