# Handover: Osgrep Stabilization + Tool-Path Activation

> Status update (2026-03-14): This handover is superseded by finalization report `2026-03-14-osgrep-stabilization-finalization.md`.

**Date:** 2026-03-14  
**Session Context:** Continue Path A stabilization for osgrep CLI-only re-enable and execute improved Conductor plan gates.  
**Current Status:** Partial implementation complete. Engine-side fix applied and basic reruns pass. Tool-path activation still failing in-session due to runtime reload/cache behavior.

---

## User Goal (Current Thread)

1. Improve Conductor plan quality and close missed gaps.
2. Execute plan forward (not just planning), including implementation and validation.
3. Ensure no context is lost when moving to a new OpenCode session.

---

## What Was Updated

### 1) Conductor planning artifacts (improved)

- Updated plan with explicit gates, reproducibility, and tool-path activation:
  - `C:\development\opencode\.conductor\tracks\20260313-osgrep-stabilization\plan.md`
- Rewrote spec to align with plan and remove outdated mutex assumptions:
  - `C:\development\opencode\.conductor\tracks\20260313-osgrep-stabilization\spec.md`
- Updated metadata to reflect new phase model + success criteria:
  - `C:\development\opencode\.conductor\tracks\20260313-osgrep-stabilization\metadata.json`
- Updated execution log:
  - `C:\development\opencode\.conductor\tracks\20260313-osgrep-stabilization\artifacts\execution-log-2026-03-14.md`

### 2) Engine-side implementation applied

- Applied idempotent table creation fix in osgrep package:
  - File: `C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\osgrep\dist\lib\store\vector-db.js`
  - Change: `createTable(..., { schema, existOk: true })`

### 3) OpenCode tool-path implementation applied

- Updated OpenCode tool to actually execute osgrep CLI (instead of static guidance text):
  - File: `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts`
  - Added `child_process.spawn` execution path, timeout handling, CLI output return, and explicit mcp-blocking.

### 4) Backups created before edits

- `C:\Users\DaveWitkin\AppData\Roaming\npm\node_modules\osgrep\dist\lib\store\vector-db.js.bak`
- `C:\Users\DaveWitkin\.config\opencode\tool\osgrep.ts.bak`

---

## Commands Run + Observed Results

### Version checks

```bash
osgrep --version
node -e "const p=require(process.env.APPDATA + '/npm/node_modules/osgrep/package.json'); console.log('osgrep',p.version,'lancedb',p.dependencies['@lancedb/lancedb']);"
```

Observed:
- osgrep `0.5.16`
- lancedb dependency `^0.22.3`

### Baseline/verification runs (debug wrapper)

```bash
python scripts/utils/osgrep_debug_wrapper.py --label tc01-pre-fix-20260313 --cleanup-stale --timeout 30 --cwd C:/development/opencode -- -- search "auth token refresh"
python scripts/utils/osgrep_debug_wrapper.py --label tc04-pre-fix-20260313 --cleanup-stale --timeout 30 --cwd C:/development/opencode -- -- search "conductor track"

python scripts/utils/osgrep_debug_wrapper.py --label tc01-post-fix-20260314 --cleanup-stale --timeout 30 --cwd C:/development/opencode -- -- search "auth token refresh"
python scripts/utils/osgrep_debug_wrapper.py --label tc02-post-fix-20260314 --cleanup-stale --timeout 30 --cwd C:/development/opencode -- -- search "feature flag"
```

Observed:
- TC-01 pre-fix: pass (`exit_code=0`)
- TC-04 pre-fix: pass (`exit_code=0`)
- TC-01 post-fix: pass (`exit_code=0`)
- TC-02 post-fix: pass (`exit_code=0`)

Evidence:
- `C:\development\opencode\logs\osgrep-debug\20260313-202047-tc01-pre-fix-20260313\result.json`
- `C:\development\opencode\logs\osgrep-debug\20260313-202059-tc04-pre-fix-20260313\result.json`
- `C:\development\opencode\logs\osgrep-debug\20260313-203249-tc01-post-fix-20260314\result.json`
- `C:\development\opencode\logs\osgrep-debug\20260313-203249-tc02-post-fix-20260314\result.json`

### Tool-path activation check (important)

Tool call attempted in-session:

```json
{"argv":["--","search","auth token refresh"]}
```

Returned old static guidance text, indicating runtime/plugin caching lag in that session.

Interpretation:
- File on disk is updated.
- In-session tool execution still used old loaded plugin code.
- Requires new session/runtime confirmation.

---

## Most Important Current Blocker

**Tool-path activation gate is not yet proven in a fresh runtime.**

Even though `osgrep.ts` is updated on disk, the active session still returned the old static response.

Before GO/NO-GO, the new AI session must prove:
1. osgrep tool call runs CLI and returns real search output.
2. no mcp path is used.
3. fallback behavior still works.

---

## Next Actions for New Session (Exact Order)

1. **Verify tool-path activation first (blocking):**
   - invoke osgrep tool with `argv: ["--","search","auth token refresh"]`
   - confirm output is real search output (not static guidance block)

2. **If tool-path is still static:**
   - check whether plugin runtime actually reloaded
   - if needed, restart desktop app and start a completely new conversation/session
   - re-test once

3. **Run remaining matrix checks (minimum):**
   - TC-04 rerun
   - TC-05 rerun (spaced path)
   - TC-11 rerun (stale-index determinism)
   - cold-start rerun check

4. **Finalize decision package:**
   - update validation matrix and go/no-go note in parent track
   - include explicit risk table for any residual TC-04/TC-11 behavior

---

## Decision Criteria (as currently planned)

Blocking for GO:
- TC-01..TC-05 pass
- MCP guardrail pass
- Tool-path activation pass
- No unresolved `Table 'chunks' already exists` recurrence in gate run

Conditional:
- TC-11 and residual TC-04 may be risk-accepted only with explicit owner + re-eval date + mitigation

---

## Rollback (if needed)

Restore backups:

- `vector-db.js.bak` -> `vector-db.js`
- `osgrep.ts.bak` -> `osgrep.ts`

Then re-run baseline wrapper tests to confirm pre-change behavior.

---

## Quick References

- Stabilization track:  
  `C:\development\opencode\.conductor\tracks\20260313-osgrep-stabilization\`
- Parent canary track:  
  `C:\development\opencode\.conductor\tracks\20260312-osgrep-cli-only-reenable\`
- This handover:  
  `C:\development\opencode\.conductor\verification-reports\2026-03-14-osgrep-stabilization-handover.md`

---

## One-line Summary for Next AI

Plan/spec are now fixed and aligned, `existOk: true` was applied and quick reruns pass, but GO is blocked until a fresh-session tool-path activation proves `tool/osgrep.ts` now executes osgrep CLI instead of returning static guidance.
