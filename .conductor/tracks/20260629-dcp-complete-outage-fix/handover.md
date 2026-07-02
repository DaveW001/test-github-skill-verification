# Handover: DCP Loads But Does Not Function (Post-Fix Investigation)
> **RESOLVED 2026-07-01 (superseded).** The runtime-hook failure documented below has been fixed and validated in track `20260701-dcp-runtime-hooks-fix` (validation report `validation-report-2026-07-01-143503.md`). Resolution: enabled `"debug": true` in `~/.config/opencode/dcp.jsonc` and restarted OpenCode. Post-restart evidence: genuine `permission=compress` at `2026-07-01T18:14:28Z`, new prune-state `ses_0e1ecc970ffe2fYOlczHfTfws4.json` at `18:14:29Z`, end-to-end compression (`one_time_saved=33080`, `compound_saved=66160`). The proposed-fix options in this handover are now historical context; only the `dcp.jsonc` debug option (not the `opencode.jsonc` tuple) was needed. **Status below is the original 2026-07-01 investigation state, retained for the record.**


**Created:** 2026-07-01
**Session:** Follow-up investigation to the `20260629-dcp-complete-outage-fix` track
**Investigator:** 01-Planner (glm-5.1)
**Status:** Root cause identified; proposed fixes need validation and execution

---

## TL;DR

The DCP outage fix (completed 2026-06-30) successfully resolved the **load failure** (missing `@anthropic-ai/tokenizer`). However, a follow-up investigation on 2026-07-01 discovered that **DCP still does not actually function**. The plugin module loads without errors, but its hooks never fire -- zero compressions have occurred since 2026-06-25. **40 of 51 post-fix sessions (78%) met the DCP eligibility threshold but none triggered compression.** The fix track's validation (AC-2) only checked that the "loading plugin" log line appears without errors; it did not verify hook registration or runtime compression activity.

---

## Problem Statement

**DCP (Dynamic Context Pruning) loads cleanly but does not prune, compress, or inject nudges.** This means every opencode session runs at full context size with no token optimization, inflating costs and degrading retrieval quality on large sessions.

---

## Timeline

| Date | Event |
|---|---|
| Through 2026-06-25 | DCP functioning normally (last prune-state file written 06-25 18:41) |
| ~2026-06-28 | DCP breaks: `Cannot find module '@anthropic-ai/tokenizer'` error on every launch |
| 2026-06-30 12:40 | Fix applied: deleted stale 3.1.13 cache, recreated installer shim, clean `npm install` of 3.1.14 |
| 2026-06-30 12:52 | Fix validated: AC-2 confirmed "loading plugin" line present, no tokenizer error |
| 2026-06-30 to 2026-07-01 | **51 sessions ran; 0 triggered DCP compression** |
| 2026-07-01 | This investigation: discovered DCP loads but hooks never fire |

---

## Evidence Summary

### 1. DCP Plugin Loads Without Errors (CONFIRMED)

All 11 logs since the fix (2026-06-30 onward) show:
```
INFO  2026-07-01T13:00:03 +0ms service=plugin path=@tarquinen/opencode-dcp@latest loading plugin
```
Zero `failed to load plugin` or tokenizer errors. The fix track's AC-2 passes.

**Installed version:** 3.1.14 (confirmed at `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@tarquinen\opencode-dcp\package.json`)

**Tokenizer present:** `@anthropic-ai/tokenizer@0.0.4` confirmed at `...\node_modules\@anthropic-ai\tokenizer\package.json`

### 2. Zero Compression Activity Since 2026-06-25 (CONFIRMED)

**Prune-state files** (`C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp\ses_*.json`):
- Total files: 487
- **Newest file:** `ses_103d7d15fffeBleXZYaRYAZf5V.json` -- last modified **2026-06-25 18:41:00**
- No new files created since the fix (06-30) or since 06-25

**Report data** (`generate_report.py --sessions 150`):

| Metric | Value |
|---|---|
| Sessions analyzed | 150 |
| Sessions with DCP triggered | 30 (all before 06-25) |
| Sessions eligible but NO DCP | 96 |
| **Post-fix sessions (since 06-30 12:40)** | **51** |
| **Post-fix DCP triggers** | **0 (0.0%)** |
| **Post-fix eligible sessions (should have pruned)** | **40 of 51 (78%)** |

**Largest missed sessions** (all post-fix, all DCP=False):

