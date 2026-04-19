# Handover: Osgrep Stabilization Investigation Complete

**Date**: 2026-03-13  
**Track**: 20260313-osgrep-stabilization  
**Parent**: 20260312-osgrep-cli-only-reenable  
**Status**: Investigation Complete → Ready for Implementation

---

## Summary

I've completed the root cause analysis for all three osgrep failure modes blocking the CLI-only re-enablement GO decision. The investigation identified **simple, low-risk fixes** that can be implemented quickly.

**Key Discovery**: LanceDB 0.22.3 supports `{ existOk: true }`, making the race condition fix a **one-line change** instead of complex mutex implementation.

---

## Investigation Results

### 1. Table 'chunks' already exists (TC-01, TC-02) ✅ ANALYZED

**Root Cause**: Race condition in `vector-db.js:ensureTable()`  
**Location**: Line 152 in `db.createTable()` call  
**Fix Complexity**: **ONE LINE** - add `existOk: true` option

```javascript
// BEFORE (causes race condition):
const table = await db.createTable(TABLE_NAME, [this.seedRow()], { schema });

// AFTER (race-safe):
const table = await db.createTable(TABLE_NAME, [this.seedRow()], { 
    schema, 
    existOk: true  // <-- ADD THIS LINE
});
```

**Why it works**: LanceDB's `existOk` mode makes table creation idempotent - concurrent calls safely return the existing table instead of throwing "already exists".

---

### 2. FTS Inverted-Index Warning (TC-04) ✅ ANALYZED

**Root Cause**: FTS index creation may fail silently on large repos; searcher doesn't handle FTS failures gracefully  
**Location**: `searcher.js` lines 312-320 (lazy FTS init), lines 327-337 (FTS query)  
**Fix Complexity**: **Low** - add graceful degradation

The searcher already catches FTS errors and logs warnings (line 336), but the warning messages may indicate deeper issues with FTS index consistency on large repositories. The current code falls back to vector-only search when FTS fails, which is correct behavior.

**Recommended fix**: 
- Enhance `createFTSIndex()` to validate index after creation
- Consider rebuilding FTS index automatically when warnings are detected
- Document expected behavior for large repos

---

### 3. Stale Index Behavior (TC-11) ✅ ANALYZED

**Root Cause**: Search results may include entries for files that no longer exist; no validation before returning results  
**Location**: `searcher.js` - result mapping and return  
**Fix Complexity**: **Medium** - add file existence validation

The syncer removes stale entries at the end of indexing (lines 367-372 in syncer.js), but if indexing is interrupted or files change during search, stale entries can be returned.

**Recommended fix**:
- Add file existence check in `mapRecordToChunk()` or before returning results
- Filter out results where `fs.access(record.path)` fails

---

## Files to Modify

All files are in the osgrep npm module:

```
%APPDATA%/npm/node_modules/osgrep/dist/lib/store/vector-db.js  (Fix #1 - line 152)
%APPDATA%/npm/node_modules/osgrep/dist/lib/search/searcher.js  (Fix #2, #3)
```

**Backup recommended**: Copy original files before modifying.

---

## Implementation Priority

| Priority | Fix | Effort | Impact |
|----------|-----|--------|--------|
| **P0** | Add `existOk: true` to createTable | 1 line | Resolves TC-01, TC-02 |
| **P1** | Add file existence validation to search results | ~10 lines | Resolves TC-11 |
| **P2** | Enhance FTS validation | ~20 lines | Resolves TC-04 warnings |

---

## Verification Plan

After implementing fixes, run these tests to verify:

```bash
# From C:\development\opencode:

# Test 1: Concurrent queries (was failing with race condition)
python scripts/utils/osgrep_debug_wrapper.py --label verify-tc01 --timeout 30 --cwd C:/development/opencode -- -- search "auth token refresh"

# Test 2: Another concurrent scenario  
python scripts/utils/osgrep_debug_wrapper.py --label verify-tc02 --timeout 30 --cwd C:/development/opencode -- -- search "feature flag"

# Test 3: Large repo query (was showing FTS warning)
python scripts/utils/osgrep_debug_wrapper.py --label verify-tc04 --timeout 30 --cwd C:/development/opencode -- -- search "conductor track"

# Test 4: Known-answer test (verify search quality)
python scripts/utils/osgrep_debug_wrapper.py --label verify-tc10 --timeout 30 --cwd "C:/development/opencode/osgrep path repro" -- -- search "refreshAuthToken"
```

**Success Criteria**:
- All 4 tests PASS
- No "Table 'chunks' already exists" errors
- No FTS inverted-index warnings
- TC-11 behavior is deterministic

---

## Next Steps

1. **Apply Fix #1** (5 minutes): Add `existOk: true` to vector-db.js
2. **Apply Fix #2** (15 minutes): Add file existence validation to searcher.js  
3. **Apply Fix #3** (optional, 20 minutes): Enhance FTS validation
4. **Run verification tests** (10 minutes): Confirm all tests pass
5. **Update parent track** (10 minutes): Mark TC-01..TC-05 as PASS, update go-no-go.md to GO

**Total estimated time**: ~1 hour

---

## Conductor Track Files

- **Spec**: `.conductor/tracks/20260313-osgrep-stabilization/spec.md`
- **Plan**: `.conductor/tracks/20260313-osgrep-stabilization/plan.md`
- **Metadata**: `.conductor/tracks/20260313-osgrep-stabilization/metadata.json`

---

## Technical Details

### LanceDB Version Confirmed
- osgrep uses `@lancedb/lancedb@^0.22.3`
- `existOk` option confirmed present in `connection.js` lines 144-146
- Mode is translated to `"exist_ok"` internally

### Search Flow Confirmed
1. `searcher.search()` calls `this.db.ensureTable()` (line 306)
2. First search triggers lazy FTS index creation (lines 312-319)
3. Vector search + FTS search run in parallel
4. Results merged via Reciprocal Rank Fusion
5. Results mapped via `mapRecordToChunk()` (line 22+)

### Race Condition Confirmed
The `ensureTable()` pattern (openTable → catch → createTable) is a classic TOCTOU race condition. Multiple concurrent calls to `ensureTable()` during concurrent searches can all fail `openTable`, then all try `createTable`, causing the error.

---

## Decision: GO/NO-GO

**Current Status**: NO-GO (pending fixes)

**Path to GO**: 
1. Apply Fix #1 (existOk: true) - this alone should resolve TC-01, TC-02
2. Re-run TC-01 through TC-05
3. If 5/5 pass → **GO for CLI-only re-enablement**

Fixes #2 and #3 are optimizations that improve quality but aren't blockers for the GO decision.

---

## Reference Commands

```bash
# Check osgrep version
cat %APPDATA%/npm/node_modules/osgrep/package.json | grep version

# Check LanceDB existOk support
grep -n "existOk" %APPDATA%/npm/node_modules/osgrep/node_modules/@lancedb/lancedb/dist/connection.js

# Backup original files
cp %APPDATA%/npm/node_modules/osgrep/dist/lib/store/vector-db.js %APPDATA%/npm/node_modules/osgrep/dist/lib/store/vector-db.js.bak
cp %APPDATA%/npm/node_modules/osgrep/dist/lib/search/searcher.js %APPDATA%/npm/node_modules/osgrep/dist/lib/search/searcher.js.bak

# Reset osgrep index (if needed for clean test)
osgrep index --reset
cd C:/development/opencode && osgrep index
```

---

## One-Line Summary

Race condition fix is trivial (`existOk: true`), fixes #2 and #3 are enhancements; implement Fix #1, re-run TC-01..TC-05, and GO decision should be achievable within 1 hour.
