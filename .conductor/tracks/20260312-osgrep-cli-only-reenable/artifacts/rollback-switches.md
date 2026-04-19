# Rollback Switches (CLI-Only Re-Enablement)

Use this checklist to revert to disabled-by-default behavior quickly.

## Files and Switches

1. `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
   - Set `permission.skill.osgrep` from `"allow"` back to `"deny"`.

2. `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
   - Revert the `Osgrep CLI-Only (Canary)` section to disabled-by-default guidance.
   - Revert tool table row for `osgrep` to disabled state.

3. `C:\Users\DaveWitkin\.config\opencode\agent\build.md`
   - Revert semantic search rule from CLI-only enablement to non-osgrep workflow.

4. `C:\Users\DaveWitkin\.config\opencode\agent\01-planner.md`
   - Revert tool guidance to avoid osgrep usage.

5. `C:\Users\DaveWitkin\.config\opencode\skill\osgrep\SKILL.md`
   - Revert compatibility/status text to disabled mode.

6. `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts`
   - Revert description/status strings to disabled mode messaging.

7. `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md`
   - Revert build agent example language to non-osgrep workflow.

## Post-Rollback Verification

1. Restart OpenCode session to reload config and instructions.
2. Confirm active instructions no longer recommend osgrep.
3. Confirm skill permission in `opencode.jsonc` is `"osgrep": "deny"`.
4. Run one sample semantic prompt and verify fallback to `grep`/`glob`/`Read`.
