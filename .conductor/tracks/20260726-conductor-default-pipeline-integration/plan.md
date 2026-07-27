# Plan

`plan.md` is the authoritative source of truth for execution progress.

## Outcome, Constraints, and Definition of Done

### Goal / outcome

The `conductor` skill becomes the stable entry point for Conductor work and automatically imports the risk-adjusted `conductor-pipeline` contract, including mandatory baseline evidence and independent plan review.

### Constraints / non-goals

- Preserve existing pipeline risk routing, stop rules, closeout gates, and human-authority boundaries.
- Do not alter model/provider configuration, publish shared skills, or disturb unrelated dirty files.
- Back up every unversioned global skill target before editing it.

### Definition of done

The two skills and their canonical references agree that all plan creation follows `0 -> 1 -> 2`, all execution requires baseline evidence, Stage 2 uses a reviewer independent of the creator, later stages are risk-adjusted, structural and offline functional tests pass, and Conductor artifacts are synchronized.

## Phase 0: Setup & Preconditions

Objective: Establish a verified pre-edit state and protect all global skill files.

1. - [x] 0.1 Capture the pre-edit structural baseline for both skills.
   - Files: `.conductor/tracks/20260726-conductor-default-pipeline-integration/baseline-report-2026-07-26.md`
   - Prerequisites: None.
   - Command:
     ```powershell
     & 'C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1' -SkillPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor' -PrintFunctionalPrompt
     & 'C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1' -SkillPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline' -PrintFunctionalPrompt
     ```
   - Body requirements: Record both exit codes, both `RESULT:` values, and the policy gaps observed before editing.
   - Authoritative acceptance check: `(Get-Content -Raw -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration/baseline-report-2026-07-26.md').Contains('CONDUCTOR_RESULT: PASS') -and (Get-Content -Raw -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration/baseline-report-2026-07-26.md').Contains('PIPELINE_RESULT: PASS')`; expected output: `True`.
   - Diagnostic checks: Re-run either harness if its captured result is unclear.
   - Error recovery: Stop if either harness fails; preserve the output and do not edit the skill until the failure is characterized.

2. - [x] 0.2 Obtain an independent review of this plan.
   - Files: `.conductor/tracks/20260726-conductor-default-pipeline-integration/review-report-<timestamp>.md`
   - Prerequisites: `0.1`.
   - Command:
     ```text
     Dispatch a reviewer agent distinct from the plan creator using the canonical Stage 2 prompt.
     ```
   - Body requirements: The report must rate every task, dry-run every reviewer-added or modified verification command, record reviewer agent identity and model separately from the creator, give a readiness verdict, and create both `review-report-<timestamp>.md` and `review-diff-summary-<timestamp>.md`. Update metadata with non-empty `plan_reviewer` and `plan_reviewer_model` values that differ from `plan_creator` and `plan_creator_model`.
   - Authoritative acceptance check: `$m=Get-Content -Raw -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration/metadata.json' | ConvertFrom-Json; $r=Get-ChildItem -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration' -Filter 'review-report-*.md'; $d=Get-ChildItem -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration' -Filter 'review-diff-summary-*.md'; ($r.Count -ge 1) -and ($d.Count -ge 1) -and -not [string]::IsNullOrWhiteSpace($m.plan_reviewer) -and -not [string]::IsNullOrWhiteSpace($m.plan_reviewer_model) -and -not [string]::IsNullOrWhiteSpace($m.plan_creator_model) -and ($m.plan_creator_model -ne 'not recorded') -and ($m.plan_reviewer -ne $m.plan_creator) -and ($m.plan_reviewer_model -ne $m.plan_creator_model)`; expected output: `True`.
   - Diagnostic checks: Inspect the latest report for `Ready`, `Needs work`, and `Blocking` ratings.
   - Error recovery: Do not edit global skill files until all Blocking findings are resolved.

