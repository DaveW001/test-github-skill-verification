# Codex Skill Architecture Runbook

> **Status:** Authoritative reference for the Codex/OpenCode skill store layout.
> **Last verified:** 2026-07-04 (by Conductor track `20260704-session-continuation-codex-skill-architecture-fix`).

## Architecture (verified 2026-07-04)

- `C:\Users\DaveWitkin\.codex\skills` is a **directory junction** (reparse point) targeting `C:\Users\DaveWitkin\.opencode-lazy-vault`. The two paths are the **SAME folder**.
- Lazy-loaded skills are **real folders** under `C:\Users\DaveWitkin\.opencode-lazy-vault\<skill>`.
- A small **always-on set** stays under `C:\Users\DaveWitkin\.config\opencode\skill\<skill>` and is exposed in the vault as a **per-skill junction** (e.g. `C:\Users\DaveWitkin\.opencode-lazy-vault\conductor` -> `C:\Users\DaveWitkin\.config\opencode\skill\conductor`).
- The Codex root must **NEVER** have per-skill child junctions created under it directly, because that mutates the vault and can produce **self-referential junctions** (a junction whose target equals its own path).

### Stale assumption (superseded)

The earlier assumption that "`C:\Users\DaveWitkin\.codex\skills` is a normal independent skills directory" is **STALE and WRONG**. Treat it as a parent junction to the vault at all times.

## Allowed operations

- **Add a lazy skill (real folder in the vault):** create `C:\Users\DaveWitkin\.opencode-lazy-vault\<name>\` (with `SKILL.md`).
- **Add an always-on skill:** create the real folder under `C:\Users\DaveWitkin\.config\opencode\skill\<name>\`, then expose it in the vault with a per-skill junction:
  ```
  cmd /c mklink /j "C:\Users\DaveWitkin\.opencode-lazy-vault\<name>" "C:\Users\DaveWitkin\.config\opencode\skill\<name>"
  ```
- **Remove a vault entry that is a junction:** use `cmd /c rmdir` ONLY (NEVER `Remove-Item` on a junction):
  ```
  cmd /c rmdir "C:\Users\DaveWitkin\.opencode-lazy-vault\<name>"
  ```
- **Remove a vault entry that is a real folder:** back it up first, then `Remove-Item -LiteralPath "..." -Recurse -Force` is acceptable for a real folder (not a junction).

## Forbidden operations

- `New-Item -ItemType Junction -Path "C:\Users\DaveWitkin\.codex\skills\<name>" ...` (mutates the vault)
- `cmd /c mklink /j "C:\Users\DaveWitkin\.codex\skills\<name>" ...` (mutates the vault)
- `Remove-Item` on ANY junction/reparse point (use `cmd /c rmdir` instead). `Remove-Item` on a junction can recurse into and damage the target.

## What if I find a self-referential junction (target == own path)

A self-referential junction resolves to itself, so the skill is functionally absent. To remediate:

1. **Snapshot** the junction metadata (path, target, reparse flag) to a track backup folder, e.g. `C:\development\opencode\.conductor\tracks\<track>\backups\<skill>-junction-snapshot\junction-metadata.json`.
2. **If a backup with `SKILL.md` exists** under `C:\development\opencode\.conductor\tracks\<source-track>\backups\` (or native), remove the broken junction with `cmd /c rmdir` and restore a real folder from that backup (copy the backup's *children* into the new real folder, not the backup directory itself).
3. **Otherwise (no backup exists anywhere):** remove the junction with `cmd /c rmdir "<vault>\<skill>"` and document the skill as **not-restored** in `<track>\backups\skills-not-restored.md`. Do NOT create a replacement folder.

After remediation, re-scan the vault and confirm zero self-referential junctions remain.

## Quick diagnostic scan

```powershell
$vaultRoot = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
Get-ChildItem -LiteralPath $vaultRoot -Directory -Force |
  Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } |
  ForEach-Object {
    $t = (Get-Item -LiteralPath $_.FullName).Target
    if ($t -eq $_.FullName) { [pscustomobject]@{ Name=$_.Name; Path=$_.FullName; Target=$t; SELF_REFERENTIAL=$true } }
  }
```
