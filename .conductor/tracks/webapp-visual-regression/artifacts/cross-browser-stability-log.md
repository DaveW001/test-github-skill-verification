# Cross-Browser Stability Log

Track non-blocking cross-browser signal before promotion to blocking mode.

## Promotion Target
- At least 5 consecutive successful non-blocking runs
- No unresolved blocker-level rendering issues for P0 routes

## Run Log

| Date | Branch | Mode | Scope | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-03-05 | local | non_blocking | components synthetic | pass | Firefox/WebKit baselines created and verified locally (4/4) |
| 2026-03-05 | local | non_blocking | P0 smoke (`mobile-narrow contact default`) | pass | Firefox/WebKit baselines created and verified locally (2/2) |
| 2026-03-05 | local | non_blocking | full P0 matrix | pass | Firefox/WebKit baseline generation and verification completed (74/74) |

Notes:
- CI streak entries start after this workflow file exists on default branch and runs at least once.
- Use `npm run test:visual:stability-log` to generate markdown rows from recent GitHub runs.

## Ready-to-Promote Checklist
- [ ] 5 consecutive non-blocking runs green
- [x] Firefox and WebKit baseline diffs reviewed and accepted (local pass set)
- [x] No open blocker findings from cross-browser artifacts (local pass set)
- [ ] `VISUAL_CROSS_BROWSER_MODE` switched to `blocking`
