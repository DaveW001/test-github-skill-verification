# OpenAI Account Rotation Failures (`oc-codex-multi-auth`) - Troubleshooting and Validation Guide

**Status:** Active reference; remediation validated 2026-07-21
**Applies to:** OpenCode agents using `openai` provider models through ChatGPT/Codex OAuth, including gpt-5.6 Sol and Luna
**Mechanism:** `oc-codex-multi-auth` (not the Gemini proxy or Antigravity)
**Known-good plugin version:** 6.10.0 as of 2026-07-21
**Last updated:** July 21, 2026

---

## Executive Summary

A repeated usage-limit loop does not have one universal cause. The July 20-21 incident exposed three independent failure modes that can look identical:

1. **Older-runtime orphan locks:** dead-PID lock files prevented an older plugin runtime from persisting account health and rate-limit state.
2. **Corrupt/stale plugin cache:** OpenCode trusted a cached v6.7.1 `@latest` wrapper whose import failed on a missing dependency, so the plugin silently failed to expose its `codex-*` tools.
3. **Fragmented account storage:** per-project storage was enabled by default, but only one project key contained the four-account pool. Other repos and fresh child processes could see zero accounts or a different pool.

The validated remediation was to preserve rollback assets, refresh the cache to v6.10.0 without running the unsafe default installer, move the pool to global storage, disable per-project pools in the plugin's own config file, restart through fresh processes, and prove routing by switching accounts and running timestamped Sol and Luna probes.

**Validated result:** manual multi-account routing works. Automatic 429 failover remains conditionally untested because no enabled account was naturally rate-limited during the validation. Do not manufacture a 429 by burning quota or corrupting credentials.

---

## Fast Triage

| Symptom | Most likely cause | First check |
|---|---|---|
| Same `AI_APICallError: The usage limit has been reached` repeats without switching | Rotation state cannot update, plugin not loaded, or only one pool/account is visible | Check plugin tools, pool scope, and lock owners |
| `codex-list` or every `codex-*` tool is unavailable | Plugin cache/import failure or plugin absent from effective config | Run `opencode debug agent build`; inspect cache wrappers |
| Standalone CLI reports zero accounts while another repo has accounts | Per-project storage fragmentation | Locate every account pool and inspect plugin storage configuration |
| OpenAI works now after failing yesterday | Quota may have reset; this proves connectivity, not rotation | Perform a controlled manual-switch test |
| A `.lock` exists after a short-lived v6.10.0 process | Advisory sidecar may not have been removed during async shutdown | Check PID; verify the next process can take it over |
| OpenAI fails but `opencode-go` succeeds | OpenAI auth/rotation layer is suspect | Continue with this guide |
| Both OpenAI and unrelated providers fail | Broader provider/network/OpenCode problem | Do not assume this plugin is the cause |

### Do not chase these false leads

- **Gemini proxy:** `127.0.0.1:8000`, Gemini API keys, and its scheduled task serve Google models only.
- **Antigravity state:** `%APPDATA%\opencode\antigravity-accounts.json` belongs to a separate auth container.
- **A single successful OpenAI prompt:** that can be a quota reset or built-in/single-account auth and does not prove rotation.

---

## Known-Good State on This Machine

`~` means `C:\Users\DaveWitkin`.

| Purpose | Expected path/state |
|---|---|
| Canonical global OpenCode config | `~/.config/opencode/opencode.jsonc` |
| Forbidden drift config | `~/.config/opencode/opencode.json` must not exist |
| Plugin entry | `"oc-codex-multi-auth"` in the canonical JSONC `plugin` array |
| Plugin-specific config | `~/.opencode/openai-codex-auth-config.json` with `perProjectAccounts: false` |
| Effective global pool | `~/.opencode/oc-codex-multi-auth-accounts.json` |
| Historical project pools | `~/.opencode/projects/<project-key>/oc-codex-multi-auth-accounts.json` (rollback/history; not effective while global mode is configured) |
| Active runtime cache | One healthy v6.10.0 wrapper under `~/.cache/opencode/packages/oc-codex-multi-auth*` |
| Restricted rollback directory | `~/.opencode/backups/openai-rotation-20260721-143137/` |

