# Spec: Upgrade opencode-snippets Plugin v1.7.0 → v1.8.0

## Goal

Upgrade the `opencode-snippets` plugin from v1.7.0 to v1.8.0 in the local OpenCode installation and validate that all snippet functionality works correctly after the upgrade, including the new injection placement behavior.

## Context

- **Current version**: `1.7.0` (installed Feb 5, 2026)
- **Target version**: `1.8.0` (released Apr 2, 2026)
- **Plugin location**: `C:\Users\DaveWitkin\.config\opencode\node_modules\opencode-snippets\`
- **Config reference**: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` (line 4: `"opencode-snippets@1.7.0"`)
- **Package reference**: `C:\Users\DaveWitkin\.config\opencode\package.json` (line 6: `"opencode-snippets": "1.7.0"`)
- **Snippet config**: `C:\Users\DaveWitkin\.config\opencode\snippet\config.jsonc` (debug logging enabled)
- **Active snippets**: 20 custom snippets in `C:\Users\DaveWitkin\.config\opencode\snippet\`

## What Changed in v1.8.0

### Major: Injection Placement Redesign
- `<inject>` blocks now use **constant offset placement** instead of the previous refresh/sawtooth pattern
- Injections float at a fixed position N messages from the bottom (`targetPosition = max(0, messageCount - recencyWindow)`)
- As conversation grows, injections naturally age upward without snapping back
- Prevents "instruction overfitting" where the model fixates on inject content as a fresh directive
- `InjectionManager` completely rewritten with simpler, stateless position calculation
- New `registerAndGetNew()` API for first-registration-only notifications
- `touchInjections()` returns boolean instead of detailed refresh info
- New config comment for `injectRecencyMessages`: "how many messages from bottom"

### Bug Fix (from v1.7.1)
- Fixed CJS/ESM import compatibility for `opencode web` mode

## Requirements

- [ ] Update plugin version in `opencode.jsonc` from `1.7.0` to `1.8.0`
- [ ] Update plugin version in `package.json` from `1.7.0` to `1.8.0`
- [ ] Run `npm install` (or equivalent) to fetch the new version into `node_modules`
- [ ] Verify installed version is `1.8.0` in `node_modules/opencode-snippets/package.json`
- [ ] Verify existing snippet config (`config.jsonc`) remains compatible
- [ ] Validate core snippet expansion works (basic hashtag expansion)
- [ ] Validate shell command substitution in snippets works
- [ ] Validate snippet composition (snippets including other snippets) works
- [ ] Validate `<inject>` block behavior with new constant offset placement (if any snippets use inject blocks)
- [ ] Validate debug logging still works and writes to the expected daily log path
- [ ] Confirm OpenCode starts without errors after the upgrade

## Non-Requirements

- [ ] Modifying any existing snippet content
- [ ] Adding new snippets
- [ ] Changing snippet config settings
- [ ] Upgrading any other plugins

## Acceptance Criteria

- [x] `node_modules/opencode-snippets/package.json` reports version `1.8.0`
- [x] `opencode.jsonc` plugin entry updated to `opencode-snippets@1.8.0`
- [x] `package.json` dependency updated to `1.8.0`
- [x] At least 3 snippet expansion tests pass (basic, shell, composition)
- [x] No errors in OpenCode startup or snippet loading
- [x] Debug log file created for the test session showing successful snippet registration
- [x] All 19 existing snippets remain intact and discoverable
