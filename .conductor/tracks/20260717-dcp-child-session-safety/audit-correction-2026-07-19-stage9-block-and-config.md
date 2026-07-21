# Audit Correction - Hard-Limit BLOCK + Config-Wired forceChildToolDeny (Stage 9 reopen, 2026-07-19)

**Track:** 20260717-dcp-child-session-safety
**Trigger:** Prior report admitted two unmet required behaviors (A: hard-limit "block" only detected/nudged; B: forceChildToolDeny not config-wired). Both are now genuinely implemented and tested. No docs edited this pass.

## Item A - Hard-limit BLOCK (fail-fast) implemented
**Hook contract finding:** `experimental.chat.messages.transform` is triggered with `yield* plugin.trigger(...)` in `packages/opencode/src/session/prompt.ts:1255` (the main request path). The `Plugin.trigger` runner (`packages/opencode/src/plugin/index.ts:280`) propagates hook errors as failed Effects (`yield* Effect.promise(async () => fn(...))`). Therefore a hook THROW propagates and aborts the model request.

**Implementation (DCP `lib/hooks.ts` chat-message transform):** when `isContextOverLimits(...).overMaxLimit` is true AND a compress nudge was already delivered on a prior turn (`state.nudges.contextLimitAnchors.size > 0` => nudge ignored), the hook persists a content-minimized durable `generateHandoff` to `state.compressionBackup`, emits `context_still_over_limit` + `nudge_ignored` telemetry, and THROWS `__DCP_HARD_LIMIT_BLOCK__` BEFORE destructive pruning -> the request is aborted (block / fail-fast / restart). Originals are preserved (no destructive prune on this path); the compress tool remains the proactive transactional path. The first-time over-limit case still nudges (no throw) to give the model a chance to compress.

**Latent bug fixed:** `isContextOverLimits` returns `{ overMaxLimit, overMinLimit }` (an object); the prior over-limit checks used it as a boolean (always truthy). Both the early BLOCK and the late telemetry path now use `.overMaxLimit`.

**Test:** `tests/integration/plugin-wiring.test.ts` "hard-limit BLOCK aborts the request ..." drives the actual messages.transform hook (over limit + prior nudge) -> asserts it throws `/__DCP_HARD_LIMIT_BLOCK__/`, handoff persisted, originals preserved.

## Item B - Config-wired forceChildToolDeny (compatibility rollback switch)
**Authoritative schema source:** added `force_child_tool_deny: Schema.optional(Schema.Boolean)` to the `experimental` Effect Schema struct in `packages/core/src/v1/config/config.ts` (default absent => eligible). This is the schema/type source of truth (not hand-edited generated output); no JSON-schema generation script exists in this checkout, so nothing else to regenerate - the type propagates via the Effect Schema (confirmed by typecheck).

**Call-site wiring:** `packages/opencode/src/tool/task.ts` now passes `forceChildToolDeny: cfg.experimental?.force_child_tool_deny === true` to `buildChildSessionPermission`. The compatibility switch is now reachable through the real config/call path (opencode.jsonc `experimental.force_child_tool_deny: true` => legacy blanket deny of every primary_tool for Task children; default false => eligible).

**Tests:** new `packages/opencode/test/agent/child-compression-config-parse.test.ts` (3 tests) proves the authoritative Schema parses `experimental.force_child_tool_deny` (absent => eligible; true => compatibility-deny; false => eligible) and that the task.ts-style resolution distinguishes eligible vs compatibility-deny, alongside the existing eligible/explicit-deny/compatibility-deny behavior tests in `child-compression-eligibility` + `child-compression-compatibility`.

## Verification (this pass)
- DCP full suite: **128 pass / 0 fail, exit 0** (was 127; +1 block test).
- DCP `bun run build`: exit 0, `dist/index.js` 285.74 KB.
- Core `bun run typecheck`: exit 0. Core config schema test: **15/15**.
- OpenCode `bun run typecheck`: exit 0. OpenCode permission + parse suites: **37/37** (34 + 3 parse tests).

No docs edited (Stage 9 will reconcile). No commit/push; isolated temp storage; no content reads. Both previously-admitted unmet behaviors are now real product behavior with integration/parse tests.