The global pool had four entries during validation: three enabled and one disabled. Never record account emails, account IDs, access tokens, or refresh tokens in logs or documentation.

### Important configuration rule

On this machine, the only canonical global OpenCode config is `opencode.jsonc`. Do **not** run the package installer with no command: its documented default writes `~/.config/opencode/opencode.json`, which is forbidden machine drift here.

For v6.10.0, `perProjectAccounts` is read from the plugin's own JSON config or `CODEX_AUTH_PER_PROJECT_ACCOUNTS`. An OpenCode plugin tuple such as `['oc-codex-multi-auth', { perProjectAccounts: false }]` validated syntactically but did not change runtime storage selection in testing. Use:

```json
{
  "perProjectAccounts": false
}
```

at `~/.opencode/openai-codex-auth-config.json`, then fully restart OpenCode.

---

## Failure Mode 1: Dead-PID Locks

### Older behavior observed on July 20

Three lock files existed across global and project scopes. Their owners were dead. The older plugin/runtime repeatedly retried one exhausted account and did not reliably persist health changes. Removing only dead-owner locks and restarting restored immediate connectivity, but later testing showed this was not the only problem.

### v6.10.0 behavior

v6.10.0 uses an advisory JSON sidecar at `<accounts-file>.lock`. It records PID, hostname, working directory, start time, and last activity. A short-lived `opencode run` process can leave a dead-PID sidecar because asynchronous `beforeExit` cleanup is not reliably awaited by the host/runtime.

Unlike the older failure mode, v6.10.0 checks a same-host PID and can immediately take over a dead owner's sidecar. The validation observed the Luna process successfully replacing the dead lock left by the preceding Sol process.

A dead sidecar is therefore:

- still worth detecting and cleaning at final hygiene,
- not automatically proof that v6.10.0 is blocked,
- a failure if the next process does **not** take it over or cannot persist state.

### Safe lock inventory

```powershell
$localHost = [System.Net.Dns]::GetHostName()
Get-ChildItem -Path "$HOME\.opencode" -Recurse -File `
  -Filter 'oc-codex-multi-auth-accounts.json.lock' -ErrorAction SilentlyContinue |
  ForEach-Object {
    $j = Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json
    $sameHost = [string]::Equals(
      [string]$j.hostname,
      $localHost,
      [System.StringComparison]::OrdinalIgnoreCase
    )
    $alive = if ($sameHost -and $j.pid) {
      [bool](Get-Process -Id $j.pid -ErrorAction SilentlyContinue)
    } else {
      $null
    }
    [pscustomobject]@{
      Lock          = $_.FullName
      PID           = $j.pid
      Hostname      = $j.hostname
      SameHost      = $sameHost
      LastActive    = $j.lastActive
      AliveLocally  = $alive
      DeadSameHost  = $sameHost -and ($alive -eq $false)
    }
  } | Format-Table -AutoSize
```

Prefer v6.10.0's automatic dead-owner takeover. Manually delete a sidecar only during a maintenance window after **all OpenCode and plugin processes have been stopped**. Run the deletion from a separate PowerShell terminal, then re-read the sidecar immediately before removal and require the same local hostname/PID to remain dead:

```powershell
$lockPath = '<full-lock-path>'
$expectedPid = <pid-from-inventory>
$localHost = [System.Net.Dns]::GetHostName()
$current = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json

if (-not [string]::Equals(
  [string]$current.hostname,
  $localHost,
  [System.StringComparison]::OrdinalIgnoreCase
)) { throw 'Lock belongs to another host; refusing deletion' }

if ($current.pid -ne $expectedPid) {
  throw 'Lock owner changed after inventory; refusing deletion'
}

if (Get-Process -Id $current.pid -ErrorAction SilentlyContinue) {
  throw 'Lock owner is alive; refusing deletion'
}

