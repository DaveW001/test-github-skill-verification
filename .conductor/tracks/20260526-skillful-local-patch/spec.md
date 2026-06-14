# Spec

## Goal

Patch the installed `@zenobius/opencode-skillful@1.2.5` plugin to fix the `TypeError: __require is not a function` crash by replacing the Bun-specific `import.meta.require` API with a Node.js-compatible `createRequire` polyfill. This restores lazy skill loading without changing the agent workflow, AGENTS.md, or skill directory structure.

## Requirements

- [ ] Replace `var __require = import.meta.require;` in `dist/index.js` with a Node.js-compatible polyfill using `createRequire(import.meta.url)`
- [ ] Preserve all existing plugin behavior: `skill_find`, `skill_use`, `skill_resource` tools
- [ ] Do NOT modify `.agents/skills/` or `.opencode-lazy-vault/` directories
- [ ] Do NOT modify `opencode.jsonc` or `.opencode-skillful.json` configs
- [ ] Create a timestamped backup of the original `dist/index.js` before patching
- [ ] Verify OpenCode loads the patched plugin without crashing on restart
- [ ] Verify `skill_find` and `skill_use` work against the lazy vault after patch

## Non-Requirements

- [ ] No changes to AGENTS.md or agent workflow instructions
- [ ] No migration to alternative plugins (e.g., opencode-triage)
- [ ] No MCP server lazy-loading changes
- [ ] No skill content modifications

## Acceptance Criteria

- [ ] OpenCode Desktop starts without the `__require is not a function` error
- [ ] `skill_find` returns skills from `.opencode-lazy-vault/`
- [ ] `skill_use` loads a skill body successfully
- [ ] Original `dist/index.js` backed up and recoverable
- [ ] Patch is documented with exact diff for future re-application after `npm update`

## Risks

1. **npm update overwrites the patch** — Mitigated by documenting the exact diff and storing the backup
2. **Bundled file has import hoisting that conflicts with the polyfill** — Mitigated by testing the patch before applying
3. **OpenCode uses Bun runtime (not Node.js)** — If true, the crash has a different root cause; the patch would be a no-op but not harmful
