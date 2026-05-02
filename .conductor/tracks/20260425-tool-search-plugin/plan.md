# Plan: Install and Validate opencode-tool-search Plugin

**Track ID**: 20260425-tool-search-plugin  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-04-25  
**Status**: Active ( awaiting TUI restart for Phase 3 functional tests)

---

## Phase 1: Pre-Install Verification & Baseline

- [x] Check OpenCode version is ≥ v1.4.10 → **was v1.2.26, upgraded to v1.14.25** (unplanned step)
- [x] Upgrade OpenCode from v1.2.26 → v1.14.25 via `npm install -g opencode-ai@latest`
- [x] Backup current `opencode.jsonc` to track artifacts (`opencode.jsonc.backup-pre-tool-search`)
- [x] Verify npm registry has the package: `npm view opencode-tool-search version` → **v0.4.3**
- [x] Record current plugin list and tool count for before/after comparison.

## Phase 2: Installation

- [x] Add plugin entry to `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` with tuple format:
  ```jsonc
  ["opencode-tool-search", {
    "alwaysLoad": ["read", "write", "edit", "bash", "glob", "grep", "task", "skill", "todowrite", "todoread", "webfetch", "websearch", "compress"]
  }]
  ```
- [x] **Immediate Syntax Check**: `opencode debug config` parses successfully with no errors.
- [x] Plugin confirmed in resolved config output: `opencode-tool-search` with `alwaysLoad` array visible.

## Phase 3: Headless Runtime Verification

- [ ] ~~Measure post-install token usage~~ → Deferred: `opencode run` requires active TUI session
- [ ] ~~Headless test `tool_search`~~ → Deferred: requires TUI session
- [ ] ~~Headless test `tool_search_regex`~~ → Deferred: requires TUI session
- [ ] ~~Verify core tools keep full descriptions~~ → Deferred: requires TUI session
- [ ] ~~Verify non-core tools show `[d]` deferred stubs~~ → Deferred: requires TUI session

> **Note**: `opencode run [message]` returns `Error: Session not found` without an active TUI session. Plugin npm install also occurs on first TUI load. All functional tests deferred to user TUI restart.

## Phase 4: Documentation and Evidence

- [x] Update `docs/reference/opencode-configuration.md` to list `opencode-tool-search` (6 → 7 plugins).
- [x] Capture validation log in `artifacts/validation-log.md`.
- [x] Update plan.md with execution results.
- [ ] Update `metadata.json` with final status → partial (pending TUI verification).

## Phase 5: User Handoff & Rollback

- [ ] User restarts OpenCode TUI → plugin installs from npm on first load.
- [ ] User runs functional verification in TUI (see validation-log.md handoff steps).
- [ ] *(Rollback if needed)*: Restore `opencode.jsonc` from backup in artifacts.

---

## Validation Commands Reference (for TUI session)

After restarting the TUI, test these in a new session:

```
# Test BM25 keyword search
Use tool_search to find file operations. List the tool names you found.

# Test regex search  
Use tool_search_regex for 'github.*issue'. List what you find.

# Verify compress is NOT deferred
The compress tool should be available with its full description.

# Verify non-core tools ARE deferred
Check if any tools show [d] stubs instead of full descriptions.
```

---

Checkbox states:
- [x] Completed
- [ ] Pending (deferred to TUI restart)
