# Diagnostic Report: OpenCode Scheduler Desktop/CLI Divergence

## Executive Decision
Decision: Revise restore track

## Evidence Summary

### Desktop UI evidence
User screenshot shows `opencode-scheduler` listed as loaded (7 plugins total). Environment variable `OPENCODE_CLIENT=desktop` confirms Desktop runtime.

### Global config evidence
**0 scheduler references** in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`. The `plugin` array contains 6 entries: `opencode-snippets`, `@zenobius/opencode-skillful`, `oc-codex-multi-auth`, `opencode-ignore`, `opencode-mystatus`, `@tarquinen/opencode-dcp`. No `opencode-scheduler`.
- Artifact: `artifacts/global-config-plugin-block.txt`, `artifacts/global-config-scheduler-count.txt`

### Standard cache evidence
Scheduler **NOT** at expected path `C:\Users\DaveWitkin\.cache\opencode\node_modules\opencode-scheduler`.
- Artifact: `artifacts/standard-cache-scheduler-exists.txt`

### Alternate config/cache evidence
- **Backup config**: `opencode.json.bak-20260309-093134` contains `"opencode-scheduler"` at line 4 — scheduler was in global config as of March 9, 2026.
- **Cache (alternate path)**: Scheduler exists at `C:\Users\DaveWitkin\.cache\opencode\packages\opencode-scheduler@latest\node_modules\opencode-scheduler` — the package is installed but under `packages/` not directly under `node_modules/`.
- **Cache backup**: Also present in `opencode-cache-backup-20260428-094635` (both `node_modules/` and `packages/` paths).
- **Desktop directories**: No scheduler references found in any of 7 Desktop-related directories under `AppData\Roaming` or `AppData\Local`.
- **Environment**: `XDG_STATE_HOME=C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\` — Desktop may use XDG paths for effective config.
- Artifact: `artifacts/config-dir-scheduler-references.txt`, `artifacts/scheduler-package-directories.txt`, `artifacts/desktop-scheduler-references.txt`, `artifacts/opencode-env-vars.txt`

### Scheduler scope evidence
10 scheduler scope JSON files across 4 scopes: development (6 jobs), email-triage (1 job), marketing (1 job), opencode-global (2 jobs). The hourly email auto-sort job is valid: schedule `0 */1 * * *`, command `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\development\email-triage\scripts\hourly-email-auto-sort.ps1"`, workdir `C:\development\email-triage`.
- Artifact: `artifacts/scheduler-scope-json-files.txt`, `artifacts/hourly-job-summary.txt`, `artifacts/hourly-job-command.txt`

### Windows task evidence
- Task registered at `\OpenCode\opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`, State = `Ready`.
- **CRITICAL**: `Get-ScheduledTaskInfo` fails with "The system cannot find the file specified" — task registration is corrupted (listed but underlying task definition file is missing or inaccessible).
- `Export-ScheduledTask` fails with the same error — confirms corruption.
- 10 total `opencode-job-*` tasks exist (9 Ready, 1 Disabled).
- No TaskScheduler operational events found for this task.
- Artifact: `artifacts/hourly-task-registration.txt`, `artifacts/hourly-task-info.txt`, `artifacts/hourly-task.xml`, `artifacts/all-opencode-tasks.txt`, `artifacts/hourly-task-events.txt`

### Recent runtime evidence
Email-triage logs directory exists but contains no `.log` files. No recent execution evidence.
- Artifact: `artifacts/recent-email-triage-logs.txt`

## Reconciliation

**Why Desktop and CLI evidence conflict:**

1. **Plugin presence**: The scheduler plugin IS installed — it exists in the cache at `packages/opencode-scheduler@latest/node_modules/opencode-scheduler`. Desktop loads it from this path. The global config `opencode.jsonc` no longer lists it (was removed between March 9 backup and now), but Desktop may resolve plugins from the cache independently of the config file, or the config was edited outside Desktop.

2. **Task corruption**: The Windows scheduled task for the hourly email auto-sort job is in a corrupted state — it appears in `Get-ScheduledTask` listings (registry entry exists) but `Get-ScheduledTaskInfo` and `Export-ScheduledTask` both fail with "file not found" (the underlying task XML definition file is missing). This explains the ~85% failure rate previously observed.

3. **Root cause hypothesis**: The scheduler plugin was likely removed from the global config plugin array (manually or by a config sync), but Desktop cached the plugin list separately. Meanwhile, the scheduled task definition file was deleted or corrupted (possibly during a cache cleanup on April 28, which created the backup directory).

## Recommendation

**Revise the restore track** (`20260508-restore-opencode-scheduler-plugin`) with these changes:

1. **Skip plugin reinstallation** — the plugin is already in the cache at the `packages/` path. Instead, add the plugin back to the global config `plugin` array.
2. **Recreate the corrupted scheduled task** — delete the broken task registration and let the scheduler re-register it, or manually recreate it from the job definition JSON.
3. **Reconcile config sources** — investigate why Desktop and CLI have different plugin lists. Check if Desktop writes to a separate config file (possibly under `XDG_STATE_HOME`).
4. **Do not focus on plugin installation** — the plugin is present; the issues are (a) config registration and (b) task corruption.

## Decision Rule Analysis

- **Rule A** (absent from all locations): REJECTED — scheduler found in cache and backup config.
- **Rule B** (present in Desktop cache, absent from global config): TRUE — matches evidence.
- **Rule C** (present in effective config/cache): TRUE — scheduler is in the cache.
- **Rule D** (scheduler healthy but job lacks recent success): TRUE — task is corrupted, no recent events.

Multiple rules true → per plan criteria: **Revise restore track** and document ambiguity.
