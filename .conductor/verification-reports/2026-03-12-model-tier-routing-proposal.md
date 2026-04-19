# Model Tier Routing Proposal

Date: 2026-03-12
Status: Proposal only (no runtime integration yet)

## Objective

Use the lowest-cost model that still meets quality for each task class, while preserving escalation paths for complex or high-risk work.

## Tier Definitions

- Low tier: cheap, fast, high-volume tasks (single-fact verification, claim extraction, simple transforms)
- Mid tier: moderate reasoning and synthesis (draft cleanup, claim reconciliation, lightweight reviews)
- High tier: complex reasoning or high-risk domains (architecture, security/legal/financial/medical, final decision reviews)

## Proposed Routing

- verify_single_fact -> low
- extract_atomic_claims -> low
- draft_minor_rewrite -> mid
- claim_reconciliation -> mid
- architecture_planning -> high
- high_stakes_review -> high

## Risk Overrides

Always force high tier for:

- security
- legal
- financial
- medical

## Preflight Availability Check (10s Budget)

1. Start with the assigned tier.
2. Try models in listed order until one succeeds.
3. If none succeed in-tier, use tier fallback model list.
4. If still unavailable, escalate to the next tier.
5. If all tiers fail, return explicit model-availability error.

This keeps model selection deterministic and cheap by default.

## Artifacts

- Tier config: `.opencode/model-tiers.json`

## Notes

- This proposal does not change runtime behavior yet.
- Next implementation step is wiring this config into orchestrator/subagent selection logic.
