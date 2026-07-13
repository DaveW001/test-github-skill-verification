# Audit Correction — Stage 6 Exit Code

- **Track:** 20260712-pptx-reference-image-rebuild
- **Corrected:** 2026-07-13
- **Scope:** pipeline bookkeeping only

## Mismatch

The original Stage 6 report's `**Exit code:**` field contained a NUL byte instead of the captured value.

## Correct Value and Evidence

The correct exit code is `0`, supported by the same report's GREEN verdict, its captured pytest output (`18 passed in 4.30s`), and the independent Stage 7 rerun (`18 passed in 4.33s`, exit code `0`).

## Correction

The Stage 6 report was rewritten only to replace the malformed field with `**Exit code:** 0` and remove the invalid NUL byte. No source, test, configuration, plan, or execution evidence changed.
