# Spec: Eliminate recurring Windows Terminal + Microsoft account picker popups from hourly email triage automation

## Goal

Stop disruptive desktop popups caused by the hourly email triage scheduled task while preserving reliable email-sorting automation, then migrate to a fully non-interactive authentication model suitable for unattended execution.

## Problem Statement

The user observes recurring popups approximately every 1-2 hours:

1. A visible Windows Terminal/PowerShell window appears.
2. A Microsoft "Pick an account" sign-in dialog appears.

This behavior indicates an interactive authentication flow is being invoked by background automation.

## Environment and Evidence

- Host: Windows (user session)
- Scheduler namespace: `\OpenCode\`
- Candidate task identified:
  - `opencode-job-email-triage-0fff020d966c-email-triage-hourly-email-auto-sort`
  - Current action: `powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\development\email-triage\scripts\hourly-email-auto-sort.ps1"`
  - Trigger: hourly repetition (`PT1H`)
  - Principal: `DaveWitkin`, `InteractiveToken`
- Script evidence:
  - `C:\development\email-triage\scripts\hourly-email-auto-sort.ps1`
  - Uses `Connect-MgGraph -ClientId ... -TenantId ... -Scopes 'Mail.ReadWrite','Mail.Read'`
  - Header comments explicitly note first interactive Graph login and MSAL cache behavior.
- Runtime evidence:
  - Latest status: `failed`
  - Log: `C:\development\email-triage\logs\2026-04-23_12-00_run.md`
  - Error: `Graph auth failed: An error occurred when writing to a listener.`

## Confirmed Root Cause

The hourly task uses delegated Graph auth (`Connect-MgGraph`) under an interactive principal. When token/session state requires user re-authentication, Microsoft account selection UI is presented. Because the task action launches visible PowerShell (previously without hidden window style), Terminal also appears.

## Immediate Mitigation (Completed)

Short-term mitigation applied to reduce visible shell disruption:

- Updated scheduled task action to include `-WindowStyle Hidden`:
  - `powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\development\email-triage\scripts\hourly-email-auto-sort.ps1"`

### Mitigation Limitations

- This suppresses visible PowerShell window in normal runs.
- This does **not** eliminate Microsoft sign-in prompts if interactive auth is still required.
- Therefore, mitigation reduces symptom severity but does not solve root cause.

## Desired End State

1. Email triage job runs unattended (no desktop popups).
2. Authentication is non-interactive and robust across token expiry/reboots.
3. Task runs with hidden/non-interactive execution model and deterministic logging.
4. Operational runbook exists for token/cert rotation, failure diagnosis, and rollback.

## Scope

### In Scope

- Scheduled task hardening for quiet/background execution.
- Auth model redesign from delegated interactive flow to app-only (or equivalent truly non-interactive) Graph auth.
- Permission and security review (least privilege, app registration, consent).
- Verification strategy and operational documentation.

### Out of Scope

- Rewriting classification heuristics/routing logic.
- Inbox taxonomy redesign.
- Unrelated OpenCode scheduled jobs (Gemini proxy, osgrep indexer, weekly report).

## Requirements

- [x] Identify concrete task causing popups.
- [x] Apply short-term hidden-window mitigation.
- [ ] Design long-term non-interactive Graph authentication approach.
- [ ] Define secure secret/certificate storage and rotation process.
- [ ] Update script/task design for unattended resiliency.
- [ ] Validate no account picker or terminal popup across multiple scheduled intervals.
- [ ] Document implementation, operations, and rollback.

## Permission Model Assumption

The current script behavior implies the long-term app-only path will need, at minimum, these Microsoft Graph **application** permissions:

| Script Operation | Current Cmdlet | Expected App Permission |
| --- | --- | --- |
| Read unread messages from Inbox child folder | `Get-MgUserMailFolderMessage` | `Mail.Read` or `Mail.ReadWrite` |
| Move messages between folders | `Move-MgUserMailFolderMessage` | `Mail.ReadWrite` |

Implementation should confirm these exact permissions against the final API/cmdlet path before cutover.

## Risks and Constraints

- Graph app-permission migration may require tenant admin consent.
- App-only mail operations can behave differently than delegated permissions depending on endpoint/permission grants.
- Secret handling must avoid plaintext exposure in scripts, logs, and task definitions.
- Existing MSAL cache artifacts may mask testing if not explicitly validated under clean/session-change conditions.
- Existing app registration (`ClientId 14d82eec-204b-4c2f-b7e8-296a70dab67e`) may be reusable, but reuse-vs-new must be decided explicitly to avoid permission drift or ownership ambiguity.

## Acceptance Criteria

- [ ] No visible Terminal window across at least 3 consecutive scheduled runs.
- [ ] No Microsoft account picker/sign-in popup across at least 3 consecutive scheduled runs.
- [ ] Scheduled task `LastTaskResult` returns success for validation window.
- [ ] Validation includes at least one run with the user session locked or otherwise unavailable for interactive sign-in.
- [ ] Email triage behavior remains functionally correct (messages still classified and moved).
- [ ] Runbook includes setup, verification commands, incident triage, and rollback steps.

## Success Metrics

- User-reported popup incidents drop to zero after rollout.
- Scheduled task success rate >= 95% over a 7-day observation window.
- Mean time to diagnose failures reduced via structured logs and explicit failure categories.
