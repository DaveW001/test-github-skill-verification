# Session Handoff: Scheduler-Restore Follow-Ups (junction + task-info + bookkeeping)

## Original Session

- Title: Conductor pipeline run — track `20260508-restore-opencode-scheduler-plugin`
- Repo: `C:\development\opencode`
- Watermark: 2026-07-04T15:00:00-04:00 (pipeline closed; validation verdict "Close with minor follow-ups")
- Source track dir: `C:\development\opencode\.conductor\tracks\20260508-restore-opencode-scheduler-plugin\`
- Source validation report: `…\20260508-restore-opencode-scheduler-plugin\validation-report-2026-07-04-145809.md`

## Recovered Goal

The scheduler-plugin restore is DONE and validated. This handoff covers the three out-of-scope items the executor/validator flagged, scoped and ready for a fresh session to fix. The highest-value item is a broken lazy-vault junction that blocks hourly email auto-sort Graph auth.

## Work Already Done (evidence)

- Plugin restored exactly once; cache present (v1.3.0); hourly task `Ready`; JSONC parses. See the source validation report above.
- The email auto-sort manual run fails with exit code 10 ("No-WAM Graph auth wrapper not found") because the wrapper is unreachable via the vault path. The **cert is healthy** (CN=daily-priority-briefing-graph, NotAfter 2029-03-09, private key present) — this is NOT an auth/cert regression.

## Successor Sessions Reviewed

| Session | Relevant? | Finding |
|---|---|---|
| None after the watermark | — | No successor session has addressed any of these items. |

---

## Issue 1 — [HIGH] Self-referential `microsoft-graph` junction → email auto-sort auth failure

### Symptom
- `pwsh -File C:\development\email-triage\scripts\hourly-email-auto-sort.ps1` exits **10** with "No-WAM Graph auth wrapper not found".
- `Test-Path C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1` → **False**.

### Root cause (verified)
- `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph` is a **Junction** whose reported target points **to itself**:
  `Get-Item …\microsoft-graph`.Target = `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph`. Following it never reaches real content.
- The **real** wrapper exists at:
  `C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1`
  (a skillshare copy also exists at `…\development-config\AppData\Roaming\skillshare\skills\microsoft-graph\…`).

### Scope (important — likely systemic, not one skill)
- Comparing all lazy-vault junctions: skills whose real content lives under `C:\Users\DaveWitkin\.config\opencode\skill\` (git-push, conductor, conductor-pipeline, osgrep, opencode-scheduler, perplexity-search, session-handoff, skill-discovery) have **correct** targets.
- Skills whose real content lives under `.opencode-lazy-vault\` (**dozens**: agent-writer, calendar-*, clickup, clickup-cli, email-*, microsoft-graph, slack-*, etc.) **all** report self-referential targets. So the vault-junction reconciliation appears broken vault-wide — same systemic root cause already logged in track `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\`.
- Decision for the new session: fix **only microsoft-graph** to unblock email auto-sort quickly, OR address the **vault-wide** reconciliation. Recommend the latter since the defect is systemic, but start with microsoft-graph as the acceptance gate.

### In Scope
- Diagnose why `.opencode-lazy-vault\*` junctions self-reference (OpenCode desktop host likely re-pointed them on a reconcile pass).
- Re-create the `microsoft-graph` junction so `…\lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1` resolves to the OneDrive source.
- (Optional, if scoped) repair the rest of the lazy-vault cohort using the same pattern.
- Re-run the hourly email auto-sort manual dry-run and confirm it reaches Graph auth / connects.

### Out of Scope
- Changing scheduler cadence or the `*/15 * * * *` job JSON.
- Modifying email-triage production logic beyond confirming auth now works.
- Rotating the Graph cert (it is healthy).

### How to fix (concrete)
1. Snapshot current junction state:
   `Get-ChildItem C:\Users\DaveWitkin\.opencode-lazy-vault -Force | Select-Object Name, LinkType, Target | Format-Table -AutoSize`
2. For microsoft-graph, remove the broken junction and recreate it pointing at the real source (run from an elevated/admin shell if needed):
   ```powershell
   $vault = "C:\Users\DaveWitkin\.opencode-lazy-vault"
   $src   = "C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph"
   Remove-Item "$vault\microsoft-graph" -Force      # removes the junction link only, not real content
   New-Item -ItemType Junction -Path "$vault\microsoft-graph" -Target $src
   ```
3. Confirm resolution:
   `Test-Path "$vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"` → **True**;
   `(Resolve-Path "$vault\microsoft-graph").Path` → the OneDrive source (not itself).
4. Re-run the manual dry-run (use **pwsh**, PS 7 — see Issue 3):
   `pwsh -NoProfile -ExecutionPolicy Bypass -File C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
   Expect: reaches `## Authentication`, connects via no-WAM/app-only, writes a new `*_run.md` log.
