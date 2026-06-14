# OpenCode Desktop Performance: Skillful Isolation

## Goal / Outcome

Diagnose and reduce OpenCode Desktop slowdown after the dual OpenCode Go subscription setup by isolating noisy MCP startup behavior from lazy skill discovery behavior, then validate whether `@zenobius/opencode-skillful` should remain enabled, be reconfigured, or be temporarily removed.

## Constraints / Non-Goals

- Do not reinstall OpenCode Desktop until config and plugin causes have been isolated.
- Do not remove API keys, providers, models, or the working OpenCode Go setup.
- Do not delete skill folders or junctions during initial troubleshooting; rename or disable only after backups and explicit validation.
- Do not expose secret values from `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` or `.env` in logs, docs, or screenshots.
- Keep all changes reversible with timestamped backups.

## Definition Of Done

- `control-chrome`, `slack`, and `playwright` MCPs are confirmed disabled in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- A baseline Desktop log is captured after MCP disablement and compared against the prior noisy log.
- A controlled A/B test is documented for running OpenCode Desktop with and without `@zenobius/opencode-skillful`.
- The lazy skill discovery configuration at `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json` and related docs are inspected and summarized.
- The final recommendation states whether to keep Skillful, reconfigure it, or disable it, with rollback steps.
- CLI config validation and at least one Desktop smoke test are recorded in the execution log.

## Current Evidence

- OpenCode Desktop startup was fast in the latest inspected logs: `Server ready elapsed=1.1484155s`.
- The app then repeatedly discovered and initialized skills through `OpencodeSkillful`.
- Logs showed repeated `MCP error -32601` prompt-discovery errors for `slack` and `control-chrome`.
- Logs showed duplicate skill-name warnings across `C:\Users\DaveWitkin\.agents\skills`, `C:\Users\DaveWitkin\.config\opencode\skill`, `C:\Users\DaveWitkin\.config\opencode\skills`, and project-local `.opencode\skills` folders.
- A later log showed `MaxListenersExceededWarning`, consistent with repeated event listener registration.
- `opencode debug config` parses after disabling the MCP entries.

## Key Files

- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json`
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
- `C:\Users\DaveWitkin\.config\opencode\docs\SKILL-SYNC-SETUP.md`
- `C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs`
- `C:\development\opencode\docs\troubleshooting\active\opencode-desktop-white-window-startup.md`
- `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\plan.md`
- `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\execution-log.md`

## Recommended Direction

Do not reinstall first. The evidence points to runtime config/plugin churn, especially Skillful discovery loops and noisy MCP startup calls. Reinstalling Desktop is unlikely to help if the same global config is loaded afterward.

Proceed in this order:

1. Validate that disabling MCPs removes the prompt-discovery errors.
2. Capture a clean log baseline.
3. Temporarily remove only `@zenobius/opencode-skillful` from the plugin array and restart Desktop.
4. Compare Desktop responsiveness and logs.
5. If Skillful is the slowdown source, decide between reconfiguration and temporary disablement.
6. Only consider reinstall if the slowdown remains after MCP and Skillful isolation.
