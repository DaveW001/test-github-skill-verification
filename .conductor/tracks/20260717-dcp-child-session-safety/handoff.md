# Handoff - Track ready for Stage 9 (docs + post-doc + terminal closeout)

**Track:** 20260717-dcp-child-session-safety
**Stage 7 + Stage 8 validation:** COMPLETE (`validation-report-20260719-020453Z.md` + `validation-report-20260719-021615Z.md`, validator `openai/gpt-5.6-luna`) - verdict "not ready to close" on formal bookkeeping, now reconciled. Product/changed-module acceptance is qualified-green; this validation-fix loop performed disposition/provenance/audit reconciliation only (no source behavior changes).

**Progress:** 29 tasks = 26 completed `[x]` + 2 deferred `[~]` (0.1, 5.2) + 1 pending Stage 9 `[~]` (F.4) = 27 non-deferred + 2 deferred.

## Deferral dispositions (formal, plan + metadata)
- **0.1 [DEFERRED]** - RCA aggregates (200/22/0) require message/part content columns; forbidden by the no-content rule. Not fabricated. Follow-up: a user-approved content-access waiver (or redefined metadata-only acceptance) reruns `scripts/capture_rca_evidence.py`. Evidence: `artifacts/rca-evidence.json` (BLOCKED), `artifacts/rca-evidence-blockers-20260719T003200Z.md`.
- **5.2 [DEFERRED/WAIVED]** - DCP full is GREEN (123/0, exit 0). OpenCode full is qualified-green only: 3203 pass / 9 pre-existing sandbox-env failures + 1 live-subprocess hang (`instance-bootstrap.test.ts`), 0 changed-module regressions. Literal `all(exit_code==0)` cannot be satisfied in this sandbox. **User-requested continuation rationale:** pipeline authorized to continue on the qualified-green product result rather than block on environment-only failures. Future environment to lift the waiver: symlink-capable (Dev Mode/admin), Zed installed, controlled instruction-file isolation, working live-opencode-subprocess support. Not claimed as passed.
- **F.4 [PENDING STAGE 9]** - Stage 7 validation done; remaining: Stage 9 `doc-update-log-<ts>.md` + mandatory `post-doc-validation-<ts>.md` (change is contract-affecting: public permission behavior, compatibility policy, DCP enforcement/state APIs, rollout semantics), then the terminal closeout gate. Stage 7 + Stage 8 are COMPLETE; only Stage 9 remains (Stage 8 was the single permitted pass and is exhausted).

## DONE + verified (do not redo)

- **Stage 9 reopen (continued): hard-limit BLOCK + config-wired forceChildToolDeny.** (A) xperimental.chat.messages.transform THROWS __DCP_HARD_LIMIT_BLOCK__ when overMaxLimit + prior-nudge-ignored -> propagates via yield* in packages/opencode/src/session/prompt.ts:1255 and aborts the model request (fail-fast/restart); durable handoff persisted, originals preserved (block test in plugin-wiring.test.ts). (B) xperimental.force_child_tool_deny added to the authoritative core Effect Schema (packages/core/src/v1/config/config.ts) and wired in 	ask.ts (orceChildToolDeny: cfg.experimental?.force_child_tool_deny === true); 3 parse/resolution tests. DCP full 128/0, build exit 0; core+opencode typecheck 0; core config 15/15; opencode permission/parse 37/37. See udit-correction-2026-07-19-stage9-block-and-config.md.

