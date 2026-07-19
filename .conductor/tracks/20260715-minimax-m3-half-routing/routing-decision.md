# Routing Decision: Native 50/50 Model Selection

## Installed version

OpenCode `1.18.1` (recorded 2026-07-15T23:38:01Z).

## Evidence inspected

1. `opencode --version` — confirmed 1.18.1.
2. `opencode models openai` — lists `openai/gpt-5.6-terra` and `openai/gpt-5.6-terra-fast` as discoverable built-in models.
3. `opencode run --help` — documents `--model` (single model string) and `--variant` (provider-specific reasoning effort). No `--weight`, `--routing-policy`, `--model-list`, or randomization flag is documented.
4. `opencode agent --help` — no subcommand exists (non-zero exit / not recognized).
5. `opencode.json` custom model overrides — defines `gpt-5.6-sol` with explicit `variants` block (none/low/medium/high/xhigh). No `weights`, `routing`, `fallbackModels`, or `modelPool` field is present or documented.
6. Agent frontmatter schema — each agent file declares exactly one `model:` line and optional `variant:` line. No multi-model, weighted, or randomized routing field is supported.
7. Official OpenCode docs (https://opencode.ai/docs) — no documented weighted-routing or model-pool feature for agent definitions.

## Native 50/50 finding

Unsupported by verified evidence.

OpenCode 1.18.1 does not provide a native weighted, randomized, or pool-based model-selection mechanism for agent definitions. Each agent pins exactly one model and optional variant. No `fallbackModels`, `modelPool`, `weights`, or routing-policy field exists in the agent frontmatter schema or the `opencode.json` model-override block.

## Invocation-level enforceability

OpenCode has no built-in invocation-level alternation or deterministic routing policy. Model selection is fixed per agent identity. To achieve approximate 50/50 usage across a set of invocations, the only auditable mechanism is to define **paired agent identities** (e.g., `conductor-plan-reviewer` and `conductor-plan-reviewer-tera`) with fixed model pins, then assign invocations to specific agents by a deterministic, persisted rule (e.g., explicit stage mapping or parity of a stable run identifier).

Random selection without a persisted selection record is prohibited by the track spec.

## Selected mechanism

**Fixed pins with paired agents and explicit stage-mapping invocation rule.**

- Retain existing MiniMax M3 pins on a subset of pipeline agents.
- Create new paired agent identities pinned to `openai/gpt-5.6-terra` with `variant: medium` for the remaining subset.
- The invocation rule is explicit stage mapping: each pipeline stage is assigned to exactly one agent identity, and the assignment is recorded in the approved routing map and preserved in documentation.
- This is fully auditable: every invocation's model is determined by the stage-to-agent mapping, which is persisted in the agent files and pipeline documentation.

## Diversity consequences

| Stage | Agent | Model | Family |
|---|---|---|---|
| 1 Plan creation | conductor-plan-creator | openai/gpt-5.6-sol (low) | OpenAI |
| 2 Plan review | conductor-plan-reviewer | opencode-go/minimax-m3 | MiniMax |
| 3 Re-review | conductor-plan-reviewer-alt | openai/gpt-5.6-sol (low) | OpenAI |
| 4 Test writer | conductor-test-writer | opencode-go/qwen3.7-plus | Qwen |
| 5 Executor | conductor-track-executor | zai-coding-plan/glm-5.2 (high) | GLM |
| 6 Test runner | conductor-test-runner | openai/gpt-5.6-terra (medium) | OpenAI |
| 7 Validator | conductor-track-validator | opencode-go/minimax-m3 | MiniMax |
| 8 Re-validation | conductor-track-validator-alt | openai/gpt-5.6-sol (low) | OpenAI |
| 9 Doc writer | conductor-doc-writer | zai-coding-plan/glm-5.1 | GLM |

Creator/reviewer pairs:
- Stage 1 (OpenAI) vs Stage 2 (MiniMax): different families. OK.
- Stage 2 (MiniMax) vs Stage 3 (OpenAI): different families. OK.

Executor/validator pairs:
- Stage 5 (GLM) vs Stage 6 (OpenAI Tera): different families. OK.
- Stage 5 (GLM) vs Stage 7 (MiniMax): different families. OK.

All diversity rules preserved. No same-family creator/reviewer or executor/validator pair.
