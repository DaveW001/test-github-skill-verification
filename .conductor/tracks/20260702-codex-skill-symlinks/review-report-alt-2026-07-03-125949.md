# Stage 3 Conditional Re-review: Codex Skill Junction Layer

- **Track:** `20260702-codex-skill-symlinks`
- **Reviewer:** conductor-plan-reviewer-alt (`gpt-5.5`)
- **Review date:** 2026-07-03
- **Spec:** `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\spec.md`
- **Plan:** `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\plan.md`
- **Prior review:** `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\review-report-2026-07-03-123547.md`

## Executive summary

This Stage 3 pass reviewed the post-Stage-2 plan and targeted the three surfaced items. I applied two plan fixes and one clarification/removal:

1. **Phase 5.2 scheduler JSON shape fixed.** The existing global-scope jobs use direct `powershell.exe ... -File <script.ps1>` invocation, not the marketing-scope `opencode-run-safe.ps1 --command ... --title ... -- ""` wrapper. Phase 5.2 now matches the global-scope pattern and its acceptance check validates the direct script path plus `-Apply`.
2. **Phase 4.1 report shape pinned.** The reconciliation script authoring task now requires a JSON report shape compatible with F.1/F.2: top-level `Apply`, `GeneratedAt`, and `Actions`, with action names including `would-create-junction`, `created-junction`, `conflict`, and `real-folder-needs-manual-backup-convert`.
3. **External-interference language removed.** The lingering top-risk note about an external process/reversion was removed. The issue is resolved as junction topology, and Phase M already breaks vault-to-native junctions and creates real vault copies.

No new Blocking items were introduced by the Stage 2 fixes. The remaining plan weaknesses are non-blocking: 3.1 has a weak file-exists acceptance check, 6.1 still gives only minimal runbook literals, and F.4 leaves Conductor bookkeeping mostly diagnostic. These do not prevent execution of the filesystem/scheduler work, but they lower executability for a weaker agent.

## Active verification performed

| Check | Result | Status |
|---|---:|---|
| Existing global jobs in `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\opencode-global-7a3f9c2e1b84\jobs\` use `opencode-run-safe.ps1` | `False` for both `gemini-proxy-monitor.json` and `gemini-proxy-starter.json` | Confirms direct pattern |
| Existing global jobs use direct `-File "C:\...\.ps1"` pattern | `True` for both global jobs | Confirms Phase 5.2 fix |
| Simulated revised Phase 5.2 acceptance check | `Scheduler simulated acceptance: True` | Passed |
| Simulated revised Phase 4.1 literal-shape acceptance check | `Phase 4.1 acceptance simulated: True` | Passed |
| Plan search for `external process`, `external interference`, `reversion` | `0` matches | Passed |

Note: the existing global job files contain unescaped Windows backslashes and are not strict JSON for `ConvertFrom-Json`; the verification therefore inspected raw file content for invocation shape instead of parsing those existing files.

## Per-task ratings for changed / attention tasks

| Task | Rating | Finding / applied fix |
|---|---|---|
| 4.1 Write `C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1` | **Ready after fix** | Added explicit report-shape requirements and acceptance check literals for `Apply`, `Actions`, `would-create-junction`, `created-junction`, and `conflict`, aligning 4.1 with F.1/F.2. |
| 4.2 Dry-run weekly reconciliation script | **Ready** | Acceptance check already validates `$report.Apply -eq $false`; with 4.1 shape pinned, this is now coherent. |
| 5.2 Write Scheduler job JSON in global scope | **Ready after fix** | Replaced wrapper invocation with direct global-scope pattern: `powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1 -Apply`. Acceptance check updated accordingly. |
| 5.3 Verify Scheduled Task | **Ready** | Still cannot be fully executed until JSON exists and Scheduler registers it, but command is active and specific. No change needed. |
| Top 3 risks / external interference note | **Ready after clarification** | Removed stale external-process/reversion warning. The topology issue is handled by Phase M. |
| 3.1 Compute missing junction list | **Needs work (non-blocking)** | Prior review item remains: file-exists acceptance is weak. Final 3.2 validates all canonical map entries, so execution safety is preserved. |
| 6.1 Create runbook | **Needs work (non-blocking)** | Still under-specified for documentation quality; the acceptance check can pass with minimal content. Not a blocker for junction execution. |
| F.4 Execution log / Conductor bookkeeping | **Needs work (non-blocking)** | Still lacks hard assertions for metadata/ledger updates. Not a blocker for filesystem/scheduler correctness. |

## Fixes applied to `plan.md`

- Phase 4.1 now pins the reconciliation report schema and action names required by final validation.
- Phase 5.2 now matches the two existing global jobs' direct `.ps1` invocation shape and no longer depends on `opencode-run-safe.ps1`.
- Removed the stale external-process/reversion note from the risk section.

## Overall readiness

**92% Ready.**

The plan is ready for execution by a less capable agent if the executor follows the PowerShell-first preflight and runs each authoritative acceptance check exactly. The remaining Needs Work items are quality/documentation/bookkeeping rigor issues, not blockers to safe junction conversion or scheduler registration.

## Ready for execution?

**Yes.** Proceed with Phase M.1 first.

## Plan document path

`C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\plan.md`
