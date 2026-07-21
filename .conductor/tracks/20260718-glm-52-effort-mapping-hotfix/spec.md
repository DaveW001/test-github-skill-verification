# Specification: GLM-5.2 High/Max Effort-Mapping Hotfix

## Goal / Outcome

Restore the intended operator-facing behavior for `zai-coding-plan/glm-5.2`: `high` remains the default and should consume approximately one-half of `max` reasoning tokens, `max` remains the expensive opt-in, and `none` continues to produce zero hidden reasoning tokens. Apply a documented temporary transport-mapping workaround, preserve reproducible evidence, rerun the nine-call benchmark immediately, and reevaluate it on or after 2026-07-25.

## Incident Summary

The live 2026-07-18 benchmark used three identical light prompts under each of `high`, `none`, and `max`. OpenCode's response `step_finish.tokens` objects reported:

| Operator-facing variant | Calls | Reasoning tokens | Visible output tokens | Generated tokens | Overall tokens |
|---|---:|---:|---:|---:|---:|
| `none` | 3 | 0 | 11 | 11 | 28,358 |
| `high` | 3 | 181 | 14 | 195 | 28,560 |
| `max` | 3 | 85 | 14 | 99 | 28,464 |

Observed generated-token ratios were `high = 1772.73% of none`, `max = 900.00% of none`, and `max = 50.77% of high`. This is the reverse of the intended high/max cost relationship. The request-shape audit separately proved that OpenCode 1.18.1 currently sends `reasoning_effort: "high"` for `high` and `reasoning_effort: "max"` for `max`; `none` sends `thinking.type: "disabled"` and produced zero live reasoning tokens.

### Canonical benchmark prompts

The immediate and one-week runs must use this exact ordered array without paraphrasing:

1. `A store discounts a $48 item by 25%, then adds 8% sales tax to the discounted price. Return only the final price in dollars, rounded to two decimals.`
2. `All tulips are flowers. No flowers are made of metal. Can any tulip be made of metal? Return only Yes or No.`
3. `A meeting starts at 14:35 and lasts 1 hour 45 minutes, followed immediately by a 20-minute break. At what time does the break end? Return only the 24-hour time in HH:MM format.`

## Chosen Remediation

Apply a clearly labeled, reversible compatibility workaround in the canonical global JSONC config:

```jsonc
"options": {
  "reasoningEffort": "max" // temporary transport mapping for logical default `high`
},
"variants": {
  "none": {
    "thinking": { "type": "disabled" }
  },
  "high": {
    "reasoningEffort": "max"
  },
  "max": {
    "reasoningEffort": "high"
  }
}
```

Operator-facing names do not change: agents and users continue to select `high`, `none`, or `max`. Only the outbound GLM-5.2 `reasoningEffort` mapping is swapped. The model-level default must map to outbound `max` so an unqualified/default call retains logical `high` behavior. This workaround is evidence-driven but provisional; it must be reevaluated against live response token usage on or after 2026-07-25.

## Scope

### In scope

- Modify only the GLM-5.2 options/variants block in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- Preserve `high` as the operator-facing default and `none` as explicit thinking-off.
- Build a reusable diagnostic at `scripts/diagnostics/test_glm_thinking_levels.py` with local request-shape and live nine-call modes.
- Preserve machine-readable evidence under `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/evidence/`.
- Document the incident, workaround, results, rollback, and dated reevaluation in `docs/diagnostics/glm-52-thinking-effort-mapping.md`.
- Synchronize active Z.AI and Conductor-pipeline documentation with the logical-label/transport-mapping distinction.
- Rerun the same live benchmark immediately after the change and once on or after 2026-07-25.

### Constraints / Non-goals

