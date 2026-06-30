# Review Diff Summary - 20260629-conductor-pipeline-retro-improvements

- **Stage:** 2 (Plan Review)
- **Reviewer model:** `opencode-go/minimax-m3` (M3)
- **Reviewer timestamp:** 2026-06-29-162817
- **Files modified:** `plan.md`, `spec.md`
- **Files NOT modified:** `metadata.json`, all global skill files, all execution-time artifacts

---

## High-Confidence Edits Applied Directly

### `plan.md` (32,356 bytes -> 47,605 bytes)

14 surgical fixes applied. Each fix replaces a single task block in-place; no task was added or removed; no phase boundary moved.

| # | Task | Change | Reason |
|---|---|---|---|
| 1 | 1.1 | Replaced shallow "count==1" verification with content checks for `git diff --no-index <backup> <target>` AND `git diff -- <path>` substrings; added labeled-command template | The original "Required snippet includes" content was never actually verified - a heading-only insertion would pass. |
| 2 | 1.2 | Added content checks for `line-anchored` and `## Hello World` substrings; clarified that the regex is inserted as LITERAL TEXT because verification uses `-SimpleMatch` | Original verification could pass with an empty idempotency section. |
| 3 | 1.3 | Added content check for `temp copy` to confirm the follow-on sentence about readiness-score reduction | Original only checked for the first sentence's phrase. |
| 4 | 1.4 | Added content check for `diagnostic checks` to confirm the contrast with `authoritative acceptance checks` | Original only checked for one phrase; the contrast was never verified. |
| 5 | 1.5 | Added content checks for all 5 required checklist items (`plan.md`, `metadata.json`, `tracks.md`, `tracks-ledger.md`, `execution-log-`) AND the `Upsert rows...` phrase | Original only checked the heading; an empty heading would have passed. |
| 6 | 1.6 | Added content checks for all 4 required body lines (`file-tool status`, `fallback shell`, `path quoting`, `Bun is not defined`); specified insertion must be before `## Stage 1` | Original only checked the heading. |
| 7 | 1.7 | Added content checks for `minor follow-up` and `Stage 6` to confirm the classification and owner | Original only checked for the bookkeeping phrase; the ownership transfer was never verified. |
| 8 | 2.1 | Added content check for `## Scope Language` heading exactly once | Original only checked for the two body phrases; the heading anchor was never verified. |
| 9 | 2.2 | Added content checks for all 5 required bullet phrases (each `- ` line); changed to `Add-Content` since the section is appended to the end | Original only checked the heading; the bullets were never verified. |
| 10 | 5.1 | Replaced shallow literal-phrase check with content checks for 4 log sections (`## Changed Files`, `## Validation Commands Run`, `## Deviations / Issues`, `## Handover Notes`) AND 8 file path mentions (every file that will be changed) | The original "Test-AppendOnly.ps1 smoke test" check is trivially fakeable. |
| 11 | 5.2 | Replaced status-only check with full schema check: `status=executed`, `progress.phase=executed`, `progress.completed_tasks=29`, `progress.total_tasks=29`, `executed_at=2026-06-29`; provided the exact JSON shape | The original verification only checked `.status` and missed 4 other fields the task claims to set. |
| 12 | 5.3 | Replaced count-only check with content checks: row must contain `\| executed \|`, `\| 2026-06-29 \|`, and the correct absolute path; provided the exact replacement logic | The original count==1 check is vacuous because the row already exists - the count is 1 before AND after the update. |
| 13 | **5.4** | **REPLACED BROKEN `Where-Object { $_ -like '*[trackid]*' }` with `Where-Object { $_ -match '\[trackid\]' }`**; added content checks for `Phase: executed 2026-06-29` and absence of `Phase: planning`; documented the bug in the task's `Command` block | **BLOCKING**: The original `-like` pattern with square brackets throws `WildcardPatternException` because PowerShell treats `[...]` as wildcard character classes and the hyphens create invalid character ranges. Verified by test execution: original throws, fixed returns 1. |
| 14 | 6.5 | Replaced literal-phrase check with content checks for 3 required handover lines (`Final status: executed.`, `Validation: all acceptance criteria met.`, `Next recommended smoke test: ...`) | The original `Final status: executed.` check is trivially fakeable. |

