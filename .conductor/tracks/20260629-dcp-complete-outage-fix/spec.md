# Spec

## Goal
Restore the `@tarquinen/opencode-dcp` (Dynamic Context Pruning) plugin to a loading, functional state. It is currently failing to load on EVERY opencode launch (interactive TUI and every scheduled `opencode run` job), so token-aware context pruning has been completely offline since at least 2026-06-28.

## Incident Summary (live evidence, this machine, 2026-06-29)
- **Symptom:** Every opencode launch logs, at plugin-load time:
  `ERROR service=plugin path=@tarquinen/opencode-dcp@latest ... error=Cannot find module '@anthropic-ai/tokenizer' from '...\node_modules\@tarquinen\opencode-dcp\dist\index.js' failed to load plugin`
- **Live evidence:** `C:\Users\DaveWitkin\.local\share\opencode\log\2026-06-29T150002.log` (line: `ERROR 2026-06-29T15:00:03 ... service=plugin path=@tarquinen/opencode-dcp@latest ... error=Cannot find module '@anthropic-ai/tokenizer' ... failed to load plugin`). Identical error present in the 2026-06-28 logs.
- **User impact:** DCP does nothing - context pruning is off. Sessions grow to full context windows (esp. the 1M-window models), inflating token cost and degrading retrieval quality. The plugin's own `/dcp` panel and config (`~/.config/opencode/dcp.jsonc`) are inert.

## Root Cause (definitive, confirmed by direct inspection this session)
- The opencode plugin cache pins `@tarquinen/opencode-dcp` at **3.1.13**: `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\` whose top-level `package.json` is the installer shim `{"dependencies": {"@tarquinen/opencode-dcp": "3.1.13"}}`.
- The real plugin code lives nested at `node_modules\@tarquinen\opencode-dcp\dist\index.js` and at **line 1601** does: `import * as _anthropicTokenizer from "@anthropic-ai/tokenizer";`
- The plugin's own `package.json` (3.1.13) declares `"@anthropic-ai/tokenizer": "^0.0.4"` as a dependency - **but the package is absent from the cache's `node_modules`** (confirmed: `Test-Path ...\node_modules\@anthropic-ai\tokenizer` => False). The install was incomplete; npm never hoisted the tokenizer.
- At launch, the import throws -> opencode logs `failed to load plugin` -> DCP is dead for the whole process lifetime. This happens BEFORE any session runs and BEFORE `dcp.jsonc` is parsed, so the `dcp.jsonc` model caps are NOT the cause.

## Fix Strategy
1. **Primary (durable):** Replace the incomplete 3.1.13 cache install with a clean, complete **3.1.14** install (the newest stable; 3.2.x are all betas). 3.1.14 also declares `@anthropic-ai/tokenizer ^0.0.4` (confirmed via `npm view`), so a clean `npm install` hoists the tokenizer correctly.
2. **Fallback (if hoisting misbehaves on 3.1.14):** Manually `npm install @anthropic-ai/tokenizer@0.0.4 --prefix <cacheDir>` to place the missing dep exactly where the plugin's import resolves (the cache-root `node_modules`).
3. **Verify:** Trigger a fresh opencode launch and assert the newest log has NO `failed to load plugin` / `@anthropic-ai/tokenizer` line, and that the DCP plugin-load line IS present.

## Requirements
- [ ] Restore DCP to a loading state (tokenizer present in plugin `node_modules`; no `failed to load plugin` in a fresh launch log).
- [ ] Confirm DCP is functional (plugin-load line present; `dcp.jsonc` config parses; the active model gets its configured cap).
- [ ] All cache mutations are reversible and backed up (copy the current cache dir before deleting).
- [ ] Do NOT touch the opencode runtime, the SQLite DB, the scheduler, or `opencode.jsonc` plugin list. The separate `20260628-opencode-session-message-seq-fatal` track owns the runtime upgrade + seq FATAL; this track is DCP-only.

## Non-Requirements
- [ ] Do NOT upgrade the opencode runtime (1.15.10 -> 1.17.x). That is out of scope; see the seq-fatal track.
- [ ] Do NOT attempt to fix the `session_message.seq` FATAL. It will STILL appear in logs after this fix and is expected; it is tracked separately. Validation here must NOT key on the seq error.
- [ ] Do NOT change the `dcp.jsonc` model-cap entries (incl. the `go-dave/minimax-m3` / `go-tiberius/minimax-m3` keys, which are harmless extras per the config's own comments). Only validate they parse.
- [ ] Do NOT modify the plugin list in `opencode.jsonc`.

## Acceptance Criteria
- [ ] AC-1 - Tokenizer present: `Test-Path 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@anthropic-ai\tokenizer\package.json'` returns True.
- [ ] AC-2 - Plugin loads on a fresh launch: the newest log under `C:\Users\DaveWitkin\.local\share\opencode\log` contains a `service=plugin path=@tarquinen/opencode-dcp` line and NO `failed to load plugin` and NO `@anthropic-ai/tokenizer` error on the same launch.
- [ ] AC-3 - Backup of pre-fix cache exists: `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest.bak-<ts>` (or equivalent) with non-zero size.
- [ ] AC-4 - `dcp.jsonc` parses as valid JSONC (jsonc-parser / structural check passes) and the active model (`zai-coding-plan/glm-5.2`) resolves to its configured cap (150000).
- [ ] AC-5 - Track closed: `metadata.json` status=completed, percentage=100; `tracks.md` row=complete; `execution-log.md` has a dated "Execution Complete" entry.

## Evidence Sources
- Live failure log: `C:\Users\DaveWitkin\.local\share\opencode\log\2026-06-29T150002.log`
- DCP cache root: `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\`
- Real plugin manifest: `...\node_modules\@tarquinen\opencode-dcp\package.json` (version 3.1.13)
- DCP user config: `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc`
- Plugin declaration: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` -> `plugin: ["@tarquinen/opencode-dcp@latest", ...]`
- Related track (separate problem): `C:\development\opencode\.conductor\tracks\20260628-opencode-session-message-seq-fatal\`