3. - [x] 0.3 Back up every global skill target before editing.
   - Files: `.conductor/tracks/20260726-conductor-default-pipeline-integration/backups/2026-07-26-pre-edit/*`, `.conductor/tracks/20260726-conductor-default-pipeline-integration/backup-dir.txt`, `.conductor/tracks/20260726-conductor-default-pipeline-integration/backup-manifest-2026-07-26.json`
   - Prerequisites: `0.2`.
   - Command:
     ```powershell
      $targets=@(
        @{target='C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md';name='conductor__SKILL.md.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md';name='conductor-pipeline__SKILL.md.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md';name='conductor-pipeline__stage-prompts.md.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md';name='conductor-pipeline__threshold-policy.md.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md';name='conductor__track-plan.template.md.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-metadata.template.json';name='conductor__track-metadata.template.json.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md';name='conductor-pipeline__README.md.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md';name='commands__conductor-pipeline.md.pre-edit.bak'},
        @{target='C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md';name='agent__conductor-pipeline-orchestrator.md.pre-edit.bak'}
      )
      $backupDir='C:\development\opencode\.conductor\tracks\20260726-conductor-default-pipeline-integration\backups\2026-07-26-pre-edit'
      New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
      $manifest=foreach($item in $targets){
        $backup=Join-Path $backupDir $item.name
        Copy-Item -LiteralPath $item.target -Destination $backup -Force
        [pscustomobject]@{target=$item.target;backup=$backup;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $backup).Hash}
      }
      $manifest | ConvertTo-Json | Set-Content -LiteralPath 'C:\development\opencode\.conductor\tracks\20260726-conductor-default-pipeline-integration\backup-manifest-2026-07-26.json' -Encoding utf8
      $backupDir | Set-Content -LiteralPath 'C:\development\opencode\.conductor\tracks\20260726-conductor-default-pipeline-integration\backup-dir.txt' -Encoding utf8
     ```
   - Body requirements: Back up all nine global targets using a filename ending in `.pre-edit.bak`, record the fully qualified backup directory, and write a JSON manifest with each target, backup path, and SHA256. Do not use the backups as an edit target.
   - Authoritative acceptance check: `$manifest=Get-Content -Raw -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration/backup-manifest-2026-07-26.json' | ConvertFrom-Json; ($manifest.Count -eq 9) -and (($manifest | Where-Object { -not (Test-Path -LiteralPath $_.backup) -or $_.sha256 -ne (Get-FileHash -Algorithm SHA256 -LiteralPath $_.backup).Hash }).Count -eq 0)`; expected output: `True`.
   - Diagnostic checks: Compare each backup length with its source before editing.
   - Error recovery: Stop on any missing or mismatched backup.

Phase exit criteria: Baseline is recorded, the plan is independently reviewed with no unresolved blockers, and all nine edit targets have verified backups.

## Phase 1: Implementation

Objective: Make composition, baseline, review independence, and model flexibility consistent across the skills and templates.