Remove-Item -LiteralPath $lockPath -Force
```

Never classify a different-host lock as dead by checking the local process table. For a foreign-host lock, let the plugin's stale-lock logic take over or independently verify the remote owner and timestamp. If OpenCode cannot be fully stopped, do not delete the sidecar manually.

---

## Failure Mode 2: Corrupt or Stale Plugin Cache

### What happened

The plugin was listed correctly in effective config, but fresh agents exposed no `codex-*` tools. Direct inspection found:

- an old active cache at v6.3.4,
- a stale `oc-codex-multi-auth@latest` wrapper at v6.7.1,
- a direct Bun import failure from the stale wrapper: missing `@openauthjs/openauth/pkce`.

OpenCode v1.18.4 resolves a bare npm plugin through its cached package wrapper and trusts an existing nested `node_modules/<package>` without reinstalling it. The load failure may be published internally as a session error without a clear startup message, so configuration can look correct while the tool surface is absent.

The package's installer also clears cache paths that do not fully match current OpenCode wrapper behavior. Running the installer was both insufficiently targeted and unsafe here because of the forbidden JSON config behavior.

### Diagnose cache wrappers without exposing secrets

```powershell
Get-ChildItem -Path "$HOME\.cache\opencode\packages" -Directory `
  -Filter 'oc-codex-multi-auth*' |
  ForEach-Object {
    $packageJson = Join-Path $_.FullName `
      'node_modules\oc-codex-multi-auth\package.json'
    if (Test-Path -LiteralPath $packageJson) {
      $package = Get-Content -Raw -LiteralPath $packageJson | ConvertFrom-Json
      [pscustomobject]@{
        Wrapper = $_.FullName
        Version = $package.version
      }
    }
  }
```

Then inspect only the relevant lines from the fresh agent registry rather than emitting the entire merged agent configuration:

```powershell
$agentDebug = & opencode debug agent build 2>&1
if ($LASTEXITCODE -ne 0) { throw 'Agent registry inspection failed' }
$agentDebug | Select-String -Pattern 'codex-(list|status|health|limits|switch|doctor|warm)'
```

A healthy v6.10.0 load should expose 24 tools, including at least:

- `codex-list`
- `codex-status`
- `codex-health`
- `codex-limits`
- `codex-switch`
- `codex-doctor`
- `codex-warm`

### Safe cache refresh used in this incident

1. Back up `opencode.jsonc`, the effective account pool, and cache package metadata.
2. Verify the account-pool backup hash without printing its contents.
3. Move stale/corrupt `oc-codex-multi-auth*` wrapper directories into a restricted rollback directory instead of deleting them immediately.
4. Run a fresh `opencode debug agent build`. OpenCode should resolve and install the current package.
5. Verify the nested package version is 6.10.0 and the `codex-*` tools are present.
6. Validate `opencode debug config` by exit status with its output suppressed, and confirm forbidden global `opencode.json` is absent.
7. Fully restart long-lived OpenCode desktop/TUI processes.

Do not use `npx -y oc-codex-multi-auth@latest` with no command on this machine.

---

## Failure Mode 3: Pool Scope Fragmentation

### What happened

Per-project accounts were enabled by default. Only one historical project key contained the four-account pool; the current repo's other project key had no pool, and no global pool existed. Standalone status commands looked only at global storage and therefore reported zero accounts.

This allowed repos, child agents, and standalone diagnostics to disagree about whether any accounts existed.

### Inventory all pools without printing credentials

```powershell
Get-ChildItem -Path "$HOME\.opencode" -Recurse -File `
  -Filter 'oc-codex-multi-auth-accounts.json' -ErrorAction SilentlyContinue |
  ForEach-Object {
    $j = Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json
    [pscustomobject]@{
      Path        = $_.FullName
      AccountCount = @($j.accounts).Count
      ActiveIndex = $j.activeIndex
      Modified    = $_.LastWriteTime
    }
  } | Format-Table -AutoSize
```

### Validated normalization

The selected design is one global pool with per-project storage disabled:

1. Create a restricted backup of the source project pool.
2. Copy it byte-for-byte to `~/.opencode/oc-codex-multi-auth-accounts.json`.
3. Verify source and destination SHA-256 hashes match.
4. Restrict the destination ACL to the current user and SYSTEM.
5. Create `~/.opencode/openai-codex-auth-config.json` with `perProjectAccounts: false`.
6. Leave historical project pools in place as rollback sources; do not print or commit them.
7. Restart OpenCode and verify redacted account count/active index from the current repo and a fresh process.

Do not migrate or merge OAuth JSON by hand unless a verified backup and rollback path exist. These files contain secret-bearing token state.

---

## Controlled Validation Procedure

Treat the following as separate claims:

