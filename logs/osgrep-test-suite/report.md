# osgrep Comprehensive Test Suite Report

**Track**: 20260531-osgrep-comprehensive-test-suite  
**Date**: 2026-05-31  
**osgrep Version**: 0.5.16  
**Repository**: C:\development\opencode (~538 files)  
**Mode**: CLI-only (canary)  

---

## Executive Summary

| Category | Total | PASS | FAIL | SKIP | WARN |
|----------|-------|------|------|------|------|
| **BLOCKING** | 14 | 14 | 0 | 0 | 0 |
| **NON-BLOCKING** | 33 | 31 | 0 | 1 | 1 |
| **TOTAL** | 47 | 45 | 0 | 1 | 1 |

**Overall Verdict: PASS** - All blocking tests passed.

---

## Performance Summary

| Operation | Typical Duration |
|-----------|-----------------|
| Version/Doctor | 0.5-1.7s |
| Full repo index | 120-140s |
| Scoped index | 1.9-2.1s |
| Search (warm) | 1.9-4.1s |
| Search with --sync | 6.8-14.2s |
| Symbols/Trace | 0.9-1.0s |
| Cold start search | 2.4s |

---

## Issues Found

1. TC-E3a: index --sync not valid (plan bug, not osgrep)
2. TC-E2: Query during indexing returns exit=1 (correct behavior)
3. TC-F2: Requires OpenCode session (SKIPPED in CLI-only)

## Bugs Fixed During Testing

1. UnicodeDecodeError: Added encoding=utf-8 to subprocess calls
2. Double -- stripping: Changed if to while loop

---

*Generated: 2026-05-31*