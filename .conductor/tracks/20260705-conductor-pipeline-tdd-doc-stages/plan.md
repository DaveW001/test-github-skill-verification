# Plan: Conductor Pipeline TDD + Documentation Stages

**Track ID**: 20260705-conductor-pipeline-tdd-doc-stages
**Created**: 2026-07-05
**Status**: Plan drafted — Phase 0 complete - decisions resolved (see decisions-resolved.md), backups created, test baseline recorded.

> **Read first:** `spec.md` in this folder. This plan implements that spec. Every task below carries ONE `Authoritative acceptance check:` plus optional `Diagnostic checks:`. Stages 4/4b/6/9 only apply to `code`-type tracks; `bookkeeping` tracks skip them (see Phase 2).

---

## Phase 0 — Setup & Preconditions

**Objective:** resolve open decisions, back up the files we will modify, and establish the test-framework baseline before any agent is created.

- [x] 0.1 **Resolve the seven open decisions with the user** (spec.md section 9). Capture answers inline here before proceeding: (1) discriminator mechanism, (2) doc-writer position, (3) context-isolation level, (4) doc-writer model, (5) agent names, (6) in-flight-track handling, (7) test-framework metadata field.
  - **Authoritative acceptance check:** all seven decisions have a recorded answer in this task's checkboxes (e.g. `[x] discriminator=Option A`), and no item remains an open question.
  - Diagnostic checks: none.

- [x] 0.2 **Back up every file this plan modifies**, using the global-skill-versioning backup pattern (`references/global-skill-versioning.md`). Backups live in the active track folder (per the standard), not the global config folder. For the six pre-existing targets: `backups\2026-07-05-pre-edit\agent\conductor-pipeline-orchestrator.md.pre-edit.bak`, `...\conductor-track-executor.md.pre-edit.bak`, `...\conductor-track-validator.md.pre-edit.bak`, `...\skill\conductor-pipeline\SKILL.md.pre-edit.bak`, `...\skill\conductor-pipeline\references\stage-prompts.md.pre-edit.bak`, `...\skill\conductor-pipeline\references\threshold-policy.md.pre-edit.bak`. For the three NEW agents (which do not exist yet) write a `__FILE_DID_NOT_EXIST_BEFORE_EDIT__` marker at `backups\2026-07-05-pre-edit\agent\<agent-name>.md.__FILE_DID_NOT_EXIST__.bak` so the backup set is complete and auditable. Also back up `agent-development-standards.md` (referenced by the standards doc for the new agents) at `backups\2026-07-05-pre-edit\agent-development-standards.md.pre-edit.bak`.
  - **Authoritative acceptance check:** all six pre-edit backups + three new-agent markers + the standards backup exist. Verify with `(Get-ChildItem -Recurse -Path "C:\development\opencode\.conductor\tracks\20260705-conductor-pipeline-tdd-doc-stages\backups\2026-07-05-pre-edit" -File).Count -ge 10` returning `True`.
  - Diagnostic checks: `Test-Path` returns True for the six pre-edit `.pre-edit.bak` files and the three `__FILE_DID_NOT_EXIST__` markers.

- [x] 0.3 **Record the test-framework baseline** for the opencode repo so new agents have a known `test_command`. This meta-track is `bookkeeping`-type and will not run TDD stages itself; baseline is recorded for the future code-bearing tracks that DO use this fork. **Baseline finding for THIS repo:** NO unit-test runner is installed (no `test`/`typecheck`/`build`/`lint` script in `package.json`; no `bunfig.toml`; no vitest/jest config; zero `*.test.ts`/`*.spec.ts` files; only `test:visual:*` playwright scripts exist). Therefore `test_framework` = `none` and `test_command` = `n/a` for this repo. The metadata fields are informational defaults for future code-bearing tracks.
  - **Authoritative acceptance check:** `metadata.json` shows `test_framework: "n/a"` and `test_command: "n/a"`; running `bun --version` succeeds (Bun is available) and `bun test` exits non-zero with "no tests" or "test script not defined" (document the exit code in the execution log).
  - Diagnostic checks: `(Get-ChildItem -Recurse -Include *.test.ts,*.spec.ts -Path C:\development\opencode).Count` returns 0; `(Test-Path C:\development\opencode\package.json) -and -not (Select-String -SimpleMatch '"test":' -LiteralPath C:\development\opencode\package.json)` returns `True` (no top-level `test` script).

