# Plan

`plan.md` is the authoritative source of truth for execution progress.

## Outcome, Constraints, and Definition of Done

### Goal / outcome

Create a maintainable, cross-harness instruction architecture in which shared rules live once under the OpenCode user-level folder, Codex and OpenCode retain thin adapters, specialized material is progressively disclosed, project `AGENTS.md` files remain concise and local, and the user-level OpenCode `.env` remains the central commented source of truth.

### Constraints / non-goals

- Preserve `C:\Users\DaveWitkin\.config\opencode\.env` as the central source of truth. It is verify-only in this track: do not print, compare, rewrite, rotate, or delete any value. The approved existing variable for the one affected property is `SLACK_USER_TOKEN`.
- The only authentication-bearing configuration migration is `mcp.slack.environment.SLACK_MCP_XOXP_TOKEN` in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` from its literal value to OpenCode's `{env:SLACK_USER_TOKEN}` reference. Do not inspect or record the old value.
- Back up every pre-existing modified file before editing. Record created files as `created-no-preimage`; rollback removes only those created paths.
- Do not commit or push the OpenCode repository. Do not publish, send external communications, restart applications, or change application source.
- Preserve unrelated dirty-worktree changes and record before/after status for repository-scoped edits.

### Definition of done

- All 15 tracked tasks are checked off, or any exception is explicitly deferred in the final handoff.
- Global and project instruction files are reduced or routed without losing required behavior.
- Agent-writer templates and references are current and internally consistent.
- The affected credential field uses `{env:SLACK_USER_TOKEN}` and `.env` remains unchanged.
- Deterministic validation, backup, rollback, execution, and Conductor closeout artifacts agree.

## Closed Target and Ownership Table

This table is closed. No path outside it may be modified or created by the track without a documented plan amendment and a new review.

| ID | Absolute path | Operation | Owner | Rollback action |
|---|---|---|---|---|
| M01 | `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` | modify | OpenCode adapter | restore backup |
| M02 | `C:\Users\DaveWitkin\.codex\AGENTS.md` | modify | Codex adapter | restore backup |
| M03 | `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` | modify | OpenCode config | restore backup |
| M04 | `C:\Users\DaveWitkin\.config\opencode\.env` | verify-only | user central env | no mutation permitted |
| M05 | `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc` | verify-only | secret metadata | no mutation permitted |
| M06 | `C:\Users\DaveWitkin\.opencode-lazy-vault\agent-writer\SKILL.md` | modify | agent-writer skill | restore backup |
| M07 | `C:\Users\DaveWitkin\.opencode-lazy-vault\agent-writer\references\agent-templates.md` | modify | agent-writer skill | restore backup |
| M08 | `C:\Users\DaveWitkin\.opencode-lazy-vault\agent-writer\references\validation.md` | modify | agent-writer skill | restore backup |
| M09 | `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md` | modify | OpenCode standards | restore backup |
| M10 | `C:\Users\DaveWitkin\.config\opencode\command-development-standards.md` | modify | OpenCode standards | restore backup |
| M11 | `C:\Users\DaveWitkin\.config\opencode\opencode-standards-reference.md` | modify | OpenCode standards index | restore backup |
| M12 | `C:\development\chief-of-staff\AGENTS.md` | modify | project adapter | restore backup |
| M13 | `C:\development\02-Kx-to-process\AGENTS.md` | modify | project adapter | restore backup |
| M14 | `C:\development\command-center\AGENTS.md` | modify | project adapter | restore backup |
| M15 | `C:\development\marketing\AGENTS.md` | modify | project adapter | restore backup |
| C01 | `C:\Users\DaveWitkin\.config\opencode\agent-rules\common-core.md` | create | shared rules | remove created path |
| C02 | `C:\Users\DaveWitkin\.config\opencode\agent-rules\authority-boundaries.md` | create | shared rules | remove created path |
| C03 | `C:\Users\DaveWitkin\.config\opencode\agent-rules\filesystem-and-git.md` | create | shared rules | remove created path |
| C04 | `C:\Users\DaveWitkin\.config\opencode\agent-rules\research-and-evidence.md` | create | shared rules | remove created path |
| C05 | `C:\Users\DaveWitkin\.config\opencode\agent-rules\agent-authoring.md` | create | shared rules | remove created path |
| C06 | `C:\Users\DaveWitkin\.config\opencode\agent-rules\reference-index.md` | create | shared rules | remove created path |
| C07 | `C:\Users\DaveWitkin\.config\opencode\agent-rules\RULES-MANIFEST.md` | create | shared rules | remove created path |
| C08 | `C:\development\opencode\scripts\validate-agents-architecture.ps1` | create | validation | remove created path |
| C09 | `C:\development\opencode\docs\runbooks\agents-md-cross-harness.md` | create | documentation | remove created path |

## Phase 0: Setup & Preconditions

Objective: complete the baseline and independent plan-review gates before implementation.

1. - [x] 0.1 Mandatory Baseline: capture pre-change state.
   - Files: `.conductor/tracks/20260731-agents-md-cross-harness-remediation/baseline-report-2026-07-31-170000.md`
   - Authoritative acceptance check: `pwsh -NoProfile -Command "if ((Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\baseline-report-2026-07-31-170000.md') -and ((Get-Content -LiteralPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\baseline-report-2026-07-31-170000.md' -Raw) -match '(?m)^PASS$')) { exit 0 } else { exit 1 }"` exits 0.
   - Diagnostic checks: inventory global/project `AGENTS.md` files, `.env` variable names, configuration hashes, and existing Git status without values.

2. - [x] 0.2 Independent Plan Review: dispatch an independent reviewer on a different capable model.
   - Files: review report, review diff summary, `metadata.json`.
   - Prerequisites: `0.1` and the repaired Stage 1 plan.
   - Authoritative acceptance check: `pwsh -NoProfile -Command "& { $m=Get-Content -LiteralPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\metadata.json' -Raw | ConvertFrom-Json; if(($m.review_status -eq 'accepted') -and ($m.plan_reviewer) -and ($m.plan_reviewer_model) -and ($m.plan_reviewer -ne $m.plan_creator) -and ($m.plan_reviewer_model -ne $m.plan_creator_model)){ exit 0 } else { exit 1 } }"` exits 0; the report records the active metadata reviewer identity/model and proves both differ from the creator without hard-coding a prior review identity.
   - Diagnostic checks: inspect every reviewer-added command and confirm no blocker remains.

Phase exit criteria: baseline PASS; review status `accepted`; creator/reviewer identities and models differ; no blocking finding remains.

## Phase 1: Safety, Inventory, and Canonical Layout

Objective: create recoverable backups and establish the shared rule tree.

3. - [x] 1.1 Create timestamped backups and a closed-manifest record.
   - Files: `C:\Users\DaveWitkin\.config\opencode\backups\20260731-agents-md-remediation\`, `.conductor/tracks/20260731-agents-md-cross-harness-remediation/backup-manifest.json`.
   - Prerequisites: `0.2`.
   - Authoritative acceptance check: `pwsh -NoProfile -Command "if ((Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\backup-manifest.json') -and ((Get-Content -LiteralPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\backup-manifest.json' -Raw | ConvertFrom-Json).entries.Count -eq 24)) { exit 0 } else { exit 1 }"` exits 0; the 24 entries are M01–M15 plus C01–C09 with create/modify/verify-only operation labels and hashes where applicable.
   - Diagnostic checks: compare pre-edit `git status --short` snapshots for `C:\development\opencode`, `C:\development\chief-of-staff`, `C:\development\02-Kx-to-process`, `C:\development\command-center`, and `C:\development\marketing`.
   - Error recovery: stop before editing if any modify backup or manifest entry is missing; restore only the affected file.

4. - [x] 1.2 Create the shared rule directory, seven modular rule files, and ownership/loading manifest.
   - Files: C01–C07.
   - Prerequisites: `1.1`.
   - Authoritative acceptance check: `pwsh -NoProfile -Command "if ((Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\agent-rules' -File | Where-Object Name -in @('common-core.md','authority-boundaries.md','filesystem-and-git.md','research-and-evidence.md','agent-authoring.md','reference-index.md','RULES-MANIFEST.md')).Count -eq 7) { exit 0 } else { exit 1 }"` exits 0, and the manifest has exactly one owner, scope, and loading mode for each module.
   - Diagnostic checks: compare the source-to-destination rule matrix against the pre-change global files.
   - Error recovery: remove only C01–C07 paths marked `created-no-preimage` if the manifest is incomplete.

## Phase 2: Global Bootstrap and Progressive Disclosure

Objective: reduce always-loaded files while retaining harness-specific controls and clear triggers.

5. - [x] 2.1 Rewrite OpenCode global `AGENTS.md` as a thin adapter.
   - Files: M01.
   - Prerequisites: `1.2`.
   - Authoritative acceptance check: `pwsh -NoProfile -Command '& { $p="C:\Users\DaveWitkin\.config\opencode\AGENTS.md"; $t=Get-Content -LiteralPath $p -Raw; if(((Get-Item -LiteralPath $p).Length -lt 7000) -and ($t -match "agent-rules\\common-core.md") -and ($t -match "JSONC Only") -and ($t -match "secrets-index") -and ($t -match "Cross-Client Peer-Review")){exit 0}else{exit 1} }'` exits 0.
   - Diagnostic checks: run the source-to-destination matrix and retain every allowlisted always-on safety rule or route it to an explicit trigger.
   - Error recovery: restore M01 from backup and leave C01–C07 intact for review.

6. - [x] 2.2 Rewrite Codex global `AGENTS.md` as a thin Codex adapter.
   - Files: M02.
   - Prerequisites: `1.2`.
   - Authoritative acceptance check: `pwsh -NoProfile -Command '& { $p="C:\Users\DaveWitkin\.codex\AGENTS.md"; $t=Get-Content -LiteralPath $p -Raw; if(((Get-Item -LiteralPath $p).Length -lt 5000) -and ($t -match "agent-rules") -and ($t -match "Codex Task Title Convention") -and ($t -match "Code Mode Tool-Call Batching") -and ($t -notmatch "(?m)^\s*permission:")){exit 0}else{exit 1} }'` exits 0.
   - Diagnostic checks: verify Codex-only title, project-root, calendar, and batching behavior remains present.
   - Error recovery: restore M02 if a Codex-only rule is lost.

7. - [x] 2.3 Add OpenCode configuration wiring for the universal shared core only.
   - Files: M03.
   - Prerequisites: `2.1` and `2.2`.
   - Authoritative acceptance check: run `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode InstructionWiring -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\instruction-wiring-report.json'` and then this bounded redacted effective-config capture; both must exit 0: `pwsh -NoProfile -Command '& { $job=Start-Job -ScriptBlock { & opencode debug config 2>&1; "__OPENCODE_EXIT__=$LASTEXITCODE" }; if(-not (Wait-Job -Job $job -Timeout 30)){Stop-Job -Job $job; Remove-Job -Job $job -Force; exit 124}; $out=@(Receive-Job -Job $job); Remove-Job -Job $job -Force; $exitLine=$out | Where-Object { $_ -match "^__OPENCODE_EXIT__=" } | Select-Object -Last 1; if($null -eq $exitLine){exit 125}; $code=[int]($exitLine -replace "^__OPENCODE_EXIT__=",""); $out | Where-Object { $_ -notmatch "^__OPENCODE_EXIT__=" } | ForEach-Object { $s=($_ | Out-String).TrimEnd(); if($s -match "(?i)(apiKey|token|secret|password|authorization|cookie)"){ "[REDACTED_CONFIG_LINE]" } else { $s } } | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\opencode-debug-config-redacted.txt" -Encoding UTF8; if($code -eq 0){exit 0}else{exit $code} }'`; the validator confirms the single exact entry `agent-rules/common-core.md`, its resolved path, uniqueness, and absence of specialized modules, and the capture path is named and contains no unredacted scalar credential values.
   - Diagnostic checks: inspect the effective configuration with redacted output only; do not treat a conversational response as evidence.
   - Error recovery: restore M03 and rerun the validator.

## Phase 3: Agent-Writer and Standards Consolidation

Objective: make agent authoring current and remove duplicate normative sources.

8. - [x] 3.1 Update agent-writer templates and lint policy.
   - Files: M07–M08.
   - Prerequisites: `1.2`.
   - Authoritative acceptance check: `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode AgentFrontmatter -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\agent-frontmatter-report.json'` exits 0; the policy rejects plural `permissions:`, `tools.write`, `tools.edit`, `tools.bash`, and `permission.write`, requires singular `permission.edit`, `permission.bash`, and `permission.task` for each applicable template, and permits `tools.skill: false` only as an explicitly documented exception.
   - Diagnostic checks: compare templates against the current OpenCode CLI/docs and the canonical agent-authoring module.
   - Error recovery: restore M07–M08 only; do not alter the canonical standards during a template rollback.

9. - [x] 3.2 Repair missing agent-writer references and establish the canonical authoring reference.
   - Files: M06 and C05.
   - Prerequisites: `3.1`.
   - Authoritative acceptance check: `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode SkillReferences -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\skill-reference-report.json'` exits 0 and every path named in `agent-writer/SKILL.md` resolves to an existing file.
   - Diagnostic checks: search for the retired `skill-guidelines` paths and duplicate permission philosophies.
   - Error recovery: replace a removed historical reference with a compatibility pointer; do not delete historical notes.

10. - [x] 3.3 Consolidate duplicated OpenCode standards while retaining a compatibility index.
    - Files: M09–M11 and C05.
    - Prerequisites: `3.2`.
    - Authoritative acceptance check: `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode StandardsOwnership -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\standards-ownership-report.json'` exits 0 and reports one canonical owner for each permission, command, and agent-authoring rule with zero conflicting `tools:` capability maps, plural `permissions:`, or `permission.write` claims.
    - Diagnostic checks: inspect the compatibility index and headings for intentional historical context only.
    - Error recovery: restore an individual standards file and reapply only the ownership index.

## Phase 4: Environment, Project Files, and Validation Tooling

Objective: preserve the central environment source, simplify selected project adapters, and add repeatable checks.

11. - [x] 4.1 Add the deterministic cross-harness validator and negative fixtures.
    - Files: C08.
    - Prerequisites: `3.3`.
    - Authoritative acceptance check: `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode SelfTest -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\validator-selftest-report.json'` exits 0; each negative fixture fails its targeted check and the clean fixture passes, with no scalar configuration values emitted.
    - Diagnostic checks: inspect only paths, names, counts, and hashes in the reports.
    - Error recovery: restore the last known-good validator backup or leave the track blocked; do not weaken a failing check.

12. - [x] 4.2 Replace the one affected inline credential with the existing central environment reference.
    - Files: M03; M04 and M05 verify-only.
    - Prerequisites: `4.1` and the approved no-rotation boundary.
    - Authoritative acceptance check: `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode EnvReference -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\env-reference-report.json'` exits 0 and reports property `mcp.slack.environment.SLACK_MCP_XOXP_TOKEN` equals `{env:SLACK_USER_TOKEN}`, that `SLACK_USER_TOKEN` is defined in the central `.env`, and that the `.env` file hash/comments are unchanged; no value is printed, compared, or written.
    - Diagnostic checks: use a fresh noninteractive child process to test variable-name visibility only; never echo the value.
    - Error recovery: restore M03 from backup; do not alter M04.

13. - [x] 4.3 Refine selected project `AGENTS.md` adapters without dropping project commands or constraints.
    - Files: M12–M15.
    - Prerequisites: `2.1`, `2.2`, `3.3`, and `4.1`.
    - Authoritative acceptance check: `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode ProjectAdapters -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\project-adapter-report.json'` exits 0 and the closed source-to-destination matrix confirms each project-specific command/constraint remains in its adapter or points to an existing canonical document.
    - Diagnostic checks: compare pre/post headings and run project-local structural checks where available; keep unrelated Git changes unchanged.
    - Error recovery: restore an individual project adapter if its behavior is not preserved.

14. - [x] 4.4 Write the runbook describing progressive disclosure, loading triggers, env centralization, and rollback.
    - Files: C09.
    - Prerequisites: `4.2` and `4.3`.
    - Authoritative acceptance check: `pwsh -NoProfile -Command '& { $p="C:\development\opencode\docs\runbooks\agents-md-cross-harness.md"; if(-not (Test-Path -LiteralPath $p)){exit 1}; $t=Get-Content -LiteralPath $p -Raw; if(($t -match "OpenCode") -and ($t -match "Codex") -and ($t -match "progressive disclosure") -and ($t -match "SLACK_USER_TOKEN") -and ($t -match "rollback")){exit 0}else{exit 1} }'` exits 0.
    - Diagnostic checks: redact tokens and verify every referenced path resolves.
    - Error recovery: restore/delete only C09 according to the backup manifest.

## Final Phase: Validation & Handover

Objective: prove the result, preserve evidence, and synchronize Conductor state.

15. - [x] F.1 Run the complete validator and close out Conductor state.
    - Files: validation report, execution log, anomaly summary, rollback manifest, updated plan/metadata/ledgers, handoff artifacts.
    - Prerequisites: all implementation tasks.
    - Authoritative acceptance check: `pwsh -NoProfile -File 'C:\development\opencode\scripts\validate-agents-architecture.ps1' -Mode All -ReportPath 'C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\final-validation-report.json'` exits 0; it reports 15 task IDs, zero missing references, zero deprecated active capability maps, zero inline-secret findings for the approved field, intact `.env` hash, and metadata/ledgers agree on 15/15.
    - Diagnostic checks: bounded fresh-session spot checks in Codex and OpenCode, `opencode debug config`, `git status --short`, and `git diff --check`; identify unrelated dirty changes without rewriting them.
    - Error recovery: classify any mismatch as deliverable, plan, or bookkeeping; fix only bounded issues or leave a precise blocker artifact.

Phase exit criteria: all 15 task IDs are `[x]`; validation passes; artifacts exist; ledgers agree; credential rotation remains explicitly deferred.

## Execution Readiness Checklist

- [x] Atomic tasks and a closed target/ownership table.
- [x] Explicit commands, expected exit codes, and report paths.
- [x] Backup and rollback boundaries.
- [x] Cross-harness scope and no-rotation boundary.
- [x] Independent review accepted after the plan repair.

## Top 3 Implementation Risks + Mitigations

1. **Loss of an always-on safety rule during extraction** — maintain a source-to-destination matrix and compare the allowlisted always-on set before shortening any rule.
2. **Credential leakage during configuration edits** — use redacted scans, an existing env variable reference, an unchanged `.env`, and reports containing only names/counts/hashes.
3. **Dirty worktree collision** — back up exact target files, edit only the closed table, and record pre-existing Git changes before and after repository-scoped edits.

## First Task to Execute Immediately

After the repaired Stage 2 review is accepted, create timestamped backups and the closed manifest; do not edit global, project, skill, or config files before that manifest passes validation.
