# Plan: Diagnose and Restore OpenCode Snippet Expansion

## Phase 1 - Reproduce and Bound the Failure
- [x] Confirm known snippet alias exists in `plan-review.md` (`planrev`, `plan-review`, `revplan`).
- [x] Confirm global OpenCode config still loads `opencode-snippets@1.8.0`.
- [x] Confirm package dependency and installed package version are both `1.8.0`.
- [x] Review recent snippet logs to establish last-known-good vs current-failing behavior.
- [x] Validate `#planrev` expands correctly when the plugin is invoked directly in Bun outside OpenCode.
- [ ] Reproduce in a fresh OpenCode session with a minimal prompt containing `#planrev`.
- [ ] Capture exact before/after message text and the corresponding snippet log lines.

## Phase 2 - Root-Cause Investigation
- [ ] Inspect the plugin’s runtime loader path in the actual failing environment.
- [ ] Determine whether the failing OpenCode session is using a stale or divergent plugin/runtime instance.
- [ ] Check whether OpenCode core/autoupdate changed between the last-known-good session and the first failing session.
- [x] Check whether multiple OpenCode processes, stale plugin state, or mixed runtimes explain the intermittent success/failure pattern seen on 2026-04-06.
- [ ] Verify whether the problem is limited to this plugin or affects other CJS-backed plugins too.

## Phase 3 - Fix Strategy Selection
- [ ] Prefer the smallest reversible fix:
  - [ ] Option A: restart/refresh the OpenCode host so it loads the current plugin state cleanly.
  - [ ] Option B: reinstall or pin a known-good plugin/core combination if the regression is version-specific.
  - [ ] Option C: patch plugin import interop logic only if the failing runtime path reproduces in isolation.
- [ ] Document why the selected option is safest.
- [ ] Document rollback steps before making runtime changes.

## Phase 4 - Validation
- [ ] Restart OpenCode after applying the fix.
- [ ] Validate alias expansion: `#planrev`.
- [ ] Validate filename expansion: `#plan-review`.
- [ ] Validate another existing snippet with aliases, such as `#ctx` or `#safe`.
- [ ] Validate a shell-enabled snippet still expands correctly.
- [ ] Validate that the standalone Bun smoke test still passes after any runtime change.
- [ ] Review the daily snippet log and confirm there are no new `matter is not a function` warnings.
- [ ] Review the daily snippet log and confirm there are no new `parseJsonc is not a function` warnings.
- [ ] Confirm plugin startup log shows snippets loaded and a non-zero snippet count.

## Phase 5 - Documentation and Hardening
- [ ] Update snippet troubleshooting documentation with the new failure signature and fix.
- [ ] Update the snippet upgrade/validation workflow to require a real end-to-end hashtag smoke test after restart.
- [ ] Record the exact versions, commands, and verification evidence used.

## Recommended Test Matrix
- [ ] Fresh session, single alias: `#planrev`
- [ ] Fresh session, primary name: `#plan-review`
- [ ] Mixed prompt text plus snippet: `Please review this plan #planrev`
- [ ] Shell snippet: `#ctx` or equivalent
- [ ] Cross-project check in a second repo to rule out repo-specific state

## Risks
- [ ] Intermittent behavior may hide the true trigger unless logs are captured immediately after restart.
- [ ] A host-runtime regression may require pinning or upstream escalation rather than a local plugin-only fix.
- [ ] Reinstall-only fixes may mask the underlying import-shape bug if validation is too shallow.

Checkbox states:
- [ ] Pending
- [~] In Progress
- [x] Completed

Important: this plan is intentionally biased toward runtime reproduction and log-backed verification, because static package checks already passed once while the real feature still failed later.
