# App Route and Selector Intake

## Purpose
Collect the minimum concrete app details required to replace manifest placeholders and start executable visual snapshot tests.

## Required Inputs

### 1) Target App
- Canonical base URL (local):
- Optional fallback URL:
- App framework (if known):

### 2) P0 Routes (PR-gated)
Provide at least 2-3 routes.

| Route ID | Path | Why P0 | Requires Auth (Y/N) |
| --- | --- | --- | --- |
| app-home | / |  |  |
| app-primary-flow |  |  |  |
| app-settings-or-admin |  |  |  |

### 3) State Setup per Route
For each route, provide setup method for:
- default
- empty
- loading
- error
- overlay
- long-content

Format example:
```yaml
route: /orders
states:
  default:
    fixture: orders-default
    mocks: []
    actions: []
  loading:
    fixture: orders-default
    mocks:
      - route: "**/orders*"
        behavior: delay
```

### 4) Required Selectors
For each P0 route, provide:
- `ready.waitForSelector`
- `stickyHeaderSelector` (if present)
- `primaryCtaSelector`
- Any selectors to ignore in snapshots (dynamic regions)

### 5) Auth/Test Data Constraints
- Is login required for P0 routes?
- Preferred test account strategy:
- Data-reset mechanism (if any):

## Output Action
Once this intake is filled, update:
- `.conductor/tracks/webapp-visual-regression/artifacts/page-state-manifest.draft.yaml`

Then execution proceeds to native snapshot wiring.
