# Stage 3 Conditional Re-Review - Scheduled Task Read Inconsistency

- **Track:** 20260705-scheduled-task-read-inconsistency
- **Stage 2 reviewer model:** opencode-go/minimax-m3
- **Stage 3 re-reviewer model:** openai/gpt-5.5 (variant low)
- **Diversity check:** Stage 3 model != Stage 2 model - OK.
- **Spec:** C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\spec.md
- **Plan:** C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\plan.md
- **Prior report:** C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\review-report-2026-07-05-113940.md
- **Re-review timestamp:** 2026-07-05-120033
- **Environment:** Native file tools are broken (Bun is not defined); this pass used bounded PowerShell via the ash tool only. Elevation-dependent gsudo commands remain untested (requires elevation).

## Overall Verdict

Stage 2's seven strengthenings mostly closed the original review gaps. I agree with Stage 2's **75% at the time of its report** because the pre-edit plan had real template/verification weaknesses and many elevation-dependent commands could not be tested from the reviewer shell.

After this Stage 3 pass and the high-confidence edits applied below, the plan is **execution-ready with elevation/approval gates**. Remaining risk is operational, not structural: Phase 1/3/4 elevated commands still must be validated by the executor in an environment where UAC can be approved.

**Readiness score after Stage 3 edits: 90%.**

## High-Confidence Edits Applied in Stage 3

Plan backup created before editing:
C:\development\opencode\.conductor\tracks\20260705-scheduled-task-read-inconsistency\plan.md.rereview-backup-2026-07-05-115800

1. **Task 2.1 placeholder check:** added the two interpretation placeholders (<Missing GUID blob / ...> and <Option 1 / Option 2 / Option 3>) to the strict no-placeholder acceptance check.
2. **Task 2.2 command:** replaced ambiguous literal replacements to <chosen branch> / <chosen option> with explicit $chosenBranch and $chosenOption variables, allowed-value guards, and literal [string]::Replace() calls using those concrete values.
3. **Task 3.1 gate wording:** changed error recovery to explicitly **STOP before Tasks 3.2 and 3.3** if approval is denied or ambiguous.
4. **Task 3.3 timestamp:** changed the command to capture the JSON result, print it for acceptance checking, and append ## Remediation Applied: <iso timestamp> to the execution log only after successful Option 1 re-registration.
5. **Task 4.3 hourly-firing surrogate:** updated the acceptance check so it passes either when a post-remediation/same-day run log is found or when the bounded-run follow-up note has been appended. This avoids falsely failing a run simply because the hourly cadence has not ticked yet.

## Verification-Snippet Testing Performed

- Task 2.2 replacement logic was simulated against a temp root-cause evidence file. Result: True; placeholders were replaced by concrete branch/option values.
- Task 4.3 revised acceptance logic was simulated for two relevant cases:
  - post-remediation log exists: True
  - pre-remediation log only, but follow-up note logged: True
- Stage 2's prior dry-runs for non-elevated syntax/placeholder checks remain valid.
- gsudo/Task Scheduler/registry commands are **untested (requires elevation)** and must be validated by the Stage 4 executor.

## Task-by-Task Ratings

### Phase 0 - Setup & Preconditions

- **Task 0.1 - Confirm required input artifacts exist:** Ready. Exact paths and Test-Path loop are executable.
- **Task 0.2 - Confirm elevated-command readiness without running diagnostics:** Ready, gated on elevation. Stage 2's try/catch hardening closes the non-JSON/denied-elevation parse gap.
- **Task 0.3 - Create the execution log skeleton for this track:** Ready. Uses a deterministic dated path and concrete section skeleton.

### Phase 1 - Elevated Diagnostic

