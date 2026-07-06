# Spec: Conductor Pipeline TDD + Documentation Stages

**Track ID**: 20260705-conductor-pipeline-tdd-doc-stages
**Created**: 2026-07-05
**Author**: 01-Planner
**Status**: Spec complete — awaiting user decisions on open questions, then plan review

---

## 1. Goal / Outcome

Extend the six-stage Conductor pipeline into a TDD-disciplined, documentation-closing pipeline by inserting three specialized stages and three new subagents:

1. **Write tests first** (RED) — a new `conductor-test-writer` agent authors failing tests from the spec/plan acceptance criteria **before** any implementation code is written.
2. **Write code** (GREEN) — the existing `conductor-track-executor`, re-scoped to write implementation code that makes the tests pass, and **no longer authors tests**.
3. **Test the code** — a new `conductor-test-runner` agent independently runs the suite and reports pass/fail (read-only; does not fix code).
4. **Validate** — the existing `conductor-track-validator`, updated to also confirm the test suite is green and that tests cover acceptance criteria.
5. **Update documentation** — a new `conductor-doc-writer` agent runs at the end to keep README, API docs, changelog, and ADRs in sync with the implemented change.

The outcome is a pipeline where tests are written adversarially from the spec (not from the implementation the same agent is about to write), where an independent model runs the tests, and where documentation never drifts from shipped code.

## 2. Why (problem being solved)

- The current executor both writes code **and** writes tests. This creates the dominant AI-coding failure mode identified across the research: **tests that pass by construction** — the agent writes tests that merely assert the behavior of the code it just wrote, so the feedback loop collapses and regressions hide.
- There is no independent test-execution stage; the executor marks its own homework.
- Documentation (README, API docs, changelog, ADRs) is never systematically updated by the pipeline, so it drifts from the code after every change.

## 3. Constraints / Non-Goals