| Session | Requests | Max Input | Total Tokens | Title |
|---|---|---|---|---|
| ses_0f0bab354... | 110 | 185,648 | 14,509,079 | Logic Review KG NotebookLM |
| ses_0eba5854... | 132 | 160,858 | 12,092,781 | HTML AI review playbook |
| ses_0e6661125... | 165 | 148,374 | 19,284,060 | Stage 2: Review plan (Conductor) |
| ses_0f0c4d690... | 78 | 116,223 | 8,195,212 | Agility data thought leadership |
| ses_0ebb7be0d... | 184 | 101,353 | 15,753,431 | Run govpulse-knowledge-graph |

### 3. No Compress Tool Registered (CONFIRMED via log comparison)

**Old log (06-13, when DCP worked)** -- `C:\Users\DaveWitkin\.local\share\opencode\log\opencode.log` (22MB):
```
level=INFO message=evaluated permission=compress pattern=* action.permission=compress action.action=allow
level=INFO message=found pruned=21252 total=55566
```
These lines appear dozens of times -- the compress tool was registered, permitted, and actively pruning.

**Recent logs (06-30 onward):** The word `compress` does not appear in ANY per-session log file since 06-30. This means:
- The compress tool was never registered (no permission evaluations)
- No compression was ever attempted
- DCP's `config` hook (which adds the compress tool and permission) did not run

### 4. DCP Log Directory Never Created (INDICATIVE)

DCP's Logger class writes to `~/.config/opencode/logs/dcp/`:
```javascript
// Line 4693 of dist/index.js
this.logDir = join3(configHome, "opencode", "logs", "dcp");
```

**This directory does not exist.** However, this is not fully conclusive because:
- DCP config defaults to `"debug": false`
- The Logger constructor takes an `enabled` flag from `config.debug`
- When `debug: false`, the logger may skip all writes including directory creation
- The `write()` method was not fully examined (output truncated)

**Interpretation:** The missing log dir is consistent with hooks never firing, but could also be explained by debug mode being off. It is supporting evidence, not primary evidence.

### 5. DCP Hooks Are the Right Hooks (CONFIRMED)

The `@opencode-ai/plugin` type definitions bundled with DCP 3.1.14 (at `...\node_modules\@opencode-ai\plugin\dist\index.d.ts`) define the `Hooks` interface, which includes:

```typescript
export interface Hooks {
    // ...
    "experimental.chat.messages.transform"?: (input: {}, output: {
        messages: { info: Message; parts: Part[]; }[];
    }) => Promise<void>;
    "experimental.chat.system.transform"?: (input: {
        sessionID?: string;
        model: Model;
    }, output: {
        system: string[];
    }) => Promise<void>;
    // ...
}
```

DCP 3.1.14's plugin factory (line 7925 of `dist/index.js`) returns these hooks:
```javascript
return {
    "experimental.chat.system.transform": createSystemPromptHandler(state, logger, config, prompts),
    "experimental.chat.messages.transform": createChatMessageTransformHandler(client, state, logger, config, prompts, hostPermissions),
    "experimental.text.complete": createTextCompleteHandler(),
    "command.execute.before": createCommandExecuteHandler(client, state, logger, config, ctx.directory, hostPermissions),
    event: createEventHandler(state, logger),
    tool: { ...config.compress.permission !== "deny" && { compress: ... } },
    config: async (opencodeConfig) => { ... },
};
```

The `experimental.chat.messages.transform` handler is the critical one -- it performs:
1. `checkSession()` -- session state initialization
2. `prune()` -- actual context pruning
3. `injectCompressNudges()` -- tells the model to compress when context is large
4. `assignMessageRefs()` -- message ID aliasing
5. Various other context management tasks

If this hook never fires, none of this work happens.

---

## Root Cause Analysis

### Primary Hypothesis: `server()` Factory Fails Silently

DCP's plugin entry point is a factory function (`server()`) that opencode calls during plugin initialization. This function:
1. Reads config from `dcp.jsonc` and opencode plugin options
2. Initializes state, logger, prompts
3. Returns the `Hooks` object

If this function **throws during steps 1-2**, the Hooks object is never returned, and opencode registers zero hooks. The plugin appears loaded (the "loading plugin" log line was already written before the factory call), but nothing actually works.

**Why no error in logs?** opencode may catch plugin initialization errors silently, or the error may not be logged at the per-session log level. The old opencode.log (22MB, from 06-13) uses a different log format (`timestamp=... level=INFO run=...`) and may have been the server-level log that would show such errors. The recent per-session logs may not capture plugin initialization errors.

### Supporting Evidence from GitHub Issues

Multiple GitHub issues describe the **identical symptom** (DCP shows "loading plugin" but hooks never register):

