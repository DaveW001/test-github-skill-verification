# Skill Review Matrix

Track: `20260726-top-skills-agents-review`. One entry per selected skill (20). Every frozen rubric item is recorded in each packet under `review-batches/skills/<name>.json`; this matrix summarizes results, functional verdicts, and fix dispositions.

Functional confirmation is mostly `FUNCTIONAL_SMOKE_TEST_UNVERIFIED` by design: live functional cases require credentials, external mutation, network, or orchestration/subagent dispatch, all prohibited in this review-only track. `session-db-query` was functionally exercised read-only in Task 1.1.

| # | Skill | Conf | Harness | Functional | Fails (items) | Pass/NA/Unv |
|---|-------|------|---------|-----------|---------------|-------------|
| 1 | conductor | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED | 30/11/1 |
| 2 | doc | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED | 31/9/2 |
| 3 | clickup | low | FAIL | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_01_ENTRYPOINT_SIZE, STRUCT_03_ONE_LEVEL_REFERENCES, TROUBLE_04_REFERENCE_EXISTENCE, SCRIPT_04_SYNTAX | 35/3/1 |
| 4 | conductor-pipeline | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_01_ENTRYPOINT_SIZE, STRUCT_02_ADVANCED_DETAILS_DISCLOSED | 28/12/1 |
| 5 | git-push | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED | 31/10/1 |
| 6 | retrospective | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_01_ENTRYPOINT_SIZE, STRUCT_02_ADVANCED_DETAILS_DISCLOSED | 28/13/0 |
| 7 | skill-creator | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_03_ONE_LEVEL_REFERENCES, TROUBLE_04_REFERENCE_EXISTENCE | 31/8/2 |
| 8 | opencode-scheduler | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED, TRIG_02_SUGGEST_ONLY_TRUE | 30/10/1 |
| 9 | humanizer | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED | 27/14/1 |
| 10 | osgrep | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | DESC_01_WHAT_WHEN_KEYWORDS, STRUCT_02_ADVANCED_DETAILS_DISCLOSED, TRIG_02_SUGGEST_ONLY_TRUE | 27/12/1 |
| 11 | diagram-svg | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | — | 38/4/1 |
| 12 | pptx-from-layouts | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_01_ENTRYPOINT_SIZE, STRUCT_02_ADVANCED_DETAILS_DISCLOSED, TEST_01_ACTIVATION, SCOPE_02_REALISTIC_TRIGGERS | 31/7/1 |
| 13 | pre-delivery-ai-review | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_01_ENTRYPOINT_SIZE, GUARD_03_CONCISE_ACTIONABLE_EXAMPLES | 37/3/1 |
| 14 | image-ocr | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | DESC_02_LENGTH, STRUCT_02_ADVANCED_DETAILS_DISCLOSED, TEST_01_ACTIVATION, SCOPE_02_REALISTIC_TRIGGERS | 29/8/2 |
| 15 | enrich-meeting-notes | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED, TEST_01_ACTIVATION, SCOPE_02_REALISTIC_TRIGGERS | 23/16/1 |
| 16 | opencode-event-log-compactor | low | FAIL | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | DESC_02_LENGTH, STRUCT_01_ENTRYPOINT_SIZE, STRUCT_02_ADVANCED_DETAILS_DISCLOSED, SCRIPT_04_SYNTAX | 32/6/1 |
| 17 | opencode-go-key-rotation | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | TEST_01_ACTIVATION, SCOPE_02_REALISTIC_TRIGGERS | 30/11/0 |
| 18 | root-cause-analysis | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED, GUARD_03_CONCISE_ACTIONABLE_EXAMPLES | 28/12/1 |
| 19 | scheduled-job-best-practices | low | PASS | FUNCTIONAL_SMOKE_TEST_UNVERIFIED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED | 26/15/1 |
| 20 | session-db-query | low | PASS | FUNCTIONAL_SMOKE_TEST_PASSED | STRUCT_02_ADVANCED_DETAILS_DISCLOSED, GUARD_03_CONCISE_ACTIONABLE_EXAMPLES | 30/9/2 |

## Queued skill fixes (Major)

- **FIX-SKILL-001-clickup-SCRIPT_04_SYNTAX** — `clickup` item `SCRIPT_04_SYNTAX`: skill script(s) fail the authoritative skill-test-harness SCRIPT SYNTAX check — failing script(s) corrected to pass harness SCRIPT SYNTAX without changing capability or authority
- **FIX-SKILL-002-opencode-event-log-compactor-SCRIPT_04_SYNTAX** — `opencode-event-log-compactor` item `SCRIPT_04_SYNTAX`: skill script(s) fail the authoritative skill-test-harness SCRIPT SYNTAX check — failing script(s) corrected to pass harness SCRIPT SYNTAX without changing capability or authority

## No-fix dispositions (Minor heuristic findings)

Each Minor heuristic finding is recorded here with an explicit reason; it is NOT auto-fixed. These remain Optional/Dave-decision and are not concealed.

