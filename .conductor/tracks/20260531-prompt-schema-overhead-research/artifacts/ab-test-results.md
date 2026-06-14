# A/B Test Results

## Codex tooling disabled
- Baseline artifact: artifacts/baseline-tokenscope.txt
- Codex-disabled artifact: PENDING - A/B test deferred
- System token delta: PENDING - deferred
- Interpretation: PENDING - deferred
- Config restored: N/A - no config changes made yet

## Status
**DEFERRED** - Codex A/B test requires a fresh OpenCode session. The user has other sessions running and will run this test later.

## Estimated Range (from prior track)
- Codex tooling estimated at 2,000-3,500 tokens
- Midpoint: ~2,750 tokens (~15.8% of 17,377 baseline)

## To Run This Test
1. Back up opencode.jsonc
2. Remove 'oc-codex-multi-auth' from plugin array
3. Start fresh OpenCode session
4. Run tokenscope tool
5. Copy output to artifacts/codex-disabled-tokenscope.txt
6. Restore opencode.jsonc from backup
7. Update this file with measured delta
