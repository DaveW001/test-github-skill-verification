# Conductor Tracks Ledger

This ledger tracks all active, completed, and archived tracks in this repository.

## Active Tracks


- [20260630-conductor-skill-hardening](./tracks/20260630-conductor-skill-hardening/spec.md): Harden the global conductor-pipeline skill with the remaining retro recommendations: Stage 1 plan-authoring hardening (one authoritative acceptance check, diagnostic separation, body-content verification, literal matching), Stage 2 reviewer dry-run enforcement, metadata schema cleanup (task_count/readiness_check_count/total_checkbox_count/completed_tasks), a new powershell-pitfalls.md reference, and a new global-skill-versioning.md reference. All 5 scoped body checks pass. (Phase: executed 2026-06-30)

- [20260630-conductor-pipeline-run-retro](./tracks/20260630-conductor-pipeline-run-retro/spec.md): Retrospective on the successful Conductor Pipeline retro-improvements run, focusing on plan quality, reviewer regression prevention, metadata/checklist semantics, and environment/tool preflight propagation. (Phase: executed 2026-06-30)


- [20260629-conductor-pipeline-retro-improvements](./tracks/20260629-conductor-pipeline-retro-improvements/spec.md): Codify all retrospective improvements from the Hello World smoke-test pipeline run, including file-state classification, semantic idempotency, append-only verification, exact dry-run standards, closeout sync, scope-language clarity, tool preflight propagation, runbooks, and helper scripts. (Phase: executed 2026-06-29)

- [20260628-multi-agent-conductor-orchestration](./tracks/20260628-multi-agent-conductor-orchestration/spec.md): Design an OpenCode-native six-stage Conductor pipeline from idea to validation using command entry point, model-pinned subagents, explicit handoffs, measurable conditional gates, max-loop caps, and failure/rollback paths. (Phase: built 2026-06-28; runtime dry-run pending restart)




