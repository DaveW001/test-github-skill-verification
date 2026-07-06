# Handover: Conductor Pipeline TDD + Documentation Stages

**Track ID:** 20260705-conductor-pipeline-tdd-doc-stages  
**Created:** 2026-07-05  
**Purpose:** Hand off the Conductor pipeline enhancement work to the next OpenCode session so it can implement the planned improvements and the original recommendation set.

---

## 1) What was done in this session

### Research completed
I researched the current Conductor pipeline and related agent standards, then surveyed strong GitHub examples for role-separated agent workflows and TDD/documentation pipelines.

#### Internal Conductor context reviewed
- `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\artifact-output-format.md`

#### Strong GitHub patterns found
Most relevant repositories / patterns:
- `https://github.com/ondrej-svec/hog` — best match to the requested structure. Separate roles for test-writer, implementer, adversarial red-team, and ship/docs. Key insight: implementer cannot see the spec; test-writer cannot see the implementation. Includes RED verification before implementation.
- `https://github.com/sam-agents/sam` — strict RED/GREEN/REFACTOR role split with test writer, developer, reviewer, docs/changelog-style finishing stage.
- `https://github.com/codefather-labs/claude-code-sdlc` — documentation-first + TDD-enforced pipeline with dedicated test-writer, build-runner, verifier, doc-updater.
- `https://github.com/hugo-bluecorn/claude-code-tdd-workflow` — context-isolated TDD agents with hooks that enforce order.
- `https://github.com/elasticLove1/claude-code-tdd` — tester/coder/reviewer split with filesystem boundary rules.
- `https://github.com/affaan-m/everything-claude-code` and `https://github.com/jakezp/everything-opencode` — strong OpenCode doc-updater / tdd-guide / verify patterns.
- `https://github.com/kevinlupera/everything-opencode` — OpenCode agent catalog with `doc-updater`, `tdd-guide`, `e2e-runner`.
- `https://github.com/shariqriazz/opencode-agents-system` — large OpenCode agent system including testing and documentation specialists.
- `https://github.com/openkash/ai-agent-dev-workflow` — artifact-triggered review gates.
- `https://github.com/jpshook/claude-agent-workflow` — includes an auto-documentation phase.

### Web research conclusion
The current best-practice pattern is:
- **spec-driven tests**,
- **separate test-writing and implementation agents**,
- **independent test execution/verification**,
- **final documentation update stage**,
- and ideally **context isolation or strong prompt separation** so tests do not become implementation-synchronized.

---

## 2) Artifacts created in this track

### Spec
`C:\development\opencode\.conductor\tracks\20260705-conductor-pipeline-tdd-doc-stages\spec.md`

### Plan
`C:\development\opencode\.conductor\tracks\20260705-conductor-pipeline-tdd-doc-stages\plan.md`

### Metadata
`C:\development\opencode\.conductor\tracks\20260705-conductor-pipeline-tdd-doc-stages\metadata.json`

### Handover file
`C:\development\opencode\.conductor\tracks\20260705-conductor-pipeline-tdd-doc-stages\handover.md`

### Global index update
A row for this track was appended to:
- `C:\development\opencode\.conductor\tracks.md`

---

## 3) Current status

The track is **plan-drafted-blocked-on-decisions**.

The plan is intentionally paused before implementation because there are open design questions that should be answered before the next session starts modifying agent files and pipeline artifacts.

---

## 4) The most important design conclusions

### A. The biggest missing piece: track-type discrimination
The pipeline must **branch** based on whether a track is code-bearing or bookkeeping/doc/config. TDD stages only make sense for code-bearing tracks.

Recommended approach:
- Add `track_type` to metadata (`code` | `bookkeeping`)
- Default to `bookkeeping` when uncertain
- Only `code` tracks run the test-writer / RED gate / test-runner loop

This is the single most important thing to get right before implementation.

### B. Add a RED-state gate before implementation
Before the executor writes code, the orchestrator must verify that the freshly written tests actually fail.

If tests pass immediately:
- reopen the test-writer once
- do not proceed to implementation until the tests are genuinely RED

### C. Add an independent test-runner stage
The new test-runner should be a read-only verifier that runs the suite and reports results. If the suite fails after implementation, route back to the executor once; after one retry loop, stop and surface the issue.

### D. Documentation belongs at the end, but scope should be explicit
The doc-writer should update at least:
- README / usage docs
- API docs
- changelog / release notes
- ADRs / architecture notes

Potentially also:
- codemaps / architecture maps when structure changes

---

## 5) Improvements added beyond the original recommendation

These were added after the first recommendation set because the broader GitHub research showed them to be important:

1. **Add `lint_command`, `typecheck_command`, and `build_command` metadata** in addition to `test_command`.
   - Reason: several strong workflows treat verification as broader than tests alone.

