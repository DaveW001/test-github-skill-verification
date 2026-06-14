# Spec: Prompt Schema Overhead Research

## Goal / Outcome

Determine how many system-prompt tokens are consumed by OpenCode runtime/tool overhead after the prior system-prompt reduction work, with priority on MCP/plugin tool schemas, Codex Authenticator / Codex account-management tooling, and native tool schemas. Produce evidence-backed recommendations for whether the system prompt can be reduced toward or below 15,000 tokens through safe configuration changes, controlled feature toggles, or upstream OpenCode changes.

## Constraints / Non-Goals

- Do not modify OpenCode application source code.
- Do not permanently disable or remove user capabilities without explicit user approval.
- Do not commit, push, or create PRs.
- Do not expose secrets. Redact tokens, account IDs, Slack tokens, OAuth material, and private IDs from artifacts.
- Do not rely on stale estimates when a controlled measurement can be run.
- Do not treat heuristic tokenscope output as exact. Label estimates and confidence levels.
- Prefer reversible A/B tests using timestamped backups and immediate restoration.
- The build agent may create temporary scripts and artifact files for measurement, but must not edit production code.

## Definition of Done

- A clean baseline token measurement is captured in a fresh OpenCode session.
- The current effective OpenCode config is inventoried, including plugins, MCP servers, permissions, native tools visible to the session, and Codex Authenticator / Codex account-management tooling.
- The source of Codex-related tools is identified: plugin, MCP server, native tool, or other runtime integration.
- MCP/plugin tool schema token costs are measured or bounded with a reproducible method.
- Native tool schema token costs are measured or bounded with a reproducible method.
- Task/subagent tool definition overhead is measured or bounded with a reproducible method.
- A controlled A/B test plan is executed for candidate high-savings toggles, especially Codex-related tooling, while restoring original config afterward.
- Final report states whether 15,000 tokens is reachable through safe local config changes, aggressive reversible local toggles, or only upstream/runtime changes.
- All artifacts are stored under `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/`.
- `plan.md`, `metadata.json`, `execution-log.md`, `.conductor/tracks.md`, and `.conductor/tracks-ledger.md` agree on the final status when the work is complete.

## In Scope

- Inspect and measure effective prompt overhead from:
  - Codex Authenticator / Codex account-management tools.
  - MCP tool schemas, including disabled vs enabled server behavior.
  - Native OpenCode tool schemas.
  - Task/subagent tool definitions.
  - Session/runtime scaffolding where measurable.
- Repair or work around tokenscope context export failure if needed for measurement, without modifying OpenCode application source.
- Use alternative measurement approaches if tokenscope export remains unavailable.
- Create redacted inventories and A/B measurement artifacts.
- Propose safe next steps and upstream issue content.

## Out of Scope

- Permanent removal of Codex Authenticator, account-management, MCP, task, or native tools without explicit user approval.
- Editing `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.go`, `.rs`, or other OpenCode application source files.
- Rewriting skills or user instructions for additional token savings unless needed only as a documented recommendation.
- Changing OAuth account state.
- Publishing reports externally.

## Required Artifacts

- `.conductor/tracks/20260531-prompt-schema-overhead-research/spec.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/plan.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/metadata.json`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/execution-log.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/baseline-tokenscope.txt`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/effective-config-inventory.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/tool-surface-inventory.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/codex-tool-origin-analysis.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/schema-token-estimates.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/ab-test-results.md`
- `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/final-report.md`

## Acceptance Criteria

- [ ] Baseline and each A/B measurement include session ID, timestamp, config state, system-token estimate, telemetry caveats, and artifact path.
- [ ] Codex-related tooling origin is identified with file/config evidence, not assumption.
- [ ] MCP schema contribution is measured directly or bounded with a clearly documented fallback method.
- [ ] Native tool schema contribution is measured directly or bounded with a clearly documented fallback method.
- [ ] Candidate savings are ranked by estimated tokens saved, reversibility, user-impact risk, and confidence.
- [ ] All config changes used for A/B tests are backed up before testing and restored afterward.
- [ ] Final report answers: `Can safe local changes reach 15,000 tokens?`, `Can aggressive reversible local toggles reach 15,000 tokens?`, and `What requires upstream OpenCode changes?`
- [ ] No artifacts contain unredacted secrets or disallowed control characters.

## Known Starting Evidence

- Prior track: `.conductor/tracks/20260526-system-prompt-token-audit/`.
- Prior fresh-session post-reduction estimate: 21,144 system tokens in `artifacts/post-reduction-tokenscope-fresh.txt`.
- Later non-fresh current-session tokenscope estimate: 18,550 system tokens.
- Existing estimates from prior artifacts:
  - Task/subagent full tool definition: approximately 749-901 tokens.
  - Subagent descriptions only: approximately 292-363 tokens.
  - Native tool schemas: approximately 2,350 tokens.
  - MCP tool schemas: approximately 2,800-5,800 tokens total historical estimate.
  - Codex-related tool surface: approximately 2,000-3,500 tokens historical estimate.
- Current visible MCP config appears to have Playwright, Control Chrome, and Slack disabled, but Codex-related tools may be provided by a plugin or other runtime tool surface.
- Tokenscope context export previously failed because a `bun` package import could not be resolved.
