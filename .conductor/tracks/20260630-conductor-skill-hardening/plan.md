# Plan: Conductor Skill Hardening

Track ID: `20260630-conductor-skill-hardening`
Workspace root: `C:\development\opencode`

## Goal / Outcome
Harden the global `conductor-pipeline` skill using the remaining recommendations from `C:\development\opencode\.conductor\docs\conductor-pipeline-run-retro-2026-06-30.md`.

## Constraints / Non-Goals
- Target files are global files outside repo git history.
- Back up before every edit.
- Use PowerShell-first commands with `-LiteralPath` and quoted Windows paths.
- Verification must inspect body content, not headings or isolated phrases only.
- Do not execute this plan during Stage 1.
- **Body-writing rule (critical for backtick/bracket fidelity):** Whenever a task body contains literal backticks (`` ` ``), brackets, or dollar signs (e.g., `` `[string]::Replace()` ``, `` `task_count` ``, `` `$text.Replace(`$old,`$new) ``), the executor MUST write the body via a single-quoted PowerShell here-string (`@''...''@` ... `|''@`) or `[System.IO.File]::WriteAllText($path, $literal, [System.Text.Encoding]::UTF8)` with a literal `$literal` string. **Never** use a double-quoted here-string (`@"..."@`) or a double-quoted PowerShell string to hold a body that contains `` ` `` because `` `t `` becomes a tab, `` ` `` before `"` escapes the closing quote (parse error), and other backtick-escape bugs corrupt the file.
- **Body-content verification rule:** All body-content checks use single-quoted PowerShell strings with `[string]::Contains()` (literal substring matching) so backticks and brackets in patterns are not interpreted. `-notlike` is NOT used for body-content substring checks because `[` and `]` are wildcards in `-like` and the check would silently fail even when the body is correct.

## Definition of Done
`stage-prompts.md`, `threshold-policy.md`, `powershell-pitfalls.md`, and `global-skill-versioning.md` contain the required body guidance; backups exist; validation artifacts prove body content.

## Phase 0: Setup & Preconditions
Objective: Confirm inputs and create backups.

- [x] **Task 0.1 - Create track backup folder.**
  Command:
  ```powershell
  $TrackDir="C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening"; $RefDir="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references"; if(-not(Test-Path -LiteralPath $RefDir)){throw "Missing $RefDir"}; $BackupDir="$TrackDir\backups\$(Get-Date -Format 'yyyy-MM-dd-HHmmss')-pre-edit"; New-Item -ItemType Directory -Force -Path $BackupDir|Out-Null; Set-Content -Encoding utf8 -LiteralPath "$TrackDir\backup-dir.txt" -Value $BackupDir
  ```
  Authoritative acceptance check:
  ```powershell
  $b=(Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\backup-dir.txt").Trim(); if((Test-Path -LiteralPath $b) -and $b.Contains("20260630-conductor-skill-hardening\backups")){"backup folder body valid"}else{throw "bad backup folder"}
  ```
  Diagnostic checks: none.
  Error recovery: If the global references directory is missing, stop and ask for the correct skill path.

- [x] **Task 0.2 - Confirm retro body requirements.**
  Command:
  ```powershell
  $r=Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\docs\conductor-pipeline-run-retro-2026-06-30.md"; $terms=@('one authoritative acceptance check','dry-run every verification command','task_count','PowerShell pitfalls','global-skill versioning/backups'); foreach($t in $terms){if(-not $r.Contains($t)){throw "missing retro body: $t"}}; "retro body confirmed"
  ```
  Authoritative acceptance check: The command must print `retro body confirmed` after checking all five body terms.
  Diagnostic checks: none.
  Error recovery: If wording changed, manually inspect Codify/Reuse and What To Do Differently sections; do not weaken the intended requirements.

- [x] **Task 0.3 - Back up all four target files or nonexistence markers.**
  Command:
  ```powershell
  $b=(Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\backup-dir.txt").Trim(); $targets=@("stage-prompts.md","threshold-policy.md","powershell-pitfalls.md","global-skill-versioning.md"); foreach($n in $targets){$t="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\$n"; if(Test-Path -LiteralPath $t){Copy-Item -LiteralPath $t -Destination "$b\$n.pre-edit.bak" -Force}else{Set-Content -Encoding utf8 -LiteralPath "$b\$n.pre-edit.bak" -Value "__FILE_DID_NOT_EXIST_BEFORE_EDIT__"}}
  ```
  Authoritative acceptance check:
  ```powershell
  $b=(Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\backup-dir.txt").Trim(); @("stage-prompts.md","threshold-policy.md","powershell-pitfalls.md","global-skill-versioning.md")|%{$p="$b\$_.pre-edit.bak"; if(!(Test-Path -LiteralPath $p)){throw "missing backup $p"}; if([string]::IsNullOrWhiteSpace((Get-Content -Raw -LiteralPath $p))){throw "empty backup $p"}}; "backup bodies valid"
  ```
  Diagnostic checks: `Get-Item -LiteralPath "$b\stage-prompts.md.pre-edit.bak"`.
  Error recovery: If copying fails, stop before edits and fix permissions.

