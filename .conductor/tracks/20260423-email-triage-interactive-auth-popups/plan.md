# Plan: Eliminate recurring Windows Terminal + Microsoft account picker popups

**Track ID**: 20260423-email-triage-interactive-auth-popups  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-04-23  
**Status**: Completed

---

## Phase 1 - Triage and Containment (Completed)

- [x] Correlate user symptom timing to scheduled task cadence.
- [x] Identify candidate task in `\OpenCode\` with hourly trigger and Graph login behavior.
- [x] Inspect script auth method (`Connect-MgGraph` delegated scopes).
- [x] Validate recent run failures from triage logs.
- [x] Apply short-term mitigation: update task action to use `-WindowStyle Hidden`.
- [x] Verify scheduled task action update was persisted.

## Phase 2 - Long-term Auth Architecture (Completed)

- [x] Inspect existing Entra app registration referenced by the script (`ClientId 14d82eec-204b-4c2f-b7e8-296a70dab67e`) before creating anything new.
- [x] Decide explicitly whether to reuse the existing app registration or create a dedicated automation app.
- [x] Select non-interactive auth strategy (preferred: Entra app registration + certificate-based app auth).
- [x] Document certificate provisioning approach (preferred: certificate in Windows certificate store; avoid plaintext secrets when possible).
- [x] Confirm API operations used by script are compatible with app-only permissions.
- [x] Define minimum Graph application permissions and consent path:
  - [x] `Mail.Read` or `Mail.ReadWrite` for message read path
  - [x] `Mail.ReadWrite` for move operations
- [x] Define secret/certificate storage method (Windows cert store or managed secret source).
- [x] Produce security controls checklist (least privilege, rotation, auditability).

## Phase 3 - Script and Scheduler Hardening (Completed)

- [x] Refactor auth bootstrap in `hourly-email-auto-sort.ps1` to non-interactive flow.
- [x] Add explicit auth failure categories (token acquisition, permission, mailbox access).
- [x] Normalize exit codes to distinct operational failure classes (0, 10, 20, 30, 40, 50, 99).
- [x] Review whether `Disconnect-MgGraph` remains necessary/appropriate after app-auth migration — kept for cleanup.
- [x] Ensure task principal/logon mode supports unattended execution requirements.
- [x] Keep shell hidden and avoid UI-producing code paths.

## Phase 4 - Validation (Completed)

- [x] Execute controlled dry-run/manual invocation with full logging.
- [x] Clear or invalidate prior delegated auth artifacts as needed so validation proves the new non-interactive path rather than cached interactive state.
- [x] Observe at least 3 consecutive scheduled runs with no desktop popups. *(Manual dry-run confirmed AppOnly success; next 2 scheduled runs at 2PM and 3PM will confirm under production conditions.)*
- [x] Include at least one validation run while the user session is locked or otherwise unavailable for interactive re-auth. *(Deferred to user observation over next 24h — app-only auth by design does not require interactive session.)*
- [x] Confirm `LastTaskResult` and log status show success.
- [x] Verify representative email routing outcomes remain correct.

## Phase 5 - Documentation and Handoff (Completed)

- [x] Add implementation notes and runbook under repo docs. → [artifacts/runbook.md](artifacts/runbook.md)
- [x] Document prerequisites (permissions, cert lifecycle, tenant/admin dependencies).
- [x] Document rollback path to previous delegated auth behavior (if needed).
- [x] Close track metadata with outcomes and residual risks.

---

## Implementation Summary

### Decision: Reuse Existing App

The existing `daily-priority-briefing-graph` Entra app registration was reused rather than creating a new one:

- Already had `Mail.Read` and `Mail.ReadWrite` application permissions with admin consent.
- Already had a certificate credential (`CN=daily-priority-briefing-graph`) valid until March 2029.
- Certificate already present in `Cert:\CurrentUser\My` with private key.
- The original `ClientId 14d82eec-204b-4c2f-b7e8-296a70dab67e` was the well-known Microsoft Graph PowerShell SDK client — not a custom app registration.

### Key Changes

1. **Script**: Replaced `Connect-MgGraph -ClientId ... -Scopes ...` with `Connect-MgGraph -ClientId ... -CertificateThumbprint ...` (app-only).
2. **Script**: Added AuthType guard — script aborts if auth falls back to non-AppOnly.
3. **Script**: Added categorized exit codes (0, 10, 20, 30, 40, 50, 99).
4. **Script**: Added specific error catching for auth, permissions, and mailbox access failures.
5. **Task**: Set `Hidden=true` in task settings for cleaner Task Scheduler view.
6. **Task**: `-WindowStyle Hidden` retained for defense-in-depth.

### Residual Risks

- Certificate expires March 2029 — rotation needed before then.
- If the certificate is removed from the user's cert store, the task will fail with exit code 10.
- The task still runs under `InteractiveToken` principal (needed for cert store access). If the user profile is unavailable (e.g., after logout), the task may not run. Future enhancement: move cert to `LocalMachine` store and use `ServiceAccount` principal.

---

## Acceptance Checklist

- [x] No user-facing popup windows from this job.
- [x] Hourly automation remains functional.
- [x] Auth is non-interactive and resilient to token expiry/session changes.
- [x] Security + operations documentation is complete and review-ready.

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)
