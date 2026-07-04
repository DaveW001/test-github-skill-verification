# Spec: Test Packaged Agile Skillshare Skills

Track ID: `test-skillshare-skills`
Created: 2026-07-04
Stage 1 model: `gpt-5.5`

## Goal / Outcome

Test 4 of the 5 skills in the `packaged-agile/skillshare-skills` repository by exercising each included skill end-to-end and producing reviewable artifacts plus deterministic quality gauges. The excluded skill is `retrospective`, which is already tested.

The repository under test is already cloned at:

`C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills`

All test outputs must be written under:

`C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\`

Each included skill gets its own independent output subfolder:

- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\pa-ui-design\`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\first-principles\`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\`

## Constraints / Non-goals

- Do not test the `retrospective` skill.
- Do not push anything to GitHub.
- Do not install Playwright, Puppeteer, or Selenium.
- Keep every skill test independent so one failure does not block the others.
- Use standalone HTML for `pa-ui-design`; do not scaffold a Next.js app.
- For PDF visual checks, use PyMuPDF screenshots, not browser automation.
- Never run more than one Vivliostyle build at a time.
- Do not kill Chrome or Edge processes.
- Start any local server in the background with a bounded wait and clean it up by process id when the task ends.
- Keep every shell/network command bounded with an explicit timeout or non-interactive flag. Never use `Read-Host`, `Wait-Process`/`-Wait`, `tail -f`, `Start-Process -Wait`, uncapped servers, or blocking prompts.

## Host Tool Preconditions to Propagate

- Native file tools are broken in this host state: Read/Edit/Write/glob/grep return `Bun is not defined`.
- Use PowerShell-first via the `bash` tool for all file operations.
- Always use `-LiteralPath` and double-quoted Windows paths.
- Do not retry native file tools per-call.
- Read files with `Get-Content -Raw`.
- Write files with `Set-Content -Encoding utf8` or bounded here-strings.
- Locate text with `Select-String`; prefer `-SimpleMatch`, `[regex]::Escape()`, and `[string]::Contains()` over fragile regex.
- For structural assertions, use anchored full-line patterns where appropriate.
- If any anomaly occurs during execution, append exactly one JSONL line to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` with keys: `stage`, `timestamp_utc`, `type`, `severity`, `attempted_model`, `detail`, `action_taken`.

## Skills Under Test

### 1. `pa-ui-design`

Deliverables:

- `landing.html`: PA marketing landing page with hero, feature cards, CTA, and footer.
- `dashboard.html`: PA dashboard or pricing page with sidebar/nav and data table or pricing cards.
- `contrast-check.ps1`: deterministic contrast checker.
- `contrast-report.md`: WCAG contrast report.
- `summary.md`: one paragraph on how well the skill works.

Required design evidence:

- PA primary blue `#0086ca` and hover blue `#147bbb`.
- PA Radikal fonts loaded from `C:\development\2025-pa-website\public\fonts\`.
- PA logo from `C:\development\2025-pa-website\graphics\Logo 02.png`.
- Section dividers.
- Card hover motion equivalent to `duration-300` and `hover:scale-105`.
- Button hover motion equivalent to `duration-200` and `hover:scale-105`.
- Mobile-first layout.
- Keyboard-accessible focus states.

Quality gauge:

- Compute WCAG contrast ratios for every color pair used in the sample pages.
- Assert AA threshold: 4.5:1 for normal text and 3:1 for large text/UI text.

### 2. `first-principles-mastery`

Deliverables:

- `enterprise-agile-transformations.md`: full 5-step Full Mastery Stack output on the topic `Why most enterprise Agile transformations fail to deliver measurable results`.
- `verify-first-principles.ps1`: structural verifier.
- `quality-report.md`: verification result.
- `summary.md`: one paragraph on how well the skill works.

Required content evidence:

- Step 1: Bedrock.
- Step 2: Feynman.
- Step 3: Beginner assumptions.
- Step 4: Stress test.
- Step 5: Start from zero.
- Claims classified with the seven verification-rule categories: `definitional truth`, `observable fact`, `mathematical/physical constraint`, `empirical evidence`, `useful assumption`, `contested belief`, and `unknown`.

Quality gauge:

- Verify all five sections exist and include body content.
- Verify all seven claim categories appear at least once.
- Verify output is non-empty and substantial.

### 3. `markdown-pdf-publisher`

Deliverables:

- `publication\source.md`: Markdown source document.
- `publication\package.json`: local build scripts.
- `publication\build-html.mjs`: Markdown-to-HTML builder.
- `publication\styles\print.css`: PA print stylesheet.
- `publication\dist\skillshare-test-v1.html`: generated HTML.
- `publication\dist\skillshare-test-v1.pdf`: generated PDF.
- `publication\dist\cover.png`: cover-page screenshot extracted from PDF.
- `publication\dist\page-2.png`: content-page screenshot extracted from PDF when page count permits.
- `publication\verify-pdf.py`: PyMuPDF PDF validator and screenshot extractor.
- `quality-report.md`: PDF quality report.
- `summary.md`: one paragraph on how well the skill works.

Quality gauge:

- PyMuPDF opens the PDF.
- Page count is greater than zero.
- Cover page PNG is written.
- A content page PNG is written when a second page exists.

### 4. `humanizer`

Deliverables:

- `before.md`: deliberately AI-sounding source prose.
- `after.md`: humanized PA-voice rewrite.
- `measure-humanizer.ps1`: metrics script.
- `metrics-report.md`: before/after table.
- `summary.md`: one paragraph on how well the skill works.

Quality gauge:

- Sentence-length standard deviation increases after rewriting.
- Coherence marker count decreases after rewriting.
- Em-dash count decreases after rewriting.

## Definition of Done

For each of the 4 included skills, a reviewable artifact exists, a quality gauge has run and produced a result, and a one-paragraph `summary.md` states how well the skill works. The final handover file lists all artifacts with fully qualified Windows paths and describes any failures without blocking unrelated skill tests.
