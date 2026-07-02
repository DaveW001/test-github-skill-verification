# Spec: DCP runtime hook failure follow-up

Track ID: `20260701-dcp-runtime-hooks-fix`

## Goal / outcome

Restore and prove runtime behavior for `@tarquinen/opencode-dcp` in Dave's OpenCode environment. The successful end state is not just plugin module load; it is observable DCP hook/config/tool behavior in a live or freshly generated eligible OpenCode session.

## Constraints / non-goals

- Do not print, copy, or persist secrets from `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- Treat this as a user-environment/plugin-installation/config issue first; do not assume repo application code is defective.
- Native file tools may fail with `Bun is not defined`; use PowerShell-first fallback through the shell with `-LiteralPath` and quoted Windows paths.
- Do not kill, restart, remove, or upgrade running OpenCode processes without user approval when the executor cannot safely determine restart impact.
- Prefer low-risk diagnostics before reinstall, version pinning, or runtime upgrade.
- Prefer DCP config file debug (`C:\Users\DaveWitkin\.config\opencode\dcp.jsonc`) over plugin tuple options unless OpenCode plugin option syntax is verified first.

## Definition of done

- Baseline evidence confirms whether DCP is merely loading or actually registering hooks/tools.
- A direct plugin factory smoke test establishes whether DCP 3.1.14 can construct its hook object in the current Node/OpenCode package environment.
- If needed, DCP debug is enabled through `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc` with a timestamped backup and rollback path.
- Runtime acceptance criteria are checked: `permission=compress` or a visible compress tool, `/dcp` command availability, DCP debug log or prune-state creation, and report-based `has_dcp=True` for an eligible session when a live eligible session can be generated.
- Any package cache removal/reinstall/version pin/upgrade step has a backup and rollback instruction.

## Primary evidence from handover

- DCP 3.1.14 loads without tokenizer errors after the previous outage fix.
- No prune-state files have been created since 2026-06-25.
- 40 of 51 post-fix sessions were eligible for DCP but none showed DCP activity.
- Recent logs show plugin load lines but no `compress` permission/tool activity.
- DCP 3.1.14 bundled `server` returns hooks including `experimental.chat.messages.transform`, `command.execute.before`, `tool.compress`, and `config`.
- The handover's original Fix 1 proposed plugin tuple options; this track supersedes that with `dcp.jsonc` debug because DCP reads `debug` via `getConfig(ctx)` from DCP config locations.

## Proposed fix sequence

1. Baseline diagnostics and backups only.
2. Direct plugin factory smoke test to determine whether hook object construction succeeds outside OpenCode launch.
3. Enable DCP debug via `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc`, restart only with approval, and inspect DCP logs/runtime registration.
4. If factory or registration remains blocked, cleanly re-resolve the DCP package cache using OpenCode's own plugin/package mechanism or restore from backup.
5. If `@latest` resolution is suspect, pin `@tarquinen/opencode-dcp@3.1.14` with config backup and rollback.
6. Upgrade OpenCode only as a later fallback after diagnostics indicate the installed 1.15.10 runtime is not invoking plugin hooks.
