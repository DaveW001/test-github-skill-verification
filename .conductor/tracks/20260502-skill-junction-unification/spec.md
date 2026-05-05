# Spec — Skill Junction Unification

## Goal

Unify skill discovery across OpenCode, Codex, and `.agents` by establishing a single source of truth for all skills and repairing 49 broken junctions in Codex's `~/.codex/skills/` directory.

## Problem Statement

When skills were migrated from `~/.config/opencode/skill/` to `~/.opencode-lazy-vault/` for the `@zenobius/opencode-skillful` lazy-loading plugin (track `20260501-skill-token-optimization`), the junctions that Codex (and `.agents`) use to discover skills were never updated. Today:

- **Codex** (`~/.codex/skills/`) has 54 junctions: 49 are broken (dangling pointers to moved/deleted directories), 5 work.
- **`.agents`** (`~/.agents/skills/`) has 4 junctions — only the always-on skills, missing all 50 lazy-vault skills.
- **`skill_find`/`skill_use`** can only discover the 50 skills in the lazy vault; the 4 always-on skills in `skill/` are invisible to the plugin's `basePaths` config.
- **Antigravity** (`~/.antigravity/`) has no `skills/` directory at all — it was never set up with junctions.

## Current Skill Locations

| Tier | Location | Count | Skills |
|------|----------|-------|--------|
| Always-on (native) | `C:\Users\DaveWitkin\.config\opencode\skill\` | 4 | conductor, git-push, osgrep, perplexity-search |
| Lazy vault | `C:\Users\DaveWitkin\.opencode-lazy-vault\` | 50 | agent-writer through youtube-shorts (incl. microsoft-graph) |
| **Total unique** | | **54** | |

## Requirements

- [ ] R1: All 54 skills are discoverable by `skill_find`/`skill_use` in OpenCode
- [ ] R2: All 54 skills are visible to Codex via `~/.codex/skills/` junction(s)
- [ ] R3: All 54 skills are visible to `.agents` via `~/.agents/skills/` junction(s)
- [ ] R4: Junctions are maintainable — adding/removing a skill from the vault requires zero junction maintenance
- [ ] R5: The 4 always-on skills remain in `~/.config/opencode/skill/` for OpenCode's native scanner
- [ ] R6: No skill content is modified — only junction targets and plugin config change
- [ ] R7: Rollback procedure exists and is documented

## Non-Requirements

- [ ] Setting up Antigravity skill junctions (it has no `skills/` directory; out of scope)
- [ ] Modifying skill content (SKILL.md, reference files, scripts)
- [ ] Changing the lazy-loading plugin itself (`@zenobius/opencode-skillful`)
- [ ] Moving skills between always-on and lazy-vault tiers
- [ ] Fixing the `~/.local/skills/html-demo-design/` duplicate (flagged for future cleanup)

## Architecture Decision

**Single source of truth: `~/.opencode-lazy-vault/`**

The lazy vault becomes the "complete set" by adding 4 junctions (pointing to `skill/`) for the always-on skills. Then Codex and `.agents` each get ONE parent-level junction to the vault, replacing all individual skill-level junctions.

```
~/.opencode-lazy-vault/              ← Primary directory (54 entries)
├── agent-writer/                     ← real directory
├── ... (49 more real directories)
├── conductor → junction → ~/.config/opencode/skill/conductor/
├── git-push    → junction → ~/.config/opencode/skill/git-push/
├── osgrep      → junction → ~/.config/opencode/skill/osgrep/
└── perplexity-search → junction → ~/.config/opencode/skill/perplexity-search/

~/.codex/skills/      → junction → ~/.opencode-lazy-vault/
~/.agents/skills/     → junction → ~/.opencode-lazy-vault/
```

## Acceptance Criteria

- [ ] `skill_find "*"` returns all 54 skills (4 always-on + 50 lazy)
- [ ] Codex `~/.codex/skills/` resolves all 54 skill directories
- [ ] `.agents` `~/.agents/skills/` resolves all 54 skill directories
- [ ] OpenCode's `<available_skills>` system prompt still shows only 4 always-on skills (token optimization preserved)
- [ ] No broken junctions remain in `~/.codex/skills/`
- [ ] Adding a new skill folder to `~/.opencode-lazy-vault/` is immediately visible to Codex and `.agents` without any junction changes