- **Stage 9 post-doc -> reopened Stage 5 (2026-07-19): REAL runtime wiring added** (was helper-only). index.ts resolves per-session state via sessionStateRegistry.getOrCreate for ALL hooks + compress tool (no shared mutable state); chat transform wires hard-limit enforcement (isContextOverLimits -> durable generateHandoff) + 6 telemetry transitions; event handler emits compaction_completed. New 	ests/integration/plugin-wiring.test.ts (4 tests) drives real hook factories + real registry concurrently. DCP full 127/0, build + typecheck exit 0. See udit-correction-2026-07-19-stage9-runtime-wiring.md.
- Phase 4 (config + containment), Phase 2 (core permission: forceChildToolDeny opt-in, default eligible), Phase 3 (DCP registry/atomic-persistence/telemetry/enforcement/handoff), Phase 0.3 (inventory + verifier scripts), Phase 5.1/5.3/5.4 (integration/rollback/canary vs BUILT dist), Final F.1/F.2/F.3 gates.
- Stage 6 retry: DCP full suite FIXED to all-zero (prompts.test.ts Bun node:test subtest flatten). OpenCode full diagnosed (pre-existing env).
- Stage 7 reconciliation: plan 3.3/3.6 acceptance-command name-pattern drift corrected to actual test names (rerun: 3.3 -> 8 pass/exit 0; 3.6 -> 3 pass/exit 0); source-map.json reconciled to actual revisions with provenance_history; control-char + provenance audit corrections written; metadata dates/blockers cleared; tracks.md + ledger reconciled.

## Provenance (reconciled 2026-07-19)
- OpenCode core: `C:\development\opencode-core-dcp-fix` @ `c4018482d748dfc45c8b3485ef879281fe58b84a` (dev), clean. (Prior pinned base `45cd8d7` recorded in source-map provenance_history.)
- DCP: `C:\development\opencode-dcp-child-fix` @ `558e03757e6bdc9f4a1db4f6a022039c0854caf2` (master), dirty test-only `tests/prompts.test.ts`. (Prior pinned base `85b6f5c` in history.)

## Key facts / constraints
- User decision (preserve): retain `openai/gpt-5.6-luna`; both Luna and Terra capped 150000; unrelated `modelMaxLimits` keys preserved. Do NOT undo verified Phase 2/3/4/5 code or Phase 4 containment.
- DCP test I/O: set `XDG_DATA_HOME=<isolated temp>`; keep `XDG_CONFIG_HOME` real so `active-model-limits` reads the global `dcp.jsonc`.
- No commit/push. No live DB/state/log writes. No content/secret fields selected.

## Verification commands (currently GREEN)
- OpenCode (packages/opencode): targeted permission suites 34/34; opencode pkg `bun run typecheck` exit 0.
- DCP (isolated XDG_DATA_HOME): targeted+integration+rollback all green; full `bun test` 123/0 exit 0.
- Gates: `verify_dcp_limits.py`, `verify_model_inventory.py`, `verify_validation_matrix.py --require-all`, `verify_handover.py`, `validate_track_closeout.py --require-zero-fail` (0 FAIL); Conductor `ValidateSkill`/`ValidateAgents`.
- Corrected 3.3: `bun test ... --test-name-pattern "migration|cancellation|rollback|legacy|originals"` (8 pass/exit 0); 3.6: `"reentrant|rollback|transactional|automatic"` (3 pass/exit 0).
## Stage 9 reopen (continued, 2026-07-19): hard-limit BLOCK + config-wired forceChildToolDeny
- **(A) Hard-limit BLOCK (fail-fast):** DCP `experimental.chat.messages.transform` throws `__DCP_HARD_LIMIT_BLOCK__` when `isContextOverLimits(...).overMaxLimit` + prior-nudge-ignored -> propagates via `yield*` in `packages/opencode/src/session/prompt.ts:1255` and aborts the model request (block / fail-fast / restart); durable handoff persisted, originals preserved (no destructive prune on the block path). Block integration test added.
- **(B) Config-wired forceChildToolDeny:** `experimental.force_child_tool_deny` added to the authoritative core Effect Schema (`packages/core/src/v1/config/config.ts`, default absent=eligible) and wired in `packages/opencode/src/tool/task.ts` (`forceChildToolDeny: cfg.experimental?.force_child_tool_deny === true`); 3 parse/resolution tests (`child-compression-config-parse.test.ts`).
- Verification: DCP full 128/0 + build exit 0; core typecheck 0 + core config 15/15; opencode typecheck 0 + permission/parse 37/37. See `audit-correction-2026-07-19-stage9-block-and-config.md`.
