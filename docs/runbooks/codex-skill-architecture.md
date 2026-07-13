# Codex / OpenCode Skill Architecture Runbook

> **Status:** Authoritative reference for this machine's OpenCode/Codex skill storage layout.  
> **Last verified:** 2026-07-06.  
> **Supersedes:** older guidance in `docs/reference/lazy-loaded-skills.md`, `docs/reference/global-skills-index.md`, and the older `.agents` unification assumptions in `.conductor/tracks/20260502-skill-junction-unification/`.

## Executive summary

Use **one active skill store** for normal work:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault
```

That lazy vault is the default location for new skills. Codex sees the same skills because its skill directory is a parent junction to the lazy vault:

```text
C:\Users\DaveWitkin\.codex\skills
  -> C:\Users\DaveWitkin\.opencode-lazy-vault
```

Only a small always-on OpenCode set remains under:

```text
C:\Users\DaveWitkin\.config\opencode\skill
```

Do **not** create new skills there unless the user explicitly wants the skill always injected into every OpenCode session.

## Current surfaces

| Surface | Path | Expected current type | Purpose | Policy |
|---|---|---:|---|---|
| Lazy vault | `C:\Users\DaveWitkin\.opencode-lazy-vault` | Real directory | Default store for most OpenCode/Codex skills | New skills go here by default. |
| Codex skills | `C:\Users\DaveWitkin\.codex\skills` | Parent junction to lazy vault | Makes lazy-vault skills visible to Codex | Keep as one parent junction; never add child junctions under it. |
| OpenCode always-on skills | `C:\Users\DaveWitkin\.config\opencode\skill` | Real directory | Small prompt-injected OpenCode skill set | Only foundational skills belong here. |
| OpenCode compatibility plural path | `C:\Users\DaveWitkin\.config\opencode\skills` | Compatibility directory/path | Historical/plural OpenCode scan path | Do not use as the default creation target. Prefer `skill\` for always-on and lazy vault for normal skills. |
| Generic `.agents` skills | `C:\Users\DaveWitkin\.agents\skills` | **Archived / absent** | Historical generic Codex/agent convention | Removed from the live filesystem on 2026-07-06 to avoid confusion. Do not recreate unless a future tool explicitly requires it. |
| OneDrive development-config backing | `C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config` | Backup/sync mirror, not active runtime root | Historical sync/backing source for many entries | Do not create new local skills as OneDrive-backed junctions unless explicit cross-machine sync is requested. |

## Current always-on OpenCode set

As of 2026-07-06, the always-on native directory contains these seven skills:

```text
conductor
conductor-pipeline
git-push
opencode-scheduler
osgrep
perplexity-search
skill-discovery
```

This set should stay small. Every skill here can be injected into OpenCode session context. If a skill is useful but not foundational, keep it in the lazy vault instead.

## Default new-skill placement

For normal new skills, create a real folder here:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>\SKILL.md
```

This is sufficient for:

- OpenCode lazy loading through `skill_find` / `skill_use` when the skillful plugin indexes the vault.
- Codex visibility through `C:\Users\DaveWitkin\.codex\skills`, because that path is a parent junction to the lazy vault.

Use the always-on directory only when explicitly requested:

```text
C:\Users\DaveWitkin\.config\opencode\skill\<skill-name>\SKILL.md
```

If an always-on skill should also appear in the lazy vault, expose it with a vault child junction:

```cmd
cmd /c mklink /j "C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>" "C:\Users\DaveWitkin\.config\opencode\skill\<skill-name>"
```

## Codex parent-junction rule

`C:\Users\DaveWitkin\.codex\skills` is a directory junction to the lazy vault. Therefore these two paths refer to the same children:

```text
C:\Users\DaveWitkin\.codex\skills\<skill-name>
C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>
```

Because of that, these operations are forbidden:

```powershell
New-Item -ItemType Junction -Path "C:\Users\DaveWitkin\.codex\skills\<skill-name>" -Target "..."
```

```cmd
cmd /c mklink /j "C:\Users\DaveWitkin\.codex\skills\<skill-name>" "..."
```

Creating child junctions under the Codex parent junction actually mutates the lazy vault and can create self-referential junctions.

## `.agents\skills` policy

`C:\Users\DaveWitkin\.agents\skills` was used by older Codex/generic-agent experiments and by migration references copied from upstream Codex skill tooling. Current local evidence does **not** show it being required by active OpenCode or Codex configuration:

