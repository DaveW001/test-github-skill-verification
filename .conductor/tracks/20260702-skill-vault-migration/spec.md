# Spec: Skill Vault Migration

Track ID: `20260702-skill-vault-migration`
Created: 2026-07-02
Stage: 1 - Plan Creation
Planner model: openai/gpt-5.5
Workspace root: `C:\development\opencode`
Track directory: `C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\`
Backup directory: `C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\`

## Tool/environment preflight

- Native Read/Edit/Write/glob/grep tools are considered broken for executor handoff because this environment reports `Bun is not defined`.
- Execute the entire track PowerShell-first via the `bash` tool.
- Every `bash` call must include an explicit timeout, for example `timeout: 120000`.
- Use PowerShell cmdlet mapping:
  - Read: `Get-Content -Raw -LiteralPath "<path>"`
  - Write: `Set-Content -Encoding utf8 -LiteralPath "<path>" -Value <content>`
  - Glob: `Get-ChildItem -Recurse -LiteralPath "<path>"`
  - Grep: `Select-String -SimpleMatch -LiteralPath "<path>" -Pattern "<literal>"`
- Always quote Windows paths with double quotes and use `-LiteralPath` for file paths.
- Do not run commands that can block indefinitely: no `Read-Host`, no `Pause`, no uncapped waits, no `tail -f`, no server/watch processes.
- PowerShell verification should prefer literal checks: `[string]::Contains()`, `Select-String -SimpleMatch`, `[regex]::Escape()`, or line-anchored full-line regex.

## Goal/outcome

Migrate exactly five skills out of the native always-on folder `C:\Users\DaveWitkin\.config\opencode\skill\` into the lazy-loaded vault `C:\Users\DaveWitkin\.opencode-lazy-vault\`, reducing always-on native skills from 11 to 6. Fix malformed or missing YAML frontmatter on migrated skills so each resolves through the opencode-skillful lazy-vault path and passes skill-creator best-practice validation.

Target skills to migrate:

1. `knowledge_graph_query`
2. `nlm-skill`
3. `pptx-to-pdf-converter`
4. `enrich_meeting_notes`
5. `retrospective`

## Constraints and non-goals

- Do not migrate, edit, rename, or delete these six native always-on skills: `conductor`, `conductor-pipeline`, `osgrep`, `perplexity-search`, `git-push`, `skill-discovery`.
- Do not change `C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs` except to read/verify it.
- Do not change the native skill folder location `C:\Users\DaveWitkin\.config\opencode\skill\`.
- Do not refactor SKILL.md bodies beyond frontmatter changes specified in the plan.
- Preserve `enrich_meeting_notes` and `retrospective` body content byte-for-byte when moving; only prepend frontmatter to `enrich_meeting_notes`.
- Do not delete any native folder until its vault copy is verified complete and backed up.
- Back up all five native folders before edits/deletes because global skills are unversioned.
- For files that already exist in the vault and will be edited, back up the vault file/folder before editing.

## Required frontmatter standards

Every migrated vault skill must have YAML frontmatter at the top of `SKILL.md` with exactly these two fields:

```yaml
---
name: <folder-name>
description: <what it does plus specific trigger contexts>
---
```

No additional YAML fields are allowed. In particular, remove `version:` from `nlm-skill`.

## Definition of done

- All five target skills exist only in `C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>\` and no native copies remain under `C:\Users\DaveWitkin\.config\opencode\skill\`.
- `knowledge_graph_query` and `enrich_meeting_notes` have valid frontmatter added.
- `nlm-skill` vault copy has no `version:` field and has an improved trigger-rich description.
- `pptx-to-pdf-converter` and `retrospective` remain valid and pass validation.
- `quick_validate.py` passes for all five vault skill folders.
- Backups of all five native folders exist in `C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\`.
- The six always-on skills remain present under the native folder and are untouched.
- `execution-log-2026-07-02.md` documents validation evidence and the OpenCode restart caveat for authoritative end-to-end available_skills refresh.
- Conductor bookkeeping (`metadata.json`, `.conductor\tracks.md`, `.conductor\tracks-ledger.md`, and checked-off `plan.md`) is synchronized by the executor during closeout.
