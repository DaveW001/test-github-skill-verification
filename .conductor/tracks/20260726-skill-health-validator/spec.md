# Spec

## Goal

Harden the existing daily `skill-health-validator` job so it validates the current OpenCode skill architecture, applies only safe/idempotent repairs, and produces trustworthy reports without creating junction corruption or false index alarms.

## Current Evidence

- The scheduled job already exists in the central `C:\development` scope as `skill-health-validator` (`0 6 * * *`); do not create a duplicate job.
- Its launcher reads `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md` and runs it through `C:\development\_shared-scripts\skill-health-validator-quiet.ps1`.
- The architecture runbook establishes that `C:\Users\DaveWitkin\.codex\skills` is a parent junction to `C:\Users\DaveWitkin\.opencode-lazy-vault`; child junction creation under it is forbidden.
- `.agents\skills` is archived/absent and is not an active required surface; the validator must not recreate it.
- The current report shows 7 canonical skills checked and 38 index flags because the index is historical and contains many lazy-vault names. This is a known taxonomy/authority mismatch that must be resolved explicitly rather than silently hiding flags.
- The current archive-cleanup instruction uses `Remove-Item` on junctions, which conflicts with the architecture runbook's safe-removal rule (`cmd /c rmdir` for junctions).

## Requirements

- [ ] Preserve the supplied validator checks: preflight, canonical frontmatter flags, index freshness checks, junction consistency, archive hygiene, report generation, exact console summary, idempotency, and exclusions.
- [ ] Treat the architecture runbook as authoritative: detect the Codex parent-junction-to-vault state and skip Codex child-junction creation in that state.
- [ ] Never remove a junction/reparse point with recursive or content-destructive semantics; classify the item first and use a junction-safe removal path.
- [ ] Keep frontmatter issues and missing/stale index entries as flags only; do not mutate frontmatter or add missing index entries.
- [ ] Make index stale-name replacement precise to one verified table row and do not rewrite the index when no safe rename is identified.
- [ ] Make report and CSV writes deterministic and idempotent, including one row per date and a stable count of auto-fixes/flags.
- [ ] Preserve the required final console output format exactly.
- [ ] Validate only canonical skill directories containing `SKILL.md`, excluding directories whose names begin with `_`, package-managed skills, and project-local skills.
- [ ] Document the authority decision for the historical global index. If lazy-vault skills are intentionally outside the canonical validation set, report them as index-stale flags rather than auto-adding them.
- [ ] Keep the existing daily schedule and registry entry unchanged unless implementation verification demonstrates drift.

## Non-Requirements

- [ ] Do not create a second scheduled job or migrate the existing job to another scope.
- [ ] Do not write production application code or modify the architecture runbook as part of this track.
- [ ] Do not auto-repair frontmatter, add missing index rows, categorize skills, or recreate `.agents\skills`.
- [ ] Do not validate package-cache or project-local skills.
- [ ] Do not remove archived skill content; only remove a conflicting surface entry when it is proven to be an orphaned junction/directory and the safe-removal policy permits it.

## Acceptance Criteria

- [ ] A dry-run or controlled validation demonstrates successful preflight and correctly identifies the Codex parent junction without child-junction creation.
- [ ] A fixture/test review proves malformed frontmatter is flagged only, safe index rename handling is narrow, missing entries remain flags, and archive cleanup cannot recursively delete a junction target.
- [ ] Two consecutive runs produce no duplicate junctions, no duplicate CSV date row, and equivalent report counts/content apart from the runtime date when applicable.
- [ ] The generated report contains total checked, issue count, separate auto-fix and manual-flag sections, and a one-sentence summary.
- [ ] The final console output matches the required five-line contract.
- [ ] The existing `skill-health-validator` job remains the only validator job, and `C:\development\_shared-scripts\scheduler-registry.md` still reflects it.
- [ ] All tasks in `plan.md` are marked `[x]` by the Build agent before track completion.
