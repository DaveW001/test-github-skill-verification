# Plan

> **Scope:** DCP plugin ONLY. This plan does NOT upgrade the opencode runtime, touch the SQLite DB, change the scheduler, or edit `opencode.jsonc`. The separate `20260628-opencode-session-message-seq-fatal` track owns the runtime/seq fix.
>
> **Context-aware note (read first):** The fix steps (Phases 1-2) only edit files inside the opencode plugin cache directory - they are SAFE to run whether or not opencode is currently running, and SAFE to run from inside a live opencode session (unlike the seq-fatal track, which hard-aborts). The verification step (Phase 3) triggers a fresh opencode launch; that is fine to run from inside opencode (it spawns a short-lived child `opencode run` process).
>
> **Expected non-error to IGNORE:** After the fix, a fresh `opencode run` will STILL crash with `NOT NULL constraint failed: session_message.seq` (the separate seq bug, runtime 1.15.10). That error is OUT OF SCOPE. Phase 3 validation gates ONLY on the DCP plugin-load lines, NOT on exit code and NOT on the seq error.
>
> **Tool-layer note:** File tools (Read/Grep/Glob/Write) may return `Bun is not defined` in this session. Use PowerShell cmdlets (`Get-Content`, `Select-String`, `Get-ChildItem`, `Set-Content`, `ConvertFrom-Json`) via the `bash` tool instead. Do not retry the failing tool.

## Phase 0 - Setup & Preconditions
Objective: confirm the failure is present, confirm npm reachability + target version, and back up the current cache. No fix applied yet.

