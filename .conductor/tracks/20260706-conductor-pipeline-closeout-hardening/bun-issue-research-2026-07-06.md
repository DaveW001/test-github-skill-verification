# Bun Issue Research - 2026-07-06

## Upstream issue

- URL: https://github.com/anomalyco/opencode/issues/25880
- Title: Desktop v1.14.39: Bun-target plugins fail to load (Node.js sidecar lacks Bun APIs)
- State: OPEN
- Last updated: 2026-05-19T15:20:25Z
- Source: `gh issue view 25880 --repo anomalyco/opencode`

## Local fallback protocol (current)

Source: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` -> "Tool-Layer Failure Protocol (Bun is not defined)".

Protocol (verbatim intent):
- At session start, run one cheap file op. If a file tool returns `Bun is not defined`, switch the **whole session**
  to PowerShell-first via the bash tool immediately; do NOT retry the failing tool per-call (each retry is wasted).
- Bun 1.3.4 IS installed; this is a runtime sandbox-init failure (Node.js sidecar lacks Bun APIs), not a missing install.
- Cmdlet map: Read -> `Get-Content -Raw`, Write -> `Set-Content -Encoding utf8` (or verbatim here-string),
  Edit -> `Select-String` to locate + literal `[string]::Replace()`, glob -> `Get-ChildItem -Recurse`,
  grep -> `Select-String`.
- Full runbook: `docs\troubleshooting\tool-failure-bun-undefined.md`.

## Disposition

Document the actionable recommendation in the canonical troubleshooting doc (Phase 4.3). This track does NOT patch
runtime internals; the fix belongs upstream in issue #25880.
