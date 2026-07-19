# Handoff - Stage 5 GREEN (Phases 2, 3, 4 done) -> Phase 5 + Final

**Track:** 20260717-dcp-child-session-safety
**Progress:** 19/29 tasks complete (66%); 0.3 partial; 0.1 + Phase 5 + Final remaining.
**From:** Tier 1 `zai-coding-plan/glm-5.2`.

## DONE (verified - do not redo)
- **Phase 4** (config + containment): global `dcp.jsonc` 7 exact 150K caps (Luna+Terra per user decision; unrelated preserved); 3 skill + 12 agent guardrail sections; `active-model-limits.test.ts` 5/5; `ValidateSkill`/`ValidateAgents` PASS; 16 backups in `backups\2026-07-17-pre-edit\`.
- **Phase 2** (core permission): `subagent-permissions.ts` gates primary_tools deny behind opt-in `forceChildToolDeny` (default false=eligible); explicit parent/subagent deny = hard ceiling; nested + unrelated preserved. `child-compression-eligibility` 6/6, `child-compression-compatibility` 3/3, `task`+`plan-mode-subagent-bypass` 25/25, opencode `typecheck` exit 0. (`task.ts` call site intentionally NOT config-wired; see deviation.) `task.test.ts` assertion updated to eligible policy.
- **Phase 3** (DCP): `lib/state/registry.ts` (SessionStateRegistry + globalThis); atomic temp+rename persistence w/ backward-compatible schemaVersion(=2, legacy=1)+revision; `lib/logger.ts` content-free telemetry (sha256 session-ID redaction, 6 events); `lib/enforcement/{context-limit,handoff}.ts` + `getConfig`-attached API; SessionState enforcement fields. DCP targeted 26/26; full DCP 109/1 (pre-existing unrelated prompts.test.ts node:test subtest fail).

## RESUME POINT - next child starts here

### Step 1: Phase 0.1 + 0.3 (cheap bookkeeping, unblocks verify scripts)
- `scripts\capture_rca_evidence.py`: read-only SQLite URI `file:C:/Users/DaveWitkin/.local/share/opencode/opencode.db?mode=ro`; emit ONLY aggregates (audited_child_sessions==200, children_over_150k==22, child_compress_calls==0; permission action counts; DCP-state-file existence counts). NEVER select prompt/part/message-body/tool-payload columns. Output `artifacts\rca-evidence.json` with `db_open_mode=="read-only"`, `secret_or_content_fields_emitted==0`.
- `scripts\inventory_active_models.py`, `verify_model_inventory.py`, `verify_dcp_limits.py` (JSONC-aware: `//`, `/* */`, trailing commas; subset semantics: required keys ⊆ file keys, each == integer 150000, extras allowed). A curated `active-model-inventory.json` already exists.

### Step 2: Phase 5 (integration / full suites / rollback / canary)
- 5.1 `tests\integration\task-child-dcp.test.ts` - disposable harness, temp storage, synthetic messages; two concurrent children, nested child, cancel, retry, tool denial, over-limit. No live paths.
- 5.2 Full upstream suites: `bun test --timeout 30000` (workdir `opencode-core-dcp-fix\packages\opencode`) and `bun test` (DCP clone); write `artifacts\full-suite-results.json` with all `exit_code==0`. NOTE: opencode repo-root `bun run typecheck` has a PRE-EXISTING unrelated `@opencode-ai/enterprise` failure (`custom-elements.d.ts`) - record it, do not chase; the `@opencode-ai/opencode` package typechecks clean. DCP full suite has a PRE-EXISTING unrelated `prompts.test.ts` node:test subtest fail - record it.
- 5.3 `tests\integration\rollback.test.ts` - toggle compatibility deny (forceChildToolDeny), disable enforcement/auto-compression, verify originals readable; print/hash originals-preserved, legacy-readable, compatibility-deny-restored.
- 5.4 Canary: BUILD DCP first (`bun run build` or recorded build), then run parent+2 children through 135K nudge / 150K enforcement against BUILT source + isolated storage root; `artifacts\canary-report.json`. NEVER run against in-tree TS (red gate).

### Step 3: Final (F.1-F.4)
- F.1 `validation-matrix.md` mapping spec acceptance criteria -> tests/commands/exit/artifact; create `scripts\verify_validation_matrix.py`.
- F.2 `handover.md` (deployment/migration/security/rollback; universal-eligibility decision); `scripts\verify_handover.py`.
- F.3 Completion hygiene: ensure `execution-log-2026-07-17.md`, metadata, `tracks.md` (1 row), `tracks-ledger.md` (1 row) agree; create `scripts\validate_track_closeout.py` -> `0 FAIL`.
- F.4 Terminal closeout report + doc-update log/waiver; `scripts\validate_terminal_closeout.py` -> `READY_TO_CLOSE`.

## Key facts for the next child
- User decision (preserve): retain `openai/gpt-5.6-luna`; require BOTH Luna and Terra capped at integer 150000; preserve unrelated `modelMaxLimits` keys. Already done in Phase 4 - do not undo.
- Do NOT undo verified Phase 4 containment (skill/agent guardrails) or Phase 2/3 GREEN code.
- Compatibility switch `forceChildToolDeny` exists on `buildChildSessionPermission` (default false). Config-level wiring requires regenerating the strict `experimental` config type (deferred 2.2 item).
- DCP test I/O: set `XDG_DATA_HOME` to an isolated temp dir when running DCP tests (so persistence/logger never touch live `~/.local/share/opencode/storage/plugin/dcp`); keep `XDG_CONFIG_HOME` real so `active-model-limits` reads the global `dcp.jsonc`.
- Constraints: read-only live DB/state/logs; never select content/secret columns; backups before global edits; atomic writes; preserve originals until validated commit; bounded child (handoff ~135K, hard-stop ~140K); append 7-key JSONL anomalies.

## Verification commands (reuse, all currently GREEN)
- OpenCode core (workdir `packages\opencode`): `bun test test\agent\child-compression-eligibility.test.ts test\agent\child-compression-compatibility.test.ts test\tool\task.test.ts test\agent\plan-mode-subagent-bypass.test.ts --timeout 30000`; `bun run typecheck` (opencode pkg exit 0).
- DCP (workdir DCP clone, XDG_DATA_HOME=temp): `bun test tests\active-model-limits.test.ts tests\telemetry-events.test.ts tests\session-state-registry.test.ts tests\context-limit-enforcement.test.ts`.
- Conductor guardrail: `pwsh -NoProfile -File ...\conductor_context_guard.Tests.ps1 -Mode ValidateSkill` / `-Mode ValidateAgents`.