Exit criteria: backup folder and four backup files exist.

## Phase 1: Stage Prompt Hardening
Objective: Add requirements inside prompt blocks.

- [x] **Task 1.1 - Insert Stage 1 plan-authoring hardening.**
  Command: Edit `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md` inside the Stage 1 fenced prompt block after verification standard with this body:
  ```text
- Each task must name exactly ONE authoritative acceptance check: the single check that proves the task succeeded. Label it exactly `Authoritative acceptance check:`.
- Diagnostic/convenience/supporting commands must be separated under `Diagnostic checks:` and must not be counted as proof.
- Verification must inspect intended BODY CONTENT, not just heading existence or isolated phrase presence. Reject heading-only or phrase-only checks that can pass when intended body text is absent.
- For Windows paths and literal content, prefer `Select-String -SimpleMatch`, `[regex]::Escape()`, or line-anchored full-line patterns over ad hoc regex construction.
  ```
  Authoritative acceptance check:
  ```powershell
  # NOTE: Use single-quoted patterns and .Contains() to avoid -like wildcard interpretation of [ and ].
  $p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Stage 1 - Plan Creation"); $e=$t.IndexOf("## Stage 2 / 3",$s); if($s -lt 0 -or $e -lt 0){throw "Stage 1 anchors not found"}; $b=$t.Substring($s,$e-$s); $required=@('exactly ONE authoritative acceptance check','Diagnostic checks:','BODY CONTENT','Reject heading-only or phrase-only checks','Select-String -SimpleMatch','[regex]::Escape()'); foreach($r in $required){if(-not $b.Contains($r)){throw "Stage 1 body missing: $r"}}; "Stage 1 hardening body valid"
  ```
  Diagnostic checks: `Select-String -LiteralPath "...\stage-prompts.md" -SimpleMatch "exactly ONE authoritative acceptance check"`.
  Error recovery: If anchors fail, manually locate the Stage 1 fenced prompt; do not append outside the block.

- [x] **Task 1.2 - Insert Stage 2 reviewer dry-run enforcement.**
  Command: Edit the Stage 2/3 fenced prompt block after the anti-laziness paragraph with this body:
  ```text
Reviewer dry-run enforcement: You must dry-run EVERY verification command you add or modify, not just commands that look risky. Treat any reviewer-added shell, regex, or PowerShell logic as UNTRUSTED until executed exactly as written against the real target or a temp copy. If a command cannot be dry-run during review, mark it `untested`, explain why, deduct readiness points, and list it as an executor validation priority.
  ```
  Authoritative acceptance check:
  ```powershell
  # NOTE: Single-quoted patterns and .Contains() for consistency.
  $p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Stage 2 / 3"); $e=$t.IndexOf("## Stage 4",$s); if($s -lt 0 -or $e -lt 0){throw "Stage 2 anchors not found"}; $b=$t.Substring($s,$e-$s); $required=@('dry-run EVERY verification command','add or modify','UNTRUSTED until executed exactly as written','real target or a temp copy','untested','deduct readiness points'); foreach($r in $required){if(-not $b.Contains($r)){throw "Stage 2 body missing: $r"}}; "Stage 2 dry-run body valid"
  ```
  Diagnostic checks: `Select-String -LiteralPath "...\stage-prompts.md" -SimpleMatch "Reviewer dry-run enforcement"`.
  Error recovery: If anchor fails, insert inside the fenced Stage 2 block, not after it.

Exit criteria: Stage 1 and Stage 2 checks pass.

## Phase 2: Metadata Schema Cleanup
Objective: Clarify count semantics.

