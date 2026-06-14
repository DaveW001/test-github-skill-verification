# Skillful Desktop Cache Patch Log

Status: active workaround
Owner context: Dave's Windows 11 OpenCode Desktop setup
Primary config: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

## Current Position

`@zenobius/opencode-skillful@1.2.5` is archived and still has a Node/Electron-incompatible bundle line:

```js
var __require = import.meta.require;
```

OpenCode Desktop can load Skillful from its own cache, not from the global npm install. The active Desktop cache bundle is:

```text
C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius\opencode-skillful@latest\node_modules\@zenobius\opencode-skillful\dist\index.js
```

The required local patch is:

```js
import { createRequire as __createRequire } from "module";
var __require = __createRequire(import.meta.url);
```

The bundle also contains Bun filesystem APIs that must be replaced for Node/Electron:

```text
Bun.file(...)
new Bun.Glob(...)
```

## Running Log

| Date | Event | Evidence | Result |
| --- | --- | --- | --- |
| 2026-05-26 | Root cause verified in npm package | `dist/index.js` used `import.meta.require`; package was Bun-targeted and archived | Local patch plan created under `.conductor\tracks\20260526-skillful-local-patch` |
| 2026-05-26 | Global npm install patched | `C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\@zenobius\opencode-skillful\dist\index.js` changed to `createRequire` | CLI and Desktop smoke tests passed at that time |
| 2026-05-31 | Desktop froze/crashed again after cache refresh | Desktop cache copy still had `var __require = import.meta.require;`; global copy was still patched | Confirmed Desktop was loading/redownloading an unpatched cache copy |
| 2026-05-31 | Desktop cache patched directly | Backup saved as `.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-cache-index.js.backup-20260531-1158`; `node import()` returned `NODE_IMPORT_OK` | Immediate Skillful crash vector fixed |
| 2026-05-31 | Skill architecture corrected | `.agents\skills` was a junction to `.opencode-lazy-vault`, causing native scan of lazy skills; changed to a real empty directory | Lazy vault restored to 60 non-native skills; native vault remains 7 skills; no native/lazy duplicate names |
| 2026-05-31 | Desktop retry produced zero-byte CLI logs but non-empty Desktop logs | `AppData\Roaming\ai.opencode.desktop\logs\20260531T164827\server.log` showed `Initialization failed: Bun is not defined`; `window.log` showed renderer hanging in `MessageTimeline.constructMessageRows` | Added second cache patch replacing `Bun.file` and `Bun.Glob` with Node `fs` traversal |
| 2026-05-31 | Skillful Windows config path corrected, first attempt | Skillful README says Windows global config is `%APPDATA%\opencode-skillful\config.json`; Desktop logs were falling back to default paths | Created `C:\Users\DaveWitkin\AppData\Roaming\opencode-skillful\config.json`, but later logs proved this is not the path the archived bundle actually searches |
| 2026-05-31 | Desktop resume state moved aside | `window.log` showed renderer unresponsive while constructing message rows; no OpenCode process was running during cleanup | Moved `opencode.workspace*.dat`, `window-state.json`, and `.window-state.json` from `AppData\Roaming\ai.opencode.desktop` to `.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-state-backup-20260531-1300` |
| 2026-05-31 | Skillful importable config added | Bundled `dist/index.js` searches `~\.config\opencode-skillful`, `~\.config`, and `~`; it dynamic-imports config files, so JSON config can be skipped/fail in Node/Electron | Created `C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs`; `opencode debug skill` no longer emits `No valid base paths` |
| 2026-05-31 | Skillful Windows config-import patch | Bundled config loader used `await import(configPath + cacheBuster)`, which can fail on Windows absolute paths in Node/Electron | Patched cache bundle to `await import(pathToFileURL(configPath).href + cacheBuster)` and added `import { pathToFileURL } from "url"` |
| 2026-05-31 | Desktop storage reset (renderer recovery) | `window.log` repeatedly stuck in `MessageTimeline.constructMessageRows`; startup remained unstable | Backed up and reset `Local Storage` and `Session Storage` to `.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-state-backup-20260531-1730` |
| 2026-05-31 | OpenCode DB rotation (renderer recovery) | `opencode.db` had grown to ~3.47 GB and renderer continued looping in `constructMessageRows` despite storage reset | Moved `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` to `.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-state-backup-20260531-1738\opencode.db` so Desktop can recreate a clean database |

