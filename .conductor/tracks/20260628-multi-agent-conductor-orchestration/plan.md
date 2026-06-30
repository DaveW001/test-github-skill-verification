# Plan

## Phase 0 - Research and Prompt Mapping
- [x] Read `C:\Users\DaveWitkin\AppData\Roaming\espanso\match\migrated_snippets.yml` and map standard prompts to all six pipeline stages.
- [x] Read OpenCode command and agent development standards from `C:\Users\DaveWitkin\.config\opencode\`.
- [x] Inspect the Conductor skill and templates for expected track artifacts.
- [x] Consult current OpenCode docs for commands, agents, config, model pinning, and subagent task permissions.
- [x] Inspect local model configuration and `opencode models` enough to identify confirmed canonical IDs for GPT-5.5 Low and MiniMax M3 Thinking.

## Phase 1 - Architecture Proposal
- [x] Decide command + orchestrator agent + stage subagents as the recommended OpenCode-native structure.
- [x] Define model assignment table with diversity rules and fallbacks.
- [x] Define context handoff artifacts for every stage boundary.
- [x] Define measurable re-review and re-validation trigger options for Dave to choose from.
- [x] Define max-iteration caps and escalation behavior.
- [x] Define model-unavailable, plan/review failure, execution failure, and validation failure paths.

## Phase 2 - Approval Checkpoint
- [x] Present the proposal to Dave with plain-language open questions.
- [x] Get Dave’s decision on autonomy level: **FULL AUTO through validation** (chosen 2026-06-28; overrides recommended pause).
- [x] Get Dave’s threshold choice for conditional re-review: **B+C hybrid** (structural OR readiness <90% OR any Blocking).
- [x] Get Dave’s threshold choice for conditional re-validation: **A+C hybrid** (verdict not-ready/prod-fix OR acceptance unmet OR progress inconsistent).
- [x] Get Dave’s preference on command-only vs command + skill reference pack: **Command + skill reference pack**.
- [x] Confirm canonical GPT-5.5 and MiniMax model IDs: OpenAI uses `openai/gpt-5.5` with `reasoningEffort: low`; MiniMax M3 uses `opencode-go/minimax-m3`.

## Phase 3 - Implementation Plan for Build Agent (Deferred Until Approval)
- [x] Create global command `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md` with frontmatter targeting the orchestrator.
- [x] Create orchestrator agent `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` with explicit `permission.task` allow-list.
- [x] Create stage subagents in `C:\Users\DaveWitkin\.config\opencode\agent\` with explicit models and minimal necessary permissions.
- [x] If chosen, create skill/reference pack under `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\` for long prompts and policy references.
- [x] Add documentation README for invocation, stages, thresholds, model diversity, fallbacks, and rollback behavior.
- [x] Restart OpenCode and verify agents/commands are loaded.
- [ ] Run a dry-run on a documentation-only toy request and inspect produced artifacts before using on production work.

## Phase 4 - Verification Criteria for Final Workflow
- [x] `opencode agent list` shows all new subagents as Task-callable subagents or `mode: all` where intentionally dual-use.
- [x] `opencode models` / `opencode debug config` confirms `openai/gpt-5.5`, low reasoning options, and `opencode-go/minimax-m3` resolve in the final runtime after command/agent files are created.
- [ ] A dry-run creates a Conductor track with `spec.md`, `plan.md`, `metadata.json`, review report, and validation report.
- [ ] Re-review gate triggers only when the selected threshold is met.
- [ ] Re-validation gate triggers only when the selected threshold is met.
- [ ] Diversity checks are logged: creator model ≠ reviewer model; executor model ≠ validator model.
- [ ] Failure simulation for unavailable model or blocked execution produces a clear stop message and no silent continuation.

## Current Status
**APPROVED 2026-06-28.** Architecture + threshold defaults accepted by Dave. Decisions: full-auto autonomy, B+C re-review trigger, A+C re-validation trigger, command + skill reference pack layout. Phase 3 implemented 2026-06-28: command + orchestrator + 6 stage subagents + skill pack + README created and statically verified (opencode agent list loads all 7 with correct modes; opencode models resolves all model IDs). Files placed in agent\ and skill\ (singular) to match live scanned config. Phase 3 item 7 (live dry-run) + Phase 4 items 3-7 (runtime gate/diversity/failure-sim checks) require a post-restart session: OpenCode does not hot-reload, so the new subagents are not invokable in the session that created them.