- [x] **Task 2.1 - Add metadata schema section to threshold policy.**
  Command: Insert before `## Diversity rules` in `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`:
  ```markdown
## Metadata schema guidance

Use distinct metadata fields when a plan mixes executable tasks with readiness or quality checklists:

- `task_count` - count executable implementation task checkboxes only.
- `readiness_check_count` - count readiness, quality, or handover checklist items that are not executable implementation tasks.
- `total_checkbox_count` - count all markdown checkboxes in the plan; this should equal `task_count + readiness_check_count` when those are the only checkbox categories.
- `completed_tasks` - map this value to completed executable tasks out of `task_count`, not to `total_checkbox_count`.

Validators must not compare `completed_tasks` to readiness or quality checklist counts unless metadata explicitly defines a separate completed-readiness field. Report separate units such as `29/29 executable tasks`, `8/8 readiness checks`, and `37/37 total checkboxes`.
  ```
  Authoritative acceptance check:
  ```powershell
  # NOTE: Single-quoted patterns preserve literal backticks; .Contains() does literal matching.
  $p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Metadata schema guidance"); $e=$t.IndexOf("## Diversity rules",$s); if($s -lt 0 -or $e -lt 0){throw "Metadata schema anchors not found"}; $b=$t.Substring($s,$e-$s); $required=@('`task_count` - count executable implementation task checkboxes only','`readiness_check_count` - count readiness','`total_checkbox_count` - count all markdown checkboxes','`completed_tasks` - map this value to completed executable tasks out of `task_count`','29/29 executable tasks','37/37 total checkboxes'); foreach($r in $required){if(-not $b.Contains($r)){throw "metadata body missing: $r"}}; "metadata schema body valid"
  ```
  Diagnostic checks: `Select-String -LiteralPath "...\threshold-policy.md" -SimpleMatch "Metadata schema guidance"`.
  Error recovery: If section already exists, merge required body terms once; do not duplicate headings.

Exit criteria: metadata schema body check passes.

## Phase 3: New Reference Files
Objective: Create two reusable references.

- [x] **Task 3.1 - Create PowerShell pitfalls reference.**
  Command: Create `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\powershell-pitfalls.md` containing these exact body fragments (write the file via `@''...''@` here-string or `[System.IO.File]::WriteAllText` to preserve backticks/`$`):

```text
# PowerShell Pitfalls (Conductor Pipeline)

## Static vs instance Replace

- [string]::Replace() is not a safe static call in PowerShell 7; there is no `[string]::Replace($a, $b)` static overload that returns a new string. Use the .NET instance method `$text.Replace($old, $new)` for literal (non-regex) replacement, or use `-replace` only when you intentionally want a regex.
- `-replace` is a regex operator; it treats `$` literally only in single-quoted strings. In double-quoted strings, `$1` expands to the last captured group.

## Where-Object indexing

- Where-Object returns a collection (often single-element). Index the result with `@(...)[0]` or `Select-Object -First 1` to get a single value safely. `$row = $result | Where-Object {...}; $row[0]` returns the first CHARACTER of the matching string, not the row.

## Wildcard characters in -like / -notlike

- `-like` and `-notlike` treat `[` and `]` as wildcard character-class brackets. The pattern `*[string]::Replace()*` is parsed as a character class and will NOT match the literal `[string]::Replace()`. Prefer `Select-String -SimpleMatch`, `.Contains()`, `[regex]::Escape()`, or anchored full-line patterns for literal content.

## Prefer literal matching over ad hoc regex

- Prefer literal matching (`Select-String -SimpleMatch`, `.Contains()`, `[regex]::Escape()`, or line-anchored full-line patterns) over ad hoc regex construction for Windows paths and other literal content. Use `-clike` or `[WildcardPattern]::Escape()` only when you intentionally want wildcard semantics.
```

