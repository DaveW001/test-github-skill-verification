# Spec: Upgrade oc-chatgpt-multi-auth to oc-codex-multi-auth

## Goal

Upgrade the OpenCode Codex multi-auth plugin from the deprecated `oc-chatgpt-multi-auth@5.4.4` (with local patches) to the renamed `oc-codex-multi-auth@6.1.8` (latest known version at planning time), preserving the functional value of local patches while discarding debug artifacts.

## Background

The package was renamed from `oc-chatgpt-multi-auth` to `oc-codex-multi-auth`. The currently installed version (`5.4.4`) has local patches applied across 5 files in the OpenCode plugin cache. The new version (`6.1.8`) has incorporated some but not all of these patches upstream.

**Related track:** `20260429-openai-silent-failure` — where the original local patches were applied.

## Current State

- **Installed plugin:** `oc-chatgpt-multi-auth@5.4.4` at `C:\Users\DaveWitkin\.cache\opencode\packages\oc-chatgpt-multi-auth@5.4.4\`
- **Plugin config:** Already updated to `oc-codex-multi-auth` by the `npx` setup run in `C:\Users\DaveWitkin\.config\opencode\opencode.json`
- **Config backups:** Created automatically at `C:\Users\DaveWitkin\.config\opencode\opencode.json.bak-2026-05-01_*`
- **OpenCode restart required:** The current OpenCode process will not load the new plugin or new User environment variable until it is fully closed and restarted
- **Version note:** `opencode.json` uses the unversioned plugin name `oc-codex-multi-auth`; OpenCode may install the latest available version, expected to be `6.1.8` at planning time

## Implementation Decision

Use the **User environment variable** approach for the stream stall timeout.

- Set `CODEX_AUTH_STREAM_STALL_TIMEOUT_MS=120000` at the User environment scope
- Do **not** edit cached plugin source files
- Do **not** use plugin config for this setting unless a future maintainer explicitly validates the schema and chooses to change this plan

Exact command:

```powershell
[Environment]::SetEnvironmentVariable('CODEX_AUTH_STREAM_STALL_TIMEOUT_MS','120000','User')
```

Verification command:

```powershell
[Environment]::GetEnvironmentVariable('CODEX_AUTH_STREAM_STALL_TIMEOUT_MS','User')
```

Expected output:

```text
120000
```

## Patch Reconciliation Analysis

### Incorporated Upstream (no source patch action needed)

| Local Patch | How Upstream Handles It |
|---|---|
| `gpt-5.4-mini` model variants (none/low/medium/high/xhigh) in model-map.js | Present in v6.1.8 model-map.js with all variants |
| `STREAM_ERROR_CODE` — structured 502 JSON on SSE error events | Present in response-handler.js lines 139-161 |
| `function_call` null/undefined arguments → `"{}"` fix in request-transformer.js | Present in request-transformer.js lines 596-598 |

### Not Incorporated (monitor only, except timeout env var)

| Local Patch | File in 5.4.4 | Impact if Lost | Mitigation |
|---|---|---|---|
| **Stream stall timeout 45s → 120s** | `config.js` default + `response-handler.js` timeout | Long-running model responses may time out with 502 errors | Set User env var `CODEX_AUTH_STREAM_STALL_TIMEOUT_MS=120000` |
| **All call-type arguments fix** (`ensureCallArgumentsInInput`) | `fetch-helpers.js` | Non-`function_call` call types with null args could cause API errors | Low risk — monitor only; do not patch now |
| **SSE no `response.done` raw text fallback** | `response-handler.js` lines ~163-171 | When SSE stream ends without `response.done`, raw text may be returned instead of structured 502 JSON | Edge case — monitor only; do not patch now |

### Debug Artifacts (intentionally discard)

| Artifact | File | Notes |
|---|---|---|
| `DEBUG_CHATGPT_PROXY` env var logging | `response-handler.js` | Local debug switch, not needed in production |
| `require('fs').writeFileSync(...)` body dump | `fetch-helpers.js` | Local debug line writing request bodies to disk — must NOT be preserved |

## Requirements

- [ ] `C:\Users\DaveWitkin\.config\opencode\opencode.json` references `oc-codex-multi-auth`, not `oc-chatgpt-multi-auth`
- [ ] User environment variable `CODEX_AUTH_STREAM_STALL_TIMEOUT_MS` is set to `120000`
- [ ] OpenCode is fully restarted after the environment variable is set
- [ ] New plugin cache directory exists under `C:\Users\DaveWitkin\.cache\opencode\packages\oc-codex-multi-auth@*`
- [ ] Existing OAuth accounts are preserved and functional
- [ ] Required model entries are present in `opencode.json`
- [ ] OpenCode Codex tools `codex-list`, `codex-status`, and `codex-health` work after upgrade
- [ ] Debug artifacts from local patches are NOT carried forward
- [ ] Old plugin cache directory remains present for rollback

## Non-Requirements

- [ ] Re-patching the all-call-types arguments fix
- [ ] Re-patching the raw-text SSE fallback
- [ ] Modifying cached upstream plugin source code directly
- [ ] Deleting old package cache directories or backup directories
- [ ] Installing the plugin with npm globally

## Acceptance Criteria

- [ ] PowerShell command confirms `opencode.json` plugin list contains `oc-codex-multi-auth`
- [ ] PowerShell command confirms `opencode.json` has no `oc-chatgpt-multi-auth` references
- [ ] PowerShell command confirms `CODEX_AUTH_STREAM_STALL_TIMEOUT_MS` User env var is exactly `120000`
- [ ] After OpenCode restart, PowerShell command confirms a `oc-codex-multi-auth@*` package cache directory exists
- [ ] OpenCode tool `codex-list` shows configured OAuth accounts
- [ ] OpenCode tool `codex-status` returns account status without tool errors
- [ ] OpenCode tool `codex-health` validates refresh tokens or identifies only user-actionable account failures
- [ ] PowerShell command confirms required model keys are present in `opencode.json`
- [ ] PowerShell command confirms no `writeFileSync` debug body dump exists in the new plugin source
- [ ] `C:\development\opencode\.conductor\tracks\20260501-codex-multi-auth-upgrade\metadata.json` is marked completed only after all validation passes

## Rollback Criteria

Rollback is required if OpenCode cannot load the `oc-codex-multi-auth` plugin after two restarts, or if the Codex account tools are unavailable after confirming `opencode.json` references the new plugin.

Rollback action:

1. Restore `C:\Users\DaveWitkin\.config\opencode\opencode.json` from the most recent `opencode.json.bak-2026-05-01_*` backup, or manually set the plugin list back to `"oc-chatgpt-multi-auth"`.
2. Restart OpenCode.
3. Leave all package cache and patch backup directories intact.
