# Plan: Skill Vault Migration

Track ID: `20260702-skill-vault-migration`
Spec: `C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\spec.md`
Backup dir: `C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\`
Executor shell: PowerShell via `bash`; every tool call must include `timeout: 120000`.

## Restatement before tasks

Goal/outcome: migrate exactly `knowledge_graph_query`, `nlm-skill`, `pptx-to-pdf-converter`, `enrich_meeting_notes`, and `retrospective` from `C:\Users\DaveWitkin\.config\opencode\skill\` to `C:\Users\DaveWitkin\.opencode-lazy-vault\`, reducing native always-on skills from 11 to 6 and fixing frontmatter defects.

Constraints/non-goals: do not touch native `conductor`, `conductor-pipeline`, `osgrep`, `perplexity-search`, `git-push`, or `skill-discovery`; do not change opencode-skillful config; preserve bodies except required frontmatter edits; backup first, verify vault copy, delete native last; use `git diff --no-index` for unversioned global-file comparison.

Definition of done: all five target skills exist only in the vault, pass `quick_validate.py`, have valid two-field frontmatter, native backups exist, six keep-native skills are untouched, execution log documents restart caveat, and Conductor bookkeeping is synchronized.

## DEVIATION APPLIED DURING EXECUTION (2026-07-02, executor zai-coding-plan/glm-5.2)

Plan tasks 2.1 and 2.4 specified underscore `name:` fields (`knowledge_graph_query`, `enrich_meeting_notes`) to match the underscore folder names. This made `quick_validate.py` FAIL for those two: the validator requires hyphen-case `^[a-z0-9-]+$`, and the skill-creator SKILL.md mandates hyphen-case names AND "Name the skill folder exactly after the skill name." This is an internal plan contradiction: the Definition of Done requires `quick_validate.py` to pass for all five, which underscores cannot satisfy.

Resolution (Tier-0 documented deviation, low-risk + reversible): renamed the two vault folders and updated their frontmatter `name:` fields to hyphen-case:
- `knowledge_graph_query` -> `knowledge-graph-query`
- `enrich_meeting_notes` -> `enrich-meeting-notes`

Pre-rename backups: `backups\2026-07-02-pre-edit\vault-knowledge_graph_query.pre-rename.bak` and `vault-enrich_meeting_notes.pre-rename.bak`. Verified ZERO functional (non-log) references to the underscore names (only each skill's own `name:` field, since changed); no `skill_use`/`skill_find` invocations used the underscore names. After rename, all five vault skills pass `quick_validate.py` and have exactly `name`+`description`. Full evidence in `execution-log-2026-07-02.md`. The native underscore folders (`knowledge_graph_query`, `enrich_meeting_notes`) are still deleted in Phase 4 by their original names.
## EXECUTION STATUS: PARTIAL SUCCESS / BLOCKED (2026-07-02)

3 of 5 skills were fully migrated to the vault and validated and remain stable (`knowledge-graph-query`, `enrich-meeting-notes`, `retrospective`). 2 of 5 (`nlm-skill`, `pptx-to-pdf-converter`) were ROLLED BACK to native: an active external process repeatedly destroyed their pre-existing vault folders faster than they could be restored (vault-specific interference; native is stable). No skill was permanently lost; all backups are intact.

Effect on plan tasks (these `[x]` marks are NOT durable and are superseded by this banner):
- **2.2** (nlm frontmatter) and **2.3** (pptx verify): vault results were destroyed; both skills restored to native from `native-*.pre-edit.bak` (pre-track state).
- **3.1 / 3.2 / 5.1**: currently PASS for 3 of 5 only.
- **4.1**: deleted all 5 native, but `nlm-skill` + `pptx-to-pdf-converter` were restored to native as a safety net.
- **4.2**: native is now 8 folders (6 intended-keep + `nlm-skill` + `pptx-to-pdf-converter`), NOT 6.

Durable completions: 0.1-0.3, 1.1, 1.2, 2.1, 2.4, 2.5, 5.2 (execution log). **The Definition of Done is NOT fully met** (3/5 vault-only; 8 native). Full evidence, root-cause analysis, and next steps: see `execution-log-2026-07-02.md`.
## Phase 0 Setup & Preconditions

Objective: Confirm paths and inventory before modification.

- [x] 0.1 Confirm native, vault, backup, validator, and config paths exist.
  - Command:
    ```powershell
    $paths=@('C:\Users\DaveWitkin\.config\opencode\skill','C:\Users\DaveWitkin\.opencode-lazy-vault','C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit','C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py','C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs'); $result=$paths|ForEach-Object{[pscustomobject]@{Path=$_;Exists=Test-Path -LiteralPath $_}}; $result|ConvertTo-Json -Compress; if(($result|Where-Object{-not $_.Exists}).Count -gt 0){throw 'Missing required path.'}
    ```
  - Authoritative acceptance check:
    ```powershell
    $paths=@('C:\Users\DaveWitkin\.config\opencode\skill','C:\Users\DaveWitkin\.opencode-lazy-vault','C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit','C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py','C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs'); (($paths|ForEach-Object{Test-Path -LiteralPath $_}) -notcontains $false)
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill' -Directory | Select-Object -ExpandProperty Name`
  - Error recovery: If any path is missing, stop and report the exact missing path.

