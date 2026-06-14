# Website Regression Guardrails Spec

## Goal / Outcome

Create a practical, low-noise regression testing setup for a mostly stable public website that still receives new pages, blog posts, and occasional template/style changes. The finished system should catch real website breakage before or shortly after release without producing daily unavoidable failures.

## Constraints / Non-Goals

- Do not delete the existing visual regression capability unless an equivalent replacement is already working.
- Do not keep the current weekday scheduled workflow as a blocking failure if it repeatedly fails due to accepted content or baseline drift.
- Do not require a hosted visual testing SaaS product for the first implementation.
- Do not test every individual blog post with brittle full-page screenshots.
- Do not automatically approve or overwrite screenshot baselines in CI.
- Do not execute this plan while authoring this track; this track is a handoff artifact for a build agent.

## Definition of Done

- The repository has a tuned GitHub Actions workflow at `.github/workflows/visual-regression.yml` that runs on pull requests, manual dispatch, and a reduced scheduled cadence.
- Scheduled workflow runs are informational/non-blocking or clearly marked so they do not create daily noisy failure pressure.
- Visual coverage is limited to stable representative templates and critical conversion pages.
- Dynamic or frequently changing content regions are masked or excluded from screenshot assertions where practical.
- Link checking is available through an explicit npm script and CI job/step.
- Accessibility checking is available through an explicit npm script and CI job/step.
- SEO/metadata or Lighthouse-style health checking is available through an explicit npm script and CI job/step where feasible.
- A validation run proves the guardrails can pass from a clean checkout before the work is considered complete.
- The final handover documents how to interpret failures, update baselines intentionally, and recover from common problems.

## Background

The existing `webapp-visual-regression` Conductor track created Playwright screenshot testing for `https://www.packagedagile.com`. The current GitHub Actions workflow runs every weekday and fails on screenshot diffs such as `insights-mobile-narrow-full.png`. That means the suite is detecting real visual difference or baseline drift, but the daily blocking cadence is too noisy for a mostly stable content website.

## Recommended Strategy

Use a layered quality gate:

1. Visual regression for stable layouts/templates and critical conversion pages.
2. Link checking for broken URLs, missing assets, redirects, and 404s.
3. Accessibility checks for key pages and representative templates.
4. SEO/health checks for metadata and major performance regressions.
5. Manual review workflow for screenshot baseline updates.

## Expected User Impact

- Fewer noisy daily failures.
- Better signal when a code, template, or style change breaks the site.
- Continued protection against layout regressions after new content is added.
- Clear instructions for intentional baseline updates.
