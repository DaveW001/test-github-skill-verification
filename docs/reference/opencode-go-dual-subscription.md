# OpenCode Go Dual-Subscription Behavior

## What You See
When selecting a model in OpenCode Desktop or running `opencode models` in the CLI, you will only see a **single provider entry** labeled `opencode-go` (or `OpenCode Go`). You will not see separate entries for `go-dave` and `go-tiberius`, even though both are configured in `opencode.jsonc`.

## Why This Happens
OpenCode's model resolver groups providers into a single namespace when they share:
1. The same `baseURL` (`https://opencode.ai/zen/go/v1`)
2. The same SDK (`@ai-sdk/openai-compatible`)

This merging is intentional. It prevents duplicate models from appearing in the UI picker and consolidates the catalog under a unified `opencode-go/` prefix (e.g., `opencode-go/qwen3.6-plus`, `opencode-go/glm-5.1`). The `name` field in the config (`"OpenCode Go (Dave)"` / `"OpenCode Go (Tiberius)"`) is used internally for logging and config parsing, but the UI/CLI collapses them into one provider.

## How Load Balancing & Failover Works
Even though they appear as one provider, **both API keys are active and loaded** at startup. OpenCode uses them for:
- **Rate-limit failover:** If one key hits a rate limit or quota cap, OpenCode automatically falls back to the other key for the same model.
- **Quota distribution:** Requests are distributed across both subscriptions based on availability and authentication success.
- **Key resolution:** The resolver attempts authentication with the configured keys in order. If the first fails (e.g., expired token, quota exceeded), it retries with the second.

You do not lose access to either subscription; you simply see a unified model list in the UI.

## How to Validate It Is Working
To confirm both subscriptions are active and handling requests:

### 1. Check Startup Logs
OpenCode logs provider resolution at startup. Run `opencode --print-logs` in a terminal, or inspect Desktop logs at:
```
%LOCALAPPDATA%\ai.opencode.desktop\logs\opencode-desktop_*.log
```
Look for lines indicating both `go-dave` and `go-tiberius` keys were loaded and resolved successfully.

### 2. CLI Smoke Test
You can explicitly target the merged provider to verify endpoint health:
```powershell
$env:OPENCODE_SERVER_PASSWORD = $null
$env:OPENCODE_SERVER_USERNAME = $null
$env:OPENCODE_CLIENT = $null
opencode run -m opencode-go/qwen3.6-plus "hello"
```
*(Note: Unset server auth env vars if `opencode run` throws "Session not found" due to known CLI bug #8502.)*

### 3. Monitor OpenCode Go Dashboard
Check the usage dashboards for both OpenCode Go subscriptions. You should see token/request counts incrementing across both accounts over time, confirming that load distribution and failover are functioning.

## Configuration Reference
The explicit `models` block was added to both providers in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` to force `qwen3.6-plus` visibility after the OpenCode Zen free tier was deprecated. This workaround ensures the model appears in the merged catalog even if dynamic registry updates lag.

```jsonc
"go-dave": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "OpenCode Go (Dave)",
  "options": { "baseURL": "https://opencode.ai/zen/go/v1", "apiKey": "{env:OPENCODE_GO_DAVE_API_KEY}" },
  "models": {
    "qwen3.6-plus": { "name": "qwen3.6-plus" }
  }
},
"go-tiberius": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "OpenCode Go (Tiberius)",
  "options": { "baseURL": "https://opencode.ai/zen/go/v1", "apiKey": "{env:OPENCODE_GO_TIBERIUS_API_KEY}" },
  "models": {
    "qwen3.6-plus": { "name": "qwen3.6-plus" }
  }
}
```

## Related Context
- Prior troubleshooting track: `20260519-opencode-desktop-config-troubleshoot`
- OpenCode GitHub Issue #21455: Qwen 3.6 Plus Free deprecated, requesting user's access to paid version
- OpenCode GitHub Issue #8502: `opencode run` fails with "Session not found" when `OPENCODE_SERVER_USERNAME` / `OPENCODE_SERVER_PASSWORD` are set
