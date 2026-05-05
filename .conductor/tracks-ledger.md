# Conductor Tracks Ledger

This ledger tracks all active, completed, and archived tracks in this repository.

## Active Tracks

- [20260502-skill-junction-unification](./tracks/20260502-skill-junction-unification/spec.md): Repair 49 broken Codex junctions and establish lazy vault as single source of truth for all 54 skills via parent-level directory junctions + plugin basePaths expansion. (Phase: planning)
- [army-kb-extraction](./tracks/army-kb-extraction/spec.md): Extract Army knowledge (challenges, key people, agile practices/frameworks) from NotebookLM for the Packaged Agile KB. (Phase: planning)
- [20260428-kb-ingest-troubleshoot](./tracks/20260428-kb-ingest-troubleshoot/spec.md): Diagnose and fix the hourly KB ingest scheduled job (`Session not found` error). (Phase: diagnosis)
- [20260429-openai-silent-failure](./tracks/20260429-openai-silent-failure/spec.md): Patched oc-chatgpt-multi-auth cached runtime for OpenAI silent failures: parseable JSON 502 on malformed/no-terminal SSE, 120s stream stall default, gpt-5.4-mini preservation, and DEBUG_CHATGPT_PROXY diagnostics. (Phase: validation pending live OpenCode model tests)




## Completed Tracks

- [20260502-lazy-skill-discovery-regression](./tracks/20260502-lazy-skill-discovery-regression/spec.md): Fixed lazy skill discovery regression caused by plugin config in wrong directory. Root cause: config at `~/.config/opencode/` but plugin searches `~/.config/opencode-skillful/`. Also moved leaked microsoft-graph skill to vault, fixed 5 stale doc refs, added frontmatter. All smoke tests pass: 48 skills discovered via skill_find, skill_use works with underscores. (Completed: 2026-05-02)
- [20260502-disable-md-table-formatter-plugin](./tracks/20260502-disable-md-table-formatter-plugin/spec.md): Disabled `@franlol/opencode-md-table-formatter@0.0.3` from global OpenCode plugin array. Timestamped backup created, config parsing validated, reference docs updated to 6 plugins. (Completed: 2026-05-02)
- [20260501-skill-token-optimization](./tracks/20260501-skill-token-optimization/spec.md): Completed skill token optimization migration using @zenobius/opencode-skillful; native skill prompt reduced from 53 to 5 core skills; ~93% token reduction achieved. Lazy skills remain available through skill_find/skill_use. (Completed: 2026-05-01)
- [20260501-codex-multi-auth-upgrade](./tracks/20260501-codex-multi-auth-upgrade/spec.md): Upgraded runtime from oc-chatgpt-multi-auth@5.4.4 to oc-codex-multi-auth@6.1.8 by fixing effective global config source (`opencode.jsonc`), validating plugin cache, Codex account health/tools, required models, env timeout, rollback cache preservation, and supersession note linkage. (Completed: 2026-05-01)
- [openai-parameter-fix](./tracks/openai-parameter-fix/spec.md): Fixed OpenAI SDK parameter mismatch by pinning `@ai-sdk/openai` provider and patched `oc-chatgpt-multi-auth` missing arguments on deferred tools. All 5 validation gates passed. (Completed: 2026-04-29)
- [20260429-email-calendar-mcp-audit](./tracks/20260429-email-calendar-mcp-audit/spec.md): Fix Outlook email skills tool-name mismatch, install Google Gmail/Calendar MCP server, create Outlook calendar skills, and document test plan. All 6 phases complete. (Completed: 2026-04-29)
- [20260430-google-skills](./tracks/20260430-google-skills/spec.md): Created 6 Google-side skills (gmail-inbox-triage, gmail-draft-reply, google-calendar-today, google-calendar-schedule, unified-calendar-today, google-contacts) with reference.md files. All phases complete. (Completed: 2026-04-29)
- [20260501-scheduler-headless-hardening](./tracks/20260501-scheduler-headless-hardening/spec.md): Migrated 4 OpenCode scheduled tasks to wscript/VBS headless launcher pattern, created runbook, updated scheduler skill v2.1.0. All validation passed. (Completed: 2026-05-01)

## Archived Tracks

*(None yet)*
