# Context Pruning Add-In (DCP)

## Add-in name

- Package: `@tarquinen/opencode-dcp`
- Purpose: Dynamic context pruning support via `/dcp` in interactive OpenCode sessions.

## Where it is configured

- Active OpenCode user config: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- Installed in the `plugin` array as: `"@tarquinen/opencode-dcp@latest"`

## How we installed it (brief)

1. Confirmed install instructions from the project README.
2. Added `"@tarquinen/opencode-dcp@latest"` to the `plugin` list in the active user config file.
3. Verified plugin resolution with:

```bash
opencode debug config | rg "@tarquinen/opencode-dcp|plugin"
```

## How we tested it (brief)

Source repo used for validation:

- `C:\development\temp\opencode-dynamic-context-pruning`

Validation command run in that repo:

```bash
npm ci && npm run test && npm run build && npm run typecheck
```

Observed results:

- Dependencies installed cleanly
- Tests passed (`10 passed, 0 failed`)
- Build passed
- Typecheck passed

Note:

- `opencode run "/dcp"` returned `Session not found` in non-interactive mode; this is expected for that invocation style.
- Final smoke test should be done in an interactive session after restart by running `/dcp`.

## Incident history

This plugin has had two cache-corruption incidents, both resolved:

1. **2026-05-26** - `Cannot find module 'dist\lib\config'` (corrupted cache; cleared and reinstalled). See `docs\troubleshooting\active\plugin-status-and-remediation.md`.
2. **2026-06-28 .. 2026-06-30 (module-load outage)** - `Cannot find module '@anthropic-ai/tokenizer'`. The cached 3.1.13 install never hoisted the declared `@anthropic-ai/tokenizer@^0.0.4` dependency, so the plugin failed to load on every launch for ~2 days. Resolved by clean-installing **3.1.14** (which hoists the tokenizer correctly). See track `20260629-dcp-complete-outage-fix` (validated).
3. **2026-06-30 .. 2026-07-01 (runtime hooks not firing)** - After the 3.1.14 reinstall the plugin *loaded* but its hooks/tools never registered: zero compressions after 2026-06-25, no new prune-state files, and no genuine `permission=compress` evaluations. Root cause: runtime registration did not complete until DCP debug logging and a full OpenCode restart were performed. Resolved by enabling "debug": true in ~/.config/opencode/dcp.jsonc and restarting OpenCode (2026-07-01). Runtime restoration validated: genuine `permission=compress` at 2026-07-01T18:14:28Z, new prune-state ses_0e1ecc970ffe2fYOlczHfTfws4.json at 18:14:29Z, and end-to-end compression (one_time_saved=33080, compound_saved=66160). Note: 3.1.14 fixed only module loading, not runtime hook registration. See track `20260701-dcp-runtime-hooks-fix` (validated).

**Current state (2026-07-01):** loads cleanly AND runtime hooks fire on every launch; compression verified end-to-end post-restart.

## Where the supporting documentation is

- This file: `C:\development\opencode\docs\reference\context-pruning-addin.md`
- DCP runtime-hooks restoration track: `C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\` (validated 2026-07-01; validation report `validation-report-2026-07-01-143503.md`)
- Conductor track root: `C:\development\opencode\.conductor\tracks\20260314-dcp-install-validation`
- Conductor validation log: `C:\development\opencode\.conductor\tracks\20260314-dcp-install-validation\artifacts\validation-log.md`

## Do we need to keep the local cloned repo?

Short answer: **No, it is safe to delete** if you do not plan to modify or re-run plugin source tests right now.

Reason:

- OpenCode uses the configured plugin package (`@tarquinen/opencode-dcp@latest`) from config resolution, not the local clone in `C:\development\temp\opencode-dynamic-context-pruning`.

If you want to delete it now:

```bash
rm -rf "C:\development\temp\opencode-dynamic-context-pruning"
```