- [20260628-opencode-session-message-seq-fatal](./tracks/20260628-opencode-session-message-seq-fatal/spec.md): Resolve FATAL 'NOT NULL constraint failed: session_message.seq' that blocks all scheduled opencode run jobs (agent/model switch path) by upgrading the pre-fix 1.15.10 runtime to v1.17.11 (upstream fix 8bc501b; issues #31204/#31412/#31413/#31606). DB is healthy (integrity ok, source-of-truth intact) so no wipe. Also fix secondary DCP plugin '@anthropic-ai/tokenizer' load failure by re-resolving cache to 3.1.14. (Phase: planning - ready for execution)
- [20260629-smoke-test-hello-world](./tracks/20260629-smoke-test-hello-world/spec.md): Append one Hello World toy/sanity-check documentation section to `.conductor/smoke-test/hello-world.md`, preserving all existing content via pre-edit backup and path-scoped git diff verification. (Phase: executed 2026-06-29)
- [20260615-glm-52-model-migration](./tracks/20260615-glm-52-model-migration/spec.md): Migrate all OpenCode agent models from GLM 5.1/4.7 to GLM 5.2. Two-layer architecture: primary agents inherit global default (overridable per-session), subagents pinned with explicit model for cost isolation from expensive orchestrators like GPT-5.5. (Phase: ready-for-build)
- [20260608-opencode-desktop-startup-freeze](./tracks/20260608-opencode-desktop-startup-freeze/spec.md): Diagnose and recover OpenCode Desktop 1.16.0 startup freeze caused by renderer message timeline load of an oversized persisted session, with separate follow-up for scheduled-run `session_message.seq` database write errors. (Phase: incident plan ready)
- [20260526-opencode-desktop-log-remediation](./tracks/20260526-opencode-desktop-log-remediation/spec.md): Remediate May 26 Desktop startup issues by clearing broken plugin caches, resolving Git snapshot GC blockage, and handling duplicate skill-root warnings only if still needed after primary fixes. (Phase: completed)
- [20260519-opencode-desktop-performance-skillful-isolation](./tracks/20260519-opencode-desktop-performance-skillful-isolation/spec.md): Isolate OpenCode Desktop slowdown by validating MCP disablement, inspecting lazy Skillful discovery, and A/B testing Desktop with `@zenobius/opencode-skillful` disabled before considering reinstall. (Phase: phase5-handover)
- [20260519-opencode-desktop-config-troubleshoot](./tracks/20260519-opencode-desktop-config-troubleshoot/spec.md): Diagnose OpenCode Desktop config/runtime issue after dual OpenCode Go subscription setup; leading hypothesis is Desktop cannot see `.env`-only Go API key variables, with secondary checks for `/models` provider ambiguity and Desktop state drift. (Phase: go-dual-sub-diagnosis)
- [army-kb-extraction](./tracks/army-kb-extraction/spec.md): Extract Army knowledge (challenges, key people, agile practices/frameworks) from NotebookLM for the Packaged Agile KB. (Phase: planning)
- [20260428-kb-ingest-troubleshoot](./tracks/20260428-kb-ingest-troubleshoot/spec.md): Diagnose and fix the hourly KB ingest scheduled job (`Session not found` error). (Phase: diagnosis)
- [20260429-openai-silent-failure](./tracks/20260429-openai-silent-failure/spec.md): Patched oc-chatgpt-multi-auth cached runtime for OpenAI silent failures: parseable JSON 502 on malformed/no-terminal SSE, 120s stream stall default, gpt-5.4-mini preservation, and DEBUG_CHATGPT_PROXY diagnostics. (Phase: validation pending live OpenCode model tests)
- [20260411-notebooklm-cli-install](./tracks/20260411-notebooklm-cli-install/spec.md): Install notebooklm-mcp-cli (nlm CLI v0.6.5) and official OpenCode skill, archive legacy custom skill. (Phase: validation complete, awaiting user auth)
- [20260530-global-skills-index-regen](./tracks/20260530-global-skills-index-regen/spec.md): Regenerate global-skills-index.md to include all 64 active skills (currently only 40 listed, 27 missing, 1 duplicate). (Phase: pending)




- [20260526-system-prompt-token-audit](./tracks/20260526-system-prompt-token-audit/spec.md): Audit and reduce the OpenCode system prompt from ~29,001 tokens to <=15,000 tokens. Local reductions applied (~2,535 tokens saved), skill YAML repaired, corruption removed, all 33 plan tasks completed. Target not locally achievable - non-local components total ~17,053 tokens. (Phase: completed)



- [20260531-prompt-schema-overhead-research](./tracks/20260531-prompt-schema-overhead-research/spec.md): Research remaining OpenCode system prompt overhead from Codex/account tooling, MCP/plugin tool schemas, native tool schemas, task/subagent definitions, and runtime scaffolding to determine whether the 15,000-token target is reachable through safe config changes, aggressive reversible toggles, or upstream OpenCode changes. (Phase: validation-complete)
- [20260614-image-ocr-skill](./tracks/20260614-image-ocr-skill/spec.md): Create a new OpenCode skill (image-ocr) that extracts plain text from images and outputs clean Markdown. Two-tier architecture: Gemini 2.5 Flash primary (best quality, free tier) with Tesseract offline fallback (zero setup). Mirrors visual-ocr Gemini API patterns and doc-to-markdown batch/output patterns. (Phase: planning-complete-ready-for-build)


## Completed Tracks

- [20260629-dcp-complete-outage-fix](./tracks/20260629-dcp-complete-outage-fix/spec.md): Restore @tarquinen/opencode-dcp plugin to a loading state by replacing the incomplete 3.1.13 cache install (missing @anthropic-ai/tokenizer) with a clean 3.1.14 install. DCP-only scope; did not touch runtime/SQLite/scheduler/opencode.jsonc. (Completed: 2026-06-30)
- [20260623-api-key-centralization-index](./tracks/20260623-api-key-centralization-index/spec.md): Create a metadata-only API key discovery index, add an AGENTS.md lookup rule, fix conductor-reporter .env gitignore coverage, and clean handover encoding artifacts without moving or exposing secret values. (Completed: 2026-06-24)- [20260613-dcp-token-savings-analysis](./tracks/20260613-dcp-token-savings-analysis/spec.md): Quantify Dynamic Context Pruning (DCP) token + USD savings across the last 100 OpenCode sessions into one self-contained HTML report with overall totals, per-model breakdown (tokens saved + DCP call counts), and a total-savings headline. Python 3 stdlib only; reads DCP state + opencode storage; offline. (Completed: 2026-06-13)
- [20260622-glm-52-non-thinking-variant](./tracks/20260622-glm-52-non-thinking-variant/spec.md): Add a 'none' reasoning variant to GLM 5.2 so thinking can be toggled off via Ctrl+T. Config variants merge with built-in {high, max}, yielding {high, max, none}. Variant overrides hardcoded forced thinking at request time (highest merge precedence). Single model, no alias. (Completed: 2026-06-22)

- [20260531-osgrep-comprehensive-test-suite](./tracks/20260531-osgrep-comprehensive-test-suite/spec.md): Executed comprehensive 47-test suite for OsGrep CLI-only canary mode. All 14 blocking tests passed, 31 non-blocking tests verified. Produced unified report, process snapshots, and resolved debug wrapper Windows UTF-8/args bugs. (Completed: 2026-05-31)

- [20260526-skillful-local-patch](./tracks/20260526-skillful-local-patch/spec.md): Patched @zenobius/opencode-skillful@1.2.5 dist/index.js to fix TypeError: __require is not a function by replacing Bun-specific import.meta.require with Node.js createRequire polyfill. All 17 tasks complete, syntax verified, backup and diff saved. (Completed: 2026-05-26)

- [20260511-clickup-windows-encoding-fix](./tracks/20260511-clickup-windows-encoding-fix/spec.md): Fixed UnicodeEncodeError on Windows by adding UTF-8 reconfigure to shared common.py module. All 14 tasks complete, smoke tests passed, troubleshooting doc updated. (Completed: 2026-05-11)
- [20260508-scheduler-desktop-cli-diagnostics](./tracks/20260508-scheduler-desktop-cli-diagnostics/spec.md): Diagnosed OpenCode Scheduler Desktop/CLI divergence. Found scheduler present in cache (packages path) but absent from global config plugin array; hourly scheduled task corrupted (registered but definition missing). Decision: Revise restore track. 19/19 artifacts collected, diagnostic report and handover complete. (Completed: 2026-05-08)
- [20260508-website-regression-guardrails](./tracks/20260508-website-regression-guardrails/spec.md): Tuned website visual regression into a low-noise quality guardrail. Weekly schedule, PR path filters, non-blocking scheduled runs, reduced P0 routes to home+contact, added link/accessibility/health checks, documented failure triage and known issues. All validation passed. (Completed: 2026-05-08)
- [20260502-lazy-skill-discovery-regression](./tracks/20260502-lazy-skill-discovery-regression/spec.md): Fixed lazy skill discovery regression caused by plugin config in wrong directory. Root cause: config at `~/.config/opencode/` but plugin searches `~/.config/opencode-skillful/`. Also moved leaked microsoft-graph skill to vault, fixed 5 stale doc refs, added frontmatter. All smoke tests pass: 48 skills discovered via skill_find, skill_use works with underscores. (Completed: 2026-05-02)
- [20260502-disable-md-table-formatter-plugin](./tracks/20260502-disable-md-table-formatter-plugin/spec.md): Disabled `@franlol/opencode-md-table-formatter@0.0.3` from global OpenCode plugin array. Timestamped backup created, config parsing validated, reference docs updated to 6 plugins. (Completed: 2026-05-02)
- [20260501-skill-token-optimization](./tracks/20260501-skill-token-optimization/spec.md): Completed skill token optimization migration using @zenobius/opencode-skillful; native skill prompt reduced from 53 to 5 core skills; ~93% token reduction achieved. Lazy skills remain available through skill_find/skill_use. (Completed: 2026-05-01)
- [20260501-codex-multi-auth-upgrade](./tracks/20260501-codex-multi-auth-upgrade/spec.md): Upgraded runtime from oc-chatgpt-multi-auth@5.4.4 to oc-codex-multi-auth@6.1.8 by fixing effective global config source (`opencode.jsonc`), validating plugin cache, Codex account health/tools, required models, env timeout, rollback cache preservation, and supersession note linkage. (Completed: 2026-05-01)
- [openai-parameter-fix](./tracks/openai-parameter-fix/spec.md): Fixed OpenAI SDK parameter mismatch by pinning `@ai-sdk/openai` provider and patched `oc-chatgpt-multi-auth` missing arguments on deferred tools. All 5 validation gates passed. (Completed: 2026-04-29)
- [20260429-email-calendar-mcp-audit](./tracks/20260429-email-calendar-mcp-audit/spec.md): Fix Outlook email skills tool-name mismatch, install Google Gmail/Calendar MCP server, create Outlook calendar skills, and document test plan. All 6 phases complete. (Completed: 2026-04-29)
- [20260430-google-skills](./tracks/20260430-google-skills/spec.md): Created 6 Google-side skills (gmail-inbox-triage, gmail-draft-reply, google-calendar-today, google-calendar-schedule, unified-calendar-today, google-contacts) with reference.md files. All phases complete. (Completed: 2026-04-29)
- [20260501-scheduler-headless-hardening](./tracks/20260501-scheduler-headless-hardening/spec.md): Migrated 4 OpenCode scheduled tasks to wscript/VBS headless launcher pattern, created runbook, updated scheduler skill v2.1.0. All validation passed. (Completed: 2026-05-01)

- [20260502-skill-junction-unification](./tracks/20260502-skill-junction-unification/spec.md): Established lazy vault as single source of truth for all 63 skills (56 OpenCode + 7 built-in Codex). Bridged 6 always-on skills into vault via junctions, deduplicated pptx-to-pdf-converter, preserved 7 built-in Codex skills, replaced individual junctions with single parent-level junctions in Codex and .agents. Plugin configured with single basePath. (Completed: 2026-05-05)
- [20260614-image-ocr-glm-primary](./tracks/20260614-image-ocr-glm-primary/spec.md): Inverted image-ocr engine priority: GLM-OCR (Z.AI dedicated OCR model) is now Tier 1 primary, Gemini 2.5 Flash demoted to Tier 2 secondary, Tesseract stays Tier 3 offline fallback. Raw httpx integration with Pillow format conversion + downscale. Live-validated 2026-06-15: 4-line test image OCR'd perfectly via both --engine glmocr and --engine auto (frontmatter confirms engine: glm-ocr). (Completed: 2026-06-15)

## Archived Tracks

*(None yet)*