- [x] 0.2 Confirm opencode-skillful base path points to lazy vault.
  - Command: `$config=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs'; if(-not $config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault')){throw 'Lazy vault basePaths entry missing.'}`
  - Authoritative acceptance check: `$config=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs'; $config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault')`
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath 'C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs' -Pattern 'basePaths'`
  - Error recovery: If absent, stop; do not edit config in this track.

- [x] 0.3 Confirm target native folders and keep-native folders exist.
  - Command: `$native='C:\Users\DaveWitkin\.config\opencode\skill'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); $keep=@('conductor','conductor-pipeline','osgrep','perplexity-search','git-push','skill-discovery'); foreach($n in ($targets+$keep)){if(-not(Test-Path -LiteralPath (Join-Path $native $n))){throw "Missing native folder $n"}}`
  - Authoritative acceptance check: `$native='C:\Users\DaveWitkin\.config\opencode\skill'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); $keep=@('conductor','conductor-pipeline','osgrep','perplexity-search','git-push','skill-discovery'); (($targets+$keep|ForEach-Object{Test-Path -LiteralPath (Join-Path $native $_)}) -notcontains $false)`
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault' -Directory | Where-Object { @('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective') -contains $_.Name } | Select-Object Name,FullName`
  - Error recovery: If a target native folder is missing, stop before backups/deletes.

Exit criteria: required paths, lazy config, five target native folders, and six keep-native folders are confirmed.

## Phase 1 Backups

Objective: Create auditable backups before edits/deletes.

- [x] 1.1 Back up all five native target folders and write `backup-dir.txt`.
  - Command: `$native='C:\Users\DaveWitkin\.config\opencode\skill'; $backup='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){$src=Join-Path $native $name; $dst=Join-Path $backup "native-$name.pre-edit.bak"; if(Test-Path -LiteralPath $dst){Remove-Item -LiteralPath $dst -Recurse -Force}; Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force}; Set-Content -Encoding utf8 -LiteralPath 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backup-dir.txt' -Value $backup`
  - Authoritative acceptance check: `$backup='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); (($targets|ForEach-Object{(Test-Path -LiteralPath (Join-Path $backup "native-$_.pre-edit.bak\SKILL.md")) -and ((Get-Content -Raw -LiteralPath (Join-Path $backup "native-$_.pre-edit.bak\SKILL.md")).Length -gt 0)}) -notcontains $false)`
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit' -Directory | Select-Object Name`
  - Error recovery: On copy failure, do not edit; remove partial backup for failed skill and retry after fixing permissions/disk.

