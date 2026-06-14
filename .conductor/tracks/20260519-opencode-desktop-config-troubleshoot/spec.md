# OpenCode Desktop Config Troubleshooting

## Track ID

20260519-opencode-desktop-config-troubleshoot

## Problem

OpenCode Desktop appears to have a configuration/runtime problem after changes made on Monday, May 18, 2026. The exact user-visible failure still needs to be reproduced, but the May 18 Desktop logs show config-adjacent anomalies during startup:

- Desktop sidecar started but logged `No CLI installation found, skipping sync`.
- Skillful repeatedly initialized within seconds.
- Skill discovery emitted duplicate skill-name warnings across multiple roots:
  - `C:\Users\DaveWitkin\.agents\skills`
  - `C:\Users\DaveWitkin\.config\opencode\skill`
  - `C:\Users\DaveWitkin\.config\opencode\skills`
  - project-local `.agents\skills` and `.opencode\skills` folders
- Prior conductor work intentionally unified skill sources via junctions in `20260502-skill-junction-unification`, so duplicate resolution or Desktop state caching may have drifted.
- Prior Desktop/CLI diagnostics in `20260508-scheduler-desktop-cli-diagnostics` already found Desktop and global config could diverge.
- The directly relevant prior config track is `C:\Users\DaveWitkin\.config\opencode\.conductor\tracks\20260517-opencode-go-dual-sub-config`, which added `go-dave` and `go-tiberius` providers backed by `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` in `C:\Users\DaveWitkin\.config\opencode\.env`.
- Existing repo documentation for OpenRouter says Desktop has previously failed to resolve provider API keys from `.env`, requiring Windows user-level environment variables instead.

## Goal

Identify what changed or became inconsistent around May 18, isolate the root cause, apply the smallest reversible fix, and validate OpenCode Desktop starts with the expected config, plugin list, skill roots, and provider/auth behavior.

## Scope

In scope:

- `C:\development\opencode` repo conductor/docs/history.
- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`, `tui.json`, `AGENTS.md`, `agent`, `skill`, `skills`, `plugin`, `scheduler`, and backups.
- `C:\Users\DaveWitkin\.opencode` cache/state where relevant.
- `C:\Users\DaveWitkin\.config\opencode\.conductor\tracks\20260517-opencode-go-dual-sub-config`
- OpenCode Desktop app state and logs under:
  - `C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop`
  - `C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop`
- Prior conductor tracks:
  - `20260502-skill-junction-unification`
  - `20260508-scheduler-desktop-cli-diagnostics`
  - `20260501-codex-multi-auth-upgrade`
- `20260429-openai-silent-failure`
- `C:\Users\DaveWitkin\.config\opencode\.conductor\tracks\20260517-opencode-go-dual-sub-config`

Out of scope unless evidence points there:

- Broad OpenCode core changes.
- Reinstalling Desktop.
- Deleting Desktop state or auth files before backups and an explicit rollback path exist.

## Leading Hypotheses

1. **Desktop cannot see the new Go API key environment variables**: The dual-sub track stored keys in `.env`, but Windows user-level and current process checks show `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` are not set outside `.env`. Prior OpenRouter evidence says Desktop may not reliably load `.env`, which would cause missing-auth failures in Desktop while config parsing still looks valid.
2. **Provider display ambiguity**: The prior execution log says both `go-dave` and `go-tiberius` appear as the same `opencode-go/` model catalog in `opencode models`, so `/models` may not expose the two subscriptions as visibly distinct even if the provider entries are separate.
3. **Duplicate skill roots after junction unification**: Desktop is loading both `skill` and `skills` plus `.agents`, causing duplicate warnings, excess prompt/tool context, or incorrect skill resolution.
4. **Desktop state/cache drift**: Desktop `.dat` state files or Electron storage still reference stale workspaces/config roots from before the latest config changes.
5. **CLI sync failure**: `No CLI installation found, skipping sync` means Desktop cannot reconcile with the expected CLI/config installation path.
6. **Plugin/config mismatch**: The effective Desktop plugin list may differ from `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`, similar to the earlier scheduler divergence.

## Success Criteria

- The concrete user-visible failure is reproduced or ruled out with evidence.
- Effective Desktop config matches the intended global config, or any intentional divergence is documented.
- Duplicate skill warnings are either eliminated or proven harmless with a documented reason.
- Desktop startup log after fix shows clean initialization without repeated Skillful reload loops.
- `opencode debug config` and a Desktop-side smoke test agree on plugin list and key model/provider settings.
- Go provider credentials are available to Desktop, preferably via Windows user-level env vars if `.env` loading is confirmed unreliable.
- Rollback instructions exist before any risky state/config mutation.
