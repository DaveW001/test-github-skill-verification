# Review Diff Summary - test-skillshare-skills

- **Source plan:** `C:\development\opencode\.conductor\tracks\test-skillshare-skills\plan.md`
- **Review pass:** Stage 2
- **Reviewer model:** `opencode-go/minimax-m3`
- **Review timestamp:** 2026-07-04T17:45:34Z
- **Edits applied:** 6 (5 substantive + 1 cleanup)
- **Tool used:** PowerShell `[string]::Replace()` via `bash` (native `Edit` tool returns `Bun is not defined` in this host session)

This is a **semantic** diff summary (what changed and why), not a textual unified diff. Run `git diff -- C:\development\opencode\.conductor\tracks\test-skillshare-skills\plan.md` from the repo root for the textual diff.

## Edit 1 - Task 0.2 acceptance check (false-positive fix)

**Why:** `Get-Content` on a missing file is a non-terminating error in PowerShell 7, so `$r|?{...}.Count -eq 0` evaluated to `True` even when the action command never ran.

**Pattern before:**

```powershell
$r=Get-Content -Raw -LiteralPath '...preflight-assets.json'|ConvertFrom-Json; ($r|?{-not $_.Exists}).Count -eq 0
```

**Pattern after:**

```powershell
$j='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\preflight-assets.json'; (Test-Path -LiteralPath $j) -and ((Get-Content -Raw -LiteralPath $j|ConvertFrom-Json)|?{-not $_.Exists}).Count -eq 0
```

**Dry-run:** `True` when file exists with all `Exists=true`; `False` when file is missing.

## Edit 2 - Task 1.3 contrast-check.ps1 (text-size classification + independent check)

**Why:** `#0086ca/#ffffff` and `#ffffff/#0086ca` are 3.99:1, which fails AA-normal 4.5:1 but passes AA-large 3:1. Without a size-classification column the verifier would (correctly) emit `AllPass: False` and the plan's exit criterion "contrast report passes" would never be met. Pre-computed actual ratios added to the action spec so the executor does not have to re-derive them.

**Before:** "checks `#0086ca/#ffffff`, `#ffffff/#0f172a`, `#334155/#ffffff`, `#ffffff/#0086ca`, `#ffffff/#147bbb`, and `#0f172a/#eff6ff`; writes a table and `AllPass: True` or `AllPass: False`; exits 1 on failure."

**After:** specifies a `Class` column (`normal` -> 4.5, `large` -> 3.0) and per-pair thresholds; the two white-on-`#0086ca` pairs are classified as `large`. Adds an independent acceptance check that does not trust the script's self-reported `AllPass`:

```powershell
$rep = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\contrast-report.md'
(($rep -match 'AllPass:\s*True') -and ($rep -match '\| 3\.99 \|') -and ($rep -match '\| 4\.58 \|') -and ($rep -match 'large')) -and ($rep -match 'normal')
```

The check verifies both the existence of the `3.99` ratio row (the failing-for-normal case) AND the `large` classification token, so a bug that classifies the 3.99 pair as `normal` is caught.

## Edit 3 - Task 3.2 (build files + `npm install` + exact `build:pdf` script)

**Why (three reasons):**

1. The original `package.json` acceptance check verified the string `skillshare-test-v1.pdf` was present, but did not verify the actual `build:pdf` script. The executor could have written any package.json with that string and passed.
2. `npm install` was buried in the error-recovery footer; if the executor runs the action verbatim without hitting the error path, no install happens and Task 3.3 will fail with `could not resolve markdown-it`.
3. The Vivliostyle `--timeout` unit is **seconds** (verified via `npx --yes @vivliostyle/cli build --help`), not milliseconds. The original `--timeout 120000` was 33 hours; `--timeout 60000` from the skill is 16.6 hours. 60 seconds is sufficient for a single-file build.

**After:** specifies the exact `build:pdf` script:

```json
"build:pdf": "npx --yes @vivliostyle/cli build dist/skillshare-test-v1.html -o dist/skillshare-test-v1.pdf --timeout 60"
```

Promotes `npm install` to a numbered action step with a 60 s `fetch-timeout`. New acceptance check now also verifies that the local installs exist (`node_modules\@vivliostyle\cli\package.json` and `node_modules\markdown-it\package.json`).

## Edit 4 - Task 3.3 Vivliostyle build (Blocking bug fix)

**Why (this was the Blocking issue):** the original command `npx --prefix $p vivliostyle build ...` has two confirmed bugs:

