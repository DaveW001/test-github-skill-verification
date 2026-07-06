# Plan: Humanizer Peer Review Fixes

## Restatement
- Goal/outcome: fix the 8 peer-review issues for the expanded `humanizer` skill, rerun the measurement suite, update reports, document the out-of-band improvement, and push the skill repo changes.
- Constraints/non-goals: shell-first PowerShell only if file tools are broken; exact `-LiteralPath` Windows paths; bounded non-interactive commands; no pattern-category expansion beyond 22; no unrelated skills/PDF work; preserve Packaged Agile voice; no amend or force-push.
- Definition of done: all 8 issues fixed, new measurement coverage passes with zero short sentence stacks and `AllPass: True`, reports are grounded in the new checks, the test-track execution log is appended, and the temp skill repo is committed and pushed.

## Phase 0 Setup & Preconditions
Objective: confirm the active working set and create safe backups before editing.

- [x] Task 0.1: Confirm all required files exist.
  - Command:
    ```powershell
    $paths = @(
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\SKILL.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md',
      'C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md'
    )
    $missing = $paths | Where-Object { -not (Test-Path -LiteralPath $_) }
    [pscustomobject]@{ MissingCount = @($missing).Count; Missing = $missing } | ConvertTo-Json -Compress
    ```
  - Authoritative acceptance check:
    ```powershell
    $paths = @(
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\SKILL.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md',
      'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md',
      'C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md'
    ); @($paths | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -eq 0
    ```
    Expected output: `True`
  - Diagnostic checks: `git -C "C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills" status --short`
  - Error recovery: if any file is missing, stop and report the missing path; do not create substitute files.

- [x] Task 0.2: Create timestamped backups beside every editable file.
  - Command:
    ```powershell
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $paths = @('C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\SKILL.md','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md','C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md')
    foreach ($p in $paths) { Copy-Item -LiteralPath $p -Destination "$p.bak-$stamp" -ErrorAction Stop }
    $stamp | Set-Content -Encoding utf8 -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-humanizer-peer-review-fixes\backup-stamp.txt'
    ```
  - Authoritative acceptance check:
    ```powershell
    $stamp = (Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260704-humanizer-peer-review-fixes\backup-stamp.txt').Trim(); $baks = @("C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\SKILL.md.bak-$stamp","C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md.bak-$stamp","C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md.bak-$stamp","C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1.bak-$stamp","C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md.bak-$stamp"); @($baks | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -eq 0
    ```
    Expected output: `True`
  - Diagnostic checks: list backups with `Get-ChildItem -LiteralPath "C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer" -Filter "*.bak-$stamp"`.
  - Error recovery: if copying fails, check permissions and free space; do not edit until backups exist.

## Phase 1 Implementation: Skill File Contradictions and Checklist
Objective: resolve recommendation contradictions, synchronize Kobak wording, and prioritize the checklist.

- [x] Task 1.1: Reword `brand-voice.md` Rule 3 to one clear em-dash rule.
  - Command: edit `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md` using literal `[string]::Replace()` so Rule 3 contains the exact sentence: `Use em dashes sparingly, only for sharp interruptions. Never for explanatory clauses.`
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md'; $c.Contains('Use em dashes sparingly, only for sharp interruptions. Never for explanatory clauses.') -and -not $c.Contains('Avoid em dashes')
    ```
    Expected output: `True`
  - Diagnostic checks: `Select-String -LiteralPath "...\brand-voice.md" -SimpleMatch "em dash"`.
  - Error recovery: if original text differs, locate Rule 3 with `Select-String -SimpleMatch 'Rule 3'` and make a minimal manual edit.

- [x] Task 1.2: Remove `Here's the thing` endorsement from `brand-voice.md` Rule 7 and make it explicitly banned.
  - Command: edit Rule 7 in `brand-voice.md` so it includes `Do not use "Here's the thing" as an opener or transition; it is an observer-opener AI tell.` and does not list it as a natural transition.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md'; $c.Contains('Do not use "Here''s the thing" as an opener or transition; it is an observer-opener AI tell.')
    ```
    Expected output: `True`
  - Diagnostic checks: `Select-String -LiteralPath "...\brand-voice.md" -SimpleMatch "Here's the thing"`.
  - Error recovery: if quote escaping is confusing, use a single-quoted here-string assignment and `Set-Content -Encoding utf8`.


- [x] Task 1.2b: Remove `Here's the thing` from `ai-patterns-to-fix.md` Pattern 10 Observer Opener list (resolve the triple contradiction across the three files).
  - Command: edit Pattern 10 in `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md` so the Observer Opener bullet no longer includes `"Here's the thing."` Keep the other Observer Opener examples intact.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md'; (-not ($c | Select-String -Pattern 'Observer Opener:.*Here.s the thing')) -and ((Select-String -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md' -Pattern 'Observer Opener:').Count -ge 1)
    ```
    Expected output: `True`
  - Diagnostic checks: `Select-String -LiteralPath '...\ai-patterns-to-fix.md' -SimpleMatch 'Here''s the thing'`.
  - Error recovery: if Pattern 10 was renumbered in the current working copy, locate the Observer Opener list with `Select-String -SimpleMatch 'Observer Opener'` and edit that line only.

- [x] Task 1.3: Synchronize the full 26-word Kobak excess list in `brand-voice.md`.
  - Command: add or replace the Kobak list with this exact comma-separated list: `delve, underscores, showcasing, pivotal, intricate, meticulously, realm, tapestry, landscape, ecosystem, robust, seamless, comprehensive, multifaceted, nuanced, holistic, leverage, utilize, harness, streamline, facilitate, optimize, empower, navigate, foster, elevate`.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md'; $c.Contains('delve, underscores, showcasing, pivotal, intricate, meticulously, realm, tapestry, landscape, ecosystem, robust, seamless, comprehensive, multifaceted, nuanced, holistic, leverage, utilize, harness, streamline, facilitate, optimize, empower, navigate, foster, elevate')
    ```
    Expected output: `True`
  - Diagnostic checks: count terms by splitting the string on commas.
  - Error recovery: if a term is disputed, prefer the list already present in `humanization-checklist.md` and document the difference.

