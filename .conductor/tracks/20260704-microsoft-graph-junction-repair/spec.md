# Spec: Microsoft Graph Junction Repair

Track id: `20260704-microsoft-graph-junction-repair`
Workspace: `C:\development\opencode`
Source handoff: `C:\development\opencode\.opencode\handoffs\20260704-1715-scheduler-followups.md`

## Goal / outcome
Repair the self-referential lazy-vault `microsoft-graph` junction that blocks hourly email auto-sort Graph auth; then safely handle the broader lazy-vault cohort, diagnose scheduled-task metadata reads, and fix scheduler-restore bookkeeping.

## Constraints / non-goals
Do not change scheduler cadence or `*/15 * * * *` job JSON. Do not edit email-triage production logic except to confirm auth. Do not rotate the Graph cert. Do not delete/recreate the scheduled task without approval. Never remove real directories: only remove paths where `LinkType` is exactly `Junction`. Missing OneDrive sources must be skipped and reported. Use `pwsh`, not `powershell`.

## Definition of done
- `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph` targets `C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\microsoft-graph`, not itself.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1` exists.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File C:\development\email-triage\scripts\hourly-email-auto-sort.ps1` reaches app-only Graph auth and newest `C:\development\email-triage\logs\*_run.md` does not contain `No-WAM Graph auth wrapper not found`.
- Systemic lazy-vault preview/report exists and guarded repairs are applied only where source exists.
- Scheduled-task info/export issue is either fixed or documented with safe remediation; no unapproved task recreation.
- Source track plan/metadata bookkeeping is corrected.
