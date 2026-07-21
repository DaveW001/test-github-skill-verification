# Audit Correction - Provenance Reconciliation (Stage 7, 2026-07-19)

**Track:** 20260717-dcp-child-session-safety  
**Issue:** `artifacts/source-map.json` recorded stale pinned commits (`opencode 45cd8d76920839e4a7b6b931c4e26b52e1495636`, `dcp 85b6f5ceba144fee9e65eb28dc36cab1b960e418`, both `dirty:false`). Stage 7 (`validation-report-20260719-020453Z.md`) identified that the actual checkouts advanced: the track's production/test changes are now committed in both clones.

**Actual state (verified by `git rev-parse HEAD` + `git status --short`):**
- OpenCode core `C:\development\opencode-core-dcp-fix`: HEAD `c4018482d748dfc45c8b3485ef879281fe58b84a` (branch `dev`), **clean**. Core production/test changes are in this commit.
- DCP `C:\development\opencode-dcp-child-fix`: HEAD `558e03757e6bdc9f4a1db4f6a022039c0854caf2` (branch `master`), **dirty** — one uncommitted test-only retry change: `tests/prompts.test.ts` (Stage 6 Bun node:test subtest flatten). DCP implementation is in commits `64bb37a` and `558e037`.

**Action taken:** `source-map.json` updated to the actual commits/dirty state. Prior recorded values preserved in `artifacts/source-map-provenance-history.json` (moved out of source-map.json on the Stage 8 fix so source-map.json retains its exact Task 0.2 top-level shape {opencode, dcp}; not silently overwritten). The earlier pinned commits remain the upstream base; this correction reflects that the track's changes have since been committed on top. The earlier pinned commits remain the upstream base; this correction reflects that the track's changes have since been committed on top.

**No source behavior change.** Prior evidence (RED gates, reviews, Stage 6 reports, audit corrections, full-suite-results) is unchanged.