- **[Issue #511](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning/issues/511)**: "OpenCode Desktop Electron shows DCP installed but does not expose compress because 3.1.9 fails during server hook load." Root cause: extensionless ESM imports under Electron's Node runtime. Fixed in 3.1.10+ via tsup bundling.

- **[Issue #507](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning/issues/507)**: "npm 3.1.9 still ships extensionless ESM imports." The fix was tsup bundling (PR #499). Version 3.1.14 IS bundled (single 278KB `dist/index.js`), so this specific issue should be resolved.

- **[Issue #476](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning/issues/476)**: "Plugin fails to load in `opencode web` mode." Root cause: `jsonc-parser` CJS/ESM interop failure under Node.js strict ESM.

- **[Issue #30631](https://github.com/anomalyco/opencode/issues/30631)** (opencode repo): "Plugin `@latest` specifier gets permanently pinned to stale version." The wrapper `package.json` permanently pins the version. Manual shim recreation (as the fix track did) can introduce subtle resolution issues.

**Note:** 3.1.14 IS properly bundled with tsup (single `dist/index.js`, 278KB), so the extensionless-import issue from #511/#507 should be fixed. However, there may be a NEW failure mode in 3.1.14 on opencode 1.15.10.

### Secondary Hypothesis: Hooks Registered But Never Invoked

opencode 1.15.10 may have changed how it invokes `experimental.chat.messages.transform` and `experimental.chat.system.transform`. If the server stopped calling these hooks (renamed, removed, or changed invocation timing), DCP's hooks would be registered but never fire.

**Evidence for:** opencode Issue #30240 documents that v1.15.13 had bugs where the Desktop TUI didn't reflect plugin configuration, fixed in 1.17.0. The user is on 1.15.10.

**Evidence against:** The `@opencode-ai/plugin` type definitions bundled with DCP 3.1.14 still define these hooks. If opencode removed them, the types would likely be updated.

### Tertiary Hypothesis: Installer Shim Broke Module Resolution

The fix track manually recreated the `@latest` wrapper. The shim's `package.json` is:
```json
{
  "dependencies": {
    "@tarquinen/opencode-dcp": "3.1.14"
  }
}
```

This has no `main` field, no `dist/`, no `index.js`. However, this is the **same structure** as other working plugins (tokenscope uses the identical pattern), so this is likely opencode's standard resolution mechanism and not the problem.

---

## How the Fix Track's Validation Was Insufficient

The fix track's **AC-2** states:
> "Plugin loads on a fresh launch: the newest log contains a `service=plugin path=@tarquinen/opencode-dcp` line and NO `failed to load plugin` and NO `@anthropic-ai/tokenizer` error."

This validation only confirms the plugin **module** loads without errors. It does **not** verify:
1. That the `server()` factory function completed successfully
2. That the `Hooks` object was returned and registered with opencode
3. That the `compress` tool is exposed to sessions
4. That `experimental.chat.messages.transform` fires on chat messages
5. That prune-state files are created for eligible sessions
6. That the `config` hook ran (adding compress permission/tool to opencode config)

**Recommendation for future DCP validation:** Add acceptance criteria that verify runtime behavior, not just load success. See "Improved Acceptance Criteria" below.

---

## Troubleshooting Methodology (for Validation Review)

The investigation followed this evidence chain:

1. **Found the report tool** -- Located `docs/workflows/re-run-dcp-report.md` and `generate_report.py` in the `20260613-dcp-token-savings-analysis` track.

2. **Ran the report** -- `generate_report.py --sessions 150` with `--verify` self-checks passing.

3. **Parsed aggregate.json** -- Extracted session-by-session DCP trigger data.

4. **Cross-referenced with SQLite DB** -- Wrote a custom Python script querying `opencode.db` to get timestamps, request counts, and max input tokens for all post-fix sessions. Initial inline script had an SQL escaping bug (`\$` in Python `-c` strings mangled JSON path expressions); corrected by writing a proper `.py` file with raw string literals.

5. **Verified plugin load status** -- Searched all 11 post-fix logs: 11/11 show "loading plugin", 0/11 show errors.

6. **Checked prune-state files** -- Newest file is 2026-06-25; nothing since.

7. **Located and read the plugin source** -- Found DCP 3.1.14 at `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@tarquinen\opencode-dcp\dist\index.js` (278KB bundled).

8. **Analyzed hook registration** -- Searched the bundled source for hook patterns, found the plugin factory return at line 7925 with all hooks defined.

9. **Analyzed the message transform handler** -- Read `createChatMessageTransformHandler` (line 7494): this is the auto-trigger that does pruning, nudging, and context management.

10. **Compared old vs new logs** -- The 22MB `opencode.log` (06-13) shows `permission=compress ... allow` and `found pruned=21252`; recent logs show zero compress references.

11. **Checked DCP's own log directory** -- `~/.config/opencode/logs/dcp/` does not exist.

12. **Read the `@opencode-ai/plugin` type definitions** -- Confirmed both experimental hooks are defined in the interface.

13. **Researched known issues** -- Web search found GitHub Issues #511, #507, #476, #30631, and #30240 documenting identical symptoms and various root causes.

14. **Checked DCP config** -- The opencode config declares DCP as `"@tarquinen/opencode-dcp@latest"` (simple string, no options object). Defaults apply: `enabled: true`, `debug: false`, `autoUpdate: true`.

---

## Key Files and Paths

### Plugin Installation
- **Shim:** `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\package.json`
- **Real package:** `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@tarquinen\opencode-dcp\`
- **Bundled source:** `...\node_modules\@tarquinen\opencode-dcp\dist\index.js` (278,751 bytes, 8000+ lines)
- **Plugin type defs:** `...\node_modules\@opencode-ai\plugin\dist\index.d.ts`
- **Backup (pre-fix):** `C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest.bak-20260630-124022\`

### Data Sources
- **OpenCode DB:** `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` (4.1 GB, SQLite)
- **DCP prune state:** `C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp\ses_*.json` (487 files, newest 06-25)
- **Opencode logs:** `C:\Users\DaveWitkin\.local\share\opencode\log\` (per-session `*.log` files + 22MB `opencode.log` from 06-13)
- **DCP config:** `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc`
- **Opencode config:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` (plugin declared at line 7)

### Report Tool
- **Workflow doc:** `C:\development\opencode\docs\workflows\re-run-dcp-report.md`
- **Generator script:** `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\scripts\generate_report.py`
- **Report output:** `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\artifacts\dcp-savings-report.html`
- **Aggregate JSON:** `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\artifacts\aggregate.json`

### Track Artifacts (this investigation's parent track)
- **Spec:** `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\spec.md`
- **Plan:** `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\plan.md`
- **Validation report:** `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\validation-report-2026-06-30-125046.md`
- **Execution log:** `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\execution-log-2026-06-30.md`

### Version Info
- **opencode:** 1.15.10 (Desktop Electron app)
- **DCP plugin:** 3.1.14 (published 2026-06-25 on npm)
- **DCP SDK dep:** `@opencode-ai/sdk: ^1.4.3`
- **DCP tokenizer dep:** `@anthropic-ai/tokenizer: ^0.0.4` (installed: 0.0.4)
- **DCP config defaults:** `enabled: true`, `debug: false`, `autoUpdate: true`, `compress.permission` defaults to `"allow"`, `compress.maxContextLimit: 100000`, `compress.minContextLimit: 50000`, `compress.iterationNudgeThreshold: 15`

### DCP Source Code Key Locations (in bundled `dist/index.js`)
- **Line 7925:** Plugin factory return (all hooks registered here)
- **Line 7494:** `createChatMessageTransformHandler` -- the auto-trigger (prune, nudge, inject)
- **Line 7541:** `createCommandExecuteHandler` -- `/dcp` command handler
- **Line 7634:** `createTextCompleteHandler` -- strips hallucinations from output
- **Line 7639:** `createEventHandler` -- tracks compression timing
- **Line 4688:** `Logger` class -- writes to `~/.config/opencode/logs/dcp/`
- **Line 1338:** Default config values (`maxContextLimit: 1e5`, `minContextLimit: 5e4`, etc.)
- **Line 2824:** `STORAGE_DIR` -- prune-state file path (`~/.local/share/opencode/storage/plugin/dcp/`)

---

## Proposed Fixes (for Validation)

### Fix 1: Enable Debug Mode + Restart (Diagnostic)

Change the opencode config to pass debug options to DCP:

**File:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
**Current (line 7):** `"@tarquinen/opencode-dcp@latest",`
**Change to:**
```json
["@tarquinen/opencode-dcp@latest", {"debug": true}],
```

Then restart opencode and check:
- Does `~/.config/opencode/logs/dcp/` get created?
- Are there any initialization errors in the DCP log?
- Does the compress tool appear in sessions?

**Risk:** Low. Only enables debug logging. Does not change DCP behavior.
**Validates:** Whether the `server()` factory function completes and whether hooks fire.

### Fix 2: Clean Reinstall via opencode's Own Mechanism (Primary Fix)

Remove the manually-created shim and let opencode resolve the plugin fresh:

```powershell
# Remove the manually-recreated shim
Remove-Item -Recurse -Force "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"

# Let opencode re-resolve on next launch
# OR explicitly:
opencode plugin remove @tarquinen/opencode-dcp@latest
opencode plugin add @tarquinen/opencode-dcp@latest
```

Then restart opencode and verify:
- The `@latest` shim is recreated by opencode (not manually)
- The compress tool is registered (check logs for `permission=compress`)
- Prune-state files are created for eligible sessions

**Rationale:** The fix track manually recreated the installer shim. GitHub Issue #30631 documents that `@latest` resolution and shim creation is delicate. Letting opencode handle it natively may resolve subtle resolution issues.

**Risk:** Low-Medium. The backup still exists at `.bak-20260630-124022`.

### Fix 3: Upgrade opencode to 1.17.0+ (Environment Fix)

opencode Issue #30240 documents plugin loading/display bugs in 1.15.13, fixed in 1.17.0. The user is on 1.15.10.

```powershell
# Check current version
opencode version

# Upgrade (mechanism depends on install method)
# For Desktop: download from https://opencode.ai/downloads
# For CLI: winget upgrade opencode or equivalent
```

**Rationale:** If opencode 1.15.10 has a bug where `experimental.chat.messages.transform` is not invoked, upgrading would fix it.

**Risk:** Medium. May introduce other changes. The `20260628-opencode-session-message-seq-fatal` track is separately tracking a runtime issue.

**Note:** The original fix track's spec explicitly listed "Do NOT upgrade the opencode runtime (1.15.10 -> 1.17.x)" as a non-requirement. However, that constraint was scoped to the tokenizer fix only. With the new evidence that DCP hooks don't fire, an upgrade may be necessary.

### Fix 4: Pin Explicit Version Instead of @latest (Workaround)

Per GitHub Issue #30631, `@latest` can get permanently pinned to a stale version. Change to explicit version:

**File:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
**Current:** `"@tarquinen/opencode-dcp@latest",`
**Change to:** `"@tarquinen/opencode-dcp@3.1.14",`

**Rationale:** Forces opencode to resolve the exact version. May trigger a fresh resolution path that avoids the shim issue.

**Risk:** Low. Future DCP updates would require manual version bumps.

### Fix 5: Consider Sleev (Alternative)

DCP's npm page (as of 2026-06-25) states:
> "Development on DCP has slowed because most new context-management work has moved to Sleev and the sleev CLI. Sleev is a local proxy for Claude Code, Codex, and OpenCode that builds on DCP's core ideas with newer context-management features."

If DCP cannot be made to work on opencode 1.15.10, Sleev may be the better long-term path.

---

## Improved Acceptance Criteria (for Future DCP Validation)

Any future DCP fix should validate ALL of the following:

1. **AC-LOAD:** Plugin loads without errors (existing AC-2) -- `"loading plugin"` present, no `failed to load plugin`
2. **AC-CONFIG:** The `config` hook ran -- compress permission appears in session creation log (`permission=compress`) or the compress tool is listed in available tools
3. **AC-HOOK-RUNTIME:** The `experimental.chat.messages.transform` hook fires -- create a test session with >10K context and verify either:
   - A prune-state file (`ses_*.json`) is created in `~/.local/share/opencode/storage/plugin/dcp/`
   - OR DCP debug log (`~/.config/opencode/logs/dcp/`) shows hook activity
4. **AC-COMPRESSION:** After a session with >50K peak input and >15 requests, verify the report shows `has_dcp=True` for that session
5. **AC-COMMAND:** `/dcp help` is recognized as a valid command in an interactive session

---

## Session Notes

- **Tool layer:** Native file tools (Read, Write, Edit, glob, grep) return `Bun is not defined`. All file operations were performed via PowerShell through the `bash` tool.
- **Inline Python escaping:** When running Python via `python -c "..."` in PowerShell, `$.type` in SQL JSON path expressions gets mangled by `\$` escape handling. Use a `.py` file with raw strings instead.
- **Opencode API:** The server API was not accessible on common ports (4096, 3000, 8080, 8888, 1340). The Desktop Electron app likely uses a different mechanism. Could not query live tool registration.
- **Log formats:** The old `opencode.log` (22MB, from 06-13) uses `timestamp=... level=INFO run=... message=...` format. Recent per-session logs use `INFO 2026-07-01T13:00:03 +0ms service=...` format. These appear to be different log sinks.
- **Opencode version:** 1.15.10 confirmed from `2026-07-01T130002.log` line: `version=1.15.10`
- **Running opencode processes:** 7 `OpenCode.exe` processes were active during investigation (Electron multi-process architecture).