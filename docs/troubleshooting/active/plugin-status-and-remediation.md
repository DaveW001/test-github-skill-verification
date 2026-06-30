# Plugin Status & Remediation Record

**Last updated:** 2026-06-30
**Author:** build-agent (Conductor track `20260526-opencode-desktop-log-remediation`)

## Overview

This document records the status of OpenCode Desktop plugins, known issues, remediation actions taken, and rollback procedures. Use this when troubleshooting startup errors, plugin load failures, or excessive log noise.

## Plugin Inventory

| Plugin | Status | Errors | Action Taken | Reason |
|--------|--------|--------|--------------|--------|
| `@tarquinen/opencode-dcp` | Active | 0 (post-fix 2026-06-30) | Cache cleared & clean-installed 3.1.14 | Two incidents: (1) 2026-05-26 missing `dist\lib\config` -> cache purge; (2) 2026-06-28..30 `@anthropic-ai/tokenizer` missing -> clean 3.1.14 reinstall. See track `20260629-dcp-complete-outage-fix` |
| `@zenobius/opencode-skillful` | Active with local Desktop cache patch | Recurred 2026-05-31 | Patched Desktop cache bundle with `createRequire` and Node `fs` traversal; global npm patch alone was insufficient | Upstream Bun-targeted bundle bug; archived package |
| `opencode-mystatus` | Removed | ~~13~~ -> 0 | Disabled first, then removed from config, package.json, and cache | Upstream dependency bug (missing ``@opencode-ai/plugin/dist/tool``); fully removed on 2026-05-26 |
| Slack MCP | Benign | 8 | None | `prompts not supported` is expected for Slack's MCP implementation |

## Detailed Plugin Notes

### `@zenobius/opencode-skillful` (ACTIVE WITH LOCAL PATCH)

**What it does:** Provides `skill_find`, `skill_use`, `skill_resource` tools for lazy-loaded skill discovery from `~/.agents/skills/` and `~/.config/opencode/skill/`.

**Error:** `__require is not a function` at `dist/index.js`

**Root cause:** The package uses CommonJS `__require` (likely from a bundler like esbuild) in an ESM module context. This is an upstream packaging bug in `@zenobius/opencode-skillful` v1.2.5.

**Current fix:** Patch the OpenCode Desktop cache bundle, not only the global npm install:

```text
C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius\opencode-skillful@latest\node_modules\@zenobius\opencode-skillful\dist\index.js
```

Replace `var __require = import.meta.require;` with the Node ESM `createRequire(import.meta.url)` polyfill, and replace `Bun.file` / `Bun.Glob` filesystem calls with Node `fs` traversal. The repo script is:

```powershell
powershell -ExecutionPolicy Bypass -File C:\development\opencode\scripts\Repair-SkillfulDesktopCache.ps1
```

**Durability:** This is a cache patch and can be overwritten by OpenCode Desktop updates, plugin cache refreshes, or package redownloads. Treat it as a short-term workaround. See `C:\development\opencode\docs\troubleshooting\active\skillful-desktop-cache-patch-log.md`.



### `opencode-mystatus` (REMOVED)

**What it does:** Provides the `/mystatus` slash command for checking AI quota, account status, and usage limits.

**Error:** `Cannot find module '@opencode-ai/plugin/dist/tool'`

**Root cause:** The package has a broken dependency resolution -- `@opencode-ai/plugin/dist/tool` is missing from the installed dependency tree. This is an upstream packaging bug.

**Impact of removal:** The `/mystatus` command is gone. Use the `codex-limits` or `codex-status` tools as alternatives for checking quota/usage.

**How to restore:** Re-add `"opencode-mystatus"` to the `plugin` array in `opencode.jsonc`, restore the `mystatus` command block if desired, and add `"opencode-mystatus": "^1.2.2"` to `package.json`, then run `bun install`.



### `@tarquinen/opencode-dcp` (ACTIVE)

**What it does:** Dynamic Context Pruning (DCP) plugin. Provides token-aware context pruning via `/dcp` in interactive sessions; reads `~/.config/opencode/dcp.jsonc` for per-model context caps.

