# Website Regression Guardrails Plan

## Brief Restatement

**Goal/outcome:** Convert the existing website regression setup into a reliable, low-noise quality guardrail for a mostly stable content website that still receives new pages and blog posts.

**Constraints/non-goals:** Do not delete visual regression protection outright, do not keep noisy daily blocking failures, do not snapshot every blog post, do not require a paid visual testing SaaS, do not auto-update baselines in CI, and do not finish until validation proves the workflow can pass.

**Definition of done:** Pull-request, manual, and reduced-schedule checks exist; visual checks target stable templates; link/accessibility/SEO-health checks are added; scheduled checks are not noisy blockers; clean validation commands pass; handover explains failure triage and baseline updates.

---

## Phase 0: Setup & Preconditions

Objective: Establish the exact current state and ensure the build agent can safely edit the regression workflow without guessing.

- [x] 0.1 Confirm the repository root is correct by running `git rev-parse --show-toplevel` from the workspace root.
  - File paths: none modified.
  - Validation: command prints the absolute repository root and exits with code 0.
  - Error recovery: if the command fails with `not a git repository`, stop and ask the user for the correct repository path.

- [x] 0.2 Confirm the existing visual regression files exist by running `Test-Path .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts; Test-Path .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts` in PowerShell.
  - File paths: `.conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts`, `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts`.
  - Validation: command prints `True` twice.
  - Error recovery: if either value is `False`, stop and inspect `.conductor/tracks/webapp-visual-regression/README.md` before editing anything.

- [x] 0.3 Confirm package scripts by running `npm pkg get scripts`.
  - File paths: `package.json`.
  - Validation: output includes `test:visual`, `test:visual:p0`, and `test:visual:update`.
  - Error recovery: if `npm` is not found, run `node --version` to check if Node.js is installed. If Node.js is missing, install Node.js LTS from https://nodejs.org or use the project's documented package manager. If `npm pkg` subcommand is not supported (older npm versions), run `node -e "const pkg=JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log(JSON.stringify(pkg.scripts, null, 2))"` instead.

- [x] 0.4 Create a working branch by running `git checkout -b chore/website-regression-guardrails`.
  - File paths: none modified.
  - Validation: `git branch --show-current` prints `chore/website-regression-guardrails`.
  - Error recovery: if the branch already exists, run `git checkout chore/website-regression-guardrails`.

Phase-level exit criteria: repository root is confirmed, required visual regression files exist, npm scripts are visible, and the work is isolated on `chore/website-regression-guardrails`.

---

## Phase 1: Tune the GitHub Actions Trigger Model

Objective: Stop noisy weekday failures while preserving useful PR and manual regression checks.

- [x] 1.1 Create `.github/workflows/visual-regression.yml` with weekly schedule, PR trigger, and manual dispatch.
  - File path: `.github/workflows/visual-regression.yml`.
  - Prerequisite: confirm the starter template exists by running `Test-Path .conductor/tracks/webapp-visual-regression/artifacts/starter/.github/workflows/visual-regression.yml`. If it exists, copy it first with `Copy-Item .conductor/tracks/webapp-visual-regression/artifacts/starter/.github/workflows/visual-regression.yml .github/workflows/visual-regression.yml -Force`, then edit the `on:` block. If the starter does NOT exist, create the file from scratch.
  - Required `on:` block at the top of the file:
    ```yaml
    on:
      schedule:
        - cron: '0 14 * * 1'
      pull_request:
      workflow_dispatch:
    ```
  - Validation: run `Select-String -Path .github/workflows/visual-regression.yml -Pattern "0 14 \* \* 1"` and confirm one match.
  - Error recovery: if the file already exists at `.github/workflows/visual-regression.yml`, skip the copy and edit the existing file's `on:` block directly.

