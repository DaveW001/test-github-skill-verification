# Spec

## Goal
Fix silent failures when OpenCode routes requests to OpenAI models (gpt-5.3-codex, gpt-5.4-mini) through the `oc-chatgpt-multi-auth` plugin. The model starts responding but the session silently falls back to the ZAI model without logging errors.

## Background
- Yesterday's track (`openai-parameter-fix`) fixed two bugs: provider package mismatch and missing `arguments` on deferred tool calls
- Both fixes are confirmed working
- Today, requests to `openai/gpt-5.3-codex` still fail silently — the model starts responding, generates tool calls, but the session falls back to `zai-coding-plan/glm-5.1`
- No ERROR-level messages appear in OpenCode logs

## Root Cause Candidates (from code audit)

### Candidate 1: SSE→JSON fallback returns raw text (HIGH probability)
**File**: `response-handler.js` lines 157-166
**Issue**: If the SSE stream lacks a `response.done` event, the handler returns raw SSE text as the response body with HTTP 200 status. The AI SDK tries to parse this as JSON and fails silently.
**Fix**: Return a proper JSON error response instead of raw SSE text.

### Candidate 2: Stream stall timeout too aggressive (MEDIUM probability)
**File**: `response-handler.js` line 116
**Issue**: Default `streamStallTimeoutMs` = 45 seconds. Complex agent responses with tool calls can pause >45s between chunks.
**Fix**: Increase timeout to 120s or make it configurable via opencode.jsonc.

### Candidate 3: gpt-5.4-mini model name lost (MEDIUM probability)
**File**: `model-map.js` — pattern matching normalizes `gpt-5.4-mini` → `gpt-5.4`
**Issue**: The "mini" qualifier is stripped. If ChatGPT backend expects `gpt-5.4-mini` as a distinct model, the request may fail.
**Fix**: Add explicit `gpt-5.4-mini` entry to model-map.

### Candidate 4: Missing diagnostic logging (enabling factor)
**Issue**: No verbose logging in the request pipeline. Failures happen silently.
**Fix**: Add configurable debug logging to request-transformer and response-handler.

## Requirements
- [ ] Patch `response-handler.js` to return proper JSON error when SSE stream has no `response.done` event
- [ ] Add `gpt-5.4-mini` to `model-map.js` to preserve the full model name
- [ ] Increase or make configurable the stream stall timeout (default ≥120s)
- [ ] Add diagnostic logging to request pipeline (configurable via env var or config)
- [ ] Test all 3 OpenAI models (gpt-5.3-codex, gpt-5.4-mini, gpt-5.4) after fixes
- [ ] Verify OpenCode logs show errors instead of silent fallbacks

## Non-Requirements
- [ ] Rewriting the SSE parser (current parser works when stream is well-formed)
- [ ] Changes to the Codex account rotation logic (accounts are healthy)
- [ ] Changes to the `arguments` fix from yesterday (confirmed working)
- [ ] Changes to OpenCode core (only plugin modifications)

## Acceptance Criteria
- [ ] OpenAI model requests produce visible errors in logs when they fail (no silent fallbacks)
- [ ] SSE fallback returns parseable JSON error, not raw text
- [ ] `gpt-5.4-mini` preserved as-is in model-map
- [ ] Stream stall timeout ≥120 seconds
- [ ] At least one OpenAI model completes a full agent loop (user message → tool calls → final response) without fallback
- [ ] All tasks in plan.md marked [x]

## Supersession Note

Superseded on 2026-05-01 by track 20260501-codex-multi-auth-upgrade. The local runtime patches documented here were reconciled against upstream oc-codex-multi-auth@6.1.8. The stream stall timeout is now preserved via CODEX_AUTH_STREAM_STALL_TIMEOUT_MS=120000 rather than source patching.
