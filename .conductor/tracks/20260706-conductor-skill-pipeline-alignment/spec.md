# Spec - Conductor Skill <-> Pipeline Drift Reconciliation

**Track ID:** 20260706-conductor-skill-pipeline-alignment
**Type:** maintenance  |  **track_type:** bookkeeping
**Created:** 2026-07-06
**Pipeline determination:** mode=`bookkeeping`, path=`1 -> 5 -> 7 -> 9`
**Peer review:** approved direction 2026-07-06 with required revisions (applied below). Verdict: do-not-execute-as-is; revise first.

## Problem

A related session (track `20260705-conductor-pipeline-tdd-doc-stages`, status `p0-p2-fixes-applied-needs-restart`) added a risk-adjusted pipeline to the **`conductor-pipeline`** skill: four `pipeline_mode` values (full/standard/bookkeeping/emergency), Pipeline Determination, and a Stage 7/8 Terminal closeout gate that verifies `pipeline_mode`/`pipeline_path` match the executed path. Those edits landed 2026-07-06 13:07 in `stage-prompts.md` and `conductor-pipeline\SKILL.md`.

Those changes touched only `conductor-pipeline`, `commands/`, and `agent/`. The separate **`conductor`** skill (templates + Completion Hygiene) was not touched. This produced measurable drift:

1. **`track-metadata.template.json` is non-compliant.** Verified 2026-07-06: it ships only legacy camelCase fields (mtime 2026-01-17) and is missing all 7 fields Stage 1 requires (`track_type`, `test_framework`, `test_command`, `pipeline_mode`, `pipeline_path`, `pipeline_rationale`, `skipped_stages`). A track created from the official template today would fail the Stage 7/8 Terminal closeout gate and halt Stages 4/6.
2. **Stage 1 does not propagate conductor hygiene rules** (Upsert-row ledger wording, dual-ledger registration, 5-point Completion Gate, track-ID convention, 3-state checkboxes, phase numbering, task-safety rules). Confirmed Stage 1 already says: `Phase 0 Setup & Preconditions; Phase 1+ Implementation; Final Phase Validation & Handover`.
3. **`conductor` skill is not pipeline-aware** - its Completion Gate (line 69) predates `pipeline_mode` and still reads `tracks.md and tracks-ledger.md both updated and agree` (unconditional).
4. **Internal contradiction** - conductor Completion Gate says ledgers are always mandatory; Stage 7/8 says conditional ("when the repo uses one").

**Evidence the drift is live (corrected per peer review):** BOTH recent shipping tracks are missing the 4 newer pipeline fields (`pipeline_mode`, `pipeline_path`, `pipeline_rationale`, `skipped_stages`) - neither would pass the new Terminal closeout gate. They differ only in casing convention for the older fields: `20260705-...tdd-doc-stages` uses snake_case names (`track_id`, `task_count`) and carries `track_type`/`test_framework`/`test_command`; `20260706-...closeout-hardening` uses a camelCase+snake_case hybrid (`trackId`, `progress.totalTasks`) plus `track_type`/`test_framework`/`test_command`.

## Scope (in)

Close the drift by making the `conductor` skill the single source of truth for templates/hygiene and pointing Stage 1 at it, then making both skills pipeline-aware and mutually consistent. Six work items across FIVE target files (all backed up first):

- **WI-1** `track-metadata.template.json` - add the 7 pipeline fields (snake_case, matching what Stages 4/6/7/8 read); keep legacy camelCase fields; keep both `type` (work category) and `track_type` (TDD routing). `pipeline_path` is a **selected-path placeholder/example**, NOT a hardcoded bookkeeping default. `test_framework` examples: `none|n/a|bun:test|vitest|jest|pytest|go|<framework>` (matches Stage 1).
- **WI-2** Stage 1 prompt (`stage-prompts.md`) - add a directive to load the `conductor` skill and follow its templates + Completion Hygiene + Completion Gate + Upsert-row ledger convention; register the track in both ledgers; use `YYYYMMDD-slug`; 3-state checkboxes; phase convention `Phase 0 Setup & Preconditions -> Phase 1+ Implementation -> Final Phase Validation & Handover`.
- **WI-3** Reconcile inconsistencies: (a) ledger mandatory-vs-conditional -> align both to "when the repo maintains a ledger"; (b) phase wording -> exact match Stage 1's `Final Phase Validation & Handover` everywhere; (c) `[~]` in-progress vocabulary.
- **WI-4** `conductor/SKILL.md` - pipeline-aware Completion Gate (confirm `pipeline_mode`/`pipeline_path` match executed path when present); change line 69 ledger wording to conditional; add `type` vs `track_type` glossary; cross-reference `conductor-pipeline`.
- **WI-5** `track-plan.template.md` - renumber phases to match Stage 1; add a `pipeline_mode`/`pipeline_path` consistency checkbox to the Final Phase.
- **WI-6** `conductor-pipeline/SKILL.md` - add the pipeline-side cross-reference back to `conductor` (templates/hygiene source). (Reverse direction added in WI-4.)

## Out of scope

- No production/application code.
- No changes to the four pipeline modes, Pipeline Determination logic, or threshold policy (settled by the related session).
- No renumbering of the nine pipeline stages.
- No normalization of ALL metadata to one casing (deliberate: changing 5+ pipeline stages is higher-risk than adding snake_case fields alongside legacy camelCase).
- No backfill/edit of historical track metadata.json files (only the template).

## Decisions (locked, user-delegated 2026-07-06; refined per peer review)

1. **Keep both `type` and `track_type`.** `type` = work category (`feature|bugfix|retro|maintenance|chore`); `track_type` = TDD routing (`code|bookkeeping`).
2. **Casing:** legacy camelCase preserved; pipeline-routing fields added in snake_case.
3. **Phase convention:** exact Stage 1 wording - `Phase 0 Setup & Preconditions`, `Phase 1+ Implementation`, `Final Phase Validation & Handover`.
4. **Template `pipeline_path`:** selected-path placeholder/example, not a bookkeeping default, so future full/standard/emergency tracks do not inherit an incorrect path.
5. **Closeout date:** plain `YYYY-MM-DD` at completion (fractions only for incomplete tracks).

## Validation criteria

- A track created from the updated template carries all 7 pipeline fields, `pipeline_path` as a placeholder, and passes a dry-run of the Stage 7/8 Terminal closeout gate (mode/path semantically consistent, not just present).
- Stage 1 prompt instructs the plan-creator to load the `conductor` skill, use Upsert-row wording, and register both ledgers.
- `conductor/SKILL.md` Completion Gate references `pipeline_mode`/`pipeline_path` consistency and uses conditional ledger wording.
- Both skills agree on ledger-mandatory wording and the exact phase convention.
- All 5 target files backed up before editing; literal/schema checks pass; no production code; ledgers upserted and agree.

## Related tracks

- `20260705-conductor-pipeline-tdd-doc-stages` - added the risk-adjusted pipeline / Pipeline Determination (parked: p0-p2-fixes-applied-needs-restart, 19/22; NOT re-run since 2026-07-05 execution log).
- `20260706-conductor-pipeline-closeout-hardening` - terminal closeout gate, audit-correction, post-doc validation (completed 25/25).

## Risks

- **OpenCode restart required** - agent/skill/command config is not hot-reloaded.
- **Casing churn deferred** - future normalization touches 5+ pipeline stages.
- **Concurrent sessions** - a parallel OpenCode session was active 2026-07-06 editing unrelated tracks (skill-junction-unification); it did not touch the 5 target files, but coordinate on the shared ledgers (upserts are guarded).
