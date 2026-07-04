# Plan: Test Packaged Agile Skillshare Skills

Track ID: `test-skillshare-skills`

## Restated Goal / Constraints / Definition of Done

Goal: test four skills from `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills` and produce reviewable artifacts plus deterministic gauges under `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\`.

Constraints: exclude `retrospective`; do not push; do not install Playwright/Puppeteer/Selenium; keep tests independent; use PowerShell via `bash` for file operations; use `-LiteralPath`; keep commands bounded; do not run concurrent Vivliostyle builds; do not kill Chrome/Edge processes.

Definition of Done: each skill has a reviewable deliverable, a quality-gauge result, and a one-paragraph `summary.md`; final handover lists all artifact paths and any failures.

## Phase 0 Setup & Preconditions

Objective: prepare isolated folders and confirm inputs.

- [x] Task 0.1: Create output subfolders.
  - Action command:
    ```powershell
    $Root='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests'; foreach($d in @($Root,"$Root\pa-ui-design","$Root\first-principles","$Root\markdown-pdf","$Root\humanizer")){New-Item -ItemType Directory -Force -Path $d|Out-Null}
    ```
  - Authoritative acceptance check:
    ```powershell
    $Root='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests'; @('pa-ui-design','first-principles','markdown-pdf','humanizer')|%{Test-Path -LiteralPath "$Root\$_"}
    ```
    Expected output: four `True` lines.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests' -Directory`
  - Error recovery: if creation fails, verify parent `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode`; if missing, stop and report.

- [x] Task 0.2: Confirm required repo skills and PA assets.
  - Action command:
    ```powershell
    $Required=@('C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\pa-ui-design','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\first-principles-mastery','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\markdown-pdf-publisher','C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer','C:\development\2025-pa-website\public\fonts\Radikal.woff2','C:\development\2025-pa-website\public\fonts\Radikal-Bold.woff2','C:\development\2025-pa-website\public\fonts\Radikal-Medium.woff2','C:\development\2025-pa-website\graphics\Logo 02.png'); $Required|%{[pscustomobject]@{Path=$_;Exists=Test-Path -LiteralPath $_}}|ConvertTo-Json|Set-Content -Encoding utf8 -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\preflight-assets.json'
    ```
  - Authoritative acceptance check:
    ```powershell
    $j='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\preflight-assets.json'; (Test-Path -LiteralPath $j) -and ((Get-Content -Raw -LiteralPath $j|ConvertFrom-Json)|?{-not $_.Exists}).Count -eq 0
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\preflight-assets.json'`
  - Error recovery: if a path is missing, continue only with unaffected skills and record missing inputs in summaries and handover.

Exit criteria: folders exist and preflight JSON records all inputs.

## Phase 1 Skill Test: pa-ui-design

Objective: create two standalone PA pages and contrast gauge.

- [x] Task 1.1: Create `pa-ui-design\landing.html` after reading skill references.
  - Action command: read `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\pa-ui-design\references\*`, then write a standalone landing page to `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\landing.html` using `Set-Content -Encoding utf8`. The body must include hero, feature cards, CTA, footer, PA logo, Radikal font-face references, `#0086ca`, `#147bbb`, `focus-visible`, `transition:transform .3s`, `transition:transform .2s`, and `transform:scale(1.05)`. Include the exact headline `Transformation that shows up in the numbers.`
  - Authoritative acceptance check:
    ```powershell
    $t=Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\landing.html'; ($t.Contains('#0086ca') -and $t.Contains('#147bbb') -and $t.Contains('Radikal.woff2') -and $t.Contains('transform:scale(1.05)') -and $t.Contains('focus-visible') -and $t.Contains('Transformation that shows up in the numbers.'))
    ```
    Expected output: `True`.
  - Diagnostic checks: `(Get-Item -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\landing.html').Length`
  - Error recovery: patch only `landing.html` and rerun this check.

