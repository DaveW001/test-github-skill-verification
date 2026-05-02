# Plan

## Phase 1 — Skill Creation Runbook
- [x] Create `~/.config/opencode/templates/skill-creation-runbook.md`
  - Preflight section: naming regex check, path decision (global vs project), frontmatter rules ✓
  - Fidelity guard section: rules for preserving user-provided prompt content verbatim ✓
  - Reference structure section: when to use references, one-level-deep rule, progressive disclosure ✓
  - Activation smoke test section: how to verify the skill loads and activates ✓
  - Validation checklist section: structural + behavioral checks ✓

## Phase 2 — Retro Delivery Checklist
- [x] Create `~/.config/opencode/templates/retro-skill-delivery-checklist.md`
  - 6 mandatory questions (what went well, improve, differently, systemic issues, learned, codify) ✓
  - Systemic improvement categories (skills, commands, agents, preferences, docs) ✓
  - Action mapping template: finding → category → target location → apply/propose ✓
  - Evidence gathering checklist (git state, file reads, context review) ✓
  - Validation section for retro changes ✓

## Phase 3 — Verbatim Preservation Snippet
- [x] Create verbatim-preservation snippet using snippet-writer standards
  - Location: `~/.config/opencode/snippet/verbatim-preservation.md` ✓
  - Include frontmatter with name, description, aliases ✓
  - Body: instructions for preserving user prompt blocks exactly as provided ✓
  - Rules: no condensation, no summarization, no reformatting of quoted prompt text ✓
  - Markers: how to designate "verbatim-preserve zones" in source material ✓
  - Exceptions: when light formatting (whitespace, heading levels) is acceptable ✓

## Phase 4 — Global Skill Index Note
- [x] Create repo-level docs reference pointing to global skill assets
  - Path: `docs/reference/global-skills-index.md` ✓
  - List all global skills by name with one-line description ✓
  - Note the path pattern: `C:\Users\DaveWitkin\.config\opencode\skill\<name>\` ✓
  - Explain the difference between global skills (personal) and project skills (team) ✓
  - Cross-reference the skill-writer skill for creating new ones ✓

## Phase 5 — Validation
- [x] Read-back validate all 4 deliverables
- [x] Verify Skill Creation Runbook covers all retro findings
- [x] Verify Retro Checklist maps to the 6 questions used in this session
- [x] Verify Snippet follows snippet frontmatter standards
- [x] Verify Index Note lists `nlm-meta-prompt` and other existing global skills
- [x] Update this plan.md with completion status

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.
