# Plan Diff Summary - 20260630-conductor-skill-hardening

**Reviewer:** Stage 2 (`opencode-go/minimax-m3`)
**Review timestamp:** 2026-06-30-134835
**File modified:** `C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\plan.md`
**spec.md:** unchanged.

---

## High-level summary

- **5 of 9 task acceptance checks contained PowerShell bugs** that would have made the check silently fail (return `True` for `-notlike` even when the body was correct) or, in one case, a hard parse error that aborts the whole script.
- **1 task body description was underspecified** relative to its strict verification patterns (Task 3.1).
- All bugs were deterministic and reproducible; all rewrites were dry-run against simulated post-insertion bodies and now report the expected success message.

I rewrote the broken pieces directly. `spec.md` was not touched.

---

## Constraint section: 2 new bullets added (high-level rule + verification rule)

### Before
```
## Constraints / Non-Goals
- Target files are global files outside repo git history.
- Back up before every edit.
- Use PowerShell-first commands with `-LiteralPath` and quoted Windows paths.
- Verification must inspect body content, not headings or isolated phrases only.
- Do not execute this plan during Stage 1.
```

### After
```
## Constraints / Non-Goals
- Target files are global files outside repo git history.
- Back up before every edit.
- Use PowerShell-first commands with `-LiteralPath` and quoted Windows paths.
- Verification must inspect body content, not headings or isolated phrases only.
- Do not execute this plan during Stage 1.
- **Body-writing rule (critical for backtick/bracket fidelity):** Whenever a task body contains literal backticks (`` ` ``), brackets, or dollar signs, the executor MUST write the body via a single-quoted PowerShell here-string (`@''...''@` ... `|''@`) or `[System.IO.File]::WriteAllText($path, $literal, [System.Text.Encoding]::UTF8)` with a literal `$literal` string. **Never** use a double-quoted here-string (`@"..."@`) or a double-quoted PowerShell string to hold a body that contains `` ` `` because `` `t `` becomes a tab, `` ` `` before `"` escapes the closing quote (parse error), and other backtick-escape bugs corrupt the file.
- **Body-content verification rule:** All body-content checks use single-quoted PowerShell strings with `[string]::Contains()` (literal substring matching) so backticks and brackets in patterns are not interpreted. `-notlike` is NOT used for body-content substring checks because `[` and `]` are wildcards in `-like` and the check would silently fail even when the body is correct.
```

These two bullets are the **root cause** of the bugs and the explicit fix. The rest of the diff applies them.

---

## Task 0.2 acceptance check

### Before (works, but unsafe pattern)
```powershell
$r=Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\docs\conductor-pipeline-run-retro-2026-06-30.md"; @("one authoritative acceptance check","dry-run every verification command","task_count","PowerShell pitfalls","global-skill versioning/backups")|%{if($r -notlike "*$_*"){throw "missing retro body: $_"}}; "retro body confirmed"
```

### After (works; uses .Contains() per the new constraint)
```powershell
$r=Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\docs\conductor-pipeline-run-retro-2026-06-30.md"; $terms=@('one authoritative acceptance check','dry-run every verification command','task_count','PowerShell pitfalls','global-skill versioning/backups'); foreach($t in $terms){if(-not $r.Contains($t)){throw "missing retro body: $t"}}; "retro body confirmed"
```

Why: Model the right pattern; future-proof against the executor adding backtick/bracket terms.

---

## Task 1.1 acceptance check

### Before (BLOCKING: `[regex]::Escape()` pattern fails because `[regex]` is a wildcard char class)
```powershell
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Stage 1 - Plan Creation"); $e=$t.IndexOf("## Stage 2 / 3",$s); $b=$t.Substring($s,$e-$s); @("exactly ONE authoritative acceptance check","Diagnostic checks:","BODY CONTENT","Reject heading-only or phrase-only checks","Select-String -SimpleMatch","[regex]::Escape()")|%{if($b -notlike "*$_*"){throw "Stage 1 body missing $_"}}; "Stage 1 hardening body valid"
```

### After (works; verified via test_combined.ps1)
```powershell
# NOTE: Use single-quoted patterns and .Contains() to avoid -like wildcard interpretation of [ and ].
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Stage 1 - Plan Creation"); $e=$t.IndexOf("## Stage 2 / 3",$s); if($s -lt 0 -or $e -lt 0){throw "Stage 1 anchors not found"}; $b=$t.Substring($s,$e-$s); $required=@('exactly ONE authoritative acceptance check','Diagnostic checks:','BODY CONTENT','Reject heading-only or phrase-only checks','Select-String -SimpleMatch','[regex]::Escape()'); foreach($r in $required){if(-not $b.Contains($r)){throw "Stage 1 body missing: $r"}}; "Stage 1 hardening body valid"
```

Why: `.Contains()` does literal substring matching; single-quoted patterns preserve the literal `[regex]::Escape()` text; the anchor-existence guard fails loudly if the headings are missing.

---

## Task 1.2 acceptance check

### Before (works, but unsafe pattern)
```powershell
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Stage 2 / 3"); $e=$t.IndexOf("## Stage 4",$s); $b=$t.Substring($s,$e-$s); @("dry-run EVERY verification command","add or modify","UNTRUSTED until executed exactly as written","real target or a temp copy","untested","deduct readiness points")|%{if($b -notlike "*$_*"){throw "Stage 2 body missing $_"}}; "Stage 2 dry-run body valid"
```

### After (works; verified via test_combined.ps1)
```powershell
# NOTE: Single-quoted patterns and .Contains() for consistency.
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Stage 2 / 3"); $e=$t.IndexOf("## Stage 4",$s); if($s -lt 0 -or $e -lt 0){throw "Stage 2 anchors not found"}; $b=$t.Substring($s,$e-$s); $required=@('dry-run EVERY verification command','add or modify','UNTRUSTED until executed exactly as written','real target or a temp copy','untested','deduct readiness points'); foreach($r in $required){if(-not $b.Contains($r)){throw "Stage 2 body missing: $r"}}; "Stage 2 dry-run body valid"
```

Why: Consistency with the rest of the plan.

---

## Task 2.1 acceptance check

### Before (BLOCKING: parser error in 4th pattern + backtick corruption in others)
```powershell
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Metadata schema guidance"); $e=$t.IndexOf("## Diversity rules",$s); $b=$t.Substring($s,$e-$s); @("`task_count` - count executable implementation task checkboxes only","`readiness_check_count` - count readiness","`total_checkbox_count` - count all markdown checkboxes","`completed_tasks` - map this value to completed executable tasks out of `task_count`","29/29 executable tasks","37/37 total checkboxes")|%{if($b -notlike "*$_*"){throw "metadata body missing $_"}}; "metadata schema body valid"
```

### After (works; verified via test_fix2.ps1, test_task21.ps1)
```powershell
# NOTE: Single-quoted patterns preserve literal backticks; .Contains() does literal matching.
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md"; $t=Get-Content -Raw -LiteralPath $p; $s=$t.IndexOf("## Metadata schema guidance"); $e=$t.IndexOf("## Diversity rules",$s); if($s -lt 0 -or $e -lt 0){throw "Metadata schema anchors not found"}; $b=$t.Substring($s,$e-$s); $required=@('`task_count` - count executable implementation task checkboxes only','`readiness_check_count` - count readiness','`total_checkbox_count` - count all markdown checkboxes','`completed_tasks` - map this value to completed executable tasks out of `task_count`','29/29 executable tasks','37/37 total checkboxes'); foreach($r in $required){if(-not $b.Contains($r)){throw "metadata body missing: $r"}}; "metadata schema body valid"
```

Why: 4th pattern `` "`completed_tasks` - map this value to completed executable tasks out of `task_count`" `` had a backtick before the closing `"` that escaped the quote, causing a parse error. The first 3 patterns had backticks interpreted as tab/CR, so the pattern text no longer matched the body. Single-quoted + `.Contains()` fixes both.

