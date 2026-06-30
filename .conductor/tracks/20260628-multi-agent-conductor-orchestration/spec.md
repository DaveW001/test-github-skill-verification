# Spec

## Goal
Design an OpenCode-native workflow that moves a user request from idea → Conductor plan → independent plan review → optional re-review → execution → independent validation → optional re-validation, with explicit model diversity and auditable context handoffs at every gate.

This track is a **design/proposal track only** until Dave approves the architecture and threshold choices. It intentionally does not implement production code.

## Research Summary

### Local standards consulted
- `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md`
  - Primary agents can orchestrate other agents.
  - Task-callable workers must be `mode: subagent` or `mode: all`.
  - Write-enabled subagents are rare and must justify write/edit/bash access.
  - New agent definitions should use explicit `mode`, `model`, and `permission` fields.
- `C:\Users\DaveWitkin\.config\opencode\command-development-standards.md`
  - “Commands orchestrate, agents execute.”
  - Commands gather context and invoke specialized agents.
  - Complex commands can define multi-pattern orchestration.
  - Use `subtask: true` for isolated analysis; do not isolate iterative workflow commands by default.
- `C:\Users\DaveWitkin\.config\opencode\docs\reference\subagent-model-routing.md`
  - To force a Task/subagent onto a specific model, define the target as a subagent and set explicit `model`.
  - If a subagent has no explicit model, it inherits the invoking primary model.
  - Restart OpenCode after changing command/agent config.
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md`
  - Preferred track path: `.conductor/tracks/<track-id>/`.
  - Conductor track completion requires synchronized `plan.md`, `metadata.json`, execution logs, and ledgers.
  - Completion gate requires validation, artifact verification, logs, and ledger consistency.

### OpenCode docs consulted on 2026-06-28
- `https://opencode.ai/docs/commands/`
  - Commands live in `~/.config/opencode/commands/` or `.opencode/commands/` as Markdown files.
  - Commands support `description`, `agent`, `subtask`, and `model` frontmatter.
  - Commands support shell output injection, arguments, and file references, but docs do not describe native conditional branching inside command frontmatter.
- `https://opencode.ai/docs/agents/`
  - Primary agents are user-facing orchestrators.
  - Subagents can be invoked automatically or manually and can be constrained by `permission.task`.
  - Subagents can pin a specific `model`.
  - `permission.task` controls which subagents an orchestrator can invoke.
- `https://opencode.ai/docs/config/`
  - Configs merge from global and project sources.
  - `.opencode` directories and `~/.config/opencode` use plural directories such as `agents/` and `commands/`, with singular supported for compatibility.
  - `snapshot` is enabled locally and can support rollback through OpenCode’s undo/snapshot mechanism.

## Standard Prompt Mapping from Espanso Snippets

Source file read first as requested:

`C:\Users\DaveWitkin\AppData\Roaming\espanso\match\migrated_snippets.yml`

| Pipeline stage | Snippet comment | Trigger(s) | Source lines | Mapping confidence | Notes |
|---|---|---|---:|---|---|
| 1. Plan creation | `# OC Create New Conductor Plan` | `#createplan`, `#createtrack`, `#newplan`, `#newtrack` | 241-284 | High | Creates or updates an active Conductor track and writes `spec.md` + `plan.md`; explicitly says not to execute the plan. |
| 2. Plan review | `# OC Review Conductor Plan` | `#planrev`, `#reviewplan`, `#reviewtrack`, `#revplan` | 287-315 | High | Reviews active track `spec.md` and `plan.md`, can update confident improvements, and surfaces uncertain changes to the user. |
| 3. Conditional re-review | Same as stage 2 | Same as stage 2 | 287-315 | High | Reuses the same standard review prompt when review changed the docs beyond the selected threshold. |
| 4. Execution | `# OC Run Conductor Track` | `#runplan`, `#runtrack`, `#trackrun` | 322-341 | High | Executes pending non-deferred plan items in order, synchronizes Conductor artifacts, validates, and creates `execution-log-YYYY-MM-DD.md`. |
| 5. Validation | `# OC Validate Track Complete` | `#validaterun`, `#validatetrack` | 565-596 | High | Validates Conductor track closeout artifacts and outputs closeout verdict/evidence/mismatches/fixes/recommendation. |
| 6. Conditional re-validation | Same as stage 5 | Same as stage 5 | 565-596 | High | Reuses validation prompt after fixes or if validation finds material unresolved issues. |

