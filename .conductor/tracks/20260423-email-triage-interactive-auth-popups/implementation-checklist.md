# Build Agent Execution Checklist

Track: `20260423-email-triage-interactive-auth-popups`

## Objective

Eliminate recurring Microsoft account picker popups by migrating hourly email triage auth from delegated interactive Graph login to non-interactive app auth, while preserving triage behavior.

---

## Phase 1 — Preconditions and Access

- [ ] Confirm tenant/admin access for Entra app registration and Graph admin consent.
- [ ] Confirm mailbox target: `dave.witkin@packagedagile.com` and existing folder IDs are still valid.
- [ ] Export backup of current task XML before any changes.
- [ ] Confirm rollback owner and rollback window.

**Validation commands**

- `Get-ScheduledTask -TaskPath "\OpenCode\" -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort"`
- `Export-ScheduledTask -TaskPath "\OpenCode\" -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort"`

---

## Phase 2 — App Registration + Permissions

- [ ] Inspect the existing app registration referenced by the script (`ClientId 14d82eec-204b-4c2f-b7e8-296a70dab67e`).
- [ ] Decide whether to reuse that app or create a dedicated app for email triage automation.
- [ ] Create/designate Entra application for email triage automation.
- [ ] Prefer certificate credential over client secret.
- [ ] If creating a local certificate, generate one in the appropriate Windows certificate store and record thumbprint + expiry in secure ops notes.
- [ ] Configure certificate credential (preferred) for app auth.
- [ ] Grant minimum Graph application permissions required for mailbox read/move workflow.
- [ ] Complete admin consent.
- [ ] Record app ID, tenant ID, cert thumbprint, and validity dates in secure ops notes (no secrets in repo).

**Expected permissions to validate**

- [ ] `Mail.Read` or `Mail.ReadWrite` for reading unread messages from the target mailbox/folder path.
- [ ] `Mail.ReadWrite` for move operations.

**Acceptance gate**

- [ ] App-only token acquisition works non-interactively.
- [ ] Graph calls needed by triage script are supported with granted app permissions.

---

## Phase 3 — Script Refactor (Auth + Reliability)

- [ ] Replace delegated interactive `Connect-MgGraph` usage with non-interactive app auth bootstrap.
- [ ] Remove/disable any code path that can invoke interactive UI.
- [ ] Review `Disconnect-MgGraph` usage and keep/remove it intentionally for the app-auth model.
- [ ] Add explicit failure categories in logs:
  - [ ] auth/token failure
  - [ ] permissions/consent failure
  - [ ] mailbox/folder access failure
  - [ ] message move failure
- [ ] Normalize exit codes by category for scheduler observability.
- [ ] Preserve current classification/move behavior (no logic drift unless explicitly requested).

**Acceptance gate**

- [ ] Manual local run succeeds without prompts.
- [ ] Log output identifies success/failure category deterministically.

---

## Phase 4 — Scheduled Task Hardening

- [ ] Keep hidden execution (`-WindowStyle Hidden`).
- [ ] Confirm principal/logon configuration is compatible with unattended runs.
- [ ] Ensure task action does not depend on interactive session state.
- [ ] Verify retry and multiple-instance behavior remains safe.

**Validation commands**

- `Get-ScheduledTask -TaskPath "\OpenCode\" -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Select-Object -ExpandProperty Principal`
- `Get-ScheduledTaskInfo -TaskPath "\OpenCode\" -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort"`

---

## Phase 5 — Verification Window

- [ ] Run controlled manual invocation once.
- [ ] Clear or invalidate prior delegated/MSAL auth artifacts as needed before validation.
- [ ] Observe **3 consecutive hourly scheduled runs**.
- [ ] Include at least one run while the user session is locked or otherwise unavailable for interactive sign-in.
- [ ] Confirm no Windows Terminal popup.
- [ ] Confirm no Microsoft account picker popup.
- [ ] Confirm `LastTaskResult` indicates success.
- [ ] Spot-check moved emails for expected routing behavior.

**Validation commands**

- `Get-ScheduledTaskInfo -TaskPath "\OpenCode\" -TaskName "opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort" | Select-Object LastRunTime,NextRunTime,LastTaskResult`
- Review latest files under: `C:\development\email-triage\logs\`

---

## Phase 6 — Documentation + Closeout

- [ ] Update runbook with setup, cert rotation, diagnostics, and incident response.
- [ ] Document rollback steps to prior auth mode.
- [ ] Update conductor artifacts (`plan.md`, `metadata.json`) with completion details.
- [ ] Capture residual risks and owners.

---

## Rollback Plan (if failures occur)

- [ ] Restore previous scheduled task XML/action.
- [ ] Revert script auth block to prior known-good behavior.
- [ ] Re-run one manual and one scheduled test.
- [ ] Communicate temporary known limitation: interactive auth may reintroduce popups.

---

## Final Done Criteria

- [ ] Zero popup incidents in verification window.
- [ ] Triage continues operating successfully.
- [ ] Non-interactive auth is in place and documented.
- [ ] Conductor track updated and ready for closure.
