# Spec: DCP Protection for Task-Created Child Sessions

**Track ID:** 20260717-dcp-child-session-safety  
**Created:** 2026-07-17  
**Status:** Planned  
**Classification:** Uncertain (high-risk production/plugin/core behavior spanning two upstream repositories plus shared global agent/process configuration; exact source revisions and final test commands must be pinned in Phase 0)

## Restatement Before Tasks

### Goal / Outcome

Make every eligible OpenCode conversation—including Task-created children, concurrent children, and nested children—independently eligible for Dynamic Context Pruning (DCP), cap every exact model identity used by active agents/subagents at 150,000 tokens, and prevent Conductor stages from crossing approximately 140,000 tokens without a bounded split, handoff, compression gate, or safe restart.

### Constraints / Non-Goals

- Stage 1 creates planning artifacts only. It must not modify the live SQLite database, DCP state, DCP logs, OpenCode runtime/plugin code, or active configuration.
- Treat `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` and existing DCP state/logs as read-only evidence. Never print prompt bodies, tool payloads, credentials, or secret values.
- Do not patch generated cache bundles as the durable fix. Changes belong in pinned source checkouts and must be upstreamable; cache patching is permitted only as an explicitly approved, reversible containment experiment after source tests pass.
- Do not equate “DCP enabled” with “automatic lossy compression always runs.” Eligibility/tool availability, threshold notification, and enforcement are separate controls.
- Preserve explicit administrator/agent denials and OpenCode’s security permission ceilings. Do not broaden unrelated read/write/bash/task permissions.
- Do not assume aliases, variants, or display names match DCP keys. Runtime `providerID/modelID` observations determine exact keys.
- Do not mutate or delete historical session state during migration. Unknown/legacy state must fail closed and remain rollback-readable.

### Definition of Done

The current failure is reproduced by deterministic tests; Task children no longer receive an unconditional `compress: deny`; DCP state is keyed and persisted per child `session_id`; exact 150K limits cover every active named model identity including GPT-5.6 SOL and GPT-5.6 Tera/Terra identities actually resolved at runtime; concurrent/nested/cancelled/retried sessions remain isolated; telemetry covers all required outcomes; Conductor enforces a pre-140K bounded-stage guardrail; and rollback, migration, security, data-loss, compatibility, and end-to-end tests are green.

## Problem Statement and RCA Evidence

Current evidence shows a systemic protection gap, not an isolated oversized conversation:

- OpenCode Task child creation adds `{ "permission":"compress", "pattern":"*", "action":"deny" }`.
- All 200 audited child sessions had compression denied.
- 22 child sessions exceeded 150K tokens and had no DCP state file.
- Child sessions made zero `compress` calls.
- Current DCP startup creates one mutable session state and changes its active `sessionId`, which is unsafe for concurrent parent/child traffic and cannot provide durable per-child isolation.

Evidence sources (read-only):