- `C:\Users\DaveWitkin\.codex\skills` is the active Codex path on this machine.
- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` does not depend on `.agents\skills`.
- Current user/global OpenCode guidance points to the lazy vault and `skill-creator`, not `.agents\skills`.

Therefore `.agents\skills` is **legacy / non-authoritative**. It was archived and removed from the live location on 2026-07-06:

```text
C:\Users\DaveWitkin\.agents\archive\skills-20260706-144958
```

Do not add new skills there and do not treat it as a required mirror.

If future tooling explicitly requires `.agents\skills`, prefer one of these deliberate choices and document the decision before changing filesystem state:

1. Create `C:\Users\DaveWitkin\.agents\skills` as a parent junction to `C:\Users\DaveWitkin\.opencode-lazy-vault`; or
2. Keep it archived/absent and configure that future tool to use `C:\Users\DaveWitkin\.codex\skills` or the lazy vault directly.

Do not maintain a partial set of child junctions in `.agents\skills`; that state drifts and creates broken links.

## OneDrive-backed junction policy

Previously, many lazy-vault entries were junctions to:

```text
C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\<skill-name>
```

That pattern was historical sync/backup plumbing from `development-config`, not a runtime requirement. **As of 2026-07-06, all 63 OneDrive-backed lazy-vault junctions were localized to real folders** (content-identical, SHA256-verified) via track `20260706-lazy-vault-localization`. The OneDrive originals remain as a backup layer. The active runtime root remains:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault
```

Policy going forward:

- New skills should be **real folders directly under the lazy vault**.
- **Do not create OneDrive-backed runtime junctions.** The previous 63 were retired/localized on 2026-07-06; only 7 native-backed always-on junctions (pointing to `~/.config/opencode/skill`) remain by design.
- If a skill should be made portable/synced, copy it deliberately to the OneDrive backing tree as a *backup* (not a junction target), and record the reason in the skill or track notes.

This means skills such as `handoff-quick` and `handoff-deep` are acceptable as local real folders under:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault\handoff-quick
C:\Users\DaveWitkin\.opencode-lazy-vault\handoff-deep
```

unless/until cross-machine sync is explicitly desired.

## Safe operations

### Add a normal lazy skill

```powershell
New-Item -ItemType Directory -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>"
```

Then create:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>\SKILL.md
```

### Add an always-on skill

Only when explicitly requested:

```powershell
New-Item -ItemType Directory -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\<skill-name>"
```

Optional vault bridge:

```cmd
cmd /c mklink /j "C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>" "C:\Users\DaveWitkin\.config\opencode\skill\<skill-name>"
```

### Remove a junction

Never use `Remove-Item` on a junction. Use:

```cmd
cmd /c rmdir "<junction-path>"
```

### Remove a real folder

Back it up first, verify it is not a reparse point, then `Remove-Item -Recurse -Force` is acceptable for a real folder.

## Forbidden operations

- Creating per-skill child junctions under `C:\Users\DaveWitkin\.codex\skills\<name>`.
- Treating `C:\Users\DaveWitkin\.codex\skills` as an independent real folder.
- Maintaining `.agents\skills` as a partial ad hoc mirror.
- Using `Remove-Item` on any junction/reparse point.
- Creating new skills in `C:\Users\DaveWitkin\.config\opencode\skill` unless they are intentionally always-on.

## What if I find a self-referential junction?

A self-referential junction is a junction whose target equals its own path. It usually means a prior script created a child junction under a parent junction by mistake.

Remediation:

1. Snapshot metadata to a track backup folder.
2. If a backup with `SKILL.md` exists, remove the broken junction with `cmd /c rmdir` and restore the real folder from backup.
3. If no backup exists, remove the broken junction with `cmd /c rmdir` and document the skill as not restored.
4. Re-scan and confirm zero self-referential junctions remain.

## Quick diagnostic commands

### Root state

```powershell
foreach ($p in @(
  'C:\Users\DaveWitkin\.opencode-lazy-vault',
  'C:\Users\DaveWitkin\.codex\skills',
  'C:\Users\DaveWitkin\.config\opencode\skill',
  'C:\Users\DaveWitkin\.agents\skills'
)) {
  if (Test-Path -LiteralPath $p) {
    $i = Get-Item -LiteralPath $p -Force
    [pscustomobject]@{
      Path = $p
      IsReparse = [bool]($i.Attributes -band [IO.FileAttributes]::ReparsePoint)
      Target = if ($i.Target) { $i.Target -join ';' } else { '' }
    }
  }
}
```

### Self-referential vault junction scan

```powershell
$vaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
Get-ChildItem -LiteralPath $vaultRoot -Directory -Force |
  Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } |
  ForEach-Object {
    $t = (Get-Item -LiteralPath $_.FullName).Target
    if ($t -is [array]) { $t = $t[0] }
    if ($t -eq $_.FullName) {
      [pscustomobject]@{ Name=$_.Name; Path=$_.FullName; Target=$t; SELF_REFERENTIAL=$true }
    }
  }
```

## Historical notes

- `.conductor/tracks/20260502-skill-junction-unification/` proposed using both `.codex\skills` and `.agents\skills` as parent junctions. The Codex half is now implemented and remains authoritative; the `.agents` half is superseded because `.agents\skills` is not an active required surface.
- `.conductor/tracks/20260704-session-continuation-codex-skill-architecture-fix/` corrected the important root cause: child operations under a parent-junction Codex root mutate the lazy vault. This is the basis for the current Codex rule.
