# Spec: Install and Validate OpenCode DCP Plugin

**Track ID**: 20260314-dcp-install-validation  
**Created**: 2026-03-14  
**Status**: Completed  
**Priority**: High  
**Owner**: Build

---

## Problem Statement

The Dynamic Context Pruning plugin (`@tarquinen/opencode-dcp`) needs to be installed and validated in this environment, with evidence that package-level tests pass and OpenCode resolves the plugin in active configuration.

---

## Goals

- Install and validate plugin source repository build/test workflow.
- Add the plugin to OpenCode config used by this machine.
- Confirm OpenCode resolves the plugin in runtime configuration.
- Capture reproducible verification evidence in a conductor artifact.

---

## Scope

In scope:

- Clone `https://github.com/Opencode-DCP/opencode-dynamic-context-pruning`.
- Run `npm ci`, `npm run test`, `npm run build`, and `npm run typecheck`.
- Update `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` plugin list.
- Verify with `opencode debug config` that DCP is resolved.
- Record command outputs in track artifacts.

Out of scope:

- Publishing package updates.
- Modifying plugin source code.
- Deep functional behavior testing across many live OpenCode sessions.

---

## Success Criteria

- Dependency install, test suite, build, and typecheck all pass in cloned DCP repo.
- OpenCode config includes `@tarquinen/opencode-dcp@latest`.
- `opencode debug config` shows resolved DCP plugin entry.
- Track includes clear verification log and any remaining manual follow-up steps.
