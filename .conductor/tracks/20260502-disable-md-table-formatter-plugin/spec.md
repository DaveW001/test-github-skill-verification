# Disable OpenCode Markdown Table Formatter Plugin

## Brief Restatement

### Goal / Outcome

Disable the global OpenCode add-in `@franlol/opencode-md-table-formatter@0.0.3` so it no longer loads at OpenCode startup, while preserving a safe rollback path and keeping local OpenCode configuration documentation accurate.

### Constraints / Non-Goals

- Do not execute implementation during planning.
- Do not remove unrelated OpenCode plugins.
- Do not change models, providers, permissions, skills, agents, commands, MCP servers, or scheduler tasks.
- Do not delete backups or historical config files.
- Do not uninstall npm packages unless validation proves the package is independently installed and no longer referenced; current research found it is referenced in `opencode.jsonc` but not listed in `C:\Users\DaveWitkin\.config\opencode\package.json` dependencies.
- Treat `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` as the active global OpenCode config.
- Keep all repository changes limited to Conductor/docs unless the build agent is executing this track.

### Definition of Done

- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` has a timestamped backup.
- The `plugin` array in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` no longer contains `@franlol/opencode-md-table-formatter@0.0.3`.
- OpenCode config parses successfully with `opencode debug config`.
- A verification command confirms the removed plugin string is absent from the active global config.
- `docs/reference/opencode-configuration.md` is updated so the active plugin count and plugin list no longer claim the markdown table formatter is active.
- Rollback instructions are recorded in the handover.

## Background and Current State

The active config reference at `docs/reference/opencode-configuration.md` says global config is sourced from `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`, and that no project-level OpenCode config exists for this repository. The same reference currently lists `@franlol/opencode-md-table-formatter@0.0.3` as an active plugin.

Target active config excerpt currently observed:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "opencode-snippets@1.8.0",
    "@zenobius/opencode-skillful",
    "oc-codex-multi-auth",
    "opencode-ignore@1.1.0",
    "opencode-mystatus",
    "@franlol/opencode-md-table-formatter@0.0.3",
    "@tarquinen/opencode-dcp@latest"
  ],
  "permission": {
    ...
  }
}
```

`C:\Users\DaveWitkin\.config\opencode\package.json` currently lists only these dependencies:

```json
{
  "dependencies": {
    "@opencode-ai/plugin": "1.2.26",
    "opencode-antigravity-auth": "^1.2.9-beta.1",
    "opencode-mystatus": "^1.2.2",
    "opencode-snippets": "1.8.0"
  }
}
```

This suggests disabling the plugin is primarily a `plugin` array edit, not a package removal.

## Files In Scope

Implementation files:

- `C:/Users/DaveWitkin/.config/opencode/opencode.jsonc` — remove exactly one plugin array entry.
- `docs/reference/opencode-configuration.md` — update active plugin count and plugin list.

Generated safety artifact:

- `C:/Users/DaveWitkin/.config/opencode/opencode.jsonc.backup-disable-md-table-formatter-<yyyyMMdd-HHmmss>` — timestamped backup created before editing.

Conductor tracking files:

- `.conductor/tracks/20260502-disable-md-table-formatter-plugin/spec.md`
- `.conductor/tracks/20260502-disable-md-table-formatter-plugin/plan.md`
- `.conductor/tracks/20260502-disable-md-table-formatter-plugin/metadata.json`
- `.conductor/tracks-ledger.md`

## Expected Config Change

Only remove this exact line from the active `plugin` array:

```jsonc
    "@franlol/opencode-md-table-formatter@0.0.3",
```

Expected resulting plugin array:

```jsonc
  "plugin": [
    "opencode-snippets@1.8.0",
    "@zenobius/opencode-skillful",
    "oc-codex-multi-auth",
    "opencode-ignore@1.1.0",
    "opencode-mystatus",
    "@tarquinen/opencode-dcp@latest"
  ],
```

## Validation Strategy

Use command-line validation before and after the edit:

- Confirm target string exists before editing.
- Copy a backup before editing.
- Parse active OpenCode config after editing.
- Confirm target string is absent from active config.
- Confirm documentation references no longer identify the table formatter as active.

## Rollback Strategy

If parsing fails, OpenCode startup fails, or the user wants the plugin restored, copy the timestamped backup over the active config:

```powershell
$latest = Get-ChildItem "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-disable-md-table-formatter-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $latest.FullName "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Force
opencode debug config 2>$null | Select-String -Pattern '"plugin"|md-table-formatter'
```

Expected rollback result: `md-table-formatter` appears again in the debug/config output or active config text, and OpenCode config parses without errors.