The body to insert (the `markdown` code block) was already correct and is unchanged.

---

## Task 3.1 body description and acceptance check

### Before (BLOCKING: 8 of 8 verification patterns broken; body underspecified)

**Body description (prose):**
> Command: Create `...powershell-pitfalls.md` covering: `[string]::Replace()` is not a safe static call in PowerShell 7; use `$text.Replace($old,$new)` or intentional `-replace`; `Where-Object` returns collection-like results and should be indexed via `@(...)[0]` or `Select-Object -First 1`; `-like`/`-notlike` treat `[` and `]` as wildcard chars; prefer `Select-String -SimpleMatch`, `.Contains()`, `[regex]::Escape()`, or anchored full-line patterns for Windows paths.

**Acceptance check:**
```powershell
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\powershell-pitfalls.md"; $t=Get-Content -Raw -LiteralPath $p; @("[string]::Replace()","`$text.Replace(`$old,`$new)","Where-Object returns","Select-Object -First 1","wildcard","Select-String -SimpleMatch","[regex]::Escape","Prefer literal matching")|%{if($t -notlike "*$_*"){throw "pitfalls body missing $_"}}; "PowerShell pitfalls body valid"
```

### After (works; body is now an exact `text` block, check is single-quoted + `.Contains()`)

**Body description (exact `text` block):**
> Command: Create `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\powershell-pitfalls.md` containing these exact body fragments (write the file via `@''...''@` here-string or `[System.IO.File]::WriteAllText` to preserve backticks/`$`):
>
> ```text
> # PowerShell Pitfalls (Conductor Pipeline)
>
> ## Static vs instance Replace
>
> - [string]::Replace() is not a safe static call in PowerShell 7; there is no `[string]::Replace($a, $b)` static overload that returns a new string. Use the .NET instance method `$text.Replace($old, $new)` for literal (non-regex) replacement, or use `-replace` only when you intentionally want a regex.
> - `-replace` is a regex operator; it treats `$` literally only in single-quoted strings. In double-quoted strings, `$1` expands to the last captured group.
>
> ## Where-Object indexing
>
> - Where-Object returns a collection (often single-element). Index the result with `@(...)[0]` or `Select-Object -First 1` to get a single value safely. `$row = $result | Where-Object {...}; $row[0]` returns the first CHARACTER of the matching string, not the row.
>
> ## Wildcard characters in -like / -notlike
>
> - `-like` and `-notlike` treat `[` and `]` as wildcard character-class brackets. The pattern `*[string]::Replace()*` is parsed as a character class and will NOT match the literal `[string]::Replace()`. Prefer `Select-String -SimpleMatch`, `.Contains()`, `[regex]::Escape()`, or anchored full-line patterns for literal content.
>
> ## Prefer literal matching over ad hoc regex
>
> - Prefer literal matching (`Select-String -SimpleMatch`, `.Contains()`, `[regex]::Escape()`, or line-anchored full-line patterns) over ad hoc regex construction for Windows paths and other literal content. Use `-clike` or `[WildcardPattern]::Escape()` only when you intentionally want wildcard semantics.
> ```
>
> The body MUST contain these literal substrings: `[string]::Replace()`, `` `$text.Replace(`$old,`$new) ``, `Where-Object returns`, `Select-Object -First 1`, `wildcard`, `Select-String -SimpleMatch`, `[regex]::Escape`, `Prefer literal matching`.

