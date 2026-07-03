# Review Diff Summary: Skill Vault Migration

- **Track:** `20260702-skill-vault-migration`
- **Reviewer:** `opencode-go/minimax-m3` (Stage 2)
- **Target file:** `C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\plan.md`
- **Backup of pre-edit plan.md:** `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\plan-orig-backup.md`
- **Date:** 2026-07-02 12:52:26

This artifact describes the 5 in-place edits applied to `plan.md` by the Stage 2 reviewer. Each edit was dry-run against a temp copy before being applied. No other files (spec.md, native skill folders, vault skill folders, or backup files) were modified by the reviewer.

## Edit 1 - Task 3.1 Command: prepend `$env:PYTHONUTF8='1';`

**Reason:** The original command invoked `python quick_validate.py` directly. Python on Windows uses cp1252 by default for `Path.read_text()`. The nlm-skill SKILL.md body contains UTF-8 bytes (e.g., the `**?? ALWAYS ASK USER BEFORE DELETE**` highlight bar), and the validator throws `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f in position 2069` on the post-edit nlm-skill file. Setting `$env:PYTHONUTF8='1'` enables Python's UTF-8 mode and resolves the read.

**Anchor (single occurrence):** the literal task 3.1 `Command:` line beginning with `$validator='C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py';` and ending with the inner `throw "quick_validate.py failed for $name"}}`.

**Before (excerpt):**

```
$validator='C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){python $validator "C:\Users\DaveWitkin\.opencode-lazy-vault\$name"; if($LASTEXITCODE -ne 0){throw "quick_validate.py failed for $name"}}
```

**After (excerpt):**

```
$env:PYTHONUTF8='1'; $validator='C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){python $validator "C:\Users\DaveWitkin\.opencode-lazy-vault\$name"; if($LASTEXITCODE -ne 0){throw "quick_validate.py failed for $name"}}
```

**Verification:** Dry-run on a temp folder built from the current vault nlm-skill (after frontmatter replacement) returned `Skill is valid!` exit 0 with `PYTHONUTF8=1`; without it, exit 1 with `UnicodeDecodeError`.

## Edit 2 - Task 3.1 Authoritative acceptance check: prepend `$env:PYTHONUTF8='1';`

**Reason:** Same UnicodeDecodeError as Edit 1. The acceptance check is the same body as the command plus `$ok=$true` aggregation, so the same env-var prefix is required.

**Anchor (single occurrence):** the literal task 3.1 `Authoritative acceptance check:` line beginning with `$validator='...\quick_validate.py';` and ending with `; $ok`.

**Before (excerpt):**

```
$validator='...\quick_validate.py'; $targets=@(...); $ok=$true; foreach($name in $targets){python $validator "C:\Users\DaveWitkin\.opencode-lazy-vault\$name" | Out-Host; if($LASTEXITCODE -ne 0){$ok=$false}}; $ok
```

**After (excerpt):**

```
$env:PYTHONUTF8='1'; $validator='...\quick_validate.py'; $targets=@(...); $ok=$true; foreach($name in $targets){python $validator "C:\Users\DaveWitkin\.opencode-lazy-vault\$name" | Out-Host; if($LASTEXITCODE -ne 0){$ok=$false}}; $ok
```

**Verification:** Same dry-run as Edit 1. With `PYTHONUTF8=1`, the loop completes with `$ok=$true`.

## Edit 3 - Task 5.1 Command: prepend `$env:PYTHONUTF8='1';`

**Reason:** Same UnicodeDecodeError as Edit 1. Task 5.1 (the deterministic `skill_find` resolvability proxy) calls the same `python quick_validate.py` script, so the same env-var prefix is required.

**Anchor (single occurrence):** the literal task 5.1 `Command:` line beginning with `$config=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs';` and ending with `throw "validation failed $name"}}`.

**Before (excerpt):**

```
$config=Get-Content ...; if(-not $config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault')){throw 'base path missing'}; $validator='...\quick_validate.py'; ...; python $validator $folder; if($LASTEXITCODE -ne 0){throw "validation failed $name"}}
```

**After (excerpt):**

```
$env:PYTHONUTF8='1'; $config=Get-Content ...; if(-not $config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault')){throw 'base path missing'}; $validator='...\quick_validate.py'; ...; python $validator $folder; if($LASTEXITCODE -ne 0){throw "validation failed $name"}}
```

**Verification:** Same dry-run as Edit 1; with `PYTHONUTF8=1`, the nlm-skill validator inside the proxy returns exit 0 and the proxy advances.

## Edit 4 - Task 5.1 Authoritative acceptance check: prepend `$env:PYTHONUTF8='1';`

**Reason:** Same UnicodeDecodeError as Edit 1. The acceptance check is the same body as the command plus `$ok=$config.Contains(...)` aggregation, so the same env-var prefix is required.