Additional related validation snippet:

| Related use | Snippet comment | Trigger(s) | Source lines | Notes |
|---|---|---|---:|---|
| Non-track/peer validation | `# OC Validate Non-Track Work` | `#doublecheck`, `#peerreview`, `#validatework` | 392-438 | Useful fallback when validating work that is not contained in a Conductor track. Not the primary validation prompt for this workflow. |

## Exact Standard Prompt Text Extracted

### Stage 1: Plan Creation (`#createplan`, `#createtrack`, `#newplan`, `#newtrack`)

```text
Create a brand-new conductor track (spec.md and plan.md) that can be immediately executed by a less capable AI build agent. Do not output all of the information that you go through below to the user's screen.

Before writing tasks, briefly restate:
- the goal/outcome,
- the constraints/non-goals,
- and the definition of done.

Then produce a phased implementation plan with checkbox tasks, and enforce these standards for **every** task. You do not need to output all of the information that you go through below to the user's screen.

1. **Atomic tasks** — One clear action per checkbox. Split anything that combines multiple decisions or multiple file edits.
2. **Exact file paths** — Name precise files to create/modify (full repo-relative paths). No ambiguous "find the file" instructions.
3. **Explicit commands** — Write terminal commands verbatim (e.g., `npm install package@x.y.z`, `npm run test -- foo.spec.ts`).
4. **Clear ordering** — Put tasks in strict execution order with prerequisites first.
5. **Verification per step** — Each each task includes a concrete, deterministic command to confirm it worked (expected output, test pass, file existence, etc.).
6. **No assumed context** — Write so an unfamiliar agent can execute without extra repo exploration.
7. **Concrete examples** — Where format/structure matters, include inline templates, snippets, or expected output examples.
8. **Error recovery** — Add fallback instructions for common failures (missing dependency, failing command, occupied port, path not found, etc.).

Required plan structure:

- **Phase 0: Setup & Preconditions**
- **Phase 1+: Implementation** (split by capability or subsystem)
- **Final Phase: Validation & Handover**

For each phase, include:
- Objective sentence
- Ordered checklist tasks
- Phase-level exit criteria

At the end, include:
- **Execution readiness checklist** (pass/fail against the 8 standards)
- **Top 3 implementation risks + mitigations**
- **First task the build agent should execute immediately**

If there is an active conductor track that is a good fit for this work, update it with the proposed `spec.md` and `plan.md` content. If there is no active conductor track or the existing track is not a good fit for this work, create a condutor track and update it with the proposed `spec.md` and `plan.md` content.

Write the proposed spec.md and plan.md content into the active Conductor track files. Do not execute the plan.

After you update the conductor track files, let the user know that the track has been updated and is ready for execution. Give them brief information about the plan like how many steps there are and how many lines are in the plan.

At the end, please give me a fully qualified path to the conductor plan document so I can open a new session and run it there.
```

### Stages 2 and 3: Plan Review / Conditional Re-review (`#planrev`, `#reviewplan`, `#reviewtrack`, `#revplan`)

