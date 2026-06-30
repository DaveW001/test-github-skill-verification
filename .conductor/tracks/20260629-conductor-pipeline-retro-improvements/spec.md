# Spec: Conductor Pipeline Retrospective Improvements

## Goal / Outcome
Codify every improvement identified by the retrospective of the `20260629-smoke-test-hello-world` Conductor Pipeline run so future AI and human operators can reuse the lessons without rediscovering them. The implementation will update the Conductor Pipeline skill guidance, add reusable append-only and closeout documentation, add optional validation helper scripts, and strengthen executor/validator prompts around metadata synchronization and evidence quality.

## Background
The smoke-test run succeeded, but it exposed reusable pipeline lessons:

1. A file can live inside a git repo while still being untracked, so path-scoped `git diff -- <path>` can be insufficient.
2. Idempotency checks must match semantic structure, not loose substrings.
3. Append-only verification should prove byte-prefix preservation and additions-only diff behavior.
4. Reviewer-added verification commands need exact dry-run validation.
5. Conductor closeout state is split across `metadata.json`, `plan.md`, `tracks.md`, and `tracks-ledger.md`.
6. Pipeline prompts should distinguish deliverable/application scope from Conductor bookkeeping scope.
7. Stage handoffs should propagate tool/environment preflight facts, such as file-tool fallback guidance.

## Constraints / Non-goals
- Do not execute the implementation in this planning track.
- Preserve existing Conductor Pipeline behavior unless a change directly codifies a retrospective lesson.
- Do not edit application/runtime code outside the explicitly planned helper scripts.
- Do not require a clean git working tree; existing unrelated dirty files may remain dirty.
- Any edits to global OpenCode skill files under `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\` must be treated as global behavior changes and validated by re-reading the files.
- New repo-local helper scripts must live under `.conductor/scripts/` and be narrowly scoped to Conductor validation utilities.
- New repo-local documentation must live under `.conductor/docs/`.

## Definition of Done
- The Conductor Pipeline skill docs/prompts include a target file-state decision tree.
- The Conductor Pipeline skill docs/prompts include semantic/structural idempotency guidance.
- The Stage 4 executor prompt includes a closeout synchronization checklist for `plan.md`, `metadata.json`, `tracks.md`, `tracks-ledger.md`, and execution logs.
- Stage handoff guidance includes environment/tool preflight propagation.
- Plan-review standards require exact dry-runs of newly introduced verification snippets and distinguish authoritative acceptance checks from convenience/diagnostic checks.
- Repo-local runbook `.conductor/docs/append-only-verification.md` exists and documents the append-only verification pattern.
- The Conductor Pipeline README contains a smoke-test lessons section documenting the untracked-file, no-index diff, semantic idempotency, and closeout-sync lessons.
- Helper script `.conductor/scripts/Test-AppendOnly.ps1` exists and validates backup-vs-target append-only edits.
- Helper script `.conductor/scripts/Test-ConductorTrackCloseout.ps1` exists and validates track closeout synchronization.
- Executor and validator guidance explicitly assigns ownership and classification of closeout metadata mismatches.
- A smoke validation against `C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md` and `C:\development\opencode\.conductor\smoke-test\hello-world.md` passes.
- The track artifacts are synchronized: `plan.md`, `metadata.json`, `.conductor/tracks.md`, and `.conductor/tracks-ledger.md` agree on status at handover.

## Acceptance Criteria
1. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` contains the exact heading `### Target file-state decision tree`.
2. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` contains the regex example `^##\s+Hello World\s*$`.
3. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` contains the exact heading `### Executor closeout synchronization checklist`.
4. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` contains the exact phrase `deliverable/application scope` and the exact phrase `pipeline bookkeeping scope`.
5. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md` contains the exact heading `## Smoke-Test Lessons Learned`.
6. `C:\development\opencode\.conductor\docs\append-only-verification.md` exists and contains `git diff --no-index --numstat`.
7. `C:\development\opencode\.conductor\scripts\Test-AppendOnly.ps1` exists and exits 0 when run against the smoke-test backup and target.
8. `C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1` exists and exits 0 when run against `20260629-smoke-test-hello-world` after index synchronization.
9. `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\execution-log-2026-06-29.md` documents every file changed, validation command run, and deviation encountered.
10. `.conductor/tracks.md` and `.conductor/tracks-ledger.md` contain exactly one row/entry for this track and show the final status/date at closeout.
11. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` contains the phrase `Reviewer-added verification commands must be dry-run exactly as written` (plan task 1.3, anti-laziness dry-run standard).
12. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` contains both phrases `authoritative acceptance checks` and `diagnostic checks` (plan task 1.4, classification standard).
13. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` contains the heading `### Tool preflight` with all four required body lines: `file-tool status`, `fallback shell`, `path quoting`, `Bun is not defined` (plan task 1.6, environment handoff).
14. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` contains the phrase `correct deliverable but stale Conductor bookkeeping` plus the classification `minor follow-up` and owner `Stage 6` (plan task 1.7, validator ownership).
15. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` contains the heading `## Scope Language` (plan task 2.1, scope-language section anchor).

## Files Expected to Change
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`
- `C:\development\opencode\.conductor\docs\append-only-verification.md`
- `C:\development\opencode\.conductor\scripts\Test-AppendOnly.ps1`
- `C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1`
- `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\plan.md`
- `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\metadata.json`
- `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\execution-log-2026-06-29.md`
- `C:\development\opencode\.conductor\tracks.md`
- `C:\development\opencode\.conductor\tracks-ledger.md`