2. **Add a test-coverage mapping artifact**.
   - The test-writer should produce a mapping from acceptance criteria to test files / test names.
   - This makes validator coverage checks deterministic.

3. **Add file-boundary verification after test-writing and code-writing.**
   - The test-writer should only touch test files and test support.
   - The executor should not modify test files.
   - Use `git diff --name-only` / boundary checks to confirm.

4. **Treat existing tests as read-only unless explicitly approved.**
   - The test-writer can add tests, but should not weaken or silently rewrite existing coverage.

5. **Expand doc-writer scope to include codemaps or architecture maps where relevant.**
   - Especially useful for OpenCode-style doc-heavy workflows.

6. **Consider a quality-runner future enhancement.**
   - Keep the initial name `conductor-test-runner` for compatibility, but let it execute broader quality commands if metadata provides them.

---

## 6) Open decisions the next session must resolve

The plan is blocked until the user answers these:

1. **How should track-type discrimination work?**
   - Recommended: explicit metadata `track_type` field.

2. **Where should the doc-writer run?**
   - Recommended: after re-validation, as the final closeout step.

3. **How strong should context isolation be?**
   - Recommended: prompt-level isolation for v1; hard worktree isolation is a future enhancement.

4. **What model should the doc-writer use?**
   - Recommended: `openai/gpt-5.5` low.

5. **What should the new agent names be?**
   - Recommended: `conductor-test-writer`, `conductor-test-runner`, `conductor-doc-writer`.

6. **Should in-flight tracks migrate to the new pipeline?**
   - Recommended: no. Let existing tracks finish on the old path; apply the new pipeline only to new tracks.

7. **Should metadata include test framework and command fields?**
   - Recommended: yes (`test_framework`, `test_command`).

8. **Should Stage 6 stay narrow, or become a broader quality runner?**
   - Recommended: keep the name `conductor-test-runner`, but allow it to run additional quality commands when metadata provides them.

---

## 7) Next steps for the next OpenCode session

### Step 1 — Resolve the blocked decisions
Answer the open decisions in `spec.md` section 9 / `plan.md` Phase 0 Task 0.1.

### Step 2 — Update the plan if the answers change scope
If the user chooses different defaults, update:
- `spec.md`
- `plan.md`
- any affected metadata fields

### Step 3 — Implement the pipeline wiring
Once decisions are resolved, the next session should update in this order:
1. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`
2. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`
3. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
4. `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`
5. `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md`
6. `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md`
7. create the three new agents:
   - `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md`
   - `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md`
   - `C:\Users\DaveWitkin\.config\opencode\agent\conductor-doc-writer.md`

### Step 4 — Restart the OpenCode session after creating new agents
OpenCode caches agent discovery. After creating new agent markdown files, restart the current session before trying to invoke them via the Task tool.

### Step 5 — Smoke-test the new agents
Use CLI parse checks to verify the new agents are structurally sound:
- `opencode run --agent conductor-test-writer "test"`
- `opencode run --agent conductor-test-runner "test"`
- `opencode run --agent conductor-doc-writer "test"`

### Step 6 — Add an execution smoke test
Run the updated pipeline on:
- one bookkeeping/doc/config track
- one code-bearing track

Verify that:
- bookkeeping tracks skip the TDD stages
- code tracks execute test-writer -> RED gate -> executor -> test-runner -> validator -> doc-writer

---

## 8) Useful references for the next AI

### Best match
- `https://github.com/ondrej-svec/hog`

### Strong supporting examples
- `https://github.com/sam-agents/sam`
- `https://github.com/codefather-labs/claude-code-sdlc`
- `https://github.com/hugo-bluecorn/claude-code-tdd-workflow`
- `https://github.com/elasticLove1/claude-code-tdd`
- `https://github.com/jakezp/everything-opencode/`
- `https://github.com/kevinlupera/everything-opencode`
- `https://github.com/shariqriazz/opencode-agents-system`
- `https://github.com/openkash/ai-agent-dev-workflow`
- `https://github.com/jpshook/claude-agent-workflow`

---

## 9) Important caution

The attempted peer-review invocation in this session was not actually successful because the task tool was unavailable and CLI fallback could not run the subagent. Treat the recommendations in this handover as **planner-authored**, not as an official peer review result.

---

## 10) Suggested handoff summary for the next session

> Implement the Conductor pipeline enhancement so code-bearing tracks run a TDD sequence with a dedicated test-writer, independent test-runner, re-scoped executor, updated validator, and final documentation agent; keep bookkeeping/doc tracks on the simpler path; add metadata-driven track-type discrimination, RED-state verification, test coverage mapping, and stronger file-boundary checks; then smoke-test the new agents and the two branch behaviors.