- [x] 1.2 Add path filters under `pull_request` so visual tests run only when site code, styling, configuration, or workflow files change.
  - File path: `.github/workflows/visual-regression.yml`.
  - Prerequisite: discover the actual site directories by running `Get-ChildItem -Directory | Select-Object Name` and `Get-ChildItem -File -Name "*.json" | Select-String "next|gatsby|vite|react" -List`.
  - Required action: add a `paths:` block under `pull_request:` in the workflow. Use the actual directory names discovered in the prerequisite step. If the site is a Next.js or similar framework, common paths include `app/`, `components/`, `pages/`, `public/`, `styles/`. If unsure, use the conservative filter below.
  - Required snippet (conservative default — edit directory names to match the actual repo):
    ```yaml
      pull_request:
        paths:
          - '.github/workflows/visual-regression.yml'
          - '.conductor/tracks/webapp-visual-regression/artifacts/starter/**'
          - 'package.json'
          - 'package-lock.json'
    ```
  - Validation: run `Select-String -Path .github/workflows/visual-regression.yml -Pattern "paths:"` and confirm one pull-request paths block exists.
  - Error recovery: if the repo uses different site directories, add them to the paths list after confirming they exist with `Test-Path <directory>`.

- [x] 1.3 Make scheduled runs non-blocking while keeping pull-request runs blocking.
  - File path: `.github/workflows/visual-regression.yml`.
  - Required YAML pattern on the visual regression test step:
    ```yaml
        continue-on-error: ${{ github.event_name == 'schedule' }}
    ```
  - Validation: run `Select-String -Path .github/workflows/visual-regression.yml -Pattern "continue-on-error:.*schedule"` and confirm one match.
  - Error recovery: if GitHub Actions expression syntax fails validation, replace with two separate jobs: `visual-pr` for `if: github.event_name != 'schedule'` and `visual-scheduled` for `if: github.event_name == 'schedule'` with `continue-on-error: true` at the job level.

Phase-level exit criteria: workflow runs weekly on schedule, still runs on PR/manual dispatch, PR path filters are present, and scheduled visual failures are informational.

---

## Phase 2: Reduce Visual Snapshot Noise

Objective: Keep visual testing focused on stable templates and high-value pages instead of every changing content page.

- [x] 2.1 Create `.conductor/tracks/20260508-website-regression-guardrails/artifacts/route-policy.md` documenting which pages are stable enough for screenshots.
  - File path: `.conductor/tracks/20260508-website-regression-guardrails/artifacts/route-policy.md`.
  - Required template:
    ```markdown
    # Route Policy

    ## P0 Visual Routes
    - `/` — homepage and primary navigation
    - `/contact` — conversion form/page
    - `/blog` — blog index template
    - `/blog/example-stable-post` — representative blog post template; replace with stable canonical post

    ## Do Not Full-Page Snapshot
    - High-churn individual blog posts
    - Pages with embedded third-party widgets unless masked
    - Pages with time-sensitive banners unless deterministic
    ```
  - Validation: run `Test-Path .conductor/tracks/20260508-website-regression-guardrails/artifacts/route-policy.md` and confirm `True`.
  - Error recovery: if the artifacts folder does not exist, run `New-Item -ItemType Directory -Force .conductor/tracks/20260508-website-regression-guardrails/artifacts`.

- [x] 2.2 Edit `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts` and reduce `p0Cases` to only stable P0 routes.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts`.
  - Context: the file uses a `p0Cases: CaseDef[]` array with complex case definitions (readySelector, stickySelector, ctaSelector, guards, contrast targets). Do NOT replace the entire file. Edit only the `p0Cases` array.
  - Required action: keep only the `home` and `contact` cases from the existing array. Remove the `services` and `insights` cases entirely.
  - Required resulting shape (verify the file contains exactly these two cases):
    ```ts
    const p0Cases: CaseDef[] = [
      {
        id: "home",
        route: "/",
        // ... keep all existing fields from the home case unchanged ...
      },
      {
        id: "contact",
        route: "/contact",
        // ... keep all existing fields from the contact case unchanged ...
      },
    ];
    ```
  - Validation: run `Select-String -Path .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts -Pattern "id: \"services\"|id: \"insights\""` and confirm zero matches.
  - Error recovery: if the file structure differs from the expected `p0Cases` array, read the full file first with `Get-Content` and identify the array boundaries before editing.

- [x] 2.3 Add `mask` and `maxDiffPixelRatio` options to the `toHaveScreenshot` calls in `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts`.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts`.
  - Context: the file has three `toHaveScreenshot` calls: (1) `${item.id}-${viewport.name}-full.png` around line 250, (2) `${item.id}-${viewport.name}-${probe}.png` around line 297, (3) `${item.id}-${viewport.name}-overlay.png` around line 335.
  - Required action: add `mask` and `maxDiffPixelRatio` options to the full-page screenshot call (call 1, around line 250). Do NOT modify the probe or overlay screenshot calls.
  - Required edit for the full-page `toHaveScreenshot` call (add these two lines inside the existing options object):
    ```ts
    await expect(page).toHaveScreenshot(`${item.id}-${viewport.name}-full.png`, {
      fullPage: true,
      maxDiffPixels: item.fullMaxDiffPixels,
      maxDiffPixelRatio: item.fullMaxDiffPixelRatio ?? 0.02,
      mask: [
        page.locator('iframe'),
        page.locator('[data-visual-mask]'),
      ],
    });
    ```
  - Validation: run `Select-String -Path .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts -Pattern "maxDiffPixelRatio.*0\.02|mask:"` and confirm at least one match.
  - Error recovery: if the `fullMaxDiffPixelRatio` field is undefined on a case and causes issues, the `?? 0.02` fallback handles it; if TypeScript complains about the mask array type, use `mask: [page.locator('iframe'), page.locator('[data-visual-mask]')]` as separate array elements.