- `npx --prefix` is not a valid npx flag; it is silently ignored (verified: `npx --prefix $p ...` behaves identically to `npx ...` from the current directory).
- The CLI package shortname `vivliostyle` does not exist on npm; the correct package is `@vivliostyle/cli`. Verified: `npx --prefix $p vivliostyle build ...` against a clean directory returns `npm error could not determine executable to run`.

A secondary issue: the plan's spec assumption that "Vivliostyle requires a URL" is **outdated** for `@vivliostyle/cli` v11.0.4. Verified: `npx --yes @vivliostyle/cli build <local.html> -o <pdf>` against a local file path produces a real PDF (28 KB, 1 page, `%PDF` magic bytes confirmed via PyMuPDF). No HTTP server is required in CLI v11.

**Before:**

```powershell
$p='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication'; npm run build:html --prefix $p; npx --prefix $p vivliostyle build "$p\dist\skillshare-test-v1.html" -o "$p\dist\skillshare-test-v1.pdf" --timeout 120000
```

**After:**

```powershell
$p='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication'
npm run build:html --prefix $p
npm run build:pdf  --prefix $p
```

A rationale paragraph was added inline so the executor understands WHY the command was rewritten and so future reviewers see the empirical evidence. Acceptance check now includes `%PDF` magic-bytes and v1/v2 fallback (so the EBUSY -> v2 escape hatch is not a false failure):

```powershell
$d='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\dist'; $candidates=@("$d\skillshare-test-v1.pdf","$d\skillshare-test-v2.pdf"); $pdf=$candidates|Where-Object{(Test-Path -LiteralPath $_) -and ((Get-Item -LiteralPath $_).Length -gt 10000) -and ((-join ([System.IO.File]::ReadAllBytes($_)[0..3]|ForEach-Object{[char]$_})) -eq '%PDF')}|Select-Object -First 1; [bool]$pdf
```

## Edit 5 - Task 5.1 final validation (false-positive fix)

**Why:** same false-positive shape as Edit 1. The expression `($r.Pass -contains $false) -eq $false` returns `True` when `$r.Pass` is missing or `$null` (no false to contain).

**Before:**

```powershell
$r=Get-Content -Raw -LiteralPath '...final-validation.json'|ConvertFrom-Json; ($r.Pass -contains $false) -eq $false
```

**After:**

```powershell
$j='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\final-validation.json'; (Test-Path -LiteralPath $j) -and ((Get-Content -Raw -LiteralPath $j|ConvertFrom-Json).Pass -notcontains $false)
```

`-notcontains` is the standard negation operator; clearer than the `-contains ... -eq $false` pattern.

## Edit 6 (cleanup) - removed duplicate authoritative acceptance check in Task 1.3

After Edit 2 added the new "Independent authoritative acceptance check", the original simple "Authoritative acceptance check" remained as a second block (because Edit 2 was a prepend, not a replace of the whole acceptance block). Stage 1 standard requires exactly one authoritative acceptance check per task, so the duplicate was removed. The new independent check is the only authoritative one for Task 1.3.

## Items NOT applied (surfaced to user, see review-report-2026-07-04-134531.md)

- **S1.** Task 3.1 source-content mismatch (first-principles copy vs. markdown-pdf-publisher's `<h2>Introduction</h2>` anchor). The plan's "if unavailable, write a fresh two-heading, five-paragraph PA proposal" branch is the safer primary path, but I did not swap them without user confirmation.
- **S2.** Task 4.2 humanizer metrics - independent recomputation. The third criterion (after std dev > before std dev) is text-dependent and would require either a fixed before/after template or a separate measurement. Surfaced for confirmation.
- **S3.** Local HTTP server path (`cmd /c start /b npx -y serve ...`). The empirical v11 result says it is not required, so the simpler local-file path was kept. Surfaced for confirmation that this is acceptable.
- **S4.** Top 3 Risks #2 in the plan is now stale after Edit 2; the new mitigation is "ensure white-on-`#0086ca` is `large`". Cosmetic.

## Files

- `C:\development\opencode\.conductor\tracks\test-skillshare-skills\plan.md` (6 edits applied)
- `C:\development\opencode\.conductor\tracks\test-skillshare-skills\review-report-2026-07-04-134531.md` (this review)
- `C:\development\opencode\.conductor\tracks\test-skillshare-skills\review-diff-summary-2026-07-04-134531.md` (this file)