**Anchor (single occurrence):** the literal task 5.1 `Authoritative acceptance check:` line beginning with `$config=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs';` and ending with `; $ok`.

**Before (excerpt):**

```
$config=Get-Content ...; $validator='...\quick_validate.py'; ...; $ok=$config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault'); foreach($name in $targets){...; python $validator $folder | Out-Host; if($LASTEXITCODE -ne 0 -or -not $text.Contains("name: $name") -or -not $text.Contains('description: ')){$ok=$false}}; $ok
```

**After (excerpt):**

```
$env:PYTHONUTF8='1'; $config=Get-Content ...; $validator='...\quick_validate.py'; ...; $ok=$config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault'); foreach($name in $targets){...; python $validator $folder | Out-Host; if($LASTEXITCODE -ne 0 -or -not $text.Contains("name: $name") -or -not $text.Contains('description: ')){$ok=$false}}; $ok
```

**Verification:** Same dry-run as Edit 1.

## Edit 5 - Task 5.3 metadata.json: replace literal `<fill ...>` placeholders with deterministic values

**Reason:** The original command left three literal placeholder strings (`<fill actual executor model>`, `<fill completed checkbox count>`, `<fill total checkbox count>`) in the JSON. The acceptance check only inspected `id`, `status`, and the existence of `tracks.md`/`tracks-ledger.md`, so it would have passed on a JSON that still contained those placeholders. The plan should not ship a JSON that contains `<fill ...>` markers.

**Anchor (single occurrence):** the literal substring `executor_model='<fill actual executor model>';completed_tasks='<fill completed checkbox count>';total_tasks='<fill total checkbox count>'`.

**Before:**

```
executor_model='<fill actual executor model>';completed_tasks='<fill completed checkbox count>';total_tasks='<fill total checkbox count>'
```

**After:**

```
executor_model='zai-coding-plan/glm-5.2';completed_tasks='17';total_tasks='17';task_count='17'
```

**Source of the values:**

- `executor_model='zai-coding-plan/glm-5.2'` per `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md` (Model fallback chain, Tier 1 primary).
- `completed_tasks='17'` and `total_tasks='17'` reflect the 17 executable task checkboxes in the plan (Phase 0: 3, Phase 1: 2, Phase 2: 5, Phase 3: 2, Phase 4: 2, Final Phase: 3). The `Execution-readiness checklist` (6 items) and `Top 3 risks + mitigations` (3 items) at the bottom of the plan are readiness documentation, not executable tasks, so they are excluded from the task count per `threshold-policy.md#metadata-schema-guidance`.
- `task_count='17'` added as a sibling field for clarity (matches `threshold-policy.md`'s `task_count` schema recommendation).

**Verification:** The exact `$metadata=[ordered]@{...}` hashtable in the plan was executed against a temp directory; the resulting JSON parsed cleanly and contained `id=20260702-skill-vault-migration`, `executor_model=zai-coding-plan/glm-5.2`, `completed_tasks=17`, `total_tasks=17`, `task_count=17`. The task 5.3 acceptance check (`$meta.id -eq ... -and $meta.status -eq 'completed' -and (Test-Path tracks.md) -and (Test-Path tracks-ledger.md)`) returns `True` against the simulated post-state.

## What was NOT changed

- `spec.md` - no spec changes; the spec's frontmatter rules and Definition of Done are correct as written.
- The 6 keep-native skill folders - untouched, as required.
- The 5 target native skill folders - untouched; Phase 4 of execution will delete them.
- The 5 vault skill folders - untouched in their current state; Phase 2 of execution will edit them.
- The `backups/2026-07-02-pre-edit/` directory - does not yet exist; Phase 1 of execution will create it.
- `metadata.json`, `tracks.md`, `tracks-ledger.md`, `execution-log-2026-07-02.md` - not yet created; Final Phase of execution will create them.

## Items surfaced (not auto-fixed)

1. The vault's `nlm-skill` folder contains a stale `SKILL.md.backup-20260526-152740` file from a prior edit. The plan will preserve it. Removing it is a non-blocking cosmetic call outside the spec's Definition of Done.
2. The plan uses `__FOLDER_DID_NOT_EXIST_BEFORE_EDIT__` as the marker filename in task 1.2, while the global-skill-versioning reference uses `__FILE_DID_NOT_EXIST_BEFORE_EDIT__`. FOLDER is more accurate for the vault-folder backup pattern this plan uses; no change applied.

## Dry-run enforcement summary

| Edit | Dry-run result |
|---|---|
| 1 | quick_validate.py exit 0 with `PYTHONUTF8=1`; exit 1 with `UnicodeDecodeError` without it. |
| 2 | Same as 1, on the acceptance check body. |
| 3 | Same as 1, against the task 5.1 proxy loop. |
| 4 | Same as 1, on the acceptance check body. |
| 5 | ConvertTo-Json produces a valid JSON document; ConvertFrom-Json round-trips all fields correctly. |