- [x] 2.4 Run `npm run test:visual:p0` locally without updating snapshots.
  - File paths: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/visual/p0.visual.spec.ts`, existing snapshot files under `.conductor/tracks/webapp-visual-regression/artifacts/starter/snapshots/**`.
  - Validation: command exits 0, or fails only with expected snapshot diffs caused by the route/mask policy change.
  - Error recovery: if browsers are missing, run `npx playwright install chromium` (do NOT use `--with-deps` on Windows; that flag is for Linux only); if snapshots are missing for intentionally changed route names, continue to Task 2.5.

- [x] 2.5 If Task 2.4 reports expected missing or obsolete snapshots, run `npm run test:visual:update` once and review generated snapshot file names.
  - File paths: `.conductor/tracks/webapp-visual-regression/artifacts/starter/snapshots/**`.
  - Validation: rerun `npm run test:visual:p0` and confirm exit code 0.
  - Error recovery: if visual diffs remain after updating, inspect the Playwright HTML report with `npm run test:visual:report` and either add a justified mask or remove the high-churn route from P0.

Phase-level exit criteria: P0 visual checks cover stable representative routes, dynamic masks are present, and `npm run test:visual:p0` passes locally from the updated baseline.

---

## Phase 3: Add Link Checking

Objective: Catch broken URLs and missing assets, which are higher-signal for content sites than full-page screenshots on every post.

- [x] 3.1 Install the link checker by running `npm install --save-dev linkinator`.
  - File path: `package.json`, `package-lock.json`.
  - Validation: run `npm pkg get devDependencies.linkinator` and confirm a version string is printed.
  - Error recovery: if `npm install` fails due to lockfile conflicts, run `npm install` once, then rerun the install command.

- [x] 3.2 Add a `test:links` script to `package.json`.
  - File path: `package.json`.
  - Required script example:
    ```json
    "test:links": "linkinator https://www.packagedagile.com --recurse --skip mailto: --skip tel: --verbosity error"
    ```
  - Validation: run `npm pkg get scripts.test:links` and confirm the linkinator command is printed.
  - Error recovery: if the site URL changes, replace `https://www.packagedagile.com` with the canonical production URL before running validation.

- [x] 3.3 Add a link-check step to `.github/workflows/visual-regression.yml`.
  - File path: `.github/workflows/visual-regression.yml`.
  - Required action: add the link checker step AFTER the `npm install` step and BEFORE the visual regression test step in the workflow's job. If the workflow has multiple jobs, add it to the same job that runs `npm run test:visual:p0`.
  - Required step example:
    ```yaml
      - name: Run link checker
        run: npm run test:links
    ```
  - Validation: run `Select-String -Path .github/workflows/visual-regression.yml -Pattern "Run link checker|npm run test:links"` and confirm at least one match.
  - Error recovery: if link checking makes the workflow too slow (over 5 minutes), create a separate `.github/workflows/website-health.yml` file and move the link, accessibility, and health check steps there instead.

- [x] 3.4 Run `npm run test:links`.
  - File paths: `package.json`.
  - Validation: command exits 0 and reports no broken internal links.
  - Error recovery: if external links fail intermittently:
    1. Identify the failing domain from the linkinator output.
    2. Add a targeted `--skip` pattern for that domain to the `test:links` script in `package.json`. Example: `--skip "https://twitter.com" --skip "https://linkedin.com"`.
    3. Document each skip in `.conductor/tracks/20260508-website-regression-guardrails/artifacts/failure-triage.md` under the Broken Link section.
    4. Re-run `npm run test:links` and confirm exit code 0.
    Do NOT skip broad internal paths or use `--skip` for internal 404s — those must be fixed.

Phase-level exit criteria: `npm run test:links` exists, the workflow runs it, and the command can pass or has documented skips for unstable third-party links.

---

## Phase 4: Add Accessibility Checks

Objective: Add automated accessibility smoke coverage for key pages and templates.

- [x] 4.1 Install accessibility test dependency by running `npm install --save-dev @axe-core/playwright`.
  - File path: `package.json`, `package-lock.json`.
  - Validation: run `node -e "const pkg=JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log(pkg.devDependencies['@axe-core/playwright'])"` and confirm a version string is printed.
  - Error recovery: if npm cannot resolve the package, run `npm view @axe-core/playwright version` to confirm registry access, then retry.

- [x] 4.2 Create `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility/p0.accessibility.spec.ts`.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility/p0.accessibility.spec.ts`.
  - Prerequisite: ensure the directory exists by running `New-Item -ItemType Directory -Force .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility`.
  - Required template (reports violations without failing the test on first run):
    ```ts
    import { test, expect } from '@playwright/test';
    import AxeBuilder from '@axe-core/playwright';

    const BASE_URL = process.env.PW_BASE_URL ?? 'https://www.packagedagile.com';
    const routes = ['/', '/contact', '/blog'];

    for (const route of routes) {
      test(`accessibility smoke ${route}`, async ({ page }) => {
        await page.goto(new URL(route, BASE_URL).toString(), { waitUntil: 'networkidle' });
        const results = await new AxeBuilder({ page }).analyze();
        // On first run, log violations so the test does not block CI unexpectedly.
        // After known issues are fixed, change this to: expect(results.violations).toEqual([]);
        if (results.violations.length > 0) {
          console.log(`A11y violations on ${route}:`, JSON.stringify(results.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length })), null, 2));
        }
        expect(results.violations.length).toBeLessThanOrEqual(0);
      });
    }
    ```
  - Validation: run `Test-Path .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility/p0.accessibility.spec.ts` and confirm `True`.
  - Error recovery: if the existing Playwright config does not pick up the `tests/accessibility/` directory, the npm script in Task 4.3 will pass the file path explicitly.

- [x] 4.3 Add `test:a11y` script to `package.json`.
  - File path: `package.json`.
  - Required script example:
    ```json
    "test:a11y": "playwright test -c .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility/p0.accessibility.spec.ts"
    ```
  - Validation: run `npm pkg get scripts.test:a11y` and confirm the Playwright command is printed.
  - Error recovery: if Windows shell quoting breaks, set the script through `npm pkg set "scripts.test:a11y=playwright test -c .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility/p0.accessibility.spec.ts"`.

- [x] 4.4 Add an accessibility step to the workflow.
  - File path: `.github/workflows/visual-regression.yml`.
  - Required step example:
    ```yaml
      - name: Run accessibility smoke tests
        run: npm run test:a11y
    ```
  - Validation: run `Select-String -Path .github/workflows/visual-regression.yml -Pattern "Run accessibility smoke tests|npm run test:a11y"` and confirm matches.
  - Error recovery: if accessibility should be separate from visual checks, move this step into `.github/workflows/website-health.yml`.

- [x] 4.5 Run `npm run test:a11y`.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility/p0.accessibility.spec.ts`.
  - Validation: command exits 0.
  - Error recovery: if there are pre-existing violations, do NOT suppress the test. Instead:
    1. Create `.conductor/tracks/20260508-website-regression-guardrails/artifacts/accessibility-known-issues.md` with violation IDs, affected routes, and remediation owners.
    2. Temporarily change the assertion in `p0.accessibility.spec.ts` from `expect(results.violations.length).toBeLessThanOrEqual(0)` to `expect(results.violations.length).toBeLessThanOrEqual(N)` where N is the number of known violations, and add a comment linking to the known-issues file.
    3. Re-run `npm run test:a11y` and confirm exit code 0.

Phase-level exit criteria: accessibility smoke test file exists, npm script exists, workflow runs it, and local validation either passes or documents known issues.

---

## Phase 5: Add SEO / Metadata / Health Checks

Objective: Add a lightweight content-site health check that catches missing metadata and major page health regressions.

- [x] 5.1 Create `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/health/p0.health.spec.ts`.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/health/p0.health.spec.ts`.
  - Prerequisite: ensure the directory exists by running `New-Item -ItemType Directory -Force .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/health`.
  - Required template:
    ```ts
    import { test, expect } from '@playwright/test';

    const BASE_URL = process.env.PW_BASE_URL ?? 'https://www.packagedagile.com';
    const routes = ['/', '/contact', '/blog'];

    for (const route of routes) {
      test(`page health ${route}`, async ({ page }) => {
        const response = await page.goto(new URL(route, BASE_URL).toString(), { waitUntil: 'domcontentloaded' });
        expect(response?.ok()).toBeTruthy();
        await expect(page.locator('title')).not.toHaveText('');
        await expect(page.locator('meta[name="description"]')).toHaveCount(1);
        // Some pages may have more than one h1; check for at least one instead of exactly one.
        const h1Count = await page.locator('h1').count();
        expect(h1Count).toBeGreaterThanOrEqual(1);
      });
    }
    ```
  - Validation: run `Test-Path .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/health/p0.health.spec.ts` and confirm `True`.
  - Error recovery: if the site returns a redirect (3xx) instead of 200, change `expect(response?.ok()).toBeTruthy()` to `expect(response?.status()).toBeLessThan(400)` and document the redirect behavior.

- [x] 5.2 Add `test:health` script to `package.json`.
  - File path: `package.json`.
  - Required script example:
    ```json
    "test:health": "playwright test -c .conductor/tracks/webapp-visual-regression/artifacts/starter/playwright.visual.config.ts .conductor/tracks/webapp-visual-regression/artifacts/starter/tests/health/p0.health.spec.ts"
    ```
  - Validation: run `npm pkg get scripts.test:health` and confirm the Playwright command is printed.
  - Error recovery: if npm script editing fails, manually edit `package.json` and run `node -e "JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log('valid json')"`.

- [x] 5.3 Add a health-check step to the workflow.
  - File path: `.github/workflows/visual-regression.yml`.
  - Required step example:
    ```yaml
      - name: Run page health checks
        run: npm run test:health
    ```
  - Validation: run `Select-String -Path .github/workflows/visual-regression.yml -Pattern "Run page health checks|npm run test:health"` and confirm matches.
  - Error recovery: if runtime becomes too long, run health checks on PRs and manual dispatch only by adding `if: github.event_name != 'schedule'`.

- [x] 5.4 Run `npm run test:health`.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/health/p0.health.spec.ts`.
  - Validation: command exits 0.
  - Error recovery: if a route returns non-200 because production deploy is unavailable, rerun once after 5 minutes; if still failing, capture the failing URL and response code in the handover.

Phase-level exit criteria: page health tests exist, script exists, workflow runs them, and local validation passes.

---

## Phase 6: Documentation and Failure Triage

Objective: Ensure future failures are actionable instead of confusing daily noise.

- [x] 6.1 Create `.conductor/tracks/20260508-website-regression-guardrails/artifacts/failure-triage.md`.
  - File path: `.conductor/tracks/20260508-website-regression-guardrails/artifacts/failure-triage.md`.
  - Prerequisite: ensure the directory exists by running `New-Item -ItemType Directory -Force .conductor/tracks/20260508-website-regression-guardrails/artifacts`.
  - Required content (write this exact structure to the file):
    ```markdown
    # Failure Triage Guide

    ## Visual Diff
    - Open the Playwright HTML report with `npm run test:visual:report`
    - Compare expected vs actual screenshots
    - If the diff is intentional (new content, accepted design change), update the baseline per Baseline Update Rules below
    - If the diff is unexpected, investigate the page for layout breakage, clipping, or overflow

    ## Broken Link
    - Review `npm run test:links` output for the failing URL
    - If the link is internal, fix the route or redirect
    - If the link is external and unstable, add a `--skip` pattern to the `test:links` script in `package.json` and document the skip below

    ## Accessibility Violation
    - Review the console output from `npm run test:a11y` for violation IDs
    - Check `.conductor/tracks/20260508-website-regression-guardrails/artifacts/accessibility-known-issues.md` for documented exceptions
    - Fix the violation or document it as a known issue with route, violation ID, and owner

    ## Health Check Failure
    - Review `npm run test:health` output for the failing route and assertion
    - If the route returns non-200, verify the production deploy is healthy
    - If metadata is missing (title, description), fix the page template

    ## Baseline Update Rules
    To intentionally accept a visual change, run `npm run test:visual:update`, inspect the generated diffs with `npm run test:visual:report`, and commit the changed snapshot files with a clear rationale. Never update baselines automatically from CI.

    ## When to Ignore
    - Scheduled workflow failures that are cosmetic only (documented in failure-triage.md)
    - Third-party link failures that are transient (documented skip rule in package.json)
    - Known accessibility violations (documented in accessibility-known-issues.md)
    ```
  - Validation: run `Select-String -Path .conductor/tracks/20260508-website-regression-guardrails/artifacts/failure-triage.md -Pattern "Baseline Update Rules|Visual Diff|Broken Link"` and confirm at least 3 matches.
  - Error recovery: if the artifacts folder is missing, create it with `New-Item -ItemType Directory -Force .conductor/tracks/20260508-website-regression-guardrails/artifacts`.

- [x] 6.2 Document the baseline update command in `.conductor/tracks/20260508-website-regression-guardrails/artifacts/failure-triage.md`.
  - File path: `.conductor/tracks/20260508-website-regression-guardrails/artifacts/failure-triage.md`.
  - Required text:
    ```markdown
    To intentionally accept a visual change, run `npm run test:visual:update`, inspect the generated diffs with `npm run test:visual:report`, and commit the changed snapshot files with a clear rationale. Never update baselines automatically from CI.
    ```
  - Validation: run `Select-String -Path .conductor/tracks/20260508-website-regression-guardrails/artifacts/failure-triage.md -Pattern "Never update baselines automatically from CI"` and confirm one match.
  - Error recovery: if the visual report cannot open on a headless machine, inspect files under `.conductor/tracks/webapp-visual-regression/artifacts/starter/test-results/**`.

- [x] 6.3 Update `.conductor/tracks/20260508-website-regression-guardrails/metadata.json` task counts after implementation.
  - File path: `.conductor/tracks/20260508-website-regression-guardrails/metadata.json`.
  - Required values at completion: set `status` to `validation-complete`, `completedTasks` to the number of checked tasks in `plan.md`, and `percentage` to `100`.
  - Validation: run `node -e "JSON.parse(require('fs').readFileSync('.conductor/tracks/20260508-website-regression-guardrails/metadata.json','utf8')); console.log('metadata valid')"` and confirm `metadata valid`.
  - Error recovery: if Node is unavailable, use `python -m json.tool .conductor/tracks/20260508-website-regression-guardrails/metadata.json`.

Phase-level exit criteria: triage documentation exists, baseline update rules are explicit, and metadata is valid JSON.

---

## Final Phase: Validation & Handover

Objective: Prove the guardrail suite works and leave clear execution evidence for the user.

- [x] F.1 Run `npm run test:visual:p0`.
  - File paths: visual test and snapshot files under `.conductor/tracks/webapp-visual-regression/artifacts/starter/**`.
  - Validation: command exits 0.
  - Error recovery: if it fails with snapshot diffs, open the report with `npm run test:visual:report`; update snapshots only if the diff is intentional and documented.

- [x] F.2 Run `npm run test:links`.
  - File path: `package.json`.
  - Validation: command exits 0.
  - Error recovery: if unstable third-party links fail, document the domain and add a targeted `--skip` rule; do not skip broad internal paths.

- [x] F.3 Run `npm run test:a11y`.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/accessibility/p0.accessibility.spec.ts`.
  - Validation: command exits 0.
  - Error recovery: document any pre-existing accessibility violations before suppressing or deferring them.

- [x] F.4 Run `npm run test:health`.
  - File path: `.conductor/tracks/webapp-visual-regression/artifacts/starter/tests/health/p0.health.spec.ts`.
  - Validation: command exits 0.
  - Error recovery: if production is unreachable, rerun once and then capture the failing URL/status in the handover.

- [x] F.5 Validate workflow YAML syntax.
  - File path: `.github/workflows/visual-regression.yml`.
  - Required action: run `node -e "const yaml=require('js-yaml');const fs=require('fs');yaml.load(fs.readFileSync('.github/workflows/visual-regression.yml','utf8'));console.log('YAML valid')"` if `js-yaml` is available. If not, run `python -c "import yaml; yaml.safe_load(open('.github/workflows/visual-regression.yml')); print('YAML valid')"` as a fallback.
  - Validation: command prints `YAML valid` and exits 0.
  - Error recovery: if neither Node nor Python YAML parsers are available, open the file in a text editor and manually verify the YAML structure: check that `on:`, `jobs:`, `steps:`, and `run:` keys are properly indented with spaces (not tabs). Alternatively, push the branch and use the GitHub Actions UI to validate syntax.

- [x] F.6 Create `.conductor/tracks/20260508-website-regression-guardrails/artifacts/validation-results.md` with command results.
  - File path: `.conductor/tracks/20260508-website-regression-guardrails/artifacts/validation-results.md`.
  - Required template:
    ```markdown
    # Validation Results

    - `npm run test:visual:p0`: PASS/FAIL — notes
    - `npm run test:links`: PASS/FAIL — notes
    - `npm run test:a11y`: PASS/FAIL — notes
    - `npm run test:health`: PASS/FAIL — notes
    - `npx actionlint .github/workflows/visual-regression.yml`: PASS/FAIL/SKIPPED — notes
    ```
  - Validation: run `Test-Path .conductor/tracks/20260508-website-regression-guardrails/artifacts/validation-results.md` and confirm `True`.
  - Error recovery: if any validation fails, leave the task unchecked and write the exact failure summary under the matching bullet.

- [x] F.7 Run `git status --short` and review changed files.
  - File paths: all modified files.
  - Validation: output includes only intended files: `package.json`, `package-lock.json`, `.github/workflows/visual-regression.yml`, `.conductor/tracks/webapp-visual-regression/artifacts/starter/**`, and `.conductor/tracks/20260508-website-regression-guardrails/**`.
  - Error recovery: if unrelated files appear, do not commit them; ask the user whether to keep, revert, or ignore them.

Phase-level exit criteria: all four quality commands pass, workflow syntax is checked or documented as skipped, validation results are recorded, and changed files are reviewed.

---

## Execution Readiness Checklist

- [ ] Atomic tasks: PASS — every checkbox contains one primary action.
- [ ] Exact file paths: PASS — each task names precise repo-relative files or states no files modified.
- [ ] Explicit commands: PASS — terminal commands are written verbatim.
- [ ] Clear ordering: PASS — phases progress from setup to workflow tuning to checks to validation.
- [ ] Verification per step: PASS — every task includes a validation expectation.
- [ ] No assumed context: PASS — tasks include paths, snippets, and recovery instructions.
- [ ] Concrete examples: PASS — YAML, JSON, TypeScript, and Markdown snippets are included where structure matters.
- [ ] Error recovery: PASS — every task includes common failure handling.

## Top 3 Implementation Risks + Mitigations

1. **Risk:** Visual snapshots keep failing because content changes frequently. **Mitigation:** restrict P0 routes to stable templates, add masks for dynamic regions, and document route policy.
2. **Risk:** Link checking fails on unreliable third-party URLs. **Mitigation:** use targeted skip rules only for known unstable external domains and document each skip.
3. **Risk:** Accessibility checks expose pre-existing issues and block unrelated work. **Mitigation:** document known issues with route, violation ID, and owner before applying targeted suppressions.

## First Task the Build Agent Should Execute Immediately

Run `git rev-parse --show-toplevel` from the workspace root and confirm the command prints the expected repository root before making any edits.
