# Plan - Conductor Skill <-> Pipeline Drift Reconciliation

**Track ID:** 20260706-conductor-skill-pipeline-alignment
**Pipeline:** bookkeeping (`1 -> 5 -> 7 -> 9`). All edits are skill/config/template docs; no production code.
**Peer review 2026-07-06:** direction approved; revisions applied (5th target file in backups; phase wording = Stage 1 exact; template pipeline_path = placeholder; test_framework broadened; evidence corrected; closeout date plain).

Checkbox states: `[ ]` pending | `[~]` in progress | `[x]` completed. `plan.md` is the authoritative source of truth.
Phase convention (must match Stage 1 exactly): `Phase 0 Setup & Preconditions` | `Phase 1+ Implementation` | `Final Phase Validation & Handover`.

## Phase 0 - Setup & Preconditions

- [ ] **0.1 Back up all FIVE target files**
  ```powershell
  $ts = Get-Date -Format yyyyMMdd-HHmmss
  foreach ($f in @(
    'C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-metadata.template.json',
    'C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md',
    'C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md',
    'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md',
    'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md'
  )) { Copy-Item -LiteralPath $f -Destination "$f.bak-$ts" }
  ```
  **Authoritative acceptance check:** all five `*.bak-<ts>` files exist (`Test-Path` True for each).
  **Error recovery:** if any source is missing, stop and re-verify the path before proceeding.

- [ ] **0.2 Confirm current state & no concurrent edit of target files**
  Re-read the five files; confirm anchors unchanged. Expected (verified 2026-07-06 14:40): metadata template mtime ~2026-01-17, NO `track_type`; plan template `Phase 1 - Setup`; conductor SKILL.md line 69 = `both updated and agree`, NO `pipeline_mode`; stage-prompts Stage 1 line 74 ends `Final Phase Validation & Handover`; conductor-pipeline SKILL.md mtime 2026-07-06 13:07.
  **Authoritative acceptance check:** none of the target files contain my new strings yet (`track_type` absent from metadata template; `when the repo maintains` absent from conductor SKILL.md) AND none was modified after 13:07 today (no concurrent collision).
  **Diagnostic checks:** `Select-String '"type": "feature' track-metadata.template.json`; `Select-String 'Phase 1 - Setup' track-plan.template.md`; `Select-String 'both updated and agree' conductor\SKILL.md`.

## Phase 1 - Implementation

- [ ] **1.1 (WI-1) Add the 7 pipeline fields to `track-metadata.template.json`**
  Insert immediately AFTER the `"type"` line, BEFORE `"tags"` (group classification fields; preserve all existing camelCase fields):
  ```json
    "track_type": "code|bookkeeping",
    "test_framework": "none|n/a|bun:test|vitest|jest|pytest|go|<framework>",
    "test_command": "n/a | <exact test command, e.g. bun test, vitest run>",
    "pipeline_mode": "full|standard|bookkeeping|emergency",
    "pipeline_path": "<selected path, e.g. 1 -> 5 -> 7 -> 9 for bookkeeping>",
    "pipeline_rationale": "Why this mode/path was selected (risk, scope, test coverage)",
    "skipped_stages": [],
  ```
  `pipeline_path` is a PLACEHOLDER/example - do NOT hardcode a bookkeeping path (peer fix: future full/standard/emergency tracks must not inherit an incorrect path). Keep `"type"` as-is (work category) - it is NOT replaced by `track_type`.
  **Authoritative acceptance check:** `Get-Content -Raw track-metadata.template.json | ConvertFrom-Json` succeeds AND the property set contains all of `track_type, test_framework, test_command, pipeline_mode, pipeline_path, pipeline_rationale, skipped_stages` AND the `pipeline_path` value contains a placeholder marker (`<` ... `>`), not a bare `1 -> 5 -> 7 -> 9`.
  **Diagnostic checks:** `Select-String '"track_type"','"pipeline_mode"','"skipped_stages"'` returns 3 matches.
  **Error recovery:** if JSON fails to parse after edit, restore from the 0.1 backup and re-apply via full-file rewrite.

- [ ] **1.2 (WI-5) Update `track-plan.template.md`: renumber phases + add pipeline-consistency check**
  Renumber to match Stage 1 exactly:
  - `Phase 1 - Setup` -> `Phase 0 - Setup & Preconditions`
  - `Phase 2 - Implementation` -> `Phase 1 - Implementation`
  - `Phase 3 - Verification` -> `Phase 2 - Verification`
  - `Phase 4 - Completion Validation` -> `Final Phase - Validation & Handover`
  Add ONE checkbox to the Final Phase block (alongside existing metadata/tracks.md checks):
  ```markdown
  - [ ] Verify `metadata.json` `pipeline_mode`/`pipeline_path`/`skipped_stages` match the executed pipeline path
  ```
  Keep the 3-state checkbox definitions + Task Safety Rules + Task Authoring Standards sections.
  **Authoritative acceptance check:** `Select-String 'Phase 0 - Setup','Final Phase - Validation & Handover','pipeline_mode' track-plan.template.md` all match AND `Select-String 'Phase 1 - Setup'` returns NONE.
  **Error recovery:** if both old and new phase headings coexist, restore backup and reapply via full rewrite.

