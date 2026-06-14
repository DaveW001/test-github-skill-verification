---
name: skill-discovery
description: Use when finding, editing, loading, or troubleshooting OpenCode skills. Explains that most skills are lazy-loaded via opencode-skillful and should be found with skill_find/skill_use before manually searching folders.
---

# Skill Discovery Router

Before declaring a skill missing or editing a skill, check the lazy-loaded skill system.

## Fast Path

1. Search: `skill_find "<keyword>"`
2. Load: `skill_use "<skill_name>"`
3. Read references if needed: `skill_resource "<relative-path>"`

## Active Lazy-Loaded Skill Vault

- Plugin: `@zenobius/opencode-skillful`
- Config: `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json`
- Current base path: `C:\Users\DaveWitkin\.opencode-lazy-vault`

## Important Distinction

- `skills/` and `skill/` contain always-on or native skills.
- `.opencode-lazy-vault/` contains active lazy-loaded skills.
- `_archived_skills/` and `skill-backups/` are not active unless explicitly restored or configured.