## Reapply Command

Run this after OpenCode Desktop updates, plugin cache refreshes, or the `__require is not a function` error returns:

```powershell
powershell -ExecutionPolicy Bypass -File C:\development\opencode\scripts\Repair-SkillfulDesktopCache.ps1
```

Then verify:

```powershell
$target = "C:\Users\DaveWitkin\.cache\opencode\packages\@zenobius\opencode-skillful@latest\node_modules\@zenobius\opencode-skillful\dist\index.js"
Select-String -LiteralPath $target -Pattern "import\.meta\.require|createRequire|var __require"
node -e "import('file:///C:/Users/DaveWitkin/.cache/opencode/packages/@zenobius/opencode-skillful@latest/node_modules/@zenobius/opencode-skillful/dist/index.js').then(() => console.log('NODE_IMPORT_OK')).catch(e => { console.error(e); process.exit(1) })"
opencode debug config
```

Expected:

- No `import.meta.require` match.
- No `Bun.file` or `Bun.Glob` match.
- `createRequire` and `var __require = __createRequire(import.meta.url);` are present.
- Node import prints `NODE_IMPORT_OK`.
- `opencode debug config` completes.

Also verify the importable Windows Skillful config exists:

```powershell
Get-Content C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs
```

The archived plugin README documents `%APPDATA%\opencode-skillful\config.json`, and the repair script keeps that file populated as a reference copy. The active cached bundle's actual `bunfig` search path on Windows is `~\.config\opencode-skillful`, `~\.config`, then `~`.

## Cache Durability Assessment

This patch is not durable across cache refreshes. OpenCode Desktop may redownload unpinned plugin cache contents when:

- the Desktop app updates,
- plugin cache is cleared,
- the plugin is unpinned as `@zenobius/opencode-skillful` in `opencode.jsonc`,
- OpenCode decides to refresh `@latest` package cache state.

Because the upstream package is archived, there is no reliable upstream fix to wait for. The short-term control is to keep the repair script and run it after updates. The long-term control should be replacing Skillful with a maintained OpenCode-native lazy skill strategy or a local fork/package whose published artifact already contains the `createRequire` fix and removes the Bun filesystem APIs in `src/lib/SkillFs.ts`.

## Current Desktop Retry Finding

The `C:\Users\DaveWitkin\.local\share\opencode\log\2026-05-31T164723.log` and `2026-05-31T164829.log` files were zero bytes. The useful logs were the matching Desktop logs:

```text
C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\logs\20260531T164722\
C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\logs\20260531T164827\
```

Those logs showed:

- sidecar/server started,
- no `__require is not a function`,
- repeated Skillful `Bun is not defined`,
- renderer unresponsive in `MessageTimeline.constructMessageRows`.

Interpretation: the first patch removed the CommonJS loader crash but did not fully make the Bun-targeted bundle Node-compatible. If the renderer still hangs after the second patch, investigate stale session/message rendering state next.

Later `20260531T170054` logs showed no `__require` or `Bun is not defined`, but still showed Skillful using default base paths instead of the lazy vault:

```text
C:\Users\DaveWitkin\AppData\Local\opencode\skills
C:\Users\DaveWitkin\.config\opencode\skills
C:\Users\DaveWitkin\.opencode\skills
C:\development\opencode\.opencode\skills
```

Root cause: the README-documented `%APPDATA%` config was not read by this archived bundle, and the JSON config under `~\.config\opencode-skillful` was not reliably importable. The working config is now:

