---
name: windows-task-scheduler
description: Create and modify Windows scheduled tasks with descriptions. Use when automating recurring tasks, scheduling scripts, or setting up periodic maintenance.
compatibility:
  - Windows 10/11
  - PowerShell ScheduledTasks module
---

# Windows Task Scheduler

Create and modify Windows Scheduled Tasks using PowerShell's `ScheduledTasks` module, with an emphasis on clear task descriptions and repeatable prompting.

## When to Use This Skill

Use this skill when you need to:
- Create a scheduled task for a script/app (daily/weekly/interval/startup/logon)
- Modify an existing task (trigger/action/user/description)
- Standardize task documentation so future-you can understand "what" and "why"

## Activation Examples

Use this skill when the user says things like:
- "Create a scheduled task to run a PowerShell script every weekday at 7:30am"
- "Change my existing task to run at startup instead of daily"
- "List scheduled tasks and show their descriptions"
- "Disable a task and re-enable it after testing"

## Prerequisites

- Windows Task Scheduler available (built into Windows)
- PowerShell available
- Admin privileges may be required depending on task scope / Run As account

## Core Workflow: Create a New Task

### Step 1: Gather Required Information

Always ask for:
1. Task name
2. Description (what it does + why it exists)
3. Command/script to run (executable or `.ps1`)
4. Arguments (optional)
5. Working directory (optional)
6. Schedule (daily/weekly/every X days/weekdays/startup/logon) + time if applicable
7. Run As account (current user vs SYSTEM vs service account)
8. Documentation path (optional, but ask)

### Step 2: Validate

Before creating the task:
- Confirm the command/script path exists
- Confirm the working directory exists (if provided)
- Confirm schedule details are unambiguous (timezone/time format/days)
- Confirm the description includes both "what" and "why"

### Step 3: Create

- Use `New-ScheduledTaskAction`, `New-ScheduledTaskTrigger`, and `Register-ScheduledTask`.
- Keep the action/trigger code minimal in-chat; put longer recipes in references.

### Step 4: Verify

After creation:
- Confirm the task exists and is enabled
- Show the configured trigger(s)
- Show the stored description
- Explain how to run it manually for a one-time test

## Headless-by-Default Policy for Windows Tasks

When creating or modifying scheduled tasks that run console-capable tools, PowerShell scripts, CLI apps, or `opencode run`, default to the headless-safe launcher pattern:

- Set task `Settings.Hidden = True`.
- Use `wscript.exe` as the task action executable.
- Use `C:\development\_shared-scripts\launch-hidden.vbs` with `//B` to launch PowerShell or the target script hidden.
- Do not rely on `powershell.exe -WindowStyle Hidden` alone for tasks that may spawn child console processes.
- Before modifying an existing task, export rollback XML.
- After creation/modification, force-run the task and ask the user whether any visible window appeared.

Standard action pattern:

Execute:
`wscript.exe`

Arguments:
`//B "C:\development\_shared-scripts\launch-hidden.vbs" "powershell.exe" "-NoProfile" "-ExecutionPolicy" "Bypass" "-WindowStyle" "Hidden" "-File" "<SCRIPT_PATH>"`

### When to Use the Headless Pattern

Use `wscript.exe` + `launch-hidden.vbs` when the task:
- Calls `opencode-run-safe.ps1`, `opencode run`, or any CLI tool that allocates its own console
- Runs a PowerShell script that spawns child processes which may create console windows
- Involves `python`, `node`, or other runtime executables that allocate consoles

### When Direct PowerShell Is Acceptable

Tasks running **direct PowerShell scripts** (no child console processes) can keep `powershell.exe -WindowStyle Hidden` with `Settings.Hidden=True`:
- Scripts using Microsoft Graph API directly
- Indexing/maintenance scripts
- Registry sync scripts
- Proxy management scripts

### Full Documentation

See `C:\development\_shared-scripts\docs\scheduler-headless-runbook.md` for migration procedures, error recovery, and troubleshooting.

## Core Workflow: Modify an Existing Task

### Step 1: Identify the Task

Ask for the exact task name.
If needed, list tasks and let the user choose (see references for commands).

### Step 2: Gather Changes

Ask what to change:
- Description
- Trigger(s)
- Action (command/args/working directory)
- Run As / run level

### Step 3: Apply and Verify

- Retrieve the task, update the relevant fields, then apply changes.
- Verify triggers/actions/description reflect the requested intent.

## Required Prompting Checklist

When creating or modifying tasks, always confirm:
- Task name
- Full description (what + why)
- Command/script
- Arguments (if any)
- Working directory (if any)
- Scheduling details (frequency + time + days)
- Run As account / privileges
- Documentation path (optional, but ask)

## Conventions

- When examples include Windows paths as literals, use forward slashes (example: `C:/scripts/backup.ps1`).
- Keep task descriptions explicit and future-proof (include purpose, cadence, and where docs live).

## References

Deeper examples and command recipes live under `references/`:
- `references/powershell-recipes.md`
- `references/description-examples.md`
- `references/troubleshooting.md`
- `references/complete-walkthrough.md`

---

Version: 2.1.0
Last Updated: 2026-05-01
