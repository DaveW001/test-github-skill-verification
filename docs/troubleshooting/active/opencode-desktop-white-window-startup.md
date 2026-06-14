# OpenCode Desktop White Window On Startup

**Status:** Active troubleshooting note  
**Applies To:** OpenCode Desktop startup on Windows  
**Date Captured:** 2026-05-19

---

## Symptom

OpenCode Desktop launches, but the window stays completely white with no visible text or controls. The shell appears to start, but the GUI never becomes usable.

Observed during this incident:
- Desktop process starts
- App window opens white/blank
- No usable text is visible
- User cannot interact with the app normally

---

## What We Found

This was not a broken `opencode.jsonc` structure.

Validation showed:
- `opencode debug config` parsed successfully
- CLI smoke test worked with `opencode run -m opencode-go/glm-5.1`
- GUI prompts later worked for `opencode-go/glm-5.1` and `opencode-go/deepseek-v4-pro`

The strongest evidence pointed to stale Desktop session/state, not malformed JSONC:
- Desktop log showed a failed resumed session using `providerID=opencode-go`
- The request failed with:
  - `Error from provider: Extra inputs are not permitted, field: 'permissions'`
- That is consistent with a bad startup/resume path, not invalid JSONC syntax

---

## Likely Cause

The Desktop app is starting with stale session/state data that can trigger a bad resume path or a provider request the Go backend rejects. In this case, the user could recover by reopening the app and using a fresh prompt path.

Secondary contributors seen in the logs:
- repeated Skillful initialization
- duplicate skill-root warnings
- `No CLI installation found, skipping sync`

Those were noisy, but they did not block CLI operation once the correct Go API keys were moved to Windows user-level environment variables.

---

## Cleanup Procedure

Use this sequence when the GUI opens white/blank again:

1. Fully quit OpenCode Desktop.
2. Back up the Desktop state folders:
   - `C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop`
   - `C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop`
3. Clear only the session/state artifacts, not auth or config first:
   - remove or rename `opencode.workspace*.dat`
   - remove or rename `window-state.json`
   - remove or rename `.window-state.json`
   - remove or rename stale `Local Storage` / `Session Storage` contents if the window still comes back white
4. Leave these in place unless you have a separate auth problem:
   - `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
   - `C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe`
   - `C:\Users\DaveWitkin\.local\share\opencode\auth.json`
5. Reopen OpenCode Desktop.
6. Start a fresh chat instead of resuming the bad session.
7. Test with a known-working model such as:
   - `opencode-go/glm-5.1`
   - `opencode-go/deepseek-v4-pro`

### One-Command Recovery (Preferred)

For this environment, use the hardened recovery script:

```powershell
powershell -ExecutionPolicy Bypass -File C:\development\opencode\scripts\Invoke-OpenCodeDesktopSafeRecovery.ps1
```

What it does in order:
- Reapplies Skillful Desktop cache fixes via `Repair-SkillfulDesktopCache.ps1`
- Backs up and resets workspace/window state files
- Backs up and resets Desktop `Local Storage` / `Session Storage`
- Rotates `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` (optional, enabled by default)
- Writes a JSON recovery report in the timestamped artifact backup directory

---

## What Not To Change First

Do not start by editing `opencode.jsonc`. In this incident the config structure was valid.

Do not delete the auth file unless you are also solving a separate authentication issue.

Do not remove the user-level Go API keys once Desktop is working. The keys are required for Desktop GUI access.

---

## Validation Checklist

After cleanup:

- Desktop window renders normally
- `opencode-go/glm-5.1` runs a prompt successfully
- `opencode-go/deepseek-v4-pro` runs a prompt successfully
- No new provider error about `permissions`
- No repeat white-window startup on relaunch

---

## Related Files

- [OpenCode desktop troubleshooting track](file:///C:/development/opencode/.conductor/tracks/20260519-opencode-desktop-config-troubleshoot/spec.md)
- [Execution log](file:///C:/development/opencode/.conductor/tracks/20260519-opencode-desktop-config-troubleshoot/execution-log.md)
- [opencode configuration reference](file:///C:/development/opencode/docs/reference/opencode-configuration.md)

## Performance Follow-Up: MCP And Skillful Isolation

- On 2026-05-19, `control-chrome`, `slack`, and `playwright` MCPs were disabled during Desktop slowdown troubleshooting.
- If Desktop slows after startup, inspect logs for `OpencodeSkillful`, `duplicate skill name`, `MCP error -32601`, and `MaxListenersExceededWarning`.
- Use the conductor plan at `C:\development\opencode\.conductor\tracks\20260519-opencode-desktop-performance-skillful-isolation\plan.md`.