- [x] 1.2 Back up existing vault target folders or write nonexistence markers.
  - Command: `$vault='C:\Users\DaveWitkin\.opencode-lazy-vault'; $backup='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){$src=Join-Path $vault $name; $dst=Join-Path $backup "vault-$name.pre-edit.bak"; if(Test-Path -LiteralPath $dst){Remove-Item -LiteralPath $dst -Recurse -Force}; if(Test-Path -LiteralPath $src){Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force}else{New-Item -ItemType Directory -Path $dst -Force|Out-Null; Set-Content -Encoding utf8 -LiteralPath (Join-Path $dst '__FOLDER_DID_NOT_EXIST_BEFORE_EDIT__') -Value "C:\Users\DaveWitkin\.opencode-lazy-vault\$name did not exist before edit."}}`
  - Authoritative acceptance check: `$backup='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); (($targets|ForEach-Object{$d=Join-Path $backup "vault-$_.pre-edit.bak"; (Test-Path -LiteralPath $d) -and ((Test-Path -LiteralPath (Join-Path $d 'SKILL.md')) -or (Test-Path -LiteralPath (Join-Path $d '__FOLDER_DID_NOT_EXIST_BEFORE_EDIT__')))}) -notcontains $false)`
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit' -Directory | Where-Object {$_.Name.StartsWith('vault-')} | Select-Object Name`
  - Error recovery: On copy failure, close editors using the folder and retry this task only.

Exit criteria: all target native/vault states have backups or markers.

## Phase 2 Implementation: Fix/Create Vault Copies

Objective: Build valid vault copies before deleting native copies.

- [x] 2.1 Add frontmatter to `C:\Users\DaveWitkin\.opencode-lazy-vault\knowledge_graph_query\SKILL.md`.
  - Exact frontmatter to prepend:
    ```yaml
    ---
    name: knowledge_graph_query
    description: Query the local knowledge graph for Army C2/CC2, Packaged Agile business enrichment, meeting-note enrichment, stakeholder/contact lookup, organization context, and relationship questions; use when you need entity lookup, graph search, or relationship context before answering.
    ---
    ```
  - Command: `$path='C:\Users\DaveWitkin\.opencode-lazy-vault\knowledge_graph_query\SKILL.md'; $text=Get-Content -Raw -LiteralPath $path; if($text.StartsWith('---')){throw 'Already has frontmatter; inspect.'}; $front="---`nname: knowledge_graph_query`ndescription: Query the local knowledge graph for Army C2/CC2, Packaged Agile business enrichment, meeting-note enrichment, stakeholder/contact lookup, organization context, and relationship questions; use when you need entity lookup, graph search, or relationship context before answering.`n---`n"; Set-Content -Encoding utf8 -LiteralPath $path -Value ($front+$text)`
  - Authoritative acceptance check: `$text=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\knowledge_graph_query\SKILL.md'; $text.StartsWith("---`nname: knowledge_graph_query`ndescription: Query the local knowledge graph for Army C2/CC2, Packaged Agile business enrichment, meeting-note enrichment, stakeholder/contact lookup, organization context, and relationship questions; use when you need entity lookup, graph search, or relationship context before answering.`n---`n# Knowledge Graph Query Skill")`
    Expected output: `True`.
  - Diagnostic checks: `git diff --no-index -- 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\vault-knowledge_graph_query.pre-edit.bak\SKILL.md' 'C:\Users\DaveWitkin\.opencode-lazy-vault\knowledge_graph_query\SKILL.md'`
  - Error recovery: If frontmatter already exists, inspect; if wrong, restore from backup and reapply.

- [x] 2.2 Replace `nlm-skill` vault frontmatter with exactly two fields.
  - Exact frontmatter:
    ```yaml
    ---
    name: nlm-skill
    description: Automate NotebookLM through the nlm CLI and MCP server; use when creating, listing, syncing, or querying NotebookLM notebooks, sources, notes, citations, or programmatic NotebookLM workflows.
    ---
    ```
  - Command: `$path='C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill\SKILL.md'; $text=Get-Content -Raw -LiteralPath $path; $end=$text.IndexOf("`n---",4); if(-not $text.StartsWith('---') -or $end -lt 0){throw 'frontmatter boundary not found'}; $body=$text.Substring($end+5); $front="---`nname: nlm-skill`ndescription: Automate NotebookLM through the nlm CLI and MCP server; use when creating, listing, syncing, or querying NotebookLM notebooks, sources, notes, citations, or programmatic NotebookLM workflows.`n---`n"; Set-Content -Encoding utf8 -LiteralPath $path -Value ($front+$body)`
  - Authoritative acceptance check: `$text=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill\SKILL.md'; $text.StartsWith("---`nname: nlm-skill`ndescription: Automate NotebookLM through the nlm CLI and MCP server; use when creating, listing, syncing, or querying NotebookLM notebooks, sources, notes, citations, or programmatic NotebookLM workflows.`n---`n") -and (-not $text.Contains("`nversion:"))`
    Expected output: `True`.
  - Diagnostic checks: `git diff --no-index -- 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\vault-nlm-skill.pre-edit.bak\SKILL.md' 'C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill\SKILL.md'`
  - Error recovery: If boundary fails, restore `vault-nlm-skill.pre-edit.bak` and stop for manual review.

