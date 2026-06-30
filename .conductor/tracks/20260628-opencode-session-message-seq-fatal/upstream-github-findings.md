# Upstream GitHub Findings - session_message.seq NOT NULL constraint

Research performed 2026-06-28 against `anomalyco/opencode` (fork; tracks `sst/opencode` releases in sync). Latest release at time of research: **v1.17.11** (2026-06-25).

## The fix (confirmed present in upstream, absent in 1.15.10)

- **Commit:** [`8bc501b`](https://github.com/anomalyco/opencode/commit/8bc501b5358128b10db2e34e380c62a41c90d702) - `fix(core): guard against null event.seq when inserting session_messages` (2026-06-08).
- **Change:** all `event.seq === undefined` checks -> `event.seq == null` (catches both `null` and `undefined`).
- **Files:** `packages/core/src/session.ts`, `packages/core/src/session/input.ts`, `packages/core/src/session/projector.ts` (+8/-8), `packages/opencode/src/event-v2-bridge.ts`. Related PR **#31419** (@Cain-Brouwer).
- **Quote:** "The NOT NULL constraint on session_message.seq could be violated when event.seq is null instead of undefined... This occurred during session.next.agent.switched handling, preventing the build agent from responding after switching from plan mode."
- Verified via `gh api repos/anomalyco/opencode/commits/8bc501b...` => message + date confirmed.

## Issue cluster (all same root cause / stack)

| Issue | Title | Trigger | State |
| --- | --- | --- | --- |
| [#31204](https://github.com/anomalyco/opencode/issues/31204) | session_message.seq NOT NULL on agent-switched sessions | `session.next.agent.switched` | canonical report |
| [#31412](https://github.com/anomalyco/opencode/issues/31412) | `opencode run` + HTTP POST fail with seq NOT NULL (1.15.13) | new-row insert path | dup of 31204 |
| [#31413](https://github.com/anomalyco/opencode/issues/31413) | `opencode run` + HTTP POST fail with seq NOT NULL (1.15.13) | new-row insert path | closed dup of 31204 |
| [#31606](https://github.com/anomalyco/opencode/issues/31606) | Switching model mid-session -> seq NOT NULL | `session.next.model.switched` | open (assigned StarpTech) |
| [#31072](https://github.com/anomalyco/opencode/issues/31072) | Subagent seq race in commitSyncEvent | concurrent seq assignment | related (masked UNIQUE) |

## Canonical stack (matches this machine's log exactly)
```
SQLiteError: NOT NULL constraint failed: session_message.seq
  at run (unknown)
  at #run (bun:sqlite:185:20)
  at appendMessage
  at session.next.agent.switched   <- trigger
  at SessionPrompt.createUserMessage
  at SessionPrompt.prompt
  at SessionHttpApi.prompt
```

## Schema (from issue #31412/#31413 + sst/opencode `session.sql.ts`)
```sql
CREATE TABLE session_message (
  id text PRIMARY KEY,
  session_id text NOT NULL,
  type text NOT NULL,
  time_created integer NOT NULL,
  time_updated integer NOT NULL,
  data text NOT NULL,
  seq integer NOT NULL           -- <-- failing column, NO DEFAULT
);
CREATE UNIQUE INDEX session_message_session_seq_idx
  ON session_message (session_id, seq);
```
Note: on `dev`, later refactors **remove** the `seq` column from `SessionMessageTable` entirely, so the column is transitional. Confirmed locally: this DB has the column + the unique index.

## Workarounds confirmed by community (consistent)
1. **Upgrade** to a fixed release: `opencode upgrade v1.17` (multiple confirmations in #31204). This is the recommended fix.
2. Use the canonical newer binary path; no DB migration/wipe needed (newer runtime honors the migrated schema).
3. **Model-switch variant (#31606):** start a new session after switching models (workaround until upgrade).
4. **Nuclear (only if DB actually corrupt):** delete `opencode.db` -> loses sessions. **NOT applicable here** (our `integrity_check` = ok, source-of-truth intact).

## Distinct scenario we EXCLUDED
- **Issue #30963** - migration `20260604172448` wiped `session_message`/`event` tables, making `MAX(seq)+1 = NULL`. Excluded here because our `event` table has 21,416 rows and `session_message` has 62 valid rows (0 NULL seq); the wipe did not happen on this DB.

## DCP plugin (secondary) - npm facts
- `@anthropic-ai/tokenizer`: latest **0.0.4**, last modified 2026-06-04 (still installable; not deleted from registry).
- `@tarquinen/opencode-dcp`: latest **3.1.14** (2026-06-25), beta **3.2.8-beta0**. User cache pinned at 3.1.13.
- Plugin cache `package.json` is malformed (self-referential dep, version `None`), and `@anthropic-ai/tokenizer` is absent from its `node_modules` -> direct cause of the load failure.
