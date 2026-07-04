# Session Handoff: OpenCode Scheduler Plugin Drift Analysis

**Track:** `20260508-restore-opencode-scheduler-plugin`
**Handoff type:** Session-context handoff (analysis state), NOT an execution-log handover.
**Date:** 2026-07-04
**Prepared by:** 01-Planner (model: glm-5.1)
**Status of this handoff:** Analysis complete, recommendation delivered to user, **awaiting user decision** (Option A vs B). No config or code was modified.

---

## 1. Why This Document Exists

The user is opening a fresh OpenCode session to continue working on the OpenCode scheduler housekeeping issue. This document captures the full verified analysis so the next session loses no context.

**The reported anomaly:** "scheduler plugin package exists in cache, scheduler job files exist, Windows scheduled tasks exist, but the active OpenCode global config does not currently list `opencode-scheduler`."

**The user's questions:** What's going on? Is it something to fix? (Also: check the opencode repo for scheduler docs.)

---

## 2. TL;DR Diagnosis

This is a **config/cache/plugin DRIFT, not a runtime outage.** Scheduled jobs keep running fine because they execute via Windows Task Scheduler directly (not via the plugin at runtime). The `opencode-scheduler` plugin entry was dropped from the global config sometime before 2026-05-08, so OpenCode stopped loading/installing it, and the cache entry disappeared. The impact is a **management/maintenance gap** (can't add/modify jobs through the plugin), not an execution failure. A Conductor track to fix this has been sitting in `ready-for-execution` for ~2 months, never run.

---

## 3. Verified Current-State Facts (2026-07-04, PowerShell)

| Claim | Verified reality |
|---|---|
| "plugin package exists in cache" | **FALSE** at the authoritative path `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler`, nor any of 6 other checked locations, nor global npm. The reporter's claim does not hold. |
| "scheduler job files exist" | **TRUE** — 6 scopes under `...\opencode\scheduler\scopes`, 23 jobs total per registry. |
| "Windows scheduled tasks exist" | **TRUE** — ~20 tasks under `\OpenCode\`, mostly Ready/Enabled, many last run today. |
| "config doesn't list opencode-scheduler" | **TRUE** — plugin array has 5 entries, none is opencode-scheduler. |

### Active config plugin array (CURRENT — use THIS, not the plan's outdated example)
File: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`

```
"plugin": [
  "@zenobius/opencode-skillful",
  "oc-codex-multi-auth",
  "opencode-ignore@1.1.0",
  "@tarquinen/opencode-dcp@latest",
  "@ramtinj95/opencode-tokenscope@latest"
]
```

Default agent: `01-Planner`. Model: `zai-coding-plan/glm-5.2`.

### Scheduler scope root
`C:\Users\DaveWitkin\.config\opencode\scheduler\scopes` — EXISTS. 6 scopes:
- `02-kx-to-process-a13895517ca9`
- `development-88876ee600f5`
- `email-triage-0fff020d966c`
- `marketing-1cd46ed3b6ad`
- `opencode-a1480a5519b6`
- `opencode-global-7a3f9c2e1b84`

### The plugin package
`opencode-scheduler@1.3.0` IS published to npm (third-party, NOT part of upstream opencode). It is simply not installed in any cache.

---

## 4. Why Jobs Still Run (Decoupled Execution Model)

The scheduler has a **decoupled model**:

- **Registration** was historically done BY the plugin (creating scope JSONs + Windows tasks).
- **Execution** is done BY Windows Task Scheduler directly — each task invokes `powershell.exe`/`pwsh` -> `opencode-run-safe.ps1` -> the target script directly (or the `opencode` CLI binary). The plugin is NOT in that runtime path.
- **Reconciliation** is handled independently by `C:\development\_shared-scripts\Sync-SchedulerRegistry.ps1`, which runs daily 9 AM and auto-generates `C:\development\_shared-scripts\scheduler-registry.md`.

**Latest registry (regenerated 2026-07-04T09:00):** 23 total jobs, 22 OK, 1 Disabled, **0 drift, 0 orphans.** Many jobs last ran today with Result 0. Two showed Running/267009 (0x41301 = "task currently running"): `scheduler-registry-sync`, `hourly-email-auto-sort`.

So dropping the plugin broke nothing at runtime — it only removed the ability to manage jobs through the plugin.

---

## 5. Documentation Finding

User asked to check the opencode repo (`C:\development\opencode`) for scheduler docs. **There are NONE.** `opencode-scheduler` is a third-party plugin, not part of upstream opencode. Every "scheduler" reference in the repo is either our own `.conductor\tracks\` planning files or unrelated gemini-proxy scheduled-task docs (`docs\reference\gemini-proxy.md`, `docs\troubleshooting\active\gemini-proxy-down.md`). The real "scheduler documentation" for this setup is the auto-generated `scheduler-registry.md`.

---

## 6. The Housekeeping Issues

1. **Genuine config/cache/plugin drift** — can't add or modify jobs through the plugin anymore; only by hand-editing scope JSONs (which the sync script tolerates).
2. **A stale Conductor track never executed.** `20260508-restore-opencode-scheduler-plugin` (owner: 01-Planner) has been `ready-for-execution` for ~2 months. Its spec/DoD is exactly right for this problem.
3. **The track's plan.md is OUTDATED and would REGRESS the config if run as-is.** See section 8 below.
4. **A circular-ish dependency (worth noting, not urgent):** the `Sync-SchedulerRegistry.ps1` job is itself a scheduled task managed through the scope system it reconciles. It works (0 drift), but the safety net is part of the system it watches.

---

## 7. Recommendation (delivered to user, awaiting decision)

Low urgency but worth closing out. Two clean options:

- **Option A — Restore the plugin (RECOMMENDED).** Refresh the plan's outdated plugin-array example to match today's config, then hand to a Build/Executor agent: add `opencode-scheduler` back to config, restart OpenCode, verify cache path + DoD. Restores plugin-based job management.
- **Option B — Accept the decoupled model.** If hand-editing jobs + sync script is sufficient, formally CLOSE the stale track and optionally document the hand-edit workflow.

Either way, the stale track should not remain in `ready-for-execution`.

---

## 8. CRITICAL: The Plan's Outdated Plugin Array (Must Refresh Before Option A)

`plan.md` Task 1.1 "Required final structure example" shows this STALE array:

```
"plugin": [
  "opencode-snippets@1.8.0",        <-- REMOVED since May 8
  "@zenobius/opencode-skillful",
  "oc-codex-multi-auth",
  "opencode-ignore@1.1.0",
  "opencode-mystatus",              <-- REMOVED since May 8
  "@tarquinen/opencode-dcp@latest",
  "opencode-scheduler"
]
```

This is OUTDATED. `opencode-snippets@1.8.0` and `opencode-mystatus` were since removed from the active config, and `@ramtinj95/opencode-tokenscope@latest` was since added. **Running this plan as-is would REGRESS the plugin set.** The correct target is: append `opencode-scheduler` to the CURRENT array in section 3.

A May 8 artifact (`global-config-plugin-block.txt`) confirmed the plugin set was already different on May 8 AND already lacked `opencode-scheduler` — so the drop predates the track. The `standard-cache-scheduler-package.txt` artifact from May 8 = "standard cache package.json missing".

---

## 9. Next Steps for the New Session

1. **Confirm the user's choice** (Option A vs Option B). The analysis and recommendation have been delivered; the user has NOT yet decided (as of this handoff).
2. **If Option A:** A Planner should refresh `plan.md` Task 1.1 to use the current plugin array from section 3 (append `opencode-scheduler`), then hand to a Build/Executor agent to execute the plan (Phases 0 through 5). The spec DoD is already correct and does not need changes.
3. **If Option B:** Close the track — update `metadata.json` status to `cancelled`/`closed` with rationale, and optionally add a `docs/workflows/` note on hand-editing scope JSONs.
4. **Either way:** No config or code was modified in this analysis session (read-only, Planner scope).

---

## 10. Key Paths and Quick-Reference Commands

- Active config: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- Scheduler scopes: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\`
- Expected plugin cache (after restore): `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler`
- Registry doc: `C:\development\_shared-scripts\scheduler-registry.md`
- Sync script: `C:\development\_shared-scripts\Sync-SchedulerRegistry.ps1`
- Registry backups: `C:\development\_shared-scripts\scheduler-registry-backups`
- Track dir: `C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\`
- This handover: `C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\handover.md`

Quick checks:
```powershell
# Plugin absent?
Select-String -Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern 'opencode-scheduler' -SimpleMatch
# Cache present?
Test-Path "C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler"
# OpenCode tasks (query the FOLDER path, not a wildcard task name; schtasks treats * literally)
Get-ScheduledTask -TaskPath "\OpenCode\*" | Select-Object TaskName, State
```

---

## 11. Tool-Layer Note for the Next Session

This session hit `Bun is not defined` failures on the `read`, `glob`, `write`, and `edit` file tools. The session was run **PowerShell-first via the `bash` tool** (Get-Content, Get-ChildItem, Select-String, Set-Content) per the AGENTS.md tool-failure protocol. If the next session hits the same, switch immediately and do NOT retry the failing tool per-call. Bun 1.3.4 IS installed; this is a runtime sandbox-init failure, not a missing install. Full runbook: `~/.config/opencode/docs/troubleshooting/tool-failure-bun-undefined.md`.

---

## 12. Related Conductor Tracks (for context, not necessarily action)

All under `C:\development\opencode\.conductor\tracks\`:
- `20260314-gemini-proxy-scheduler-hardening` — gemini-proxy scheduled tasks (different concern).
- `20260501-scheduler-headless-hardening` — has execution-log, task-inventory, plan, spec.
- `20260508-restore-opencode-scheduler-plugin` — THIS track (the relevant one).
- `20260508-scheduler-desktop-cli-diagnostics` — diagnostic-report, execution-log, handover, plan, spec, plus ~20 artifacts.

---

## Change Log
- 2026-07-04: Created by 01-Planner. Session-context handoff documenting completed read-only analysis of the scheduler config/cache/plugin drift. No execution performed; awaiting user decision on Option A vs B.