- [x] Task 1.4: Add a top-five high-signal checks callout near the top of `humanization-checklist.md`.
  - Command: insert after the title/opening paragraph a callout containing exactly these five bullets:
    ```markdown
    > **Top 5 high-signal checks:**
    > 1. Kill hook-formula openers before they frame the piece like a template.
    > 2. Break every short-sentence stack of four or more consecutive sentences under 12 words.
    > 3. Remove Kobak excess words before polishing tone.
    > 4. Replace resolution closers with a concrete next move.
    > 5. Add rhetorical contrast only where it sharpens the operating choice.
    ```
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md'; $c.Contains('> **Top 5 high-signal checks:**') -and $c.Contains('> 2. Break every short-sentence stack of four or more consecutive sentences under 12 words.') -and $c.Contains('> 5. Add rhetorical contrast only where it sharpens the operating choice.')
    ```
    Expected output: `True`
  - Diagnostic checks: ensure the callout appears before the long checklist with `Select-String` line numbers.
  - Error recovery: if duplicate callout exists, keep one complete callout and remove duplicates.

- [x] Task 1.5: Confirm the full 26-word Kobak list is synchronized between `humanization-checklist.md` and `brand-voice.md`.
  - Command: if needed, edit `humanization-checklist.md` so the same exact list from Task 1.3 appears once in its Kobak section.
  - Authoritative acceptance check:
    ```powershell
    $list = 'delve, underscores, showcasing, pivotal, intricate, meticulously, realm, tapestry, landscape, ecosystem, robust, seamless, comprehensive, multifaceted, nuanced, holistic, leverage, utilize, harness, streamline, facilitate, optimize, empower, navigate, foster, elevate'; $a = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md'; $b = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md'; $a.Contains($list) -and $b.Contains($list)
    ```
    Expected output: `True`
  - Diagnostic checks: split and compare arrays for 26 terms.
  - Error recovery: if either file has table formatting, include the comma-separated canonical line in addition to any table.

## Phase 2 Implementation: Measurement Script
Objective: add programmatic coverage for the new pattern categories and expose pass/fail signals.

- [x] Task 2.1: Add short-sentence stack detection to `measure-humanizer.ps1`.
  - Command: edit `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1` to calculate `ShortSentenceStackCount` where short sentence means fewer than 12 words and stack means 4+ consecutive short sentences.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'; $c.Contains('ShortSentenceStackCount') -and $c.Contains('4+ consecutive') -and $c.Contains('12 words')
    ```
    Expected output: `True`
  - Diagnostic checks: run `pwsh -NoProfile -File "...\measure-humanizer.ps1"` after Task 2.5.
  - Error recovery: if sentence splitting is hard, use `[regex]::Matches($Text, '[^.!?]+[.!?]')` and count word tokens with `[regex]::Matches($sentence, '\b[\p{L}\p{N}'']+\b')`.

