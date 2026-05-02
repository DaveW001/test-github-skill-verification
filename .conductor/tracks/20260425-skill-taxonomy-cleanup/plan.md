# Plan: Skill Taxonomy Cleanup and Rename Plan

## Phase 0 - Preflight and Archive Setup
- [ ] Inventory exact current skill list from a fresh session.
- [ ] Create timestamped backup folder: `C:\Users\DaveWitkin\.config\opencode\skill-backups\20260425-cleanup\`.
- [ ] Create archive folder for deprecated skills: `C:\Users\DaveWitkin\.config\opencode\_archived_skills\`.
- [ ] Back up every skill directory/file that will be touched.

## Phase 1 - Opaque Name Clarification & Physical Target Renames
Task: `retro` -> `session-retro`
- [ ] Rename folder `skill\retro` to `skill\session-retro`.
- [ ] Update `SKILL.md` frontmatter to `name: session-retro`.
- [ ] Delete `retro` junctions in `.codex\skills` and `.agents\skills`.
- [ ] Create `session-retro` junctions in `.codex\skills` and `.agents\skills`.

Task: `huashu-design` -> `html-demo-design` (Junction Target Rename)
- [ ] Rename physical target `C:\Users\DaveWitkin\.local\skills\huashu-design` to `html-demo-design`.
- [ ] Update `SKILL.md` frontmatter in that target to `name: html-demo-design` and clarify description.
- [ ] Delete old `huashu-design` junctions in `opencode\skill`, `.codex\skills`, and `.agents\skills`.
- [ ] Create new `html-demo-design` junctions in all three locations pointing to the renamed local target.

## Phase 2 - NotebookLM Standardization & Archiving
Task: Standardize active skills
- [ ] Rename `skill\nlm-skill` to `skill\notebooklm-cli` and update frontmatter.
- [ ] Rename `skill\nlm-meta-prompt` to `skill\notebooklm-meta-prompt` and update frontmatter.
- [ ] Sync junctions in `.codex\skills` and `.agents\skills` (delete old, create new).

Task: Archive legacy skills
- [ ] Move `notebooklm` and `notebooklm-legacy` from `opencode\skill` to `_archived_skills\`.
- [ ] Delete their corresponding junctions in `.codex\skills` and `.agents\skills`.

## Phase 3 - Add Cross-References (No Renames)
Add concise "Related skills / Which one should I use?" notes to:
- [ ] `email-auto-sorter`, `outlook-inbox-triage`, `email-draft-reply` (link to each other).
- [ ] `image-generator` and `image-manifest-builder` (link to each other).
- [ ] `thinking-partner` and `first-principles-mastery` (clarify broad vs deep).
- [ ] `snippet-writer` (add note that package-managed `snippets` provides the runtime).

## Phase 4 - Verification
- [ ] Run `skill-writer` validation pass on `session-retro`, `html-demo-design`, `notebooklm-cli`, and `notebooklm-meta-prompt` to ensure directory slug matches frontmatter `name`.
- [ ] Test all newly created junctions using `Test-Path`.
- [ ] Verify OpenCode can discover the new/modified skills after restart.
- [ ] Confirm `available_skills` list is shorter and clearer.

## Phase 5 - Cleanup
- [ ] Update this plan with completed tasks and final decisions.
- [ ] Update `metadata.json` status/progress.

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)
