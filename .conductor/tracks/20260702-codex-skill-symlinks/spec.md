# Spec: Codex Skill Junction Layer

Track ID: 20260702-codex-skill-symlinks
Created: 2026-07-02
Stage: 1 - Plan Creation only
Creator model: openai/gpt-5.5 (low)

## Restated goal/outcome

Make `C:\Users\DaveWitkin\.codex\skills\` a thin junction layer that represents every user skill from the two canonical OpenCode stores:

- Lazy vault: `C:\Users\DaveWitkin\.opencode-lazy-vault\`
- Native always-on store: `C:\Users\DaveWitkin\.config\opencode\skill\`

The final state must use Windows junctions in `C:\Users\DaveWitkin\.codex\skills\`, not copied folders, and a weekly OpenCode Scheduler job must keep the layer synchronized.

## Scope

In scope:

0. Complete pending vault migrations for nlm-skill and pptx-to-pdf-converter: break vault-to-native junction, create real vault copy, fix frontmatter, delete native, repoint codex junction to vault.
1. Inventory `C:\Users\DaveWitkin\.codex\skills\`, `C:\Users\DaveWitkin\.opencode-lazy-vault\`, and `C:\Users\DaveWitkin\.config\opencode\skill\`.
2. Exclude `.system` and `_archived_skills` from skill representation.
3. Convert real duplicate Codex skill folders to junctions after timestamped backup and duplicate/content verification.
4. Create missing Codex junctions with `cmd /c mklink /j`.
5. Write an idempotent weekly PowerShell reconciliation script at `C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1`.
6. Register a weekly OpenCode Scheduler job JSON under global scope `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\opencode-global-7a3f9c2e1b84\jobs\codex-skill-junction-reconcile.json`.
7. Document the architecture in `C:\Users\DaveWitkin\.config\opencode\docs\CODEX-SKILL-JUNCTION-RUNBOOK.md` and annotate/supersede `C:\Users\DaveWitkin\.config\opencode\docs\SKILL-SYNC-SETUP.md`.
8. Record backups in `C:\development\opencode\.conductor\tracks\20260702-codex-skill-symlinks\backups\<date>-pre-edit\`.

## Constraints and non-goals

- This Stage 1 work writes only this `spec.md` and `plan.md`; it does not create junctions, move folders, register tasks, or edit global docs/scripts.
- Do not touch the content of the always-on native skills: `conductor`, `conductor-pipeline`, `osgrep`, `perplexity-search`, `git-push`, or `skill-discovery` except by pointing junctions at them; `nlm-skill` and `pptx-to-pdf-converter` are intentionally being migrated out of native into real vault folders before Codex is repointed to vault.
- Do not create Codex junctions for `.system` or `_archived_skills` unless the user later opts in.
- Do not rewrite `C:\development\marketing\scripts\skill-sync-monitor.ps1`; it is related but out of scope and likely stale.
- Do not trust the old plural `skills\` path in `C:\Users\DaveWitkin\.config\opencode\docs\SKILL-SYNC-SETUP.md`; annotate it as superseded for Codex.
- Use PowerShell-first execution through the bash tool. Every bash tool call must include an explicit timeout.
- Use `-LiteralPath` and quote Windows paths with double quotes.
- Avoid interactive commands and commands that can block indefinitely.

## Canonical source rules

- If a skill exists in both vault and native and the vault entry points to the native folder, the Codex junction must point directly at native.
- If a skill is vault-only, the Codex junction must point at the vault folder.
- If a skill is native-only, the Codex junction must point at native.
- If a skill exists in both vault and native as separate real folders, stop and record a conflict for human decision; do not silently choose.
- Existing valid non-canonical junctions may be reported but must not be destructively replaced without explicit backup/replacement logic and user acceptance.

## Verified facts to preserve

- `C:\Users\DaveWitkin\.codex\skills\` currently has 72 entries: 8 junctions and 64 real folders.
- Existing Codex junctions include 7 native skill junctions and `image-to-html-reconstruction` pointing to `C:\Users\DaveWitkin\.local\skills\html-demo-design`.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\` has 70 included skill folders: 8 junctions and 62 real folders, excluding `.system` and `_archived_skills`.
- `C:\Users\DaveWitkin\.config\opencode\skill\` has 8 native always-on folders.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill` is a junction pointing to `C:\Users\DaveWitkin\.config\opencode\skill\nlm-skill`.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter` is a junction pointing to `C:\Users\DaveWitkin\.config\opencode\skill\pptx-to-pdf-converter`.
- Junctions can be created without admin rights using `cmd /c mklink /j <link> <target>`.
- OpenCode Scheduler job files live under `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\<scopeId>\jobs\<slug>.json` and create Windows Scheduled Tasks named `opencode-job-<scopeId>-<slug>` under `\OpenCode\`.

## Definition of done for eventual execution

- `C:\Users\DaveWitkin\.codex\skills\` contains a valid junction for every included vault skill and every native skill, pointing at the canonical source.
- Real duplicate Codex folders have been converted to junctions with backups, or explicitly excepted in the report with a reason.
- No orphaned or dangling Codex skill junctions remain unreported.
- `C:\development\_shared-scripts\codex-skill-junction-reconcile.ps1` exists, supports dry-run and apply modes, is idempotent, logs every action, and writes a report.
- `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\opencode-global-7a3f9c2e1b84\jobs\codex-skill-junction-reconcile.json` exists and the corresponding task is Ready under `\OpenCode\`.
- Documentation exists and explains architecture, manual maintenance, job registration, report location, and stale legacy docs.
- Pre-change backups of converted Codex real folders exist under this track's `backups\<date>-pre-edit\` folder.