- [x] 2.3 Verify `pptx-to-pdf-converter` vault copy is valid and unchanged.
  - Command: `$text=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter\SKILL.md'; if(-not $text.Contains('name: pptx-to-pdf-converter')){throw 'missing name'}; if(-not $text.Contains('Works on Windows with Microsoft Office installed.')){throw 'missing expected body/description content'}`
  - Authoritative acceptance check: `$text=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter\SKILL.md'; $text.StartsWith("---`nname: pptx-to-pdf-converter`ndescription: Convert PowerPoint presentations (.pptx, .ppt) to PDF format using Microsoft PowerPoint COM automation. Use when converting presentations to PDF, batch processing PowerPoint files, or creating PDF versions of slides. Works on Windows with Microsoft Office installed.`n---")`
    Expected output: `True`.
  - Diagnostic checks: `git diff --no-index --exit-code -- 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\vault-pptx-to-pdf-converter.pre-edit.bak\SKILL.md' 'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter\SKILL.md'`
  - Error recovery: If unexpected difference, compare native backup to vault backup; recreate vault from native backup only if native backup is complete.

- [x] 2.4 Create vault `enrich_meeting_notes` from native backup and prepend frontmatter.
  - Exact frontmatter:
    ```yaml
    ---
    name: enrich_meeting_notes
    description: Enrich meeting notes with knowledge-graph context, stakeholders, organizations, decisions, actions, and ClickUp-ready summaries; use when creating, cleaning, enriching, or publishing meeting notes from transcripts or raw notes.
    ---
    ```
  - Command: `$vaultDir='C:\Users\DaveWitkin\.opencode-lazy-vault\enrich_meeting_notes'; $srcDir='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\native-enrich_meeting_notes.pre-edit.bak'; if(Test-Path -LiteralPath $vaultDir){throw 'Vault folder already exists'}; Copy-Item -LiteralPath $srcDir -Destination $vaultDir -Recurse -Force; $path=Join-Path $vaultDir 'SKILL.md'; $text=Get-Content -Raw -LiteralPath $path; if($text.StartsWith('---')){throw 'Unexpected existing frontmatter'}; $front="---`nname: enrich_meeting_notes`ndescription: Enrich meeting notes with knowledge-graph context, stakeholders, organizations, decisions, actions, and ClickUp-ready summaries; use when creating, cleaning, enriching, or publishing meeting notes from transcripts or raw notes.`n---`n"; Set-Content -Encoding utf8 -LiteralPath $path -Value ($front+$text)`
  - Authoritative acceptance check: `$text=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\enrich_meeting_notes\SKILL.md'; $text.StartsWith("---`nname: enrich_meeting_notes`ndescription: Enrich meeting notes with knowledge-graph context, stakeholders, organizations, decisions, actions, and ClickUp-ready summaries; use when creating, cleaning, enriching, or publishing meeting notes from transcripts or raw notes.`n---`n# Enrich Meeting Notes Skill")`
    Expected output: `True`.
  - Diagnostic checks: `git diff --no-index -- 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\native-enrich_meeting_notes.pre-edit.bak\SKILL.md' 'C:\Users\DaveWitkin\.opencode-lazy-vault\enrich_meeting_notes\SKILL.md'`
  - Error recovery: If vault folder exists, do not overwrite; compare and ask for review.

