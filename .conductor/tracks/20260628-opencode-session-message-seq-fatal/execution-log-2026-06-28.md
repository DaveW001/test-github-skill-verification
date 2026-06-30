# Issue Log - 20260628-opencode-session-message-seq-fatal
**Run date:** 2026-06-28
**Agent:** Build (default)
**Outcome:** ABORTED at Phase 0.1 - no remediation work performed.

## Issue I1 - Executing agent runs inside a live OpenCode session (Phase 0.1 gate failure)

**Severity:** Blocking (hard abort per plan).
**Type:** Execution-context conflict / self-termination risk.

**Detail:** The Conductor track was invoked from inside a running OpenCode desktop session. The plan's Phase 0.1 preflight check requires the executing shell NOT be a child of an OpenCode process. The captured parent chain proves it is:

| PID | Process | Role |
|-----|---------|------|
| 6292 | pwsh | bash-tool shell executing the plan |
| 46488 | OpenCode (node utility, 
ode.mojom.NodeService) | direct parent of the shell - HOSTS the agent |
| 5736 | OpenCode (--updated) | main desktop application |
| 14596 | explorer | session root |

Seven OpenCode processes + four 
ode processes were live at the time.

**Why this blocks every subsequent phase:**
- Phase 1.2 runs Get-Process opencode | Stop-Process -Force, which is case-insensitive on Windows and would match the OpenCode desktop PIDs - including 46488, the agent's own parent. Executing it would kill the agent mid-run.
- Phase 2.1 runs 
pm install -g opencode-ai@1.17.11, mutating the runtime currently hosting this session.
- The plan's header warning is explicit: "Do not run the upgrade from inside a live opencode session."
- Task Safety Rule: "Never upgrade the runtime while a live opencode session/scheduler holds the DB."

**Resolution / next action for the user:**
1. Close ALL OpenCode desktop windows (and verify zero OpenCode / opencode-server processes via Task Manager).
2. Open a **plain** PowerShell 7 window from the Start Menu or Windows Terminal (NOT from inside OpenCode). Confirm the parent chain is pwsh -> WindowsTerminal -> explorer (or pwsh -> explorer).
3. Re-invoke the Conductor track execution from that terminal. Phase 0.1 will then pass and the 27-task plan (0.2 onward) can execute end to end.

## Other issues
None. No tool calls failed for environmental reasons beyond the already-known Bun is not defined file-tool failure (handled by switching the whole session to PowerShell-first: Get-Content/Set-Content/Select-String/Get-ChildItem). No API/access errors. No items skipped by ambiguity. No deferred/out-of-scope items were touched.

## Validation performed
- Phase 0.1 parent-chain inspection (the only check run). Result: FAIL -> abort.
- No DB, runtime, cache, scheduler, or config validation was performed or needed, because the abort precedes all such steps.