### Constraints
- **Follow `~/.config/opencode/agent-development-standards.md`** for all agent creation (canonical `permission:` syntax, anti-recursion `task: { "*": deny }` for subagents, `bash: allow` even on read-only agents due to the Bun-fallback runtime, etc.).
- **Preserve the existing model-diversity guarantee** (reviewer != creator; validator != executor). The new test-writer and test-runner stages must add diversity, not collapse it.
- **Do not break non-code tracks.** The pipeline currently handles documentation, skill, config, and agent-config tracks. TDD stages are meaningless for those and MUST be conditionally skipped.
- **OpenCode has no native per-agent worktree isolation** (unlike hog's git-worktree-per-agent model). v1 uses prompt-level isolation; hard sandboxing is out of scope.
- **Native file tools (`Read`/`Write`/`Edit`) fail with `Bun is not defined`** in this environment. New agents must be shell-first (PowerShell via the `bash` tool) and follow `references/artifact-output-format.md` for writing artifacts.

### Non-Goals (v1)
- Adversarial test augmentation by the test-runner (it runs the suite; it does not write new failing tests to break the impl — that is a v2 "red-team" upgrade).
- Full git-worktree isolation per agent (v2, pending platform support).
- Parallel story execution (the pipeline stays sequential per track).
- A `conductor-arbitrator` subagent (already a reserved extension hook in `threshold-policy.md`).

## 4. Proposed Pipeline (after enhancement)

Stages grouped into three clusters. **TDD cluster stages run ONLY for code-bearing tracks** (see track-type discriminator, section 5).

### Planning cluster (unchanged)
| # | Stage | Agent | Model |
|---|-------|-------|-------|
| 1 | Plan creation | conductor-plan-creator | openai/gpt-5.5 (low) |
| 2 | Plan review | conductor-plan-reviewer | opencode-go/minimax-m3 |
| 3 | Conditional re-review | conductor-plan-reviewer-alt | openai/gpt-5.5 (low) |

### TDD cluster (NEW — code-bearing tracks only)
| # | Stage | Agent | Model | Write? |
|---|-------|-------|-------|--------|
| 4 | Write tests (RED) | **conductor-test-writer** (NEW) | openai/gpt-5.5 (low) | edit: allow (test files only) |
| 4b | RED-state verification gate | orchestrator logic (not an agent) | — | runs suite; tests MUST fail |
| 5 | Write code (GREEN) | conductor-track-executor (RE-SCOPED) | zai-coding-plan/glm-5.2 | edit: allow; NO test authoring |
| 6 | Run tests (verify) | **conductor-test-runner** (NEW) | opencode-go/minimax-m3 | edit: deny (read-only runner) |

### Closeout cluster
| # | Stage | Agent | Model | Write? |
|---|-------|-------|-------|--------|
| 7 | Validation | conductor-track-validator (UPDATED) | opencode-go/minimax-m3 | edit: deny |
| 8 | Conditional re-validation | conductor-track-validator-alt | openai/gpt-5.5 (low) | edit: deny |
| 9 | Documentation (NEW) | **conductor-doc-writer** (NEW) | openai/gpt-5.5 (low) | edit: allow (docs only) |

### Diversity log (per-gate)
- Test-writer (gpt-5.5) != executor (glm-5.2). OK.
- Test-runner (minimax-m3) != executor (glm-5.2). OK — genuine cross-check.
- Doc-writer (gpt-5.5) != executor (glm-5.2). OK.
- Validator (minimax-m3) != executor (glm-5.2). OK (unchanged).

## 5. The track-type discriminator (MOST IMPORTANT missing piece)

This is the single biggest thing to think about that is not in the original request.

The Conductor pipeline runs over heterogeneous work: TypeScript code, but also markdown skills, JSON config, agent frontmatter, reference docs. **TDD (write-tests -> code -> run-tests) is meaningless for a non-code deliverable.** Forcing a test-writer onto a SKILL.md edit would produce nonsense or stall.

**Decision needed:** how does the orchestrator classify a track?
- **Option A (recommended):** the plan-creator declares a `track_type` field in `metadata.json` (`code` | `bookkeeping`). The orchestrator reads it and routes code-bearing tracks through the TDD cluster; bookkeeping/doc/config tracks skip stages 4/4b/6 and go straight 1->2->3->5(executor)->7->8->9.
- **Option B:** the orchestrator heuristically inspects which files the plan touches (`.ts`/`.py`/etc. => code; `.md`/`.json` => bookkeeping). More fragile.

Either way, the pipeline MUST branch. This is gated as an open question in section 9.

## 6. RED-state verification gate (second missing piece)

Before the code-writer (Stage 5) runs, the orchestrator verifies the test suite is actually RED (failing). This is hog's `verifyRedState` pattern and the AugmentCode/VS-Code "tests must fail first" rule from the research.

- If the freshly-written tests PASS immediately => the tests are asserting existing behavior, not new behavior. **Reopen Stage 4** (test-writer) once.
- If tests FAIL => proceed to Stage 5 (GREEN).
- This gate is orchestrator logic (a bounded `bash` test-suite run), not a separate agent.

Without this gate, the test-writer can write tests that already pass, defeating the entire TDD purpose.

## 7. Test-runner failure loop (third missing piece)

When Stage 6 (test-runner) reports failures after implementation:
1. Route back to Stage 5 (code-writer) **once**, with the test-runner's failure report as input.
2. Re-run Stage 6.
3. If still failing after one retry loop => stop and surface to the user (mirrors the existing "route back to execution once, then stop" validation rule in `threshold-policy.md`).

A retry cap MUST be defined; otherwise the pipeline can loop forever between writer and runner.

## 8. Documentation agent scope (fourth missing piece)

Per the Perplexity research (Addy Osmani / Arun Gupta, 2025-2026), the doc-writer should read the updated spec + code (public API surface) + tests + commit metadata, and update:
- **README / usage docs** — when public APIs or setup steps change.
- **API docs** — functions, endpoints, schemas (param names/types matching tests + spec).
- **Changelog** — append an Added/Changed/Fixed entry from the spec diff + test results.
- **ADRs** — when an architectural or NFR-driven decision is made.

**Decision needed:** does the doc-writer run BEFORE validation (so docs are part of the validated deliverable) or AFTER re-validation as a true closeout step? The user said "at the end," so the spec assumes **after re-validation (Stage 9)**. Flagged in section 9.

## 9. Open decisions requiring user input BEFORE execution

These are deferred to the user. The plan.md marks the corresponding tasks as BLOCKED until resolved.

1. **Track-type discriminator mechanism** — Option A (metadata `track_type` field) vs Option B (heuristic file inspection). Recommendation: A.
2. **Doc-writer position** — before validation (docs validated) vs after re-validation (true closeout). User phrasing implies after; confirm.
3. **Context-isolation level** — v1 prompt-level isolation (test-writer instructed to write from spec, not to read impl) vs full isolation (hard, needs platform worktree support). Recommendation: v1 prompt-level.
4. **Doc-writer model** — gpt-5.5 (low) (good prose, differs from executor) vs qwen3.7-plus (spreads load). Recommendation: gpt-5.5 (low).
5. **Agent naming** — `conductor-test-writer` / `conductor-test-runner` / `conductor-doc-writer` (recommended, consistent with existing `conductor-*` convention) vs alternatives (`conductor-track-tester`, `conductor-documenter`).
6. **Existing in-flight tracks** — do we migrate them to the new model or let them finish on the old 6-stage path? Recommendation: let them finish; new pipeline applies to new tracks only.
7. **Test framework declaration** — should `track_type` metadata also carry a `test_framework` + `test_command` field (e.g. `bun test`, `vitest run`, `pytest`) so agents don't have to detect it each run? Recommendation: yes.

## 10. Files affected

### NEW files (3 agents)
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-writer.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-doc-writer.md`

### MODIFIED files (pipeline wiring)
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` — new stages 4/4b/6/9, track-type branching, `task:` allowlist additions, RED gate + test-runner retry logic.
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md` — re-scope to GREEN/code-only; remove test authoring; add "tests already exist, make them pass" guidance.
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md` — add test-suite-green + acceptance-coverage checks.
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` — new model table (9 stages), updated stage flow, track-type discriminator section.
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` — Stage 4 (test-writer), Stage 6 (test-runner), Stage 9 (doc-writer) prompt blocks.
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md` — RED-gate definition, test-runner retry cap (1), doc-stage rules.
- `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md` — optional: add a note that TDD-pipeline agents follow the `conductor-test-*` / `conductor-doc-*` naming.

### Research references (informed this spec, not edited)
- hog (ondrej-svec/hog) — structural role separation, RED verification, ship/docs agent. Closest architectural match.
- sam-agents/sam — Titan (RED) / Dyna (GREEN) / Argus (refactor) role split.
- openkash/ai-agent-dev-workflow — artifact-triggered review gates (review-plan + review-impl).
- t1/tdder — TDD + clean-code skills, OpenCode-compatible.
- jakezp/everything-opencode + kevinlupera/everything-opencode — OpenCode-native `doc-updater`, `tdd-guide`, `e2e-runner` agents to model on.
- shariqriazz/opencode-agents-system — 79-agent catalog incl. unit/integration/e2e testing + technical-writer/code-documenter/api-documenter/changelog-maintainer doc agents.
- Perplexity research: context-isolation + doc-agent best practices (Osmani, Gupta, Abrahami, AugmentCode, VS Code TDD agents).

## 11. Definition of Done

- Three new agents exist, pass CLI frontmatter parse (`opencode run --agent <name> "test"`), and follow agent-development-standards.
- Orchestrator routes a code-bearing track through all 9 stages and a bookkeeping track through the 6-stage path (skipping 4/4b/6).
- RED gate correctly reopens the test-writer when tests pass prematurely.
- Test-runner reports a real failure and the orchestrator retries Stage 5 once then stops.
- Doc-writer updates README + changelog for a sample change.
- Validator confirms test-green + acceptance coverage before closeout.
- Session restart documented; new agents recognized by the Task tool after restart.
- All Conductor bookkeeping (metadata.json, tracks.md, tracks-ledger.md, anomaly log) updated per protocol.

## 12. Top risks

1. **TDD stages misfire on non-code tracks** if the discriminator is wrong => nonsense tests or stalls. Mitigation: require explicit `track_type` metadata; default to `bookkeeping` (skip TDD) when absent.
2. **Test framework mis-detection** => test-writer emits the wrong runner syntax. Mitigation: spec-declared `test_command` in metadata; fall back to detection with a documented guess.
3. **Model-unavailable on a new stage** => pipeline stalls. Mitigation: each new stage follows the existing "report model-unavailable, stop, ask user" rule (no new fallback chains in v1).
4. **Cost/latency inflation** => 3 extra stages on every code track. Mitigation: the discriminator skips TDD for non-code tracks; the RED gate + retry cap bound loops.
5. **Behavioral regression on the executor** => re-scoping executor to code-only may break existing in-flight tracks that relied on it writing tests. Mitigation: new pipeline applies to new tracks only; document the change in the executor agent body.
