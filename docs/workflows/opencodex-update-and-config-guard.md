# Workflow: OpenCodex Update and Config Guard

**Last updated:** 2026-08-17
**Owner:** Dave Witkin
**Applies to:** Codex Desktop routing through the OpenCodex proxy (`@bitkyc08/opencodex`)

> **Current installed version (verified 2026-08-17):** `@bitkyc08/opencodex@2.21.0`,
> running on `http://127.0.0.1:10101`; `GET /healthz` returns 200.
> The 2.10.0-era notes below describe the original fix and the legacy guard;
> the guard and the manual checks remain installed on this workstation.

## Overview

Codex Desktop reads the auto-compaction threshold from root keys in
`~/.codex/config.toml`:

```toml
model_auto_compact_token_limit = 150000
model_auto_compact_token_limit_scope = "total"
```

Upstream bug [lidge-jun/opencodex#817](https://github.com/lidge-jun/opencodex/issues/817)
made the opencodex injector delete `model_auto_compact_token_limit` on every
re-inject (while intentionally keeping `model_context_window`). Sessions then
grew past 300k tokens without compacting. The fix was merged in [PR #832](https://github.com/lidge-jun/opencodex/pull/832)
and is included in OpenCodex `2.10.0`, verified live on 2026-08-03.

The local patch and daily guard described below are now legacy safety measures.
They remain installed on this workstation pending a separate cleanup decision;
they are no longer required to fix issue #817 in `2.10.0`.

## Files involved

| File | Purpose |
| --- | --- |
| `~/.codex/config.toml` | Root compaction keys (must be before the first `[table]`) |
| `%APPDATA%\npm\node_modules\@bitkyc08\opencodex\src\codex\inject.ts` | Installed injector; `2.10.0` strips only root `model_context_window` |
| `~/.codex/scripts/opencodex-config-guard.ps1` | Legacy guard; retained until separately reviewed and retired |
| `~/.codex/scripts/README.md` | Guard reference and manual-run instructions |
| `~/.codex/logs/opencodex-config-guard.log` | Guard run log |
| `~/.opencodex/runtime-port.json` | Proxy PID/port used for restarts |

## Scheduled guard (legacy)

Task `\OpenCode\OpenCodex-Config-Guard` remains installed as a legacy daily
safety net (hidden window, no admin). It:

1. Reapplies the injector filter fix if an update reverted it.
2. Restores both root config keys (timestamped backup first) if missing.
3. Restarts the proxy only when the patch was reapplied, then waits for
   `http://127.0.0.1:10101/healthz` to return 200.

## Step-by-step: after installing or updating opencodex

1. Confirm every other Codex task is idle or complete. Do not restart the
   shared proxy while another Codex task is processing.

2. Back up `~/.codex/config.toml`, then note the new version:

   ```powershell
   npm list -g @bitkyc08/opencodex
   ```

3. Install/update:

   ```powershell
   npm install -g @bitkyc08/opencodex   # or npm update -g @bitkyc08/opencodex
   ```

4. Restart the proxy once the idle gate is still clear:

   ```powershell
   ocx restart
   ```

5. Verify the version, proxy health, and startup state:

   ```powershell
   opencodex --version
   ocx status --json
   ```

   The expected OpenCodex 2.21.0 state is a healthy proxy with the service
   protected and reboot-safe.

6. Verify the keys survive the fresh re-inject:

   ```powershell
   Select-String -Path "$env:USERPROFILE\.codex\config.toml" `
     -Pattern '^\s*model_auto_compact_token_limit\s*=','^\s*model_auto_compact_token_limit_scope\s*='
   ```

   Both lines must still be present. Start a new Codex session only after this
   check completes.

7. Watch a fresh long session: `token_count` / `context_compacted` events in
   `~/.codex/sessions/**` should show compaction near ~143–150k, not 300k+.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Guard log says `Injector structure changed` | Upstream rewrote the function | Review `inject.ts`, update the patch markers in the guard, or re-patch manually |
| Config keys missing after proxy restart | Injector reverted and guard did not run yet | Run the guard task immediately |
| Existing session still grows past 300k | Session loaded its threshold before the fix | Use `/compact` in that session; only new sessions honor 150k |
| Proxy not healthy after restart | Wrapper task did not respawn | `Start-ScheduledTask -TaskName 'opencodex-proxy'` |

## Legacy guard retirement

Because #817 is fixed and released:

1. Keep the root config keys.
2. Review whether the legacy guard protects any unrelated local invariants.
3. If it has no remaining purpose, remove the task and script in a separately
   approved cleanup operation; do not combine that deletion with an upgrade.

## References

- [OpenCodex Config Guard README](C:/Users/DaveWitkin/.codex/scripts/README.md)
- [Upstream issue #817](https://github.com/lidge-jun/opencodex/issues/817)
- [Fix PR #832](https://github.com/lidge-jun/opencodex/pull/832)
- [OpenCodex 2.10.0 release](https://github.com/lidge-jun/opencodex/releases/tag/v2.10.0)
- Durable note (current): `C:/development/opencodex-ops/docs/2026-08-15-codex-context-compaction-decision.md`
