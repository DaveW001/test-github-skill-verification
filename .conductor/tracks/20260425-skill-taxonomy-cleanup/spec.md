# Spec: Skill Taxonomy Cleanup and Rename Plan

## Goal
Reduce duplicate/ambiguous OpenCode skill entries and improve skill discoverability by standardizing names, moving legacy duplicates to an archive, and adding cross-references between overlapping skills.

## Architectural Constraints & Corrections
1. **The Frontmatter Mismatch Trap**: An OpenCode skill directory name MUST exactly match the `name:` in its `SKILL.md`. Therefore, we cannot have two different junction names pointing to the same target folder, nor can we rename a junction without renaming its target.
2. **The Clutter Rule**: Leaving "deprecated stubs" in the active skill directory means they will still be loaded into the LLM's system prompt. To truly reduce clutter, deprecated skills must be physically moved out of the `skill` directory into an `_archived_skills` folder.
3. **Cross-Surface Syncing**: Every rename operation in the canonical OpenCode folder MUST be mirrored by deleting the old junction and creating a new junction in both `.codex/skills` and `.agents/skills`.

## Scope

### In Scope
- [ ] Create `C:\Users\DaveWitkin\.config\opencode\_archived_skills\` to safely store deprecated skills out of the runtime path.
- [ ] Standardize NotebookLM naming:
  - `nlm-skill` → `notebooklm-cli`
  - `nlm-meta-prompt` → `notebooklm-meta-prompt`
  - `notebooklm` & `notebooklm-legacy` → move to `_archived_skills`
- [ ] Clarify opaque names:
  - `retro` → `session-retro`
  - `huashu-design` → physically rename target to `C:\Users\DaveWitkin\.local\skills\html-demo-design`, update frontmatter, and recreate junctions as `html-demo-design`.
- [ ] Add "Related skills" cross-references to overlapping skills (email trio, thinking/first-principles, image generation).
- [ ] Explicitly remove orphaned `.codex` and `.agents` junctions for renamed skills and create the new ones.
- [ ] Validate all modified skills with `skill-writer` rules.

### Out of Scope
- [ ] Renaming the `snippets` package-managed skill (modifying npm cache is unsafe). We will rely on cross-referencing in `snippet-writer` instead.
- [ ] Rewriting actual skill logic or workflows.

## Acceptance Criteria
- [ ] Deprecated skills are moved to `_archived_skills/` and no longer appear in the active skill list.
- [ ] All renamed skills (e.g., `session-retro`, `html-demo-design`) pass Skill Writer validation (directory name == frontmatter name).
- [ ] Codex and `.agents` skill directories contain no broken junctions, and new junctions reflect the renamed skills.
- [ ] A fresh OpenCode session shows a cleanly reduced, clearly named `available_skills` list.
