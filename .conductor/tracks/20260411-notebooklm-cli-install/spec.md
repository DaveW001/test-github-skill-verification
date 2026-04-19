# Spec

## Goal
Install the official NotebookLM CLI (`nlm`) from the `notebooklm-mcp-cli` package, verify both shipped executables (`nlm` and `notebooklm-mcp`), and deploy the official OpenCode skill at user level in the actual directory OpenCode scans on this machine. The end state is a fully functional, documented NotebookLM CLI installation with an official skill that can be triggered from any OpenCode session, while preserving a safe rollback path from the legacy custom-built skill.

## Background
The user referenced `jacob-bd/notebooklm-cli`, which is deprecated and merged into `jacob-bd/notebooklm-mcp-cli` (3.5k stars, v0.5.22). The new unified package provides both the CLI (`nlm`) and MCP server (`notebooklm-mcp`) in a single install. It also includes `nlm skill install opencode` which installs official skill files for OpenCode.

There is an existing custom-built NotebookLM skill at `C:\Users\DaveWitkin\.config\opencode\skill\notebooklm\` with hand-written Python scripts, a venv, and browser automation via patchright. It should be preserved until the official skill is installed and verified, then archived (not deleted) with a clear rollback path.

## Requirements
- [ ] Install `notebooklm-mcp-cli` via pip (only available package manager)
- [ ] Record the exact installed package version for reproducibility
- [ ] Verify `nlm` command is accessible from PATH
- [ ] Verify `notebooklm-mcp` command is installed as part of the unified package
- [ ] Record executable locations (`where nlm`, `where notebooklm-mcp`)
- [ ] Run `nlm --version` to confirm version
- [ ] Run `nlm doctor` to validate installation diagnostics, separating install success from expected unauthenticated state
- [ ] Install official OpenCode skill via `nlm skill install opencode`
- [ ] Verify the actual user-level skill directory OpenCode scans on this machine (`skill/` vs `skills/`)
- [ ] Verify the official skill is installed there and discoverable by OpenCode
- [ ] Snapshot existing NotebookLM-related skill files before modifying anything
- [ ] Archive the old custom skill only after successful install and verification of the official skill
- [ ] Preserve a rollback path if official skill installation fails or is not discoverable
- [ ] Capture `nlm --ai` output for reference
- [ ] Verify `nlm --help` works and shows expected command groups
- [ ] Verify `nlm login --check` reports expected pre-auth status without requiring user interaction
- [ ] Document basic usage instructions for the user

## Non-Requirements
- [ ] MCP server configuration (user didn't ask for MCP; CLI-only for now)
- [ ] Completing interactive authentication (requires Chrome + user interaction; will instruct user)
- [ ] Removing or modifying the old custom skill's data files (auth cookies, library, etc.)
- [ ] Installing `uv` or `pipx` package managers

## Acceptance Criteria
- [ ] `nlm --version` returns a version number (v0.5.x)
- [ ] `notebooklm-mcp` is also present from the same package install
- [ ] Exact installed version and executable locations are recorded
- [ ] `nlm doctor` confirms installation health; any auth-related not-logged-in result is treated as expected pre-auth state, not install failure
- [ ] Official OpenCode skill is installed in the actual user-level directory OpenCode uses on this machine
- [ ] Official skill structure and triggerability are verified by reading installed files
- [ ] Old custom skill is archived only after official skill verification, with rollback path documented
- [ ] User has clear instructions for first-time authentication
- [ ] User understands basic `nlm` commands for daily use

## Risks
| Risk | Mitigation |
|------|------------|
| `pip install` requires admin or `--user` flag | Prefer `python -m pip install --user ...`; verify Windows Scripts PATH; record fallback binary path if needed |
| `nlm` installs but is not on PATH | Verify with `where`; capture direct executable path and document it |
| OpenCode skill path differs from assumptions (`skill/` vs `skills/`) | Detect actual discovery path before validating success |
| Old custom skill conflicts with new official skill | Preserve legacy skill until official skill is verified, then archive |
| Authentication requires user interaction (Chrome) | Clearly document the `nlm login` step |
| Cookie expiration (~2-4 weeks) | Document re-auth workflow |
| Rate limits (~50 queries/day free tier) | Note in user instructions |
| Official skill install fails or lacks parity with legacy workflow | Keep snapshot and rollback plan to restore legacy skill name/path |
