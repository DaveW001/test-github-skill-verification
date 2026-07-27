# Portfolio Review Report — Top Skills and Agents

**Track:** `20260726-top-skills-agents-review`  
**Generated (UTC):** 2026-07-26T23:45:11+00:00  
**Pipeline:** bookkeeping, `1 -> 2 -> 5 -> 7 -> 9` (Stage 2 retained for broad unversioned global-artifact risk; Stage 3 conditional re-review consumed; manual plan correction closed RR-B1..B5; Stages 3/4/4b/6/8 skipped per threshold policy).  
**Executor model:** `zai-coding-plan/glm-5.2` (variant `high`).

## Methodology and confidence

- **Agents** ranked from **direct** `session.agent` evidence in `opencode.db` (read-only, `?mode=ro`, archived sessions included) — **high confidence**.
- **Skills** ranked from **inferred** `session.title` mentions + operational importance — **low confidence**. There is **no structured skill-call table** in `opencode.db` (event types are message/session lifecycle only; `session.metadata` empty). Codex-local `~/.codex/sessions` exists but was NOT parsed (message bodies; would need a body-redaction contract) — recorded as an evidence gap.
- Weights (frozen in `ranking-contract.json`, SHA-256 `af23dffcad1f`): frequency 0.55, breadth 0.25, recency 0.15, operational-importance 0.05.
- Functional confirmation: 1 skill functionally PASSED (`session-db-query`, exercised read-only in Task 1.1); 19 `FUNCTIONAL_SMOKE_TEST_UNVERIFIED` (credentials/external mutation/orchestration dispatch prohibited). Agent smoke: `AGENT_SMOKE_UNVERIFIED` (live `opencode run` not dispatched — the `opencode` CLI hangs; unbounded session risk).

## Skills (20)

| # | Skill | Conf | Harness | Functional | Major findings | Applied fix |
|---|-------|------|---------|-----------|----------------|-------------|
| 1 | conductor | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 2 | doc | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 3 | clickup | low | FAIL | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | yes (3 file(s)) |
| 4 | conductor-pipeline | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 5 | git-push | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 6 | retrospective | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 7 | skill-creator | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 8 | opencode-scheduler | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 9 | humanizer | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 10 | osgrep | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 11 | diagram-svg | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 12 | pptx-from-layouts | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 13 | pre-delivery-ai-review | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 14 | image-ocr | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 15 | enrich-meeting-notes | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 16 | opencode-event-log-compactor | low | FAIL | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | yes (1 file(s)) |
| 17 | opencode-go-key-rotation | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 18 | root-cause-analysis | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 19 | scheduled-job-best-practices | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | — |
| 20 | session-db-query | low | PASS | FUNCTIONAL_SMOKE_TEST_PASSED | — | — |

## Agents (10)

| # | Agent | Model | Mode | Smoke | Minor findings |
|---|-------|-------|------|-------|----------------|
| 1 | 01-planner | openai/gpt-5.6-luna | primary | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL, AGENT_09_BOUNDED_COMMANDS, AGENT_10_SAFETY_STOPS |
| 2 | build | openai/gpt-5.6-luna | primary | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL, AGENT_09_BOUNDED_COMMANDS, AGENT_10_SAFETY_STOPS |
| 3 | conductor-track-executor | zai-coding-plan/glm-5.2 | subagent | AGENT_SMOKE_UNVERIFIED | — |
| 4 | conductor-track-validator | openai/gpt-5.6-luna | subagent | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL |
| 5 | conductor-plan-reviewer | opencode-go/minimax-m3 | subagent | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL |
| 6 | peer-review | openai/gpt-5.6-sol | subagent | AGENT_SMOKE_UNVERIFIED | AGENT_09_BOUNDED_COMMANDS |
| 7 | conductor-pipeline-orchestrator | openai/gpt-5.6-luna | primary | AGENT_SMOKE_UNVERIFIED | — |
| 8 | conductor-test-runner | openai/gpt-5.6-luna | subagent | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL |
| 9 | conductor-plan-reviewer-alt | openai/gpt-5.6-sol | subagent | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL |
| 10 | conductor-doc-writer | opencode-go/deepseek-v4-flash | subagent | AGENT_SMOKE_UNVERIFIED | — |

## Fixes applied

- **clickup** (3 file(s) changed, `authority_delta: none`): Fixed syntax-only defects in scripts/input_validation.py (8 literal-newline-inside-string literals corrected to \n; systematic corruption) and tests/test_input_validation.py (fixed indentation of f.write inside `with` block + removed a stray duplicated fragment). Removed unreferenced scripts/patch_script.py after Dave explicitly authorized removal; the exact pre-edit recovery copy remains in the track backup.
- **opencode-event-log-compactor** (1 file(s) changed, `authority_delta: none`): Fixed syntax-only PS 5.1 incompatibility in scripts/Switch-ValidatedDatabase.ps1: replaced null-conditional operator `dbHash?.Substring(0,16)` with a PS 5.1-safe `if ($dbHash) { ... Substring }` expression (identical null-safe display behavior).
- **Agent fixes:** none queued (0).

## Validation results

- **clickup** — verdict `PASS`: all applied-fix files PASS syntax; skill-level harness SCRIPT SYNTAX PASS
- **opencode-event-log-compactor** — verdict `PASS`: all applied-fix files PASS syntax; skill-level harness SCRIPT SYNTAX PASS
- **Changed agents:** none → NOT_APPLICABLE.

## Unresolved findings and Dave decisions

- (none)

### Unresolved Major skill finding

- (none)

## Optional improvements and Unverified items

- **Optional (no-fix dispositions):** 41 skill Minor heuristic findings and 11 agent Minor heuristic findings received explicit no-fix dispositions (content/behavior decisions for Dave). See `fix-queue.json`.
- **Unverified:** 19 skills `FUNCTIONAL_SMOKE_TEST_UNVERIFIED`; all 10 agents `AGENT_SMOKE_UNVERIFIED`; agent model routes `AGENT_04/05` Unverified for LIVE availability (config-level evidence only). These are NOT turned into Pass.

- **ClickUp offline diagnostic:** 21/23 unit tests passed. One fixture does not actually exercise an emoji condition; the prioritization import test also exposes missing `run_prioritization.py` / `prioritization_helpers` packaging. These are non-blocking follow-ups for this syntax/removal correction, not a 23/23 pass.

## Reconciliation

```json
{
  "skills": 20,
  "agents": 10,
  "queued_skill_fixes": 2,
  "queued_agent_fixes": 0,
  "applied_skill_changes": 2,
  "skill_no_fix_dispositions": 41,
  "agent_no_fix_dispositions": 11,
  "dave_decisions": 0,
  "validation_pass": 2,
  "validation_partial_preexisting": 0,
  "validation_fail": 0
}
```

Skill entry names: clickup, conductor, conductor-pipeline, diagram-svg, doc, enrich-meeting-notes, git-push, humanizer, image-ocr, opencode-event-log-compactor, opencode-go-key-rotation, opencode-scheduler, osgrep, pptx-from-layouts, pre-delivery-ai-review, retrospective, root-cause-analysis, scheduled-job-best-practices, session-db-query, skill-creator

Agent entry names: 01-planner, build, conductor-doc-writer, conductor-pipeline-orchestrator, conductor-plan-reviewer, conductor-plan-reviewer-alt, conductor-test-runner, conductor-track-executor, conductor-track-validator, peer-review

---
_Report generated from immutable source JSON; counts reconcile to `usage-ranking.json`, `fix-queue.json`, `change-manifest.json`, and `validation-results.json`._