- `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`
- `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc`
- `C:\Users\DaveWitkin\.config\opencode\agent\*.md` (exclude backups)
- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` and relevant project config
- `C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp\`
- `C:\Users\DaveWitkin\.config\opencode\logs\dcp\`

## Universal Enablement Decision

**Decision:** DCP should be universally *eligible* for Task-created conversational child sessions, subject to the same explicit policy and security controls as primary sessions. There is no legitimate reason to deny compression merely because a session was created by Task. The observed blanket child deny is therefore unsafe and should be removed or replaced by a configurable policy whose safe default permits DCP.

There are legitimate reasons not to enable or invoke DCP in particular sessions, but they are capability/safety exclusions—not a Task-child class exclusion:

1. DCP’s own internal compression-helper sessions, to prevent recursion/reentrancy.
2. Explicit administrator or agent policy denying compression.
3. Non-conversational, ephemeral, already-finalizing, cancelled, or cleanup-only sessions where no context will be reused.
4. Models/providers without a compatible compression tool path or with signed/reasoning payload invariants not yet proven safe.
5. A session already inside native/DCP compaction, retry recovery, or a state migration critical section.
6. Corrupt, ambiguous, or unpersistable state, where fail-fast plus generated handoff is safer than destructive pruning.

Thus, “universal” means default eligibility and protection coverage for all eligible child sessions, not unconditional automatic compression under every condition.

## Required Architecture

### OpenCode Core Permission Policy

- Replace the unconditional child `compress: deny` in `packages/opencode/src/agent/subagent-permissions.ts` (and its Task call site if required) with a named policy decision.
- Safe default: do not synthesize a deny for `compress`; preserve an explicit parent/session/subagent deny as a hard ceiling.
- Provide an opt-out/configurable compatibility switch for rollback. The switch must not silently weaken unrelated permission inheritance.
- Unit tests must distinguish absent policy, explicit allow, explicit deny, parent deny, child deny, nested child, and unrelated permission rules.

### DCP Per-Session State

- Replace the plugin-global mutable `SessionState` ownership in `index.ts` and `lib/state/**` with a `SessionStateRegistry` keyed by exact OpenCode `sessionID`.
- Every hook/tool/event resolves state from its own session ID; no “current active session” fallback when multiple sessions exist.
- Persist one atomic state record per session ID with schema version, generation/revision, timestamps, and checksum or equivalent corruption detection.
- Serialize writes per session while permitting independent sessions to proceed concurrently. Use temp-file + atomic rename (or equivalent), monotonic revision checks, and stale-write rejection.
- Parent/child lineage is metadata only; state must never be shared by reference. Nested children get independent records.
- Cancellation/retry semantics: cancellation cannot commit a partial prune; retry is idempotent; cleanup removes only eligible transient state after a documented retention period; active state is never deleted by another session’s cleanup.
- Migrate legacy files lazily and non-destructively. If ownership cannot be proven, preserve the legacy file and start isolated state rather than attaching it to the wrong session.

### Thresholds, Telemetry, and Enforcement

- `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc` must contain an exact `150000` cap for every runtime-resolved provider/model key used by active named agents/subagents and configured built-ins. The inventory must explicitly resolve GPT-5.6 SOL and GPT-5.6 Tera/Terra; no guessed spelling or alias is accepted.
- Emit structured telemetry without content bodies for: `resolved_threshold`, `nudge_delivered`, `tool_unavailable`, `nudge_ignored`, `compaction_completed`, and `context_still_over_limit`. Include session ID hash/redaction, parent ID hash when present, exact provider/model key, threshold, observed token count, policy source, attempt/revision, and outcome.
- Enforcement choice: **request blocking pending compression with bounded fail-fast handoff fallback** is the preferred design. At the hard limit, block additional model requests, attempt one eligible non-reentrant compression, then either resume below limit or generate a durable handoff and fail/restart. Automatic compression alone is not accepted because summarization can lose instructions/evidence, tool execution may be unavailable, concurrent hooks can race, signed reasoning metadata can be corrupted, and recursive compression helpers can deadlock.
- Automatic compression may be enabled only for a proven-compatible allowlist and must be transactional: retain originals until summary validation and durable state commit succeed; on any failure, leave original context untouched.

### Conductor Immediate Containment

- Until runtime/plugin fixes are validated and deployed, label Task children “DCP-unprotected.”
- Update `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`, `references\stage-prompts.md`, `references\threshold-policy.md`, and active Conductor agent prompts so every stage samples child context and initiates split/handoff by ~135K, never knowingly starting another long phase at or above ~140K.
- Replace 100–200 tool-call monoliths with bounded phases (recommended maximum 40 tool calls or 30K token growth per child), each producing a compact handoff artifact before the next Task child.
- Guardrail outcomes: terminate/retry, hand off/restart, or split; never silently continue above the bound.

## Active Model Inventory Baseline (Must Be Revalidated at Execution)

Stage 1 observed these active explicit identities (backup files excluded):

- `zai-coding-plan/glm-5.2`
- `openai/gpt-5.6-sol`
- `openai/gpt-5.6-luna` (current files; reconcile with requested/declared GPT-5.6 Tera/Terra)
- `opencode-go/minimax-m3`
- `opencode-go/qwen3.7-plus`
- `opencode-go/mimo-v2.5-pro`

Configured built-ins also inherit or name models in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`. The execution inventory must include primary agents without an explicit `model:` (resolved default), hidden agents, project-local agents/config, model variants, aliases, and the exact runtime identity for GPT-5.6 Tera/Terra. A cap is complete when the runtime-resolved active model-key set is a subset of the DCP `modelMaxLimits` keys and every required active-model value is integer `150000`. Existing unrelated cap keys must be preserved. Provider discovery confirms the exact Tera/Terra spelling is `openai/gpt-5.6-terra`, but current active Conductor files resolve to `openai/gpt-5.6-luna`; that model-assignment decision remains a pre-execution user gate.

## Acceptance Criteria

- A fixture reproduces the old Task-child `compress: deny`, zero tool availability, and missing child state before the fix.
- OpenCode core tests prove default child compression eligibility while preserving every explicit deny and unrelated permission ceiling.
- DCP tests prove separate state records for parent, concurrent siblings, and nested children; no cross-session refs, nudges, blocks, stats, or cleanup.
- Cancellation during compression leaves original context and prior durable state intact; retry is idempotent.
- Legacy state migration is non-destructive, schema-versioned, and rollback-readable.
- Every runtime-resolved active model key is present in `modelMaxLimits` at integer `150000`; unrelated existing cap keys are preserved and do not fail validation. GPT-5.6 SOL is required. The exact catalog identity is `openai/gpt-5.6-terra`, while current active Conductor files use `openai/gpt-5.6-luna`; execution must stop until the user decides whether to retain Luna and cap both keys or migrate the relevant agents to Terra.
- Enforcement tests cover successful transactional compression, unavailable tool, ignored nudge, still-over-limit, incompatible model, reentrancy, and handoff/restart fallback without dropping original messages.
- Required structured telemetry events are emitted once per state transition and contain no message/tool body data.
- Conductor guardrail tests prove a stage is split/handed off before ~140K and bounded-phase limits prevent 100–200-call loops.
- Both upstream suites, integration tests, type checks, and rollback tests pass from pinned clean source revisions.
- Completion Hygiene gate passes: plan synchronized, tests green, artifacts verified, execution log present, ledgers agree, and pipeline metadata reflects the path actually run.

## Out of Scope

- Modifying or vacuuming the live OpenCode SQLite database.
- Retrofactively compressing historical sessions before the new isolation and rollback design is proven.
- Logging prompts, summaries, tool arguments/results, secrets, or raw session content.
- Treating prompt-only instructions as the durable product fix.
- Automatically deleting legacy DCP state or logs.

## Rollback Strategy

- Core: restore the configurable compatibility policy to explicit child compression deny while retaining tests and telemetry; do not revert unrelated permission inheritance.
- DCP: disable per-session enforcement/automatic compression, keep registry reads backward-compatible, and preserve all original messages and legacy state.
- Config: restore the timestamped `dcp.jsonc` backup atomically after JSONC/schema validation.
- Conductor: retain the 140K containment guardrail even if product rollout is rolled back.