The body MUST contain these literal substrings: `[string]::Replace()`, `` `$text.Replace(`$old,`$new) ``, `Where-Object returns`, `Select-Object -First 1`, `wildcard`, `Select-String -SimpleMatch`, `[regex]::Escape`, `Prefer literal matching`.
  Authoritative acceptance check:
  ```powershell
  # NOTE: Single-quoted patterns preserve literal backticks; .Contains() does literal matching.
  if(-not (Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\powershell-pitfalls.md")){throw "powershell-pitfalls.md does not exist"}; $p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\powershell-pitfalls.md"; $t=Get-Content -Raw -LiteralPath $p; $required=@('[string]::Replace()','`$text.Replace(`$old,`$new)','Where-Object returns','Select-Object -First 1','wildcard','Select-String -SimpleMatch','[regex]::Escape','Prefer literal matching'); foreach($r in $required){if(-not $t.Contains($r)){throw "pitfalls body missing: $r"}}; "PowerShell pitfalls body valid"
  ```
  Diagnostic checks: `Test-Path -LiteralPath "...\powershell-pitfalls.md"`.
  Error recovery: If file exists, merge required sections rather than overwriting without using the backup.

- [x] **Task 3.2 - Create global skill versioning reference.**
  Command: Create `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\global-skill-versioning.md` explaining that global skill files under `C:\Users\DaveWitkin\.config\opencode\skill\` are outside repo git history and unversioned; require timestamped `.pre-edit.bak` backups in `backups/<date>/`; recommend `git diff --no-index --numstat <backup> <target>` and full `git diff --no-index`; reference `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\backups\2026-06-29-pre-edit\`.
  Authoritative acceptance check:
  ```powershell
  # NOTE: Single-quoted patterns preserve literal backslashes; .Contains() does literal matching.
  if(-not (Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\global-skill-versioning.md")){throw "global-skill-versioning.md does not exist"}; $p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\global-skill-versioning.md"; $t=Get-Content -Raw -LiteralPath $p; $required=@('outside repo git history','unversioned','timestamped','.pre-edit.bak','git diff --no-index --numstat','20260629-conductor-pipeline-retro-improvements','backups\2026-06-29-pre-edit'); foreach($r in $required){if(-not $t.Contains($r)){throw "versioning body missing: $r"}}; "global skill versioning body valid"
  ```
  Diagnostic checks: `Test-Path -LiteralPath "...\global-skill-versioning.md"`.
  Error recovery: If path check fails because of brackets or wildcards, use `-LiteralPath` and body `.Contains()` checks.

Exit criteria: both new-file body checks pass.

## Final Phase: Validation & Handover
Objective: Prove changes and document execution.

- [x] **Task 4.1 - Produce backup-vs-target comparison artifact.**
  Command:
  ```powershell
  $td="C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening"; $b=(Get-Content -Raw -LiteralPath "$td\backup-dir.txt").Trim(); $names=@("stage-prompts.md","threshold-policy.md","powershell-pitfalls.md","global-skill-versioning.md"); $out=@(); foreach($n in $names){$out += "--- $n ---"; $target="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\$n"; $out += git diff --no-index --numstat "$b\$n.pre-edit.bak" "$target"}; Set-Content -Encoding utf8 -LiteralPath "$td\backup-vs-target-numstat.txt" -Value ($out -join "`n")
  ```
  Authoritative acceptance check:
  ```powershell
  # Section markers use simple ASCII; .Contains() avoids -like's wildcard interpretation and is faster.
  $t=Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\backup-vs-target-numstat.txt"; $markers=@('--- stage-prompts.md ---','--- threshold-policy.md ---','--- powershell-pitfalls.md ---','--- global-skill-versioning.md ---'); foreach($m in $markers){if(-not $t.Contains($m)){throw "numstat missing: $m"}}; "numstat covers all targets"
  ```
  Diagnostic checks: inspect the numstat file manually.
  Error recovery: `git diff --no-index` exit code 1 means files differ; capture output and continue.

- [x] **Task 4.2 - Run combined scoped body validation.**
  Command: Re-run the authoritative acceptance checks from Tasks 1.1, 1.2, 2.1, 3.1, and 3.2 without weakening terms.
  Authoritative acceptance check: All five commands must print their success messages: `Stage 1 hardening body valid`, `Stage 2 dry-run body valid`, `metadata schema body valid`, `PowerShell pitfalls body valid`, and `global skill versioning body valid`.
  Diagnostic checks: none.
  Error recovery: If any check fails, update the relevant body section; do not change the check to heading-only verification.

- [x] **Task 4.3 - Create execution log.**
  Command: Create `C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\execution-log-2026-06-30.md` listing changed files, backup folder, validation commands/results, deviations/skips, and handoff notes.
  Authoritative acceptance check:
  ```powershell
  if(-not (Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\execution-log-2026-06-30.md")){throw "execution log does not exist"}; $p="C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\execution-log-2026-06-30.md"; $t=Get-Content -Raw -LiteralPath $p; $required=@('## Changed files','stage-prompts.md','threshold-policy.md','powershell-pitfalls.md','global-skill-versioning.md','## Backup folder','## Validation performed','## Deviations','## Handoff notes'); foreach($r in $required){if(-not $t.Contains($r)){throw "log body missing: $r"}}; "execution log body valid"
  ```
  Diagnostic checks: none.
  Error recovery: If executed on a later date, use actual date in filename and update checks accordingly.

Exit criteria: backup comparison artifact and execution log exist; all body-content checks pass.

## Execution-Readiness Checklist
- [x] Backups are required before edits.
- [x] Every task has exactly one authoritative acceptance check.
- [x] Diagnostic checks are separated.
- [x] Checks inspect body content.
- [x] Commands use exact paths.
- [x] Error recovery is provided.

## Top 3 Risks + Mitigations
1. Global files are unversioned. Mitigation: timestamped backups plus `git diff --no-index`.
2. Shallow checks create false confidence. Mitigation: scoped body-content checks with multiple body terms.
3. PowerShell wildcard/regex pitfalls. Mitigation: `-LiteralPath`, literal matching, and dedicated pitfalls reference.

## First Task to Execute
Task 0.1 - Create track backup folder.