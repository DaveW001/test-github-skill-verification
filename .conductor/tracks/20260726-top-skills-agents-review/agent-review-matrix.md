# Agent Review Matrix

Track: `20260726-top-skills-agents-review`. One entry per selected agent (10). Every frozen agent rubric item is recorded in each packet under `review-batches/agents/<name>.json`.

Model/variant route evidence is config-level: live `opencode models` hangs in this environment (verified, not retried), so AGENT_04/05 are recorded `Unverified` for LIVE availability with config-level supporting evidence from `opencode.jsonc`. No route was changed.

Agent smoke (`AGENT_13`) is `AGENT_SMOKE_UNVERIFIED`: a live `opencode run` session is not dispatched because the `opencode` CLI hangs and a live session cannot be bounded to the 20-tool-call/10K-token cap from the dispatch side. Fixture-only prompt records are saved under `evidence/agent-smoke-tests/`. No model was substituted.

| # | Agent | Model | Mode | Smoke | Fails | Pass/NA/Unv |
|---|-------|-------|------|-------|-------|-------------|
| 1 | 01-planner | None | None | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL, AGENT_09_BOUNDED_COMMANDS, AGENT_10_SAFETY_STOPS | 9/2/2 |
| 2 | build | None | None | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL, AGENT_09_BOUNDED_COMMANDS, AGENT_10_SAFETY_STOPS | 9/2/2 |
| 3 | conductor-track-executor | None | None | AGENT_SMOKE_UNVERIFIED | — | 13/0/3 |
| 4 | conductor-track-validator | None | None | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL | 12/0/3 |
| 5 | conductor-plan-reviewer | None | None | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL | 12/1/2 |
| 6 | peer-review | None | None | AGENT_SMOKE_UNVERIFIED | AGENT_09_BOUNDED_COMMANDS | 11/1/3 |
| 7 | conductor-pipeline-orchestrator | None | None | AGENT_SMOKE_UNVERIFIED | — | 13/0/3 |
| 8 | conductor-test-runner | None | None | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL | 12/0/3 |
| 9 | conductor-plan-reviewer-alt | None | None | AGENT_SMOKE_UNVERIFIED | AGENT_08_WINDOWS_PATH_SHELL | 12/0/3 |
| 10 | conductor-doc-writer | None | None | AGENT_SMOKE_UNVERIFIED | — | 13/0/3 |

## Queued agent fixes (Critical/Major)

- (none — zero high-confidence Critical/Major agent defects)

## No-fix dispositions (Minor heuristic findings)

- `01-planner` `AGENT_08_WINDOWS_PATH_SHELL` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `01-planner` `AGENT_09_BOUNDED_COMMANDS` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `01-planner` `AGENT_10_SAFETY_STOPS` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `build` `AGENT_08_WINDOWS_PATH_SHELL` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `build` `AGENT_09_BOUNDED_COMMANDS` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `build` `AGENT_10_SAFETY_STOPS` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `conductor-track-validator` `AGENT_08_WINDOWS_PATH_SHELL` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `conductor-plan-reviewer` `AGENT_08_WINDOWS_PATH_SHELL` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `peer-review` `AGENT_09_BOUNDED_COMMANDS` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `conductor-test-runner` `AGENT_08_WINDOWS_PATH_SHELL` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files
- `conductor-plan-reviewer-alt` `AGENT_08_WINDOWS_PATH_SHELL` (Minor): heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe auto-fix; detection may also miss guidance present in referenced pattern files