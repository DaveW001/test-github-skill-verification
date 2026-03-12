# Osgrep Unwanted Folder Creation Summary

## Scope

This summary documents a historical MCP/integration-specific failure mode.

- It does not prove standalone CLI behavior is broken in the same way.
- The central status doc is `docs/troubleshooting/active/osgrep-intermittent-hang-disablement-2026-03-11.md`.

## Observed Behavior

- During prior integration experiments, osgrep created `.osgrep` state under unexpected paths.
- String/path handling allowed non-project locations to be treated as project roots.

## Why It Matters

- Unexpected directory creation can pollute workspaces and confuse follow-up diagnostics.
- It reinforced the decision to keep OpenCode osgrep automation disabled until controlled CLI-only re-introduction.

## Practical Guidance

- Use explicit working directories for any osgrep debug runs.
- Capture logs with `scripts/utils/osgrep_debug_wrapper.py`.
- Treat MCP/service-mode findings separately from direct CLI evidence.
