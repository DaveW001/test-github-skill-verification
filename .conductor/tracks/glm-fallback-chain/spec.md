# Spec: GLM fallback chain

Track ID: `glm-fallback-chain`

## Stage 1 restatement

### Goal / outcome
Implement a procedural, documented three-tier fallback chain for Conductor pipeline GLM-5.2 failures:

1. Tier 1 primary: `zai-coding-plan/glm-5.2`
2. Tier 2 fallback 1: `zai-coding-plan/glm-5.1`
3. Tier 3 fallback 2 / last resort: `opencode-go/qwen3.7-plus`

The chain must retry GLM-5.2 on transient failure, identify failures reliably via provider timeouts and explicit `model-unavailable` reporting, then fall back to GLM-5.1 and finally Qwen 3.7 Plus.

### Constraints / non-goals
- OpenCode has no native model fallback; `AgentConfig.model` is a single string and there is no `fallbackModels` field.
- The orchestrator cannot override a Task subagent's pinned model and cannot swap its own model at runtime.
- Only two GLM-5.2 pipeline agents are in scope: `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` and `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md`.
- Preserve diversity: validator remains `opencode-go/minimax-m3`; every executor tier differs from it.
- Execution must be shell-first via PowerShell 7+ through the `bash` tool because native file tools return `Bun is not defined`.
- Back up `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` before editing.

### Definition of done
- `SKILL.md` and `threshold-policy.md` state the exact three-tier chain, failure signals, retry counts, fallback executor subagents, diversity note, and orchestrator self-swap limitation.
- Two new hidden fallback executor subagents exist with correct pinned models and near-copy executor instructions.
- The orchestrator can legally invoke all three executor variants and its body describes retry/fallback routing.
- `opencode.jsonc` has timeout options for `zai-coding-plan` and `opencode-go`, with a backup taken first.
- Final validation proves all three model IDs are available, agent frontmatter model lines are correct, JSONC parses with a JSONC-tolerant parser, and orchestrator task permissions list all executor variants.

## Required design

### Provider timeout detection
Add `options.timeout = 600000`, `options.headerTimeout = 60000`, and `options.chunkTimeout = 120000` to both `zai-coding-plan` and `opencode-go` provider blocks so freezes, overload, unreachable providers, and stalled streams become detectable failures.

### Retry/fallback protocol
Transient failure signals are: timeout/abort, HTTP 429, HTTP 5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze, or stream stall.

Retry the same tier up to two additional attempts with brief backoff. Escalate from Tier 1 to Tier 2, then Tier 3. If Tier 3 fails, log `model-unavailable` with attempted model, stage, tier, and failure signal, then stop and ask.

### Stage 4 routing table

| Tier | Subagent | Model |
|---|---|---|
| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` |
| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` |
| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` |

### Orchestrator limitation
The orchestrator remains pinned to `zai-coding-plan/glm-5.2` and cannot self-swap at runtime. Provider timeouts fail fast. If the orchestrator's own model is unavailable, recovery is to restart OpenCode after the failure is surfaced, optionally after changing the orchestrator `model:` line to a fallback tier.

## Files in scope
- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md` (new)
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md` (new)
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`

## Implementation analysis: failure-detection scope & limitations (added 2026-07-02)

Post-implementation question: "If the orchestrator calls a subagent and it returns no text for 3-5 minutes, will the pipeline identify that and act?" This records the honest answer.

### Two timer layers

| Layer | Bounded? | Mechanism |
|---|---|---|
| Provider HTTP layer (one model<->provider request) | Yes | `options.timeout` 600000 ms / `headerTimeout` 60000 ms / `chunkTimeout` 120000 ms on `zai-coding-plan` and `opencode-go` |
| Task-tool / subagent layer (whole child invocation: many turns + tool calls) | No | OpenCode provides no per-agent execution timeout; the Task tool exposes no `timeout` parameter |

### Caught (the dominant real-world GLM failure)
A frozen/overloaded/unreachable provider: `chunkTimeout` (2 min) aborts the model request inside the subagent and surfaces it as an error (previously it hung forever). The executor then reports `model-unavailable` and the orchestrator applies retry/escalation (same tier x2 -> next tier -> stop). So for provider-side stalls, detection ~2 min, recovery automatic.

### Not caught (the gap)
A subagent stalled on a NON-model operation - a bash/tool call blocking indefinitely with no timeout, a hung MCP tool, `Read-Host`/`-Wait`/`tail -f`, or any command the provider timeouts never reach. There is NO orchestrator-level watchdog: the Task-tool call blocks indefinitely until a human stops the run, and the fallback chain does NOT engage (it is triggered by the subagent's RETURNED message, which never arrives). Root cause: OpenCode has no per-agent execution-timeout primitive; provider timers reach only the model HTTP layer, not the child's agentic loop or tool calls. This cannot be closed from configuration alone.

### Mitigation applied 2026-07-02 (cheap, child-side)
Tool-call self-bounding added to all three executor agent bodies and to the Stage 4 prompt in `references/stage-prompts.md`: every bash call MUST carry an explicit `timeout` (e.g. `timeout: 120000`), and executors must never run commands that can block indefinitely (interactive prompts, uncapped network calls, Wait-Process/-Wait, tail -f, Start-Process -Wait, servers/watch processes). A tool-side hang now self-aborts inside the child and surfaces as a failed tool call instead of stalling the pipeline. This removes the most common non-model-stall trigger.

### Residual gap + recommended platform fix
The only complete fix is a per-agent execution timeout that aborts the Task-tool call after N idle/progress-less minutes - an OpenCode platform feature that does not yet exist. Until it ships, the child-side self-bounding above is the practical defense, and the operational fallback is: if an orchestrator run goes silent past ~6-8 min, treat it as a stuck child, stop manually, and re-run.

### Operational note
Backups for this follow-up edit set: `C:\development\opencode\.conductor\tracks\glm-fallback-chain\backups\2026-07-02-pre-edit\` (per `references/global-skill-versioning.md`).
