# Task Inventory: Scheduler Headless Hardening

Generated: 2026-05-01

| TaskName | State | Hidden | LogonType | Execute | Classification | Rationale |
| --- | --- | --- | --- | --- | --- | --- |
| opencode-job-development-88876ee600f5-development-conductor-weekly-report | Ready | True | Interactive | powershell.exe | Migrate to wscript | Arguments contain `opencode-run-safe.ps1`; child `opencode run` can pop console |
| opencode-job-development-88876ee600f5-development-offer-validation-round1-daily-rollup | Disabled | True | Interactive | powershell.exe | Migrate to wscript | Arguments contain `opencode-run-safe.ps1`; task is currently Disabled but should be hardened for when re-enabled |
| opencode-job-development-88876ee600f5-development-osgrep-auto-indexer | Ready | True | Interactive | powershell.exe | Keep as-is | Runs `Update-OsgrepIndex.ps1` directly — no `opencode run` child process |
| opencode-job-development-88876ee600f5-development-scheduler-registry-sync | Ready | True | Interactive | powershell.exe | Keep as-is | Runs `Sync-SchedulerRegistry.ps1` directly — no `opencode run` child process |
| opencode-job-development-88876ee600f5-knowledge-base-ingest | Ready | True | Interactive | wscript.exe | Already migrated | Previously migrated in track `20260501-headless-scheduled-tasks` |
| opencode-job-development-88876ee600f5-skill-health-validator | Ready | True | Interactive | powershell.exe | Migrate to wscript | Wrapper `skill-health-validator-quiet.ps1` calls `opencode-run-safe.ps1`; child `opencode run` can pop console |
| opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort | Ready | True | Interactive | powershell.exe | Keep as-is | Runs `hourly-email-auto-sort.ps1` directly via Microsoft Graph — no `opencode run` child process |
| opencode-job-marketing-1cd46ed3b6ad-skill-sync-monitor | Ready | True | Interactive | powershell.exe | Migrate to wscript | Arguments contain `opencode-run-safe.ps1`; child `opencode run` can pop console |
| opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-monitor | Ready | True | ServiceAccount | powershell.exe | Keep as-is | Runs `monitor-proxy.ps1` directly under SYSTEM — no `opencode run` child process |
| opencode-job-opencode-global-7a3f9c2e1b84-gemini-proxy-starter | Ready | True | Interactive | powershell.exe | Keep as-is | Runs `start-proxy-quiet.ps1` directly — no `opencode run` child process |

## Summary

| Classification | Count | Tasks |
| --- | --- | --- |
| Already migrated | 1 | knowledge-base-ingest |
| Migrate to wscript | 4 | conductor-weekly-report, offer-validation-round1-daily-rollup, skill-health-validator, skill-sync-monitor |
| Keep as-is | 5 | osgrep-auto-indexer, scheduler-registry-sync, hourly-email-auto-sort, gemini-proxy-monitor, gemini-proxy-starter |
