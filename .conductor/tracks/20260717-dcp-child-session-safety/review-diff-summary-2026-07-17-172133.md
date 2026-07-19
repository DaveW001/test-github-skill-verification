# Conditional Re-review Diff Summary (Stage 3)

- **Track:** `20260717-dcp-child-session-safety`
- **Timestamp:** `2026-07-17-172133`
- **Plan:** `C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\plan.md`
- **Spec:** `C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety\spec.md`
- **Task count:** unchanged at 29
- **Phase count:** unchanged at 7 under the track's counting convention
- **Production changes:** none

## Confident corrections applied

1. **Spec acceptance semantics:** replaced strict whole-map set equality with required-active-key subset coverage. Every required value must be integer `150000`; unrelated existing keys are preserved.
2. **Spec model identity:** recorded that provider discovery confirms exact key `openai/gpt-5.6-terra`, while active Conductor files currently use distinct key `openai/gpt-5.6-luna`; added a pre-execution user decision gate.
3. **Plan Task 0.3:** removed the unsafe generic waiver branch. The executor must stop and request one of two explicit choices: retain Luna and cap Luna+Terra, or separately authorize agent migration to Terra.
4. **Plan Task 4.1 diagnostics:** replaced stale “exactly 4 missing keys” language with the dynamic missing-key set emitted by `verify_dcp_limits.py`; added full textual diff alongside numstat.

## Uncertain change not applied

No agent model frontmatter was changed. Whether Luna should remain active or be migrated to Terra is a behavior-changing user decision and is outside a reviewer-only correction.

## Net effect

- The DCP cap-preservation ambiguity is fully resolved and executable without guessing.
- The Terra/Luna identity itself is technically resolved, but the desired runtime assignment is not. Execution must stop for the exact user decision in the Stage 3 report.
- Remaining Blocking items: 1.
- Readiness: 82/100.