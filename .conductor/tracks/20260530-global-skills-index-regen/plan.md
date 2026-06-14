# Plan: Global Skills Index Regeneration

**Track ID**: 20260530-global-skills-index-regen
**Created**: 2026-05-30
**Status**: pending

## Tasks

### Phase 1: Data Collection

- [ ] **T1**: Read all 64 active SKILL.md frontmatters from `~/.agents/skills/` (excluding `_archived_skills/`, `.system/`, `codex-primary-runtime/`)
- [ ] **T2**: Extract `name` and `description` from each frontmatter into a structured dataset
- [ ] **T3**: Read the current `global-skills-index.md` to understand category structure and formatting conventions

### Phase 2: Categorization

- [ ] **T4**: Map all 64 skills to existing or new categories based on their descriptions
  - Existing categories: Content Creation, Visuals & Design, NotebookLM & Research, Development & Deployment, Documents & Publishing, Productivity & Workflow, Email & Communication, Thinking & Analysis, AI & Agent Tooling
  - New categories may be needed for: Google Workspace, Knowledge Management, ClickUp
- [ ] **T5**: Resolve `notebooklm-meta-prompt` duplicate — assign to single category

### Phase 3: Generation

- [ ] **T6**: Generate new markdown tables per category with columns: Skill | Description
- [ ] **T7**: Add table of contents / category headers
- [ ] **T8**: Update "Last updated" date to 2026-05-30
- [ ] **T9**: Write regenerated file to `docs/reference/global-skills-index.md`

### Phase 4: Validation

- [ ] **T10**: Verify all 64 skills present (no missing, no duplicates)
- [ ] **T11**: Verify markdown table syntax is valid
- [ ] **T12**: Run health validator again to confirm 0 flags on index freshness

### Phase 5: Cleanup

- [ ] **T13**: Update CSV log entry for the day if re-running health validator
- [ ] **T14**: Update conductor track status to complete

## Risks

| Risk | Mitigation |
|------|-----------|
| Category assignment disagreements | Use description keywords to auto-classify; document borderline cases |
| Breaking downstream references to index | Preserve table column structure; only add rows |
| Missing frontmatter for some skills | Already validated — all 64 have valid frontmatter |

## Dependencies

- All 64 active skills must remain on disk during regeneration
- No concurrent skill install/uninstall operations
