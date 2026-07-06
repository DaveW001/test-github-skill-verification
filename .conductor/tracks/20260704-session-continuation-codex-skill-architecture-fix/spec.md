# Spec: Codex Skill Architecture Repair and Automation Hardening

## Source Session

- Title: 2026-07-03 Peer Review Skill migration handoff
- Session ID: ses_0d5dc5f6dffe9JJBeutG1SekuY
- Repo: C:\development\opencode
- Watermark: 2026-07-04T18:02:56.366000
- Handoff created: 2026-07-04

## Goal

Finish the Codex/OpenCode skill migration safely and harden the automation so it cannot recreate self-referential junctions or mutate the wrong store. The immediate broken artifact is `pptx-to-pdf-converter`; broader work is to update scripts/plans/validators to respect the actual parent-junction architecture.

## Background / Evidence

### Original intent

The session began by reviewing `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\handoff-skill-migration-investigation-2026-07-03.md` and then attempted to implement the peer-review recommendations. The intended architecture was clarified over the session:

1. `C:\Users\DaveWitkin\.codex\skills` is not an independent real folder; it is a directory junction/reparse point targeting `C:\Users\DaveWitkin\.opencode-lazy-vault`.
2. Lazy-loaded skills should be real folders in `C:\Users\DaveWitkin\.opencode-lazy-vault`.
3. A small always-on set remains in `C:\Users\DaveWitkin\.config\opencode\skill` and is exposed through per-skill junctions inside the vault.
4. The two pending migrations were `nlm-skill` and `pptx-to-pdf-converter`: they should be absent from native and should be real vault folders.

### Major correction discovered late in the session

Earlier automation incorrectly treated `C:\Users\DaveWitkin\.codex\skills` as an independent root containing child entries. Because that path is itself a junction to the vault, operations like creating `C:\Users\DaveWitkin\.codex\skills\pptx-to-pdf-converter` actually create/mutate `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter`. This caused self-referential vault junctions such as:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter
  -> C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter
```

This supersedes the earlier mistaken explanation that OpenCode Desktop itself was recreating junctions. The peer-review subagent agreed that the parent-junction root cause is technically sound.

### Current verified filesystem state at handoff

Verified with read-only PowerShell during this handoff:

```text
C:\Users\DaveWitkin\.codex\skills
  Attributes: Directory, ReparsePoint
  Target: C:\Users\DaveWitkin\.opencode-lazy-vault

C:\Users\DaveWitkin\.opencode-lazy-vault
  Attributes: Directory

C:\Users\DaveWitkin\.config\opencode\skill
  Attributes: Directory
```

Current target-skill state:

```text
nlm-skill:
  NativeExists: false
  VaultExists: true
  VaultAttrs: Directory
  VaultHasSkill: true
  Codex path resolves through parent junction and sees SKILL.md: true
  Status: functionally correct; do not create a child junction for it.

pptx-to-pdf-converter:
  NativeExists: false
  VaultExists: true
  VaultAttrs: Directory, ReparsePoint
  VaultTarget: C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter
  VaultHasSkill: false
  Codex path resolves to the same broken vault self-junction and cannot see SKILL.md.
  Status: broken; restore vault entry as a real folder from backup.
