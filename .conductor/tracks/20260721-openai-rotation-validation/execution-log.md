# Execution Log: OpenAI Multi-Account Rotation Validation

**Date:** 2026-07-21  
**Outcome:** `manual-rotation-validated-auto-failover-deferred`

## Safety and rollback

- Never printed OAuth tokens, account identifiers, or unmasked emails.
- Did not manufacture a 429, burn quota, corrupt credentials, run the default installer, create forbidden global `opencode.json`, commit, or push.
- Created restricted, hash-verified rollback assets under the user OpenCode backup directory. Secret-bearing backup contents are intentionally omitted here.

## Baseline and remediation

1. Reconstructed the July 20 failure from session history, logs, and the troubleshooting guide. The prior runtime repeatedly retried one quota-limited account while dead-PID lock files prevented reliable health-state updates.
2. Found the active plugin cache at v6.3.4 and a corrupt stale `oc-codex-multi-auth@latest` wrapper at v6.7.1. Direct import of the stale wrapper failed on a missing dependency.
3. Preserved rollback artifacts, removed the corrupt cache wrapper, and let a fresh OpenCode process install reviewed npm v6.10.0.
4. Verified all 24 `codex-*` tools are exposed in a fresh Build-agent registry.
5. Migrated the four-account pool to global storage with a hash-matched copy and restricted ACLs. The original project pool remains as a rollback source.
6. Added `C:\Users\DaveWitkin\.opencode\openai-codex-auth-config.json` with `perProjectAccounts: false`. A temporary OpenCode plugin tuple was reverted after source/runtime evidence showed v6.10.0 reads its own plugin config file or environment variable rather than tuple options.

## Redacted validation evidence

- Global visibility: 4 accounts total, 3 enabled, 1 disabled; no identifiers emitted.
- Manual switch: invoked the shipped `codex-switch` implementation directly with target account 3. Stored active index changed from zero-based 0 to zero-based 2.
- Sol fresh-process probe: exit 0, expected exact response received, stored active index remained zero-based 2.
- Luna fresh-process probe: exit 0, expected exact response received, stored active index remained zero-based 2.
- Cross-process lock recovery: the Luna process successfully took over the dead-PID advisory lock left by the preceding Sol process. This confirms v6.10.0 no longer strands the pool behind that dead owner.
- Manual restoration: invoked the same shipped switch implementation for account 1. Stored active index returned to zero-based 0, matching the pre-test state.
- Bounded probe log scan: 0 usage-limit/API/error matches during the test window.
- Final hygiene: 0 account-pool lock files, canonical config validates, npm latest is 6.10.0, and forbidden global `opencode.json` is absent.

## Automatic failover disposition

`codex-limits` reported no enabled account in a natural rate-limit or cooldown state. Per the safety boundary, no quota was consumed deliberately and no token was corrupted to manufacture failure. Automatic 429 failover is therefore **deferred**, not claimed as tested. The safe future test is to repeat one tiny request when an account is naturally limited and require one final success, a changed active state, and `lastSwitchReason=rate-limit` without a repeated retry loop.

## Lock behavior and residual risk

v6.10.0 uses an advisory JSON sidecar lock. Short-lived `opencode run` processes can leave a dead-PID sidecar because asynchronous `beforeExit` cleanup is not reliably awaited by the host/runtime. Unlike the older failure mode, the next v6.10.0 process detects the dead same-host PID, takes over immediately, and proceeds; this was observed directly. Final state was cleaned to zero lock files. Long-lived desktop operation should still be monitored at the next real quota event.

## Deviations

- Used direct invocation of the shipped `codex-switch` tool implementation for deterministic proof. Calling `codex-switch` through a model turn caused the model's follow-up request to persist the already-loaded account manager state and overwrite the switch, so it was unsuitable as an isolated switch test.
- Automatic failover was deferred because no account was naturally limited.
- No commit or push was performed because none was requested.
## Documentation follow-up

On 2026-07-21, the canonical troubleshooting guide at `docs/troubleshooting/active/openai-rotation-oc-codex-orphan-locks.md` was upgraded to version 2.0. It now documents all three observed failure modes (older dead-PID locks, corrupt/stale cache wrappers, and pool-scope fragmentation), the safe v6.10.0/global-pool remediation, deterministic manual-switch testing, fresh Sol/Luna probes, v6.10.0 advisory-lock takeover behavior, and the explicit deferral criteria for automatic 429 failover.

An independent peer review then passed after hardening foreign-host lock handling, suppressing merged config output, replacing raw `codex-list` JSON with local aggregate projection, and eliminating the manual lock-deletion race by requiring a stopped-process maintenance window plus immediate owner revalidation.
