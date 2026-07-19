# Root Cause Analysis: NotebookLM Query Connection Failures

**Incident class:** Intermittent query-stream failure

**Date assessed:** 2026-07-14

## Executive conclusion

The reported failure was **not an account-access or missing-notebook problem**, but the first `0.8.6` validation was insufficient: it tested metadata access and one successful query, then a later identical minimal query reliably reproduced the incomplete-chunked-read failure. The upgraded profile had valid cookies, CSRF, and build metadata but **no persisted NotebookLM session ID**. The CLI's streamed query request omits its `f.sid` parameter when that stored session ID is empty; its notebook/source RPCs and `nlm login --check` still succeed without it.

The strongest local explanation is therefore an **incompletely refreshed persisted authentication profile**, inherited through the package upgrade, rather than a general loss of access. `nlm doctor auth-replay` did not detect it because its probes exercise the list-notebooks RPC and obtain a session ID from a temporary browser page; they do not verify the saved profile's session ID or the streamed query endpoint. Running `nlm login --force` re-extracted and saved a complete profile (38 cookies plus a session ID). The same one-source query then succeeded under default `httpx` transport, followed by a cited all-source query.

The incident is **not currently persistent after the forced profile refresh**. The target notebook remains accessible and the local host can retrieve source-grounded data through default transport. This does not prove the service will remain reliable under repeated or long-running use, and a future disconnect should still follow the bounded recovery procedure.

## Evidence

| Check | Result | Meaning |
|---|---|---|
| `nlm doctor` | CLI `0.6.6`; one default profile; 34 cookies; CSRF token present; saved Chrome profile available | Local installation and credential prerequisites were present. |
| `nlm login --check` | Authentication valid; four notebooks available | Rejects expired/invalid credentials as the incident cause. |
| `nlm notebook list --json` | Target notebook is available and reports 162 sources | Rejects a missing notebook, wrong account, or empty-notebook explanation. |
| `nlm source list <target> --quiet` | 162 source IDs returned | Confirms source inventory can be read through the same account/CLI. |
| Minimal query | Completed successfully | Confirms the query endpoint was reachable at assessment time. |
| Grounded query | Returned a cited answer using source `34b00daa-7ed9-45cb-a6cf-8425ac3e4472` | Confirms actual source-grounded data retrieval, not merely metadata access. |
| Reported failures | Three single-notebook queries failed after short retries with remote disconnect / incomplete chunked-read messages | Indicates a response-stream interruption rather than an auth rejection. |
| Historical local execution log | A prior C2/CC2 run completed five queries, then multiple minimal and short single-notebook retries failed with the same disconnect/EOF family | Shows the failure mode is recurrent and can begin after successful requests; it is not a deterministic inability to open this notebook. |
| Approved upgrade and post-upgrade verification | `notebooklm-mcp-cli` upgraded from `0.6.6` to `0.8.6`; both resolved `nlm.exe` locations report `0.8.6`; `doctor`, auth, JSON notebook listing, and a cited query passed | The supported current client and default transport are operational for the target notebook. |
| Exact minimal reproduction on `0.8.6` | A one-source title query failed in about 10 seconds with `peer closed connection without sending complete message body (incomplete chunked read)` | Confirms the issue was still active after upgrade and is independent of source-count workload. |
| Persisted-profile inspection | Stored CSRF and build label were present, but `session_id` was absent; 34 cookies were stored | Explains why list/source RPCs and login checks could pass while the query-specific `f.sid` parameter was omitted. |
| Forced profile refresh | `nlm login --force` re-extracted 38 cookies and persisted a session ID for the same account | Restored the local state required for the query request. |
| Post-refresh exact reproduction | The same one-source title query succeeded under default transport | Strongly supports the incomplete persisted profile as the local trigger. |
| Post-refresh grounded query | A 162-source query returned a cited answer and source passage | Confirms normal source-grounded querying is restored. |
| Scoped CDP investigation | The experimental CDP transport could not self-start because Chrome already listened on `127.0.0.1:9222`, while the transport misidentified that port as free when it lacked a valid DevTools response | CDP is not a current fallback; the default transport is fixed by profile refresh. |

## Cause analysis

### Confirmed immediate failure mode

The remote side (NotebookLM itself or an intermediary in its RPC path) closed the HTTP response stream before a complete chunked response was delivered. `httpx` surfaces this as `Server disconnected without sending a response` and `peer closed connection ... incomplete chunked read`. These are transport-protocol errors, not explicit NotebookLM authorization responses.

### Strongly supported local trigger

The saved `default` profile lacked `session_id` after upgrade. In `0.8.6`, the streamed query implementation adds `f.sid` only when that value exists, while the metadata and source RPCs can still execute using cookies, CSRF, and build metadata. The failure was reproduced with exactly one selected source, then cleared immediately after `nlm login --force` persisted the missing value. This is strong evidence that the missing persisted session state triggered this instance; it is not proof that every historical EOF was caused by the same condition.

### Likely contributing factors

1. **Incomplete persisted session state - high confidence for this reproduced incident.** The missing saved session ID, query-specific `f.sid` behavior, failed one-source request, forced refresh, and successful repeat form a direct, controlled before/after sequence.
2. **Old client against an undocumented, changing API - historical high-confidence contributor.** The host formerly ran `notebooklm-mcp-cli 0.6.6`; it now runs `0.8.6`. The upgrade did not repair inherited incomplete profile data, so upgrade validation must include a repeatable query and persisted-session check.
3. **Upstream transient capacity, throttling, or stream instability - residual medium confidence.** No upstream request ID or server telemetry is available. Historical failures may include a remote component, but the present reproduction has a verified local remediation.
4. **Large notebook / query workload - lowered confidence for this incident.** The 162-source notebook can increase response duration, but the failure reproduced with one source and the repaired default transport completed an all-source cited query.

### Ruled out

- Expired or invalid cookies or account authentication.
- Wrong Google account or inaccessible target notebook.
- A source-less notebook.
- A permanent inability for this host to retrieve notebook-grounded data.

## Risk statement

Do not set `NOTEBOOKLM_RPC_TRANSPORT=cdp` globally or by default. Upstream documents it as experimental and appropriate only when its auth-replay diagnostic shows that browser-page access succeeds while normal HTTP replay fails. The current default transport succeeds, so enabling CDP now would add browser-process complexity without evidence that it is required.

## Sources

- Local commands and results recorded in this track's plan.
- Historical execution log captured in local OpenCode session history for the C2/CC2 query run.
- Upstream release notes: [v0.8.2](https://github.com/jacob-bd/notebooklm-mcp-cli/releases/tag/v0.8.2), [v0.8.3](https://github.com/jacob-bd/notebooklm-mcp-cli/releases/tag/v0.8.3), and [v0.8.6](https://github.com/jacob-bd/notebooklm-mcp-cli/releases/tag/v0.8.6).
