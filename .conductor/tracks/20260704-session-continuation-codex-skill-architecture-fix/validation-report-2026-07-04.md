# Validation Report - Codex Skill Architecture Repair and Automation Hardening

- **Track:** 20260704-session-continuation-codex-skill-architecture-fix
- **Executor:** conductor-track-executor (Stage 4)
- **Model:** zai-coding-plan/glm-5.2 (Tier 1)
- **Executed at (UTC):** 2026-07-05T01:13:52.6884082Z
- **Plan reviewed (Stage 2):** 87% GO. **Re-reviewed (Stage 3):** 92% GO.
- **Preflight source:** <track>/preflight-state.json (Task 1)

## Block 1 - Parent architecture

```
CodexRootIsReparse   = True
CodexRootTarget      = C:\Users\DaveWitkin\.opencode-lazy-vault
TargetMatchesVault   = True
VaultIsRealDirectory = True
```

## Block 2 - Target skills final state

```json
[
  { "Name": "nlm-skill",             "NativeExists": false, "VaultExists": true, "VaultIsReparse": false, "VaultHasSkill": true, "CodexSeesSkill": true, "CodexAliasIsNotReparse": true },
  { "Name": "pptx-to-pdf-converter", "NativeExists": false, "VaultExists": true, "VaultIsReparse": false, "VaultHasSkill": true, "CodexSeesSkill": true, "CodexAliasIsNotReparse": true }
]
```

SHA-256 (vault == codex alias, proving parent-junction aliasing):
- nlm-skill SKILL.md: `209A6B7891DC2BBFB8953C13DB5AA78BBFCC051D43EC2CD6043F51C6B925AF30`
- pptx-to-pdf-converter SKILL.md: `1B75F6E8E929D4B20FD5ABD04BF7A016D3E112F3875F32F9A577B5684D37985F` (matches backup)

## Block 3 - Self-referential vault junction check

```
Self-referential count: 0
[]
```

## Block 4 - Always-on native set

```
ExpectedAlwaysOn      = conductor, conductor-pipeline, git-push, opencode-scheduler, osgrep, perplexity-search, session-handoff, skill-discovery
ActualNative          = (identical 8 names)
MissingAlwaysOn       = []
TargetSkillsStillInNative = [] (nlm-skill, pptx-to-pdf-converter both absent from native)
AllAlwaysOnPresent    = True
TargetsAbsentFromNative = True
```

## Acceptance Criteria (spec.md - 9 criteria)

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Codex parent junction -> vault | **PASS** | Block 1: CodexRootIsReparse=True, TargetMatchesVault=True |
| 2 | nlm-skill real vault folder with SKILL.md | **PASS** | Block 2: VaultExists=True, VaultIsReparse=False, VaultHasSkill=True |
| 3 | pptx-to-pdf-converter real vault folder with SKILL.md | **PASS** | Task 2 postcheck + Block 2: VaultIsReparse=False, VaultHasSkill=True, SHA matches backup 1B75F6E8... |
| 4 | nlm/pptx absent from native | **PASS** | Block 2: NativeExists=False for both |
| 5 | Always-on native set intact | **PASS** | Block 4: AllAlwaysOnPresent=True (all 8 present) |
| 6 | No self-referential junctions in vault | **PASS** | Block 3: count=0 |
| 7 | Flawed scripts disabled/patched | **PASS** | Task 6: Assert-CodexRootIsNotParentJunction in both scripts; mklink "$codexPath"=0; all 5 broader patterns=0; dry-run aborts at guard |
| 8 | skill-health-validator.md updated | **PASS** | Task 7: isCodexParentJunction=4, "Do NOT create per-skill Codex child junctions"=1, old dangerous form=0 |
| 9 | Final validation report records commands, outputs, backups, deviations | **PASS** | This report (see "Commands run", "Backups", "Deviations") |

**Overall: 9/9 PASS.** Status: `complete-with-followup`.

## Commands run (Stage 4)

1. Task 1 preflight -> `preflight-state.json` (all acceptance fields True).
2. Task 2: snapshot `backups/pptx-junction-snapshot/junction-metadata.json`; `cmd /c rmdir` the pptx self-ref junction; restore real folder from `2026-07-04-090412-pptx-repair/native`; postcheck all True.
3. Task 3: nlm-skill 6-field assertion all True.
4. Task 4: vault/codex SHA equality for both skills; both codex aliases NotReparse.
5. Task 5a: scan -> 1 self-ref (image-to-html-reconstruction; pptx already real). 5b: skip (pptx done by Task 2). 5c: snapshot `backups/image-to-html-reconstruction-junction-snapshot/junction-metadata.json`; `cmd /c rmdir`; document in `backups/skills-not-restored.md`; re-scan -> 0.
6. Task 6: backup both scripts; add guard + call; neutralize Codex-child mutation calls; parse-check; Select-String + dry-run verification.
7. Task 7: backup validator; rewrite Check 3 + Paths note + Preflight bullet; verify.
8. Task 8: create `docs/runbooks/`; write `codex-skill-architecture.md`; add validator runbook cross-reference.
9. Task 9: this report; metadata.json; ledger upserts.

## Backups taken

- `backups/pptx-junction-snapshot/junction-metadata.json` (Task 2.1)
- `backups/image-to-html-reconstruction-junction-snapshot/junction-metadata.json` (Task 5c)
- `backups/2026-07-04-210409-task6-scripts/` (both flawed scripts pre-edit) + `*.bak` beside originals
- `backups/<stamp>-task7-validator/skill-health-validator.md` + `skill-health-validator.md.bak`
- pptx restore source: `tracks/20260702-codex-skill-symlinks/backups/2026-07-04-090412-pptx-repair/native` (pre-existing)

## Deviations / Tier-0 decisions

- **Tier-0 (Task 6):** Chose plan-sanctioned targeted-edit patch (guard + neutralize Codex-child mutation calls) over the `*.disabled.ps1` rename fallback, to keep filenames/verification paths stable and satisfy both binding and Stage-3 broader-pattern checks with zero matches.
- **No-backup safe-remove (Task 5c):** `image-to-html-reconstruction` removed as a self-referential junction only; no replacement folder created. Documented as not-restored (no backup SKILL.md exists anywhere). Recorded in `followups`.
- **New-Item -LiteralPath unsupported** on this PowerShell build for directory creation; used `New-Item -Path` (paths contain no wildcards). No functional impact.
- **Latent follow-up (not in plan scope):** validator Check 4 (Archive Hygiene) still uses `Remove-Item "<path>\<name>" -Force` on Codex/Agents entries; under the parent-junction architecture this could touch a reparse point. Task 7 scoped only Check 3. Flagged in followups for a future hardening pass.

## Followups

- `image-to-html-reconstruction`: self-referential junction removed; NOT restored (no backup). Re-add intentionally if/when content is authored.
- validator Check 4: harden `Remove-Item` against reparse points (use `cmd /c rmdir` when target is a junction).