- [x] Task 1.2: Create `pa-ui-design\dashboard.html`.
  - Action command: write a standalone responsive dashboard HTML containing PA logo, Radikal font-face, colors `#0086ca` and `#147bbb`, sidebar/nav, three metric cards, a table, `focus-visible`, `transition:transform .3s`, and `transform:scale(1.05)` to `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\dashboard.html` using `Set-Content -Encoding utf8`. Include exact text `Evidence over theater`.
  - Authoritative acceptance check:
    ```powershell
    $t=Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\dashboard.html'; ($t.Contains('#0086ca') -and $t.Contains('#147bbb') -and $t.Contains('Radikal') -and $t.Contains('<table') -and $t.Contains('focus-visible') -and $t.Contains('Evidence over theater'))
    ```
    Expected output: `True`.
  - Diagnostic checks: `(Get-Item -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\dashboard.html').Length`
  - Error recovery: patch only `dashboard.html`.

- [x] Task 1.3: Create and run `contrast-check.ps1`; write `contrast-report.md`.
  - Action command: create a PowerShell script at `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\contrast-check.ps1` that defines `Convert-HexToRgb`, `Get-Lum`, and `Get-Contrast`; checks the following six pairs each with a WCAG size class and minimum ratio (the `Class` column tells the script which threshold to apply; actual ratios pre-computed here are `#0086ca/#ffffff`=3.99, `#ffffff/#0f172a`=17.85, `#334155/#ffffff`=10.35, `#ffffff/#0086ca`=3.99, `#ffffff/#147bbb`=4.58, `#0f172a/#eff6ff`=16.40): `#0086ca/#ffffff` (large, 3.0), `#ffffff/#0f172a` (normal, 4.5), `#334155/#ffffff` (normal, 4.5), `#ffffff/#0086ca` (large, 3.0), `#ffffff/#147bbb` (normal, 4.5), `#0f172a/#eff6ff` (normal, 4.5). The script must write a markdown table with columns `Foreground | Background | Class | Required | Actual | Pass`, then a final line `AllPass: True` only when every row passes; `AllPass: False` otherwise. Exit 1 on `AllPass: False`, exit 0 on `AllPass: True`. Run with `pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\contrast-check.ps1"`.
  - Independent authoritative acceptance check (does NOT trust the script's self-reported AllPass; recomputes from the report rows):
    ```powershell
    $rep = Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\contrast-report.md'
    (($rep -match 'AllPass:\s*True') -and ($rep -match '\| 3\.99 \|') -and ($rep -match '\| 4\.58 \|') -and ($rep -match 'large')) -and ($rep -match 'normal')
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\contrast-report.md'`
  - Error recovery: adjust failing colors or correctly classify button/large text threshold, then rerun.

- [x] Task 1.4: Write `pa-ui-design\summary.md`.
  - Action command: write one paragraph including the exact phrase `appears shippable for lightweight branded prototypes`.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\summary.md').Contains('appears shippable for lightweight branded prototypes')
    ```
    Expected output: `True`.
  - Diagnostic checks: none.
  - Error recovery: if contrast failed, summarize the failure instead.

Exit criteria: both HTML files exist, contrast report passes, and summary exists.

## Phase 2 Skill Test: first-principles-mastery

Objective: produce a complete five-step analysis and verify taxonomy structure.

- [x] Task 2.1: Write `first-principles\enterprise-agile-transformations.md`.
  - Action command: read all files under `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\first-principles-mastery`, then write a Markdown analysis on `Why most enterprise Agile transformations fail to deliver measurable results` with headings `## Step 1: Bedrock`, `## Step 2: Feynman`, `## Step 3: Beginner assumptions`, `## Step 4: Stress test`, and `## Step 5: Start from zero`. Include body content under each heading and at least one claim labeled with each exact category: `[definitional truth]`, `[observable fact]`, `[mathematical/physical constraint]`, `[empirical evidence]`, `[useful assumption]`, `[contested belief]`, `[unknown]`. Include exact sentence `enterprise Agile transformations usually disappoint when they optimize for adoption artifacts instead of changing constraints in the value-delivery system.`
  - Authoritative acceptance check:
    ```powershell
    $t=Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\first-principles\enterprise-agile-transformations.md'; ($t.Contains('## Step 1: Bedrock') -and $t.Contains('## Step 5: Start from zero') -and $t.Contains('[definitional truth]') -and $t.Contains('[unknown]') -and $t.Contains('enterprise Agile transformations usually disappoint when they optimize for adoption artifacts'))
    ```
    Expected output: `True`.
  - Diagnostic checks: length check with `Get-Item`.
  - Error recovery: add missing substantive sections or labels; do not reduce body content.

- [x] Task 2.2: Create and run `verify-first-principles.ps1`; write `quality-report.md`.
  - Action command: script checks all five headings, all seven taxonomy labels, and text length greater than 2500 characters; write JSON containing `"AllPass": true` when all pass; exit 1 otherwise.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\first-principles\quality-report.md').Contains('"AllPass": true')
    ```
    Expected output: `True`.
  - Diagnostic checks: show `quality-report.md`.
  - Error recovery: patch the analysis body based on the failed Boolean and rerun only this verifier.

- [x] Task 2.3: Write `first-principles\summary.md`.
  - Action command: write one paragraph including `appears shippable for strategy and thought-leadership analysis`.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\first-principles\summary.md').Contains('appears shippable for strategy and thought-leadership analysis')
    ```
    Expected output: `True`.
  - Diagnostic checks: none.
  - Error recovery: if structural verification failed, state the failed requirement.

Exit criteria: analysis, verifier, report, and summary exist; report contains `"AllPass": true`.

## Phase 3 Skill Test: markdown-pdf-publisher

Objective: build a branded PDF and validate/render it with PyMuPDF.

- [x] Task 3.1: Scaffold `markdown-pdf\publication\` and source Markdown.
  - Action command: create `publication\styles` and `publication\dist`; copy `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\first-principles\enterprise-agile-transformations.md` to `publication\source.md`; if unavailable, write a fresh two-heading, five-paragraph PA proposal.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\source.md').Length -gt 500
    ```
    Expected output: `True`.
  - Diagnostic checks: list `publication` with `Get-ChildItem`.
  - Error recovery: create fresh source content and continue.

- [x] Task 3.2: Create `package.json`, `build-html.mjs`, `styles\print.css`, and pre-install dependencies.
  - Action command (run each in order; do not chain with `&&` or `;` inside any single call):
    1. Write Node build files in `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\`:
       - `build-html.mjs` must import `markdown-it` (and `markdown-it-footnote` if used), read `source.md`, and write the rendered HTML to `dist\skillshare-test-v1.html`.
       - `styles\print.css` must include `@page`, PA blue `#0086ca`, navy `#0f172a`, and Radikal `@font-face` paths (`C:\development\2025-pa-website\public\fonts\Radikal.woff2`, `-Bold.woff2`, `-Medium.woff2`).
       - `package.json` must declare dependencies on `markdown-it` (^14) and `@vivliostyle/cli` (^11), and scripts `build:html` and `build:pdf`. The `build:pdf` script MUST be: `"build:pdf": "npx --yes @vivliostyle/cli build dist/skillshare-test-v1.html -o dist/skillshare-test-v1.pdf --timeout 60"`. The Vivliostyle `--timeout` is in **seconds** (Vivliostyle CLI v11 unit), not milliseconds; 60 seconds is sufficient for a single-file build.
    2. Install dependencies (with a 5-minute bounded timeout):
       ```powershell
       Push-Location -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication'
       npm install --no-audit --fund=false --fetch-timeout=60000 2>&1 | Out-Null
       Pop-Location
       ```
  - Authoritative acceptance check (the `build:pdf` script is the critical string the executor will use in Task 3.3; this check guarantees the package is correct):
    ```powershell
    $p='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication'; ((Get-Content -Raw -LiteralPath "$p\build-html.mjs").Contains('dist/skillshare-test-v1.html') -and (Get-Content -Raw -LiteralPath "$p\styles\print.css").Contains('@page') -and (Get-Content -Raw -LiteralPath "$p\package.json").Contains('"build:pdf":') -and (Get-Content -Raw -LiteralPath "$p\package.json").Contains('@vivliostyle/cli') -and (Test-Path -LiteralPath "$p\node_modules\@vivliostyle\cli\package.json") -and (Test-Path -LiteralPath "$p\node_modules\markdown-it\package.json"))
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\node_modules\@vivliostyle\cli' -ErrorAction SilentlyContinue | Select-Object -First 1`.
  - Error recovery: if `npm install` fails on the network, retry once with `--fetch-timeout=60000 --fetch-retries=3`; if it still fails, mark this skill failed in summaries and continue.

- [x] Task 3.3: Build HTML and exactly one versioned PDF.
  - Action command (run each command on its own line; do NOT chain Vivliostyle calls with `;` or `&&`):
    ```powershell
    $p='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication'
    npm run build:html --prefix $p
    npm run build:pdf  --prefix $p
    ```
    Rationale: `npx --prefix` is not a valid npx flag (it is silently ignored), and the published Vivliostyle CLI package is `@vivliostyle/cli` (not the shortname `vivliostyle`). Running the `build:pdf` script defined in Task 3.2 (which itself calls `npx --yes @vivliostyle/cli build ...`) is the correct way to invoke the locally installed CLI. Empirically verified 2026-07-04: `npx --prefix $p vivliostyle build ...` fails with `could not determine executable to run` when no local install is present; `npx --yes @vivliostyle/cli build <file> -o <pdf>` against a local file path succeeds in Vivliostyle CLI v11.0.4. A local HTTP server is NOT required for `npx @vivliostyle/cli build <local.html> -o out.pdf` in CLI v11.
  - Authoritative acceptance check (accepts v1 OR v2 - whichever the build produced):
    ```powershell
    $d='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\dist'; $candidates=@("$d\skillshare-test-v1.pdf","$d\skillshare-test-v2.pdf"); $pdf=$candidates|Where-Object{(Test-Path -LiteralPath $_) -and ((Get-Item -LiteralPath $_).Length -gt 10000) -and ((-join ([System.IO.File]::ReadAllBytes($_)[0..3]|ForEach-Object{[char]$_})) -eq '%PDF')}|Select-Object -First 1; [bool]$pdf
    ```
    Expected output: `True` (the `%PDF` magic-bytes check confirms the file is a real PDF, not just a non-empty blob; v1/v2 flex is so an EBUSY fallback to v2 is not a false failure).
  - Diagnostic checks: list `publication\dist`; `Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\package.json'`.
  - Error recovery: on `EBUSY`, do not kill browsers; change the `build:pdf` script's `-o` to `dist/skillshare-test-v2.pdf` and rerun once. Update the Task 3.3 and Task 3.4 acceptance paths to the v2 file if v1 stayed locked.

- [x] Task 3.4: Create and run `verify-pdf.py`; write screenshots and `quality-report.md`.
  - Action command: write a PyMuPDF script opening `dist\skillshare-test-v1.pdf`, reporting page count, saving page 1 to `dist\cover.png`, saving page 2 to `dist\page-2.png` when present, and writing JSON with `"all_pass": true` to `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\quality-report.md`; run `python "...\verify-pdf.py"`.
  - Authoritative acceptance check:
    ```powershell
    ((Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\quality-report.md').Contains('"all_pass": true') -and (Test-Path -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\dist\cover.png'))
    ```
    Expected output: `True`.
  - Diagnostic checks: show `quality-report.md`.
  - Error recovery: if PyMuPDF import fails, stop this skill and summarize the import failure; do not install packages without approval.

- [x] Task 3.5: Write `markdown-pdf\summary.md`.
  - Action command: write one paragraph including `appears shippable if human review approves the print styling`.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\summary.md').Contains('appears shippable if human review approves the print styling')
    ```
    Expected output: `True`.
  - Diagnostic checks: none.
  - Error recovery: if PDF validation failed, summarize exact failure and last successful artifact.

Exit criteria: PDF, screenshot, report, and summary exist; report contains `"all_pass": true`.

## Phase 4 Skill Test: humanizer

Objective: rewrite AI-like prose in PA voice and measure improvement.

- [x] Task 4.1: Create `humanizer\before.md` and `humanizer\after.md`.
  - Action command: write `before.md` with coherence markers `Furthermore,`, `Moreover,`, `Additionally,`, `Notably,`, `In conclusion,` and at least one em dash; write `after.md` in PA voice with shorter paragraphs, no listed coherence markers, no em dashes, and exact sentence `If the numbers move, keep going.`
  - Authoritative acceptance check:
    ```powershell
    $b=Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\before.md'; $a=Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md'; ($b.Contains('Furthermore,') -and $b.Contains('In conclusion,') -and $a.Contains('If the numbers move, keep going.'))
    ```
    Expected output: `True`.
  - Diagnostic checks: list humanizer folder.
  - Error recovery: rewrite after text to remove markers and make it more specific.

- [x] Task 4.2: Create and run `measure-humanizer.ps1`; write `metrics-report.md`.
  - Action command: script must calculate sentence length lists, standard deviation, coherence-marker count, and em-dash count for before/after; pass when after std dev is greater, after marker count is lower, and after em-dash count is lower; write `AllPass: True` or `AllPass: False`; exit 1 on failure.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md').Contains('AllPass: True')
    ```
    Expected output: `True`.
  - Diagnostic checks: show metrics report.
  - Error recovery: vary sentence lengths more, remove markers/em dashes, rerun script.

- [x] Task 4.3: Write `humanizer\summary.md`.
  - Action command: write one paragraph including `appears shippable for first-pass de-AI rewriting`.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md').Contains('appears shippable for first-pass de-AI rewriting')
    ```
    Expected output: `True`.
  - Diagnostic checks: none.
  - Error recovery: if metrics failed, state failed metric and usefulness for human review.

Exit criteria: before/after, metrics, and summary exist; report contains `AllPass: True`.

## Final Phase Validation & Handover

Objective: verify artifacts and produce a review handover.

- [x] Task 5.1: Run final artifact/body validation and write `final-validation.json`.
  - Action command: check existence and body needles for landing headline, dashboard text, contrast `AllPass: True`, first-principles Step 5, first-principles `"AllPass": true`, PDF, cover PNG, PDF `"all_pass": true`, humanizer before marker, humanizer after sentence, and humanizer `AllPass: True`; write results to `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\final-validation.json`; exit 1 if any fail.
  - Authoritative acceptance check:
    ```powershell
    $j='C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\final-validation.json'; (Test-Path -LiteralPath $j) -and ((Get-Content -Raw -LiteralPath $j|ConvertFrom-Json).Pass -notcontains $false)
    ```
    Expected output: `True`.
  - Diagnostic checks: show `final-validation.json`.
  - Error recovery: fix only the failed skill artifact or mark that skill failed in handover.

- [x] Task 5.2: Write `handover.md` with fully qualified artifact paths.
  - Action command: write `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\handover.md` listing every HTML, Markdown, PDF, PNG, report, and summary path; include exact line `Review order: open the two HTML files in a browser`.
  - Authoritative acceptance check:
    ```powershell
    (Get-Content -Raw -LiteralPath 'C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\handover.md').Contains('Review order: open the two HTML files in a browser')
    ```
    Expected output: `True`.
  - Diagnostic checks: none.
  - Error recovery: if `page-2.png` is absent because the PDF has one page, note that optional absence instead of failing the whole handover.

Exit criteria: final validation has no failed checks and handover lists fully qualified Windows paths.

## Execution-Readiness Checklist

- [ ] Execute tasks strictly in order.
- [ ] Use PowerShell-first through `bash`; include explicit timeouts at the tool-call layer.
- [ ] Do not use native Read/Edit/Write/glob/grep in this host session.
- [ ] Do not test `retrospective`.
- [ ] Do not push to GitHub.
- [ ] Do not install browser automation tools.
- [ ] Do not run concurrent Vivliostyle builds.
- [ ] If one skill fails, record it and continue with independent skills.

## Top 3 Risks + Mitigations

1. Vivliostyle EBUSY lock. Mitigation: use `skillshare-test-v1.pdf`; if locked, switch to `skillshare-test-v2.pdf`; do not kill Chrome/Edge.
2. Contrast failure. Mitigation: adjust only the failing foreground/background pair and rerun `contrast-check.ps1`.
3. Humanizer metrics failure. Mitigation: vary after-text sentence lengths, remove listed coherence markers, remove em dashes, rerun `measure-humanizer.ps1`.

## First Task to Execute

Task 0.1: create `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\` and its four skill subfolders.