---

## Phase 1 — New agents (create the three subagents)

**Objective:** stand up `conductor-test-writer`, `conductor-test-runner`, `conductor-doc-writer` per `agent-development-standards.md`. Each is `mode: subagent`, `task: { "*": deny }` (anti-recursion), `bash: allow`, `skill: { conductor: allow, conductor-pipeline: allow }`.

- [x] 1.1 **Create `conductor-test-writer.md`** at `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md`. Frontmatter: `model: openai/gpt-5.5`, `variant: low`, `permission: { edit: allow, bash: allow, task: { "*": deny }, skill: { conductor: allow, conductor-pipeline: allow } }`.
  - **Authoritative acceptance check:** all four checks pass - (1) Test-Path -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' returns True; (2) (Get-Content -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' -Raw).StartsWith("---\n") returns True; (3) Select-String -SimpleMatch 'mode: subagent' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' AND Select-String -SimpleMatch '"*": deny' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' each return at least one match; (4) Select-String -SimpleMatch 'Tool-call self-bounding' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' AND Select-String -SimpleMatch 'model-unavailable' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' AND Select-String -SimpleMatch 'pipeline-anomalies.jsonl' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' each return at least one match. (Note: in this environment opencode run --agent conductor-test-writer 'test' returns 'Session not found' - a session-init error, NOT a YAML parse error; the YAML parse check is independently proven by check (2)+(3) above.)
  - Diagnostic checks: Select-String -SimpleMatch 'openai/gpt-5.5' 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md' confirms model pinning.

- [x] 1.2 **Create `conductor-test-runner.md`** at `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md`. Frontmatter: `model: opencode-go/minimax-m3` (independent family from the glm executor), `permission: { edit: deny, bash: allow, task: { "*": deny }, skill: { conductor: allow, conductor-pipeline: allow } }`. Body: run the project's test command (`test_command` from metadata); report per-test pass/fail + captured output into `test-run-report-<ts>.md` in the track folder; do NOT edit code (read-only verifier); if tests fail, the orchestrator (not this agent) decides the retry. **MUST include** the tool-call self-bounding block (timeout on every bash call, no uncapped commands, anti-stall) AND the `model-unavailable` reporting block (mirroring `conductor-track-executor.md`), AND the closeout anomaly-logging line (one JSONL append per observed anomaly to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` per `references/anomaly-logging.md`). `bash: allow` is required even on a read-only runner because the test command runs through bash; read-only behavior is enforced by the prompt protocol restricting bash to test-running + report-writing only.
  - **Authoritative acceptance check:** all four checks pass - (1) `Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md"` returns `True`; (2) `(Get-Content -LiteralPath ... -Raw).StartsWith("---\n")` returns `True`; (3) `Select-String -SimpleMatch 'edit: deny' conductor-test-runner.md` returns at least one match; (4) `Select-String -SimpleMatch 'Tool-call self-bounding' conductor-test-runner.md` AND `Select-String -SimpleMatch 'model-unavailable' conductor-test-runner.md` AND `Select-String -SimpleMatch 'pipeline-anomalies.jsonl' conductor-test-runner.md` each return at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'opencode-go/minimax-m3' conductor-test-runner.md` confirms model pinning.

- [x] 1.3 **Create `conductor-doc-writer.md`** at `C:\Users\DaveWitkin\.config\opencode\agent\conductor-doc-writer.md`. Frontmatter: `model: openai/gpt-5.5`, `variant: low` (per Decision 4), `permission: { edit: allow, bash: allow, task: { "*": deny }, skill: { conductor: allow, conductor-pipeline: allow } }`. Body: read updated spec + code public-API surface + tests + commit metadata; update README, API docs, changelog, ADRs ONLY (do not modify source/tests); write `doc-update-log-<ts>.md` listing every doc file touched. Self-verify that every public API in code appears in docs. **MUST include** the tool-call self-bounding block (timeout on every bash call, no uncapped commands, anti-stall) AND the `model-unavailable` reporting block, AND the closeout anomaly-logging line. `edit: allow` is justified for doc files (README/markdown/ADRs/changelog only) but NOT for source/test files - enforce via prompt protocol with a hard prohibition list.
  - **Authoritative acceptance check:** all four checks pass - (1) `Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-doc-writer.md"` returns `True`; (2) `(Get-Content -LiteralPath ... -Raw).StartsWith("---\n")` returns `True`; (3) `Select-String -SimpleMatch 'edit: allow' conductor-doc-writer.md` AND `Select-String -SimpleMatch 'openai/gpt-5.5' conductor-doc-writer.md` each return at least one match; (4) `Select-String -SimpleMatch 'Tool-call self-bounding' conductor-doc-writer.md` AND `Select-String -SimpleMatch 'pipeline-anomalies.jsonl' conductor-doc-writer.md` each return at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'README|changelog|ADR' conductor-doc-writer.md` confirms the doc-surface scope.

