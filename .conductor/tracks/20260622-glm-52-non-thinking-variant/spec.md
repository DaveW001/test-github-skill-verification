# Spec: GLM 5.2 Non-Thinking Variant

## Goal / Outcome

Enable a `none` reasoning variant for GLM 5.2 (`zai-coding-plan/glm-5.2`) in OpenCode so Dave can toggle thinking OFF via Ctrl+T, selecting the `none` reasoning level - all while keeping a single model named GLM-5.2 (no separate alias).

This saves token burn on routine tasks where thinking is unnecessary.

## Background - The Root Cause (verified against `anomalyco/opencode` `dev` source)

Two hardcoded mechanisms in OpenCode currently prevent non-thinking mode for GLM-5.2:

1. **Variant computation (`transform.ts:690-695`):** GLM-5.2 on `@ai-sdk/openai-compatible` gets ONLY `{high, max}` computed variants. No `none` variant is generated. This is why the Ctrl+T menu only offers high/max.

2. **Forced thinking (`transform.ts:1112-1120`):** The `options()` function unconditionally injects `thinking: { type: "enabled", clear_thinking: false }` for any provider whose ID contains `"zai"` or `"zhipuai"` (and `zai-coding-plan` matches). This fires regardless of variant.

### Why the fix works

Config-supplied variants **merge** with computed variants (`provider.ts:1461`, deep-merge via remeda). Adding a `none` variant yields `{high, max, none}` - three options in the Ctrl+T menu.

At request-assembly time (`session/llm/request.ts:91`), the variant has the **highest precedence** in the merge chain:
```
mergeOptions(mergeOptions(mergeOptions(base, model.options), agent.options), variant)
```
So a `none` variant with `thinking: { type: "disabled" }` overrides the base's forced `thinking: { type: "enabled" }`, producing a final payload of `{ type: "disabled", clear_thinking: false }`.

The `zai-coding-plan` provider is already known to OpenCode (built-in), so we only need to add the `models.glm-5.2.variants.none` overlay in user config - no `npm`, `name`, `options`, etc. need to be re-declared (they fall through to the built-in defaults).

## Requirements

- [x] Add a `provider.zai-coding-plan.models.glm-5.2` block to `opencode.jsonc` with a `none` variant that sets `thinking: { type: "disabled" }`
- [x] The `none` variant must be selectable via Ctrl+T (reasoning level menu)
- [x] Config-supplied variant must merge cleanly - built-in `{high, max}` must be preserved alongside `none`
- [x] All built-in capabilities/cost/limits for GLM-5.2 must be preserved (no accidental override via the fallback chain)
- [x] One model only: `zai-coding-plan/glm-5.2` - no `-lite` alias or separate model ID
- [x] Timestamped backup of `opencode.jsonc` before editing
- [x] JSONC syntax validated after edit (comments preserved)

## Non-Requirements

- **Do NOT create a separate model alias** (e.g. `glm-5.2-lite`). User explicitly rejected this approach.
- **Do NOT define a custom providerID** (e.g. `glm-direct`) to dodge the forced-thinking guard. The variant override is sufficient and simpler.
- **Do NOT change the global `model` or `small_model` settings.** They stay `zai-coding-plan/glm-5.2`.
- **Do NOT touch any agent files or permissions.**
- **Do NOT restart OpenCode as part of this plan.** Restart is the user's responsibility.
- Small-model calls (summarization, etc.) will continue to use thinking ON - this is an opencode architectural limitation (`smallOptions()` ignores the variant selection). Accepted.

## Acceptance Criteria

### Build-Agent Verification (deterministic, CLI-checkable - all must be green)

- [x] Timestamped backup exists at `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.backup-YYYYMMDD-HHMMSS` with byte-identical content to pre-edit source
- [x] `opencode.jsonc` contains the literal nesting `provider > zai-coding-plan > models > glm-5.2 > variants > none > thinking > type: "disabled"` (verifiable by ordered substring search)
- [x] `Test-JsonC` (custom JSONC parser that strips `//` and `/* */` comments) returns `True` for the new file
- [x] All 6 existing provider blocks (`google`, `openai`, `moonshot`, `openrouter`, `go-dave`, `go-tiberius`) are byte-identical between backup and new file
- [x] Global `"model": "zai-coding-plan/glm-5.2"` and `"small_model": "zai-coding-plan/glm-5.2"` are unchanged
- [x] `Compare-Object` diff against backup shows ONLY the inserted `zai-coding-plan` block and a trailing comma on the previous `go-tiberius` close - no other additions, no removals
- [x] If `opencode` CLI is in PATH, `opencode --version` loads the config without parse errors
- [x] `.conductor/tracks/20260622-glm-52-non-thinking-variant/metadata.json` is updated to `status: complete` and `progress.percentage: 100`
- [x] `.conductor/tracks.md` row for this track shows `complete` and today's date in the `Completed` column
- [x] `.conductor/tracks-ledger.md` entry has moved from "Active Tracks" to "Completed Tracks" with `(Completed: 2026-06-22)` tag
- [x] Execution log written to `C:\development\opencode\.conductor\tracks\20260622-glm-52-non-thinking-variant\execution-log-2026-06-22.md`

### User Verification (requires OpenCode restart - NOT in build agent scope)

- [ ] After restart, Ctrl+T menu shows three variants for GLM-5.2: `none`, `high`, `max`
- [ ] After restart, selecting `none` produces API requests without thinking content (verify via DevTools network tab or proxy log)

## Fallback Plan (if Z.ai rejects `thinking: { type: "disabled" }`)

These steps require live API testing, which is the user's responsibility after restart (not in `plan.md`):

1. Try adding `"clear_thinking": true` to the variant: `"none": { "thinking": { "type": "disabled", "clear_thinking": true } }`
2. If still rejected, escalate to custom-providerID approach: define a provider with ID NOT containing `"zai"`/`"zhipuai"` (e.g. `"glm-direct"`) pointing at the same Z.ai baseURL. This bypasses the forced-thinking guard entirely.

Either fallback will require a new conductor track because the change involves more than a one-block insert (full provider definition + providerID logic).