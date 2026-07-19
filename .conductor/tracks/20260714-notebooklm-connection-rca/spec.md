# NotebookLM Query Connection RCA

**Status:** RCA complete; remediation requires approval and execution.

## Objective

Determine why OpenCode sessions intermittently failed to retrieve data from the `C2/CC2 Portfolio Engagement Kx` NotebookLM notebook despite valid authentication, and define a safe, evidence-based remediation path.

## Scope

- `notebooklm-mcp-cli` / `nlm` on this Windows host.
- Read-only NotebookLM list, source-inventory, authentication, and query checks.
- The reported transport failures: `Server disconnected without sending a response`, `peer closed connection`, and `incomplete chunked read`.

## Out of Scope

- Modifying notebook sources, Studio artifacts, or sharing settings.
- Changing credentials or exposing cookies/tokens.
- Implementing the package upgrade or a new retry runner in this RCA track.

## Acceptance Criteria

- [x] Separate confirmed facts from likely contributing factors and hypotheses.
- [x] Verify current authentication, notebook access, source count, and a grounded data query.
- [x] Establish whether the incident is a current permanent outage or an intermittent failure.
- [x] Identify supported upstream recovery capabilities and the installed-versus-current version gap.
- [x] Provide a gated remediation plan that avoids blindly enabling experimental transport.
