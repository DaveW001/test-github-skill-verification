# Spec

## Goal

Make every invocation of the `conductor` skill automatically compose the applicable `conductor-pipeline` workflow, using the canonical stage prompts and risk-adjusted routing.

## Requirements

- [ ] Every Conductor plan creation uses the canonical Stage 0 baseline, Stage 1 plan-creation, and Stage 2 independent-review prompts.
- [ ] Baseline testing is mandatory before deliverable edits for every pipeline mode.
- [ ] Plan review is mandatory and performed by an agent/model distinct from the plan creator.
- [ ] Pipeline stages after review remain risk-adjusted; unnecessary stages may be skipped only with recorded rationale.
- [ ] Model assignments are defaults that may be substituted when unavailable or better suited, while preserving creator/reviewer and executor/validator independence.
- [ ] Every stage uses a capable model from the documented defaults or a capability-equivalent substitute; `gpt-5.4-mini` and other mini/nano economy models are prohibited.
- [ ] Conductor templates and pipeline policy describe the same paths and metadata.

## Non-Requirements

- [ ] Do not change OpenCode provider configuration or install models.
- [ ] Do not publish the skills to SkillShare without Dave's explicit approval.
- [ ] Do not modify unrelated Conductor tracks or overwrite existing user changes.

## Acceptance Criteria

- [ ] Structural smoke tests pass for both skills after the edits.
- [ ] An independent functional reviewer confirms that a representative "create a Conductor plan" request necessarily produces baseline evidence and independent plan review before execution.
- [ ] Cross-file consistency checks find no remaining path that permits Stage 0 or Stage 2 to be skipped.
- [ ] All tasks in plan.md are marked [x] or explicitly deferred with rationale.
