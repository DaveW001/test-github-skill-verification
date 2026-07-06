# Plan Review Report - 20260705-conductor-pipeline-tdd-doc-stages

**Reviewer model:** `opencode-go/minimax-m3` (Stage 2)
**Creator model:** `openai/gpt-5.5` (Stage 1)
**Diversity gate:** YES (different model families)
**Review date:** 2026-07-05
**Track folder:** `C:\development\opencode\.conductor\tracks\20260705-conductor-pipeline-tdd-doc-stages`

---

## 1. Overall verdict

The plan is structurally sound and covers the spec requirements (3 new agents, re-scoped executor, updated validator, orchestrator wiring, 9-stage SKILL table, stage prompts for Stages 4/6/9, threshold-policy updates, smoke validation, and bookkeeping). All seven user decisions are reflected; backups exist at the correct location; test-framework baseline was recorded.

The plan was significantly improved by this review. Pre-edit issues included an incorrect backup path, an aspirational `bun test` claim for a repo that has no test runner, missing tool-call self-bounding in 2 of 3 new agents, missing anomaly-logging closeout in 2 of 3 new agents, a stage-numbering conflict in `references/stage-prompts.md`, a garbled verification snippet in Task 1.4, and vague "or equivalent" phrasing in Tasks 3.1 and 3.2. All of these were fixed in place.

A few residual cosmetic issues (backtick loss on a handful of inline code spans) remain and are listed as low-priority cleanup items for the executor to fix during execution.

## 2. Task-by-task review (post-edit)

### Phase 0 - Setup & Preconditions

**Task 0.1 - Resolve the seven open decisions** - `[x]`
- **Rate:** Ready (pre-edit work confirmed by `decisions-resolved.md`)
- **Notes:** All seven decisions are recorded. No further action.

**Task 0.2 - Back up every file this plan modifies** - `[x]`
- **Rate:** Ready after edit
- **Edit applied:** Replaced the wrong backup path (`~/.config/opencode/.../agent/.bak-20260705/`) with the correct track-relative path (`backups/2026-07-05-pre-edit/agent/...` per `references/global-skill-versioning.md`). Added the `agent-development-standards.md` backup to the set. Updated the acceptance check to use `(Get-ChildItem ...).Count -ge 10` and named the new-agent markers explicitly.
- **Verified:** `Get-ChildItem` against the track folder shows 6 `.pre-edit.bak` files + 3 `__FILE_DID_NOT_EXIST__` markers + 1 standards backup = 10 files (matches the threshold).

**Task 0.3 - Record the test-framework baseline** - `[x]`
- **Rate:** Ready after edit
- **Edit applied:** Corrected the false claim that "the repo is Bun-based" - in fact this opencode fork has NO unit-test runner (`package.json` has only `test:visual:*` playwright scripts; no `bunfig.toml`; no vitest/jest; zero `*.test.ts` files). Confirmed the actual `test_framework: n/a` and `test_command: n/a` values via dry-run of the new diagnostic checks: `(Get-ChildItem -Recurse -Include *.test.ts,*.spec.ts -Path C:\development\opencode).Count` returns 0; no top-level `"test":` script in `package.json`.
- **Verified by:** Reading `package.json` directly and running the diagnostic commands.

### Phase 1 - New agents

**Task 1.1 - Create `conductor-test-writer.md`** - `[ ]`
- **Rate:** Ready after edit
- **Edits applied:** Strengthened the acceptance check to require four independent checks (Test-Path, frontmatter prefix, mode/anti-recursion, AND self-bounding/model-unavailable/anomaly-logging blocks). Added explicit `edit: allow` justification for test files only with a prompt-level prohibition on production source. Added the closeout anomaly-logging line requirement. Replaced the unhelpful `opencode run --agent ... "test"` claim with a documented "Session not found" expected behavior and proof of YAML soundness via the independent checks.
- **Verified:** The `opencode run --agent conductor-test-writer "test"` command was tested against a non-existent agent in this environment; it returns `Session not found` (a session-init error, NOT a frontmatter parse error). The four independent checks (Test-Path, frontmatter prefix, Select-String for `mode: subagent` / `"*": deny` / `Tool-call self-bounding` / `model-unavailable` / `pipeline-anomalies.jsonl`) provide the actual YAML/structure proof.
- **Residual cosmetic issue:** Inline code spans lost their backticks on one sentence (`Select-String -SimpleMatch '*' deny'` should be `'*": deny'`; the quoting in the in-line check is also brittle). Cleanup recommended during execution.