1. - [x] 1.1 Add the mandatory composition contract to `conductor`.
   - Files: `C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md`
   - Prerequisites: `0.3`.
   - Command:
     ```text
     Use apply_patch to add a new `## Mandatory Pipeline Composition` section immediately before `## Completion Hygiene (Required)`.
     ```
   - Body requirements: The new section must explicitly require `conductor-pipeline` to load whenever `conductor` is invoked; require `Stage 0 (Baseline) -> Stage 1 (Plan Creation) -> Stage 2 (Independent Plan Review)` for every new or updated plan; prohibit Stage 0 and Stage 2 waivers; require plan-only requests to stop after the Stage 2 review artifacts exist; and retain risk-adjusted routing only after review.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md'; @('## Mandatory Pipeline Composition','conductor-pipeline','Stage 0 (Baseline) -> Stage 1 (Plan Creation) -> Stage 2 (Independent Plan Review)','Stage 0 and Stage 2 are non-waivable','Plan-only requests stop after Stage 2','risk-adjusted') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Search for contradictory language permitting plan-review skips.
   - Error recovery: Restore from the pre-edit backup if frontmatter or reference resolution breaks.

2. - [x] 1.2 Update the pipeline orchestration contract and mode paths.
   - Files: `C:/Users/DaveWitkin/.config/opencode/skill/conductor-pipeline/SKILL.md`
   - Prerequisites: `1.1`.
   - Command:
     ```text
     Use apply_patch with content anchors to update Pipeline Determination, all four mode paths, stage flow, and model-assignment policy in this file only.
     ```
   - Body requirements: Define non-waivable Stage 0 baseline before Stage 1; require Stage 2 for every newly created or updated plan, including existing-plan updates; state that plan-only requests stop after Stage 2; make each non-emergency mode path begin `0 -> 1 -> 2`; retain conditional Stage 3/8 and risk-adjusted stages 4/4b/6; and state that model assignments are defaults and any substitute must preserve creator/reviewer and executor/validator independence.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md'; @('Stage 0 Baseline','Plan review is mandatory','Plan-only requests stop after Stage 2','model assignments are defaults','0 -> 1 -> 2') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Search mode tables and stage-flow prose for paths lacking `0 -> 1 -> 2`.
   - Error recovery: Restore the backup and split the edit into smaller anchors if any target text is ambiguous.

3. - [x] 1.3 Update the active pipeline command so it cannot bypass the mandatory gates.
   - Files: `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`
   - Prerequisites: `1.2`.
   - Command:
     ```text
     Use apply_patch with content anchors to update Pipeline modes and Stage catalog/routing rules in this command file only.
     ```
   - Body requirements: The command must invoke Stage 0 before Stage 1, invoke Stage 2 after every new or updated plan, prohibit low-risk bookkeeping review skips, stop plan-only requests after Stage 2 artifacts, retain risk-adjusted later stages, and permit model substitution only when creator/reviewer and executor/validator independence remains true.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md'; @('Stage 0','Stage 2','mandatory','Plan-only','independence','0 -> 1 -> 2') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Search this command for `Skip by default for low-risk` and `5 -> 7 -> 9`; both must have zero matches.
   - Error recovery: Restore this command only from its pre-edit backup if its YAML frontmatter or orchestration instructions become malformed.

4. - [x] 1.4 Update the active orchestrator so it enforces the mandatory gates.
   - Files: `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`
   - Prerequisites: `1.3`.
   - Command:
     ```text
     Use apply_patch with content anchors to update the numbered run sequence, pipeline-mode table, Stage 2 routing, and substitute-model rule in this agent file only.
     ```
   - Body requirements: The orchestrator must run Stage 0 adaptive baseline first, require usable baseline evidence before Stage 1 or any deliverable edit, require Stage 2 for every new or updated plan, stop plan-only requests after review, keep only later stages risk-adjusted, and select replacement models only when distinct creator/reviewer and executor/validator identities remain. It must remove all bookkeeping paths that skip Stage 2.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md'; @('Stage 0','baseline evidence','Stage 2','Plan-only','substitute','independence','0 -> 1 -> 2') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Search this agent for `Skip Stage 2`, `Skip for low-risk bookkeeping`, and `5 -> 7 -> 9`; all must have zero matches.
   - Error recovery: Restore this agent only from its pre-edit backup if frontmatter, permissions, or stage routing becomes malformed.

5. - [x] 1.5 Add the canonical baseline prompt and strengthen independent review wording.
   - Files: `C:/Users/DaveWitkin/.config/opencode/skill/conductor-pipeline/references/stage-prompts.md`
   - Prerequisites: `1.4`.
   - Command:
     ```text
     Insert Stage 0 before Stage 1 and amend Stage 1/2 prompt requirements.
     ```
   - Body requirements: Define adaptive baseline commands and PASS/KNOWN-RED/BLOCKED outcomes; require baseline evidence as plan input; require reviewer identity different from creator; require review report before a plan is execution-ready.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'; @('## Stage 0 - Baseline','PASS','KNOWN-RED','BLOCKED','baseline evidence','reviewer identity must differ from the plan creator','execution-ready') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Verify the Stage 1 prompt references the baseline artifact and Stage 2 blocks on missing baseline evidence.
   - Error recovery: Restore the backup if Markdown fences become unbalanced.

6. - [x] 1.6 Align threshold policy with non-waivable baseline and review gates.
   - Files: `C:/Users/DaveWitkin/.config/opencode/skill/conductor-pipeline/references/threshold-policy.md`
   - Prerequisites: `1.5`.
   - Command:
     ```text
     Update mode paths, skip policy, diversity rule, and failure paths.
     ```
   - Body requirements: No mode may skip Stage 0; no new/updated plan may skip Stage 2; Stage 3 remains conditional; missing/unusable baseline blocks execution; creator/reviewer independence is role-based, not tied to a fixed model ID.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md'; @('Stage 0 and Stage 2 are mandatory','missing/unusable baseline','creator/reviewer independence','role-based') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Search for `Stage 2 was skipped` and resolve remaining contradictions.
   - Error recovery: Restore the backup if policy paths and SKILL.md paths cannot be reconciled exactly.

7. - [x] 1.7 Add mandatory baseline and independent-review tasks to the plan template.
   - Files: `C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md`
   - Prerequisites: `1.6`.
   - Command:
     ```text
     Use apply_patch to add a mandatory Stage 0 baseline task and a mandatory Stage 2 independent-review gate to the Phase 0 template.
     ```
   - Body requirements: The template must contain `Mandatory Baseline`, `Independent Plan Review`, a plan-only stop condition after review, and a requirement that the reviewer agent/model differ from the creator.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md'; @('Mandatory Baseline','Independent Plan Review','plan-only','differ from the creator') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Verify the new template tasks retain the one-authoritative-check rule.
   - Error recovery: Restore this target only from its pre-edit backup and reapply a smaller edit.

8. - [x] 1.8 Add baseline and creator/reviewer identity fields to the metadata template.
   - Files: `C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-metadata.template.json`
   - Prerequisites: `1.7`.
   - Command:
     ```text
     Use apply_patch to add valid JSON fields for baseline status/evidence and creator/reviewer identity/model, and update the bookkeeping path example.
     ```
   - Body requirements: The valid JSON template must include `baseline_status`, `baseline_evidence`, `plan_creator`, `plan_creator_model`, `plan_reviewer`, and `plan_reviewer_model`; use an allowed `pipeline_mode` value; and show a bookkeeping path that begins `0 -> 1 -> 2`.
   - Authoritative acceptance check: `$m=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-metadata.template.json' | ConvertFrom-Json; @('baseline_status','baseline_evidence','plan_creator','plan_creator_model','plan_reviewer','plan_reviewer_model') | ForEach-Object {$null -ne $m.$_} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Confirm `$m.pipeline_mode -in @('full','standard','bookkeeping','emergency')` and `$m.pipeline_path.Contains('0 -> 1 -> 2')` both return `True`.
   - Error recovery: Restore this target only from its pre-edit backup if JSON parsing fails.

