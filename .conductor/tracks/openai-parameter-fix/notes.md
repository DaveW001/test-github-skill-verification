# Track Notes: openai-parameter-fix

## Summary
Resolved OpenAI parameter mismatch errors by explicitly pinning the `@ai-sdk/openai` provider package in `opencode.jsonc`. Single-variable change, all validation gates passed.

## Evidence
- User experienced "bad parameter" errors on GPT-5.3, 5.4, and 5.5 models on Apr 27, 2026.
- Error evidence in interactive Desktop session DB (not in headless logs).
- Error was intermittent; resolved by time of fix but likely to recur without the provider pin.

## Change Made
- **File:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- **Change:** Added `"npm": "@ai-sdk/openai"` at line 140 inside the `openai` provider block.
- **Rationale:** Forces OpenCode to use the official OpenAI SDK with Responses API support, preventing parameter mismatches (`max_tokens` vs `max_completion_tokens`, `reasoning_effort`, etc.) that occur with `@ai-sdk/openai-compatible`.

## Validation Results
| Gate                    | Result |
| ----------------------- | ------ |
| A – Syntax              | ✅ PASSED |
| B – Startup             | ✅ PASSED |
| C – Provider Resolution | ✅ PASSED |
| D – Behavior (3 models) | ✅ PASSED |
| E – Regression          | ✅ PASSED |

## Rollback State
- Config backup: `opencode.jsonc.backup-20260428-094622-openai-fix`
- Cache backup: `opencode-cache-backup-20260428-094635`
- Rollback doc: `.conductor/tracks/openai-parameter-fix/rollback.md`

## Recurrence (Phase 6 Follow-Up)
- **Error Recurred:** The user continued to encounter intermittent `Missing required parameter: 'input[57].arguments'` errors even after pinning `@ai-sdk/openai`.
- **Root Cause Identified:** The `opencode-tool-search` plugin defers tool descriptions (`[d]`) to save context. When the LLM calls a tool, it sometimes omits the arguments entirely. The Vercel AI SDK parses this as `args = undefined`. In subsequent conversational turns, when `oc-chatgpt-multi-auth` intercepts OpenCode's `ai-sdk` request to format it for the ChatGPT Responses API, `undefined` arguments are stripped from the JSON payload for historical `function_call` messages. The ChatGPT backend strictly requires `arguments` to exist.
- **Fix Applied:** Modified `C:\Users\DaveWitkin\.cache\opencode\packages\oc-chatgpt-multi-auth@5.4.4\node_modules\oc-chatgpt-multi-auth\dist\lib\request\request-transformer.js`. Specifically, updated the `filterInput` function to ensure that if `item.type === "function_call"` and `item.arguments` is missing, it explicitly sets `item.arguments = "{}"`.

## Side Discovery
- `verify.md` command has a pre-existing frontmatter syntax error (unrelated, does not block this fix).
