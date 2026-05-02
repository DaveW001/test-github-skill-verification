# Plan

## Phase 1 - Response Handler Fix (HIGH priority)
- [x] Read `response-handler.js` lines 150-170 (SSE fallback section)
- [x] Patch: When no `response.done` event found, return JSON error `{ error: { message: "SSE stream ended without response.done", type: "stream_error", code: "stream_error" } }` with status 502 instead of raw SSE text with status 200
- [x] Verify: JSON response is parseable by AI SDK

## Phase 2 - Model Map Fix (MEDIUM priority)
- [x] Read `model-map.js` to find the pattern-matching section
- [x] Add explicit entry: `"gpt-5.4-mini": "gpt-5.4-mini"` before the pattern fallback
- [x] Verify: `gpt-5.4-mini` is no longer normalized to `gpt-5.4`

## Phase 3 - Stream Stall Timeout (MEDIUM priority)
- [x] Read `response-handler.js` line 116 (timeout constant)
- [x] Increase default `streamStallTimeoutMs` from 45000 to 120000
- [x] Preserve existing configurability via `CODEX_AUTH_STREAM_STALL_TIMEOUT_MS`
- [x] Verify: Timeout value is respected

## Phase 4 - Diagnostic Logging (enabling)
- [x] Add `DEBUG_CHATGPT_PROXY` environment variable check at top of `response-handler.js`
- [x] When enabled, log: SSE stream events received, conversion start/success, and missing terminal event failures
- [x] Add similar logging to `request-transformer.js` for: original model, normalized model name, input message count, tool count
- [x] Verify: Logs appear when env var is set

## Phase 5 - Validation
- [ ] Test with `openai/gpt-5.3-codex` (plan agent model) — full agent loop
- [ ] Test with `openai/gpt-5.4-mini` (small model) — tool_search call
- [x] Module-level validation: syntax checks, model preservation, timeout default, parseable JSON 502 for missing `response.done`, and `DEBUG_CHATGPT_PROXY` logs
- [ ] Confirm no silent fallbacks occur in live OpenCode Desktop testing

## Phase 6 - Cleanup & Documentation
- [x] Update this plan with results
- [x] Update metadata.json with current status
- [x] Update tracks-ledger.md

## Implementation Notes
- Patched cached runtime package: `C:\Users\DaveWitkin\.cache\opencode\packages\oc-chatgpt-multi-auth@5.4.4\node_modules\oc-chatgpt-multi-auth\dist\`.
- Backup created before edits: `C:\Users\DaveWitkin\.cache\opencode\packages\oc-chatgpt-multi-auth@5.4.4\codex-silent-failure-backup-20260429-124515`.
- Runtime package `main` imports the `dist/lib/**` modules, so patching those files is sufficient; `dist/index.js` does not inline the changed logic.
- Live authenticated OpenAI model validation remains pending because it requires real OpenCode/Desktop model calls.

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.

## Follow-up: Live Tool Call Validation Failure
- [x] Investigated live error `Missing required parameter: 'input[2].arguments'` from Desktop validation screenshot.
- [x] Confirmed failing item was `type: "tool_search_call"`, not `type: "function_call"`; previous arguments guard was too narrow.
- [x] Confirmed active runtime uses `requestTransformMode: "native"`, which bypassed `filterInput()` and returned the body before the old sanitizer ran.
- [x] Patched `fetch-helpers.js` with a last-mile sanitizer that adds `arguments: "{}"` to any call-like input item before both native and legacy serialization paths.
- [x] Broadened `request-transformer.js` sanitizer for legacy path parity.
- [x] Removed ESM-unsafe `require('fs').writeFileSync(...)` debug dump from `fetch-helpers.js`.
- [x] Validated captured failing body: native transform now preserves `tool_search_call` and adds `arguments: "{}"`.
- [ ] Restart OpenCode Desktop and rerun the same tool-call validation prompt.

## Temporary Mitigation
- [x] Disabled opencode-tool-search in C:\Users\DaveWitkin\.config\opencode\opencode.jsonc after live validation still failed with Invalid type for 'input[44].arguments': expected an object, but got a string instead.
- [x] Backup before disabling: C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.backup-20260429-151516-disable-tool-search.
- [ ] Restart OpenCode Desktop and validate OpenAI models without tool-search loaded.