9. - [x] 1.9 Align the pipeline README with automatic composition and mandatory early gates.
   - Files: `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`
   - Prerequisites: `1.8`.
   - Command:
     ```text
     Use apply_patch with content anchors to update Invocation, Pipeline modes, Stage catalog, and Model diversity in this README only.
     ```
   - Body requirements: State that `conductor` automatically composes this pipeline, every plan follows `0 -> 1 -> 2`, plan-only requests stop after review, only later stages are risk-adjusted, and model substitutions must preserve creator/reviewer and executor/validator independence.
   - Authoritative acceptance check: `$s=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md'; @('automatically composes','0 -> 1 -> 2','Plan-only','risk-adjusted','independence') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count`; expected output: `0`.
   - Diagnostic checks: Search the README for legacy bookkeeping paths that omit Stage 0 or Stage 2.
   - Error recovery: Restore this target only from its pre-edit backup if Markdown tables become malformed.

10. - [x] 1.10 Enforce a capable-model floor for every pipeline phase.
   - Files: `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`, `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`, `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`
   - Prerequisites: `1.9`.
   - Command:
     ```text
     Add a centralized capability-floor gate and require every stage handoff to record and validate its selected model before dispatch.
     ```
   - Body requirements: In every listed active policy surface, add a `Capability floor` rule that names the currently configured capable defaults as the approved baseline; prohibits `gpt-5.4-mini`, model IDs containing `-mini` or `-nano`, and economy/low-capability substitutions; requires a capability-equivalent or stronger substitute; preserves creator/reviewer and executor/validator independence; and stops when no capable independent route exists. In `stage-prompts.md`, additionally require every stage handoff to record and validate the selected model against that floor before dispatch.
   - Authoritative acceptance check: `$files=@('C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md','C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md','C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md'); $terms=@('Capability floor','gpt-5.4-mini','-mini','-nano','economy','capability-equivalent','independence','no capable independent route'); $missing=foreach($file in $files){$s=Get-Content -Raw -LiteralPath $file; foreach($term in $terms){if(-not $s.Contains($term)){"$file :: $term"}}}; $stage=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md'; $agents=Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\agent' -Filter 'conductor-*.md' -File | Where-Object {$_.Name -notmatch '\.(bak|backup|routing|pre-write)'}; $badAgents=foreach($agent in $agents){$model=(Get-Content -LiteralPath $agent.FullName | Where-Object {$_ -match '^model:'} | Select-Object -First 1); if($model -match '(?i)gpt-5\.4-mini|[-/]mini\b|[-/]nano\b|economy'){"$($agent.FullName) :: $model"}}; ($missing.Count -eq 0) -and $stage.Contains('record and validate the selected model') -and ($badAgents.Count -eq 0)`; expected output: `True`.
   - Diagnostic checks: Enumerate every active `conductor-*.md` frontmatter `model:` value and confirm the selected models are the documented capable defaults or capability-equivalent substitutes.
   - Error recovery: If an active agent violates the floor, stop and add that agent file to the backed-up edit scope before changing it.

