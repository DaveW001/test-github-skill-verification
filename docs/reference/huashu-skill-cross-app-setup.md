# Huashu Skill Cross-App Setup (OpenCode + Antigravity + Codex)

Last updated: 2026-04-23

## Purpose

This document records exactly how `huashu-design` was installed for cross-repo, cross-app use, including:

- what was installed
- where it was installed
- why this topology was chosen
- issues encountered and how to avoid them next time
- maintenance workflow script

## What was installed

- Skill repo: `https://github.com/alchaincyf/huashu-design`
- Skill name (`SKILL.md` frontmatter): `huashu-design`

## Final topology (source of truth + links)

### Canonical source (real directory)

- `C:\Users\DaveWitkin\.local\skills\huashu-design`

This path is the only place that should be edited/updated directly.

### App-facing skill paths (junctions to canonical)

- OpenCode: `C:\Users\DaveWitkin\.config\opencode\skills\huashu-design`
- Antigravity/AionUI-style: `C:\Users\DaveWitkin\.gemini\antigravity\skills\huashu-design`
- Codex (current local behavior): `C:\Users\DaveWitkin\.codex\skills\huashu-design`
- Codex docs-aligned path: `C:\Users\DaveWitkin\.agents\skills\huashu-design`

All four should point to the canonical source above.

## Why this approach

1. **Single source of truth** avoids drift between apps.
2. **Cross-repo availability** at user level.
3. **Cross-app compatibility** (OpenCode + Antigravity + Codex desktop/CLI).
4. **Resilience** against path convention changes (Codex `.codex/skills` vs docs-preferred `.agents/skills`).

## Issues encountered during setup

### 1) Self-referencing junctions (critical)

Symptoms:

- `SKILL.md` looked missing even though path existed.
- `fsutil reparsepoint query` showed a mount-point reparse entry pointing back to itself.
- `Test-Path`/directory listing behaved inconsistently.

Cause:

- During repeated retries, a path that should have been a real directory became a junction to itself.

Mitigation:

- Use a neutral canonical root (`C:\Users\DaveWitkin\.local\skills\...`) not shared by app scanners.
- Recreate app paths as junctions to canonical.
- Validate `SKILL.md` exists through every path after linking.

### 2) `mklink /j` inconsistency for Codex path

Symptoms:

- `cmd /c mklink /j ...` sometimes failed with: `Local volumes are required to complete the operation.`

Mitigation:

- Use PowerShell junction creation (`New-Item -ItemType Junction`) when `mklink` fails.
- The Python maintenance script handles create/remove consistently via shell commands and validation.

### 3) Filesystem state churn during repeated copy/delete attempts

Symptoms:

- nested folders and stale remnants during retries.

Mitigation:

- Avoid repeatedly cloning directly into app skill directories.
- Keep canonical folder stable, only relink targets.

## Maintenance script

Script path:

- `C:\development\opencode\scripts\skill_sync_huashu.py`

### Typical usage

Validate current setup:

```bash
python C:\development\opencode\scripts\skill_sync_huashu.py --check
```

Repair all links to canonical:

```bash
python C:\development\opencode\scripts\skill_sync_huashu.py --repair-links --check
```

If canonical folder is missing, seed it from GitHub and relink:

```bash
python C:\development\opencode\scripts\skill_sync_huashu.py --seed-if-missing --repair-links --check
```

Pull latest changes (when canonical is a git clone):

```bash
python C:\development\opencode\scripts\skill_sync_huashu.py --pull --check
```

## Quick validation checklist for future agents

- [ ] `C:\Users\DaveWitkin\.local\skills\huashu-design\SKILL.md` exists
- [ ] each app path resolves and has `SKILL.md`
- [ ] no app path is self-referential
- [ ] Codex desktop/CLI restarted if new link not immediately visible

## Notes on discovery paths

- Codex docs indicate user-level skills under `~/.agents/skills`.
- This machine also uses `~/.codex/skills` in practice.
- Keeping both linked to canonical is intentional.