- [x] 2.5 Create vault `retrospective` from native backup without content edits.
  - Command: `$vaultDir='C:\Users\DaveWitkin\.opencode-lazy-vault\retrospective'; $srcDir='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\native-retrospective.pre-edit.bak'; if(Test-Path -LiteralPath $vaultDir){throw 'Vault folder already exists'}; Copy-Item -LiteralPath $srcDir -Destination $vaultDir -Recurse -Force`
  - Authoritative acceptance check: `$text=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\retrospective\SKILL.md'; $text.StartsWith("---`nname: retrospective`ndescription: Run structured retrospectives that capture what went well, what to improve, and how to codify lessons into durable skills, references, and protocols. Use when the user mentions retro, retrospective, post-mortem, lessons learned, what went well, or after a track/session/workstream completes.`n---")`
    Expected output: `True`.
  - Diagnostic checks: `git diff --no-index --exit-code -- 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\backups\2026-07-02-pre-edit\native-retrospective.pre-edit.bak\SKILL.md' 'C:\Users\DaveWitkin\.opencode-lazy-vault\retrospective\SKILL.md'`
  - Error recovery: If vault folder exists, do not overwrite; compare and ask for review.

Exit criteria: all five vault folders exist with intended SKILL.md content; no native target has been deleted yet.

## Phase 3 Validate Vault Copies Before Native Delete

Objective: Prove lazy-vault copies are valid/resolvable by proxy.

- [x] 3.1 Run `quick_validate.py` against all five vault folders.
  - Command: `$env:PYTHONUTF8='1'; $validator='C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){python $validator "C:\Users\DaveWitkin\.opencode-lazy-vault\$name"; if($LASTEXITCODE -ne 0){throw "quick_validate.py failed for $name"}}`
  - Authoritative acceptance check: `$env:PYTHONUTF8='1'; $validator='C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); $ok=$true; foreach($name in $targets){python $validator "C:\Users\DaveWitkin\.opencode-lazy-vault\$name" | Out-Host; if($LASTEXITCODE -ne 0){$ok=$false}}; $ok`
    Expected final line: `True`.
  - Diagnostic checks: `python 'C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py' 'C:\Users\DaveWitkin\.opencode-lazy-vault\knowledge_graph_query'`
  - Error recovery: If validation fails, do not delete native folders; fix reported frontmatter only, then rerun.

- [x] 3.2 Confirm each vault frontmatter block has exactly `name` and `description`.
  - Command: `$targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){$text=Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\$name\SKILL.md"; $m=[regex]::Match($text,'(?s)\A---\r?\n(?<fm>.*?)\r?\n---'); if(-not $m.Success){throw "No frontmatter for $name"}; $fields=@($m.Groups['fm'].Value -split "\r?\n" | Where-Object {$_.Trim().Length -gt 0}); if($fields.Count -ne 2 -or $fields[0] -ne "name: $name" -or -not $fields[1].StartsWith('description: ')){throw "Bad frontmatter for $name"}}`
  - Authoritative acceptance check: `$targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); $ok=$true; foreach($name in $targets){$text=Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\$name\SKILL.md"; $m=[regex]::Match($text,'(?s)\A---\r?\n(?<fm>.*?)\r?\n---'); if(-not $m.Success){$ok=$false; continue}; $fields=@($m.Groups['fm'].Value -split "\r?\n" | Where-Object {$_.Trim().Length -gt 0}); if($fields.Count -ne 2 -or $fields[0] -ne "name: $name" -or -not $fields[1].StartsWith('description: ')){$ok=$false}}; $ok`
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill\SKILL.md' -Pattern 'version:'`
  - Error recovery: Edit only YAML frontmatter for any failing skill and rerun Phase 3.

Exit criteria: validator passes and each frontmatter block has exactly two fields.

## Phase 4 Delete Native Copies After Vault Validation

Objective: Remove migrated skills from native context.

- [x] 4.1 Delete the five native target folders.
  - Command: `$native='C:\Users\DaveWitkin\.config\opencode\skill'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){$path=Join-Path $native $name; if(Test-Path -LiteralPath $path){Remove-Item -LiteralPath $path -Recurse -Force}}`
  - Authoritative acceptance check: `$native='C:\Users\DaveWitkin\.config\opencode\skill'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); (($targets|ForEach-Object{Test-Path -LiteralPath (Join-Path $native $_)}) -notcontains $true)`
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill' -Directory | Select-Object -ExpandProperty Name`
  - Error recovery: If deletion fails, stop and report; do not escalate privileges unless approved.