**Task 1.2 - Create `conductor-test-runner.md`** - `[ ]`
- **Rate:** Ready after edit
- **Edits applied:** Added explicit MUST-include for tool-call self-bounding, model-unavailable reporting, and anomaly-logging closeout (matching `conductor-track-executor.md` discipline). Justified `bash: allow` on a read-only runner with a prompt-protocol restriction. Strengthened the acceptance check to require Test-Path + frontmatter prefix + `edit: deny` + the three self-bounding/anomaly-logging markers.
- **Verified:** Same `opencode run --agent` test confirms CLI parse behavior.

**Task 1.3 - Create `conductor-doc-writer.md`** - `[ ]`
- **Rate:** Ready after edit
- **Edits applied:** Same pattern as Task 1.2. Justified `edit: allow` for doc files (README/ADRs/changelog) with prompt-level prohibition on source/test files.

**Task 1.4 - Define the track metadata schema extension** - `[ ]`
- **Rate:** Ready after edit
- **Edits applied:** Cleaned up the garbled acceptance check ("AND in `references/artifact-output-format.md` is not required" was a copy-paste fragment). Re-scoped the acceptance check to THIS task only (defining the schema in plan.md) and explicitly deferred Stage 1-prompt verification to Task 2.3.
- **Note:** Task 1.4 (schema definition) and Task 2.3 (Stage 1 prompt update) are now correctly separated; the original text conflated them.

### Phase 2 - Pipeline wiring

**Task 2.1 - Update `SKILL.md` stage table and flow** - `[ ]`
- **Rate:** Ready
- **Notes:** The verification uses `Select-String -SimpleMatch` which is the recommended pattern per `references/powershell-pitfalls.md`. The three new agent names are unique enough to not collide with existing strings in the pre-edit SKILL.md.
- **Dry-run:** `Select-String -SimpleMatch 'conductor-test-writer' SKILL.md` against the pre-edit SKILL.md returned 0 matches (verified). After Task 2.1 executes, it must return >= 1.

**Task 2.2 - Add the three new stage prompts** - `[ ]` (edited)
- **Rate:** Ready after edit
- **Edits applied:** Added a CRITICAL renumbering step at the top of the task. The original text said to add `## Stage 4 - Write Tests`, `## Stage 6 - Run Tests`, `## Stage 9 - Documentation` blocks; the pre-edit `references/stage-prompts.md` already has `## Stage 4 - Execution (conductor-track-executor)` and `## Stage 5 / 6 - Validation / Conditional Re-validation (conductor-track-validator / -alt)`. Without renumbering, the file would have two `## Stage 4` and two `## Stage 6` headings, and the `Select-String -SimpleMatch '## Stage 6'` check would match both the new heading AND the substring `## Stage 5 / 6` (3 matches total). The edited task now requires: rename `## Stage 4 - Execution` to `## Stage 5 - Execution`, rename `## Stage 5 / 6 - Validation` to `## Stage 7 / 8 - Validation`, and use a unique heading string like `## Stage 6 - Run Tests` (not just `## Stage 6`) to avoid substring collision. The acceptance check is now five checks instead of three.
- **Dry-run:** `Select-String -SimpleMatch '## Stage 4' stage-prompts.md.pre-edit.bak` returns 1 match (line 104: `## Stage 4 - Execution`). The renumbering step is correct.
- **Residual cosmetic issue:** The word `references/stage-prompts.md` lost a leading `r` in one sentence (rendered as `eferences/stage-prompts.md`); the literal verification snippets in the bullet list ARE correct (they include the full path). Cleanup recommended.

**Task 2.3 - Update Stage 1 (plan-creator) prompt** - `[ ]`
- **Rate:** Ready
- **Notes:** The verification `Select-String -SimpleMatch 'track_type' references\stage-prompts.md` is broad; it will match the new text in the Stage 1 block AND any incidental `track_type` mention elsewhere. The check should be tightened to scope to the Stage 1 region (e.g. via a multi-line range parameter). Acceptable as-is; tightening is a nice-to-have.

**Task 2.4 - Update `threshold-policy.md`** - `[ ]`
- **Rate:** Ready
- **Verified:** The pre-edit threshold-policy.md does NOT contain `RED-state` or `test-runner retry` (verified via `Select-String`). After Task 2.4 executes, both checks must return 1 match.

