# Remediation Plan: NotebookLM Query Connection Failures

**Current phase:** Query-path cause reproduced and remediated; production-batch hardening remains pending.

## 0. Future-reference documentation

- [x] Record the RCA in `rca.md` with evidence, causal confidence, upgrade gate, and CDP guardrail.
- [x] Add the reusable recovery runbook to `C:\Users\DaveWitkin\.opencode-lazy-vault\notebooklm-cli\references\connection-recovery.md`.
- [x] Link the runbook from the authoritative `notebooklm-cli` skill's Windows reliability and advanced-reference sections.

## 1. Baseline and upgrade gate

- [x] Record the pre-change state: `nlm 0.6.6`, valid authentication, target notebook access, 162 sources, and a successful grounded query.
- [x] Obtain approval to modify the globally installed Python package.
- [x] Upgrade with `python -m pip install --user --upgrade "notebooklm-mcp-cli==0.8.6"`.
- [x] Verify executable resolution and version: both resolved `nlm.exe` locations report `0.8.6`; `nlm doctor` passes installation and authentication checks.
- [x] Verify `nlm login --check`, `nlm notebook list --json`, and one minimal grounded query against the C2/CC2 notebook.
- [ ] If the upgrade breaks authentication or normal querying, stop; record the exact result; reinstall the previously recorded version `0.6.6` only with approval.

**Initial validation recorded 2026-07-14:** `nlm login --check` authenticated `dave.witkin@scruminc.com`; the JSON listing returned the target notebook with 162 sources; a cited query succeeded. That result was not sufficient to declare remediation: a later exact one-source query failed with incomplete chunked read.

**Reproduction and repair recorded 2026-07-14:** The persisted profile had CSRF/build metadata but no session ID. The one-source query then failed, while `nlm doctor auth-replay` still reported `httpx_ok` because it tests list-notebooks rather than the streamed query. `nlm login --force` refreshed the same account's profile with 38 cookies and a persisted session ID. The exact one-source query and a cited 162-source query then both passed under default transport.

**Exit gate:** Passed after the forced profile refresh. The upgraded default transport passed the repeatable query checks; batch work remains subject to the hardening controls below.

## 2. Diagnose a future failure before retrying work

- [ ] On the first disconnect/EOF, preserve the command, UTC time, installed version, notebook ID, prompt length (not sensitive prompt text), exit code, and complete stderr.
- [ ] Check whether the active profile has a persisted session ID without exposing it: `python -c "from notebooklm_tools.core.auth import AuthManager; p=AuthManager('default').load_profile(); print(bool(p.session_id))"`.
- [ ] If the session ID is absent, verify the active account and run `nlm login --force`; ordinary `nlm login` returns early when list-notebooks validation passes and will not repair this state.
- [ ] Do not run parallel queries. Run `nlm doctor`, `nlm login --check`, notebook list, and one small grounded single-notebook smoke query.
- [ ] On `0.8.6`, run `nlm doctor auth-replay` and use its result to classify the failure:
  - `stale_cookies` or equivalent: run interactive `nlm login`, then repeat the smoke query.
  - normal HTTP replay succeeds: retain default transport and treat the original event as transient/remote.
  - browser/in-page replay succeeds while normal HTTP replay fails: continue to the scoped CDP trial below.
  - both lanes fail: stop retries; treat as upstream outage or broader network failure and use the web UI fallback.

## 3. Scoped CDP transport trial (conditional only)

- [ ] Only after the exact diagnostic gate above, run a new PowerShell process with `$env:NOTEBOOKLM_RPC_TRANSPORT = 'cdp'` and one small grounded query.
- [ ] Before a CDP trial, verify that `127.0.0.1:9222` is not occupied by a non-DevTools listener. Current `0.8.6` CDP transport can choose that occupied port because it tests only for a valid DevTools response, then fail to self-start.
- [ ] Confirm that the response has a non-empty answer and source citation before using CDP for any real workload.
- [ ] Keep the setting process-scoped; do not write it into user, system, OpenCode, or repository configuration.
- [ ] If CDP is slower, unstable, or fails, discard that process-scoped setting and use the web UI fallback; capture evidence for an upstream issue.

## 4. Harden the query workflow

- [ ] Build or update the query runner to serialize requests, place a preflight smoke query before a batch, and record a manifest for every attempt.
- [ ] Replace blind 15–20 second retries with a bounded circuit breaker: after a disconnect, retry the smoke query at approximately 30 seconds, 90 seconds, then 300 seconds; stop after three transport failures.
- [ ] Split wide cross-notebook synthesis into concise single-notebook queries before attempting cross-notebook aggregation.
- [ ] Use explicit query timeouts appropriate to expected workload, but do not treat a larger client timeout as a fix for a server-terminated stream.
- [ ] Preserve partial outputs and mark missing responses as blocked; never silently substitute an uncited synthesis.

## 5. Fallback and escalation

- [ ] If the circuit breaker trips, run the remaining approved questions in the NotebookLM web UI and preserve the answer/citations as a manual fallback.
- [ ] Open an upstream issue only with sanitized diagnostics: version, operating system, timestamp/time zone, command shape, retry count, error family, and whether auth-replay lanes passed. Exclude cookies, CSRF values, notebook contents, and sensitive source titles.
- [ ] Reassess after one approved production batch. Define success as zero unhandled stream failures, every output having a manifest row, and every successful factual answer containing a source citation.

## Validation matrix

| Scenario | Required result |
|---|---|
| Normal default transport | Valid auth, notebook list, and cited small query succeed. |
| Normal batch | Requests are serial, all attempts are logged, and partial data is retained. |
| Expired cookies | Diagnostic identifies the condition; re-login restores the smoke query. |
| Browser-bound replay only | CDP trial is explicitly justified, scoped, and independently smoke-tested. |
| Repeated EOF/disconnect | Circuit breaker stops automation and uses the manual web UI fallback. |