- [x] **0.1 Confirm the DCP failure is present in the most recent launch log.**
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  $newest = Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $hit = Select-String -Path $newest.FullName -Pattern "service=plugin path=@tarquinen/opencode-dcp" -SimpleMatch
  $err = Select-String -Path $newest.FullName -Pattern "Cannot find module '@anthropic-ai/tokenizer'" -SimpleMatch
  Write-Host "newest_log=$($newest.Name)"
  if ($hit) { $hit | Select-Object -First 1 Line } else { Write-Host "NO dcp plugin line found" }
  if ($err) { Write-Host "DCP_FAILURE_PRESENT" } else { Write-Host "no tokenizer error in newest log" }
  ```
  Expected: prints a `service=plugin path=@tarquinen/opencode-dcp@latest ... failed to load plugin` line and `DCP_FAILURE_PRESENT`. If neither appears, the failure may already be fixed or the newest log is from a non-launch event - still continue (Phase 1 will reveal current cache state). Error recovery: if `$newest` is null, run `Get-ChildItem $logDir -Filter '*.log'` to confirm logs exist.

- [x] **0.2 Confirm the tokenizer is currently MISSING from the cache (pre-fix evidence).**
  ```powershell
  $dir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  $tk  = "$dir\node_modules\@anthropic-ai\tokenizer\package.json"
  Write-Host "cache_exists=$(Test-Path $dir)"
  Write-Host "tokenizer_present=$(Test-Path $tk)"
  Get-Content "$dir\package.json" -Raw
  ```
  Expected: `cache_exists=True`, `tokenizer_present=False`, and the shim prints `{"dependencies":{"@tarquinen/opencode-dcp":"3.1.13"}}`. Save this output (it is the pre-fix baseline).

- [x] **0.3 Confirm npm reachability and the target version (BEFORE deleting anything).**
  ```powershell
  npm view @tarquinen/opencode-dcp version
  npm view @tarquinen/opencode-dcp@latest dependencies
  ```
  Expected: first command prints `3.1.14`; second prints a block that INCLUDES `'@anthropic-ai/tokenizer': '^0.0.4'`. Error recovery: if npm fails (EAI_AGAIN / proxy / 429), STOP - do not delete the cache. Retry after network is restored; the whole Phase 1 depends on being able to install from npm.

- [x] **0.4 Back up the current cache directory (reversibility).**
  ```powershell
  $ts  = Get-Date -Format 'yyyyMMdd-HHmmss'
  $dir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  $bak = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest.bak-$ts"
  Copy-Item -LiteralPath $dir -Destination $bak -Recurse -Force
  Test-Path $bak
  (Get-ChildItem $bak -Recurse -File | Measure-Object Length -Sum).Sum
  ```
  Expected: `True` and a non-zero byte total (typically tens of MB). If the byte total is 0, the copy failed - STOP and re-run before Phase 1.

**Phase 0 exit criteria:** DCP failure confirmed in a log (0.1) OR cache state confirmed broken (0.2); npm reachable and 3.1.14 confirmed with the tokenizer dep (0.3); full cache backup exists and is non-empty (0.4).

## Phase 1 - Primary Fix: clean re-resolve to 3.1.14 (durable)
Objective: replace the incomplete 3.1.13 cache install with a complete 3.1.14 install that includes `@anthropic-ai/tokenizer`.

- [x] **1.1 Delete the stale cache entry (the backup from 0.4 makes this reversible).**
  ```powershell
  $dir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  Remove-Item -LiteralPath $dir -Recurse -Force
  Test-Path $dir
  ```
  Expected: `False`. Error recovery: if "file in use" / access denied, another opencode process may be mid-load. Run `Get-Process opencode,bun,node -ErrorAction SilentlyContinue`; if you can safely stop a stray short-lived child `opencode run` (NOT your own host process - see context note), do so and retry. If you cannot, fall back to Phase 2 (manual install into the existing dir without deleting).

- [x] **1.2 Recreate the cache dir with a 3.1.14 shim (mirrors opencode's installer format; built via ConvertTo-Json to stay deterministic).**
  ```powershell
  $dir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  @{ dependencies = @{ '@tarquinen/opencode-dcp' = '3.1.14' } } | ConvertTo-Json |
      Set-Content -LiteralPath "$dir\package.json" -Encoding utf8
  Get-Content "$dir\package.json" -Raw
  ```
  Expected: prints JSON with a top-level `dependencies` object whose `@tarquinen/opencode-dcp` value is `3.1.14`.

- [x] **1.3 Install the plugin and ALL its dependencies (deterministic, complete).**
  ```powershell
  $dir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  npm install --prefix $dir
  "exit=$LASTEXITCODE"
  ```
  Expected: `exit=0`, npm prints `added N packages`, and creates `$dir\node_modules\@tarquinen\opencode-dcp\` (the real plugin) plus its hoisted deps. Error recovery: if `npm install` fails, retry once with `npm install --prefix $dir --no-audit --no-fund`. If it still fails, do NOT delete again - proceed to Phase 2 (manual tokenizer install into whatever currently exists).

- [x] **1.4 Verify the tokenizer AND the real plugin are now present (in-memory proof, before any relaunch).**
  ```powershell
  $dir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  $tk     = "$dir\node_modules\@anthropic-ai\tokenizer\package.json"
  $plugin = "$dir\node_modules\@tarquinen\opencode-dcp\package.json"
  Write-Host "tokenizer_present=$(Test-Path $tk)"
  Write-Host "plugin_present=$(Test-Path $plugin)"
  if (Test-Path $plugin) { (Get-Content $plugin -Raw | ConvertFrom-Json).version }
  ```
  Expected: `tokenizer_present=True`, `plugin_present=True`, and the plugin version prints `3.1.14`. **If tokenizer_present is False, go to Phase 2.** If both True, SKIP Phase 2 and go to Phase 3.

**Phase 1 exit criteria:** cache dir recreated; `npm install` exit 0; `@anthropic-ai/tokenizer` package.json AND the real `@tarquinen/opencode-dcp` package.json both present; plugin version = 3.1.14.

## Phase 2 - Fallback Fix: manually install the missing tokenizer (only if 1.4 tokenizer_present is False)
Objective: guarantee the import target exists even if the installer/NPM hoisting misbehaves.

- [x] **2.1 Manually install @anthropic-ai/tokenizer@0.0.4 into the cache's node_modules.** (SKIPPED - correctly bypassed: Task 1.4 reported tokenizer_present=True, so Phase 2 was not required.)
  ```powershell
  $dir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  npm install --prefix $dir @anthropic-ai/tokenizer@0.0.4
  "exit=$LASTEXITCODE"
  $tk = "$dir\node_modules\@anthropic-ai\tokenizer\package.json"
  Write-Host "tokenizer_present=$(Test-Path $tk)"
  if (Test-Path $tk) { (Get-Content $tk -Raw | ConvertFrom-Json).version }
  ```
  Expected: `exit=0`, `tokenizer_present=True`, version `0.0.4`. Error recovery: as a last resort (offline), copy `@anthropic-ai/tokenizer` from the April backup if present: `$alt = "C:\Users\DaveWitkin\.cache\opencode-cache-backup-20260428-094635\node_modules\@anthropic-ai\tokenizer"; Test-Path $alt` - if True, `Copy-Item -LiteralPath $alt -Destination "$dir\node_modules\@anthropic-ai\tokenizer" -Recurse -Force` and re-run the Test-Path check.

- [x] **2.2 Re-confirm the plugin resolves the import statically (line 1601).** (SKIPPED - correctly bypassed: Phase 2 not required; primary Phase 1 install hoisted the tokenizer.)
  ```powershell
  $idx = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@tarquinen\opencode-dcp\dist\index.js"
  Test-Path $idx
  Select-String -Path $idx -Pattern '@anthropic-ai/tokenizer' -SimpleMatch | Select-Object -First 1 LineNumber,Line
  ```
  Expected: `True` and the import line `import * as _anthropicTokenizer from "@anthropic-ai/tokenizer";` - proving the dep we just installed is the one the code imports.

**Phase 2 exit criteria:** `@anthropic-ai/tokenizer@0.0.4` package.json exists in the cache node_modules; the plugin's `dist/index.js` import line confirmed.

## Phase 3 - Verify DCP Loads on a Fresh Launch (behavioral proof)
Objective: prove opencode now loads the DCP plugin without the tokenizer error.

- [x] **3.1 Trigger a fresh opencode launch and capture its log.** The launch WILL still crash on the separate seq bug - that is expected and ignored.
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  & "C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1" run --title 'dcp-verify-0629' --agent general 'Reply with the single word PING and stop. Do not call any tools.' 2>&1 | Out-Null
  "run_exit=$LASTEXITCODE"
  $newest = Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  Write-Host "newest_log=$($newest.Name)"
  ```
  Expected: a new log file is created (name like `2026-06-29T<HHMMSS>.log`). `run_exit` may be non-zero (seq crash) - ignore it. Error recovery: if `opencode.ps1` is not at that path, locate with `(Get-Command opencode -ErrorAction SilentlyContinue).Source` and use the full path returned. If the agent is itself inside opencode and the nested run hangs, fall back to 3.1b.