- Do not rename the operator-facing variants or change agents pinned to `variant: high`.
- Do not change `model`, `small_model`, provider base URL, API keys, timeouts, fallback models, or unrelated provider settings.
- Never create, restore, or edit `C:\Users\DaveWitkin\.config\opencode\opencode.json`; JSONC is the sole canonical global config.
- Do not expose API keys, tokens, authorization headers, or full merged config output in evidence or logs.
- Do not patch OpenCode application source or the installed npm package.
- Do not claim the workaround proves Z.AI's documented semantics are reversed globally; the evidence is specific to this environment and sample.
- Do not require strict monotonic token usage on every individual prompt. Evaluate aggregate generated tokens across the three-prompt sample.
- Do not automatically revert or remap again if the one-week result misses the target; stop and request an operator decision.

## Functional Requirements

1. The effective default and logical `high` mapping must send `reasoning_effort: "max"`.
2. The effective logical `max` mapping must send `reasoning_effort: "high"`.
3. The effective `none` mapping must send `thinking.type: "disabled"`.
4. A local request-shape mode must verify all four cases without contacting Z.AI.
5. A live mode must run the three canonical prompts verbatim under each of `high`, `none`, and `max`, parse `step_finish.tokens`, and write a JSON report; `docs/diagnostics/glm-52-thinking-effort-mapping.md` is the consolidated Markdown summary for both runs.
6. Live evidence must include input, cache read/write, visible output, reasoning, generated (`output + reasoning`), and overall total tokens.
7. The immediate and one-week JSON reports must contain all six pairwise percentage fields: high-vs-none, max-vs-none, and max-vs-high for both aggregate generated tokens and overall tokens.
   A percentage whose denominator is zero must be JSON `null`, never an exception, infinity, or fabricated zero. An undefined high/max ratio requires `operator-decision-required`.
8. `none` must report zero aggregate reasoning tokens; otherwise the run is a hard failure.
9. The one-week report must explicitly evaluate the intended aggregate relationship `high ~= 50% of max`, using a provisional acceptable band of 35%-65% for generated tokens.
10. The documentation must distinguish logical variant names from outbound transport values and include an exact rollback mapping.

## Required Artifacts

- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/spec.md`
- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/plan.md`
- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/metadata.json`
- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/execution-log.md`
- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/evidence/baseline-2026-07-18.json`
- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/evidence/request-shape-after.json`
- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/evidence/live-immediate.json`
- `.conductor/tracks/20260718-glm-52-effort-mapping-hotfix/evidence/live-one-week.json`
- `scripts/diagnostics/test_glm_thinking_levels.py`
- `docs/diagnostics/glm-52-thinking-effort-mapping.md`

External active files to modify:

- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- `C:\Users\DaveWitkin\.config\opencode\references\zai-calling-conventions.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`

## Definition of Done

- The canonical JSONC config contains the exact provisional swapped mapping and no unrelated config changes.
- Local request capture proves default/high -> outbound `max`, logical max -> outbound `high`, and none -> disabled.
- The immediate live nine-call run succeeds and all three `none` calls report zero reasoning tokens.
- Incident and routing documentation clearly explains the workaround, baseline data, current data, rollback, and limitations.
- On or after 2026-07-25, the same nine-call live benchmark is rerun and compared with baseline and immediate results.
- The one-week report records whether aggregate logical `high` generated tokens are 35%-65% of logical `max`; an out-of-band result is documented as `operator-decision-required`, not silently remapped.
- OpenCode has been restarted after the config-time changes, the execution log records the restart, and all non-deferred plan tasks are complete.
- `plan.md`, `metadata.json`, `.conductor/tracks.md`, and `.conductor/tracks-ledger.md` agree on final status and task counts.

## Rollback

Restore only the timestamped pre-change backup of `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`, or manually restore this original mapping:

```jsonc
"options": { "reasoningEffort": "high" },
"variants": {
  "none": { "thinking": { "type": "disabled" } },
  "high": { "reasoningEffort": "high" },
  "max": { "reasoningEffort": "max" }
}
```

Restart OpenCode after rollback and rerun local request-shape mode before making any live Z.AI call.

## Related Work

- Historical track `20260622-glm-52-non-thinking-variant` introduced `none`; its source artifacts remain recoverable from commit `b1d0c162732d6ae383b371fe4393d76eb5a4fcc8`.
- This track supersedes only the high/max operational mapping guidance. It does not supersede the validated `none` behavior.
