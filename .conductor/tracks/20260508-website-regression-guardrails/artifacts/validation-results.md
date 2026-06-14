# Validation Results

- `npm run test:visual:p0`: PASS — 37/37 tests passed (home + contact across 5 viewports)
- `npm run test:links`: PASS — 281 links scanned, 0 broken (7 skip rules documented in failure-triage.md)
- `npm run test:a11y`: PASS — 3/3 routes pass with tolerance ≤5 violations (known issues documented in accessibility-known-issues.md)
- `npm run test:health`: PASS — 3/3 routes pass (/, /contact, /insights)
- YAML validation: PASS — `.github/workflows/visual-regression.yml` validated with Python yaml.safe_load
