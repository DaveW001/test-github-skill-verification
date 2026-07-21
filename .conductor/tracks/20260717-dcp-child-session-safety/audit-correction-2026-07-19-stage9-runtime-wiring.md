# Audit Correction - False-Positive Helper-Only Validation; Real Runtime Wiring Added (2026-07-19)

**Track:** 20260717-dcp-child-session-safety
**Trigger:** Post-doc validation (Stage 9) found deliverable regressions: the DCP plugin `index.ts` still constructed ONE shared `SessionState` and passed it to every hook; `SessionStateRegistry`, `enforceContextLimit`, durable handoff, and telemetry transitions were helper-only (exported/tested directly but NOT wired through the actual runtime request/hook flow). The README documented active behavior, exposing the gap. Prior Stage 5/7/8 validation that marked 3.1-3.6 complete based on existence/helper tests was a **false positive**.

**Action (reopened Stage 5; product code, not docs):** wired the actual runtime. No weakening/skips.

## Wiring added (real production paths)
1. **Per-session registry resolution in every relevant hook/tool/event.** `index.ts` no longer creates a shared `state`; it defines `resolveState = (sessionId) => sessionStateRegistry.getOrCreate(sessionId)` and passes it to all hooks + the compress tool. `lib/hooks.ts` handlers (chat-message-transform, system-prompt, command-execute, event) resolve `state = resolveState(sessionID)` per invocation. Handler factories are backward-compatible (`SessionState | resolver`, normalized via `asResolver`) so legacy single-session tests still pass. The compress tool (`ToolContext.resolveState` + `prepareSession` rebind) resolves the exact sessionID state per compress call. Parent/siblings/nested children receive independent state objects; no mutable global-active fallback under concurrency.
2. **Hard-limit enforcement + durable handoff wired into the runtime pre-request hook.** The chat-message transform now detects over-limit (`isContextOverLimits`) on the prepared context, emits the relevant telemetry, and when still over limit persists a content-minimized durable `generateHandoff` to `state.compressionBackup` (originals never mutated). The compress pipeline remains the transactional path.
3. **Six content-free telemetry transitions wired into real runtime flow** via `logger.trackStateTransition` (once per session+transition, sha256-redacted fields): `resolved_threshold`, `nudge_delivered` (on nudge-anchor growth), `tool_unavailable` (compress denied), `nudge_ignored` (prior anchors + still over), `compaction_completed` (event hook on compress completed), `context_still_over_limit` (over-limit + handoff).
4. **Per-session serialized/race-safe persistence** retained (atomic temp+rename, schemaVersion, revision) and now keyed by the per-session state resolved in hooks.
5. **allowSubAgents** remains a real config path used in hooks/index; compatibility deny = `compress.permission = "deny"` (real config), no internal-only switch on the DCP side.
6. **Integration test driving the actual plugin wiring** (`tests/integration/plugin-wiring.test.ts`, 4 tests): wires the real hook factories with the real registry resolver (exactly as `index.ts`) and drives them concurrently with parent/sibling/nested sessionIDs, proving independent per-session state, system-prompt per-session caching, event-handler per-session + compaction telemetry, and the enforcement/handoff path.

## Verification (this pass)
- DCP full suite: **127 pass / 0 fail, exit 0** (was 123; +4 wiring tests).
- DCP `bun run build`: exit 0, `dist/index.js` 284.71 KB.
- DCP `bun run typecheck` (tsc --noEmit): exit 0.
- OpenCode targeted permission suites: **34 pass / 0 fail**; opencode package `bun run typecheck`: exit 0. (No core changes this pass.)

## Plan/disposition
Plan tasks 3.1-3.6 (and the runtime-wiring aspect of 3.4/3.5) are now GENUINELY complete (production-wired, not helper-only). No prior `[x]` required unchecking - the previously-unsupported completion claims are now supported by real runtime wiring + the plugin-wiring integration test. Product docs (README) were NOT edited this pass (Stage 9 will reconcile docs after code is proven). No commit/push; no live DB/state/log writes; isolated temp storage for tests.