```text
Review the conductor plan documents (spec.md and plan.md) in the active track. This plan will be executed by a less capable AI agent. Evaluate it for maximum executability, **absolute verification rigor**, and return specific, actionable improvements.

**CRITICAL ANTI-LAZINESS MANDATE:** Do not accept passive or shallow verification steps. If a task can be verified using a CLI tool, a test script, an API call (curl), or an automated test suite, you MUST rewrite the task to include that explicit command.

**Evaluate every plan task against these criteria:**

1. **Atomic tasks** — Is each checkbox a single, clear action? Split any task that requires multiple decisions or touches multiple files.
2. **Exact file paths** — Does every task name the exact file to create or modify? No "find the right file" ambiguity.
3. **Explicit commands** — Are terminal commands written out verbatim (e.g., `npm install xyz@1.2.3`)? No vague instructions like "install the package."
4. **Clear ordering** — Is the sequence unambiguous? Are prerequisites stated where a task depends on a prior step?
5. **Rigorous Verification per step** — Does each task include a concrete, deterministic command to confirm it worked? **REJECT shallow checks like "verify file exists," "assert build succeeds," or passive "check logs" instructions. Insist on active verification (e.g., run a specific test file, execute a CLI tool with specific flags, or hit an endpoint with curl). If logic is modified, the agent must run a command that actively exercises that specific logic.**
6. **No assumed context** — Would an agent unfamiliar with this codebase understand every instruction without searching the codebase first?
7. **Concrete examples** — Where code structure or output format matters, are snippets or expected results provided inline?
8. **Error recovery** — Are common failure modes noted with fallback actions (e.g., "if port in use, kill process on :3000")?
9. **Intent & Behavioral Testing** — Does the plan ensure the *high-level intent* is covered by automated or CLI-driven tests? If the objective introduces or modifies a feature, there must be a dedicated task to write/run integration tests or execute a functional CLI workflow that proves the feature actually works as intended, not just that it runs without crashing.

**Output format:**

- List each plan task by name and phase
- Rate each:  Ready /  Needs work /  Blocking
- For any  or : provide the exact rewritten task text the planner should use
- End with an overall readiness score (percentage rated ✅) and top 3 priorities

For items you have high confidence in, go ahead and make the updates to the conductor track. If there are any changes you are uncertain about, present them to the user after you're done making the changes you are confident in.

At the end, please give me a fully qualified path to the conductor plan document so I can open a new session and run it there.
```

### Stage 4: Execution (`#runplan`, `#runtrack`, `#trackrun`)

```text
You are a Conductor track execution specialist.

Run or continue executing the relevant Conductor track. If I did not name a track and you can't infer the track from the discussion above, identify the active/pending track from `.conductor/tracks/` and confirm the target before making changes.

Use the track's `plan.md` as the source of truth. Execute only non-deferred pending items, in plan order, unless I explicitly reprioritize. Check off each completed item immediately after it is done; do not wait until the end. Keep `metadata.json` and any required Conductor artifacts synchronized when status/progress changes.

If a task is unclear and you cannot confidently infer the right action from the plan/spec/metadata, stop and notify me before proceeding. Do not silently guess. Do not execute items explicitly marked deferred, out of scope, or assigned to another track.

After execution, validate your work using the checks in the plan or the closest deterministic checks available. Create a brief issue log in the track folder named `execution-log-YYYY-MM-DD.md` documenting failed tool calls, access/API issues, skipped items, ambiguity, or other problems. If there were no issues, say so in the log.

At the end, report:
- Track name and final status
- Items completed in this run
- Items remaining
- Validation performed and result
- Any issues or skipped items
- Fully qualified Windows links/paths to the issue log, updated `plan.md`, and any other updated Conductor files
```

### Stages 5 and 6: Validation / Conditional Re-validation (`#validaterun`, `#validatetrack`)

```text
Validate this Conductor track is done before declaring completion. Does anything need to be fixed? Was the work done as expected?

Required checks:
1. `plan.md`: all non-deferred tasks are `[x]` and ordering/dependencies are respected.
2. `metadata.json`: status/progress/date fields match actual completion state.
3. `.conductor/tracks.md`: track row status and completed date match metadata.
4. Logs: execution/change log exists and records deviations, skipped items, ambiguities, and validation performed.
5. Artifact verification: every claimed modified/created file exists and contains required acceptance strings.

Output format:

## Closeout Verdict
- Ready to close
- Close with minor follow-ups
- Not ready to close

## Evidence Checked
- List exact files/paths inspected

## Mismatches Found
- List each mismatch as: `artifact -> expected -> actual`
- If none: `No mismatches found.`

## Required Fixes Before Close
- Numbered list
- If none: `No fixes required.`

## Final Recommendation
- One concise sentence.
```

## Recommended Architecture

### Short answer
Use a **single global OpenCode command** as the user entry point, backed by **dedicated subagent definitions** with explicit model pins and a small **orchestration skill/reference pack** only if the prompt becomes too large for maintainability.

