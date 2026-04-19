# Spec: Gemini Proxy Scheduler Hardening

**Track ID**: 20260314-gemini-proxy-scheduler-hardening  
**Created**: 2026-03-14  
**Status**: In Progress  
**Priority**: High  
**Owner**: Build

---

## Problem Statement

Gemini proxy operations are functional, but operational resilience is incomplete in four areas:

1. Legacy/manual scheduled tasks can remain after migration and cause duplicate execution.
2. Scheduled-task failure visibility is limited.
3. Startup verification is implicit instead of explicit.
4. There is no single health-check command for fast diagnosis.

---

## Goals

- Keep architecture simple: no new persistent service and no additional recurring task unless required.
- Extend existing monitor/start scripts with explicit verification and alerting.
- Add an on-demand health check script for quick operator diagnostics.
- Remove orphaned legacy tasks safely.

---

## Scope

In scope:

- Update `C:\Users\DaveWitkin\.local\gemini-proxy\monitor-proxy.ps1`.
- Update `C:\Users\DaveWitkin\.local\gemini-proxy\start-proxy-quiet.ps1`.
- Add `C:\Users\DaveWitkin\.local\gemini-proxy\health-check.ps1`.
- Verify and clean targeted legacy tasks (`GeminiProxyMonitor`, `GeminiAPIKeyRotator`, `OsgrepAutoIndexer`, `OsgrepBridge`) if present.

Out of scope:

- New long-running daemons.
- New periodic task beyond current opencode-scheduler jobs.

---

## Success Criteria

- Existing monitor emits alerts for task lag/failure and startup-marker issues.
- Starter writes explicit startup marker for monitor and health checks.
- Health check script returns pass/fail snapshot for proxy + tasks + markers + logs.
- Legacy targeted tasks are absent from Task Scheduler.