1. **Connectivity:** one OpenAI request succeeds.
2. **Pool visibility:** the plugin sees the intended account count.
3. **Manual routing:** selecting another account changes persisted state and a fresh process succeeds through it.
4. **Automatic failover:** a naturally rate-limited account causes one request to finish through another account without an endless retry loop.

Do not claim a stronger result than the evidence supports.

### A. Baseline checks

```powershell
& opencode debug config 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'OpenCode config validation failed' }

npm view oc-codex-multi-auth version
Test-Path -LiteralPath "$HOME\.config\opencode\opencode.json"
```

Expected: config exit 0, reviewed package version, and `False` for the forbidden JSON path. Suppress merged config output because it can contain resolved sensitive settings.

Project the global pool locally so raw account objects never enter a tool transcript, chat, or execution log:

```powershell
$poolPath = "$HOME\.opencode\oc-codex-multi-auth-accounts.json"
$pool = Get-Content -Raw -LiteralPath $poolPath | ConvertFrom-Json
$accounts = @($pool.accounts)
$enabled = @($accounts | Where-Object { $_.enabled -ne $false }).Count
[pscustomobject]@{
  Total       = $accounts.Count
  Enabled     = $enabled
  Disabled    = $accounts.Count - $enabled
  ActiveIndex = $pool.activeIndex
}
```

Do not emit raw `codex-list` JSON. In v6.10.0 it can include account identity, label, or workspace fields even when `CODEX_TUI_MASK_EMAIL=1`; that setting masks display email but is not a complete JSON redaction boundary.

### B. Manual-switch proof

Record only the original active index. Switch to a different enabled, healthy account, then verify the stored active index changed without displaying the account object.

#### Important `codex-switch` caveat

In the July 21 test, asking a model to call `codex-switch` produced a successful tool response, but the model's follow-up provider request could save an account-manager snapshot loaded before the switch and overwrite the new active index. That conversational method was not accepted as deterministic evidence.

For v6.10.0, the deterministic test directly invoked the shipped `createCodexSwitchTool` implementation in a short-lived Bun script after calling `setStoragePath(null)`. The script supplied only minimal UI callbacks, requested a 1-based target index, asserted a successful return, and printed no account metadata. This exercised the plugin's own transaction and persistence code without a follow-up model request.

Because this uses an internal package API, re-check the v6.10.0 source signature before repeating it on another version. The exact evidence and deviations are recorded in:

`.conductor/tracks/20260721-openai-rotation-validation/execution-log.md`

### C. Fresh-process Sol and Luna probes

After switching, run tiny, timestamped probes in separate processes:

```powershell
opencode run --agent build --model openai/gpt-5.6-sol `
  'Reply exactly: SOL_AFTER_SWITCH_OK'

opencode run --agent build --model openai/gpt-5.6-luna `
  'Reply exactly: LUNA_AFTER_SWITCH_OK'
```

For each probe, require:

- exit code 0,
- exact expected reply,
- persisted active index remains the selected index,
- no repeated usage-limit sequence in the bounded log window,
- lock owner state recorded after process exit.

The July 21 validation switched from account 1 to account 3, received exact successful Sol and Luna responses in fresh processes, retained zero-based active index 2, then switched back to account 1 and restored zero-based active index 0.

### D. Lock takeover and final hygiene

If the Sol process leaves a dead-owner v6.10.0 advisory sidecar, do not immediately assume failure. Without deleting it, start the Luna probe and verify that:

- Luna succeeds,
- the sidecar PID changes to the Luna process,
- state remains writable.

That proves dead-owner takeover. At final closeout, remove only confirmed-dead sidecars or run a clean plugin operation that releases them, then require a final lock count of zero.

### E. Conditional automatic-failover proof

Use `codex-limits` to determine whether an enabled account is already naturally limited or cooling down. If none is limited, stop and mark automatic failover **deferred**.

If one is naturally limited, the safe pass criteria are:

1. record redacted starting index/state,
2. issue one tiny request,
3. receive one final success through a healthy account,
4. observe the active state change,
5. observe `lastSwitchReason=rate-limit`,
6. observe no endless same-account retries,
7. verify subsequent state writes and lock hygiene.

Never deliberately burn quota, corrupt tokens, or edit rate-limit state to manufacture a 429.