- [x] Task 2.2: Add hook-formula opener detection to `measure-humanizer.ps1`.
  - Command: add a check named `HookFormulaOpenerCount` for template openers such as `Here's the thing`, `The truth is`, `Let's be honest`, `In today's`, and `If you're like most`.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'; $c.Contains('HookFormulaOpenerCount') -and $c.Contains('Here''s the thing') -and $c.Contains('If you''re like most')
    ```
    Expected output: `True`
  - Diagnostic checks: verify the pattern list is case-insensitive.
  - Error recovery: escape apostrophes by doubling them inside single-quoted PowerShell strings.

- [x] Task 2.3: Add Kobak excess word count detection to `measure-humanizer.ps1`.
  - Command: add a check named `KobakExcessWordCount` using the exact 26-word list from Task 1.3 and whole-word/case-insensitive matching.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'; $c.Contains('KobakExcessWordCount') -and $c.Contains('streamline') -and $c.Contains('tapestry')
    ```
    Expected output: `True`
  - Diagnostic checks: confirm 26 list entries by splitting the literal array.
  - Error recovery: if hyphen matching breaks for `cutting-edge`, handle it as an escaped literal with `[regex]::Escape()`.

- [x] Task 2.4: Add resolution closer detection and rhetorical contrast detection to `measure-humanizer.ps1`.
  - Command: add checks named `ResolutionCloserCount` and `RhetoricalContrastCount`; resolution closers should catch generic closers like `in conclusion`, `at the end of the day`, and `ultimately`; rhetorical contrast should detect constructions such as `not X, but Y`, `less X, more Y`, or `the problem is not`.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'; $c.Contains('ResolutionCloserCount') -and $c.Contains('RhetoricalContrastCount') -and $c.Contains('the problem is not')
    ```
    Expected output: `True`
  - Diagnostic checks: add comments explaining pass thresholds.
  - Error recovery: if regex is brittle, use simple lower-case `.Contains()` scans for resolution closers and a conservative regex for contrast.

- [x] Task 2.5: Update `AllPass` logic and output to include all new checks.
  - Command: ensure `AllPass` requires zero short sentence stacks, zero hook-formula openers, zero Kobak excess words, zero generic resolution closers, and at least one rhetorical contrast signal unless the existing suite has a stricter threshold.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'; $c.Contains('$AllPass') -and $c.Contains('$ShortSentenceStackCount -eq 0') -and $c.Contains('$HookFormulaOpenerCount -eq 0') -and $c.Contains('$KobakExcessWordCount -eq 0') -and $c.Contains('$ResolutionCloserCount -eq 0') -and $c.Contains('AllPass: ') -and $c.Contains('ShortSentenceStackCount: ') -and $c.Contains('HookFormulaOpenerCount: ') -and $c.Contains('KobakExcessWordCount: ') -and $c.Contains('ResolutionCloserCount: ')
    ```
    Expected output: `True`
  - Diagnostic checks: run `pwsh -NoProfile -Command { $null = [scriptblock]::Create((Get-Content -Raw -LiteralPath '...\measure-humanizer.ps1')); 'parse-ok' }`.
  - Error recovery: if `RhetoricalContrastCount` is zero on good prose, lower the requirement to report-only and document that choice in the reports.

## Phase 3 Implementation: Rewrite `after.md`
Objective: remove the three short-sentence stacks without losing meaning or Packaged Agile voice.

- [x] Task 3.1: Rewrite the `Six weeks, every time...` block in `after.md` to avoid four consecutive sub-12-word sentences.
  - Command: replace that block with prose preserving the meaning, for example: `Six weeks, every time, because the point is not theater. Nothing moved until the team named the boring fix, assigned one owner, and checked the same signal again.`
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md'; $c.Contains('Six weeks, every time, because the point is not theater.') -and $c.Contains('Nothing moved until the team named the boring fix, assigned one owner, and checked the same signal again.')
    ```
    Expected output: `True`
  - Diagnostic checks: inspect nearby paragraph for voice and grammar.
  - Error recovery: if exact old block differs, find the paragraph with `Select-String -SimpleMatch 'Six weeks'` and rewrite only that paragraph.

- [x] Task 3.2: Rewrite the `Then do it again...` block in `after.md` to avoid four consecutive sub-12-word sentences.
  - Command: replace that block with prose preserving the meaning, for example: `Then do it again, using the same measure long enough to learn whether the change mattered. If the numbers move, keep going; if they do not, stop defending the favorite theory and go find the real constraint.`
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md'; $c.Contains('Then do it again, using the same measure long enough to learn whether the change mattered.') -and $c.Contains('stop defending the favorite theory and go find the real constraint.')
    ```
    Expected output: `True`
  - Diagnostic checks: inspect sentence lengths after replacement.
  - Error recovery: if the exact old block differs, locate with `Select-String -SimpleMatch 'Then do it again'`.

