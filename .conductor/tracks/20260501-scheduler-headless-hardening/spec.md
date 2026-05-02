# Spec: Scheduler Headless Hardening

## Goal

Standardize OpenCode scheduled tasks to launch headlessly on Windows, preventing visible terminal popups from child console processes (especially `opencode run`), and codify the pattern so future tasks are created correctly by default.

## Background

Track `20260501-headless-scheduled-tasks` proved that task-level `Settings.Hidden=True` alone is not always sufficient. The `knowledge-base-ingest` task still popped a visible console window (`01-planner.glm-5.1`) because `opencode run` spawned a child console. A `wscript.exe` + VBS hidden launcher pattern resolved it.

## Requirements

- [ ] Build a complete task inventory for `\OpenCode\` with action + risk classification.
- [ ] Apply a headless-safe launch pattern to all tasks where child console popups are plausible.
- [ ] Keep non-applicable tasks unchanged and document the rationale.
- [ ] Validate changed tasks with manual force-run checks and task result verification.
- [ ] Document the headless runbook for reuse.
- [ ] Update scheduler skill/workflow guidance so future scheduling defaults to headless-safe actions.

## Non-Requirements

- [ ] Rewriting business logic of job scripts.
- [ ] Changing account model (`Interactive` vs `S4U`) unless explicitly requested.
- [ ] Modifying unrelated non-OpenCode scheduled tasks.

## Acceptance Criteria

- [ ] Inventory matrix exists with decision outcome for each OpenCode task.
- [ ] All applicable tasks use `wscript.exe //B` + `launch-hidden.vbs` action pattern.
- [ ] `Settings.Hidden=True` is preserved for all OpenCode tasks.
- [ ] At least one representative forced run validates no visible popup.
- [ ] `scheduler-headless-runbook.md` documents implementation and troubleshooting.
- [ ] `windows-task-scheduler` skill includes headless-by-default policy and validation checklist.

## Headless Pattern (Target)

- Execute: `wscript.exe`
- Arguments: `//B "C:\development\_shared-scripts\launch-hidden.vbs" "powershell.exe" "-NoProfile" "-ExecutionPolicy" "Bypass" "-File" "<script.ps1>" ...`
- Task setting: `Settings.Hidden=True`
