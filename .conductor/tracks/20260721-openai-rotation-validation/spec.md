# OpenAI Multi-Account Rotation Remediation and Validation

## Objective

Restore and prove reliable `oc-codex-multi-auth` account rotation across fresh OpenCode processes and subagent/model paths, with redacted evidence, reversible changes, and no deliberate quota exhaustion or token corruption.

## Background

The 2026-07-20 incident involved dead-PID `proper-lockfile` locks that prevented account-health updates and caused repeated usage-limit retries against one account. Lock cleanup restored current connectivity but did not prove rotation. Follow-up inspection on 2026-07-21 found a stale v6.3.4 runtime cache versus npm v6.10.0, no plugin `codex-*` tool surface in a fresh child process, and a four-entry OAuth pool stored only under one project key while the current repository and global scope have no pool.

## Scope

### In Scope

- Preserve the canonical global config at `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`; never create or retain global `opencode.json`.
- Back up the JSONC config and existing secret-bearing account pool to a restricted local backup location.
- Refresh only the `oc-codex-multi-auth` runtime cache to the verified current package version.
- Verify plugin load and the expected `codex-status`, `codex-list`, `codex-health`, `codex-limits`, and `codex-switch` surface in fresh processes.
- Determine the supported v6.10.0 storage-scope mechanism and normalize the pool so intended repositories/subagents use one predictable account set.
- Prove manual account selection with redacted before/after state and timestamped tiny Sol and Luna probes.
- Conditionally prove automatic rate-limit failover only when an account is already naturally limited.
- Inspect logs, state timestamps, and lock artifacts after each test.
- Document exact rollback and final/blocked evidence.

### Out of Scope

- Printing, copying into repository files, or committing OAuth tokens, account IDs, emails, or secret values.
- Deliberately consuming quota to manufacture a 429.
- Corrupting tokens, editing account health fields by hand, or fabricating cooldown state.
- Modifying Gemini proxy or Antigravity configuration.
- Running an upstream installer that writes forbidden global `opencode.json`.
- Committing or pushing without a separate explicit request.

## Safety and Stop Rules

1. Stop before migration if v6.10.0 storage behavior differs from the documented assumptions or requires unsupported hand-editing of OAuth state.
2. Stop if the canonical JSONC cannot be backed up and parsed before cache changes.
3. Stop if refreshing the plugin would alter unrelated cached packages.
4. Never expose secret-bearing file content in logs, track artifacts, shell output, or chat.
5. Do not treat a successful request alone as rotation proof.
6. Do not run an automatic-failover test unless `codex-limits` or equivalent redacted state identifies a naturally limited account.
7. Preserve all rollback material until validation is complete.

## Acceptance Criteria

1. Canonical `opencode.jsonc` remains valid and no global `opencode.json` exists.
2. A fresh runtime resolves `oc-codex-multi-auth` v6.10.0 (or a later version explicitly re-reviewed before use).
3. Expected plugin status/health/list/limits/switch capabilities are available from the intended runtime context.
4. One intentional account-pool scope is documented and visible to the current repo plus a fresh child/subagent path.
5. Manual switch changes the redacted active account/index and both tiny Sol and Luna probes succeed in fresh processes.
6. If a naturally limited account exists, one tiny request fails over once to a healthy account, records a rate-limit switch reason, and does not enter an endless retry loop; otherwise this criterion is explicitly deferred, not claimed passed.
7. No orphaned account-pool lock remains after child processes exit.
8. Rollback instructions and dated redacted evidence are recorded in the execution log.
9. Conductor plan, metadata, and both ledgers agree on final status.

## Rollback

- Restore the pre-change plugin cache from its isolated backup or remove the refreshed package cache and allow the previously recorded version to resolve.
- Restore `opencode.jsonc` from its validated backup if it changed.
- Restore the original account-pool file and storage-scope setting from restricted backups if pool normalization fails.
- Restart OpenCode after any rollback because plugin/config state is loaded at process startup.

## Execution Model

This is a lightweight Conductor maintenance track executed directly by the Build agent. A full code-oriented Conductor pipeline is not required because the work is an operational configuration/cache repair rather than product-source implementation. Durable spec, plan, rollback, evidence, and ledger synchronization remain mandatory.