The most OpenCode-native structure is:

1. **Command**: `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`
   - User invokes `/conductor-pipeline <request>`.
   - Command runs under an orchestrator-capable primary agent.
   - Command prompt defines the six stages, gates, artifact contracts, and failure behavior.
2. **Orchestrator agent**: `C:\Users\DaveWitkin\.config\opencode\agents\conductor-pipeline-orchestrator.md`
   - `mode: primary` or `mode: all`.
   - Has `permission.task` allow-list for only the stage agents.
   - Does not directly implement production code; it delegates.
3. **Stage subagents**:
   - `conductor-plan-creator` — write-enabled for `.conductor/**` documentation only; uses Conductor skill; explicit planning model.
   - `conductor-plan-reviewer` — write-enabled for `.conductor/**` documentation only; explicit different review model.
   - `conductor-track-executor` — write/edit/bash enabled for implementation; explicit `zai-coding-plan/glm-5.2`.
   - `conductor-track-validator` — read/bash-enabled, edit denied by default; explicit non-executor validation model.
4. **Optional skill/reference pack**: only if the command becomes hard to maintain.
   - Store long stage prompts and threshold policy in `C:\Users\DaveWitkin\.config\opencode\skills\conductor-pipeline\references\`.
   - The command stays thin and instructs the orchestrator to load the skill.

### Why not only a skill?
A skill is excellent for reusable instructions, but OpenCode commands are the native user-invoked workflow entry point. The official docs describe commands as the way to create repetitive tasks with fixed prompts, while local standards say commands orchestrate and agents execute.

### Why not only agent definitions?
Agents define behavior and model/tool access, but they are not enough to encode a repeatable six-stage user invocation with arguments, thresholds, and staged handoffs. A command gives a stable `/conductor-pipeline` interface.

### Why not a custom script first?
A script could compute diffs and thresholds more deterministically, but it increases maintenance and crosses into implementation. Start with an OpenCode-native command + subagents. Add a small helper script later only if the LLM-based threshold classification proves unreliable.

## Model Assignment Table

Canonical IDs verified from local tooling/config on 2026-06-28:
- GLM execution/default: `zai-coding-plan/glm-5.2` from `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` lines 208-220.
- OpenAI subscription provider: `opencode models` lists `openai/gpt-5.5`; `C:\Users\DaveWitkin\.config\opencode\opencode.json` lines 513-555 define the `gpt-5.5` model with variants `none`, `low`, `medium`, `high`, and `xhigh`. Therefore **all OpenAI LLM usage in this workflow should be `openai/gpt-5.5` with the `low` reasoning variant / `reasoningEffort: low`**. Do not use `openai/gpt-5.2-*`; that family is outdated for this workflow.
- MiniMax M3 Thinking via OpenCode Go: `opencode models` lists `opencode-go/minimax-m3`. Local DCP config also notes MiniMax M3 is served through a Go proxy (`C:\Users\DaveWitkin\.config\opencode\dcp.jsonc` lines 41-46), with historical candidate keys `go-dave/minimax-m3` and `go-tiberius/minimax-m3`. For new OpenCode agent model pins, use the model-list canonical ID: `opencode-go/minimax-m3`.

Note on "GPT-5.5 Low" syntax: `opencode models` exposes the model as `openai/gpt-5.5`, not `openai/gpt-5.5-low`. The low setting is a model variant/provider option. Final agent definitions should pin:

```yaml
model: openai/gpt-5.5
reasoningEffort: low
reasoningSummary: auto
textVerbosity: medium
```

| Stage | Proposed agent | Primary model | Fallback model(s) | Diversity rule |
|---|---|---|---|---|
| 1. Plan creation | `conductor-plan-creator` | `openai/gpt-5.5` with `reasoningEffort: low` | `opencode-go/minimax-m3` | Must not equal stage 2 model. |
| 2. Plan review | `conductor-plan-reviewer` | `opencode-go/minimax-m3` | `zai-coding-plan/glm-5.2` | Must not equal stage 1 model. |
| 3. Conditional re-review | `conductor-plan-reviewer-alt` | `openai/gpt-5.5` with `reasoningEffort: low` | `zai-coding-plan/glm-5.2` | Must not equal the immediately preceding reviewer model; must not use the same model as the plan creator if stage 2 fell back to the creator model. |
| 4. Execution | `conductor-track-executor` | `zai-coding-plan/glm-5.2` | `opencode-go/minimax-m3` only with user approval | Preferred GLM executor per Z.ai subscription/quota. |
| 5. Validation | `conductor-track-validator` | `opencode-go/minimax-m3` | `openai/gpt-5.5` with `reasoningEffort: low` | Must not equal stage 4 model. |
| 6. Conditional re-validation | `conductor-track-validator-alt` | `openai/gpt-5.5` with `reasoningEffort: low` | `opencode-go/minimax-m3` | Must not equal execution model; preferably not equal stage 5 model. |

Recommended default model route:
- Creation: `openai/gpt-5.5` + `reasoningEffort: low`
- Review: `opencode-go/minimax-m3`
- Re-review: `openai/gpt-5.5` + `reasoningEffort: low`
- Execution: `zai-coding-plan/glm-5.2`
- Validation: `opencode-go/minimax-m3`
- Re-validation: `openai/gpt-5.5` + `reasoningEffort: low`

**Cost rationale:** MiniMax M3 is the primary validation gate so the workflow uses the cheaper/different-family model for routine closeout checks and reserves OpenAI GPT-5.5 credits for the conditional re-validation escalation path, where a stronger second opinion is most valuable.

This satisfies the non-negotiable gates: reviewer ≠ creator and validator ≠ executor. It also uses three independent model families/providers across the full pipeline: OpenAI GPT-5.5 Low, MiniMax M3 via OpenCode Go, and Z.ai GLM 5.2.

### Why MiniMax M3 Thinking belongs in the workflow

The previous draft did not include MiniMax because the initial local config text search did not find a configured `minimax` provider/model in `opencode.jsonc`. A direct `opencode models` check shows the canonical available model is `opencode-go/minimax-m3`, and your DCP config confirms MiniMax M3 is served through the Go proxy.

Recommended use: make MiniMax M3 the **primary independent plan reviewer** and **alternate validator/re-validator**. That gives the workflow a genuinely different model family at verification gates instead of only alternating OpenAI and GLM.

## Conditional Trigger Options for User Choice

### Stage 3: Re-review trigger options

Option A — **Diff-size threshold (recommended default)**
- Run one additional re-review if the reviewer changed either `spec.md` or `plan.md` by **≥25 changed lines** or **≥20% of total non-blank lines**, whichever is smaller.
- Why: easy to measure and catches major rewrites.

Option B — **Structural threshold**
- Run one additional re-review if any of these changed:
  - acceptance criteria count changed by ≥2,
  - phase count changed,
  - task count changed by ≥20%,
  - any task marked `Blocking` remains unresolved.
- Why: focuses on meaningful plan structure rather than line churn.

Option C — **Risk threshold**
- Run one additional re-review if the review reports:
  - readiness score <90%, or
  - ≥1 Blocking item, or
  - ≥3 Needs Work items.
- Why: mirrors the plan review rubric.

Recommended: **Option B + C hybrid** — re-review when structural changes are large OR readiness remains below 90% OR any Blocking item remains.

### Stage 6: Re-validation trigger options

Option A — **Verdict threshold (recommended default)**
- Run one re-validation after fixes if closeout verdict is `Not ready to close` or if `Close with minor follow-ups` includes any required fix that touches production files.

Option B — **Issue severity threshold**
- Run one re-validation if validation finds:
  - ≥1 critical mismatch,
  - ≥2 major mismatches,
  - ≥3 required fixes total,
  - any failed deterministic validation command.

Option C — **Acceptance criteria threshold**
- Run one re-validation if:
  - ≥1 acceptance criterion is unmet,
  - any non-deferred `plan.md` checkbox remains unchecked,
  - `metadata.json` progress differs from actual checklist completion by >5 percentage points.

Recommended: **Option A + C hybrid** — re-validate after fixes if not ready to close, any acceptance criterion is unmet, or Conductor status/progress is inconsistent.

## Max Iteration Caps

| Loop | Default cap | Rationale | Escalation after cap |
|---|---:|---|---|
| Conditional re-review | 1 extra pass | Usually enough to catch reviewer-induced gaps without burning quota. | Pause and ask user to approve manual plan correction or proceed with known risks. |
| Conditional re-validation | 1 extra pass after fixes | Prevents validation/fix loops from cycling indefinitely. | Produce `validation-blockers.md` and ask user whether to run another execution/fix cycle. |

Allow an advanced flag later, e.g. `/conductor-pipeline --max-review-passes 2 --max-validation-passes 2`, but default should stay conservative.

## Context Handoff Contracts

Each subagent must receive a self-contained prompt. Do not assume child sessions share state.

| Boundary | Producing step artifacts | Passed to next step |
|---|---|---|
| User request → Plan creation | User request text; repo root; relevant initial constraints; exact stage 1 prompt; Conductor skill instruction | Full user request; repo path `C:\development\opencode` or current workspace; active track detection rule; exact plan creation prompt; required output paths. |
| Plan creation → Plan review | `.conductor/tracks/<track-id>/spec.md`; `.conductor/tracks/<track-id>/plan.md`; `metadata.json`; brief creator summary | Full absolute paths to `spec.md`, `plan.md`, `metadata.json`; exact stage 2 prompt; original user request; creator model ID; instruction that reviewer model must differ. |
| Plan review → Conditional re-review decision | Updated docs; review report; diff summary; readiness score; unresolved questions | Diff summary and threshold evaluation; if triggered, pass full updated docs, previous review report, original request, and exact review prompt to alternate reviewer. |
| Review complete → Execution | Final reviewed `spec.md`/`plan.md`; metadata; review report(s); unresolved questions cleared or user-approved | Full absolute track path; exact execution prompt; final plan/spec; review reports; known risks; explicit instruction to execute only non-deferred tasks in order. |
| Execution → Validation | Updated track files; execution log; git diff/status; test/command outputs; executor summary | Full absolute paths to updated `spec.md`, `plan.md`, `metadata.json`, ledgers, execution logs, changed files list, validation commands/results, and exact validation prompt. |
| Validation → Conditional re-validation decision | Validation report; closeout verdict; required fixes; mismatch list | If fixes were applied or required, pass updated artifacts, prior validation report, issue resolution notes, and exact validation prompt to alternate validator. |
| Final validation → User | Final validation report; status; remaining risks; paths | Concise final status with absolute Windows paths to plan, logs, reports, and remaining blockers. |

Recommended artifact names inside each Conductor track:
- `review-report-YYYY-MM-DD-HHMMSS.md`
- `review-diff-summary-YYYY-MM-DD-HHMMSS.md`
- `execution-log-YYYY-MM-DD.md` (already matches standard prompt)
- `validation-report-YYYY-MM-DD-HHMMSS.md`
- `validation-blockers-YYYY-MM-DD-HHMMSS.md` only when blocked.

## Failure and Rollback Path

### Model unavailable
1. Orchestrator records `model-unavailable` in the run log with attempted model ID and stage.
2. Select fallback model from the table while preserving diversity rules.
3. If no fallback satisfies diversity, pause and ask the user whether to:
   - allow same-provider but different reasoning variant,
   - allow same model family but different provider/account,
   - or stop.

### Plan creation or review fails
1. Do not proceed to execution.
2. Save partial artifacts if available.
3. Produce a plain-language question with exact missing context.

### Execution fails mid-way
1. Executor stops on unclear/destructive/blocked tasks.
2. Executor updates `plan.md` only for completed tasks and leaves incomplete tasks unchecked.
3. Executor writes `execution-log-YYYY-MM-DD.md` with:
   - completed tasks,
   - failed command/tool call,
   - files changed before failure,
   - suggested rollback or resume point.
4. Orchestrator runs validation only if there is enough evidence to assess partial state; otherwise it pauses.
5. Rollback options:
   - Prefer OpenCode `/undo` or snapshots when the failed execution occurred in the same session.
   - Use Git only as an inspection mechanism unless user explicitly approves reset/revert.
   - Never auto-delete untracked files without user confirmation.

### Validation finds major issues
1. If issues are fixable within the original scope, route back to execution once, with validator report as input.
2. After one fix/re-validation loop, stop and ask user for approval before additional cycles.
3. If issues reveal a flawed plan, route back to plan review instead of repeatedly executing.

## Open Design Questions for Dave

> **RESOLVED 2026-06-28.** Dave approved the architecture and threshold defaults. Decisions:

| # | Question | Decision |
|---|---|---|
| 1 | Autonomy level | **Full auto through validation.** No human checkpoint between stages; the documented execution-failure safety net (stop on unclear/destructive/blocked tasks) still applies. |
| 2 | Re-review threshold (Stage 3) | **B+C hybrid.** Re-review when structural changes are large OR readiness <90% OR any Blocking item remains. |
| 3 | Re-validation threshold (Stage 6) | **A+C hybrid.** Re-validate after fixes if not ready to close, any acceptance criterion unmet, or Conductor progress inconsistent. |
| 4 | OpenAI syntax | Accepted: `openai/gpt-5.5` + `reasoningEffort: low` for all OpenAI usage. `gpt-5.5-fast` is not in the default route; whether to allow it as an emergency fallback is deferred to the Phase 3 build decision. |
| 5 | MiniMax role | Accepted: `opencode-go/minimax-m3` as default plan-reviewer and re-validator via OpenCode Go. |
| 6 | Command vs skill | **Command + skill reference pack.** Thin command; long prompts live in `skills/conductor-pipeline/`. |


1. **Autonomy level:** Should `/conductor-pipeline` pause for approval after plan review and before execution by default? Recommended: yes, because execution changes production files.
2. **Re-review threshold:** Choose Option A, B, C, or recommended B+C hybrid.
3. **Re-validation threshold:** Choose Option A, B, C, or recommended A+C hybrid.
4. **OpenAI agent syntax:** Use `model: openai/gpt-5.5` plus `reasoningEffort: low` in agent frontmatter/options for all OpenAI usage; confirm whether you want `gpt-5.5-fast` avoided entirely or allowed as an emergency fallback.
5. **MiniMax role:** Use `opencode-go/minimax-m3` as the default plan-review and re-validation model via the OpenCode Go plan/key unless live testing shows provider failure.
6. **Skill vs command size:** Should the long prompt text live directly in `conductor-pipeline.md`, or should we create a reusable `conductor-pipeline` skill with reference files and keep the command thin?

## Requirements
- [ ] User can invoke one stable workflow entry point for concept-to-validation orchestration.
- [ ] Workflow uses Conductor tracks as the source of truth for plans and execution state.
- [ ] Reviewer model is never the same model as creator model.
- [ ] Validator model is never the same model as executor model.
- [ ] Each subagent receives a self-contained context packet with absolute artifact paths and the exact standard prompt for its stage.
- [ ] Conditional loops have quantified thresholds and hard iteration caps.
- [ ] Failure handling stops unsafe execution and preserves enough logs for resume/rollback.
- [ ] User-facing output uses fully qualified absolute Windows paths.

## Non-Requirements
- [ ] Do not implement production application code in this planning track.
- [ ] Do not create final workflow command/agent files until Dave approves architecture and threshold defaults.
- [x] MiniMax M3 Thinking canonical model ID found via `opencode models`: `opencode-go/minimax-m3`.
- [ ] Do not rely on child subagent session state carrying forward automatically.

## Acceptance Criteria
- [x] Each of the 6 pipeline steps maps to an identified standard prompt from `migrated_snippets.yml`.
- [x] Model assignments are specified for every step with diversity rules verified at the gate level.
- [x] Conditional triggers have concrete, measurable threshold options.
- [x] Context handoff is explicitly defined for every step boundary.
- [x] A max-iteration cap prevents infinite conditional loops.
- [x] A fallback/rollback path exists for model unavailability and execution failure.
- [x] Dave approves threshold defaults and autonomy checkpoints (approved 2026-06-28: full-auto, B+C re-review, A+C re-validation, command+skill).
- [ ] Final command/agent/skill files are created after approval.