**Acceptance check (rewritten):**
```powershell
# NOTE: Single-quoted patterns preserve literal backticks; .Contains() does literal matching.
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\powershell-pitfalls.md"; $t=Get-Content -Raw -LiteralPath $p; $required=@('[string]::Replace()','`$text.Replace(`$old,`$new)','Where-Object returns','Select-Object -First 1','wildcard','Select-String -SimpleMatch','[regex]::Escape','Prefer literal matching'); foreach($r in $required){if(-not $t.Contains($r)){throw "pitfalls body missing: $r"}}; "PowerShell pitfalls body valid"
```

Why: The original body's prose did not include all 8 verification substrings (notably `Prefer literal matching`). The original 8 patterns were all broken: `[string]::Replace()` and `[regex]::Escape` due to bracket wildcards, `` `$text.Replace(`$old,`$new) `` because backticks stripped the dollar sign escapes. The new body is a complete `text` block and the new check is literal.

---

## Task 3.2 acceptance check

### Before (works, but unsafe pattern)
```powershell
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\global-skill-versioning.md"; $t=Get-Content -Raw -LiteralPath $p; @("outside repo git history","unversioned","timestamped",".pre-edit.bak","git diff --no-index --numstat","20260629-conductor-pipeline-retro-improvements","backups\2026-06-29-pre-edit")|%{if($t -notlike "*$_*"){throw "versioning body missing $_"}}; "global skill versioning body valid"
```

