# Spec

## Goal

Reduce OpenCode skill system prompt overhead from ~5,926 tokens to less than 1,200 tokens by migrating from "all skills always loaded" to a lazy-load architecture using the `@zenobius/opencode-skillful` plugin.

## Current State

- Canonical skill directory: `C:\Users\DaveWitkin\.config\opencode\skill`
- Mirror skill directory: `C:\Users\DaveWitkin\.config\opencode\skills`
- Agent skill symlink directory: `C:\Users\DaveWitkin\.agents\skills`
- OpenCode config file: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- Global agent instructions: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
- Track directory: `C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization`
- Hidden cache directory in canonical skill root: `C:\Users\DaveWitkin\.config\opencode\skill\.osgrep`
  - This is not a skill because it does not contain `SKILL.md`.
  - Do not move it to the lazy skill vault.

## Requirements

- [ ] Back up `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` before editing it.
- [ ] Add `@zenobius/opencode-skillful` to the plugin array in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- [ ] Create lazy skill vault directory: `C:\Users\DaveWitkin\.config\opencode\lazy-skills`.
- [ ] Create plugin config file: `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json`.
- [ ] Keep exactly 4 native skills in scanned skill directories: `conductor`, `osgrep`, `git-push`, `perplexity-search`.
- [ ] Move all other skill directories listed in `migration-inventory.md` to `C:\Users\DaveWitkin\.config\opencode\lazy-skills`.
- [ ] Reduce `C:\Users\DaveWitkin\.config\opencode\skills` to the 4 native skill entries only.
- [ ] Reduce `C:\Users\DaveWitkin\.agents\skills` to valid entries for the 4 native skills only.
- [ ] Update `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` with lazy skill discovery instructions.
- [ ] Create validation evidence in `C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\validation-results.md`.
- [ ] Keep rollback backup for at least 7 days after successful validation.

## Non-Requirements

- [ ] Do not rewrite or refactor any `SKILL.md` content.
- [ ] Do not change how individual skills work internally.
- [ ] Do not migrate to `juhas96/opencode-plugin-preload-skills` in this track.
- [ ] Do not delete skills permanently.
- [ ] Do not address the upstream dual-injection bug `anomalyco/opencode#22236` in this track.

## Architecture Decision

Use `@zenobius/opencode-skillful` because it provides on-demand skill discovery/loading with only three tools:

- `skill_find` — keyword search over lazy skill vaults
- `skill_use` — load a selected skill
- `skill_resource` — read reference docs from lazy skills

The plugin is archived, but the migration is reversible by restoring the backup, removing the plugin from `opencode.jsonc`, deleting `.opencode-skillful.json`, and restoring native skill directories.

## Native Skill Set

Exactly these 4 skills remain native:

| Skill | Reason |
|---|---|
| `conductor` | Core workflow management and track state |
| `osgrep` | Semantic code search and routing |
| `git-push` | Small git workflow skill |
| `perplexity-search` | Foundational web research skill |

## Lazy Skill Set

The exact migration set is documented in:

`C:\development\opencode\.conductor\tracks\20260501-skill-token-optimization\migration-inventory.md`

Any directory under `C:\Users\DaveWitkin\.config\opencode\skill` that contains `SKILL.md` and is not one of the 4 native skills must be moved to the lazy vault.

## Acceptance Criteria

- [ ] `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` contains `@zenobius/opencode-skillful` exactly once.
- [ ] `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json` exists and contains this exact JSON structure:
  ```json
  {
    "debug": false,
    "basePaths": ["C:\\Users\\DaveWitkin\\.config\\opencode\\lazy-skills"],
    "promptRenderer": "xml",
    "modelRenderers": {}
  }
  ```
- [ ] A fresh OpenCode session exposes plugin tools `skill_find`, `skill_use`, and `skill_resource`.
- [ ] A fresh OpenCode session native `<available_skills>` block contains exactly these 4 skills: `conductor`, `osgrep`, `git-push`, `perplexity-search`.
- [ ] Moved skills such as `calendar-today`, `email-draft-reply`, `thinking-partner`, and `image-to-html-reconstruction` do not appear in native `<available_skills>`.
- [ ] `skill_find "calendar"` returns calendar-related lazy skills.
- [ ] `skill_use "calendar-today"` loads the `calendar-today` skill content.
- [ ] `skill_use "clickup-cli"` loads the `clickup-cli` skill content.
- [ ] `skill_resource` successfully reads at least one reference file from a lazy-loaded skill that has reference docs.
- [ ] Native `skill({ name: "conductor" })` still loads Conductor.
- [ ] Native `skill({ name: "osgrep" })` still loads osgrep.
- [ ] Native `skill({ name: "git-push" })` still loads git-push.
- [ ] Native `skill({ name: "perplexity-search" })` still loads perplexity-search.
- [ ] `C:\Users\DaveWitkin\.config\opencode\skill` contains only the 4 native skill directories plus optional hidden non-skill cache directories such as `.osgrep`.
- [ ] `C:\Users\DaveWitkin\.config\opencode\lazy-skills` contains every skill listed under "Move To Lazy Vault" in `migration-inventory.md`.
- [ ] No broken symlinks remain in `C:\Users\DaveWitkin\.agents\skills`.
- [ ] `validation-results.md` documents before token estimate, after token estimate, and percent reduction.
- [ ] Token reduction is at least 80%, with after estimate less than 1,200 tokens.
- [ ] `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` contains a `Lazy-Loaded Skills` section.