- [x] **3.1b (fallback trigger) Use the next hourly scheduled-launch log instead of launching manually.** Only use this if 3.1 cannot run. The KB-ingest job launches opencode every hour on the hour and writes a `YYYY-MM-DDTHH0002.log`: (SKIPPED - correctly bypassed: Task 3.1 manual launch succeeded and produced a fresh post-fix log.)
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  ```
  Note in the execution log that verification used a scheduled-launch log instead of a manual run, and confirm that log's timestamp is AFTER the Phase 1 fix.

- [x] **3.2 Assert the DCP plugin loaded with NO tokenizer error in that log.** This is the core acceptance gate (AC-2).
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  $newest = Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $loadLine   = Select-String -Path $newest.FullName -Pattern 'service=plugin path=@tarquinen/opencode-dcp' -SimpleMatch
  $failLine   = Select-String -Path $newest.FullName -Pattern 'failed to load plugin' -SimpleMatch
  $tokMissing = Select-String -Path $newest.FullName -Pattern "Cannot find module '@anthropic-ai/tokenizer'" -SimpleMatch
  if (-not $loadLine) { throw "FAIL: no DCP plugin line in $($newest.Name) - launch may not have reached plugin load" }
  if ($failLine -or $tokMissing) { $failLine; $tokMissing; throw "FAIL: DCP still failing in $($newest.Name)" }
  "OK: DCP plugin loaded cleanly in $($newest.Name)" | Tee-Object -FilePath "$logDir\dcp-verify-0629.txt" -Append
  ```
  Expected: prints `OK: DCP plugin loaded cleanly in <file>` and appends to `dcp-verify-0629.txt`. If it throws, re-check Phase 1.4 / 2.1 (tokenizer present?) and that the newest log is actually from AFTER the fix.