Phase exit criteria: All nine active entry-point, agent, skill, template, reference, and README surfaces agree on mandatory Stage 0 and Stage 2 gates, adaptive later-stage routing, flexible models with preserved independence, and a capable-model floor for every phase.

## Final Phase: Validation & Handover

Objective: Prove structural and behavioral correctness and synchronize Conductor state.

1. - [x] F.1 Run post-edit structural smoke tests for both skills.
   - Files: `.conductor/tracks/20260726-conductor-default-pipeline-integration/post-edit-smoke-report-2026-07-26.md`
   - Prerequisites: `1.10`.
   - Command:
     ```powershell
     & 'C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1' -SkillPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor' -PrintFunctionalPrompt
     & 'C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1' -SkillPath 'C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline' -PrintFunctionalPrompt
     ```
   - Body requirements: Capture both summaries and exit codes.
   - Authoritative acceptance check: `$path='.conductor/tracks/20260726-conductor-default-pipeline-integration/post-edit-smoke-report-2026-07-26.md'; if(-not (Test-Path -LiteralPath $path)){1}else{$s=Get-Content -Raw -LiteralPath $path; @('CONDUCTOR_RESULT: PASS','CONDUCTOR_EXIT: 0','PIPELINE_RESULT: PASS','PIPELINE_EXIT: 0','BOTH_RESULTS: PASS') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count}`; expected output: `0`.
   - Diagnostic checks: Compare warnings with the baseline report and explain any new warning.
   - Error recovery: Restore affected targets from backups if either harness fails.

2. - [x] F.2 Run an independent offline functional smoke test.
   - Files: `.conductor/tracks/20260726-conductor-default-pipeline-integration/functional-test-report-2026-07-26.md`
   - Prerequisites: `F.1`.
   - Command:
     ```text
     Dispatch an independent agent to simulate a representative "create a new Conductor plan" request using only the updated skills.
     ```
   - Body requirements: The independent reviewer must inspect the updated `conductor` skill, pipeline command, and orchestrator; simulate a new plan request and a plan-only request; identify the exact baseline evidence artifact, creator/reviewer identities and models, plan-review artifacts, and stop point; and confirm that selecting bookkeeping affects only later stages. The reviewer must not execute global-skill edits or deliverable work.
   - Authoritative acceptance check: `$path='.conductor/tracks/20260726-conductor-default-pipeline-integration/functional-test-report-2026-07-26.md'; if(-not (Test-Path -LiteralPath $path)){1}else{$s=Get-Content -Raw -LiteralPath $path; @('FUNCTIONAL_SMOKE_TEST_PASSED','Baseline evidence artifact:','Creator identity/model:','Reviewer identity/model:','Plan-only stop point: Stage 2','Bookkeeping later-stage path:') | ForEach-Object {$s.Contains($_)} | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count}`; expected output: `0`.
   - Diagnostic checks: Inspect the report's forbidden-actions section.
   - Error recovery: Treat any bypass path as a blocking skill defect and correct the canonical source before rerunning.

