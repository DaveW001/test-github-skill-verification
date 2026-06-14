# Handover: Scheduler Desktop/CLI Diagnostics

## Summary
- Decision: Revise restore track
- Primary finding: The `opencode-scheduler` plugin IS installed (in cache at `packages/opencode-scheduler@latest/`), but was removed from the global config plugin array; additionally, the hourly email auto-sort Windows scheduled task is corrupted (registered but underlying definition file is missing).

## Artifacts
- Diagnostic report: `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/diagnostic-report.md`
- Artifact directory: `.conductor/tracks/20260508-scheduler-desktop-cli-diagnostics/artifacts/` (19/19 artifacts present)

## Recommended Next Action
Revise restore track (`20260508-restore-opencode-scheduler-plugin`) with these changes:
1. **Skip plugin reinstallation** — plugin already exists in cache at `packages/opencode-scheduler@latest/node_modules/opencode-scheduler`
2. **Add scheduler back to global config** `plugin` array in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
3. **Recreate corrupted scheduled task** — delete broken `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort` and let scheduler re-register it
4. **Investigate Desktop vs CLI config divergence** — Desktop may use separate config under `XDG_STATE_HOME`

## Blockers or Ambiguities
- Multiple decision rules (B, C, D) were simultaneously true; "Revise restore track" selected per plan criteria
- Unknown: when/why scheduler was removed from global config (backup from March 9 shows it was present)
- Unknown: what caused the scheduled task definition file to go missing (cache cleanup on April 28 is a suspect)
