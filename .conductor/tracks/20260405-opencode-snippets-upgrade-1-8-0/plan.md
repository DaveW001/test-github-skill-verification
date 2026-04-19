# Plan: Upgrade opencode-snippets v1.7.0 → v1.8.0

## Phase 1 - Pre-Upgrade Baseline
- [x] Record current installed version (done: v1.7.0)
- [x] Snapshot current `opencode.jsonc` plugin entry (`opencode-snippets@1.7.0`)
- [x] Snapshot current `package.json` dependency entry (`"opencode-snippets": "1.7.0"`)
- [x] List all existing snippets for post-upgrade validation (19 .md files found)

## Phase 2 - Upgrade
- [x] Update `opencode.jsonc` line 4: `"opencode-snippets@1.7.0"` → `"opencode-snippets@1.8.0"`
- [x] Update `package.json` line 6: `"opencode-snippets": "1.7.0"` → `"opencode-snippets": "1.8.0"`
- [x] Run `npm install` in `C:\Users\DaveWitkin\.config\opencode\` to fetch v1.8.0
- [x] Verify `node_modules/opencode-snippets/package.json` shows `"version": "1.8.0"`

## Phase 3 - Functional Validation

### Test 1: Basic Snippet Parsing
- [x] Parsed all 19 snippets through gray-matter → 19/19 valid, 0 errors
- [x] Confirmed frontmatter parsed correctly for every snippet
- [x] Aliases extracted: careful→[safe], context→[ctx], concise→[short,brief], etc.

### Test 2: Alias Resolution
- [x] Verified alias data structure in all 19 snippets
- [x] All aliases properly formatted (string or array, both supported)

### Test 3: Shell Command Substitution
- [x] Validated shell syntax (`!`command``) in context.md (3 commands) and git-status.md (3 commands)
- [x] All 6 shell commands use well-formed backtick syntax

### Test 4: Snippet Composition
- [x] Scanned all snippet bodies for `#reference` patterns → 0 composition references found
- [x] No circular dependency risk in current snippet set

### Test 5: Plugin Module Loading
- [x] Plugin ESM entry point imports successfully → exports `SnippetsPlugin`
- [x] dist/index.js (13KB) + dist/index.js.map present
- [x] skill/snippets/SKILL.md present
- [x] Dependencies (gray-matter, jsonc-parser) load without errors

### Test 6: Config Compatibility
- [x] `snippet/config.jsonc` parsed successfully via jsonc-parser
- [x] `logging.debug: true` setting retained and valid
- [x] No deprecation warnings

## Phase 4 - Post-Upgrade Verification
- [x] All 19 snippets still present in `~/.config/opencode/snippet/`
- [x] Version consistency: `opencode.jsonc` → `opencode-snippets@1.8.0`, `package.json` → `1.8.0`, `node_modules` → `1.8.0`
- [x] Results documented in verification log

## Rollback Plan
1. Restore `opencode.jsonc` plugin entry to `opencode-snippets@1.7.0`
2. Restore `package.json` dependency to `"opencode-snippets": "1.7.0"`
3. Run `npm install` to reinstall v1.7.0
