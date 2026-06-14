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

### Documented Skip Rules
| Pattern | Reason |
|---|---|
| `linkedin.com` | External LinkedIn company page returns 404 |
| `feed.xml` | Tag feed URLs are generated but not implemented |
| `twitter-card.png` | Missing OpenGraph image asset |
| `brad-hunter.webp` | Missing team photo asset |
| `gao.gov` | External GAO report link returns 404 |
| `18f.gsa.gov` | External government site blocks crawlers (status 0) |
| `hbr.org` | External HBR article returns 404 |

## Accessibility Violation
- Review the console output from `npm run test:a11y` for violation IDs
- Check `.conductor/tracks/20260508-website-regression-guardrails/artifacts/accessibility-known-issues.md` for documented exceptions
- Fix the violation or document it as a known issue with route, violation ID, and owner
- Current tolerance: up to 5 violations per route (see known-issues file)

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
