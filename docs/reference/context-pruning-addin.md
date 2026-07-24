# Context Pruning Add-In (DCP)

## Add-in name

- Package: `@tarquinen/opencode-dcp`
- Purpose: Dynamic context pruning support via `/dcp` in interactive OpenCode sessions.

## Where it is configured

- Active OpenCode user config: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
- Installed in the `plugin` array as: `"@tarquinen/opencode-dcp@latest"`

## How we installed it (brief)

1. Confirmed install instructions from the project README.
2. Added `"@tarquinen/opencode-dcp@latest"` to the `plugin` list in the active user config file.
3. Verified plugin resolution with:

```bash
opencode debug config | rg "@tarquinen/opencode-dcp|plugin"
```

## How we tested it (brief)

Source repo used for validation:

- `C:\development\opencode-dcp-child-fix`

Validation command run in that repo:

```bash
npm ci && npm run test && npm run build && npm run typecheck
```

Observed results:

- Dependencies installed cleanly
- Tests passed (`10 passed, 0 failed`)
- Build passed
- Typecheck passed

Note:

- `opencode run "/dcp"` returned `Session not found` in non-interactive mode; this is expected for that invocation style.
- Final smoke test should be done in an interactive session after restart by running `/dcp`.

## Where the supporting documentation is

- This file: `C:\development\opencode\docs\reference\context-pruning-addin.md`
- Conductor track root: `C:\development\opencode\.conductor\tracks\20260314-dcp-install-validation`
- Conductor validation log: `C:\development\opencode\.conductor\tracks\20260314-dcp-install-validation\artifacts\validation-log.md`

## Child-Session Safety (2026-07)

The DCP plugin was hardened to protect Task-created child sessions:

- Per-session state isolation via SessionStateRegistry (no shared mutable global)
- Default compression eligibility for child sessions (blanket deny removed; opt-in via experimental.force_child_tool_deny)
- Blocking-pending-compression enforcement with durable handoff fallback
- Content-free telemetry (6 transition events, SHA-256 redacted session IDs)
- 150K token caps for all active model identities

Source checkout: C:\development\opencode-dcp-child-fix
Track: C:\development\opencode\.conductor\tracks\20260717-dcp-child-session-safety
## Do we need to keep the local cloned repo?

Short answer: The runtime does not need a local clone to function, but the current source checkout contains unmerged child-session-safety work and should NOT be deleted until upstreamed.

Reason:

- OpenCode uses the configured plugin package (`@tarquinen/opencode-dcp@latest`) from config resolution, not the local clone in `C:\development\opencode-dcp-child-fix`.

If the work has been upstreamed and you want to clean up:

```bash
rm -rf "C:\development\opencode-dcp-child-fix"
```