```text
C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs
```

Headless validation after that change: `opencode debug skill` completes without `OpencodeSkillful`, `No valid base paths`, `Bun is not defined`, `__require`, or duplicate skill warnings.

Follow-up cleanup already completed: with no OpenCode processes running, Desktop workspace/window resume state was moved to:

```text
C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-state-backup-20260531-1300
```

Only `opencode.workspace*.dat`, `window-state.json`, and `.window-state.json` files were moved. Auth, database, plugin cache, Local Storage, and Session Storage were left in place. If Desktop still hangs after the Skillful cache patch and window-state reset, the next state cleanup target is a backup-and-clear of Desktop `Local Storage` / `Session Storage`.

## Architecture Guardrails

Current intended state after the 2026-05-31 cleanup:

- Native skill directory: `C:\Users\DaveWitkin\.config\opencode\skill`
- Native skill count: 7
- Lazy vault: `C:\Users\DaveWitkin\.opencode-lazy-vault`
- Lazy skill count: 60
- Eager `.agents` scan path: `C:\Users\DaveWitkin\.agents\skills`
- `.agents\skills` must be a real empty directory, not a junction to the lazy vault.

Validation:

```powershell
(Get-Item -LiteralPath C:\Users\DaveWitkin\.agents\skills -Force).LinkType
@(Get-ChildItem -LiteralPath C:\Users\DaveWitkin\.agents\skills -Directory -Force).Count
@(Get-ChildItem -LiteralPath C:\Users\DaveWitkin\.opencode-lazy-vault -Directory -Force).Count
@(Get-ChildItem -LiteralPath C:\Users\DaveWitkin\.config\opencode\skill -Directory -Force).Count
```

Expected:

- blank `LinkType`
- `.agents\skills` count `0`
- lazy vault count around `60`
- native count around `7`

## Long-Term Research Prompt

Use this prompt when asking Gemini or another research system for a replacement strategy:

```text
I need a current, OpenCode-focused replacement strategy for @zenobius/opencode-skillful on Windows 11.

Context:
- Primary tool is OpenCode Desktop/CLI.
- Current workaround uses archived @zenobius/opencode-skillful@1.2.5.
- It crashes in OpenCode Desktop because its bundled dist/index.js uses Bun-only import.meta.require; we locally patch it to Node ESM createRequire(import.meta.url).
- OpenCode Desktop loads plugins from C:\Users\DaveWitkin\.cache\opencode\packages, so global npm patches are not enough.
- We have about 60 reusable skills and want them lazy-loaded, not injected into every prompt.
- Native OpenCode skills are useful, but putting all skills in native scanned directories creates unacceptable prompt/context overhead.
- Current intended architecture:
  - Native essentials: C:\Users\DaveWitkin\.config\opencode\skill
  - Lazy vault: C:\Users\DaveWitkin\.opencode-lazy-vault
  - .agents\skills must not point at the lazy vault.

Research goals:
1. Find maintained, open-source OpenCode-compatible approaches for lazy-loading many SKILL.md-style skills without upfront prompt bloat.
2. Verify whether OpenCode's current first-party skill system truly avoids full skill body injection, or only defers some content while still adding metadata/tool-description overhead.
3. Identify whether OpenCode supports local plugin paths or pinned local packages so we can run a patched/forked Skillful without Desktop redownloading the broken npm artifact.
4. Compare options:
   - keep local cache patch script,
   - fork @zenobius/opencode-skillful and publish/use a fixed package,
   - use a local OpenCode plugin path,
   - use native OpenCode skills with a minimized index,
   - use MCP or another gateway as a lazy skill registry.
5. For each option, provide exact Windows/OpenCode setup steps, durability across Desktop updates, rollback, and token/context impact.

Please prioritize primary sources: OpenCode docs, OpenCode GitHub issues/PRs/code, npm package READMEs, and active GitHub repositories. Exclude abandoned plugins unless they are only used as implementation references.
```
