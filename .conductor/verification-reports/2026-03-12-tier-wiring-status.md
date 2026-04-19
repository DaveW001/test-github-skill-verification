# Tier Wiring Status

Date: 2026-03-12
Status: Wiring complete, orchestrator spawn still degraded

## What Was Wired

- Updated `cove-verifier` to act as low-tier verifier and pinned model to `zai-coding/glm-4.7`.
- Updated `cove-orchestrator` to include:
  - routing policy reference to `.opencode/model-tiers.json`
  - 10-second preflight probe
  - fallback mode using `perplexity-search` if verifier spawn fails
  - mandatory log/report artifact generation rules

## Validation

- `cove-verifier` spawn: PASS
- `cove-orchestrator` spawn: FAIL (`ProviderModelNotFoundError`)

## Practical Impact

- Tier-aware logic is documented and wired in agent config.
- Full execution through `cove-orchestrator` cannot be validated until orchestrator spawn issue is cleared.
- Workaround remains: run CoVe flow from the active primary agent and call `cove-verifier` sequentially.
