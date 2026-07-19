# MiniMax M3 Half-Usage Agent Routing

## Goal / outcome

Reduce explicit MiniMax M3 agent usage by approximately 50% by assigning ChatGPT 5.6 Tera with Medium thinking to roughly half of the applicable invocations, using the simplest OpenCode-supported, auditable routing design while preserving independent-review model diversity.

## Constraints / non-goals

- First verify the installed OpenCode version and authoritative configuration/schema evidence. Do not invent a weighted, randomized, fallback, or model-list field.
- If OpenCode does not natively support agent-level 50/50 routing, use fixed model pins plus explicit paired agents or an invocation-level deterministic alternation mechanism. Prefer paired agents when it is simpler and more auditable.
- Inventory every active agent/config that explicitly selects MiniMax M3 in `C:\Users\DaveWitkin\.config\opencode\agent`, `C:\Users\DaveWitkin\.config\opencode\agents`, and every Git repository recursively beneath `C:\development\`.
- Classify backups, archives, generated reports, `.git`, sessions, logs, handoffs, and historical Conductor artifacts separately; do not edit historical evidence.
- Do not overwrite unrelated uncommitted changes. Every target must be backed up and compared immediately before edit.
- Preserve independent-review diversity: no artifact may be reviewed or validated solely by the same model family that created or executed it.
- Preserve the established Stage 5 executor fallback sequence `zai-coding-plan/glm-5.2` -> `zai-coding-plan/glm-5.1` -> `opencode-go/qwen3.7-plus`, but because GLM-5.2 quota is exhausted, runtime execution must begin at GLM-5.1 and then Qwen. Planning and deterministic checks must not require GLM-5.2.
- Reuse the scan, backup, active-versus-history classification, parsing, and restart lessons in `C:\development\opencode\.conductor\tracks\20260714-gpt-56-sol-migration\`; do not redo that migration or change its artifacts.
- No application code or unrelated OpenCode settings are in scope.

## Definition of done

1. A version-grounded routing decision states whether the installed OpenCode supports native 50/50 model selection and cites exact evidence.
2. A complete machine-readable inventory covers both user-level agent directory spellings and every Git repository under `C:\development\`, with every M3 hit classified active or historical.
3. Approved active targets are changed through an auditable mechanism that approximates 50/50 usage, with exact before/after assignments and a distribution calculation.
4. Pipeline creator/reviewer/executor/validator assignments retain model-family independence, and Stage 5 documents/uses GLM-5.1 then Qwen while GLM-5.2 is unavailable.
5. Timestamped backups and a tested rollback command exist for every changed file; unrelated pre-existing changes remain untouched.
6. Deterministic syntax, model-pin, inventory, distribution, diversity, and fallback-chain checks pass.
7. The handoff explicitly states whether restart is required. If required, live tests run only after restart; if the known `Error: Session not found` recurs, it is recorded as a runtime blocker rather than misreported as a routing failure.

## Routing decision boundary

The executor must not assume weighted routing exists. It must inspect the installed CLI help/version, local schema/config implementation, and official documentation. Only documented support for an exact weighted/random policy may justify native 50/50 routing. Otherwise the approved default is fixed pins with paired M3/Tera-Medium agent identities and an explicit deterministic invocation rule (for example, parity of a stable run identifier), with pipeline stages mapped so creator-versus-reviewer and executor-versus-validator remain different model families. Random selection without a persisted selection record is prohibited.

## Acceptance criteria

- `routing-decision.md` contains the installed version, evidence sources, a Supported/Unsupported finding, and the selected mechanism.
- `m3-inventory.json` has one record per discovered explicit M3 selection and records `path`, `repository`, `classification`, `agent`, `model`, and `reason`.
- `approved-routing-map.json` records each active agent, old model, new model/variant, invocation rule, role family, and diversity counterpart.
- All edited JSON/JSONC/frontmatter files pass their applicable deterministic parser/checker.
- The post-change active scan and inventory reconciliation report zero unexplained explicit M3 selections.
- The measured planned assignment ratio is between 40% and 60% Tera among in-scope M3 selections, or the report documents why indivisible low counts require the nearest possible split.
- `diversity-validation.json` reports no same-family creator/reviewer or executor/validator pair.
- `fallback-validation.json` records GLM-5.2 as unavailable primary and the operational order GLM-5.1 then Qwen without changing the canonical three-tier sequence.
- `runtime-validation.md` distinguishes deterministic success, restart state, live result, and the known session-error failure mode.

## Rollback

Restore only files listed in the generated backup manifest, verify each restored SHA-256 hash against the pre-change hash, rerun active scans and parsers, and leave all pre-existing user changes untouched. Never use `git reset`, `git checkout .`, or bulk restore.