### After (works; consistency with the rest of the plan)
```powershell
# NOTE: Single-quoted patterns preserve literal backslashes; .Contains() does literal matching.
$p="C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\global-skill-versioning.md"; $t=Get-Content -Raw -LiteralPath $p; $required=@('outside repo git history','unversioned','timestamped','.pre-edit.bak','git diff --no-index --numstat','20260629-conductor-pipeline-retro-improvements','backups\2026-06-29-pre-edit'); foreach($r in $required){if(-not $t.Contains($r)){throw "versioning body missing: $r"}}; "global skill versioning body valid"
```

---

## Task 4.1 acceptance check

### Before (works, but unsafe pattern)
```powershell
$t=Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\backup-vs-target-numstat.txt"; @("--- stage-prompts.md ---","--- threshold-policy.md ---","--- powershell-pitfalls.md ---","--- global-skill-versioning.md ---")|%{if($t -notlike "*$_*"){throw "numstat missing $_"}}; "numstat covers all targets"
```

### After (works; consistency)
```powershell
# Section markers use simple ASCII; .Contains() avoids -like's wildcard interpretation and is faster.
$t=Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\backup-vs-target-numstat.txt"; $markers=@('--- stage-prompts.md ---','--- threshold-policy.md ---','--- powershell-pitfalls.md ---','--- global-skill-versioning.md ---'); foreach($m in $markers){if(-not $t.Contains($m)){throw "numstat missing: $m"}}; "numstat covers all targets"
```

---

## Task 4.3 acceptance check

### Before (works, but unsafe pattern)
```powershell
$p="C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\execution-log-2026-06-30.md"; $t=Get-Content -Raw -LiteralPath $p; @("## Changed files","stage-prompts.md","threshold-policy.md","powershell-pitfalls.md","global-skill-versioning.md","## Backup folder","## Validation performed","## Deviations","## Handoff notes")|%{if($t -notlike "*$_*"){throw "log body missing $_"}}; "execution log body valid"
```

### After (works; consistency)
```powershell
$p="C:\development\opencode\.conductor\tracks\20260630-conductor-skill-hardening\execution-log-2026-06-30.md"; $t=Get-Content -Raw -LiteralPath $p; $required=@('## Changed files','stage-prompts.md','threshold-policy.md','powershell-pitfalls.md','global-skill-versioning.md','## Backup folder','## Validation performed','## Deviations','## Handoff notes'); foreach($r in $required){if(-not $t.Contains($r)){throw "log body missing: $r"}}; "execution log body valid"
```

---

## Files NOT changed

- `spec.md` — already at the right level of abstraction; the bugs were all in `plan.md`.
- Tasks 0.1, 0.3, 4.2 — no changes needed.

## Final state

- 11 / 11 tasks Ready
- 0 Needs work
- 0 Blocking
- Readiness score: **100%**