- [x] 1.4 **Define the track metadata schema extension** used by the discriminator and test-runner. Add to the plan-creator's output contract: `metadata.json` gains `track_type` (`code` | `bookkeeping`), `test_framework` (e.g. `bun:test`, `vitest`, `pytest`; or `none` for this repo per Task 0.3), and `test_command` (e.g. `bun test`, `vitest run`; or `n/a` for this repo per Task 0.3). Default `track_type` = `bookkeeping` when the plan-creator cannot determine it (safe default = skip TDD). Note: this task DEFINES the schema; Phase 2 Task 2.3 is the edit that INSERTS the requirement into the Stage 1 prompt. Both must complete for the keys to be emitted by future plan-creator runs.
  - **Authoritative acceptance check (THIS task):** the three keys are documented here in plan.md (visible above). A reviewer can confirm the schema is defined without re-running anything. To prove the Stage 1 prompt is updated, defer to Task 2.3 acceptance check.
  - Diagnostic checks: none (the schema is plain text in this plan, not a separate artifact).

---

## Phase 2 — Pipeline wiring (orchestrator + skill + prompts + thresholds)

**Objective:** connect the new agents into the orchestrator, the SKILL model table, the stage prompts, and the threshold policy. Order matters: skill/prompts first, then orchestrator, then thresholds.

- [x] 2.1 **Update `SKILL.md` stage table and flow** at `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`. Replace the 6-stage "Model assignments" table with the 9-stage table from spec.md section 4. Add a "Track-type discriminator" subsection documenting that stages 4/4b/6 run only for `code`-type tracks and that `bookkeeping` tracks take the path 1->2->3->5->7->8->9. Add the RED-gate (4b) and test-runner retry-cap rules.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'conductor-test-writer' SKILL.md` AND `Select-String -SimpleMatch 'conductor-doc-writer' SKILL.md` AND `Select-String -SimpleMatch 'conductor-test-runner' SKILL.md` each return one match; the diversity-log bullets are present.
  - Diagnostic checks: `Select-String -SimpleMatch 'RED-state' SKILL.md`.

- [x] 2.2 **Add the three new stage prompts** to `references/stage-prompts.md`. **CRITICAL renumbering step first:** the existing `## Stage 4 - Execution (conductor-track-executor)` heading MUST be renamed to `## Stage 5 - Execution (conductor-track-executor)` (the new test-writer takes Stage 4), and the existing `## Stage 5 / 6 - Validation / Conditional Re-validation (conductor-track-validator / -alt)` heading MUST be renamed to `## Stage 7 / 8 - Validation / Conditional Re-validation (conductor-track-validator / -alt)` (the new test-runner takes Stage 6 and the new doc-writer takes Stage 9). Without this renumbering, two `## Stage 4` and two `## Stage 6` headings will exist and the verification snippets will be ambiguous. THEN add the three new blocks:
  - **Stage 4 (test-writer / RED):** write failing tests from acceptance criteria; spec-driven not impl-driven; detect framework from `metadata`; include the Tool preflight + anomaly-logging closeout append blocks.
  - **Stage 6 (test-runner):** run `test_command`; emit `test-run-report-<ts>.md` with per-test results; read-only; do not fix.
  - **Stage 9 (doc-writer):** update README/API docs/changelog/ADRs from spec+code+tests; emit `doc-update-log-<ts>.md`; docs-only edits.
  - **Authoritative acceptance check:** all of the following return one match each (line-anchored full-line patterns preferred per `references/stage-prompts.md` Structural idempotency section):
    - Select-String -SimpleMatch '## Stage 4 - Write Tests' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md' returns one match.
    - Select-String -SimpleMatch '## Stage 5 - Execution' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md' returns one match (proves the old Stage 4 was renamed).
    - Select-String -SimpleMatch '## Stage 6 - Run Tests' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md' returns one match (use a unique heading like 'Stage 6 - Run Tests' to avoid the substring collision with 'Stage 5 / 6' below).
    - Select-String -SimpleMatch '## Stage 7 / 8 - Validation' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md' returns one match (proves the old Stage 5/6 was renamed).
    - Select-String -SimpleMatch '## Stage 9 - Documentation' 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md' returns one match.
  - Diagnostic checks: each new block contains the anomaly-logging closeout line `pipeline-anomalies.jsonl`.