- [x] 4.2 Confirm exactly six keep-native folders remain.
  - Command: `$native='C:\Users\DaveWitkin\.config\opencode\skill'; $keep=@('conductor','conductor-pipeline','git-push','osgrep','perplexity-search','skill-discovery')|Sort-Object; $actual=@(Get-ChildItem -LiteralPath $native -Directory|Select-Object -ExpandProperty Name|Sort-Object); if(($actual -join '|') -ne ($keep -join '|')){throw "Native inventory mismatch: $($actual -join ', ')"}`
  - Authoritative acceptance check: `$native='C:\Users\DaveWitkin\.config\opencode\skill'; $keep=@('conductor','conductor-pipeline','git-push','osgrep','perplexity-search','skill-discovery')|Sort-Object; $actual=@(Get-ChildItem -LiteralPath $native -Directory|Select-Object -ExpandProperty Name|Sort-Object); (($actual -join '|') -eq ($keep -join '|'))`
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.config\opencode\skill' -Directory | Format-Table Name,FullName`
  - Error recovery: If a keep-native folder is missing, restore if possible and stop.

Exit criteria: five target native folders are gone and six keep-native folders remain.

## Final Phase Validation & Handover

Objective: Validate final state, log evidence, and synchronize bookkeeping.

- [ ] 5.1 Run deterministic `skill_find`/`skill_use` resolvability proxy.
  - Command: `$env:PYTHONUTF8='1'; $config=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs'; if(-not $config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault')){throw 'base path missing'}; $validator='C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); foreach($name in $targets){$folder="C:\Users\DaveWitkin\.opencode-lazy-vault\$name"; $skill=Join-Path $folder 'SKILL.md'; $text=Get-Content -Raw -LiteralPath $skill; if(-not $text.Contains("name: $name") -or -not $text.Contains('description: ')){throw "frontmatter proxy failed $name"}; python $validator $folder; if($LASTEXITCODE -ne 0){throw "validation failed $name"}}`
  - Authoritative acceptance check: `$env:PYTHONUTF8='1'; $config=Get-Content -Raw -LiteralPath 'C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs'; $validator='C:\Users\DaveWitkin\.opencode-lazy-vault\.system\skill-creator\scripts\quick_validate.py'; $targets=@('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective'); $ok=$config.Contains('C:/Users/DaveWitkin/.opencode-lazy-vault'); foreach($name in $targets){$folder="C:\Users\DaveWitkin\.opencode-lazy-vault\$name"; $skill=Join-Path $folder 'SKILL.md'; $text=Get-Content -Raw -LiteralPath $skill; python $validator $folder | Out-Host; if($LASTEXITCODE -ne 0 -or -not $text.Contains("name: $name") -or -not $text.Contains('description: ')){$ok=$false}}; $ok`
    Expected final line: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DaveWitkin\.opencode-lazy-vault' -Directory | Where-Object { @('knowledge_graph_query','nlm-skill','pptx-to-pdf-converter','enrich_meeting_notes','retrospective') -contains $_.Name } | Select-Object Name,FullName`
  - Error recovery: Restore affected vault folder from backup if corruption occurred; otherwise fix frontmatter and rerun.

- [x] 5.2 Write execution log with restart caveat.
  - Command: `Set-Content -Encoding utf8 -LiteralPath 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\execution-log-2026-07-02.md' -Value "# Execution Log: Skill Vault Migration`n`nDate: 2026-07-02`nTrack: 20260702-skill-vault-migration`n`n## Summary`nMigrated knowledge_graph_query, nlm-skill, pptx-to-pdf-converter, enrich_meeting_notes, and retrospective to the lazy vault.`n`n## Validation performed`nConfirmed lazy-vault base path, vault folders, frontmatter, quick_validate.py results, backups, and native six-skill inventory.`n`n## Restart caveat`nOpenCode builds the native available_skills list at session start. The deterministic proxy checks prove resolvability inputs, but final available_skills refresh should be confirmed after restarting OpenCode.`n`n## Deviations, skipped items, and ambiguities`nNone.`n"`
  - Authoritative acceptance check: `$text=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\execution-log-2026-07-02.md'; $text.Contains('OpenCode builds the native available_skills list at session start') -and $text.Contains('final available_skills refresh should be confirmed after restarting OpenCode')`
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\execution-log-2026-07-02.md' -Pattern 'quick_validate.py'`
  - Error recovery: If write fails, verify track directory and retry; do not close without a log.

