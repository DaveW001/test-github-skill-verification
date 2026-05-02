# Spec: openai-parameter-fix

## Background
Recent reports indicate widespread OpenCode parameter mismatch errors (for example, `max_tokens` vs `max_completion_tokens`, unsupported reasoning parameters) on newer OpenAI reasoning models. In this environment, the global config at `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` defines many OpenAI model variants with `reasoningEffort`/`reasoningSummary`, so provider/runtime compatibility must be validated carefully before and after any config change.

## Goal
Stabilize OpenCode OpenAI calls by making minimal, reversible config changes and validating the full request path (config load -> provider resolution -> real model invocation) with explicit pass/fail gates.

## Non-Goals
- No broad provider refactor.
- No unrelated plugin or command cleanup.
- No permanent deletion of recovery artifacts without validated success.

## Hypotheses (to verify with evidence)
1. OpenAI provider package resolution may be mismatched for Responses API models.
2. Cached provider artifacts may be stale and preserving bad behavior.
3. Secondary option-level incompatibilities may exist (`reasoningSummary`, include fields, etc.) and should only be touched if provider correction does not resolve failures.

## Requirements
1. Capture pre-change evidence from logs and reproduce at least one failing OpenAI call with timestamp.
2. Add explicit OpenAI provider package selection (`"npm": "@ai-sdk/openai"`) in a controlled change set.
3. Preserve rollback path:
   - Timestamped backup of `opencode.jsonc`.
   - Cache rename/archive preferred over irreversible delete.
4. Validate with a gated matrix:
   - Syntax gate
   - Startup/load gate
   - Provider-resolution gate
   - Behavior gate (real model invocations)
   - Regression gate (non-OpenAI providers unaffected)
5. Use single-variable changes after the initial provider fix. If still failing, apply one mitigation at a time and re-test.

## Validation Gates (Definition of Done)
- **Gate A – Syntax:** `opencode.jsonc` parses cleanly (JSONC).
- **Gate B – Startup:** OpenCode headless startup succeeds with no config/provider load errors.
- **Gate C – Provider Resolution:** logs or runtime evidence confirm `openai` provider uses expected package/path for Responses API behavior.
- **Gate D – Behavior:** successful calls for at least:
  - one medium reasoning model,
  - one high/xhigh reasoning model,
  - one low/none reasoning model.
- **Gate E – Regression:** Google proxy/OpenRouter model invocation still succeeds.
- **Gate F – Observability:** no recurrence of parameter mismatch errors during short post-change monitoring window.

## Constraints & Rules
- Treat the provider-package fix as a hypothesis until evidence confirms causality.
- Apply change sequencing with explicit checkpoints and rollback criteria.
- Do not remove reasoning options unless required by failed post-fix behavior tests.