5. For the systemic fix, generalize step 2 across the self-referential cohort, deriving each real source from `…\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\<name>`. Add a guard so you never delete a real directory (only junctions). Investigate WHY OpenCode desktop re-points them to avoid recurrence.

### Validation / acceptance
- `Test-Path …\microsoft-graph\scripts\connect-graph-no-wam.ps1` = True.
- Manual auto-sort run reaches auth and completes (or produces a non-wrapper error).
- Newest `C:\development\email-triage\logs\*_run.md` shows successful app-only Graph connection, no "wrapper not found".
- Optional systemic: a script asserts every `.opencode-lazy-vault\*` junction resolves to a distinct real target, not itself.

---

## Issue 2 — [LOW] `Get-ScheduledTaskInfo` / `Export-ScheduledTask` fail for the hourly task

### Symptom (verified)
- `Get-ScheduledTask -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort"` succeeds (State = Ready).
- `Get-ScheduledTaskInfo -TaskName …` AND `Export-ScheduledTask -TaskName …` both fail: **"The system cannot find the file specified."**

### Scope
- Diagnostic only. The task is registered, enabled, and actually firing (a `*_run.md` log exists at 14:30 today). This is a Task-Scheduler metadata/read inconsistency, not a functional failure.

### In Scope
- Determine why the info/export APIs cannot read a task that the state API sees. Common causes: task XML stored under a non-standard path, a stale/corrupt task object, or a path-length/encoding issue in the task name.
- Document the finding; do NOT delete/recreate the task without approval (non-goal of the original track).

### How to diagnose
1. `Get-ScheduledTask -TaskName "<name>" | Format-List *` — confirm registration path / author / source.
2. `schtasks /Query /TN "<name>" /V /FO LIST` — the legacy schtasks CLI sometimes reads what the cmdlet cannot.
3. Check the on-disk task file: `Get-ChildItem "$env:SystemRoot\System32\Tasks" -Recurse -Filter "*email-triage*"` and inspect its XML + whether the file is a reparse point/symlink.
4. If the file is missing/corrupt on disk while registered in the registry, that explains the split behavior.

### Validation / acceptance
- Either: the info/export APIs succeed and return concrete LastRunTime/NextRunTime; OR a documented root cause + a safe remediation proposal is recorded (no destructive task change without approval).

---

## Issue 3 — [INFO] Bookkeeping / interpreter notes

### 3a. Email-triage scripts require PowerShell 7 (`pwsh`), not Windows PowerShell 5.1 (`powershell`)
- During the pipeline, Task 4.4's literal `powershell -File …` failed to parse the UTF-8 script under PS 5.1 (parse-error exit 1, never reached auth). The executor's Tier-0 fix used `pwsh`, which is also what `run-hidden.vbs` invokes in production.
- **Fix:** update the closed track's plan Task 4.4 wording from `powershell` to `pwsh`, and ensure any future email-triage run instructions / docs specify `pwsh`. Confirm `run-hidden.vbs` resolves `pwsh` on PATH.

### 3b. Conductor metadata bookkeeping gap
- `…\20260508-restore-opencode-scheduler-plugin\metadata.json` has `executor_model` and `executed_at` blank (status correctly shows completed, 27/27). Non-blocking.
- **Fix:** backfill `executor_model` = `zai-coding-plan/glm-5.2` and `executed_at` = `2026-07-04T14:48:50-04:00` in that metadata.json (executor model is recorded in the execution log). Validator already passed this; it is housekeeping.

---

## Recommended Approach for the New Session

- **Issue 1 is significant, multi-step, validation-heavy** → recommend opening a Conductor track (e.g. `.conductor\tracks\20260704-microsoft-graph-junction-repair\` with spec.md + plan.md + metadata.json) per the Conductor continuation guidance. Start with microsoft-graph as the acceptance gate, then decide on the systemic vault reconciliation.
- **Issue 2** is investigative — can be a short task or a section in the same track.
- **Issue 3** is trivial housekeeping — fold into the same track's plan as final-phase tasks (no separate track needed).

## Next Steps

1. Create the Conductor track for Issue 1 (junction repair), scope decision: microsoft-graph-only vs vault-wide.
2. Reproduce + diagnose Issue 2 (task-info read inconsistency).
3. Apply Issue 3a/3b bookkeeping edits.

## Verdict

CONTINUE — no successor session has resolved these. The plugin-restore intent is complete; these are independent follow-ups ready for a fresh session.

## Handoff Artifact

- This file: `C:\development\opencode\.opencode\handoffs\20260704-1715-scheduler-followups.md`

## New-Session Bootstrap

Start the new session with:

> Continue this work using the handoff doc at `C:\development\opencode\.opencode\handoffs\20260704-1715-scheduler-followups.md`. Address Issue 1 (microsoft-graph junction repair) first by creating a Conductor track; it blocks hourly email auto-sort Graph auth. The cert is healthy — only the lazy-vault junction is broken.