---

## Command Context: Avoid This Frequent Confusion

| Context | Available operations |
|---|---|
| OpenCode plugin tool surface | `codex-list`, `codex-health`, `codex-switch`, `codex-limits`, `codex-doctor`, and the other registered tools |
| Standalone package CLI | `status`, `list`, `limits`, `health`, `doctor`, `warm`, `dashboard`, `diag` |
| OpenCode authentication CLI | `opencode auth status`, `opencode auth login` |

The standalone package CLI does **not** provide a `switch` command in v6.10.0. Also, `codex-*` are plugin tools, not ordinary PowerShell executables.

Useful environment settings include:

- `CODEX_AUTH_PER_PROJECT_ACCOUNTS=0|1`
- `CODEX_AUTH_ROTATION_STRATEGY=hybrid|sticky|round-robin`
- `CODEX_TUI_MASK_EMAIL=1`
- `ENABLE_PLUGIN_REQUEST_LOGGING=1`

Avoid `CODEX_PLUGIN_LOG_BODIES=1` unless explicitly required; request bodies may be sensitive.

---

## Fast Decision Tree

1. Is only OpenAI failing? If no, investigate the wider provider/network problem.
2. Does `opencode debug agent build` expose `codex-*` tools?
   - **No:** inspect cache wrappers/importability and refresh the corrupt cache safely.
3. Does the intended process see the expected redacted account count?
   - **No:** inventory global/project pools and verify `perProjectAccounts` configuration.
4. Are lock owners alive?
   - **Live:** do not delete.
   - **Dead on v6.10.0:** verify next-process takeover; clean at final hygiene.
5. Does a deterministic manual switch persist and do fresh Sol/Luna probes succeed?
   - **Yes:** manual routing is proven.
6. Is an account naturally limited?
   - **No:** defer automatic failover.
   - **Yes:** run one tiny automatic-failover probe with the strict criteria above.

---

## Prevention and Recurrence Checklist

- [ ] Keep one intentional account-pool scope; avoid accidental per-project copies.
- [ ] Preserve `~/.opencode/openai-codex-auth-config.json` with `perProjectAccounts: false` on this machine.
- [ ] Confirm the plugin tool surface after cache or OpenCode upgrades.
- [ ] Inspect every matching cache wrapper, not only the unversioned directory.
- [ ] Treat current connectivity, manual routing, and automatic failover as separate claims.
- [ ] Check lock PID liveness before deletion.
- [ ] Verify v6.10.0 dead-lock takeover rather than assuming any sidecar is fatal.
- [ ] Fully restart OpenCode after config/plugin changes; config is loaded once.
- [ ] Never run the default plugin installer here because it writes forbidden global `opencode.json`.
- [ ] Never print, copy into the repo, or commit OAuth pool contents.

---

## Agent and Environment Notes

- If native file tools fail with `Bun is not defined`, switch the whole session to PowerShell through the Bash tool. Do not repeatedly retry the broken file-tool layer.
- Consult `~/.config/opencode/secrets-index.jsonc` before searching repositories for credentials. Never print secret values.
- Validate `opencode debug config` after every canonical configuration edit, but suppress merged output and check only its exit status.
- Existing project pools and restricted backups are secret-bearing. Mention paths and hashes only.
- Do not modify unrelated worktree files while troubleshooting.

---

## Related Evidence and Documentation

- Detailed July 21 spec and safety boundaries: `.conductor/tracks/20260721-openai-rotation-validation/spec.md`
- Detailed July 21 execution evidence: `.conductor/tracks/20260721-openai-rotation-validation/execution-log.md`
- Gemini proxy, separate mechanism: `docs/troubleshooting/active/gemini-proxy-down.md`
- Tool-context distinction: `docs/troubleshooting/active/codex-refresh-not-recognized-and-proxy-10048.md`
- OpenCode configuration reference: `docs/reference/opencode-configuration.md`
- Plugin upstream: https://github.com/ndycode/oc-codex-multi-auth

---

**Document version:** 2.0
**Created:** July 20, 2026
**Updated:** July 21, 2026
**Current verdict:** Manual account routing validated across fresh Sol and Luna processes; automatic natural-429 failover deferred until a real quota event.