**Incident history (two cache-corruption events):**

1. **2026-05-26** - `Cannot find module 'dist\lib\config'`. Cache was corrupted; cleared the cache directory and Desktop redownloaded a clean copy on restart. Resolved.
2. **2026-06-28 .. 2026-06-30 (complete outage)** - `Cannot find module '@anthropic-ai/tokenizer'`. The cached `@tarquinen/opencode-dcp` **3.1.13** install never hoisted the declared transitive dependency `@anthropic-ai/tokenizer@^0.0.4` into `node_modules`, so the plugin failed to load on EVERY launch (interactive TUI and every scheduled `opencode run` job). Token-aware pruning was fully offline for ~2 days.

   **Root cause:** incomplete npm hoist on the 3.1.13 install; the package was declared in the plugin's `package.json` but never materialized in the cache `node_modules`.
   **Durable fix (2026-06-30):** cleared the stale 3.1.13 cache, recreated the installer shim pinning **3.1.14**, and ran a clean `npm install` which hoisted `@anthropic-ai/tokenizer@0.0.4` correctly. Verified DCP loads cleanly in launch log `2026-06-30T164204.log` (1 load line, 0 failures, 0 tokenizer-missing errors).
   **Fallback (not needed):** manually `npm install @anthropic-ai/tokenizer@0.0.4 --prefix <cacheDir>`.
   **Track:** `20260629-dcp-complete-outage-fix` (validated, Ready to close). Pre-fix cache backup: `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest.bak-20260630-124022\`.

**Current state:** Active, loads without errors on every launch (verified 2026-06-30).

## Cache Location

Plugin cache directories are stored at:
```
C:\Users\DaveWitkin\.cache\opencode\packages\
```

Each plugin has its own subdirectory (e.g., `@zenobius/opencode-skillful@latest/`).

## Backup Locations

All plugin cache backups are stored in the Conductor track artifacts:
```
C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\20260526-110855\
```

Backup directories:
- `@zenobius-backup/` (original, from Session 1)
- `zenobius-opencode-skillful-backup-20260526/` (from Session 2, disabled)
- `opencode-mystatus@latest-backup/` (original, from Session 1)
- `opencode-mystatus@latest-backup-20260526/` (from Session 2, disabled)
- `@tarquinen-backup/` (original, from Session 1 -- now resolved)

## Rollback Procedures

### Restore a removed or disabled plugin from backup
```powershell
$cacheBase = "C:\Users\DaveWitkin\.cache\opencode\packages"
$backupBase = "C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\20260526-110855"

# Restore @zenobius/opencode-skillful
Copy-Item -LiteralPath "$backupBase\zenobius-opencode-skillful-backup-20260526" -Destination "$cacheBase\@zenobius\opencode-skillful@latest" -Recurse -Force

