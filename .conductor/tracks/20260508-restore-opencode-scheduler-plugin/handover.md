# Handover: Restore OpenCode Scheduler Plugin

**Track:** `20260508-restore-opencode-scheduler-plugin`
**Stage:** 4 (Execution) -> handover
**Executor model:** `zai-coding-plan/glm-5.2` (Tier 1)
**Run date:** 2026-07-04
**Final status:** completed (plugin restoration goal fully achieved); one out-of-scope follow-up surfaced (broken `microsoft-graph` lazy-skill junction) -- see Follow-Up Items.

> NOTE: This is the EXECUTION handover. The read-only planner analysis handover is preserved at `analysis-handover.md` (not overwritten).

## Summary
- Changed: appended `"opencode-scheduler"` exactly once to the top-level `plugin` array in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`. No other plugins added/removed/reordered. Existing order preserved: `@zenobius/opencode-skillful`, `oc-codex-multi-auth`, `opencode-ignore@1.1.0`, `@tarquinen/opencode-dcp@latest`, `@ramtinj95/opencode-tokenscope@latest`, then `opencode-scheduler`.
- Not changed: scheduler scope/job JSON, Windows scheduled tasks, email-triage production code, any other config keys. No tasks deleted/recreated.

## Commands Run
- `Test-Path opencode.jsonc` -> `True` (0.1)
- `New-Item backups dir` -> exists (0.2)
- `Copy-Item opencode.jsonc -> backups\opencode.jsonc.pre-scheduler-restore-20260704-143637.bak` -> file exists, True (0.3)
- `Get-ChildItem scheduler\scopes -Recurse *.json` -> 23 job files incl. `email-triage-hourly-email-auto-sort.json` (0.4)
- `Get-ScheduledTask opencode-job-*` -> 23 tasks; hourly email auto-sort `Ready` (0.5)
- `Select-String opencode-scheduler` -> no matches (pre-edit) (0.6)
- Literal `Replace` of `@ramtinj95/opencode-tokenscope@latest"` -> appended `,\n    "opencode-scheduler"` (1.1)
- `Select-String '"opencode-scheduler"' -AllMatches` -> count 1 (1.2, 5.1)
- `node -e ... JSON.parse(stripComments)` -> `JSONC parse OK` (1.3)
- `opencode --version` -> `1.15.10` (2.1)
- `Test-Path ...\packages\opencode-scheduler\node_modules\opencode-scheduler` -> `True` (2.2, 5.2)
- `Get-Content package.json | ConvertFrom-Json` -> `opencode-scheduler` / `1.3.0` (2.3)
- `Test-Path hourly-email-auto-sort.json` -> `True` (3.1)
- `$job.schedule; $job.run.command` -> `*/15 * * * *` ; `wscript //B "C:\development\email-triage\scripts\run-hidden.vbs"` (3.2)
- `Get-ScheduledTask hourly task` -> `Ready` (3.3, 5.3)
- `Get-ScheduledTaskInfo hourly task` -> FAILED "The system cannot find the file specified." (KNOWN ISSUE); `Export-ScheduledTask` also failed (0-byte file removed) (3.4)
- `Get-ScheduledTask opencode-job-* | Sort` -> 23 tasks listed (3.5)
- `Test-Path hourly-email-auto-sort.ps1` -> `True` (4.1)
- `Test-Path connect-graph-no-wam.ps1` -> `False` (4.2, FAILED -- see Follow-Up)
- `Select-String Connect-GraphNoWam|CertThumbprint` -> line 798 `Connect-GraphNoWam -ClientId ... -CertThumbprint`, line 37 thumbprint literal (4.3, PASS -- app-only, not delegated)
- `pwsh -File hourly-email-auto-sort.ps1` (Tier-0 deviation: plan said `powershell` PS5.1 which cannot parse this UTF-8 script; used production interpreter `pwsh` 7) -> EXIT 10, auth-failure (4.4)
- `Get-Item Cert:\CurrentUser\My\764A42...` -> `CN=daily-priority-briefing-graph`, NotAfter 3/9/2029, HasPrivateKey=True (4.4 error-recovery -- cert VALID)
- newest `*_run.md` log (`2026-07-04_14-45_run.md`) -> `## Authentication` reached, "No-WAM Graph auth wrapper not found", exit 10, no old `writing to a listener` failure (4.5)