- [x] Task 3.3: Rewrite the `Choose a value stream...` block in `after.md` to avoid four consecutive sub-12-word sentences.
  - Command: replace that block with prose preserving the meaning, for example: `Choose a value stream the business actually cares about, then map it end to end with the people who do the work. The bottleneck will introduce itself once the room stops optimizing local activity and starts following flow.`
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md'; $c.Contains('Choose a value stream the business actually cares about, then map it end to end with the people who do the work.') -and $c.Contains('The bottleneck will introduce itself once the room stops optimizing local activity and starts following flow.')
    ```
    Expected output: `True`
  - Diagnostic checks: inspect paragraph continuity.
  - Error recovery: if exact old block differs, locate with `Select-String -SimpleMatch 'Choose a value stream'`.

## Phase 4 Implementation: Re-run Suite and Update Reports
Objective: regenerate metric evidence and make report claims match the expanded checks.

- [x] Task 4.1: Run the updated measurement suite against fixed `after.md`.
  - Command:
    ```powershell
    pwsh -NoProfile -ExecutionPolicy Bypass -File 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'
    ```
  - Authoritative acceptance check:
    ```powershell
    $out = pwsh -NoProfile -ExecutionPolicy Bypass -File 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'; ($out -join "`n").Contains('AllPass: True') -and ($out -join "`n").Contains('ShortSentenceStackCount: 0')
    ```
    Expected output: `True`
  - Diagnostic checks: capture full output to `C:\development\opencode\.conductor\tracks\20260704-humanizer-peer-review-fixes\measurement-output.txt`.
  - Error recovery: if `AllPass` is false, fix the failing metric before editing reports.

- [x] Task 4.2: Update `metrics-report.md` with the expanded-check results.
  - Command: edit `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md` to include a dated section with `AllPass: True`, `ShortSentenceStackCount: 0`, `HookFormulaOpenerCount: 0`, `KobakExcessWordCount: 0`, `ResolutionCloserCount: 0`, and the observed `RhetoricalContrastCount`.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md'; $c.Contains('AllPass: True') -and $c.Contains('ShortSentenceStackCount: 0') -and $c.Contains('HookFormulaOpenerCount: 0') -and $c.Contains('KobakExcessWordCount: 0') -and $c.Contains('ResolutionCloserCount: 0')
    ```
    Expected output: `True`
  - Diagnostic checks: compare to measurement output from Task 4.1.
  - Error recovery: if the script emits JSON/table instead of key-value lines, preserve the actual output format and quote it in the report.

- [x] Task 4.3: Update `summary.md` with grounded pass claims.
  - Command: edit `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md` so it states the expanded measurement suite passed and names the five new checks.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md'; $c.Contains('expanded measurement suite') -and $c.Contains('AllPass: True') -and $c.Contains('short sentence stacks') -and $c.Contains('hook-formula openers') -and $c.Contains('Kobak excess words')
    ```
    Expected output: `True`
  - Diagnostic checks: ensure no stale claim says only three original metrics were checked.
  - Error recovery: if a previous summary format is structured, add a new dated note rather than deleting useful history.

## Phase 5 Implementation: Document and Push
Objective: record the out-of-band improvement and publish skill-source changes.

- [x] Task 5.1: Append a dated section to the existing test-track execution log.
  - Command: append to `C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md` a section beginning `## 2026-07-04 Out-of-band humanizer peer-review fixes` and body text listing the contradiction fixes, checklist prioritization, measurement expansion, `after.md` stack fix, and report updates.
  - Authoritative acceptance check:
    ```powershell
    $c = Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md'; $c.Contains('## 2026-07-04 Out-of-band humanizer peer-review fixes') -and $c.Contains('measurement expansion') -and $c.Contains('after.md short-sentence stack fix')
    ```
    Expected output: `True`
  - Diagnostic checks: use `git diff --no-index` against the backup from Task 0.2 for append-only review.
  - Error recovery: if duplicate section exists, update the existing section body rather than appending another.