- `conductor` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `doc` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `clickup` `STRUCT_01_ENTRYPOINT_SIZE` (Minor): conciseness bound is a heuristic; the skill is an established large reference entrypoint -- refactoring is a content decision for Dave, not an in-scope safe fix
- `clickup` `STRUCT_03_ONE_LEVEL_REFERENCES` (Minor): broken internal reference detected; needs case-by-case validation -- recorded as Optional for Dave decision
- `clickup` `TROUBLE_04_REFERENCE_EXISTENCE` (Minor): reference existence flag mirrors STRUCT_03; same Optional disposition
- `conductor-pipeline` `STRUCT_01_ENTRYPOINT_SIZE` (Minor): conciseness bound is a heuristic; the skill is an established large reference entrypoint -- refactoring is a content decision for Dave, not an in-scope safe fix
- `conductor-pipeline` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `git-push` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `retrospective` `STRUCT_01_ENTRYPOINT_SIZE` (Minor): conciseness bound is a heuristic; the skill is an established large reference entrypoint -- refactoring is a content decision for Dave, not an in-scope safe fix
- `retrospective` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `skill-creator` `STRUCT_03_ONE_LEVEL_REFERENCES` (Minor): broken internal reference detected; needs case-by-case validation -- recorded as Optional for Dave decision
- `skill-creator` `TROUBLE_04_REFERENCE_EXISTENCE` (Minor): reference existence flag mirrors STRUCT_03; same Optional disposition
- `opencode-scheduler` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `opencode-scheduler` `TRIG_02_SUGGEST_ONLY_TRUE` (Minor): triggers.suggest_only not true; changing trigger behavior is an authority/behavior decision for Dave
- `humanizer` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `osgrep` `DESC_01_WHAT_WHEN_KEYWORDS` (Minor): description keyword heuristic; content wording decision for Dave
- `osgrep` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `osgrep` `TRIG_02_SUGGEST_ONLY_TRUE` (Minor): triggers.suggest_only not true; changing trigger behavior is an authority/behavior decision for Dave
- `pptx-from-layouts` `STRUCT_01_ENTRYPOINT_SIZE` (Minor): conciseness bound is a heuristic; the skill is an established large reference entrypoint -- refactoring is a content decision for Dave, not an in-scope safe fix
- `pptx-from-layouts` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `pptx-from-layouts` `TEST_01_ACTIVATION` (Minor): no explicit activation section detected by heuristic; existing skills rely on description activation -- Optional
- `pptx-from-layouts` `SCOPE_02_REALISTIC_TRIGGERS` (Minor): trigger-signal heuristic; existing skills activate via description -- Optional
- `pre-delivery-ai-review` `STRUCT_01_ENTRYPOINT_SIZE` (Minor): conciseness bound is a heuristic; the skill is an established large reference entrypoint -- refactoring is a content decision for Dave, not an in-scope safe fix
- `pre-delivery-ai-review` `GUARD_03_CONCISE_ACTIONABLE_EXAMPLES` (Minor): no examples detected by heuristic; adding examples is a content improvement -- Optional
- `image-ocr` `DESC_02_LENGTH` (Minor): description length slightly outside heuristic bounds; editing the activation description affects skill discovery -- Dave decision
- `image-ocr` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `image-ocr` `TEST_01_ACTIVATION` (Minor): no explicit activation section detected by heuristic; existing skills rely on description activation -- Optional
- `image-ocr` `SCOPE_02_REALISTIC_TRIGGERS` (Minor): trigger-signal heuristic; existing skills activate via description -- Optional
- `enrich-meeting-notes` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `enrich-meeting-notes` `TEST_01_ACTIVATION` (Minor): no explicit activation section detected by heuristic; existing skills rely on description activation -- Optional
- `enrich-meeting-notes` `SCOPE_02_REALISTIC_TRIGGERS` (Minor): trigger-signal heuristic; existing skills activate via description -- Optional
- `opencode-event-log-compactor` `DESC_02_LENGTH` (Minor): description length slightly outside heuristic bounds; editing the activation description affects skill discovery -- Dave decision
- `opencode-event-log-compactor` `STRUCT_01_ENTRYPOINT_SIZE` (Minor): conciseness bound is a heuristic; the skill is an established large reference entrypoint -- refactoring is a content decision for Dave, not an in-scope safe fix
- `opencode-event-log-compactor` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `opencode-go-key-rotation` `TEST_01_ACTIVATION` (Minor): no explicit activation section detected by heuristic; existing skills rely on description activation -- Optional
- `opencode-go-key-rotation` `SCOPE_02_REALISTIC_TRIGGERS` (Minor): trigger-signal heuristic; existing skills activate via description -- Optional
- `root-cause-analysis` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `root-cause-analysis` `GUARD_03_CONCISE_ACTIONABLE_EXAMPLES` (Minor): no examples detected by heuristic; adding examples is a content improvement -- Optional
- `scheduled-job-best-practices` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `session-db-query` `STRUCT_02_ADVANCED_DETAILS_DISCLOSED` (Minor): no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect
- `session-db-query` `GUARD_03_CONCISE_ACTIONABLE_EXAMPLES` (Minor): no examples detected by heuristic; adding examples is a content improvement -- Optional