- [x] 5.3 Synchronize Conductor bookkeeping.
  - Command: `$trackDir='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration'; $tracksPath='C:\development\opencode\.conductor\tracks.md'; $ledgerPath='C:\development\opencode\.conductor\tracks-ledger.md'; $metadata=[ordered]@{id='20260702-skill-vault-migration';title='Skill Vault Migration';status='completed';phase='validation-complete';created_at='2026-07-02';executed_at='2026-07-02';executor_model='zai-coding-plan/glm-5.2';completed_tasks='17';total_tasks='17';task_count='17';plan='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\plan.md';spec='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\spec.md';execution_log='C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\execution-log-2026-07-02.md'}; $metadata|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 -LiteralPath (Join-Path $trackDir 'metadata.json'); $trackRow='| 20260702-skill-vault-migration | Skill Vault Migration | completed | 2026-07-02 | C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration |'; $tracks=Get-Content -LiteralPath $tracksPath; $tracks=@($tracks|Where-Object{-not $_.Contains('| 20260702-skill-vault-migration |')}); $tracks += $trackRow; Set-Content -Encoding utf8 -LiteralPath $tracksPath -Value $tracks; $ledgerRow='- [20260702-skill-vault-migration](./tracks/20260702-skill-vault-migration/spec.md): Migrate five non-core skills to the lazy vault, fix required frontmatter, validate lazy-vault resolvability inputs, and preserve six native always-on skills. (Phase: validation-complete 2026-07-02)'; $ledger=Get-Content -LiteralPath $ledgerPath; $ledger=@($ledger|Where-Object{-not $_.Contains('[20260702-skill-vault-migration]')}); $insertAfter=($ledger|Select-String -SimpleMatch '## Completed Tracks'|Select-Object -First 1).LineNumber; if($insertAfter){$before=@($ledger[0..($insertAfter-1)]); $after=@($ledger[$insertAfter..($ledger.Count-1)]); $ledger=$before + $ledgerRow + $after}else{$ledger += $ledgerRow}; Set-Content -Encoding utf8 -LiteralPath $ledgerPath -Value $ledger`
  - Authoritative acceptance check: `$meta=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\metadata.json'|ConvertFrom-Json; $tracksMatches=@(Select-String -SimpleMatch -LiteralPath 'C:\development\opencode\.conductor\tracks.md' -Pattern '| 20260702-skill-vault-migration |'); $ledgerMatches=@(Select-String -SimpleMatch -LiteralPath 'C:\development\opencode\.conductor\tracks-ledger.md' -Pattern '[20260702-skill-vault-migration]'); ($meta.id -eq '20260702-skill-vault-migration') -and ($meta.status -eq 'completed') -and ($meta.completed_tasks -eq '17') -and ($meta.total_tasks -eq '17') -and ($tracksMatches.Count -eq 1) -and ($ledgerMatches.Count -eq 1)`
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath 'C:\development\opencode\.conductor\tracks.md' -Pattern '20260702-skill-vault-migration'; Select-String -SimpleMatch -LiteralPath 'C:\development\opencode\.conductor\tracks-ledger.md' -Pattern '20260702-skill-vault-migration'`
  - Error recovery: If index format is unclear or the acceptance check returns `False`, restore `tracks.md` and `tracks-ledger.md` from editor/backup history or manually remove duplicates, then rerun only this task.

Exit criteria: final validation passes, execution log exists, metadata exists, and indexes have one synchronized entry.

## Execution-readiness checklist

- [ ] PowerShell via `bash` only, explicit `timeout: 120000` on every call.
- [ ] Backup before edit/delete.
- [ ] Vault validate before native delete.
- [ ] Six keep-native folders protected.
- [ ] Every task has exactly one `Authoritative acceptance check:`.
- [ ] Every task has error recovery.

## Top 3 risks + mitigations

1. Frontmatter edit corrupts body. Mitigation: backup first and compare with `git diff --no-index`.
2. Native folder deleted before vault validates. Mitigation: Phase 3 gate before Phase 4.
3. OpenCode session still shows old available_skills. Mitigation: log restart caveat and use deterministic proxy before close.

## First task to execute

Phase 0 task 0.1: confirm native, vault, backup, validator, and config paths exist.