3. - [x] F.3 Run cross-file contradiction and backup comparisons.
   - Files: All nine edited targets and their backups.
   - Prerequisites: `F.2`.
   - Command:
     ```powershell
     $active=@('C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-metadata.template.json','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md','C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md','C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md'); $hits=rg -n '`1 -> 5 -> 7 -> 9`|`5 -> 7 -> 9`|Skip Stage 2|Skip by default for low-risk|Stage 2 was skipped|Plan Review: skipped|skip 2/3|Skip Stage 2/3' -- $active; $noBypass=($LASTEXITCODE -eq 1); $manifest=Get-Content -Raw -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration/backup-manifest-2026-07-26.json' | ConvertFrom-Json; $deltas=foreach($item in $manifest){git diff --no-index --numstat -- $item.backup $item.target 2>$null; if($LASTEXITCODE -gt 1){throw "Comparator failed: $($item.target)"}}; $noBypass -and ($manifest.Count -eq 9) -and ($deltas.Count -eq 9)
     ```
   - Body requirements: Prove no active entry point, orchestrator, skill, reference, template, or README permits bypassing baseline or initial plan review; capture the nine no-index comparison summaries in the execution log; and classify every changed target as intentional.
   - Authoritative acceptance check: `$active=@('C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md','C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-metadata.template.json','C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md','C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md','C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md'); rg -n '`1 -> 5 -> 7 -> 9`|`5 -> 7 -> 9`|Skip Stage 2|Skip by default for low-risk|Stage 2 was skipped|Plan Review: skipped|skip 2/3|Skip Stage 2/3' -- $active; $LASTEXITCODE -eq 1`; expected output: `True`.
   - Diagnostic checks: Review all `git diff --no-index --numstat` results.
   - Error recovery: Resolve each contradiction or explicitly classify it as historical text before closeout.

4. - [x] F.4 Synchronize the execution log, metadata, and Conductor ledgers.
   - Files: `.conductor/tracks/20260726-conductor-default-pipeline-integration/execution-log-2026-07-26.md`, `.conductor/tracks/20260726-conductor-default-pipeline-integration/metadata.json`, `.conductor/tracks.md`, `.conductor/tracks-ledger.md`
   - Prerequisites: `F.3`.
   - Command:
     ```text
     Upsert exactly one track entry in each ledger without disturbing unrelated changes.
     ```
   - Body requirements: Record changed files, baseline and final validation, review identities, model substitutions, deviations, and publication status.
   - Authoritative acceptance check: `$id='20260726-conductor-default-pipeline-integration'; $m=Get-Content -Raw -LiteralPath '.conductor/tracks/20260726-conductor-default-pipeline-integration/metadata.json' | ConvertFrom-Json; $t=@(Select-String -LiteralPath '.conductor/tracks.md' -SimpleMatch $id); $l=@(Select-String -LiteralPath '.conductor/tracks-ledger.md' -SimpleMatch $id); ($t.Count -eq 1) -and ($l.Count -eq 1) -and $t[0].Line.Contains($m.status) -and $l[0].Line.Contains($m.status)`; expected output: `True`.
   - Diagnostic checks: Compare the status/date in both ledgers with metadata.
   - Error recovery: Update existing rows in place; never append a duplicate.

Phase exit criteria: Both skill harnesses pass, independent functional validation passes, no bypass language remains, backups prove bounded edits, and Conductor artifacts agree.

## Execution Readiness Checklist

- [x] Atomic tasks: one clear action per checkbox.
- [x] Exact paths: every task names precise repo-relative or fully qualified paths.
- [x] Explicit commands: every task provides verbatim execution and verification commands.
- [x] Clear ordering: prerequisites and strict task order are explicit.
- [x] Verification per step: every task has exactly one authoritative acceptance check.
- [x] No assumed context: an unfamiliar agent can execute without extra repository exploration.
- [x] Concrete examples: format-sensitive tasks include exact expected output.
- [x] Error recovery: every task defines a safe fallback.

## Top 3 Implementation Risks + Mitigations

1. **Policy drift across four canonical surfaces** — Mitigation: cross-file contradiction search plus functional smoke test.
2. **Over-constraining low-risk bookkeeping work** — Mitigation: make only baseline and initial review mandatory; retain risk-adjusted later stages.
3. **Corrupting unversioned global skills** — Mitigation: verified per-file backups plus no-index comparisons and structural smoke tests.

## First Task to Execute Immediately

Execute task `0.3`: create and verify the nine-file pre-edit backup set before any global target is edited.

## Checkbox States

- [ ] Pending
- [~] In progress
- [x] Completed
