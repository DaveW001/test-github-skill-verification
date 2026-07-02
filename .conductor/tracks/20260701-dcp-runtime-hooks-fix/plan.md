# Plan: DCP runtime hook failure follow-up

Track ID: `20260701-dcp-runtime-hooks-fix`

## Restatement before tasks

- **Goal/outcome:** Restore DCP runtime behavior and prove hooks/tools/compression activity, not merely plugin module loading.
- **Constraints/non-goals:** Use PowerShell-first fallback because native file tools returned `Bun is not defined`; protect secrets in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`; do not make destructive process/package/config changes without backups and, for process restarts, user approval; do not treat repo code as the default root cause.
- **Definition of done:** Runtime checks show DCP config/tool registration (`permission=compress` or compress tool), DCP debug logs or prune-state creation, `/dcp` command availability, and `has_dcp=True` for an eligible session if a live eligible session can be generated; all config/cache changes are backed up and rollback instructions are documented.

## Phase 0 Setup & Preconditions

### Objective
Establish safe execution conditions, collect baseline evidence, and create backups before any change.

### Checklist

- [x] **Task 0.1 - Confirm shell-first mode and required paths exist.**
  - Action: Run this command from `C:\development\opencode`:
    ```powershell
    $paths = @(
      'C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\handover.md',
      'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc',
      'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc',
      'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest',
      'C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp',
      'C:\Users\DaveWitkin\.local\share\opencode\log'
    )
    $paths | ForEach-Object { [pscustomobject]@{ Path = $_; Exists = Test-Path -LiteralPath $_ } } | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check:
    ```powershell
    $required = @(
      'C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\handover.md',
      'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc',
      'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest'
    )
    @($required | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -eq 0
    ```
    Expected output: `True`.
  - Diagnostic checks: If `dcp.jsonc` is missing, note that Task 3.1 will create it from a minimal template after backing up the config directory.
  - Error recovery: If the package path is missing, skip factory smoke tests that depend on it and proceed to native re-resolve diagnostics in Phase 3.

- [x] **Task 0.2 - Create timestamped backups for DCP config and package cache metadata.**
  - Action: Run this command:
    ```powershell
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backupRoot = 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\backups'
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    if (Test-Path -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc') { Copy-Item -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc' -Destination (Join-Path $backupRoot "dcp.jsonc.$ts.bak") }
    if (Test-Path -LiteralPath 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\package.json') { Copy-Item -LiteralPath 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\package.json' -Destination (Join-Path $backupRoot "opencode-dcp-latest-package.json.$ts.bak") }
    Get-ChildItem -LiteralPath $backupRoot | Select-Object Name,Length | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check:
    ```powershell
    $backupRoot = 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\backups'
    (Test-Path -LiteralPath $backupRoot) -and (@(Get-ChildItem -LiteralPath $backupRoot -Filter 'opencode-dcp-latest-package.json.*.bak').Count -ge 1)
    ```
    Expected output: `True`.
  - Diagnostic checks: List backup names with `Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\backups'`.
  - Error recovery: If copying fails due to permissions, stop and ask the user before proceeding.