- [ ] **1.3 (WI-2 + WI-3c) Update Stage 1 prompt in `stage-prompts.md`**
  Target ONLY the `## Stage 1 - Plan Creation (conductor-plan-creator)` section (line 40). Add a "Conductor Skill Hygiene" directive instructing the plan-creator to:
  - load the `conductor` skill and follow its templates (`track-spec`, `track-plan`, `track-metadata`) + Completion Hygiene + 5-point Completion Gate;
  - author ledger tasks using the **Upsert row** wording convention (never "Add row");
  - register the track in `tracks.md` and, when the repo maintains one, `tracks-ledger.md`;
  - use track-ID convention `YYYYMMDD-slug`;
  - recognise three checkbox states `[ ]` / `[~]` / `[x]`;
  - use phase convention `Phase 0 Setup & Preconditions -> Phase 1+ Implementation -> Final Phase Validation & Handover` (already stated at line 74 - cross-reference, do not contradict).
  Propagates hygiene by reference (single source of truth = the `conductor` skill) rather than duplication.
  **Authoritative acceptance check:** within the Stage 1 section, `Select-String 'load the .conductor. skill','Upsert row','YYYYMMDD-slug' stage-prompts.md` each return >=1 match.
  **Error recovery:** if the Stage 1 heading anchor moved, re-read the file to relocate it before editing.

- [ ] **1.4 (WI-3a + WI-4) Update `conductor\SKILL.md`**
  (a) **Ledger wording** - replace line 69 exactly:
  - FROM: `5. **ledgers**: `tracks.md` and `tracks-ledger.md` both updated and agree on status/date`
  - TO:   `5. **ledgers**: `tracks.md` updated AND, when the repo maintains one, `tracks-ledger.md` updated and they agree on status/date`
  (b) **Pipeline-awareness** - add a note (near the Completion Gate) that pipeline-created tracks may carry `pipeline_mode`, `pipeline_path`, `skipped_stages`; the gate should confirm those match the executed path WHEN PRESENT (manual/bare-conductor tracks without them are not penalised).
  (c) **Glossary** - one-liner: `type` = work category; `track_type` = TDD routing (`code`/`bookkeeping`). Plus a cross-reference line to `conductor-pipeline` (conductor = templates/hygiene; conductor-pipeline = staged execution).
  **Authoritative acceptance check:** `Select-String 'pipeline_mode','when the repo maintains' conductor\SKILL.md` both match AND `Select-String 'both updated and agree'` returns NONE.
  **Error recovery:** if the line-69 anchor differs, re-read SKILL.md, locate the current gate wording, edit that exact text.

- [ ] **1.5 (WI-6) Add conductor-pipeline-side cross-reference in `conductor-pipeline\SKILL.md`**
  Add a one-line cross-reference pointing back to the `conductor` skill as the source of templates/hygiene. (Reverse direction was added in 1.4.) This file is now covered by the 0.1 backup.
  **Authoritative acceptance check:** `Select-String 'conductor. skill' conductor-pipeline\SKILL.md` returns a match referencing templates/hygiene.

## Final Phase - Validation & Handover

- [ ] **V.1 Dry-run the Terminal closeout gate against the updated template**
  Materialise a throwaway metadata instance from the updated template (fill bookkeeping values), then dry-run the Stage 7/8 Terminal closeout gate checks, including `pipeline_mode`/`pipeline_path` semantic consistency.
  **Authoritative acceptance check:** synthetic metadata passes the gate (fields present AND mode/path internally consistent). No FAIL.
  **Diagnostic checks:** `Get-Content -Raw <synthetic> | ConvertFrom-Json` parses.

- [ ] **V.2a Literal check - metadata template compliance + mode/path semantics**
  **Authoritative acceptance check:** the 7 field names appear in `track-metadata.template.json`, JSON parses, `pipeline_path` is a placeholder, and a bookkeeping-filled instance shows `pipeline_mode: bookkeeping` consistent with path `1 -> 5 -> 7 -> 9` (a full-mode instance would NOT use that path).

- [ ] **V.2b Literal check - cross-skill consistency**
  **Authoritative acceptance check:** `conductor\SKILL.md` and `stage-prompts.md` share ledger wording ("when the repo maintains") and the exact phase phrase (`Phase 0` ... `Final Phase Validation & Handover`); neither contains the stale `Phase 1 - Setup` template wording nor `both updated and agree`.

- [ ] **V.3 Closeout ledger sync (Upsert rows)**
  Upsert this track's row in `tracks.md` (status `completed`, completed `2026-07-06` - plain date, no fraction) and its entry in `tracks-ledger.md`. Update `metadata.json` progress to 100% / status `completed` / stage `9-closed`.
  **Authoritative acceptance check:** both ledgers agree on status/date for this track ID (exactly one row each); metadata `progress.percentage` == 100.
  **Error recovery:** if a duplicate row exists, update in place - never add a second row.

- [ ] **V.4 Restart notice + concurrent-session note**
  Tell the user to fully restart OpenCode before testing `/conductor-pipeline` (config not hot-reloaded). Note that a parallel session edited unrelated tracks on 2026-07-06; confirm no target-file collision occurred.
  **Authoritative acceptance check:** closeout summary states the restart requirement.

## Notes

- **Edit safety:** tasks 1.1-1.5 each touch a single distinct file -> low collision risk. Use targeted `oldString` edits; full-file rewrite only if a targeted edit matches multiple locations.
- **Idempotency:** ledger updates are upserts (update in place), never append-a-duplicate.
- **No production code** is touched by any task.