- [x] **3.3 Confirm a DCP init/config line appears (plugin is active, not just loaded).**
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  $newest = Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  Select-String -Path $newest.FullName -Pattern 'dcp' -SimpleMatch | Select-Object -First 5 LineNumber,Line
  ```
  Expected: at least one `dcp`-mentioning line (e.g., a `service=dcp` init line, or the plugin registering). If DCP logs nothing beyond the load line, that is still acceptable as long as 3.2 passed (DCP is lazy and may not log until a compression event). Record what you see.

**Phase 3 exit criteria:** a fresh launch log exists post-fix; it contains a `service=plugin path=@tarquinen/opencode-dcp` line; it contains NO `failed to load plugin` and NO `Cannot find module '@anthropic-ai/tokenizer'`.

## Phase 4 - Validate dcp.jsonc Config Parses & Active Model Cap Resolves
Objective: confirm the user's DCP config is valid and the active model gets its cap (so pruning will actually engage at the right threshold).

- [x] **4.1 Parse dcp.jsonc with the plugin's own jsonc-parser (preferred) and assert the active model's cap.**
  ```powershell
  $cfg = "C:\Users\DaveWitkin\.config\opencode\dcp.jsonc"
  $parser = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\jsonc-parser"
  if (Test-Path "$parser\package.json") {
    node -e "const p=require(process.argv[1]);const fs=require('fs');const e=[];const r=p.parse(fs.readFileSync(process.argv[2],'utf8'),e,{allowTrailingComma:true});if(e.length){console.error('PARSE_ERRORS',JSON.stringify(e));process.exit(1)}console.log('maxContextLimit='+r.compress.maxContextLimit);console.log('minContextLimit='+r.compress.minContextLimit);console.log('glm52_cap='+r.compress.modelMaxLimits['zai-coding-plan/glm-5.2']);console.log('protectUserMessages='+r.compress.protectUserMessages)" "$parser" "$cfg"
  } else { Write-Host "jsonc-parser not found; use python fallback in 4.2"; node -v }
  ```
  Expected: prints `maxContextLimit=65%`, `minContextLimit=50000`, `glm52_cap=150000`, `protectUserMessages=true`, exit 0. Error recovery: if `node` is missing, use the python fallback in 4.2.

- [x] **4.2 Python fallback parse (strip // comments, then json.loads).** (SKIPPED - correctly bypassed: Task 4.1 succeeded via the plugin's own jsonc-parser with node exit=0.)
  ```powershell
  $cfg = "C:\Users\DaveWitkin\.config\opencode\dcp.jsonc"
  python -c @"
import json, re
src = open(r'$cfg', encoding='utf-8').read()
src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
src = re.sub(r'(?m)//.*$', '', src)
r = json.loads(src)
print('maxContextLimit=' + str(r['compress']['maxContextLimit']))
print('glm52_cap=' + str(r['compress']['modelMaxLimits']['zai-coding-plan/glm-5.2']))
print('OK')
"@
  ```
  Expected: same key assertions + `OK`. (Use this only if 4.1 cannot run.)

**Phase 4 exit criteria:** `dcp.jsonc` parses with zero errors; `maxContextLimit=65%`; active model `zai-coding-plan/glm-5.2` cap = `150000`.

## Final Phase - Validation & Handover
Objective: prove the outage is fixed end-to-end and close the track artifacts.

- [x] **5.1 Re-scan the most recent launch log ONE more time for the DCP error signatures and explicitly document that the seq error is expected/out-of-scope.**
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  $newest = Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $dcpErr = Select-String -Path $newest.FullName -Pattern "Cannot find module '@anthropic-ai/tokenizer'|failed to load plugin" -SimpleMatch
  $seqErr = Select-String -Path $newest.FullName -Pattern 'session_message\.seq' -SimpleMatch
  if ($dcpErr) { $dcpErr | Select-Object LineNumber,Line; throw "FAIL: DCP error still present" }
  "OK: zero DCP errors in $($newest.Name)"
  if ($seqErr) { "NOTE (expected, out of scope): session_message.seq error still present - tracked by 20260628-opencode-session-message-seq-fatal" }
  "OK: DCP outage fix validated" | Tee-Object -FilePath "$logDir\dcp-outage-fixed-0629.txt"
  ```
  Expected: `OK: zero DCP errors`, a NOTE about the seq error being expected, and `OK: DCP outage fix validated`.

- [x] **5.2 Update metadata.json to completed.**
  ```powershell
  $meta = "C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\metadata.json"
  $today = Get-Date -Format 'yyyy-MM-dd'
  $j = Get-Content $meta -Raw | ConvertFrom-Json
  $j.status = 'completed'; $j.completed = $today; $j.progress.percentage = 100
  $j | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $meta -Encoding utf8
  Get-Content $meta -Raw | Select-String '"status": "completed"','"percentage": 100'
  ```
  Expected: both patterns match.

- [x] **5.3 Add/refresh the row in tracks.md (idempotent upsert).**
  ```powershell
  $md = "C:\development\opencode\.conductor\tracks.md"
  $today = Get-Date -Format 'yyyy-MM-dd'
  $row = "| 20260629-dcp-complete-outage-fix | DCP Plugin Complete Outage Fix (missing @anthropic-ai/tokenizer) | complete | $today | C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix |"
  $lines = Get-Content $md
  $found = $false
  for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\|\s*20260629-dcp-complete-outage-fix\s*\|') { $lines[$i] = $row; $found = $true; break }
  }
  if (-not $found) {
    $idx = 0
    for ($j=0; $j -lt $lines.Count; $j++) { if ($lines[$j] -match '^\| 2026') { $idx = $j; break } }
    if ($idx -gt 0) { $lines = $lines[0..($idx-1)] + $row + $lines[$idx..($lines.Count-1)] }
    else { $lines = @(Get-Content $md -Raw) + $row }
  }
  $lines | Set-Content -LiteralPath $md -Encoding utf8
  Select-String -Path $md -Pattern '20260629-dcp-complete-outage-fix' -SimpleMatch
  ```
  Expected: the row is present and shows `complete`.