- [x] **Task 0.3 - Detect running OpenCode processes and stop before restart-dependent steps if approval is needed.**
  - Action: Run this command:
    ```powershell
    Get-Process -Name 'OpenCode','opencode' -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,MainWindowTitle,Path | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check:
    ```powershell
    $p = @(Get-Process -Name 'OpenCode','opencode' -ErrorAction SilentlyContinue)
    if ($p.Count -gt 0) { 'APPROVAL_REQUIRED_BEFORE_RESTART_OR_KILL' } else { 'NO_RUNNING_OPENCODE_PROCESS_DETECTED' }
    ```
    Expected output: either `APPROVAL_REQUIRED_BEFORE_RESTART_OR_KILL` or `NO_RUNNING_OPENCODE_PROCESS_DETECTED`.
  - Diagnostic checks: Record process IDs in the execution log, but do not terminate them in this task.
  - Error recovery: If processes exist and the user has not approved restart/close, stop before any task that requires restart, cache deletion, or upgrade.

### Exit criteria
Required paths are classified, backups exist, and process restart safety is known.

## Phase 1 Low-risk diagnostics

### Objective
Determine whether DCP hook/tool registration is absent before making changes.

### Checklist

- [x] **Task 1.1 - Baseline scan for recent plugin load and compress registration.**
  - Action: Run this command:
    ```powershell
    $logDir = 'C:\Users\DaveWitkin\.local\share\opencode\log'
    $since = (Get-Date).AddDays(-3)
    $logs = Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Where-Object { $_.LastWriteTime -ge $since }
    $summary = [pscustomobject]@{
      RecentLogCount = @($logs).Count
      PluginLoadLines = @($logs | Select-String -SimpleMatch '@tarquinen/opencode-dcp' -ErrorAction SilentlyContinue).Count
      FailedPluginLines = @($logs | Select-String -SimpleMatch 'failed to load plugin' -ErrorAction SilentlyContinue).Count
      CompressLines = @($logs | Select-String -SimpleMatch 'permission=compress' -ErrorAction SilentlyContinue).Count
    }
    $summary | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check:
    ```powershell
    $logDir = 'C:\Users\DaveWitkin\.local\share\opencode\log'
    $since = (Get-Date).AddDays(-3)
    $logs = Get-ChildItem -LiteralPath $logDir -Filter '*.log' | Where-Object { $_.LastWriteTime -ge $since }
    $load = @($logs | Select-String -SimpleMatch '@tarquinen/opencode-dcp' -ErrorAction SilentlyContinue).Count
    $compress = @($logs | Select-String -SimpleMatch 'permission=compress' -ErrorAction SilentlyContinue).Count
    [pscustomobject]@{ PluginLoadLines = $load; CompressPermissionLines = $compress } | ConvertTo-Json -Compress
    ```
    Expected output: JSON with numeric `PluginLoadLines` and `CompressPermissionLines`; `CompressPermissionLines` greater than `0` means config hook registration is already observable.
  - Diagnostic checks: Also search for `/dcp` and `tool=compress` if the primary scan is inconclusive.
  - Error recovery: If logs are unavailable, continue with direct factory smoke test and runtime tests.

