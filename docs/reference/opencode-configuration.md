# OpenCode Configuration Reference

**Last updated:** 2026-07-18

> **See also:** [Workflow: Update OpenCode Default Models](../workflows/opencode-model-update.md) — step-by-step guide for changing models.

## Machine Policy: Global JSONC Only

> **Mandatory:** On Dave's machine, `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` is the one and only global configuration file. Do not create or edit a sibling `opencode.json`. Although OpenCode supports both formats generically, having both global files causes silent merging and configuration drift.
>
> If `C:\Users\DaveWitkin\.config\opencode\opencode.json` exists: stop, back up both files, merge unique settings into `opencode.jsonc`, validate the effective configuration with `opencode debug config`, and remove the JSON file. Project-level configs may still use either extension when explicitly required by that project.
## Config File Locations

OpenCode supports config in JSON or JSONC (JSON with Comments) format. Config files are **merged** (not replaced) — later sources override earlier ones for conflicting keys.

### Precedence Order (lowest → highest)

| # | Source                                        | Path                                                     | Status        |
|---|-----------------------------------------------|----------------------------------------------------------|---------------|
| 1 | Remote (`.well-known/opencode`)                 | Fetched from provider                                    | Unknown       |
| 2 | Global config (`~/.config/opencode/opencode.jsonc`) | `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`    | ✅ ACTIVE     |
| 3 | Custom (`OPENCODE_CONFIG` env var)              | —                                                        | Not set       |
| 4 | Project config (`opencode.jsonc` in project root)   | `C:\development\opencode\opencode.jsonc`                 | ❌ Missing    |
| 5 | `.opencode/` directory in project               | `C:\development\opencode\.opencode\`                     | ❌ Missing    |
| 6 | Inline (`OPENCODE_CONFIG_CONTENT` env var)      | —                                                        | Not set       |

**Since no project-level config exists, everything runs from the global config directory.**

> **Note (2026-03-25):** `opencode.json` was consolidated into `opencode.jsonc`. The old file was deleted (backup at `opencode.json.bak`). Settings unique to `opencode.json` (Slack MCP server) were merged into `opencode.jsonc`. The `keybinds` section was removed — those keys (`input_newline`, `input_submit`) are not recognized by OpenCode's config resolver.

> **Resolved drift (2026-07-18):** A reappeared `C:\Users\DaveWitkin\.config\opencode\opencode.json` was found merging at runtime. Its 17 unique OpenAI model definitions were backed up and consolidated into canonical `opencode.jsonc`, then the duplicate JSON file was removed. Effective plugins, providers, defaults, OpenAI models, and OpenCode Go authentication were verified afterward. See [Rotate the Default OpenCode Go Workspace Key](../workflows/opencode-go-key-rotation.md) for the independent credential-switch workflow.

---

## Active Config Files

### `opencode.jsonc` (Main)
**Path:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

This is the **only** config file. Contains everything:

- **OpenCode version:** v1.15.10 (verified 2026-07-06)
- **Plugins:** 6 plugins (skillful, codex-multi-auth, ignore, dcp, tokenscope, scheduler)
  - `@zenobius/opencode-skillful` - Lazy skill discovery and on-demand loading
  - `oc-codex-multi-auth` - Multi-provider auth (successor to oc-chatgpt-multi-auth)
  - `opencode-ignore@1.1.0` - File ignore patterns
  - `@tarquinen/opencode-dcp@latest` - Dynamic Context Pruning (hooks `tool.execute.before`)
  - `@ramtinj95/opencode-tokenscope@latest` - token usage analysis
  - `opencode-scheduler` - scheduled OpenCode jobs
- **Permissions:** Explicit allow rules for tools, skills, bash, etc.
- **Providers:**
  - `google` - Gemini models via local proxy (2.5-flash, 2.5-pro, 3-flash-preview, 3-pro-preview) + blacklist of unused models
  - `openai` - GPT model variants with reasoning effort levels (none/low/medium/high/xhigh)
  - `moonshot` - Kimi K2.5 and Moonshot V1 models (currently disabled)
  - `zai-coding-plan` - GLM-5.2 default model with `reasoningEffort: high`, variants `none`/`high`/`max` (`max` is opt-in)
  - `opencode-go` - OpenCode-hosted fallback models with provider timeout settings
- **Default agent:** `01-Planner`
- **Small model:** `zai-coding-plan/glm-5.2` (default high thinking)
- **Default model:** `zai-coding-plan/glm-5.2` (default high thinking)
- **Autoupdate:** enabled
- **Snapshot:** enabled
- **Disabled providers:** google-vertex, google-vertex-anthropic, moonshot, go-tiberius, go-dave
- **MCP servers:**
  - Playwright (disabled)
  - Chrome DevTools (disabled)
  - **Slack** (disabled)

### `tui.json` (TUI Settings — 8 lines)
**Path:** `C:\Users\DaveWitkin\.config\opencode\tui.json`

- **Theme:** `opencode`
- **Leader key:** `ctrl+o`
- **Tool details keybind:** `<leader>d`

---

## Agents, Commands, and Skills

All loaded from the **global config directory** (since no project-level `.opencode/` exists):

| Type       | Location                                                          |
|------------|-------------------------------------------------------------------|
| Agents     | `C:\Users\DaveWitkin\.config\opencode\agent\`                    |
| Commands   | `C:\Users\DaveWitkin\.config\opencode\command\`                  |
| Skills     | `C:\Users\DaveWitkin\.config\opencode\skill\`                     |
| Plugins    | Loaded via npm from `opencode.jsonc` `plugin` array               |

---

## Environment Variables

See [environment-variables.md](./environment-variables.md) for the full list of Windows user-level env vars set for OpenCode.

Key env vars:
- `OPENCODE_ENABLE_EXA=1` — Enables websearch tool (Exa AI)
- Google Gemini API keys are configured in the Gemini proxy, not as env vars

---

## How to Add Project-Level Config

If you want project-specific overrides, create either:
- `C:\development\opencode\opencode.json` — for JSON config
- `C:\development\opencode\opencode.jsonc` — for JSONC (with comments)

Project config will **override** global config for conflicting keys while preserving non-conflicting global settings.

---

## Backup

A backup of an older config exists at:
- `C:\Users\DaveWitkin\.config\opencode\opencode.json.backup-20260130-101943.json` (historical; do not restore as the global config)