### `spec.md` (6,214 bytes -> 7,393 bytes)

5 new acceptance criteria added (items 11-15) to bring the spec in alignment with the plan's expanded scope. The plan's task 1.3, 1.4, 1.6, 1.7, and 2.1 all add content that the spec's original 10 ACs did not cover.

| # | New AC | Source task |
|---|---|---|
| 11 | `stage-prompts.md` contains `Reviewer-added verification commands must be dry-run exactly as written` | Plan task 1.3 (anti-laziness dry-run standard) |
| 12 | `stage-prompts.md` contains both `authoritative acceptance checks` AND `diagnostic checks` | Plan task 1.4 (classification standard) |
| 13 | `stage-prompts.md` contains `### Tool preflight` with all 4 body lines | Plan task 1.6 (environment handoff) |
| 14 | `stage-prompts.md` contains `correct deliverable but stale Conductor bookkeeping` + `minor follow-up` + `Stage 6` | Plan task 1.7 (validator ownership) |
| 15 | `SKILL.md` contains heading `## Scope Language` | Plan task 2.1 (scope-language section anchor) |

---

## Surfaces for User (NOT applied)

These are observations the reviewer noticed but did NOT auto-fix because they touch on judgment calls or affect task structure:

### 1. Reference script content for tasks 4.1 and 4.3
- **Observation:** The plan requires creation of `Test-AppendOnly.ps1` and `Test-ConductorTrackCloseout.ps1` with detailed behavior lists, but provides no reference implementation. A less-capable executor (GLM 5.2) will need to write the scripts from scratch and may iterate.
- **Recommendation:** The user may want to provide a reference script in the plan (e.g., inline the full PowerShell) or accept the iteration cost during execution. The smoke tests in 4.2 and 4.4 will catch most logic bugs.
- **Decision:** SURFACED, not applied.

### 2. `total_tasks` in `metadata.json`
- **Observation:** `metadata.json` has `"total_tasks": 29`. The plan's 5 new acceptance criteria (spec items 11-15) are not tasks, so 29 is still correct.
- **Decision:** No change to `metadata.json`.

### 3. Restructuring of 2.3 (already-present verification)
- **Observation:** Task 2.3 duplicates the verifications from 2.1 and 2.2. After the 2.1 and 2.2 fixes, 2.3 is now slightly redundant but harmless.
- **Decision:** No change; redundancy is acceptable for an explicit re-verification step.

### 4. Plan's `## Execution Readiness Checklist` says all 8 items are pre-checked `[x]`
- **Observation:** The execution-readiness checklist has all 8 items pre-marked complete. This is a Stage 1 template convention; it does not reflect actual readiness, and a less-capable executor might trust it without running the new content checks. The Stage 3 re-review trigger (B+C hybrid) requires `task count changed by >= 20%` or `readiness < 90%` or any Blocking item. With 0 Blocking and 92% readiness, the B+C threshold is not triggered.
- **Decision:** SURFACED, no change. The pre-checked list is a template convention; the actual readiness is in this review.

---

## Structural Changes Summary (for Stage 3 threshold check)

- **Acceptance criteria count change:** +5 (spec items 11-15). The threshold for B+C is `acceptance-criteria count changed by >= 2`. **THRESHOLD MET: +5 >= +2**.
- **Phase count change:** 0 (still 6 phases: 0, 1, 2, 3, 4, 5, Final).
- **Task count change:** 0 (still 29 non-deferred tasks). The threshold is `>= 20%` (which would be 6+ task changes). NOT MET.
- **Readiness score:** 92% (>= 90%). NOT MET for the `< 90%` trigger.
- **Blocking items remaining:** 0. NOT MET for the Blocking trigger.

**Trigger evaluation:** B+C = `(structural change is large) OR (readiness < 90%) OR (any task rated Blocking remains unresolved)`. Two of three sub-conditions: AC count change >= 2 (MET), readiness < 90% (NOT MET), Blocking (NOT MET). At least one is met (AC change), so the B+C trigger IS MET.

**Recommend: run Stage 3 re-review (conductor-plan-reviewer-alt = openai/gpt-5.5 low) to validate the high-confidence edits applied in this Stage 2 review.** This is a one-pass re-review cap.
