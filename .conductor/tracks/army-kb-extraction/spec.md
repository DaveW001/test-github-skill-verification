# Spec

## Goal
Extract reusable, evidence-backed Army knowledge from two existing NotebookLM notebooks so Packaged Agile can safely reuse it in its internal knowledge base, sales/delivery enablement, and future Army engagement planning.

Target notebooks:

| Notebook | ID | Primary Use |
|---|---|---|
| C2/CC2 Portfolio Engagement Kx | `5125c1f1-71b3-4dbe-afc5-d725d1a4db2c` | Operating context, org structure, governance, transformation plan, workshop notes, blockers, risk, strategic docs |
| Interview Notebook | `a6341a1d-e4d2-4cd1-8cb9-5dfcb0c4cfac` | Stakeholder perspectives, pain points, incentives, contradictions, leadership concerns, interview-derived patterns |

The extraction must prioritize reusable Packaged Agile knowledge, not generic Army summaries. Every reusable claim should be traceable to source titles and classified by confidence and sensitivity.

## Requirements
- [ ] Use `nlm` CLI in a read-only extraction mode unless the user explicitly approves creating NotebookLM Studio artifacts.
- [ ] Inventory and classify sources in both target notebooks before deep querying.
- [ ] Run a structured set of cross-notebook and notebook-specific queries across defined analytical lenses.
- [ ] Require all query outputs to include claim, evidence/source title, quote or near-quote where available, confidence, Packaged Agile reuse value, and sensitivity classification.
- [ ] Pull full source content only when it meets explicit criteria (repeatedly cited, canonical, high-value interview, insufficiently cited claim, or reusable language candidate).
- [ ] Apply the `notebooklm-meta-prompt` protocol only after baseline claims have been extracted and organized.
- [ ] Produce final Markdown knowledge base assets with source traceability and sensitivity warnings.
- [ ] Maintain a claims register that separates facts, inferences, hypotheses, and missing variables.

## Non-Requirements
- [ ] Do not create, rename, delete, or modify source NotebookLM notebooks unless explicitly approved by the user.
- [ ] Do not run `nlm data-table create`, `nlm report create`, `nlm audio create`, or other Studio artifact commands unless the user approves artifact creation.
- [ ] Do not use the extracted information as public marketing copy without a sensitivity/OPSEC review.
- [ ] Do not include raw sensitive logistics/security/CAC/facility details in reusable KB assets except as internal-only notes if truly necessary.
- [ ] Do not treat NotebookLM syntheses as authoritative unless backed by source titles and direct evidence.
- [ ] Do not generate generic Agile recommendations disconnected from Army-specific evidence.

## Sensitivity / OPSEC Requirements
- [ ] Classify each claim as one of: `public-safe`, `internal-only`, `sensitive-review`, or `exclude`.
- [ ] Flag names, roles, org charts, security onboarding, CAC/facility information, acquisition authorities, strategic intent, risks, and operational friction for review.
- [ ] Preserve stakeholder names for internal mapping when useful, but avoid converting named-person details into public-facing claims.
- [ ] Distinguish reusable patterns from client-specific confidential facts.

## Expected Outputs
Create or update these documentation artifacts during execution:

- `army-source-index.md` — classified source inventory and priority pull list.
- `army-claims-register.md` — evidence-backed claims with source titles, quotes/near-quotes, confidence, sensitivity, and reuse recommendation.
- `army-context-overview.md` — concise Army/PAE/C2-CC2 context for Packaged Agile users.
- `army-stakeholder-map.md` — people/roles/stakeholder groups, influence, concerns, and sensitivity tags.
- `army-challenges-and-patterns.md` — challenge -> evidence -> impact -> reusable Packaged Agile pattern.
- `army-pae-c2cc2-operating-model.md` — governance, decision rights, portfolio/product/program structures, battle rhythm, metrics.
- `army-agile-adoption-lessons.md` — what the Army context teaches Packaged Agile about agile adoption in military/acquisition environments.
- `army-meta-prompt-insights.md` — Shadow Audit / Inversion / Second-Order / Leverage / Paradigm Destroyer findings.

Suggested output directory: `.conductor/tracks/army-kb-extraction/outputs/` unless the user specifies a Packaged Agile KB destination.

## Acceptance Criteria
- [ ] Conductor track reflects the reviewed, improved extraction workflow.
- [ ] Source inventory is created for both notebooks.
- [ ] Baseline query outputs are captured with evidence, confidence, and sensitivity fields.
- [ ] Full source pulls are limited to explicit criteria and recorded in the source index.
- [ ] Meta-prompt analysis is grounded in the baseline claims register.
- [ ] Final KB assets are drafted as Markdown documents with source traceability.
- [ ] Sensitive or uncertain claims are clearly flagged and not presented as public-safe.
- [ ] All tasks in `plan.md` are marked `[x]` when complete.
