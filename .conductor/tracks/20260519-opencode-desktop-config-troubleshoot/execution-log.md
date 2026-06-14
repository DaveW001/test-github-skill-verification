# Execution Log: 20260519-opencode-desktop-config-troubleshoot

## 2026-05-19 - Initial Investigation

### Evidence collected

- `C:\development\opencode` exists and contains the relevant `.conductor` history.
- No git commits were found in `C:\development\opencode` between `2026-05-18 00:00` and `2026-05-19 00:00`.
- No tracked repo config files were modified on May 18; only `.osgrep` index files changed inside the repo.
- `C:\Users\DaveWitkin\.config\opencode` showed no May 18 file modifications.
- `C:\Users\DaveWitkin\.opencode` showed only `cache\update-check-cache.json` modified on May 18.
- Desktop state/log files under `AppData` did change on May 18, especially:
  - `C:\Users\DaveWitkin\AppData\Local\ai.opencode.desktop\logs\opencode-desktop_2026-05-18_14-49-48.log`
  - several `C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\opencode.workspace.*.dat` files

### May 18 Desktop log observations

- Startup line: `No CLI installation found, skipping sync`.
- Desktop sidecar became ready on `http://127.0.0.1:60780`.
- Skillful discovered and registered 59 skills, then repeated initialization several times.
- Later Skillful discovered 60 skills after including `C:\development\playground\.opencode\skills`.
- OpenCode emitted duplicate skill-name warnings across `.agents`, `.config\opencode\skill`, `.config\opencode\skills`, and project skill roots.
- MCP prompt errors appeared for `slack` and `control-chrome`, but those look like unsupported prompt capability warnings rather than the main config failure.
- The session ended quickly: `Killed server`, sidecar terminated with code `1`.

### Current leading hypothesis

The strongest current signal is that the dual OpenCode Go provider keys were stored only in `C:\Users\DaveWitkin\.config\opencode\.env`, while Desktop has a documented history of not reliably inheriting `.env` provider credentials. Windows user-level and current process checks returned `False` for both `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY`.

Secondary signals are duplicate skill-root loading after prior skill junction unification and the `No CLI installation found, skipping sync` Desktop startup line.

## 2026-05-19 - Dual Go Subscription Pivot

### User clarification

The relevant May 17/18 change was setting up two different OpenCode Go subscriptions with different API keys.

### Track found

Found `C:\Users\DaveWitkin\.config\opencode\.conductor\tracks\20260517-opencode-go-dual-sub-config`.

Key findings from that track:

- It added `go-dave` and `go-tiberius` providers to `opencode.jsonc`.
- It added `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` to `.env`.
- It intended Desktop switching through `/models`.
- Its execution log notes both providers surface the same `opencode-go/` model catalog.

### Current checks

- `where opencode` found `C:\Users\DaveWitkin\AppData\Roaming\npm\opencode` and `.cmd`.
- `opencode --version` returned `1.14.29`.
- `opencode debug config` parses and shows the active global plugin list, including `oc-codex-multi-auth`.
- `opencode models` shows `opencode-go/*` models, but not visibly separate `go-dave/*` and `go-tiberius/*` model prefixes.
- Windows user-level and current process environment checks for both Go API key variables returned `False`.
- Existing `docs\reference\environment-variables.md` states Desktop previously required user-level env vars for provider API keys because `.env` did not reliably propagate into Desktop.

### Applied fix

- Promoted `OPENCODE_GO_DAVE_API_KEY` and `OPENCODE_GO_TIBERIUS_API_KEY` from `.env` into Windows user-level environment variables.
- Restarted `C:\Users\DaveWitkin\AppData\Local\Programs\OpenCode\OpenCode.exe` so the Desktop runtime can consume the new user-level variables.
- `opencode models` now returns the Go model catalog successfully in a fresh process.
- `opencode run -m opencode-go/glm-5.1 "Reply with exactly: CLI smoke test passed"` returned `CLI smoke test passed` and exited `0`.

### GUI failure detail

- The newest Desktop log shows normal app bootstrap and then repeated Skillful initialization plus MCP prompt warnings.
- A prior session request in the same log failed with:
  - `service=llm providerID=opencode-go modelID=kimi-k2.6`
  - `error=Error from provider: Extra inputs are not permitted, field: 'permissions'`
- That means the JSONC file is structurally parseable, but at least one runtime path is not accepted by the Go provider. The white GUI window is therefore more consistent with a broken startup/session-resume path than with malformed JSONC syntax.

### GUI recovery result

- User successfully opened the Desktop app after the restart.
- `opencode-go/glm-5.1` worked in the GUI.
- `opencode-go/deepseek-v4-pro` also worked in the GUI.
- This confirms the config structure is intact and the Go provider path is usable in Desktop once the stale resume state is bypassed.

### Documentation written

- Added `C:\development\opencode\docs\troubleshooting\active\opencode-desktop-white-window-startup.md` with the white-window symptom, the observed startup behavior, cleanup steps for stale Desktop state, and a validation checklist for the next agent.

### Validation note

- I briefly triggered a local `SQLiteError: database is locked` by running multiple `opencode` commands in parallel against the same local database. Re-running sequentially resolved the command-side contention.
- The latest inspected Desktop log did not yet show a new error after the restart window, but it also did not emit a fresh startup block in the captured tail. The Desktop process is running and needs one human-visible interaction pass to confirm the GUI-side auth behavior.

### Guardrails

- Do not delete Desktop `.dat`, auth, cache, or config files without a timestamped backup.
- Do not collapse `skill` versus `skills` until checking the repo/user instruction that says to stop and ask if both exist before editing.
- Apply at most one fix candidate before restarting and validating Desktop.
- Do not print or commit API key values. If promoting `.env` values to user-level env vars, use PowerShell variables/read-from-file patterns that avoid echoing secrets.
