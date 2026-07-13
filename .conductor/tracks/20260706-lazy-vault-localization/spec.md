# Spec: Lazy Vault Localization

## Goal

Remove confusing OneDrive-backed runtime junctions from the active OpenCode/Codex lazy-vault surface and make the active vault easier to reason about:

```text
C:\Users\DaveWitkin\.opencode-lazy-vault\<skill>
```

should contain real local skill folders for normal lazy-loaded skills, while preserving the seven intentional always-on native bridges back to:

```text
C:\Users\DaveWitkin\.config\opencode\skill\<skill>
```

## Background

Current inventory on 2026-07-06:

- Total lazy-vault entries: 77
- Reparse/junction children: 70
- OneDrive-backed skill junctions: 63
- Native-backed always-on junctions: 7
- Real folders: 7 (`_archived_skills`, `.system`, `handoff-deep`, `handoff-quick`, `nlm-skill`, `pptx-to-pdf-converter`, `root-cause-analysis`)
- Broken junction targets: 0

Recent session history showed the OneDrive-backed layout was historical sync/backup plumbing. A later session created a private GitHub backup/share repo (`DaveW001/opencode-skills`) after discovering the lazy vault mostly points to `development-config`. That reduces the need for OneDrive as an active runtime backing store, but the repo backup must be verified before any destructive conversion.

## Scope

In scope:

- Convert healthy OneDrive-backed lazy-vault child junctions into real local folders under `C:\Users\DaveWitkin\.opencode-lazy-vault`.
- Preserve file contents, timestamps where practical, and validation evidence.
- Preserve existing native-backed always-on junctions.
- Leave `C:\Users\DaveWitkin\.codex\skills` as a parent junction to the lazy vault.
- Keep `.agents\skills` absent/archived.
- Update architecture docs after conversion.

Out of scope:

- Deleting the OneDrive source tree.
- Changing skill content intentionally.
- Changing the seven always-on native skills into lazy-only skills.
- Recreating `.agents\skills`.

## Current known surfaces

```text
C:\Users\DaveWitkin\.opencode-lazy-vault
C:\Users\DaveWitkin\.codex\skills -> C:\Users\DaveWitkin\.opencode-lazy-vault
C:\Users\DaveWitkin\.config\opencode\skill
C:\Users\DaveWitkin\.agents\archive\skills-20260706-144958
```

## Safety requirements

- Do not use `Remove-Item` on a junction. Remove child junctions with `cmd /c rmdir` only.
- Before converting a skill, confirm its target exists and has expected content.
- Snapshot junction metadata before any conversion.
- Copy source contents into a staging directory first.
- Verify staged folder has `SKILL.md` for active skills.
- Only after verification, remove the local junction and atomically move/copy the staged real folder into place.
- Do not touch the parent Codex junction.
- Stop on first failed validation.

## Acceptance criteria

- `C:\Users\DaveWitkin\.codex\skills` remains a parent junction to `C:\Users\DaveWitkin\.opencode-lazy-vault`.
- `.agents\skills` remains absent from the live location.
- All converted OneDrive-backed entries become local real folders, not reparse points.
- The seven native-backed always-on entries remain junctions to `C:\Users\DaveWitkin\.config\opencode\skill`.
- No self-referential junctions exist under the lazy vault.
- No broken junction targets exist under the lazy vault.
- For every converted active skill, `SKILL.md` remains accessible from both the vault path and the Codex alias path.
- A rollback folder with original junction metadata and copied content exists.
- `C:\development\opencode\docs\runbooks\codex-skill-architecture.md` is updated after completion.
