# Plan: Gemini Proxy Scheduler Hardening

**Track ID**: 20260314-gemini-proxy-scheduler-hardening  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-03-14  
**Status**: Completed (2026-03-14)

---

## Phase 1: Script Hardening

- [x] Add startup marker write in starter script.
- [x] Add monitor checks for scheduled task health:
  - [x] last run freshness by expected cadence
  - [x] last task result success (`0`)
  - [x] task missing detection
- [x] Add monitor alert categories for scheduler health.

## Phase 2: Health Check Script

- [x] Add a single-run health report script with exit code semantics.
- [x] Include:
  - [x] proxy listening status
  - [x] status endpoint check
  - [x] startup marker recency
  - [x] scheduled task checks
  - [x] tail pointers to key logs

## Phase 3: Legacy Task Cleanup

- [x] Verify presence/absence of known legacy tasks.
- [x] Remove any remaining known legacy tasks.

## Phase 4: Validation

- [x] Run health check and confirm PASS/FAIL behavior.
- [x] Trigger monitor once and inspect state/alerts output.
- [x] Confirm only opencode-scheduler jobs remain for migrated tasks.
