# Manual Codex Skill Junction Sync Validation Note - 2026-07-03

Status: weekly scheduling intentionally delayed.

## Decisions

- Do not register or enable a weekly scheduled job yet.
- Use `C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1` manually until the dry-run/apply/rollback flow has been reviewed and approved.
- The script is intentionally conservative: it creates missing junctions only with `-Apply`, reports existing real Codex folders as `real-folder-needs-manual-backup-convert`, and does not delete real folders automatically.
- Duplicate precedence is explicit in reports:
  - vault-only -> vault
  - native-only -> native
  - vault junction pointing to native -> native
  - vault real + native real -> conflict/manual required
- Exclusions are explicit: `.system` and `_archived_skills` are ignored.

## Current dry-run summary

Latest reviewed dry-run reported:

- 7 `ok-existing-junction`
- 63 `real-folder-needs-manual-backup-convert`
- 1 `would-create-junction`: `conductor-pipeline`
- 1 `would-repoint-junction`: `image-to-html-reconstruction` currently points to `C:\Users\DaveWitkin\.local\skills\html-demo-design`, while the canonical report target is `C:\Users\DaveWitkin\.opencode-lazy-vault\image-to-html-reconstruction`.

## Validation performed

- Created a temporary smoke-test skill target and a temporary junction under `C:\Users\DaveWitkin\.codex\skills\codex-junction-smoke-test`.
- Verified `SKILL.md` was visible through the junction.
- Removed the smoke-test junction with `cmd /c rmdir` and removed the temporary target.
- Tested script `-Apply` and `-Rollback` against isolated temporary roots under `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\codex-sync-test`; the created junction was visible and rollback removed it.

## Next manual approval gates

Before touching the real `C:\Users\DaveWitkin\.codex\skills` entries:

1. Review the latest JSON report in `C:\Users\DaveWitkin\.config\opencode\reports\codex-skill-junctions`.
2. Decide whether `image-to-html-reconstruction` should continue pointing at `C:\Users\DaveWitkin\.local\skills\html-demo-design` or be repointed to the vault target.
3. Back up any real Codex folder before converting it to a junction.
4. Use `cmd /c rmdir` to remove junctions, never PowerShell `Remove-Item`, when breaking links.
