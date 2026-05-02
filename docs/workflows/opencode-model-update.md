# Workflow: Update OpenCode Default Models

**Last updated:** 2026-04-25
**Owner:** Dave Witkin

## Overview

This workflow covers changing the default build model, plan agent model, and/or small model in your OpenCode configuration.

## Files Involved

| File                                                       | Purpose                                      |
| ---------------------------------------------------------- | -------------------------------------------- |
| `~/.config/opencode/opencode.jsonc`                        | Main config — `model`, `small_model`, agents |
| `C:\development\opencode\.opencode\model-tiers.json`       | Agent routing tiers (low/mid/high models)    |
| `~/.local/share/opencode/auth.json`                        | Provider credentials (read-only reference)   |
| `~/.config/opencode/agent/*.md`                            | Per-agent model overrides (check these too)  |

## Model Configuration Keys

| Key in `opencode.jsonc`   | What it controls                                   | Example                          |
| ------------------------- | -------------------------------------------------- | -------------------------------- |
| `"model"`                 | Default build model (Build mode)                   | `"zai-coding-plan/glm-5.1"`      |
| `"small_model"`           | Lightweight tasks (titles, summaries)              | `"openai/gpt-5.4-mini"`          |
| `"agent"."plan"."model"`  | Plan agent model (Plan mode)                       | `"openai/gpt-5.3-codex"`         |
| `"agent".<name>."model"`  | Any custom agent override                          | `"zai-coding/glm-4.7"`           |

## Model ID Format

All model IDs use the format: `provider_id/model_id`

Examples:
- `zai-coding-plan/glm-5.1` — Z.AI Coding Plan, GLM 5.1
- `openai/gpt-5.3-codex` — OpenAI via OAuth, GPT 5.3 Codex
- `openai/gpt-5.4-mini` — OpenAI via OAuth, GPT 5.4 Mini
- `google/gemini-2.5-flash` — Google via local proxy, Gemini 2.5 Flash
- `openrouter/qwen/qwen3.6-plus:free` — OpenRouter, Qwen 3.6 Plus (free tier)

To discover valid model IDs:
1. Run `/models` in the OpenCode TUI to see available models
2. Check `auth.json` for registered provider IDs
3. Check the [OpenCode Providers docs](https://opencode.ai/docs/providers/) for built-in providers

---

## Step-by-Step Workflow

### 1. Identify the Target Model

- [ ] Confirm the exact `provider_id/model_id` string
- [ ] Verify the provider credentials exist in `auth.json` (or run `/connect` to add them)
- [ ] Check if the model requires any special provider config (e.g., custom `baseURL`)

### 2. Create a Backup

```powershell
Copy-Item "$env:USERPROFILE\.config\opencode\opencode.jsonc" `
  "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
```

### 3. Edit `opencode.jsonc`

Edit the file at `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`:

**For default build model:**
```jsonc
"model": "provider_id/model_id",
```

**For plan agent:**
```jsonc
"agent": {
  "plan": {
    "model": "provider_id/model_id"
  }
},
```

**For small model (titles, lightweight tasks):**
```jsonc
"small_model": "provider_id/model_id",
```

**For any custom agent:**
Check `~/.config/opencode/agent/*.md` files for `model:` frontmatter lines.

### 4. Update `model-tiers.json` (If Applicable)

If the new model should participate in agent routing tiers, update:
`C:\development\opencode\.opencode\model-tiers.json`

```json
"tiers": {
  "low": {
    "models": [
      "zai-coding-plan/glm-5.1",   // <-- update model IDs here
      "zai-coding/glm-4.7",
      "openrouter/kimi-2.5"
    ]
  }
}
```

### 5. Validate

Run from PowerShell:
```powershell
opencode debug config 2>$null | Select-String -Pattern '"model"|"small_model"'
```

**Expected:** All model values resolve to the new IDs with no parse errors.

### 6. Verify in TUI

1. Start or restart OpenCode
2. Check the model indicator (lower-right) shows the new default model
3. Press `Tab` to switch modes — verify plan mode uses the correct model
4. Run `/models` to confirm all models appear in the selection list
5. Send a test prompt to verify the model responds correctly

### 7. Update Reference Documentation

Update the model table in:
`C:\development\opencode\docs\reference\opencode-configuration.md`

---

## Troubleshooting

| Symptom                               | Likely Cause                                       | Fix                                                 |
| ------------------------------------- | -------------------------------------------------- | --------------------------------------------------- |
| Model not in `/models` list           | Provider not authenticated or model ID wrong       | Run `/connect` for the provider; verify model ID    |
| "Model not found" error on startup    | Typo in model ID or provider not loaded            | Check `auth.json` for provider; verify ID format    |
| Config parse error                    | JSON syntax error (missing comma, trailing comma)  | Validate JSON; restore from backup                  |
| Wrong model active after edit         | Project-level config overriding global             | Check for `opencode.json` in project root           |
| Agent still uses old model            | Agent `.md` file has explicit `model:` override    | Edit the agent file in `~/.config/opencode/agent/`  |

## Rollback

```powershell
# List backups
Get-ChildItem "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-*"

# Restore most recent backup
$latest = Get-ChildItem "$env:USERPROFILE\.config\opencode\opencode.jsonc.backup-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $latest.FullName "$env:USERPROFILE\.config\opencode\opencode.jsonc" -Force
```

## Current Model Configuration

*Last updated: 2026-04-25*

| Role            | Model ID                     | Provider              | Auth Method  |
| --------------- | ---------------------------- | --------------------- | ------------ |
| Default Build   | `zai-coding-plan/glm-5.1`    | Z.AI Coding Plan      | API Key      |
| Plan Agent      | `openai/gpt-5.3-codex`       | OpenAI (ChatGPT Team) | OAuth        |
| Small Model     | `openai/gpt-5.4-mini`        | OpenAI (ChatGPT Team) | OAuth        |
| CoVe Verifier   | `zai-coding/glm-4.7`         | Z.AI Coding           | API Key      |
| CoVe Orchestrator | `openai/gpt-5.3-codex`     | OpenAI (ChatGPT Team) | OAuth        |
