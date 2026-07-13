---
name: scheduled-job-best-practices
description: Patterns for resilient, non-interactive scheduled opencode jobs
---

## Use This Skill

Put this line at the very top of any scheduled job prompt:

@scheduled-job-best-practices

Then write your task below it.

## Central Workspace Rule

**Always schedule jobs from `C:\development`.**

The OpenCode scheduler uses scope IDs tied to where jobs are created/managed. If you schedule from different project folders, jobs can scatter across separate scopes and become invisible to `list_jobs` unless you're in the right folder. To keep jobs discoverable in one place:

- **Create** all new scheduled jobs from `C:\development`.
- **Migrate** any jobs found in other scopes into the `C:\development` scope.
- **Verify** with `list_jobs` from `C:\development` after creating or migrating.

Exception: True system-level jobs (e.g., proxy startup) that run outside any repo may live in the global scope, but should still be documented in the central ledger (`.conductor/tracks/` under `C:\development`).

## Core Principles

1. **No magic injection.** Do not assume placeholders like __TODAY__ exist. Compute runtime values using tools (bash) during the run.
2. **Non-interactive.** Scheduled jobs must not rely on QR codes, manual logins, or confirmation dialogs.
3. **Idempotent.** Make reruns safe (maintain a seen/state file; avoid duplicate messages).
4. **Observable.** Print a short summary at the end with status + outputs.
5. **Minimal side effects.** Write durable artifacts under outputs/ in the job workdir.
6. **Centralized scheduling.** Always create and manage scheduled jobs from `C:\development`.
7. **Registry maintenance.** After creating, modifying, or deleting any scheduled job, you MUST update `C:\development\_shared-scripts\scheduler-registry.md` to reflect the change. Optionally run `C:\development\_shared-scripts\Sync-SchedulerRegistry.ps1` to regenerate the registry automatically.

## Scheduler Registry

The scheduler registry at `C:\development\_shared-scripts\scheduler-registry.md` is the human- and agent-readable index of all OpenCode scheduled jobs. It is the single place to look to understand what jobs exist, their status, and their configuration.

**Mandatory:** Any agent that creates, modifies, or deletes a scheduled job must update this registry immediately after the change. The automated sync script (`Sync-SchedulerRegistry.ps1`) runs daily as a reconciliation backstop, but active maintenance prevents stale windows.

## Runtime Values: Dates

If you need local dates, compute them at runtime.

### macOS

~~~bash
TODAY="$(date +%F)"
TOMORROW="$(date -v+1d +%F)"
~~~

### Linux

~~~bash
TODAY="$(date +%F)"
TOMORROW="$(date -d 'tomorrow' +%F)"
~~~

### Windows (PowerShell)

~~~powershell
$TODAY = (Get-Date -Format "yyyy-MM-dd")
$TOMORROW = (Get-Date (Get-Date).AddDays(1) -Format "yyyy-MM-dd")
~~~

### Portable snippet (Bash)

~~~bash
if [ "$(uname)" = "Darwin" ]; then
  TODAY="$(date +%F)"
  TOMORROW="$(date -v+1d +%F)"
else
  TODAY="$(date +%F)"
  TOMORROW="$(date -d 'tomorrow' +%F)"
fi
~~~

If timezone matters, set TZ explicitly (example: TZ=America/Los_Angeles date +%F).

## Preflight Checklist

Before doing any expensive work:

- Confirm required tools are available (browser, network, etc).
- Confirm required env vars exist (source .env only if needed).
- If a dependency is missing/offline, stop early and emit a single concise reason.

## Notifications (Telegram)

Prefer the Telegram Bot API (non-interactive) over web.telegram.org.

## Output Contract

End every run with a compact summary:

- Status: success | skipped | failed
- Reason (1 line)
- Outputs written (paths)
- Notifications sent (message_id, chat_id) if applicable

## Idempotency Pattern

When notifying about "new" items (deals, alerts, etc.):

- Store a seen list in outputs/<job>/seen.json
- Only notify on items not in seen.json
- Update seen.json after sending