- [x] Task 5.2: Stage and commit only humanizer skill source changes in the temp repo.
  - Command:
    ```powershell
    git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' status --short
    git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' add -- 'skills/humanizer/SKILL.md' 'skills/humanizer/references/ai-patterns-to-fix.md' 'skills/humanizer/references/brand-voice.md' 'skills/humanizer/references/humanization-checklist.md'
    git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' commit -m 'Fix humanizer peer review findings'
    ```
  - Authoritative acceptance check:
    ```powershell
    git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' log --oneline -1
    ```
    Expected output starts with a commit hash and contains `Fix humanizer peer review findings`.
  - Diagnostic checks: `git -C "...\skillshare-skills" diff --cached --stat` before commit.
  - Error recovery: if there are no staged changes, verify whether files were already committed; never amend.

- [x] Task 5.3: Push the new humanizer commit to `origin`.
  - Command:
    ```powershell
    git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' remote -v
    git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' push origin HEAD
    ```
  - Authoritative acceptance check:
    ```powershell
    $local = git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' rev-parse HEAD; $remote = git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' ls-remote origin HEAD | ForEach-Object { ($_ -split "`t")[0] }; $local -eq $remote
    ```
    Expected output: `True`
  - Diagnostic checks: inspect remote URL; expected origin includes `https://github.com/packaged-agile/skillshare-skills.git`.
  - Error recovery: if authentication fails, report the push as blocked but keep commit local; do not force-push or change remotes without authorization.

## Final Phase Validation & Handover
Objective: prove the file fixes, reports, log, and push state are ready for closeout.

- [x] Task 6.1: Run final deterministic validation across fixed artifacts.
  - Command:
    ```powershell
    $measure = pwsh -NoProfile -ExecutionPolicy Bypass -File 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'
    $brand = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md'
    $check = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md'
    [pscustomobject]@{
      AllPass = (($measure -join "`n").Contains('AllPass: True'))
      ZeroStacks = (($measure -join "`n").Contains('ShortSentenceStackCount: 0'))
      EmDashClear = $brand.Contains('Use em dashes sparingly, only for sharp interruptions. Never for explanatory clauses.')
      HeresThingBanned = $brand.Contains('Do not use "Here''s the thing" as an opener or transition; it is an observer-opener AI tell.')
      TopFivePresent = $check.Contains('> **Top 5 high-signal checks:**')
    } | ConvertTo-Json -Compress
    ```
  - Authoritative acceptance check:
    ```powershell
    $measure = pwsh -NoProfile -ExecutionPolicy Bypass -File 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1'; $brand = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md'; $check = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md'; (($measure -join "`n").Contains('AllPass: True')) -and (($measure -join "`n").Contains('ShortSentenceStackCount: 0')) -and $brand.Contains('Use em dashes sparingly, only for sharp interruptions. Never for explanatory clauses.') -and $brand.Contains('Do not use "Here''s the thing" as an opener or transition; it is an observer-opener AI tell.') -and $check.Contains('> **Top 5 high-signal checks:**')
    ```
    Expected output: `True`
  - Diagnostic checks: inspect `git status --short` in both repos and the appended log section.
  - Error recovery: if a condition is false, return to the specific task that owns it; do not patch validation to pass.

## Execution-readiness checklist
- [ ] Shell commands are PowerShell 7+ compatible and bounded by the orchestrating tool timeout.
- [ ] Every task has exactly one `Authoritative acceptance check:`.
- [ ] Diagnostic checks are separate from authoritative proof.
- [ ] Literal body text in acceptance checks is specified in the task body.
- [ ] Push task forbids amend and force-push.

## Top 3 risks and mitigations
1. Risk: PowerShell quoting around apostrophes in `Here's the thing` breaks edits or checks. Mitigation: use single-quoted strings with doubled apostrophes or verbatim here-strings, and verify with `[string]::Contains()`.
2. Risk: Measurement script output format differs from the plan examples. Mitigation: preserve actual output format, but ensure it includes `AllPass: True` and named metric lines before updating reports.
3. Risk: Git push is blocked by credentials/network. Mitigation: keep the commit local, report push blockage as non-file-fix blocker, and never amend, force-push, or change remotes without authorization.
4. Risk: Working copy of `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills` has uncommitted modifications from the prior test-skillshare-skills track (4 humanizer files modified vs commit 38c1956). If the executor starts editing on top of these, fixes compound on an undocumented baseline. Mitigation: spec treats the current working copy as the baseline (the plan describes fixing 8 issues in the "expanded" state). Before Phase 5 commit, the executor must run `git -C 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills' status --short` and `git diff --stat -- 'skills/humanizer/'` and confirm only the 4 expected humanizer files are modified; if the actual modification set differs, report it and pause.

## First task to execute
Task 0.1: Confirm all required files exist.