- [x] **5.4 Append a dated Execution Complete entry to execution-log.md.**
  ```powershell
  $log = "C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\execution-log.md"
  Add-Content -LiteralPath $log -Value @"

## $(Get-Date -Format 'yyyy-MM-dd') - Execution Complete (Build agent)

- Before: @tarquinen/opencode-dcp 3.1.13 cached, @anthropic-ai/tokenizer MISSING -> plugin failed to load every launch.
- After: 3.1.14 cleanly installed with tokenizer present (or tokenizer manually installed via Phase 2) -> plugin loads.
- Cache backup: <path from 0.4>
- Verification log: C:\Users\DaveWitkin\.local\share\opencode\log\dcp-verify-0629.txt
- Out of scope (still present, expected): session_message.seq FATAL - see track 20260628-opencode-session-message-seq-fatal.
- Deviations: <list any>
"@
  ```
  Expected: a new `## YYYY-MM-DD - Execution Complete (Build agent)` section appended.

- [x] **5.5 Cross-link from the separate seq-fatal track's spec.md so its Phase 4 (DCP) is not re-done.**
  ```powershell
  $other = "C:\development\opencode\.conductor\tracks\20260628-opencode-session-message-seq-fatal\spec.md"
  if (-not (Select-String -Path $other -Pattern '20260629-dcp-complete-outage-fix' -SimpleMatch -Quiet)) {
    Add-Content -LiteralPath $other -Value "`n## Resolved separately`nThe secondary DCP plugin `@anthropic-ai/tokenizer` load failure (Phase 4 of this track) was resolved by dedicated track `20260629-dcp-complete-outage-fix`. When executing THIS track, Phase 4 (DCP) can be treated as already-done.`n"
  }
  Select-String -Path $other -Pattern '20260629-dcp-complete-outage-fix' -SimpleMatch
  ```
  Expected: at least one match (cross-link in place).

**Final Phase exit criteria:** newest launch log has zero DCP errors; seq error documented as out-of-scope; metadata.json completed/100%; tracks.md row present as complete; execution-log has Execution Complete entry; seq-fatal track cross-linked.

---

## Execution Readiness Checklist (against the 8 standards)
1. Atomic tasks - each checkbox is one action; file edits and command runs are split. **PASS**
2. Exact file paths - every path is fully qualified. **PASS**
3. Explicit commands - every step has verbatim PowerShell. **PASS**
4. Clear ordering - Phase 0 (preconditions) -> 1 (primary fix) -> 2 (fallback, conditional) -> 3 (verify) -> 4 (config) -> Final (close). **PASS**
5. Verification per step - each task ends with an Expected block and a deterministic check. **PASS**
6. No assumed context - preflight discovers state; error recovery on every risky step. **PASS**
7. Concrete examples - inline JSON shim, inline expected output strings, expected log line shapes. **PASS**
8. Error recovery - npm failure, access-denied, nested-run hang, missing node, offline fallback all covered. **PASS**

## Top 3 Implementation Risks + Mitigations
1. **npm install reproduces the incomplete-hoist bug on 3.1.14 (tokenizer still missing).** Mitigation: Phase 1.4 gates on `tokenizer_present=True`; if False, Phase 2 manually installs `@anthropic-ai/tokenizer@0.0.4` into the cache node_modules, with an offline copy fallback from the April backup.
2. **Verifying via opencode run is confused by the unrelated seq FATAL crash (non-zero exit).** Mitigation: Phase 3 explicitly ignores `run_exit` and the seq error; it gates ONLY on the DCP plugin-load lines. Phase 5.1 documents the seq error as expected/out-of-scope.
3. **A future opencode re-resolve (cache clear / autoupdate) wipes a Phase-2 manual fix.** Mitigation: Phase 1 (clean 3.1.14 install) is the durable path whenever it succeeds; Phase 2 is only the fallback. The plugin's own manifest declares the tokenizer dep, so any future clean re-resolve will include it.

## First task the build agent should execute immediately
**Task 0.1** - confirm the DCP failure is present in the most recent launch log (the short PowerShell block in Phase 0.1). It is read-only, instant, and confirms we are fixing the right thing before any mutation.
