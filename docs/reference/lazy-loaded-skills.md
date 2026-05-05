# Lazy-Loaded Skills Architecture

This document outlines the lazy-loaded skills architecture implemented in May 2026 using the `@zenobius/opencode-skillful` plugin. It serves as a reference for agents to understand the setup, troubleshoot issues, and maintain token efficiency.

## 1. Overview & Rationale

**The Problem:** OpenCode naturally scans `~/.config/opencode/skill/` and aggressively injects every discovered `SKILL.md` into the agent's system prompt (`<available_skills>`). With over 50 skills, this caused a massive token bloat—consuming roughly **~6,000 tokens** for every single message.
**The Solution:** We migrated from an "all skills always loaded" approach to a lazy-loaded architecture. We reduced the native folder to just **4 essential skills** and moved the remaining **50 skills** to a separate "lazy vault", dropping the prompt overhead to **~400 tokens** (~93% reduction). 

## 2. Architecture & Configuration

The setup relies on the `@zenobius/opencode-skillful` plugin to provide on-demand discovery and loading.

### Key Directories
* **Native Vault (`C:\Users\DaveWitkin\.config\opencode\skill\`):**
  Only the most foundational skills live here. They are injected natively.
  * *Current Native Skills:* `conductor`, `git-push`, `osgrep`, `perplexity-search`. (Note: `snippets` is also injected natively via its own npm package).
* **Lazy Vault (`C:\Users\DaveWitkin\.opencode-lazy-vault\`):**
  The storage directory for all other skills (e.g., email, calendar, ClickUp, UI design). OpenCode does not scan this natively.
* **Mirrors & Symlinks:**
  `C:\Users\DaveWitkin\.config\opencode\skills\` and `C:\Users\DaveWitkin\.agents\skills\` must only contain entries for the native skills. If lazy skills are placed here, OpenCode will inject them into the prompt and defeat the optimization.

### Configuration Files
* **Plugin Registration (`C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`):**
  Contains `"@zenobius/opencode-skillful"` in the `plugin` array.
* **Skillful Config (`C:\Users\DaveWitkin\.config\opencode-skillful\.opencode-skillful.json`):**
  Tells the plugin where to find the lazy skills.
  ```json
  {
    "debug": false,
    "basePaths": ["C:/Users/DaveWitkin/.opencode-lazy-vault"],
    "promptRenderer": "xml",
    "modelRenderers": {}
  }
  ```
  > **⚠️ Config Path Critical:** The plugin's bunfig loader searches `~/.config/opencode-skillful/`, `~/.config/` directly, and `~/` — NOT `~/.config/opencode/`. The config MUST be at `~/.config/opencode-skillful/.opencode-skillful.json` or the plugin will silently fail to discover lazy skills.

## 3. Agent Workflow: Using Lazy Skills

Agents should use the following tools to interact with non-native skills:

1. **Discovery:** `skill_find "<keyword>"` (e.g., `skill_find "calendar"`)
2. **Loading:** `skill_use "<skill_name>"` (e.g., `skill_use "calendar_today"`) — use **underscores**, not hyphens; the plugin normalizes the YAML `name:` field to underscores.
3. **Reference Docs:** `skill_resource "<resource-path>"` (to read supporting markdown files referenced inside the loaded skill).

## 4. Migration History & Testing Notes (May 2026)

During the implementation (Track `20260501-skill-token-optimization`), we ran into a few specific edge cases that future agents should be aware of:

* **The "Stale Prompt" Timeline Confusion:**
  During testing, an agent asked the user to start a fresh OpenCode session to verify the token reduction *before* the bulk migration of files was fully complete. Because system prompts are captured at the exact moment a session starts, that new session captured all 52 skills. This led to a confusing debugging cycle where it seemed the plugin or the globber was broken. 
  *Lesson:* Always ensure file moves are 100% complete before starting a new session to verify system prompt changes.
* **Tool Syntax Strictness:** 
  The `skill_use` tool normalizes skill names using underscores (e.g., `calendar_today`, `outlook_email_search`), regardless of whether the directory name uses hyphens (`calendar-today/`). The plugin reads the `name:` field from YAML frontmatter. If a skill's `name:` field uses hyphens, skill_use will accept both forms, but the canonical form returned by `skill_find` uses underscores.
  *Lesson:* Always check the `name:` field in the SKILL.md frontmatter, and prefer the name exactly as returned by `skill_find` output.

## 5. Troubleshooting Guide

If you are an agent troubleshooting skill issues, check the following:

| Symptom | Diagnosis & Fix |
| :--- | :--- |
| **System prompt is huge again** | Another agent likely created new skills in `~\.config\opencode\skill\` instead of the `.opencode-lazy-vault` vault. Move them to the lazy vault. |
| **`skill_find` returns nothing** | Check `~/.config/opencode-skillful/.opencode-skillful.json` (NOT `~/.config/opencode/`). Ensure the `basePaths` array points exactly to the absolute path for `.opencode-lazy-vault`. Forward slashes work (`C:/Users/...`). |
| **`skill_use` returns "skill not found"** | Verify you are using **underscores** (e.g., `email_draft_reply`), matching the `name:` field in the skill's YAML frontmatter. Check if the skill directory actually exists in the lazy vault and has valid frontmatter with `name:` and `description:` fields. |
| **Skill tools are completely missing** | Check `opencode.jsonc` to ensure `@zenobius/opencode-skillful` is still in the `plugin` array. Ensure the plugin didn't crash on startup. |

### Rollback Procedure
If the plugin critically fails and must be removed:
1. Delete `~/.config/opencode-skillful/.opencode-skillful.json`.
2. Remove the plugin from `opencode.jsonc`.
3. Move all folders from `.opencode-lazy-vault/` back to `skill/`.
4. Recreate symlinks in `~/.agents/skills/` if necessary.
5. Restart OpenCode.