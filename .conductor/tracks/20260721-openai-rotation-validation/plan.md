# Plan: OpenAI Multi-Account Rotation Remediation and Validation

## Status

- **State:** manual-rotation-validated-auto-failover-deferred
- **Progress:** 16/17 complete; 1/17 explicitly deferred
- **Track type:** maintenance / operational validation
- **Safety boundary:** no token disclosure, no manufactured quota exhaustion, no forbidden global `opencode.json`

## Phase 0 - Baseline and Documentation

- [x] **0.1 Reconstruct the incident and current state.** Review recent session history, troubleshooting documentation, runtime logs, pool metadata, lock state, and package versions without exposing secrets.
- [x] **0.2 Define pass/fail evidence.** Separate current connectivity, manual pool routing, and automatic 429 failover into distinct claims.
- [x] **0.3 Create this lightweight Conductor track and upsert both ledgers.** Record scope, safety rules, rollback, and conditional automatic-failover handling.

## Phase 1 - Preserve and Refresh

- [x] **1.1 Create restricted backups.** Back up canonical `opencode.jsonc`, the existing account pool, and plugin-cache metadata; verify backup existence without printing secret content.
- [x] **1.2 Validate baseline configuration.** Confirm JSONC resolution with `opencode debug config`, confirm no forbidden global `opencode.json`, and record redacted package/pool scope state.
- [x] **1.3 Refresh only the plugin runtime cache.** Resolve reviewed npm v6.10.0 without invoking the default installer and without modifying unrelated packages.
- [x] **1.4 Verify fresh-process plugin loading.** Confirm resolved package version and expected `codex-*` status/health/list/limits/switch surface.

## Phase 2 - Normalize Pool Scope

- [x] **2.1 Verify the supported storage mechanism.** Inspect v6.10.0 documentation/source for global versus per-project behavior and migration support.
- [x] **2.2 Select and document one intentional scope.** Prefer a global pool with per-project storage disabled when safely supported; otherwise import into explicitly required project scopes.
- [x] **2.3 Migrate with rollback protection.** Use a supported command or carefully bounded file migration; preserve ACLs and never emit account content.
- [x] **2.4 Verify pool visibility.** Confirm the intended account count and redacted active index from the current repo and a fresh child/subagent path.

## Phase 3 - Prove Rotation

- [x] **3.1 Run manual-switch proof.** Record redacted active state, switch to a different known-healthy account, and verify the changed redacted state.
- [x] **3.2 Run timestamped fresh-process probes.** Execute one tiny Sol probe and one tiny Luna/subagent-path probe; require normal completion with no repeated usage-limit loop.
- [ ] **3.3 Run conditional automatic-failover proof. — DEFERRED.** `codex-limits` found no naturally limited or cooldown account. No quota was burned and no credential was corrupted; automatic 429 failover remains unclaimed until a natural event.
- [x] **3.4 Check post-test hygiene.** Inspect redacted state changes, bounded log windows, child-process exit, and all account-pool scopes for orphan locks.

## Phase 4 - Closeout

- [x] **4.1 Record evidence and rollback status.** Create a dated execution log containing commands, redacted outcomes, deviations, and any deferred claim.
- [x] **4.2 Synchronize Conductor artifacts.** Update this plan, metadata, `tracks.md`, and `tracks-ledger.md`; do not claim complete unless every non-deferred acceptance criterion passes.

## Verification Commands

```powershell
opencode debug config
npm view oc-codex-multi-auth version
opencode run <tiny timestamped probe> --model openai/gpt-5.6-sol --variant low
# Luna probe uses the configured Luna/subagent route discovered at execution time.
# Lock scan and log inspection must print paths/counts/status only, never account content.
```

## Completion Rule

The track may close as `validated` when manual switching and cross-process probes pass and all non-conditional criteria are met. If no naturally limited account exists, task 3.3 is marked deferred and the final status must explicitly say `manual-rotation-validated-auto-failover-deferred` rather than implying automatic 429 failover was tested.
