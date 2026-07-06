# Review Diff Summary
## Track: 20260704-session-continuation-codex-skill-architecture-fix
## Reviewer: opencode-go/minimax-m3
## Date: 2026-07-04

## Files edited by this review

- `C:\development\opencode\.conductor\tracks\20260704-session-continuation-codex-skill-architecture-fix\plan.md` rewritten from 41 lines to 286 lines.

## Structural change summary

| Item | Before | After | Delta |
|---|---|---|---|
| Plan line count | 41 | 286 | +245 |
| Top-level tasks | 9 | 9 | 0 |
| Sub-tasks 5a/5b/5c | 0 | 3 within Task 5 | +3 |
| Explicit PowerShell blocks | 0 | 7 in Tasks 1, 2, 3, 4, 5, 6, 7 | +7 |
| Concrete file paths cited | ~6 | ~30 | +24 |
| SHA-256 byte-hash postchecks | 0 | 3 in Tasks 2, 4, 9 | +3 |
| Negative-test assertions | 0 | 4 in Tasks 3, 4, 7, 8 | +4 |
| Select-String or Test-Path verification commands | 0 | about 12 in Tasks 6, 7, 8, 9 | +12 |

Spec and acceptance-criteria count unchanged: 9. spec.md not edited.
Phase count unchanged: 0. Plan has no formal phase structure.


## Substantive per-task changes

### Task 1: Preflight and freeze assumptions

Before, 4 narrative bullets.

After:
- Explicit PowerShell block that reads all 4 checks plus SKILL.md SHA-256 hash.
- Writes structured JSON to preflight-state.json with a defined schema.
- 5-bullet acceptance list with explicit pass criteria.
- If any acceptance field is false, executor must STOP and surface the JSON.

### Task 2: Repair pptx-to-pdf-converter vault entry

Before, 5 narrative bullets, no exact commands.

After:
- 4 explicit steps: snapshot, remove, copy, postcheck.
- Snapshot: writes junction metadata to <track>/backups/pptx-junction-snapshot/junction-metadata.json.
- Remove: explicit `cmd /c rmdir` with a `throw` if removal fails.
- Copy: `Get-ChildItem -LiteralPath $backupNative -Force | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $vaultPptx -Recurse -Force }` - correctly copies children, not the parent directory.
- Postcheck: 7-field assertion object including SKILL.md SHA-256 match between backup and restored vault folder, plus Codex-alias not-reparse check.

### Task 3: Validate nlm-skill final state

Before, 3 narrative bullets.

After:
- Explicit PowerShell block producing a 6-field assertion object.
- Includes `CodexAliasIsNotReparse` which proves no per-skill Codex child junction was created, and `NativeAbsent`.

### Task 4: Validate Codex visibility through the parent junction

Before, 2 narrative bullets.

After:
- Explicit PowerShell block with 4 SHA-256-based hash equality assertions.
- Includes negative `NlmCodexNotReparse` and `PptxCodexNotReparse` checks.


### Task 5: Detect and remove/repair any self-referential vault junctions

Before, 1 narrative bullet, Blocking as written because no path for the no-backup case.

After, split into 5a, 5b, 5c, addresses the second self-ref junction `image-to-html-reconstruction` that has no backup:
- Step 5a: explicit scan PowerShell that writes selfref-junctions.json.
- Step 5b: parameterized repair-from-backup path. Covers pptx-to-pdf-converter. Will be a no-op if Task 2 ran first.
- Step 5c: explicit safe-remove-without-backup path for `image-to-html-reconstruction` and any other no-backup self-refs discovered later. Snapshots metadata, uses `cmd /c rmdir` which is safe because a self-ref is functionally a no-op, documents in <track>/backups/skills-not-restored.md. Does NOT create any replacement folder.
- 4-bullet acceptance list including selfref-junctions.json being empty after re-run.

### Task 6: Patch or disable flawed automation

Before, 5 narrative bullets, no concrete code.

After:
- Concrete `Assert-CodexRootIsNotParentJunction` PowerShell function body to add to BOTH scripts.
- Explicit call site near the top of each script body.
- Explicit list of code patterns to remove: `NewJunction $codexPath`, `New-Item -ItemType Junction -Path $codexPath`, `cmd /c mklink /j "$codexPath"`, `RemoveJunction $codexPath`, `Remove-Item -LiteralPath $codexPath -Recurse -Force`.
- 5-bullet verification list with Select-String commands that the old dangerous patterns are gone and the new guard pattern is present.
- Includes a dry-run smoke test command for the reconcile script.

### Task 7: Patch skill-health-validator.md

Before, 3 narrative bullets, no concrete code.

After:
- Identifies the exact root bug: the `New-Item -ItemType Junction -Path "<codex-skills>\<name>" -Target "<canonical>\<name>" -Force` call.
- Concrete replacement text for `Check 3: Junction Consistency` with an `$isCodexParentJunction` preflight and a do-not-create-child-junctions-when-parent-junction branch.
- Updates to "Action: AUTO-FIX" line.
- Updates to "Paths: constants" and "Preflight" sections.
- 3 Select-String verification commands confirming the dangerous old pattern is gone and the new guard is present.


### Task 8: Update documentation

Before, 3 narrative bullets, no specific file path.

After:
- Specific runbook file path: `C:\development\opencode\docs\runbooks\codex-skill-architecture.md`. Create the dir if missing.
- 4 explicit content sections: Architecture, Allowed operations, Forbidden operations, Self-ref remediation SOP.
- Cross-reference from `skill-health-validator.md` to the runbook.
- 2 Test-Path or Select-String verification commands.

### Task 9: Final validation and closeout

Before, 3 narrative bullets.

After:
- 4-step structure: 9.1 re-run 3 spec validations into report, 9.2 acceptance criteria PASS/FAIL table with explicit evidence per criterion, 9.3 metadata.json status update with followups array, 9.4 append to tracks-ledger.md.
- Concrete acceptance criterion list with the exact line of evidence for each.
- Concrete tracks-ledger.md append format.

## Handoff Prompt

Was 2 lines, now 3 lines. Added a sentence about the second self-referential junction `image-to-html-reconstruction` so the next-stage agent knows to handle it safely.

## Execution Rules

Was 5 bullets, now 7. Added 3 bullets:
- "Never create per-skill entries under `C:\Users\DaveWitkin\.codex\skills` while that root is a parent junction to the vault. Use `C:\Users\DaveWitkin\.opencode-lazy-vault\<name>` - the real path - instead."
- "If a command resolves `C:\Users\DaveWitkin\.codex\skills\<name>`, remember this is an alias into the vault because of the parent junction. Mutating the alias mutates the vault."
- "Each task must end with an explicit postcheck - the script or assertion object - before declaring success."

Refined 1 bullet:
- "Remove junctions only with `cmd /c rmdir`" now also says "Never use PowerShell `Remove-Item` on a junction."

## What I did NOT edit

- `spec.md`: not edited. The 9 acceptance criteria are correct and aligned with the rewritten plan tasks.
- `metadata.json`: not edited. Stage 4 will update it per Task 9.3.
- The two flawed PowerShell scripts and the validator markdown: not edited. Stage 4 will edit them per Tasks 6 and 7.

## Note on Track 2 preflight finding

The orchestrator preflight also found `image-to-html-reconstruction` as a self-ref. This review confirmed via exhaustive backup audit using the script `review-backup-audit.ps1` that NO backup exists for this skill. The plan now handles this case explicitly in Task 5c.