## Validation Results
- Config plugin count (post-edit): **1** (acceptance met)
- JSONC parse after edit: **OK**
- OpenCode CLI version: **1.15.10**
- Plugin cache exists (`packages\opencode-scheduler\node_modules\opencode-scheduler`): **True**
- Plugin package metadata: **name=opencode-scheduler, version=1.3.0**
- Hourly job JSON: schedule `*/15 * * * *`, command `wscript //B "...\run-hidden.vbs"` (current registered values, unchanged)
- Hourly task state: **Ready**
- Hourly task timing metadata: **NOT readable** -- `Get-ScheduledTaskInfo` and `Export-ScheduledTask` both fail with "The system cannot find the file specified." (documented known issue; state-only query succeeds). Captured as follow-up, did not block Phase 3.
- All `opencode-job-*` tasks: **23 total** (22 Ready + 1 Disabled: `...development-offer-validation-round1-daily-rollup`)
- Email auto-sort manual run: **auth-failure, exit code 10** -- "No-WAM Graph auth wrapper not found". Root cause = broken `microsoft-graph` junction (self-referential), NOT the cert (cert is present/valid/has private key).

## Rollback Path
- Backup file: `C:\Users\DaveWitkin\.config\opencode\backups\opencode.jsonc.pre-scheduler-restore-20260704-143637.bak`
- Restore command:
  ```powershell
  Copy-Item "C:\Users\DaveWitkin\.config\opencode\backups\opencode.jsonc.pre-scheduler-restore-20260704-143637.bak" "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Force
  ```
- (Scheduler scope JSON and Windows tasks were not modified, so no rollback is needed for them.)


## Follow-Up Items
1. **[HIGH / out of scope for this track] Broken `microsoft-graph` lazy-skill junction.**
   `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph` is a Junction whose **Target points to itself** (`C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph`), so `scripts\connect-graph-no-wam.ps1` does not resolve. As a result the hourly email auto-sort fails EVERY scheduled run (every 15 min) with exit code 10 / `auth-failure`. The Graph cert (`CN=daily-priority-briefing-graph`, thumb `764A4240264B0F302BE55247A9BC4AB1FBD5C357`, valid until 2029-03-09, private key present) is healthy -- the only defect is the unreachable wrapper. Fix path (separate track): locate the real `microsoft-graph` skill source, remove the self-referential junction, and recreate it pointing at the real source (or restore `connect-graph-no-wam.ps1` directly). This is NOT an email-triage production-code change and NOT a scheduler-plugin change.

2. **[LOW] `Get-ScheduledTaskInfo` / `Export-ScheduledTask` cannot read the hourly email auto-sort task** ("The system cannot find the file specified.") even though `Get-ScheduledTask` reports it as `Ready`. Pre-existing; other tasks exhibit normal behavior. Investigate task registration/definition corruption if/when the task needs modification. Did not block this track.

3. **[INFO] Plan Task 4.4 command used the wrong interpreter.** Plan specified `powershell` (Windows PowerShell 5.1) + `hourly-email-auto-sort.ps1`. The script cannot be parsed by PS 5.1 (UTF-8 special chars / syntax) and the production entry point is `run-hidden.vbs` -> `pwsh.exe` (PS 7) -> `run-hourly-email-auto-sort.ps1` -> child `pwsh` -> `hourly-email-auto-sort.ps1`. Applied Tier-0 deviation: ran with `pwsh` 7 targeting `hourly-email-auto-sort.ps1` (production interpreter). Plan Task 4.4 should be updated to use `pwsh` to match reality.

## Skipped / Deferred Items
- None deferred within this track. All 27 executable tasks were performed.
