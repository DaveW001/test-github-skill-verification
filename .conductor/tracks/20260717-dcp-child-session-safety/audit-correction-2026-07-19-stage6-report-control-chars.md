# Audit Correction - Stage 6 Report Control-Character Defect (2026-07-19)

**Track:** 20260717-dcp-child-session-safety  
**Immutable report (NOT edited):** `test-run-report-2026-07-18-212156.md`  
**Defect:** Lines 7 and 23 of that report contain literal control characters (TAB/backtick substitutions) that corrupt a few command/path tokens. The historical report is preserved verbatim per immutability; this artifact supplies the corrected names.

## Corrected tokens

| Corrupted in report | Corrected |
|---|---|
| `est-baseline.json` | `test-baseline.json` |
| `andexecution-log-2026-07-17.md` | `and execution-log-2026-07-17.md` |
| `un test` (command cell) | `bun test` |
| `un run typecheck` | `bun run typecheck` |
| `un run build` | `bun run build` |
| `un .conductor/...` | `bun .conductor/...` |
| `rtifacts/canary-report.json` | `artifacts/canary-report.json` |

## Pointers to readable qualified-green evidence
- DCP full suite qualified-green (123 pass / 0 fail, exit 0): `audit-correction-2026-07-18-stage6-retry.md` + `artifacts/full-suite-results.json`.
- OpenCode full suite qualified-green (3203 pass / 9 pre-existing sandbox-env failures, 0 changed-module regressions): same artifacts.
- The control characters affect only display tokens in the Stage 6 narrative; the underlying commands, exits, and per-test pass/fail table are otherwise accurate and were independently reproduced in the Stage 6 -> Stage 5 retry.

No historical report was modified.