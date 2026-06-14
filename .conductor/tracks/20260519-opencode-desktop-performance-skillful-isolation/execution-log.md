# Execution Log

## 2026-05-19 Track Creation

- Created track to isolate OpenCode Desktop slowdown after MCP prompt errors and repeated Skillful discovery were observed in Desktop logs.
- Immediate pre-plan action already completed: `control-chrome` and `slack` MCP entries were set to `"enabled": false` in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`; `playwright` was already disabled.
- `opencode debug config` completed successfully after MCP disablement and showed all three MCP entries disabled.
- Plan intentionally does not remove `@zenobius/opencode-skillful`; it defines a controlled A/B test for a later build agent/session.

## 2026-05-19 Phase 0 Setup

- Confirmed `C:\development\opencode`, `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`, and `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json` all existed.
- Created backup folder `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\artifacts\20260519-130610`.
- Backed up `opencode.jsonc` and `.opencode-skillful.json` into that artifact folder.
- Recorded CLI version `opencode 1.14.29`.
- No issues during Phase 0.

## 2026-05-19 MCP Disablement And Restart Validation

- Confirmed `playwright`, `control-chrome`, and `slack` remained disabled in `opencode.jsonc`.
- `opencode debug config` parsed successfully and showed all three MCP services disabled.
- First restart attempt brought OpenCode Desktop back up, but the newest log file remained `C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs\opencode-desktop_2026-05-19_12-34-13.log` with `LastWriteTime` 1:01 PM, older than the restart at 1:09 PM.
- That log still contains historical prompt-discovery errors for `clientName=slack` and `clientName=control-chrome` at `2026-05-19T16:34:36Z` through `2026-05-19T16:34:43Z`.
- A forced quit and relaunch produced new `OpenCode` process start times at `1:09:50 PM`, but no fresh desktop log file appeared during the sampling window.
- Result: config validation passed; post-restart log suppression could not be proven from the available log file because the file was stale.

## 2026-05-19 Duplicate Skill Roots

- Date: 2026-05-19
- Roots inspected: `C:\Users\DaveWitkin\.opencode-lazy-vault`, `C:\Users\DaveWitkin\.agents\skills`, `C:\Users\DaveWitkin\.config\opencode\skill`, `C:\Users\DaveWitkin\.config\opencode\skills`, `C:\development\marketing\.opencode\skills`, `C:\development\playground\.opencode\skills`
- Duplicate skill names: `git-push`, `osgrep`, `perplexity-search`, `skill-discovery`, `conductor`, `nlm-skill`, `pptx-to-pdf-converter`, `imagegen`, and many marketing skill pairs across `C:\development\marketing`.
- Interpretation: the lazy vault is present and healthy, but the current environment still has multiple always-on roots feeding duplicate skill names into OpenCode and Skillful. That explains the duplicate-skill warnings in the desktop log and is a separate cleanup problem from the MCP prompt errors.

## 2026-05-19 Skillful Removal Validation

- Removed only `@zenobius/opencode-skillful` from `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- `rg -n '@zenobius/opencode-skillful'` returned no matches, and `opencode debug config` still parsed successfully.
- A forced restart produced fresh `OpenCode` process start times at `1:09:50 PM`.
- The newest desktop log was still the older `opencode-desktop_2026-05-19_12-34-13.log`, so the post-removal log sample still showed historical `OpencodeSkillful`, `SkillRegistryController`, `duplicate skill name`, and `MaxListenersExceededWarning` lines.
- The GUI smoke test is still pending user action.

## 2026-05-19 Skillful Disabled A/B Result

- Date: 2026-05-19
- Config parse: pass
- Desktop startup: pass
- GUI smoke test: pass
- Log result: Skillful churn remained in the stale pre-restart log sample; no fresh post-restart log file appeared during sampling
- User-perceived responsiveness: unchanged

## 2026-05-19 Phase 4 Decision

- Restored `@zenobius/opencode-skillful` to `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` because the GUI smoke test was acceptable but not clearly faster, so the test did not justify leaving Skillful disabled.
- No user decision was provided for duplicate root cleanup, so `4.3` was left unchanged.
- Updated the troubleshooting note with the required follow-up section.

## 2026-05-19 Final Handover

- Final config state: MCPs disabled, Skillful enabled
- Validation completed: `opencode debug config`; `opencode run -m opencode-go/glm-5.1 "Reply with exactly: CLI performance smoke passed"`; GUI smoke test reported by user as `Skillful disabled smoke test passed`; final Desktop log summary
- Remaining warnings: duplicate skill name warnings remain in the newest Desktop log; no live MCP prompt errors were present in the final log sample
- Rollback: restore `opencode.jsonc` from `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\artifacts\20260519-130610\opencode.jsonc.before-skillful-isolation`
- Recommendation: keep Skillful enabled; no reinstall needed; if performance degrades again, investigate duplicate skill roots and stale Desktop state separately before changing more config
