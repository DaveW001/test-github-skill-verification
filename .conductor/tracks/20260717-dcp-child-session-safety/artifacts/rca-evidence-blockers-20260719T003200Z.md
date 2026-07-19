# RCA Evidence Blocker - Task 0.1

**Track:** 20260717-dcp-child-session-safety  
**Read-only URI:** `file:C:/Users/DaveWitkin/.local/share/opencode/opencode.db?mode=ro`  
**Generated:** 2026-07-19T00:32:00.813903Z

## Required aggregates cannot be computed without selecting content columns

The plan acceptance requires `audited_child_sessions==200`, `children_over_150k==22`, `child_compress_calls==0`. The no-content rule (Global Execution Rule #4) forbids selecting prompt/part/message-body/tool-payload columns.

## Schema discovered (`SELECT name FROM sqlite_master WHERE type='table'`)

```
__drizzle_migrations, account, account_state, control_account, credential, data_migration, event, event_sequence, message, migration, part, permission, project, project_directory, session, session_context_epoch, session_input, session_message, session_share, sqlite_sequence, todo, workspace
```

## Safe aggregates actually computed (read-only, no content)

- sessions_total: 2888
- child_sessions_parent_id_not_null: 843
- task_child_sessions_title_pattern: 843
- permission_rows: 0
- child cumulative token buckets: {"cumulative_1_to_150k": 253, "cumulative_over_150k": 571, "zero": 19}
- dcp_state_file_count: 639 (json: 639)

## Why each required aggregate is unresolvable content-free

- **audited_child_sessions**: Stage-1 RCA methodology (sampled audit of 200); not a DB-derived count. parent_id IS NOT NULL = 843, task-child title pattern = 843; neither yields 200.
- **children_over_150k**: Requires live context-window size; session.tokens_* are cumulative lifetime totals (cumulative>150000 = 571 children, not 22). Live size needs message/part `data` content.
- **child_compress_calls**: Compress tool calls are stored only in part/message `data` (content) columns; no metadata count exists.

## Conclusion

Task 0.1 acceptance gate (`assert audited_child_sessions==200 and children_over_150k==22 and child_compress_calls==0`) cannot pass honestly without violating the no-content rule. Task 0.1 left unchecked. Honest evidence written to rca-evidence.json with status BLOCKED.
