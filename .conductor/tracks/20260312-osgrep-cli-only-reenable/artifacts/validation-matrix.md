# Validation Matrix: Osgrep CLI-Only Re-Enablement

**Track ID**: 20260312-osgrep-cli-only-reenable
**Date**: 2026-03-12

## Run Summary

- Run owner: OpenCode 01-Planner session
- Environment: Windows, repo `C:\development\opencode`
- OpenCode version: not captured in-session
- Agent: 01-Planner
- Result: FAIL (canary not ready for full rollout)
- Timeout policy: 30 seconds per invocation
- Retry policy: no automatic retries in this run; failures evaluated directly

## Test Cases

| ID | Scenario | Prompt | Expected | Actual | Evidence Link | Pass/Fail | Notes |
|---|---|---|---|---|---|---|---|
| TC-01 | Code-path discovery | find code path for auth token refresh | osgrep invoked before fallback | Invocation occurred, exited `1` with `Table 'chunks' already exists` | `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc01-code-path\result.json` | FAIL | Reliability error in first-run canary query |
| TC-02 | Cross-file impact | find where feature flag X is read and written | osgrep invoked and cited | Invocation occurred, exited `1` with same chunks-table error | `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc02-feature-flag\result.json` | FAIL | Same failure mode as TC-01 |
| TC-03 | Refactor scoping | locate all call sites of function Y and related interfaces | semantic osgrep use | Exit `0`, returned cross-file matches, completed in `15.689s` | `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc03-refactor-scope\result.json` | PASS | Indexing triggered during search |
| TC-04 | Large repo | semantic query in C:\development\opencode | completes within timeout budget | Exit `0`, completed in `1.275s`, but stderr showed FTS inverted-index warning and no matches | `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc04-large-repo\result.json` | FAIL | Functional quality issue despite fast completion |
| TC-05 | Spaced path | semantic query in path with spaces | no path parsing regression | Index and search both exit `0` in spaced path | `C:\development\opencode\logs\osgrep-debug\20260312-155521-tc05-spaced-path-index\result.json`; `C:\development\opencode\logs\osgrep-debug\20260312-155530-tc05-spaced-path-search\result.json` | PASS | Path-with-spaces handling works |
| TC-06 | MCP guardrail | normal automation run | no osgrep mcp usage | No command in this run used `osgrep mcp`; all commands were CLI subcommands | `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc03-refactor-scope\result.json` | PASS | Guardrail respected |
| TC-07 | Fallback behavior | forced osgrep failure | grep/glob/read fallback works | Forced invalid cwd failure captured; fallback completed using grep | `C:\development\opencode\logs\osgrep-debug\20260312-155552-tc07-forced-failure\result.json` | PASS | Grep fallback found target symbol |
| TC-08 | Concurrent queries | two semantic prompts in one session | no hang under concurrent load | Both concurrent runs exited `0` in ~`1.24s`/`1.23s` | `C:\development\opencode\logs\osgrep-debug\20260312-155610-tc08-concurrent-a\result.json`; `C:\development\opencode\logs\osgrep-debug\20260312-155610-tc08-concurrent-b\result.json` | PASS | No timeout/hang observed |
| TC-09 | Query during index | run semantic query while index activity exists | stable behavior or explicit graceful fallback | Index and query launched together; both exited `0` | `C:\development\opencode\logs\osgrep-debug\20260312-155634-tc09-index-active\result.json`; `C:\development\opencode\logs\osgrep-debug\20260312-155634-tc09-query-during-index\result.json` | PASS | No blocking conflict observed |
| TC-10 | Known-answer query | prompt with known repo answer | non-empty relevant results | After reindex, `staleIndexSymbol` definition returned from expected file | `C:\development\opencode\logs\osgrep-debug\20260312-155714-tc10-known-answer-search\result.json` | PASS | Expected symbol appears in output |
| TC-11 | Stale index query | semantic query with stale index state | succeeds or degrades cleanly with fallback | Pre-reindex query returned noisy unrelated matches and missed expected symbol | `C:\development\opencode\logs\osgrep-debug\20260312-155704-tc11-stale-index-search\result.json` | FAIL | Stale index behavior not cleanly handled |
| TC-12 | Large result set | broad semantic query with many hits | completes within timeout budget | Exit `0`, completed in `1.175s`, returned broad matches | `C:\development\opencode\logs\osgrep-debug\20260312-155726-tc12-large-result-set\result.json` | PASS | Large-result query completed within budget |

## Aggregate Criteria

- Required pass threshold: 5/5 for TC-01 through TC-05.
- Safety criteria: TC-06 and TC-07 must pass.
- Extended reliability criteria: TC-08 through TC-12 should pass before full rollout.
- Any MCP usage in normal path is an automatic no-go.
- Per-invocation timeout: 30 seconds.
- Rollback trigger: >20% failures/timeouts across 10+ tracked invocations.

## Evidence Index

- Tool trace logs: this session plus `result.json` files under `C:\development\opencode\logs\osgrep-debug`
- Session transcripts: OpenCode session where CLI-only policy was enabled and canary matrix executed
- Debug wrapper logs (if used):
  - `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc01-code-path\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc02-feature-flag\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc03-refactor-scope\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155447-tc04-large-repo\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155521-tc05-spaced-path-index\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155530-tc05-spaced-path-search\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155552-tc07-forced-failure\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155610-tc08-concurrent-a\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155610-tc08-concurrent-b\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155634-tc09-index-active\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155634-tc09-query-during-index\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155704-tc11-stale-index-search\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155712-tc10-known-answer-index\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155714-tc10-known-answer-search\result.json`
  - `C:\development\opencode\logs\osgrep-debug\20260312-155726-tc12-large-result-set\result.json`
- Additional notes:
  - Current in-session `osgrep` tool invocation still returns disabled text, indicating runtime/plugin reload is required before claiming OpenCode automation path is fully active.
