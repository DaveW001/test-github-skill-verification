# Spec: Conductor Pipeline `write`-Permission Fix + Anomaly Logging

## Goal / Outcome
Two outcomes:
1. Eliminate mid-run permission prompts caused by the `write` tool being authorized nowhere, so conductor-pipeline runs (and any agent that creates files) never pause on file creation. Establish a durable permission model whose real guardrail is the destructive-bash `ask` rules, not the write/edit distinction.
2. Add a bounded, structured anomaly/incident log so operational anomalies (permission prompts, tool errors, model fallbacks, destructive-ask, deviations, retries) are queryable per-run and as cross-track trend data - replacing "infer from structure" with "grep the log".

## Background / Root Cause
Retrospective `conductor-pipeline-write-permission-retro-2026-07-02.md` determined:
- The `write` tool (create/overwrite) is absent from the global `opencode.jsonc` permission block and from every conductor subagent frontmatter.
- `edit` (modify existing) IS granted, but `edit` != `write` in opencode.
- No `mode`/`yolo` override exists, so unlisted tools default to ASK.
- Pipeline stages that create new files invoke `write` and prompt the user.
- The defect was masked by the 2026-06-30 shell-first workaround for `Bun is not defined`.
- No structured, queryable anomaly log exists; DCP context logs embed full system prompts so keyword search is pure noise (matched all 417 files).

## Why global `write: allow` is safe
`bash: allow` already grants every agent equivalent file-write power (PowerShell `Set-Content`, `Out-File`, redirection). A missing `write: allow` is friction, not a security boundary. The genuine guardrail is the existing destructive-bash `ask` rules (`rm *`, `git reset*`, `git clean*`, `del *`), which remain unchanged.

## Anomaly-log design (approved by user 2026-07-03)
- **Primary store:** global `.conductor/logs/pipeline-anomalies.jsonl`, append-only, ONE line per anomaly.
- **Per-run view:** generated at validation closeout by filtering the JSONL for the track id -> readable `anomaly-summary-<date>.md` in the track dir. Agents learn ONE write path (the global JSONL).
- **Closed taxonomy:** `permission-prompt` | `tool-error` | `model-fallback` | `destructive-ask` | `deviation` | `retry` | `other`.
- **Severity:** `info` | `warn` | `error`.
- **Schema (one JSONL line):** `{"ts":"ISO-8601 UTC","track":"<track-id>","stage":"<n-name>","subagent":"<name>","type":"<taxonomy>","severity":"<sev>","detail":"<terse>"}`.
- **Cap:** rotate (FIFO ARCHIVE, not truncate) at 5,000 lines. Rolled-off lines move to `.conductor/logs/pipeline-anomalies.archive-<ts>.jsonl`. At ~250 bytes/line, 5,000 lines ~ 1.25 MB; archived history retained.
- **All stages append** (not just executor): plan-creator, reviewer(s), executor, validator, orchestrator.
- **Honest limitation:** a permission prompt at the opencode PLATFORM layer is not always visible to the triggering subagent (surfaces to user/main thread). The agent-emitted log captures everything agents CAN observe. Full automatic capture of every platform permission-event needs an opencode feature (permission-event hook / DCP plugin event) - flagged as a recommended platform enhancement, NOT deliverable from config.

## Scope
- **In scope:** Global `opencode.jsonc` permission; conductor subagent frontmatter; conductor-pipeline skill docs (SKILL.md, stage-prompts.md, new anomaly-logging.md reference); agent-development-standards note; the global anomaly log + rotation convention.
- **Out of scope:** Changing destructive-bash `ask` rules. Changing model assignments. Production/application code. Removing the shell-first fallback. Building an opencode platform permission-event hook (flagged as future work only).

## Acceptance Criteria
1. `opencode.jsonc` `permission` block contains `"write": "allow"`.
2. Each conductor agent that creates files grants `write: allow` in frontmatter: conductor-plan-creator, conductor-plan-reviewer, conductor-plan-reviewer-alt, conductor-track-executor, conductor-track-executor-glm51, conductor-track-executor-qwen, conductor-pipeline-orchestrator, conductor-track-validator, conductor-track-validator-alt. The two validator agents (validator + validator-alt) KEEP `edit: deny`.
3. New reference `conductor-pipeline\references\anomaly-logging.md` exists and documents: taxonomy, severity, JSONL schema, the 5,000-line FIFO-archive rotation rule, the all-stages-append rule, the closeout per-track summary generation, and the platform-limitation note.
4. `stage-prompts.md` Tool-preflight section contains an "Anomaly logging" bullet; each stage closeout contains an append-to-`pipeline-anomalies.jsonl` instruction.
5. `conductor-pipeline\SKILL.md` Related references lists `anomaly-logging.md`.
6. `.conductor\logs\` directory exists; `pipeline-anomalies.jsonl` seeded; a `pipeline-anomalies.README.md` documents the format (JSONL cannot hold inline comments).
7. A permission-baseline checklist is added to agent-development-standards (or AGENTS.md reference): agents that create files must grant both `write` and `edit`.
8. Timestamped backups exist for every edited config/agent/skill file before changes.
9. No production/runtime application code is modified.

## Constraints / Non-goals
- Do not weaken the destructive-bash `ask` rules.
- Do not change the read-only intent of the validator beyond allowing it to emit its report.
- File tools (Bun layer) may be down during execution; use PowerShell-first via `bash` if so (literal `[string]::Replace()`, not regex `-replace`).

