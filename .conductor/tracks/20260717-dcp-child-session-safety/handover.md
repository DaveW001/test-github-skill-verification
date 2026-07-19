# Deployment Handover - Track 20260717-dcp-child-session-safety

Deployment, migration, security, rollback, and rollout notes for the DCP child-session safety fix.

## Universal eligibility decision (explicit, user-authorized)
**Universal eligibility**: every eligible Task-created conversational child session is DCP-eligible by default. The blanket Task-child `compress: deny` was removed in `buildChildSessionPermission` (opencode core). Eligibility is subject to capability/safety exclusions, NOT a class exclusion:
- DCP's own internal helper (compression-helper) sessions (`isInternalHelper`) are excluded (prevents recursion).
- **Explicit deny** (parent session / subagent / config) remains a hard ceiling and is never bypassed.
- Incompatible models (auto-compression allowlist default OFF), cancelled/cleanup-only, and reentrant sessions are excluded.
- Corrupt/ambiguous state fails fast to a handoff rather than destructive pruning.

User-authorized model decision: **retain `openai/gpt-5.6-luna`**; require BOTH `openai/gpt-5.6-luna` and `openai/gpt-5.6-terra` capped at integer 150000; preserve unrelated `modelMaxLimits` keys. (No agent migration to Terra.)

## Pinned SHAs / ownership
- opencode core: `C:\development\opencode-core-dcp-fix` @ `45cd8d76920839e4a7b6b931c4e26b52e1495636` (dev, MIT, anomalyco) - permission policy change in `packages/opencode/src/agent/subagent-permissions.ts`; test updates in `test/agent/child-compression-*.test.ts`, `test/tool/task.test.ts`.
- DCP plugin: `C:\development\opencode-dcp-child-fix` @ `85b6f5ceba144fee9e65eb28dc36cab1b960e418` (master, AGPL-3.0-or-later, Opencode-DCP) - registry, atomic persistence, telemetry, enforcement+handoff, getConfig API. Upstream PRs/patches owned by those orgs.

## Config backups + rollback commands
- Global config backups: `.conductor/tracks/20260717-dcp-child-session-safety/backups/2026-07-17-pre-edit/` (dcp.jsonc + 3 skill + 12 agent), `backups/2026-07-17-stage5-src/`, `backups/2026-07-17-stage5-dcp/`.
- **Rollback** strategy (per spec):
  - Core: set `forceChildToolDeny=true` at the `buildChildSessionPermission` call site to restore legacy blanket child deny (compatibility switch); do not revert unrelated permission inheritance.
  - DCP: disable enforcement/auto-compression (allowlist already default OFF), keep registry reads backward-compatible, preserve all original messages and legacy state. Persistence is non-destructive (schemaVersion defaults legacy to 1).
  - Config: restore timestamped `dcp.jsonc` backup atomically (`Copy-Item -LiteralPath -Force` + JSONC re-parse).
  - Conductor: RETAIN the pre-140K guardrail even if product rollout is rolled back.
- Rollback proof: `tests/integration/rollback.test.ts` prints `originals-preserved`, `legacy-readable`, `compatibility-deny-restored` (4/4 GREEN on disposable storage).

## Data loss prevention
**Data loss** is prevented by: blocking-pending-compression with bounded fail-fast handoff fallback; transactional compression that preserves originals + prior revision until summary validation + durable atomic commit succeed; atomic temp-file + rename persistence (no corrupt partial writes); stale-write rejection via monotonic revision. On any failure, original context is untouched and a content-minimized handoff is generated. Verified: zero original-message hash changes across enforcement/rollback/canary.

## Rollout order
1. Merge opencode-core permission policy (default eligibility + forceChildToolDeny compat switch).
2. Merge DCP registry/atomic-persistence/telemetry/enforcement/handoff.
3. Apply global `dcp.jsonc` exact 150K caps (already applied; Phase 4).
4. Keep Conductor guardrails (already applied; Phase 4).
5. Build DCP (`bun run build`) before live use; canary against built dist (5.4 GREEN).

## Telemetry query examples (content-free)
- Six events: `resolved_threshold`, `nudge_delivered`, `tool_unavailable`, `nudge_ignored`, `compaction_completed`, `context_still_over_limit`.
- Each carries `sessionIdHash`/`parentIdHash` (sha256, 16 hex), `providerModelKey`, `threshold`, `observedTokens`, `outcome` - NO prompt/tool-body data.
- Grep daily DCP logs: `Select-String -Pattern "TELEMETRY" <daily log>`.

## Canary / rollback commands
- Canary (against BUILT dist): `bun .conductor/tracks/20260717-dcp-child-session-safety/scripts/run_canary.mjs` with `XDG_DATA_HOME=<isolated temp>`. Report: `artifacts/canary-report.json`.
- Rollback test: `bun test tests/integration/rollback.test.ts` with `XDG_DATA_HOME=<isolated temp>`.

## Known unrelated baseline failures (not release blockers for this track)
- DCP `tests/prompts.test.ts` "system prompt overrides handle reminder tags safely": pre-existing Bun `NotImplementedError: test() inside another test()` (uses node:test `t.test()` subtests); PROVEN at pinned clean commit `85b6f5c`. Unrelated to this track's additive changes.
- opencode repo-root `bun run typecheck`: pre-existing `@opencode-ai/enterprise` `src/custom-elements.d.ts` TS1128. The `@opencode-ai/opencode` package typechecks clean (exit 0).
- opencode full `bun test --timeout 30000` did not complete within a 600s bound under isolated env (not re-run per anti-stall); targeted permission suites pass 34/34.