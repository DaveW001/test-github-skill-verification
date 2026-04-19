# Plan

## Phase 1 - Preflight & Install Strategy
- [x] Snapshot current NotebookLM-related skill paths and files before making changes
- [x] Verify the OpenCode user-level skill discovery path on this machine (`skill/` vs `skills/`)
- [x] Install with preferred Windows-safe command: `python -m pip install --user notebooklm-mcp-cli`
- [x] If needed, troubleshoot Windows Scripts PATH and record direct binary locations

## Phase 2 - Verify Package Installation
- [x] Verify `nlm --version`
- [x] Verify `notebooklm-mcp` is installed (`--help` or equivalent)
- [x] Record exact package version and executable locations with `where nlm` and `where notebooklm-mcp`
- [x] Run `nlm --help` to confirm expected command groups are available
- [x] Run `nlm doctor` and interpret auth-related not-logged-in results as expected pre-auth state

## Phase 3 - Install & Verify Official OpenCode Skill
- [x] Run `nlm skill install opencode` to install the official skill at user level
- [x] Verify the installed skill exists in the actual OpenCode-discovered user directory
- [x] Read installed `SKILL.md` to confirm structure, naming, and trigger coverage
- [x] Compare official skill placement against the legacy custom skill location
- [x] Archive old custom skill only after the official skill is verified
- [x] Document rollback steps to restore the legacy skill if needed

## Phase 4 - Validate & Document
- [x] Run `nlm --ai` and capture output to a reference file in the track
- [x] Run `nlm login --check` to confirm auth status (expected: not authenticated yet)
- [~] Document the complete setup summary for the user including:
  - What was installed and where
  - Exact installed version and executable locations
  - First-time authentication steps (`nlm login`)
  - Basic command cheat sheet
  - How the skill integrates with OpenCode
  - Legacy skill archive/rollback note
  - Important notes (session lifetime, rate limits, re-auth)

## Phase 5 - User Handoff
- [ ] Present clear summary to user
- [ ] Explain what they need to do manually (authentication)
- [ ] Explain how to use the skill in OpenCode sessions

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.