# Restore opencode-mystatus
Copy-Item -LiteralPath "$backupBase\opencode-mystatus@latest-backup-20260526" -Destination "$cacheBase\opencode-mystatus@latest" -Recurse -Force
```

### Clear all plugin caches (nuclear option)
```powershell
Remove-Item -LiteralPath "C:\Users\DaveWitkin\.cache\opencode\packages\*" -Recurse -Force
# Desktop will redownload all plugins on next restart
```

## Troubleshooting Quick Reference

### Symptom: `__require is not a function`
- **Plugin:** `@zenobius/opencode-skillful`
- **Cause:** Upstream ESM/CJS bundling bug
- **Fix:** Run `C:\development\opencode\scripts\Repair-SkillfulDesktopCache.ps1`, then restart OpenCode Desktop. If the app must be opened immediately, temporarily remove `@zenobius/opencode-skillful` from `opencode.jsonc`, but that is not the preferred steady state.

### Symptom: `Cannot find module '@opencode-ai/plugin/dist/tool'`
- **Plugin:** `opencode-mystatus`
- **Cause:** Upstream dependency resolution bug
- **Fix:** Remove the plugin from config and package dependencies, clear its cache, and use `codex-limits` / `codex-status` instead.

### Symptom: `Cannot find module 'dist\lib\config'`
- **Plugin:** `@tarquinen/opencode-dcp`
- **Cause:** Corrupted cache (2026-05-26 incident)
- **Fix:** Clear cache and restart Desktop

### Symptom: `Cannot find module '@anthropic-ai/tokenizer'`
- **Plugin:** `@tarquinen/opencode-dcp`
- **Cause:** Incomplete npm hoist of the declared transitive dep `@anthropic-ai/tokenizer@^0.0.4` on the cached 3.1.13 install (2026-06-28..30 outage).
- **Fix (durable):** Delete `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest`, recreate the installer shim pinning 3.1.14, and `npm install --prefix <dir>`. The 3.1.14 manifest declares the tokenizer and hoists it cleanly.
- **Fix (fallback):** `npm install --prefix <dir> @anthropic-ai/tokenizer@0.0.4` directly into the cache node_modules.
- **Track:** `20260629-dcp-complete-outage-fix`.

### Symptom: `prompts not supported` from Slack MCP
- **Plugin:** Slack MCP server
- **Cause:** Expected -- Slack's MCP doesn't support prompts
- **Fix:** None needed. This is benign.

## Change Log

| Date | Action | Detail |
|------|--------|--------|
| 2026-05-26 | Cache cleared | `@tarquinen/opencode-dcp` -- resolved missing module error |
| 2026-05-26 | Cache cleared + disabled | `@zenobius/opencode-skillful` -- upstream ESM bug, 21 errors eliminated |
| 2026-05-31 | Desktop cache patched | `@zenobius/opencode-skillful` -- global npm patch was not enough; Desktop cache still had `import.meta.require` |
| 2026-05-31 | Skill roots cleaned | `.agents\skills` changed from lazy-vault junction to real empty directory; lazy vault restored to 60 non-native skills; native vault remains 7 skills |
| 2026-05-31 | Desktop cache patch expanded | `@zenobius/opencode-skillful` -- Desktop logs then showed `Bun is not defined`; patched remaining `Bun.file` and `Bun.Glob` calls |
| 2026-05-31 | Skillful Windows config corrected | Created `C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs` after bundled code inspection showed the archived plugin searches `~\.config\opencode-skillful`, not `%APPDATA%`; kept `%APPDATA%\opencode-skillful\config.json` only as a README-documented reference copy |
| 2026-05-26 | Cache cleared + disabled | `opencode-mystatus` -- temporary mitigation before full removal |
| 2026-05-26 | Fully removed from config | `opencode-mystatus` -- removed from opencode.jsonc, package.json, AGENTS.md, node_modules, and cache |
| 2026-05-26 | Documented | Created this plugin status record |
| 2026-06-30 | Cache cleared & clean-installed 3.1.14 | `@tarquinen/opencode-dcp` -- resolved `@anthropic-ai/tokenizer` complete outage (2026-06-28..30). Cleared stale 3.1.13 cache, recreated 3.1.14 shim, clean `npm install` hoisted `@anthropic-ai/tokenizer@0.0.4`. Verified loads cleanly in `2026-06-30T164204.log`. Track `20260629-dcp-complete-outage-fix` |
| 2026-06-30 | Documented | Updated this record with the tokenizer-outage incident history, Quick Reference symptom, and cross-link to `20260629-dcp-complete-outage-fix` |

## Chronology Note

`opencode-mystatus` went through two states on 2026-05-26:

1. It was initially disabled as a startup-error mitigation while validating the upstream packaging bug.
2. It was later fully removed from the active OpenCode config and local package state so Desktop would stop redownloading and attempting to load it.

## Related Documents

- Conductor track: `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\`
- Execution log: `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\execution-log-2026-05-26.md`
- `/mystatus` reference: `C:\development\opencode\docs\reference\mystatus-quota-check.md`
- Skillful cache patch log: `C:\development\opencode\docs\troubleshooting\active\skillful-desktop-cache-patch-log.md`
- DCP tokenizer outage track: `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\` (validated 2026-06-30; validation report `validation-report-2026-06-30-125046.md`)
- DCP install validation (original): `C:\development\opencode\.conductor\tracks\20260314-dcp-install-validation\`
