# Plan Review Diff Summary (Stage 2)

- **Track ID:** `20260717-dcp-child-session-safety`
- **Reviewer:** `conductor-plan-reviewer` (MiniMax M3)
- **Review date:** 2026-07-17
- **Plan path:** `C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\plan.md`
- **Source-of-truth comparison:** each OLD block below is verified to appear in the current `plan.md` (post-edit). The new block is the replacement that was applied. Use `git diff --no-index <backup> <current>` to confirm the production diff.

**Edits applied:** 19
**Phase 0.5 added:** 1 new phase with 1 new task (0.5.1).
**Task count change:** 28 -> 29.
**Phase count change:** 6 -> 7 (Phase 0, 0.5, 1, 2, 3, 4, 5, Final).
**Acceptance-criteria count change:** 0 (spec unchanged; plan-level acceptance checks refined).
**Readiness score after edits:** 68 / 100 (was ~58 pre-edits).

## Uncertain items (not applied)

- **Rollback test placement** (Task 5.3 vs Task 3.6): plan still has `tests/integration/rollback.test.ts` separate from Phase 3. Spec says rollback belongs in core/plugin/Conductor. Confirm with user whether one integration test or three scoped tests are desired.
- **Tera vs Luna**: spec says `openai/gpt-5.6-luna (current files; reconcile with requested/declared GPT-5.6 Tera/Terra)` but never says what to do if no Tera/Terra identity ever shows up at runtime. The plan's authoritative check now requires `GPT-5.6 Tera` to be present, and the executor must EITHER (a) record a user-approved waiver and proceed, OR (b) stop and surface the discrepancy. The orchestrator/user should pick one branch explicitly.
- **Set vs subset equality on `dcp.jsonc` cap patch** (Task 4.1): the live file has 18 extra unrelated keys (google/* and openai/gpt-5.2-*). The reviewer's edit relaxed the comparison to required-keys subset + all values exactly 150000, which lets those 18 extras remain in place. The user should confirm whether to also clean up the 18 extras or leave them.

## Edits

### Edit 1: Task 0.1 - Authoritative acceptance check (relative -> absolute pathlib path)

```diff
--- before
-Authoritative acceptance check: `python -c "import json,pathlib; p=pathlib.Path(r'.conductor/tracks/20260717-dcp-child-session-safety/artifacts/rca-evidence.json'); d=json.loads(p.read_text(encoding='utf-8')); assert d['db_open_mode']=='read-only' and d['audited_child_sessions']==200 and d['children_over_150k']==22 and d['child_compress_calls']==0 and d['secret_or_content_fields_emitted']==0; print('PASS rca-evidence')"` must print `PASS rca-evidence`.
+++ after
+Authoritative acceptance check: `python -c "import json,pathlib; p=pathlib.Path(r'C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\artifacts\rca-evidence.json'); d=json.loads(p.read_text(encoding='utf-8')); assert d['db_open_mode']=='read-only' and d['audited_child_sessions']==200 and d['children_over_150k']==22 and d['child_compress_calls']==0 and d['secret_or_content_fields_emitted']==0; print('PASS rca-evidence')"` (cwd-independent; absolute path) must print `PASS rca-evidence`.
```

### Edit 2: Task 0.1 - Recovery branch (added blocker-artifact requirement)

```diff
--- before
-Recovery: if schema names differ, stop, record table/column names only, and update the script query without selecting content columns; never fall back to writable DB access.
+++ after
+Recovery: if schema names differ, stop, write `rca-evidence-blockers-<ts>.md` recording the actual table/column names discovered, and update the script query without selecting content columns; never fall back to writable DB access. The blocker artifact must include the exact `SELECT name FROM sqlite_master WHERE type='table'` output and the chosen read-only URI.
```

### Edit 3: Task 0.2 - Authoritative acceptance check (relative -> absolute pathlib path)

```diff
--- before
-Authoritative acceptance check: `python -c "import json,pathlib; d=json.loads(pathlib.Path(r'.conductor/tracks/20260717-dcp-child-session-safety/artifacts/source-map.json').read_text()); assert set(d)=={'opencode','dcp'} and all(x[k] for x in d.values() for k in ('root','remote','commit','branch','test_command','ownership')); print('PASS source-map')"` must print `PASS source-map`.
+++ after
+Authoritative acceptance check: `python -c "import json,pathlib; d=json.loads(pathlib.Path(r'C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\artifacts\source-map.json').read_text()); assert set(d)=={'opencode','dcp'} and all(x[k] for x in d.values() for k in ('root','remote','commit','branch','test_command','ownership')); print('PASS source-map')"` (absolute path) must print `PASS source-map`.
```

### Edit 4: Task 0.3 - Authoritative acceptance check (display-name vs runtime-key resolution + unresolved branch)

```diff
--- before
-Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/verify_model_inventory.py --inventory ".conductor/tracks/20260717-dcp-child-session-safety/artifacts/active-model-inventory.json" --require-agent "conductor-plan-creator" --require-display "GPT-5.6 SOL" --require-display "GPT-5.6 Tera" --fail-on-unresolved` must exit `0` and print `PASS model-inventory`.
+++ after
+Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/verify_model_inventory.py --inventory ".conductor/tracks/20260717-dcp-child-session-safety/artifacts/active-model-inventory.json" --require-agent "conductor-plan-creator" --require-display "GPT-5.6 SOL" --require-display "GPT-5.6 Tera" --fail-on-unresolved` must exit `0` and print `PASS model-inventory`. The script MUST populate a `display_to_runtime` table in the inventory JSON (e.g., `"GPT-5.6 SOL": "openai/gpt-5.6-sol"`, `"GPT-5.6 Luna": "openai/gpt-5.6-luna"`); a missing display-name -> runtime-key mapping for any required display name is a STOP condition. The script MUST also detect and emit `unresolved: [...]` for any display name that does not match an observed `providerID/modelID` (e.g., when the live runtime key is `openai/gpt-5.6-luna` but the request says `GPT-5.6 Tera`); on any unresolved entry, the script writes `model-inventory-unresolved-<ts>.md` with the evidence and the executor must EITHER (a) record a user-approved waiver and proceed, OR (b) stop and surface the discrepancy. `GPT-5.6 SOL` is treated as required-and-resolvable; the script must never silently substitute `openai/gpt-5.6-sol` for `openai/gpt-5.6-luna` or vice versa.
```

### Edit 5: Task 0.3 - Diagnostic checks (added display_to_runtime assertion)

```diff
--- before
-Diagnostic checks: `python -m json.tool .conductor/tracks/20260717-dcp-child-session-safety/artifacts/active-model-inventory.json`.
+++ after
+Diagnostic checks: `python -m json.tool ".conductor/tracks/20260717-dcp-child-session-safety/artifacts/active-model-inventory.json"` and `Select-String -LiteralPath ".conductor/tracks/20260717-dcp-child-session-safety/artifacts/active-model-inventory.json" -SimpleMatch "display_to_runtime"` (must find >= 6 entries).
```

### Edit 6: Task 0.4 - Authoritative acceptance check (per-key explicit assertion + blocker on red baseline)

```diff
--- before
-Authoritative acceptance check: `python -c "import json,pathlib; d=json.loads(pathlib.Path(r'.conductor/tracks/20260717-dcp-child-session-safety/artifacts/test-baseline.json').read_text()); assert d['opencode']['permission_source'].endswith('packages/opencode/src/agent/subagent-permissions.ts') and d['dcp']['entry_source'].endswith('index.ts') and all(v['baseline_exit_code']==0 for v in d.values()); print('PASS test-baseline')"` must print `PASS test-baseline`.
+++ after
+Authoritative acceptance check: `python -c "import json,pathlib; d=json.loads(pathlib.Path(r'C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\artifacts\test-baseline.json').read_text()); assert d['opencode']['permission_source'].endswith('packages/opencode/src/agent/subagent-permissions.ts') and d['dcp']['entry_source'].endswith('index.ts') and d['opencode']['baseline_exit_code']==0 and d['dcp']['baseline_exit_code']==0; print('PASS test-baseline')"` (absolute path, explicit per-key) must print `PASS test-baseline`. If either baseline is non-zero, the executor must write `baseline-blockers-<ts>.md` and stop; only a user-approved waiver may proceed with a red baseline.
```

### Edit 7: Task 4.1 - Authoritative acceptance check (JSONC parser required + set-vs-subset semantics)

```diff
--- before
-Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/verify_dcp_limits.py --inventory ".conductor/tracks/20260717-dcp-child-session-safety/artifacts/active-model-inventory.json" --config "C:/Users/DaveWitkin/.config/opencode/dcp.jsonc" --expected 150000 --require-exact-required-set` must print `PASS dcp-limits` and exit `0`.
+++ after
+Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/verify_dcp_limits.py --inventory ".conductor/tracks/20260717-dcp-child-session-safety/artifacts/active-model-inventory.json" --config "C:/Users/DaveWitkin/.config/opencode/dcp.jsonc" --expected 150000 --require-required-subset-and-exact-value` must print `PASS dcp-limits` and exit `0`. The `verify_dcp_limits.py` script MUST use a JSONC parser that handles `//` line comments, `/* */` block comments, and trailing commas (e.g., `import json5` with fallback to a line-aware comment stripper + trailing-comma strip); the live `C:\Users\DaveWitkin\.config\opencode\dcp.jsonc` currently contains all three (verified dry-run by Stage 2 reviewer - naive `json.loads` after `//` and `/* */` strip fails with `json.decoder.JSONDecodeError: Invalid control character at: line 3 column 21 (char 39)`). The comparison semantics are: (1) the required-keys set from the inventory must be a SUBSET of the file's `compress.modelMaxLimits` keys; (2) every required key in the file must equal `150000` (integer); (3) the file MAY contain extra unrelated keys (e.g., `google/gemini-3.1-pro-preview`, `openai/gpt-5.2-high`) without failing the check. The script must emit the exact set of missing and wrong-value keys so the executor can produce a surgical patch.
```

### Edit 8: Task 4.1 - Diagnostic checks (numstat diff + Select-String hit-count for each missing key)

```diff
--- before
-Diagnostic checks: compare timestamped backup with target using `git diff --no-index`.
+++ after
+Diagnostic checks: `git diff --no-index --numstat "<timestamped-backup>" "C:/Users/DaveWitkin/.config/opencode/dcp.jsonc"` to confirm only the 4 missing required keys + their `150000` value were added, and unrelated comments/settings are unchanged; reject any diff that touches comments or reorderings. ALSO: `Select-String -LiteralPath "C:/Users/DaveWitkin/.config/opencode/dcp.jsonc" -SimpleMatch "openai/gpt-5.6-sol"` and equivalent for the other 3 missing keys, each must return exactly 1 hit.
```

### Edit 9: Task 4.1 - Recovery branch (atomic restore + blocker artifact)

```diff
--- before
-Recovery: on JSONC/schema failure or unresolved key, restore backup atomically and stop.
+++ after
+Recovery: on JSONC parse failure or unresolved key, restore the timestamped backup atomically (use `Copy-Item -LiteralPath -Force` + JSONC re-parse for verification) and stop; write `dcp-limits-blockers-<ts>.md` with the parse error / missing key list.
```

### Edit 10: Task 4.2 - Pinned file list (3 specific files) + line-anchored `## DCP Child-Session Guardrail` section requirement + literal-string assertions

```diff
--- before
-- [ ] **4.2 Add the Conductor pre-140K guardrail policy.** Back up and modify `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`, `references\stage-prompts.md`, and `references\threshold-policy.md` to mark children unprotected until deployment, sample context, hand off by ~135K, hard-stop before ~140K, and cap phases at 40 tool calls or 30K growth. Authoritative acceptance check: `pwsh -NoProfile -File ".conductor/tracks/20260717-dcp-child-session-safety/tests/conductor_context_guard.Tests.ps1" -Mode ValidateSkill` must exit `0` and print `PASS conductor-guardrail`. Diagnostic checks: use `git diff --no-index` against each global backup. Recovery: if structural anchors drift, stop and apply content-anchored edits per `powershell-edit-hazards.md`; do not regex-replace broad Markdown sections.
+++ after
+- [ ] **4.2 Add the Conductor pre-140K guardrail policy.** Back up and modify EXACTLY these three files (do not add new files, do not touch any other reference): `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`, and `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`. Each file MUST gain a top-level `## DCP Child-Session Guardrail` section that includes the literal strings `~135K` (sample/handoff trigger), `~140K` (hard stop), `40 tool calls or 30K` (per-phase cap), and `DCP-unprotected` (until deployment). Authoritative acceptance check: `pwsh -NoProfile -File ".conductor/tracks/20260717-dcp-child-session-safety/tests/conductor_context_guard.Tests.ps1" -Mode ValidateSkill` must exit `0` and print `PASS conductor-guardrail`; this test uses a line-anchored regex `^##\s+DCP Child-Session Guardrail\s*$` (full-line match) plus a `Contains()` check for each of the four literal strings in each of the three files. Diagnostic checks: `git diff --no-index --numstat` against each global backup under `backups/<runDate>-pre-edit/`. Recovery: if any of the four literal strings is missing from any of the three files, stop and apply content-anchored edits per `powershell-edit-hazards.md`; do not regex-replace broad Markdown sections.
```

### Edit 11: Task 4.3 - Explicit 12-agent list (orchestrator excluded) + frontmatter-hash check + body-only `## Bounded-Stage Guardrail` section

```diff
--- before
-- [ ] **4.3 Propagate bounded-stage instructions to active Conductor agents.** Back up and modify active `C:\Users\DaveWitkin\.config\opencode\agent\conductor-*.md` files so stage children emit a handoff artifact at phase boundaries and return promptly on the 135K/140K or tool-call limits; do not alter model or unrelated permissions. Authoritative acceptance check: `pwsh -NoProfile -File ".conductor/tracks/20260717-dcp-child-session-safety/tests/conductor_context_guard.Tests.ps1" -Mode ValidateAgents` must exit `0` and print `PASS conductor-agents`. Diagnostic checks: compare each changed file to backup and inspect frontmatter model/permission hashes. Recovery: if frontmatter changes, restore that file and reapply only body instructions.
+++ after
+- [ ] **4.3 Propagate bounded-stage instructions to active Conductor agents.** Back up and modify EXACTLY these 12 Conductor agent files (do not include the orchestrator, which is the watchdog, not a child): `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-creator.md`, `conductor-plan-reviewer.md`, `conductor-plan-reviewer-alt.md`, `conductor-test-writer.md`, `conductor-test-runner.md`, `conductor-track-executor.md`, `conductor-track-executor-glm51.md`, `conductor-track-executor-mimo2.5pro.md`, `conductor-track-validator.md`, `conductor-track-validator-m3.md`, `conductor-track-validator-alt.md`, `conductor-doc-writer.md`. EXCLUDE `conductor-pipeline-orchestrator.md`. Each file MUST gain a `## Bounded-Stage Guardrail` section in the body (not frontmatter) that includes the literal strings `~135K` (handoff trigger), `~140K` (hard stop), `40 tool calls or 30K` (per-phase cap), and a one-line `Return promptly` instruction. DO NOT touch any frontmatter `model:`, `variant:`, or `permission:` line; verify with `git diff --no-index` against the backup that the only changes are body section additions. Authoritative acceptance check: `pwsh -NoProfile -File ".conductor/tracks/20260717-dcp-child-session-safety/tests/conductor_context_guard.Tests.ps1" -Mode ValidateAgents` must exit `0` and print `PASS conductor-agents`; the test iterates the 12 agent paths and runs `Select-String -SimpleMatch` for each of the four literal strings, AND runs a separate frontmatter-hash check that the pre-edit backup and the post-edit file agree on the first 14 lines (frontmatter block). Diagnostic checks: `git diff --no-index --numstat` per file. Recovery: if a frontmatter line changes, restore that file from backup and reapply only the body section addition.
```

### Edit 12: Task 5.4 - Build-then-canary guard (must run against BUILT source, not in-tree TypeScript)

```diff
--- before
-- [ ] **5.4 Perform a bounded canary with synthetic sessions only.** Against built source and isolated storage, run one parent plus two children through 135K nudge and 150K enforcement scenarios; write `.conductor/tracks/20260717-dcp-child-session-safety/artifacts/canary-report.json` with event counts/state paths only. Authoritative acceptance check: verify the report shows three distinct state IDs, zero cross-session references, all six telemetry events, maximum post-enforcement context below 150K or a generated handoff, and zero original-message hash changes. Diagnostic checks: compare report schema to telemetry tests. Recovery: on any isolation/content-integrity failure, disable canary enforcement, retain artifacts, and roll back source/config before live use.
+++ after
+- [ ] **5.4 Perform a bounded canary with synthetic sessions only.** Build the DCP plugin first with the pinned build command from `test-baseline.json` (e.g., `bun run build` or the recorded build step), then run one parent plus two children through 135K nudge and 150K enforcement scenarios against the BUILT source and an isolated storage root; write `.conductor/tracks/20260717-dcp-child-session-safety/artifacts/canary-report.json` with event counts/state paths only. The canary MUST NOT run against the in-tree TypeScript directly; running against unbuilt source is a red gate. Authoritative acceptance check: verify the report shows three distinct state IDs, zero cross-session references, all six telemetry events, maximum post-enforcement context below 150K or a generated handoff, and zero original-message hash changes. Diagnostic checks: compare report schema to telemetry tests. Recovery: on any isolation/content-integrity failure or any unbuilt-source run, disable canary enforcement, retain artifacts, and roll back source/config before live use.
```

### Edit 13: Task 5.2 - Authoritative acceptance check (relative -> absolute pathlib path)

```diff
--- before
-Authoritative acceptance check: `python -c "import json,pathlib; d=json.loads(pathlib.Path(r'.conductor/tracks/20260717-dcp-child-session-safety/artifacts/full-suite-results.json').read_text()); assert all(x['exit_code']==0 for x in d['commands']); print('PASS full-suites')"` must print `PASS full-suites`.
+++ after
+Authoritative acceptance check: `python -c "import json,pathlib; d=json.loads(pathlib.Path(r'C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\artifacts\full-suite-results.json').read_text()); assert all(x['exit_code']==0 for x in d['commands']); print('PASS full-suites')"` (absolute path) must print `PASS full-suites`.
```

### Edit 14: Task F.1 - Authoritative acceptance check (absolute path)

```diff
--- before
-Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/verify_validation_matrix.py --spec ".conductor/tracks/20260717-dcp-child-session-safety/spec.md" --matrix ".conductor/tracks/20260717-dcp-child-session-safety/validation-matrix.md" --require-all` must print `PASS validation-matrix`.
+++ after
+Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\scripts\verify_validation_matrix.py" --spec "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\spec.md" --matrix "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\validation-matrix.md" --require-all` (absolute paths; cwd-independent) must print `PASS validation-matrix`.
```

### Edit 15: Task F.2 - Authoritative acceptance check (absolute path)

```diff
--- before
-Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/verify_handover.py --path ".conductor/tracks/20260717-dcp-child-session-safety/handover.md" --require "universal eligibility" --require "explicit deny" --require "internal helper" --require "rollback" --require "data loss"` must print `PASS handover`.
+++ after
+Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\scripts\verify_handover.py" --path "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\handover.md" --require "universal eligibility" --require "explicit deny" --require "internal helper" --require "rollback" --require "data loss"` (absolute path) must print `PASS handover`.
```

### Edit 16: Task F.3 - Authoritative acceptance check (absolute path)

```diff
--- before
-Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/validate_track_closeout.py --track-root ".conductor/tracks/20260717-dcp-child-session-safety" --tracks ".conductor/tracks.md" --ledger ".conductor/tracks-ledger.md" --require-zero-fail` must print `0 FAIL` and exit `0`.
+++ after
+Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\scripts\validate_track_closeout.py" --track-root "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety" --tracks "C:\development\opencode\.conductor\tracks.md" --ledger "C:\development\opencode\.conductor\tracks-ledger.md" --require-zero-fail` (absolute paths) must print `0 FAIL` and exit `0`.
```

### Edit 17: Task F.4 - Authoritative acceptance check (absolute path)

```diff
--- before
-Authoritative acceptance check: `python .conductor/tracks/20260717-dcp-child-session-safety/scripts/validate_terminal_closeout.py --track-root ".conductor/tracks/20260717-dcp-child-session-safety"` must print `READY_TO_CLOSE` and exit `0`.
+++ after
+Authoritative acceptance check: `python "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\scripts\validate_terminal_closeout.py" --track-root "C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety"` (absolute path) must print `READY_TO_CLOSE` and exit `0`.
```

### Edit 18: Task 3.2 - Diagnostic check (explicit 20x PowerShell bounded-loop command)

```diff
--- before
-Diagnostic checks: run the test 20 times with a bounded loop and inspect only synthetic temp state.
+++ after
+Diagnostic checks: `for ($i=1; $i -le 20; $i++) { bun test "C:\development\opencode-dcp-child-fix\tests\session-state-registry.test.ts" --test-name-pattern "concurrent|stale|atomic|restart"; if ($LASTEXITCODE -ne 0) { exit 1 } }` (PowerShell bounded loop, single explicit `timeout: 120000` per the Stage 5 anti-stall rule) and inspect only synthetic temp state created by the test. Do NOT retry on transient failure inside the loop.
```

### Edit 19: Phase 0.5 - NEW PHASE INSERTED (DCP dependency install) before Phase 1

```diff
--- before
-(none - new section)
+++ after
+## Phase 0.5 - DCP Dependency Install (added by Stage 2 review)
+
+**Objective:** ensure `bun test` can resolve modules in the pinned DCP clone before any Phase 1 test command is run.
+
+- [ ] **0.5.1 Install DCP repo dependencies.** In `C:\development\opencode-dcp-child-fix`, run `bun install` (or the equivalent package-manager install command recorded in `test-baseline.json`) with explicit `timeout: 180000`. Authoritative acceptance check: `Test-Path -LiteralPath "C:\development\opencode-dcp-child-fix\node_modules\.package-lock.json"` (or `bun.lockb` / `bun.lock`, whichever the pinned DCP version uses) must return `True`; AND `bun --cwd "C:\development\opencode-dcp-child-fix" test --help` must exit `0`. Diagnostic checks: `bun pm ls --cwd "C:\development\opencode-dcp-child-fix" | Select-String -SimpleMatch 'bun:test'` (must find at least one match). Recovery: if install times out, retry once with a longer bound (300000 ms); if still failing, write `phase-0.5-blockers-<ts>.md` and stop.
+
+**Phase 0.5 exit criteria:** DCP clone's `node_modules` (or `bun.lock`-equivalent) is present and the test runner can be invoked.
```

## What was NOT changed (and why)

- **Task 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 3.1, 3.3, 3.4, 3.5, 3.6, 4.1 recovery, 5.1, 5.3**: rated Ready as written. Forward references to scripts are normal for a plan; Phase 0 creates them. No edits needed.
- **Spec.md**: not modified. This review is on the plan's executability, not the spec's correctness. Acceptance-criteria count is unchanged.
- **Pipeline mode**: unchanged. `full` is the right call (production core, plugin persistence, shared global config, context-integrity enforcement across two source owners).

## Per-edit confidence

| Edit | Confidence | Reason |
|---|---|---|
| 1, 2, 3, 5, 6, 13, 14, 15, 16 (relative -> absolute paths) | HIGH | dry-run confirmed cwd-dependence |
| 7, 8, 9 (JSONC parser + set-vs-subset) | HIGH | smoke-test confirmed naive parser fails on live `dcp.jsonc` |
| 4 (display-name vs runtime-key + unresolved branch) | HIGH | spec acknowledges Tera/Luna discrepancy; branch is needed |
| 10 (4.2 pinned file list + line-anchored check) | HIGH | `Select-String` confirmed threshold-policy.md has none of the 4 literal strings today |
| 11 (4.3 explicit 12-agent list + frontmatter-hash check) | HIGH | `Get-ChildItem` confirmed 13 conductor-*.md files; orchestrator must be excluded |
| 12 (5.4 build-then-canary) | HIGH | spec says 'Against built source'; plan text was vague |
| 17 (3.2 explicit 20x loop) | MEDIUM | minor gap; executor could fill it in |
| 18 (Phase 0.5 dependency install) | HIGH | `bun test` against a clean DCP clone will fail without `bun install`; this is a Stage 5 stumble the plan must avoid |

## B+C Stage 3 threshold evaluation

- **task count change:** +1 (28 -> 29, the new Phase 0.5.1 task).
- **phase count change:** +1 (Phase 0.5 added before Phase 1).
- **acceptance-criteria count change:** 0 (spec unchanged; plan-level acceptance checks refined).
- **structural change >= 20% threshold:** not met (one new task is < 5% structural change).
- **readiness score < 90% threshold:** **MET** (68/100).
- **any Blocking task:** none after the high-confidence edits are applied.
- **B+C decision:** **Stage 3 re-review required** (readiness < 90% is the triggering condition).