- **Task 1.1 - Capture elevated on-disk XML evidence:** Ready, untested (requires elevation). Exact path and XML parse checks are sufficient.
- **Task 1.2 - Capture elevated API split behavior:** Ready, untested (requires elevation). OK/ERR accumulator is appropriate for diagnostic evidence.
- **Task 1.3 - Capture elevated TaskCache Tree and GUID blob evidence:** Ready, untested (requires elevation). Stage 2's BlobKey==Tasks+Id check closes GUID consistency.
- **Task 1.4 - Capture elevated read-only sibling controls:** Ready, untested (requires elevation). Sibling exclusion and at-least-one-OK control are sensible.
- **Task 1.5 - Capture recent Task Scheduler operational events:** Ready, untested (requires elevation/event-log access). Empty retained event set is allowed and not a blocker.

### Phase 2 - Root Cause Determination

- **Task 2.1 - Write the root-cause evidence table:** Ready after Stage 3 edit. Stage 2 missed the interpretation placeholders in this check; now all decision placeholders must be replaced or explicitly set to UNKNOWN - <reason> where applicable.
- **Task 2.2 - Select the remediation branch based on evidence:** Ready after Stage 3 edit. The prior command would literally insert <chosen branch> and <chosen option>, then fail its own acceptance check. It now uses concrete guarded variables.

### Phase 3 - Remediation

- **Task 3.1 - Obtain explicit Tier-1 approval before touching task registration:** Ready after Stage 3 edit. The STOP/proceed branch is now unambiguous: denied/ambiguous approval means do not run Tasks 3.2/3.3.
- **Task 3.2 - Back up the on-disk XML before approved registration remediation:** Ready, untested (requires elevation). Strict length equality check is sufficient.
- **Task 3.3 - Apply approved Option 1 re-registration from on-disk XML:** Ready after Stage 3 edit, untested (requires elevation and approval). The command now emits JSON and records a remediation timestamp needed by Task 4.3.
- **Task 3.4 - Document Option 3 if remediation is deferred:** Ready. Stage 2's reason-placeholder check is adequate.

### Final Phase - Validation & Handover

- **Task 4.1 - Validate target metadata APIs after remediation or document unchanged failure after deferral:** Ready, untested (requires elevation). Correctly treats false after deferral as a known remaining issue.
- **Task 4.2 - Validate sibling tasks still read normally:** Ready, untested (requires elevation). Excludes the target and checks at least one healthy sibling.
- **Task 4.3 - Check or defer hourly firing evidence without stalling:** Ready after Stage 3 edit. The in-run surrogate is now sensible: prove a recent/post-remediation log if available; otherwise log a timed follow-up without waiting for the hourly tick.
- **Task 4.4 - Finalize handover summary:** Ready. Stage 2's no-placeholder check closes the shallow-summary gap.

## New Issues Stage 2 Missed

1. **Task 2.2 self-inconsistent command:** it inserted <chosen branch>/<chosen option> while the acceptance check required those strings to be absent. Fixed.
2. **Task 3.3/4.3 dependency mismatch:** Task 4.3 required a remediation timestamp, but Task 3.3 did not create it. Fixed.
3. **Task 4.3 cadence mismatch:** expecting True solely from a post-remediation hourly log can be unrealistic during a bounded run. Fixed by allowing an explicit timed follow-up note.

## Top 3 Priorities for Stage 4 Executor

1. **Do not proceed past Task 0.2 unless elevation is confirmed.** Most diagnostic evidence is invalid without elevated TaskCache/API access.
2. **Treat Task 3.1 as a hard STOP gate.** If approval is denied or ambiguous, skip registration-touching Tasks 3.2/3.3 and run Task 3.4 instead.
3. **For hourly firing, do not wait.** Run the bounded latest-log check once; if no post-remediation/same-day log exists, append the timed follow-up note and continue handover.

## Final Readiness

- **Overall readiness score:** 90%.
- **Agreement with Stage 2's 75%:** Yes, for the pre-Stage-3 plan. Stage 3 edits raise readiness to 90%.
- **One-line verdict:** Ready to execute, subject to real elevation availability and explicit Tier-1 approval before any registration touch.