- [x] **Task 1.2 - Check latest DCP prune-state timestamp.**
  - Action: Run this command:
    ```powershell
    $stateDir = 'C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp'
    Get-ChildItem -LiteralPath $stateDir -Filter 'ses_*.json' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name,LastWriteTime,Length | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check:
    ```powershell
    $stateDir = 'C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp'
    $newest = Get-ChildItem -LiteralPath $stateDir -Filter 'ses_*.json' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $newest) { 'NO_PRUNE_STATE_FILES' } else { $newest.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss') }
    ```
    Expected output: a timestamp string or `NO_PRUNE_STATE_FILES`.
  - Diagnostic checks: Compare the timestamp to the current date and to the previous handover's newest timestamp `2026-06-25 18:41:00`.
  - Error recovery: If the directory does not exist, record `NO_PRUNE_STATE_FILES` and continue.

### Exit criteria
The executor has a current baseline for plugin load lines, compress registration lines, and prune-state freshness.

## Phase 2 Direct plugin factory smoke test

### Objective
Test whether DCP 3.1.14 can construct its hook object directly, without relying on OpenCode launch logs.

### Checklist

- [x] **Task 2.1 - Create and run a temporary ESM smoke test that imports DCP and calls its server factory if exported.**
  - Action: Run this command from `C:\development\opencode`:
    ```powershell
    $script = 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\smoke-dcp-factory.mjs'
    @'
import { pathToFileURL } from 'node:url';
const pkgPath = 'C:/Users/DaveWitkin/.cache/opencode/packages/@tarquinen/opencode-dcp@latest/node_modules/@tarquinen/opencode-dcp/dist/index.js';
try {
  // Use pathToFileURL so Node ESM accepts the absolute Windows path
  const mod = await import(pathToFileURL(pkgPath).href);
  const factory = mod.default ?? mod.server ?? mod.plugin ?? mod;
  const ctx = { directory: 'C:/development/opencode' };
  let result = null;
  let factoryCalled = false;
  let factoryError = null;
  if (typeof factory === 'function') {
    factoryCalled = true;
    try { result = await factory(ctx); } catch (e) { factoryError = String((e && e.message) || e); }
  } else {
    result = factory;
  }
  const keys = result && typeof result === 'object' ? Object.keys(result).sort() : [];
  console.log(JSON.stringify({
    ok: true,
    exportKeys: Object.keys(mod).sort(),
    factoryCalled,
    factoryError,
    hookKeys: keys,
    hasConfig: keys.includes('config'),
    hasTool: keys.includes('tool'),
    hasCommandBefore: keys.includes('command.execute.before'),
    hasMessagesTransform: keys.includes('experimental.chat.messages.transform')
  }));
} catch (e) {
  console.log(JSON.stringify({ ok: false, error: String((e && e.message) || e) }));
}
'@ | Set-Content -LiteralPath $script -Encoding utf8
    node $script
    ```
  - Authoritative acceptance check:
    ```powershell
    $script = 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\smoke-dcp-factory.mjs'
    $json = node $script | ConvertFrom-Json
    ($json.ok -eq $true) -and ($json.factoryCalled -eq $true)
    ```
    Expected output: `True`.
  - Diagnostic checks: If `ok` is false, inspect `error` for the import failure (path encoding, missing file, syntax). If `factoryCalled` is false, the package does not export a default/callable factory - the runtime test (Task 3.2) is the only proof. If `factoryError` is non-null, the factory needs the live opencode ctx (e.g. `_client`); record the error and rely on Task 3.2 for hook-construction evidence.
  - Error recovery: If import fails because the package path is absent, go to Phase 3 native re-resolve. If factory throws due to DCP config syntax, restore the latest `dcp.jsonc.*.bak` and retry once.

### Exit criteria
The executor knows whether the bundled DCP package can produce hooks under direct Node execution.

## Phase 3 Enable DCP debug through dcp.jsonc and restart safely

### Objective
Get DCP's own diagnostic logs without relying on unverified OpenCode plugin tuple option syntax.

### Checklist

- [x] **Task 3.1 - Enable `debug: true` in `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc` with backup preservation.**
  - Action: Run this command:
    ```powershell
    $path = 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc'
    $dir = Split-Path -Parent $path
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    if (Test-Path -LiteralPath $path) { Copy-Item -LiteralPath $path -Destination "$path.$ts.bak" }
    if (Test-Path -LiteralPath $path) { $content = Get-Content -Raw -LiteralPath $path } else { $content = "{`n}`n" }
    if ($content.Contains('"debug"')) {
      $content = [regex]::Replace($content, '"debug"\s*:\s*(true|false)', '"debug": true', 1)
    } else {
      $content = [regex]::Replace($content.Trim(), '^\{', "{`n  \"debug\": true,", 1)
    }
    Set-Content -LiteralPath $path -Value $content -Encoding utf8
    Get-Content -Raw -LiteralPath $path
    ```
  - Authoritative acceptance check:
    ```powershell
    $content = Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc'
    $content.Contains('"debug": true')
    ```
    Expected output: `True`.
  - Diagnostic checks: Do not inspect or print `opencode.jsonc` secrets. Only note whether DCP is present in the plugin list if needed with a redacted targeted match.
  - Error recovery: Restore with `Copy-Item -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc.<timestamp>.bak' -Destination 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc' -Force` if syntax appears broken.

- [x] **Task 3.2 - Restart OpenCode only after user approval, then verify DCP debug/runtime registration.**
  - Action: If Task 0.3 reported running processes, ask the user to close/restart OpenCode or explicitly approve termination. After restart, run:
    ```powershell
    $dcpLogDir = 'C:\Users\DaveWitkin\.config\opencode\logs\dcp'
    $opencodeLogDir = 'C:\Users\DaveWitkin\.local\share\opencode\log'
    [pscustomobject]@{
      DcpLogDirExists = Test-Path -LiteralPath $dcpLogDir
      DcpLogFiles = if (Test-Path -LiteralPath $dcpLogDir) { @(Get-ChildItem -LiteralPath $dcpLogDir -File).Count } else { 0 }
      CompressPermissionLines = @(Get-ChildItem -LiteralPath $opencodeLogDir -Filter '*.log' | Where-Object { $_.LastWriteTime -ge (Get-Date).AddHours(-6) } | Select-String -SimpleMatch 'permission=compress' -ErrorAction SilentlyContinue).Count
    } | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check:
    ```powershell
    $dcpLogDir = 'C:\Users\DaveWitkin\.config\opencode\logs\dcp'
    $opencodeLogDir = 'C:\Users\DaveWitkin\.local\share\opencode\log'
    $hasDcpLogs = (Test-Path -LiteralPath $dcpLogDir) -and (@(Get-ChildItem -LiteralPath $dcpLogDir -File -ErrorAction SilentlyContinue).Count -gt 0)
    $hasCompressPermission = @(Get-ChildItem -LiteralPath $opencodeLogDir -Filter '*.log' | Where-Object { $_.LastWriteTime -ge (Get-Date).AddHours(-6) } | Select-String -SimpleMatch 'permission=compress' -ErrorAction SilentlyContinue).Count -gt 0
    $hasDcpLogs -or $hasCompressPermission
    ```
    Expected output: `True`.
  - Diagnostic checks: If `False`, inspect freshest OpenCode logs for `failed to load plugin`, `@tarquinen/opencode-dcp`, and DCP debug files for initialization errors.
  - Error recovery: If debug causes noisy or failing startup, restore the latest `dcp.jsonc` backup and restart again with approval.

### Exit criteria
DCP debug/logging or compress registration is observable, or the failure is documented and Phase 4 is justified.

## Phase 4 Clean reinstall / native re-resolve / explicit version pin

### Objective
Only if Phase 2 or 3 indicates hooks/factory are blocked, refresh package resolution safely.

### Checklist

- [ ] **Task 4.1 - Move the current DCP `@latest` package cache aside instead of deleting it.**
  - Action: Stop here unless OpenCode is closed or user approved restart/close. Then run:
    ```powershell
    $src = 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest'
    $dst = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest.bak-runtime-hooks-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Move-Item -LiteralPath $src -Destination $dst
    $dst
    ```
  - Authoritative acceptance check:
    ```powershell
    $currentMissing = -not (Test-Path -LiteralPath 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest')
    $backupExists = @(Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen' -Directory -Filter 'opencode-dcp@latest.bak-runtime-hooks-*').Count -ge 1
    $currentMissing -and $backupExists
    ```
    Expected output: `True`.
  - Diagnostic checks: Record the exact backup directory path in the execution log.
  - Error recovery: Roll back with `Move-Item -LiteralPath '<backup-dir>' -Destination 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest'` if re-resolution fails.

- [ ] **Task 4.2 - Let OpenCode re-resolve DCP natively and verify package recreation.**
  - Action: Launch/restart OpenCode through the user's normal method. If a CLI plugin command is available, prefer non-destructive inspection before add/remove. Then run:
    ```powershell
    $pkg = 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@tarquinen\opencode-dcp\package.json'
    if (Test-Path -LiteralPath $pkg) { Get-Content -Raw -LiteralPath $pkg | node -e "let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>{const p=JSON.parse(s); console.log(JSON.stringify({name:p.name,version:p.version}))})" } else { 'PACKAGE_NOT_RECREATED' }
    ```
  - Authoritative acceptance check:
    ```powershell
    $pkg = 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@tarquinen\opencode-dcp\package.json'
    (Test-Path -LiteralPath $pkg) -and ((Get-Content -Raw -LiteralPath $pkg).Contains('"version"'))
    ```
    Expected output: `True`.
  - Diagnostic checks: Rerun Task 2.1 and Task 3.2 after package recreation.
  - Error recovery: Restore the moved backup if OpenCode does not recreate the package or startup fails.

- [ ] **Task 4.3 - Pin `@tarquinen/opencode-dcp@3.1.14` only if `@latest` re-resolution remains suspect.**
  - Action: Before editing `opencode.jsonc`, create a backup and use a targeted replacement that does not print secrets:
    ```powershell
    $path = 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc'
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    Copy-Item -LiteralPath $path -Destination "$path.$ts.bak"
    $content = Get-Content -Raw -LiteralPath $path
    $new = $content.Replace('@tarquinen/opencode-dcp@latest', '@tarquinen/opencode-dcp@3.1.14')
    if ($new -eq $content) { throw 'DCP @latest string not found; do not guess plugin config shape.' }
    Set-Content -LiteralPath $path -Value $new -Encoding utf8
    'PIN_APPLIED_WITH_BACKUP'
    ```
  - Authoritative acceptance check:
    ```powershell
    $content = Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc'
    $content.Contains('@tarquinen/opencode-dcp@3.1.14') -and (-not $content.Contains('@tarquinen/opencode-dcp@latest'))
    ```
    Expected output: `True`.
  - Diagnostic checks: Do not output the whole config. Use targeted boolean checks only.
  - Error recovery: Restore `opencode.jsonc.<timestamp>.bak` if OpenCode fails to launch, plugin resolution worsens, or the user wants automatic updates restored.

### Exit criteria
The package is either cleanly re-resolved or restored, and any explicit version pin is backed up and reversible.

## Phase 5 Later fallback: OpenCode runtime upgrade assessment

### Objective
Upgrade only if diagnostics show DCP creates hooks but OpenCode 1.15.10 does not invoke/register them.

### Checklist

- [x] **Task 5.1 - Document current OpenCode version and decide whether upgrade is justified.**
  - Action: Run available version checks without changing installation:
    ```powershell
    $versionLines = Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.local\share\opencode\log' -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | Select-String -SimpleMatch 'version=' -ErrorAction SilentlyContinue | Select-Object -First 5
    $versionLines | ForEach-Object { $_.Line }
    ```
  - Authoritative acceptance check:
    ```powershell
    $versionLines = @(Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.local\share\opencode\log' -Filter '*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | Select-String -SimpleMatch 'version=' -ErrorAction SilentlyContinue)
    $versionLines.Count -gt 0
    ```
    Expected output: `True`.
  - Diagnostic checks: If version remains `1.15.10` and Phase 2 passes while runtime registration fails, recommend upgrade to a current OpenCode release as an environment fix.
  - Error recovery: Do not upgrade in this task. If upgrade is approved later, record installer method and rollback/reinstall path first.

### Exit criteria
Upgrade is either explicitly deferred or justified with evidence.

## Final Phase Validation & Handover

### Objective
Validate live DCP runtime behavior and document rollback state.

### Checklist

- [x] **Task V.1 - Verify `/dcp` command availability in an interactive OpenCode session.**
  - Action: In a restarted OpenCode session, run `/dcp help` or `/dcp status` if available. Capture only non-secret output or a screenshot summary in the execution log.
  - Authoritative acceptance check:
    ```powershell
    $logs = Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.local\share\opencode\log' -Filter '*.log' | Where-Object { $_.LastWriteTime -ge (Get-Date).AddHours(-6) }
    @(($logs | Select-String -SimpleMatch '/dcp' -ErrorAction SilentlyContinue), ($logs | Select-String -SimpleMatch 'command.execute.before' -ErrorAction SilentlyContinue)).Count -gt 0
    ```
    Expected output: `True`, or document manual interactive confirmation if logs do not record slash commands.
  - Diagnostic checks: If slash commands are not logged, record the exact visible result manually without secrets.
  - Error recovery: If `/dcp` is unrecognized while factory smoke test has command hooks, continue to report the runtime registration failure.

- [x] **Task V.2 - Generate or identify an eligible session and verify DCP runtime artifacts.**
  - Action: If safe and approved, create a test session exceeding DCP thresholds (>50K input context and >15 requests) or use the next naturally eligible session. Then run:
    ```powershell
    $stateDir = 'C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp'
    $dcpLogDir = 'C:\Users\DaveWitkin\.config\opencode\logs\dcp'
    [pscustomobject]@{
      NewPruneStates = @(Get-ChildItem -LiteralPath $stateDir -Filter 'ses_*.json' -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge (Get-Date).AddHours(-6) }).Count
      RecentDcpLogs = if (Test-Path -LiteralPath $dcpLogDir) { @(Get-ChildItem -LiteralPath $dcpLogDir -File | Where-Object { $_.LastWriteTime -ge (Get-Date).AddHours(-6) }).Count } else { 0 }
    } | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check:
    ```powershell
    $stateDir = 'C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp'
    $dcpLogDir = 'C:\Users\DaveWitkin\.config\opencode\logs\dcp'
    $hasState = @(Get-ChildItem -LiteralPath $stateDir -Filter 'ses_*.json' -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge (Get-Date).AddHours(-6) }).Count -gt 0
    $hasLogs = (Test-Path -LiteralPath $dcpLogDir) -and (@(Get-ChildItem -LiteralPath $dcpLogDir -File | Where-Object { $_.LastWriteTime -ge (Get-Date).AddHours(-6) }).Count -gt 0)
    $hasState -or $hasLogs
    ```
    Expected output: `True`.
  - Diagnostic checks: If no live eligible session can be generated, mark this task blocked-by-user/session and rely on V.3 for report validation when data exists.
  - Error recovery: Do not fabricate eligibility; record that runtime artifact validation needs a future eligible session.

- [ ] **Task V.3 - Run the DCP report and confirm a NEW post-fix eligible session has `has_dcp=True` (delta-based).**
  - Action: Capture the pre-fix `aggregate.json` as a baseline on first run, regenerate the report, then assert the new `sessions_with_dcp` count exceeds the baseline AND the report's `generated_at` advanced:
    ```powershell
    $runDate = (Get-Date).ToString('yyyy-MM-dd')
    $agg = 'C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\artifacts\aggregate.json'
    $baseline = 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\backups\aggregate.baseline.json'
    New-Item -ItemType Directory -Path (Split-Path -Parent $baseline) -Force | Out-Null
    if (-not (Test-Path -LiteralPath $baseline)) { Copy-Item -LiteralPath $agg -Destination $baseline }
    $baselineJson = Get-Content -Raw -LiteralPath $baseline | ConvertFrom-Json
    python 'C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\scripts\generate_report.py' --sessions 150 --verify
    python 'C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\scripts\generate_report.py' --sessions 150
    $newJson = Get-Content -Raw -LiteralPath $agg | ConvertFrom-Json
    [pscustomobject]@{
      BaselineGeneratedAt = $baselineJson.generated_at
      NewGeneratedAt = $newJson.generated_at
      BaselineSessionsWithDcp = $baselineJson.sessions_with_dcp
      NewSessionsWithDcp = $newJson.sessions_with_dcp
      BaselineHasDcpSessionCount = @($baselineJson.sessions | Where-Object { $_.has_dcp -eq $true }).Count
      NewHasDcpSessionCount = @($newJson.sessions | Where-Object { $_.has_dcp -eq $true }).Count
    } | ConvertTo-Json -Depth 3
    ```
  - Authoritative acceptance check (proves at least one new session triggered DCP since baseline):
    ```powershell
    $agg = 'C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\artifacts\aggregate.json'
    $baseline = 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\backups\aggregate.baseline.json'
    $baselineJson = Get-Content -Raw -LiteralPath $baseline | ConvertFrom-Json
    $newJson = Get-Content -Raw -LiteralPath $agg | ConvertFrom-Json
    $countGrew = $newJson.sessions_with_dcp -gt $baselineJson.sessions_with_dcp
    $reportRefreshed = ([datetime]$newJson.generated_at) -gt ([datetime]$baselineJson.generated_at)
    $countGrew -and $reportRefreshed
    ```
    Expected output: `True` only when at least one new session has triggered DCP since the baseline was captured and the report was actually re-generated. If the report cannot be regenerated (SQLite lock, schema drift), this task is blocked and prune-state/debug log evidence from V.1/V.2 becomes the runtime proof instead.
  - Diagnostic checks: Also report `sessions_missed`, `sessions_short`, and `per_model` deltas; if a known pre-fix session dropped from `has_dcp=true` to `false`, record the regression.
  - Error recovery: If the report script fails due to SQLite lock or schema drift, record the error and re-run once after a brief delay; if it still fails, fall back to prune-state / DCP debug log counts as runtime evidence and document why V.3 could not be authoritative.
- [x] **Task V.4 - Write execution log and rollback summary.**
  - Action: Capture the run date once with ``$runDate = (Get-Date).ToString('yyyy-MM-dd')`` and create ``C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix\execution-log-$runDate.md`` summarizing commands run, changes made, backups, runtime evidence, and any skipped/destructive steps. Reuse ``$runDate`` for any other date-stamped artifacts in the run.
  - Authoritative acceptance check:
    ```powershell
    $runDate = (Get-Date).ToString('yyyy-MM-dd')
    $log = Join-Path 'C:\development\opencode\.conductor\tracks\20260701-dcp-runtime-hooks-fix' "execution-log-$runDate.md"
    (Test-Path -LiteralPath $log) -and ((Get-Content -Raw -LiteralPath $log).Contains('Rollback summary')) -and ((Get-Content -Raw -LiteralPath $log).Contains('Runtime evidence'))
    ```
    Expected output: `True`.
  - Diagnostic checks: Ensure backups and any config paths are listed without secret values.
  - Error recovery: If validation is incomplete, mark remaining tasks unchecked and explain blockers.

### Exit criteria
Runtime behavior is validated or unresolved blockers are documented with backups/rollback instructions.

## Rollback quick reference

- Restore DCP debug config: `Copy-Item -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc.<timestamp>.bak' -Destination 'C:\Users\DaveWitkin\.config\opencode\dcp.jsonc' -Force`.
- Restore OpenCode config pin/plugin string: `Copy-Item -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.<timestamp>.bak' -Destination 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc' -Force`.
- Restore moved DCP cache: `Move-Item -LiteralPath '<opencode-dcp@latest.bak-runtime-hooks-timestamp>' -Destination 'C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest'`.
- Disable debug without restoring whole file: replace the exact literal `"debug": true` with `"debug": false` in `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc` after backup.

## Execution-readiness checklist

- [x] All commands use quoted absolute Windows paths and `-LiteralPath` where paths are consumed by PowerShell cmdlets.
- [x] No task requires printing the full `opencode.jsonc`.
- [x] Destructive steps are deferred until backups exist and OpenCode process safety is resolved.
- [x] Every task has exactly one `Authoritative acceptance check:`.
- [x] Runtime acceptance goes beyond plugin load lines.

## Top 3 risks and mitigations

1. **OpenCode processes are running and cache/config changes cause live-state corruption.** Mitigation: detect processes first and stop before restart/cache tasks without approval.
2. **DCP config JSONC edit breaks startup.** Mitigation: timestamped backup before edit and immediate rollback command.
3. **Report validation cannot produce a new eligible session on demand.** Mitigation: accept debug/prune-state evidence as interim proof and leave report validation pending until an eligible session exists.

## First task to execute

Start with **Task 0.1 - Confirm shell-first mode and required paths exist.**