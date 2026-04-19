# Plan: Switch to Multi-Account Codex OAuth Plugin

**Track ID**: 20260314-codex-multi-auth-setup  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-03-14  
**Status**: In Progress

---

## Phase 1: Preflight and Backup

- [x] Export current OpenCode config backup from `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- [x] Capture current auth plugin state and OpenCode version (`opencode --version`, `opencode debug config`).
- [x] Decide package/version policy:
  - Preferred: `oc-chatgpt-multi-auth@5.4.4` (pinned)
  - Alternative: `oc-chatgpt-multi-auth@latest`
- [x] Run dependency compatibility check for pinned plugin (`npm view oc-chatgpt-multi-auth@5.4.4 peerDependencies dependencies`) and record result in track notes.

## Phase 2: Configuration Change

- [x] Replace plugin entry `opencode-openai-codex-auth@4.2.0` with `oc-chatgpt-multi-auth@5.4.4`.
- [x] Preserve all existing plugin neighbors and ordering except required compatibility ordering.
- [x] Keep all existing provider/model blocks unless plugin-specific compatibility issue is observed.
- [ ] Add account-priority defaults (primary/secondary ordering) after second account enrollment and document exact command/state used.
- [x] Define rollback trigger thresholds before cutover (for example: plugin load failure, missing tools, repeated auth failure).

## Phase 3: Runtime Validation

- [x] Run `opencode debug config` and confirm resolved multi-auth plugin entry.
- [ ] Restart OpenCode session to ensure plugin lifecycle hooks initialize cleanly.
- [ ] Validate plugin tool surface from inside an active OpenCode session (for example: `codex-list`, `codex-help`, `codex-status`).
- [ ] Validate no dependency/runtime conflicts are introduced in the active OpenCode environment.

Notes:
- Direct shell invocations of `codex-*` returned `command not found` in this environment.
- Package docs indicate `codex-*` are OpenCode in-app tools; validate inside session after OAuth enrollment.

## Phase 4: OAuth Enrollment (Operator + Agent Split)

- [x] Agent prepares exact command sequence and expected prompts.
- [ ] Operator completes first `opencode auth login` browser flow.
- [ ] Operator completes second `opencode auth login` browser flow (add second account).
- [ ] Agent verifies account presence via plugin tooling and records evidence.
- [ ] Execute quick concurrency check: two concurrent OpenCode sessions can both read consistent auth/account state.

## Phase 5: Rotation and Recovery Testing

- [ ] Verify manual switch works (`codex-switch`) and active account changes as expected.
- [ ] Verify status/health view (`codex-status` and `codex-health`) before and after switching.
- [ ] Execute explicit recovery tests:
  - Token refresh path (`codex-refresh`) after simulated stale-auth scenario.
  - Primary account degraded scenario (for example 429/403) with fallback to secondary account.
  - Re-login recovery (`opencode auth login`) for one account without destroying healthy sibling account.
- [ ] Record expected/actual output snapshots for each test in artifacts.

## Phase 6: Handover

- [x] Produce concise operator runbook with daily commands, troubleshooting, and rollback procedure.
- [ ] Record any deltas from expected plugin behavior.
- [ ] Add post-handover monitoring checklist (24-48h): health checks, account drift, failed auto-switch events.
- [ ] Mark track complete once two-account validation is successful and monitoring checklist is accepted.