```

Current native always-on set:

```text
conductor
conductor-pipeline
git-push
opencode-scheduler
osgrep
perplexity-search
session-handoff
skill-discovery
```

Observed vault junctions to native during investigation included these same always-on skills. These should remain native unless the new pipeline intentionally changes the always-on policy.

### Important backups

A valid backup for `pptx-to-pdf-converter` exists at:

```text
C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\2026-07-04-090412-pptx-repair\native\SKILL.md
```

Other relevant backups and reports created during the session include:

```text
C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\2026-07-04-090431-full-migration
C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\2026-07-04-090256-nlm-repair
C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\2026-07-04-090412-pptx-repair
C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\migration-executor-report-2026-07-04-090431.json
```

### Flawed automation created/identified during the session

These scripts exist but are now known to have flawed assumptions and must not be run for real changes until corrected:

```text
C:\development\_shared-scripts\codex-skill-migration-executor.ps1
C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1
```

Both were created/edited while the assistant still assumed `C:\Users\DaveWitkin\.codex\skills` was a real independent parent. They can recreate the self-junction pattern if they create per-skill junctions under `CodexRoot` while `CodexRoot` is a parent junction to the vault.

The scheduled validator prompt also needs review/update:

```text
C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md
```

It currently describes native as the canonical skills directory and auto-creates Codex/Agents junctions from native. Under the clarified architecture, Codex is already a parent junction to the vault, so child junction creation under Codex is incorrect.

## Successor Sessions Reviewed

The session-handoff workflow scanned same-repo successors after the watermark. Reviewed sessions were unrelated to this work:

| Session Title | Session ID | Active Window | Relevant? | Finding |
|---|---|---:|---|---|
| 2026-07-04 Pipeline skillshare-rollout-improvements | ses_0d19350c5ffekO9a6QBKKu4NrV | 2026-07-04T14:38:22 -> 2026-07-04T18:05:43 | No | SkillShare rollout pipeline, unrelated to Codex skill junction repair. |
| Stage 2 plan review (@conductor-plan-reviewer subagent) | ses_0d0e0a23effe3Dmy0A0M5JxcAE | 2026-07-04T17:53:32 -> 2026-07-04T18:07:35 | No | Review of a Microsoft Graph junction repair track; not this Codex skill architecture repair. |
| Stage 2: Review humanizer fix plan (@conductor-plan-reviewer subagent) | ses_0d0e21b33ffeAplTrUBzNOLvpL | 2026-07-04T17:51:56 -> 2026-07-04T18:07:36 | No | Humanizer skill peer-review fixes, unrelated. |

No successor session superseded this intent.

## Scope

### In Scope

- Repair `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter` by removing the broken self-referential junction and restoring a real folder from backup.
- Validate `nlm-skill` remains a real vault folder and absent from native.
- Validate `C:\Users\DaveWitkin\.codex\skills` remains a parent junction to `C:\Users\DaveWitkin\.opencode-lazy-vault`.
- Update or disable flawed scripts that assume per-skill Codex child junctions should be created beneath `C:\Users\DaveWitkin\.codex\skills`.
- Update `skill-health-validator.md` so it understands the clarified architecture and does not auto-create child junctions under a parent-junction Codex root.
- Add guardrails/tests preventing future code from mutating children under `CodexRoot` when `CodexRoot` is a reparse point to `VaultRoot`.
- Preserve backups before every removal or replacement.

### Out of Scope

- Deleting or migrating the always-on native skills unless the new pipeline explicitly changes that policy.
- Killing OpenCode Desktop processes from the agent. The previous session did this once and it disrupted the user; do not repeat it.
- Re-running the flawed migration executor or reconcile script against real stores before corrections are made and dry-run validated.
- Treating the parent `C:\Users\DaveWitkin\.codex\skills` junction as wrong without an explicit architectural decision. The current discovered architecture relies on it.

## Constraints / Guardrails

- Use PowerShell-first via the bash tool if native file tools return `Bun is not defined`.
- Use absolute Windows paths.
- Never use PowerShell `Remove-Item` on a junction/reparse point. Use `cmd /c rmdir "<junction>"` to remove junctions.
- Before removing a real folder, copy it to a timestamped backup under `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\` or this continuation track's backup folder.
- Do not create child junctions under `C:\Users\DaveWitkin\.codex\skills` when that root is itself a junction to the vault.
- If a command resolves `C:\Users\DaveWitkin\.codex\skills\<name>`, remember this is also `C:\Users\DaveWitkin\.opencode-lazy-vault\<name>` because of the parent junction.
- Prefer guarded scripts with explicit prechecks and postchecks over ad hoc commands.

## Acceptance Criteria

- `C:\Users\DaveWitkin\.codex\skills` is a reparse point targeting `C:\Users\DaveWitkin\.opencode-lazy-vault`.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill` exists, is not a reparse point, and contains `SKILL.md`.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter` exists, is not a reparse point, and contains `SKILL.md`.
- `C:\Users\DaveWitkin\.config\opencode\skill\nlm-skill` and `C:\Users\DaveWitkin\.config\opencode\skill\pptx-to-pdf-converter` are absent.
- The always-on native set remains present unless intentionally changed: `conductor`, `conductor-pipeline`, `git-push`, `opencode-scheduler`, `osgrep`, `perplexity-search`, `session-handoff`, `skill-discovery`.
- No self-referential junctions remain in `C:\Users\DaveWitkin\.opencode-lazy-vault`.
- Flawed scripts either refuse real mutation when `CodexRoot` is a parent junction or are disabled/renamed with clear warnings.
- `skill-health-validator.md` no longer instructs agents to create per-skill Codex child junctions under a parent-junction Codex root.
- Final validation report records commands run, outputs, backups, and any deviations.

## Validation Commands

Use these as starting points; Conductor should refine them into precise executable steps.

```powershell
# Parent architecture
$codexRoot = 'C:\Users\DaveWitkin\.codex\skills'
$vaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
$item = Get-Item -LiteralPath $codexRoot
[pscustomobject]@{
  CodexRootIsReparse = [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
  CodexRootTarget = $item.Target
  TargetMatchesVault = ($item.Target -eq $vaultRoot)
}
```

```powershell
# Target skills final state
$nativeRoot = 'C:\Users\DaveWitkin\.config\opencode\skill'
foreach ($name in @('nlm-skill','pptx-to-pdf-converter')) {
  $v = Join-Path $vaultRoot $name
  $n = Join-Path $nativeRoot $name
  $vi = if (Test-Path -LiteralPath $v) { Get-Item -LiteralPath $v } else { $null }
  [pscustomobject]@{
    Name = $name
    NativeExists = Test-Path -LiteralPath $n
    VaultExists = Test-Path -LiteralPath $v
    VaultIsReparse = if ($vi) { [bool]($vi.Attributes -band [IO.FileAttributes]::ReparsePoint) } else { $null }
    VaultTarget = if ($vi -and ($vi.Attributes -band [IO.FileAttributes]::ReparsePoint)) { $vi.Target } else { $null }
    VaultHasSkill = Test-Path -LiteralPath (Join-Path $v 'SKILL.md')
    CodexSeesSkill = Test-Path -LiteralPath (Join-Path $codexRoot "$name\SKILL.md")
  }
}
```

```powershell
# Self-referential vault junction check
Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault' -Directory -Force |
  Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } |
  ForEach-Object {
    $target = (Get-Item -LiteralPath $_.FullName).Target
    if ($target -eq $_.FullName) { [pscustomobject]@{ Name=$_.Name; Path=$_.FullName; Target=$target } }
  }
```
