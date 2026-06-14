# Spec: OsGrep Comprehensive Test Suite

**Track ID**: 20260531-osgrep-comprehensive-test-suite
**Created**: 2026-05-31
**Parent Track**: 20260313-osgrep-stabilization (completed)
**Status**: Active
**Priority**: High
**Owner**: 01-Planner / Build
**Tags**: osgrep, testing, validation, quality-assurance, cli-only, canary

---

## Goal

Design and execute a comprehensive, repeatable test suite for OsGrep CLI-only canary mode, validating all core capabilities, edge cases, reliability concerns, and guardrails. Produce a pass/fail report that confirms OsGrep is healthy for continued production use.

## Requirements

- [ ] R1: Cover all major CLI commands: `search`, `index`, `symbols`, `skeleton`, `trace`, `list`, `doctor`, `--version`
- [ ] R2: Validate each `search` flag: `--max-count`, `--content`, `--scores`, `--min-score`, `--compact`, `--plain`, `--per-file`, `--skeleton`, `--sync`, `--dry-run`
- [ ] R3: Validate each `index` flag: `--dry-run`, `--path`, `--reset`, `--verbose`
- [ ] R4: Test reliability edge cases: concurrent queries, query during index, stale index, spaces in paths, large result sets, non-existent CWD
- [ ] R5: Verify MCP guardrail is active (osgrep mcp blocked)
- [ ] R6: Verify OpenCode tool-path activation (tool executes real CLI, not static text)
- [ ] R7: Verify fallback behavior (forced failure -> grep/glob/read)
- [ ] R8: All results captured as structured JSON logs with timestamps
- [ ] R9: Automated aggregation script produces a single pass/fail report
- [ ] R10: Known-answer tests validate search quality (not just exit codes)

## Non-Requirements

- [ ] N1: Do NOT test osgrep MCP mode (permanently disabled)
- [ ] N2: Do NOT test osgrep serve (server mode) -- out of scope for CLI canary
- [ ] N3: Do NOT modify any osgrep engine source code -- this is a test-only track
- [ ] N4: Do NOT modify the OpenCode tool `tool/osgrep.ts` -- already working
- [ ] N5: Do NOT install new npm packages globally -- use only existing tooling

## Acceptance Criteria

- [ ] AC1: All blocking tests pass (TC-B1..B6, TC-C1..C4, TC-F1..F3)
- [ ] AC2: Aggregate report at `C:\development\opencode\logs\osgrep-test-suite\report.md` shows overall pass/fail counts
- [ ] AC3: All non-blocking failures have documented root cause or known issue link
- [ ] AC4: Test suite is fully repeatable -- any agent can run `python scripts/tests/osgrep_test_suite.py` and get results
- [ ] AC5: No MCP path was invoked during any test run
- [ ] AC6: plan.md all non-deferred tasks marked [x]

## Test Categories

| Category | ID Range | Test Count | Blocking? |
|---|---|---|---|
| Health & Readiness | TC-A1..A3 | 3 | Yes |
| Index Operations | TC-B1..B6 | 6 | Yes |
| Core Search | TC-C1..C4 | 4 | Yes |
| Search Flags | TC-C5..C12 | 8 | No |
| Symbols & Structure | TC-D1..D8 | 8 | No |
| Reliability & Edge | TC-E1..E9 | 9 | No |
| Guardrails | TC-F1..F3 | 3 | Yes |
| Tooling | TC-G1..G3 | 3 | No |
| **Total** | | **44** | **16 blocking** |

## References

- Parent stabilization track: `.conductor/tracks/20260313-osgrep-stabilization/`
- Legacy validation matrix: `.conductor/tracks/20260312-osgrep-cli-only-reenable/artifacts/validation-matrix.md`
- Debug wrapper: `scripts/utils/osgrep_debug_wrapper.py`
- Process snapshot: `scripts/utils/osgrep_process_snapshot.ps1`
- OsGrep tool: `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts`
- OsGrep skill: `C:\Users\DaveWitkin\.config\opencode\skill\osgrep\SKILL.md`
