# Research Notes — 2026-07-14

## Finding

The reported pattern is strongly consistent with a known OpenCode **runtime/schema version skew**, not a MiniMax-specific failure:

1. The local CLI reports **1.15.10**.
2. Listing sessions works, which exercises a read path; a new run must also write session/message projection rows.
3. Upstream reports show 1.15.x runtimes failing during the first prompt with `NOT NULL constraint failed: session_message.seq` when a newer process has migrated the shared database.
4. The upstream fix is commit `8bc501b` (`fix(core): guard against null event.seq when inserting session_messages`), dated 2026-06-08.

This is a hypothesis until the exact local error is captured. It is sufficiently strong to make **backup + canonical runtime upgrade** the safe primary remediation, ahead of database deletion or schema changes.

## Headless-server assessment

The official CLI page recommends this supported pattern to avoid repeated cold starts:

```text
opencode serve
opencode run --attach http://localhost:4096 "<prompt>"
```

The server API creates sessions with `POST /session` and sends prompts with `POST /session/:id/message`. Therefore it does **not inherently bypass** a broken session/message database writer. It should be adopted after the compatibility fix as a performance/operational improvement, and tested as an independent path.

## Sources

- OpenCode CLI: https://opencode.ai/docs/cli/#run
- OpenCode Server API: https://opencode.ai/docs/server/
- OpenCode troubleshooting: https://opencode.ai/docs/troubleshooting/
- Upstream issue #31413: https://github.com/anomalyco/opencode/issues/31413
- Upstream issue #31204: https://github.com/anomalyco/opencode/issues/31204
- Open related issue #31606: https://github.com/anomalyco/opencode/issues/31606
- Open related issue #35116: https://github.com/anomalyco/opencode/issues/35116
- Open related Windows/headless issue #28407: https://github.com/anomalyco/opencode/issues/28407
- Fix commit 8bc501b: https://github.com/anomalyco/opencode/commit/8bc501b5358128b10db2e34e380c62a41c90d702

## Research limitation

The required Perplexity skill was loaded and its setup check passed, but its actual query failed with a LiteLLM/Perplexity connection error. Official OpenCode documentation was fetched directly and GitHub CLI searches/details were used as the specified fallback.