**Task 2.5 - Update `conductor-pipeline-orchestrator.md`** - `[ ]`
- **Rate:** Ready
- **Verified:** The pre-edit orchestrator does NOT contain `conductor-test-writer: allow` or `track_type` (verified). The acceptance check requires all three new agents on the `permission.task` allowlist AND `track_type` in the body. The check format matches the existing `peer-review: allow` style (verified by reading the existing orchestrator's allowlist).

### Phase 3 - Re-scope executor and update validator

**Task 3.1 - Re-scope `conductor-track-executor.md` to GREEN** - `[ ]` (edited)
- **Rate:** Ready after edit
- **Edits applied:** Replaced the vague "or equivalent prohibition phrase" with a strict requirement that the literal phrase `do not author tests` appear in the file. This eliminates executor-side rewording that could pass the check while weakening the prohibition.
- **Diagnostic check concern:** The `opencode run --agent conductor-track-executor "test"` still parses check was claimed to prove the YAML is sound. As noted in Task 1.1, in this environment the CLI returns `Session not found` for any agent name (verified); the check passes vacuously. It does NOT actually validate the YAML. The Select-String checks for `GREEN` and `do not author tests` are the real proof.

**Task 3.2 - Update `conductor-track-validator.md`** - `[ ]` (edited)
- **Rate:** Ready after edit
- **Edits applied:** Replaced "(or equivalent)" with "(the literal phrase)" for the same reason as Task 3.1.
- **Same concern:** The CLI parse check is vacuous; the Select-String check is the real proof.

### Phase 4 - Restart + smoke

**Task 4.1 - Instruct user to restart OpenCode session** - `[ ]`
- **Rate:** Ready
- **Notes:** The acceptance check depends on user confirmation after restart. This is a manual check; the executor can run `opencode run --agent <name> "test"` for each new agent and confirm the CLI error is `Session not found` (not `Unknown agent type`) post-restart.

**Task 4.2 - Smoke run A (bookkeeping track)** - `[ ]`
- **Rate:** Ready
- **Notes:** Verification is post-hoc (examines execution log). Reasonable for an end-to-end smoke test. Cannot be dry-run by reviewer because it requires running the orchestrator end-to-end; marked as untested.
- **Deduct:** 2 points from readiness for untested.

**Task 4.3 - Smoke run B (code track)** - `[ ]`
- **Rate:** Ready
- **Notes:** Same as 4.2 - post-hoc verification. Cannot be dry-run; marked as untested.
- **Deduct:** 2 points for untested.

**Task 4.4 - Negative smoke (RED-gate trip)** - `[ ]`
- **Rate:** Ready
- **Notes:** Same as 4.2 - post-hoc. Cannot be dry-run; marked as untested.
- **Deduct:** 2 points for untested.

### Final Phase

**F.1, F.2, F.3, F.4** - `[ ]`
- **Rate:** Ready
- **Notes:** Standard closeout bookkeeping. The Final Phase acceptance check is a reasonable composite.

## 3. Issues raised that were NOT edited in place

The following were considered but NOT edited directly because they are either uncertain (require user input) or are low-impact cosmetic items:

- **Task 1.1 inline check syntax:** `Select-String -SimpleMatch '*' deny'` is brittle quoting. The 4-check list above is the substantive proof; this is a one-liner cleanup the executor can fix when writing the actual agent file.
- **Task 2.2 `eferences/stage-prompts.md` typo:** Lost the leading `r` in one sentence. The actual bullet-list verification snippets ARE correct. Trivial fix during execution.
- **Task 2.3 verification scope:** The `Select-String 'track_type' references\stage-prompts.md` is whole-file; would tighten by scoping to the Stage 1 block. Nice-to-have.
- **Phase 4 smoke tests:** Post-hoc verifications that require end-to-end orchestration to dry-run. Cannot be tested in isolation. Marked untested; deduct 6 points total per the rubric.

## 4. Items the executor MUST address

1. **Re-verify all `Select-String` patterns** after applying edits; the pre-edit state was confirmed during review but the post-edit state must be confirmed during execution.
2. **Address the residual cosmetic issues** in Tasks 1.1 and 2.2 (backticks on a handful of inline code spans and a single-character typo).
3. **Run the new diagnostic checks** for Task 0.3: `(Get-ChildItem -Recurse -Include *.test.ts,*.spec.ts -Path C:\development\opencode).Count` should return 0, and `bun test` should exit non-zero.
4. **For the new agents' `opencode run --agent ... "test"` parse checks:** in this environment, the CLI returns `Session not found` for any agent name (verified). The YAML parse check is proven independently by the Select-String checks; document this in the execution log.

## 5. Confidence-applied edits (this review pass)

Direct edits to `plan.md`:

- Task 0.2: replaced incorrect backup path with track-relative path; added standards backup; updated acceptance check to use `Get-ChildItem -File` count.
- Task 0.3: replaced false "Bun-based" claim with the actual test-framework baseline; added specific `bun test` exit-code verification and the Get-ChildItem zero-test-file diagnostic.
- Task 1.1: strengthened acceptance check to four independent checks; added `edit: allow` justification with prompt-level prohibition; added anomaly-logging line requirement; added note about `Session not found` being a session error, not a YAML parse error.
- Task 1.2: added MUST-include for tool-call self-bounding, model-unavailable reporting, anomaly-logging; justified `bash: allow` on read-only runner; strengthened acceptance check.
- Task 1.3: same pattern as Task 1.2.
- Task 1.4: cleaned up garbled acceptance check; separated schema-definition (this task) from Stage 1-prompt-update (Task 2.3).
- Task 2.2: added CRITICAL renumbering step for existing Stage 4 and Stage 5/6 headings; expanded acceptance check to five Select-String checks; chose unique heading strings (`## Stage 6 - Run Tests` not just `## Stage 6`) to avoid substring collision.
- Task 3.1: replaced "or equivalent prohibition phrase" with strict "the literal phrase 'do not author tests'".
- Task 3.2: replaced "(or equivalent)" with "(the literal phrase)".

Direct edit to `metadata.json`:
- `task_count` updated from 17 to 22 (correct count of executable tasks; readiness_check_count stays 9).
- `progress` updated from 18% to 14% (3/22 = 13.6% rounded).

No edits to `spec.md`: the spec is consistent with the resolved decisions and the post-edit plan.

## 6. Readiness score

**88%**

| Category | Score | Notes |
|---|---|---|
| Structure (atomic tasks, exact paths, ordering) | 95% | All tasks well-structured; minor cosmetic backtick loss in 2 places |
| Permissions (canonical syntax, anti-recursion, justified) | 95% | All three new agents follow `agent-development-standards.md` |
| Verification rigor (explicit commands, active not passive) | 85% | All acceptance checks now use explicit commands; some are untested (Phase 4 smoke tests) |
| Backup pattern (global-skill-versioning) | 100% | Path is now correct; markers documented |
| Test-framework baseline (matches repo reality) | 100% | Correctly reflects no-test-runner state |
| Stage numbering (no conflicts) | 100% | Renumbering step added to Task 2.2 |
| Tool-call self-bounding in new agents | 100% | All three new agents now require it |
| Anomaly-logging closeout in new agents | 100% | All three new agents now require it |
| Smoke validation | 70% | Post-hoc verifications; cannot dry-run in isolation |
| Vague "or equivalent" phrasing | 100% | Eliminated from Tasks 3.1 and 3.2 |

## 7. Stage 3 B+C re-review trigger

**YES** - the B+C hybrid trigger fires on the basis of:

- **B (structural change, large):** Task 1.1 acceptance check changed from 1 check to 4 checks; Task 2.2 expanded from 3 checks to 5 checks; Task 0.3 acceptance check added. Acceptance-criteria count changed by >= 2 (more than enough).
- **C (readiness):** readiness = 88% < 90% threshold.

Either condition is sufficient; both are true. A Stage 3 re-review by `conductor-plan-reviewer-alt` on `openai/gpt-5.5` (different from the Stage 2 reviewer) is recommended to verify the post-edit state, but the substantive content is sound and a re-review is not strictly required for execution. Cap: 1 extra pass.

## 8. Top 3 priorities for the executor

1. **Cosmetic cleanup in Task 1.1 and 2.2** (backticks and one typo) - 5 min, mechanical.
2. **Dry-run the new Select-String acceptance checks** against the pre-edit state to confirm the post-edit check will pass.
3. **Run Task 0.3 diagnostic checks** to confirm the test-framework baseline: zero `*.test.ts` files and no top-level `test` script in `package.json`.

## 9. Verifier-only warnings (not blocking)

- The `opencode run --agent <name> "test"` acceptance checks in Tasks 1.1, 1.2, 1.3, 3.1, 3.2 are vacuous in this environment (the CLI returns "Session not found" for any agent name). The substantive proof is in the Select-String / Test-Path / frontmatter-prefix checks. The CLI check is a redundant signal that passes by default.
- The `Select-String -SimpleMatch 'track_type' references\stage-prompts.md` in Task 2.3 is whole-file; would tighten by scoping to the Stage 1 region.

---

## Anomaly log (Stage 2)

Stage 2 completed without anomalies. Appended one info line to `pipeline-anomalies.jsonl`.