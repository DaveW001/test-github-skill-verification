# Decision: Archive OpenCode Snippets Plugin and Skill

**Date:** 2026-05-09
**Status:** Completed
**Impact:** Reduces context window overhead in every OpenCode session

---

## What Changed

Removed the `opencode-snippets@1.8.0` plugin and the `snippet-writer` skill from the active OpenCode configuration. All snippet content files have been archived.

## Why

### Context Window Cost

The snippets plugin injected its runtime engine, skill instructions, and available snippet catalog into every OpenCode session's system prompt. This consumed tokens in the context window on every single conversation, regardless of whether snippets were used during that session.

For a feature that was primarily used for text expansion shortcuts (e.g., `#code-review`, `#concise`, `#retro`), this was an inefficient trade of limited context budget.

### Replacement: PhraseExpress

Snippet/text-expansion functionality has been moved to **PhraseExpress**, a dedicated text expansion tool that:

- **Zero context window cost** -- operates entirely outside the LLM
- **Cross-application** -- works in any app (IDEs, email, Slack, browsers), not just OpenCode
- **No plugin overhead** -- no npm packages, no runtime loading, no skill registration
- **Faster execution** -- expands text locally without any LLM round-trip

The snippet content that was previously defined in `~/.config/opencode/snippet/*.md` can be recreated in PhraseExpress as standard text expander phrases.

## What Was Removed

| Item | Location | Action |
|------|----------|--------|
| Plugin entry | `opencode.jsonc` plugin array | Removed `opencode-snippets@1.8.0` |
| `snippet-writer` skill (lazy vault) | `~/.opencode-lazy-vault/snippet-writer/` | Archived to `_archived_skills/` |
| `snippet-writer` skill (native agents) | `~/.agents/skills/snippet-writer/` | Was already empty/archived |
| Snippet content files (25 files) | `~/.config/opencode/snippet/` | Moved to `snippet-archive-20260509/` |
| Cached plugin package | `~/.cache/opencode/packages/opencode-snippets@1.8.0/` | Left in cache (harmless; no longer loaded) |

## What Was Preserved

| Item | Location | Notes |
|------|----------|-------|
| Archived skill | `~/.opencode-lazy-vault/_archived_skills/snippet-writer/SKILL.md` | Marked as archived with date and reason |
| Archived snippet files | `~/.config/opencode/snippet-archive-20260509/` | All 25 snippet `.md` files + `config.jsonc` |
| Config backup | `~/.config/opencode/opencode.jsonc.backup-20260509-remove-snippets` | Pre-change snapshot |
| Conductor tracks | `.conductor/tracks/20260320-*snippet*`, etc. | Historical records; left in place |
| Plugin cache | `~/.cache/opencode/packages/opencode-snippets@1.8.0/` | Not deleted; can be removed manually if desired |

## Snippet Inventory (Archived)

The following 25 snippet definitions were archived and are available for reference when recreating in PhraseExpress:

| Snippet | Purpose |
|---------|---------|
| `atom` | Atomic writing mode |
| `boost` | Productivity boost prompt |
| `careful` | Careful/deliberate mode |
| `claire` | Skeptical CIO persona |
| `clickup-task` | ClickUp task creation |
| `code-review` | Code review request |
| `concise` | Concise response mode |
| `conductor-closeout-check` | Conductor track closeout checklist |
| `conductor-run` | Run conductor workflow |
| `conductor-spec` | Create conductor spec |
| `context` | Show current project context |
| `cove` | Chain-of-Verification |
| `docs-update` | Documentation update prompt |
| `git-status` | Git status summary |
| `handover` | Session handover prompt |
| `install-plugin` | Plugin installation guide |
| `opencode-smoke-test` | OpenCode smoke test |
| `plan-create` | Create a plan |
| `plan-review` | Review a plan |
| `recommendations-only` | Recommendations-only mode |
| `retro` | Session retrospective |
| `typescript` | TypeScript best practices |
| `validate-work` | Work validation checklist |
| `verbatim-preservation` | Verbatim text preservation |

## Rollback

If needed, snippets can be restored by:
1. Adding `"opencode-snippets@1.8.0"` back to the `plugin` array in `opencode.jsonc`
2. Moving snippet files from `snippet-archive-20260509/` back to `~/.config/opencode/snippet/`
3. Restoring the `snippet-writer` skill from `_archived_skills/`