- [x] 2.3 **Update the Stage 1 (plan-creator) prompt** to require `track_type`, `test_framework`, and `test_command` in `metadata.json` (Task 1.4 schema). This is an edit to the existing Stage 1 block in `references/stage-prompts.md`.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'track_type' references\stage-prompts.md` returns at least one match within the Stage 1 block region.
  - Diagnostic checks: none.

- [x] 2.4 **Update `threshold-policy.md`** at `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`. Add: (a) RED-gate definition (tests must fail before Stage 5; on premature pass, reopen Stage 4 once, cap 1); (b) test-runner retry cap (route back to Stage 5 once, then stop); (c) a note that doc-writer edits (Stage 9) are bookkeeping-scope for re-validation purposes unless they change user-facing behavior.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'RED-state' references\threshold-policy.md` AND `Select-String -SimpleMatch 'test-runner retry' references\threshold-policy.md` each return one match.
  - Diagnostic checks: none.

- [x] 2.5 **Update `conductor-pipeline-orchestrator.md`:** (a) add `conductor-test-writer`, `conductor-test-runner`, `conductor-doc-writer` to the `permission.task` allowlist; (b) rewrite the "How to run the pipeline" section to the 9-stage flow with track-type branching (read `track_type` from metadata; if `bookkeeping` skip 4/4b/6); (c) add the RED-gate step (run `test_command`, if exit 0 reopen test-writer); (d) add the test-runner failure routing (retry Stage 5 once, then stop); (e) add Stage 9 (doc-writer) after re-validation.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'conductor-test-writer: allow' conductor-pipeline-orchestrator.md` returns one match (and likewise for the other two new agents); AND `Select-String -SimpleMatch 'track_type' conductor-pipeline-orchestrator.md` returns at least one match.
  - Diagnostic checks: `Select-String -SimpleMatch 'RED' conductor-pipeline-orchestrator.md`.

---

## Phase 3 — Re-scope the executor and update the validator

**Objective:** make the existing executor code-only (GREEN) and teach the validator to check test-green + acceptance coverage.

- [x] 3.1 **Re-scope `conductor-track-executor.md`** to the GREEN phase. Body changes: state that tests already exist (written by Stage 4) and the executor's job is to write the minimum implementation to make them pass; **remove/forbid test authoring**; keep the tool-call self-bounding + model-unavailable + fallback-chain blocks unchanged. Add a one-line note that the behavioral change applies to new tracks only (existing in-flight tracks finish on the old path per Decision 6).
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'GREEN' conductor-track-executor.md` returns at least one match AND `Select-String -SimpleMatch 'do not author tests' conductor-track-executor.md` ((the literal phrase 'do not author tests' - do not accept paraphrases like 'do not write tests' for this check)) returns one match.
  - Diagnostic checks: `opencode run --agent conductor-track-executor "test"` still parses.

- [x] 3.2 **Update `conductor-track-validator.md`** to add two checks to its Stage 5/7 prompt load: (a) the test suite is green (`test_command` exit 0 for `code`-type tracks); (b) every spec acceptance criterion has at least one covering test. These are additional required checks; the closeout verdict reflects them.
  - **Authoritative acceptance check:** `Select-String -SimpleMatch 'test suite is green' conductor-track-validator.md` ((the literal phrase)) returns one match; `opencode run --agent conductor-track-validator "test"` parses.
  - Diagnostic checks: none.

---

## Phase 4 — Restart recognition + smoke validation

**Objective:** ensure the new agents are recognized by the Task tool and prove the branched pipeline works end-to-end on two tiny synthetic tracks.

- [x] 4.1 **Instruct the user to restart the OpenCode session** (required: the Task tool caches agents at session start and will throw "Unknown agent type" for the three new agents until restart). Before asking, all three Phase-1 CLI parse checks must be green.
  - **Authoritative acceptance check:** after restart, the user confirms (or the next orchestrator run confirms) that invoking each new agent via the Task tool does NOT throw "Unknown agent type."
  - Diagnostic checks: none.

