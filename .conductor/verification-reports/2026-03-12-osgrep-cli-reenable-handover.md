# Handover: Osgrep CLI-Only Re-Enablement (Canary)

**Date:** 2026-03-12  
**Session Goal:** Re-enable osgrep for OpenCode automation in CLI-only mode, then validate real usage and safety.  
**Current Decision:** **NO-GO for full rollout** (canary remains active, but core gate failed).

---

## What Was Requested

The user asked to:

1. Confirm whether osgrep was re-enabled.
2. Create/extend Conductor planning for CLI-only re-enable (not MCP).
3. Apply policy/config changes to re-enable CLI-only usage.
4. Validate with concrete test cases that osgrep is actually used.
5. Prepare context for continuation in a new OpenCode session.

---

## Conductor Tracks Involved

### Existing baseline track
- `C:\development\opencode\.conductor\tracks\20260311-osgrep-disable-and-root-cause\spec.md`
- `C:\development\opencode\.conductor\tracks\20260311-osgrep-disable-and-root-cause\plan.md`
- `C:\development\opencode\.conductor\tracks\20260311-osgrep-disable-and-root-cause\metadata.json`

This track remains the disablement/root-cause investigation history.

### New canary re-enable track (created in this session)
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\spec.md`
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\plan.md`
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\metadata.json`

Artifacts created/updated:
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\artifacts\prompt-suite.md`
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\artifacts\validation-matrix.md`
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\artifacts\go-no-go.md`
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\artifacts\rollback-switches.md`

---

## Policy/Config Changes Applied

The session moved from disabled-by-default to **CLI-only canary enabled** guidance.

### Updated files
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
  - Replaced disablement block with "Osgrep CLI-Only (Canary)"
  - Explicitly disallows `osgrep mcp` for routine automation
  - Defines fallback to `grep`/`glob`/`Read`

- `C:\Users\DaveWitkin\.config\opencode\agent\build.md`
  - Build agent semantic search rule now allows CLI-only osgrep with fallback policy

- `C:\Users\DaveWitkin\.config\opencode\agent\01-planner.md`
  - Planner guidance now allows CLI-only osgrep, disallows MCP, and defines fallback

- `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md`
  - Example language updated to CLI-only osgrep policy

- `C:\Users\DaveWitkin\.config\opencode\skill\osgrep\SKILL.md`
  - Compatibility/status changed to CLI-only canary

- `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts`
  - Tool description/status text changed to enabled CLI-only canary messaging

- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - `permission.skill.osgrep` changed from `"deny"` to `"allow"`

---

## Validation Execution Summary

Validation used the local wrapper:
- `python scripts/utils/osgrep_debug_wrapper.py ...`

Primary log root:
- `C:\development\opencode\logs\osgrep-debug\`

### Quick outcome by test ID

- TC-01: **FAIL** (`Table 'chunks' already exists`)
- TC-02: **FAIL** (`Table 'chunks' already exists`)
- TC-03: **PASS**
- TC-04: **FAIL** (FTS inverted-index warning; quality issue)
- TC-05: **PASS** (spaced path index/search)
- TC-06: **PASS** (no MCP usage in test runs)
- TC-07: **PASS** (forced failure + fallback path validated)
- TC-08: **PASS** (concurrent queries)
- TC-09: **PASS** (query during index)
- TC-10: **PASS** (known-answer query after reindex)
- TC-11: **FAIL** (stale index behavior not clean)
- TC-12: **PASS** (large result set within timeout)

Gate result in track artifact: **FAIL / NO-GO for full rollout**.

Canonical matrix details:
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\artifacts\validation-matrix.md`

Decision note:
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\artifacts\go-no-go.md`

---

## Important Session Finding

Even after policy/config updates, one direct in-session call to the `osgrep` tool returned the older disabled response text. The source file now shows enabled canary text, so this likely indicates runtime/plugin reload lag in the current session.

Reference check file:
- `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts`

Implication:
- In the new session, verify runtime picks up the updated tool behavior before trusting automation-path results.

---

## Phase Progress Snapshot

Track plan currently reflects:
- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete
- Phase 5: partially complete (decision recorded; rollback not executed)
- Phase 6: not started

Source:
- `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\plan.md`

Metadata task counts were updated accordingly.

---

## Recommended Next Actions In New Session

1. **Reload and verify runtime state first**
   - Confirm updated guidance and tool messaging are active in-session.
   - Re-check `osgrep` tool behavior in the fresh session.

2. **Stabilize failing modes before full rollout**
   - Investigate and fix/mitigate:
     - `Table 'chunks' already exists`
     - FTS inverted-index warning behavior
     - stale index degradation behavior (TC-11)

3. **Re-run core gate tests (minimum)**
   - Re-run TC-01 through TC-05 and confirm 5/5 pass.

4. **If still unstable, execute rollback**
   - Use:
     - `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\artifacts\rollback-switches.md`

5. **Update current-status troubleshooting doc once decision is final**
   - `C:\development\opencode\docs\troubleshooting\active\osgrep-intermittent-hang-disablement-2026-03-11.md`

---

## Minimal Repro Commands (for continuation)

From `C:\development\opencode`:

```bash
python scripts/utils/osgrep_debug_wrapper.py --label tc01-rerun --cleanup-stale --timeout 30 --cwd C:/development/opencode -- -- search "auth token refresh"
python scripts/utils/osgrep_debug_wrapper.py --label tc02-rerun --cleanup-stale --timeout 30 --cwd C:/development/opencode -- -- search "feature flag"
python scripts/utils/osgrep_debug_wrapper.py --label tc04-rerun --cleanup-stale --timeout 30 --cwd C:/development/opencode -- -- search "conductor track"
python scripts/utils/osgrep_debug_wrapper.py --label tc05-rerun --cleanup-stale --timeout 30 --cwd "C:/development/opencode/osgrep path repro" -- -- search "refreshAuthToken"
```

---

## Session-Generated Test Fixture

Temporary spaced-path fixture used for validation:
- `C:\development\opencode\osgrep path repro\sample.ts`

This includes symbols used in known-answer/stale-index checks.

---

## One-Line Status for Next AI

CLI-only re-enable policy/config is in place, but canary validation failed core gate due to index/search reliability issues; do runtime reload verification, stabilize failures, and rerun TC-01..TC-05 before any GO decision.
