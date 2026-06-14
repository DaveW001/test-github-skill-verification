# Accessibility Known Issues

Documented: 2026-05-08

## Current Violations by Route

### `/` (homepage) — 3 violations
| Violation ID | Impact | Nodes | Notes |
|---|---|---|---|
| color-contrast | serious | 11 | Text elements with insufficient contrast ratio |
| heading-order | moderate | 1 | Heading levels skip a level |
| image-redundant-alt | minor | 1 | Image alt text is redundant with surrounding text |

### `/contact` — 5 violations
| Violation ID | Impact | Nodes | Notes |
|---|---|---|---|
| color-contrast | serious | 2 | Text elements with insufficient contrast ratio |
| heading-order | moderate | 1 | Heading levels skip a level |
| image-redundant-alt | minor | 1 | Image alt text is redundant with surrounding text |
| landmark-one-main | moderate | 1 | Page should have one main landmark |
| region | moderate | 12 | Some content is not contained within a landmark region |

### `/insights` — 2 violations
| Violation ID | Impact | Nodes | Notes |
|---|---|---|---|
| color-contrast | serious | 14 | Text elements with insufficient contrast ratio |
| image-redundant-alt | minor | 1 | Image alt text is redundant with surrounding text |

## Tolerance

Current max violations across P0 routes: **5** (on `/contact`).

The accessibility test assertion is set to `toBeLessThanOrEqual(5)` until these issues are remediated.

## Remediation Owners

- **color-contrast**: Design team — audit all text elements against WCAG AA 4.5:1 ratio
- **heading-order**: Content team — ensure heading hierarchy is sequential
- **image-redundant-alt**: Content team — review alt text for decorative or redundant images
- **landmark-one-main**: Dev team — ensure single `<main>` landmark per page
- **region**: Dev team — wrap content sections in landmark regions (`<section aria-label="...">`)
