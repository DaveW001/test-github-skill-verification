# Conductor Pipeline Run Retrospective — 2026-06-30

## Summary
The `20260629-conductor-pipeline-retro-improvements` pipeline run completed successfully and validated cleanly, but it exposed important process issues. The right conclusion is not that the pipeline failed; rather, the multi-stage pipeline worked because it caught defects that a single-pass process likely would have missed. The highest-value improvements are plan-authoring rigor, reviewer-regression prevention, metadata/checklist clarity, and environment preflight propagation.

## What Changed
- Stage 2 strengthened a weak Stage 1 plan by fixing shallow verification checks and one blocking PowerShell bug.
- Stage 3 caught a Stage 2 regression in a newly introduced Task 5.3 path-check regex.
- Stage 4 executed the plan and documented minor PowerShell workarounds.
- Stage 5 independently validated artifacts, bookkeeping, append-only behavior, and helper scripts.
- Stage 6 re-validation was correctly not triggered because no closeout blocker remained.

## What Went Well
- The multi-stage design caught real defects before closeout.
- The B+C re-review trigger worked: adding five acceptance criteria correctly forced a second review pass.
- The Stage 3 re-review justified its cost by catching the Stage 2 regression.
- The validator independently re-ran helper scripts instead of trusting executor claims.
- Append-only verification was evidence-based, using backup-vs-target comparison and `git diff --no-index --numstat`.
- Diversity gates were preserved across review, execution, and validation.

## What Could Be Improved
- Stage 1 produced too many shallow verification checks, especially heading-only or phrase-only checks that could pass without the intended body content.
- Stage 2 fixed many issues but introduced a new blocking verification bug, showing reviewer-added commands need the same dry-run discipline as plan-author commands.
- The plan used PowerShell constructs that needed runtime adaptation: `[string]::Replace()` static overload confusion and scalar `$row[0]` indexing after `Where-Object`.
- The readiness checklist was pre-checked, which can create false confidence because it reads like execution completion even when it is really plan-authoring readiness.
- Metadata/checklist semantics were confusing: metadata tracked 29 tasks while `plan.md` contained 37 checked boxes including 8 readiness items.
- The `Bun is not defined` tool-layer failure was handled, but every stage had to be told or rediscover the shell-first requirement.

## What To Do Differently Next Time
1. Require Stage 1 plans to name one authoritative acceptance check per task and separate it from diagnostic checks.
2. Require reviewers to dry-run every verification command they add or modify, not just commands they suspect are risky.
3. Treat any reviewer-added shell/regex/PowerShell logic as untrusted until executed against a real target or temp copy.
4. Keep readiness criteria separate from executable task checkboxes or label them as `readiness_check_count` rather than tasks.
5. Pass tool preflight status into every child session at launch, including whether native file tools are broken and the exact fallback mapping.
6. Prefer literal matching (`-SimpleMatch`, escaped regex, or `-notlike` when appropriate) over ad hoc regex construction for Windows paths.

## Systemic Issues
- **Plan-authoring quality:** The original plan's shallow verification pattern was systemic, not isolated.
- **Reviewer regression risk:** Reviewers can introduce defects while improving plans; model diversity helps, but dry-run discipline is also required.
- **metadata/checklist semantics:** The pipeline needs clearer distinctions among task count, readiness-check count, and total markdown checkbox count.
- **Environment propagation:** `Bun is not defined` is a session-level tool failure, not a per-call failure; future stage prompts should propagate that state immediately.
- **Unversioned global skill edits:** Global files under `C:\Users\DaveWitkin\.config\opencode\skill\` are outside the repo's git history, so backups and/or a versioning workflow are needed.
- **Observability:** A separate `issues-and-deviations-<YYYY-MM-DD>.md` artifact is not currently required for clean runs, but it would improve aggregation of non-blocking process lessons.

## Lessons Learned
- A successful closeout can still reveal pipeline improvements.
- Conditional re-review is valuable when review changes are structurally significant or technically risky.
- Shallow checks are often worse than no checks because they create false confidence.
- PowerShell verification snippets should be treated as executable code and tested accordingly.
- Metadata progress should be compared to the same unit it claims to count; do not compare task counters to unrelated readiness checklist items.
- Tool-layer failures must be elevated to handoff context, not rediscovered by every subagent.

## Codify / Reuse
- Add Stage 1 guidance requiring authoritative checks and body-content verification.
- Add Stage 2 guidance requiring exact dry-runs of all reviewer-added verification commands.
- Add threshold-policy guidance clarifying optional issues/deviations artifacts and Stage 6 metadata drift interpretation.
- Add or update a PowerShell pitfalls reference for Conductor validation snippets.
- Add a global-skill versioning/backups reference for files edited outside repo git history.
- Consider a future metadata schema update with `task_count`, `readiness_check_count`, and `total_checkbox_count`.

## Recommended Priority Order
1. Plan authoring hardening.
2. Reviewer-added command dry-run enforcement.
3. Metadata/checklist semantic cleanup.
4. Tool preflight propagation enforcement.
5. Optional issues/deviations artifact for observability.
6. Global skill versioning policy.

## Validation
- Confirmed original track validation report reported `Ready to close` with no mismatches.
- Confirmed helper scripts pass independently against the smoke-test fixture and current track.
- Confirmed no `change-log.md` or `issue-log.md` existed; reclassified as optional observability rather than a missed requirement.
- Confirmed threshold policy currently requires `validation-blockers-<timestamp>.md` only when blocked.
