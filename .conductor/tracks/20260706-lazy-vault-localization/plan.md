# Plan: Lazy Vault Localization

## Status

Planning only. Do not execute bulk conversion without explicit approval.

## Phase 0 - Confirm intent and quiet window

- [ ] Confirm user wants to convert all healthy OneDrive-backed lazy-vault child junctions into local real folders.
- [ ] Confirm whether OpenCode/Codex should be closed during conversion to avoid file locks or lazy-loader races.
- [ ] Confirm GitHub backup/share repo state (`DaveW001/opencode-skills`) is current enough to serve as independent recovery support.

## Phase 1 - Snapshot inventory

- [ ] Write a timestamped JSON inventory to this track with, for every lazy-vault child: name, path, is reparse, target, target exists, has `SKILL.md`, file count, and hash manifest where practical.
- [ ] Write a separate conversion candidate list containing only child junctions whose target is under:

  ```text
  C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault
  ```

- [ ] Exclude native-backed always-on junctions:

  ```text
  conductor
  conductor-pipeline
  git-push
  opencode-scheduler
  osgrep
  perplexity-search
  skill-discovery
  ```

## Phase 2 - Backup and staging

- [ ] Create a timestamped rollback root under this track, e.g.:

  ```text
  C:\development\opencode\.conductor\tracks\20260706-lazy-vault-localization\backups\<timestamp>
  ```

- [ ] For each candidate, save junction metadata before touching it.
- [ ] Copy the OneDrive target contents into a staging folder outside the vault.
- [ ] Create a hash/file-count manifest for source and staged copy.
- [ ] Verify active skill candidates have `SKILL.md` in staging.

## Phase 3 - Convert one pilot skill

- [ ] Pick one low-risk candidate skill.
- [ ] Remove the local vault child junction with `cmd /c rmdir`.
- [ ] Move the staged real folder into the vault child path.
- [ ] Verify:
  - [ ] Vault child is not a reparse point.
  - [ ] Vault child has `SKILL.md`.
  - [ ] Codex alias path has `SKILL.md`.
  - [ ] Hash/file-count manifest matches source.
- [ ] If pilot fails, restore from rollback and stop.

## Phase 4 - Batch conversion

- [ ] Convert remaining candidates in small batches.
- [ ] After each batch, run the same postchecks.
- [ ] Stop on first failed check.

## Phase 5 - Final validation

- [ ] Confirm `C:\Users\DaveWitkin\.codex\skills` is still a parent junction to the lazy vault.
- [ ] Confirm `.agents\skills` is absent.
- [ ] Confirm OneDrive-backed child junction count is zero, except any explicit documented exceptions.
- [ ] Confirm native-backed always-on junction count is seven.
- [ ] Confirm no self-referential junctions exist under the vault.
- [ ] Confirm no broken targets exist under the vault.
- [ ] Spot-check `skill_find` / `skill_use` behavior after OpenCode restart if needed.

## Phase 6 - Documentation

- [ ] Update `C:\development\opencode\docs\runbooks\codex-skill-architecture.md` from “do not create OneDrive-backed junctions by default” to “OneDrive-backed runtime junctions have been retired/localized” if conversion completes.
- [ ] Update `C:\development\opencode\docs\reports\skill-health-latest.md`.
- [ ] Record final inventory and rollback path.

## Rollback

For any converted skill:

1. Move the real local folder aside to a rollback quarantine path.
2. Recreate the original junction from saved metadata:

   ```cmd
   cmd /c mklink /j "<vault-child-path>" "<original-target>"
   ```

3. Verify `SKILL.md` from the vault path and Codex alias path.
