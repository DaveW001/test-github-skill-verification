# Spec: Conductor Skill Hardening

Track ID: `20260630-conductor-skill-hardening`
Workspace root: `C:\development\opencode`

## Goal / Outcome
Implement the remaining improvements from `C:\development\opencode\.conductor\docs\conductor-pipeline-run-retro-2026-06-30.md` in the global conductor-pipeline skill: Stage 1 plan hardening, Stage 2 dry-run enforcement, metadata schema cleanup, a PowerShell pitfalls reference, and a global skill versioning/backups reference.

## Constraints / Non-Goals
- Do not execute implementation in Stage 1; only create this track.
- Target files are global skill files outside repo git history under `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\`.
- Create timestamped `.pre-edit.bak` backups before modifying existing targets or overwriting pre-existing new-file targets.
- Use PowerShell-first commands with quoted paths and `-LiteralPath`.
- Do not duplicate already-completed retro improvements except as needed to integrate remaining guidance.

## In Scope
- Edit `stage-prompts.md` Stage 1 prompt block for exactly one authoritative acceptance check per task, diagnostic separation, body-content verification, and literal matching preference.
- Edit `stage-prompts.md` Stage 2/3 prompt block for mandatory dry-runs of every reviewer-added/modified verification command.
- Edit `threshold-policy.md` to define `task_count`, `readiness_check_count`, `total_checkbox_count`, and `completed_tasks` mapping.
- Create `powershell-pitfalls.md`.
- Create `global-skill-versioning.md`.

## Definition of Done
All target files contain the required body guidance, backups exist in the track backup folder, backup-vs-target comparison artifacts are produced, and body-content validation commands pass.