- [ ] 4.2 **Smoke run A — bookkeeping track** (e.g. a one-line README tweak). Confirm the orchestrator classifies it `bookkeeping` and runs 1->2->3->5(executor)->7->8->9, SKIPPING 4/4b/6 (no test-writer, no test-runner).
  - **Authoritative acceptance check:** the run's execution log shows NO `conductor-test-writer` or `conductor-test-runner` invocation, and Stage 9 (doc-writer) DID run.
  - Diagnostic checks: `metadata.json` `track_type` == `bookkeeping`.
  - **Smoke attempt 2026-07-05:** FAIL/BLOCKED before synthetic run. The user-facing command entrypoint `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md` still instructs the old six-stage pipeline, so Phase 4.2 cannot validate the new bookkeeping route until that P0 control-plane issue is fixed. See `smoke-test-report-2026-07-05.md`.
  - **P0/P1/P2 fixes applied 2026-07-06:** command entrypoint, stage numbering, Stage 7/8 routing, RED/no-framework/doc-safety policy, artifact inventory, read-only boundaries, and Stage 4 test-writer model diversity were patched. Restart OpenCode, then rerun this smoke test. See `p0-p2-fixes-report-2026-07-06.md`.

- [ ] 4.3 **Smoke run B — code track** (a tiny pure function with a spec'd behavior). Confirm stages 4 -> 4b(RED) -> 5(GREEN) -> 6(run) -> 7 -> 8 -> 9 all execute in order; the RED gate observed failing tests before Stage 5; Stage 6 reported green after Stage 5; Stage 9 updated the changelog.
  - **Authoritative acceptance check:** the execution log contains entries for all of: test-writer (RED reported), executor (GREEN), test-runner (green reported), doc-writer (changelog entry), in that order.
  - Diagnostic checks: `test-run-report-*.md` exists and shows passing tests.

- [ ] 4.4 **Negative smoke — RED-gate trip**: craft a code track where the test-writer's tests would pass against existing code (premature green). Confirm the orchestrator's RED gate detects the premature pass and reopens Stage 4 once.
  - **Authoritative acceptance check:** the execution log records a RED-gate reopen event referencing Stage 4, exactly once.
  - Diagnostic checks: none.

---

## Final Phase — Validation & Handover

**Objective:** closeout bookkeeping per the executor closeout synchronization checklist.

- [x] F.1 Synchronize `metadata.json` (status, progress, `executed_at`, `executor_model`, `track_type=bookkeeping` for THIS meta-track since it edits config not code).
- [x] F.2 Upsert the single row in `.conductor\tracks.md` and `.conductor\tracks\ledgers\tracks-ledger.md` with final status + completed date.
- [x] F.3 Write `execution-log-2026-07-05.md` recording changed files, the three new agents, and any deviations.
- [x] F.4 Validator (Stage 7/8) runs and issues a closeout verdict; append the anomaly-log JSONL line per `references/anomaly-logging.md`.

**Authoritative acceptance check (Final Phase):** `metadata.json` status matches the plan checklist; `tracks.md` shows one non-duplicate row for this track; `validation-report-*.md` exists with a verdict.

---

## Execution-readiness checklist
- [ ] All seven Phase-0 decisions recorded.
- [ ] Six backup files exist.
- [ ] `test_command` confirmed for the repo.
- [ ] The three new agent files parse via `opencode run --agent <name> "test"`.
- [ ] Orchestrator `task:` allowlist includes all three new agents.
- [ ] `SKILL.md` 9-stage table + discriminator present.
- [ ] `stage-prompts.md` has Stage 4/6/9 blocks.
- [ ] `threshold-policy.md` has RED-gate + retry-cap rules.
- [ ] Executor re-scoped to GREEN; validator checks test-green.

## Top 3 risks + mitigations
1. **TDD misfire on non-code tracks** => require explicit `track_type`, default `bookkeeping` (skip TDD) when absent.
2. **Test-framework mis-detection** => spec-declared `test_command` in metadata; documented fallback.
3. **Executor behavioral regression** => new pipeline applies to NEW tracks only; in-flight tracks finish on the old 6-stage path.

## First task to execute
**Task 0.1** — present the seven open decisions to the user and record the answers. Nothing downstream can start until the discriminator mechanism (Decision 1) and the agent names (Decision 5) are fixed.



