# Post-Ingest Validation

This document defines the validation commands, expected results, smoke tests, and failure recovery procedures to run after every ingestion batch.

## Required Commands

After every ingestion run, execute these commands in order:

### 1. Schema Validation

```powershell
python scripts\validate-kg.py
```

This script checks:
- All entity notes have valid `type` values from the approved list.
- All entity `id` fields match their filename stems.
- All relationships use approved predicates.
- All relationships have `source:` references.
- No duplicate slugs exist within the same entity type.
- No raw contact data (email addresses, phone numbers) unless explicitly approved.

### 2. Index Rebuild

```powershell
python scripts\build-index.py
```

This script:
- Rebuilds the SQLite FTS5 full-text search index from all markdown notes.
- Regenerates `knowledge-base/indexes/graph-index.md` listing all nodes and edges.
- Must be run after any entity note changes to keep search current.

### 3. Search Smoke Test

```powershell
python scripts\search.py "C2 transformation"
```

This confirms the index is working and returns results. Replace the query with a term relevant to recently ingested content.

## Expected Validation Results

### validate-kg.py Output

The validation script reports results per check:
- `PASS` - Check passed. No action needed.
- `FAIL` - Check failed. Must be fixed before ingestion is marked complete.
- `WARN` - Warning. Should be reviewed but does not block completion.

Typical successful output:
```
Schema validation: PASS
ID-filename match: PASS
Predicate check: PASS
Source reference check: PASS
Duplicate slug check: PASS
PII scan: PASS
Summary: 6 PASS, 0 FAIL, 0 WARN
```

### build-index.py Output

Successful output:
```
Indexing knowledge-base/people/... done (N files)
Indexing knowledge-base/organizations/... done (N files)
Indexing knowledge-base/programs/... done (N files)
...
Index rebuild complete. Total entities: N
```

### search.py Output

Successful output returns matching entity notes with relevance scores.

## Search Smoke Tests

After rebuilding the index, run 2-3 queries to confirm search is functional:

```powershell
# Test 1: Generic query to confirm index returns results
python scripts\search.py "C2 transformation"

# Test 2: Entity-specific query
python scripts\search.py "organization"

# Test 3: Recent content query (use a term from the source just ingested)
python scripts\search.py "TERM_FROM_INGESTED_SOURCE"
```

Expected: Each query returns at least one result. If a query returns zero results, the index may be corrupted or the search term may be too specific.

## Failure Recovery

### If validation shows FAIL

1. **Do not mark ingestion as complete.** The ingestion is incomplete until all FAIL items are resolved.
2. **Review the specific failure message** to identify which entity note has the issue.
3. **Fix the issue:**
   - Missing `type`: Add the correct type field to the entity frontmatter.
   - `id`/filename mismatch: Rename the file or update the `id` field.
   - Invalid predicate: Replace with an approved predicate from the 17 approved list.
   - Missing `source` reference: Add the source node link to the relationship.
   - Duplicate slug: Rename one entity or merge following `deduplication-and-merge.md`.
   - PII detected: Remove raw PII and set `contains_pii: true`.
4. **Re-run validation:**
```powershell
python scripts\validate-kg.py
```
5. **Repeat** until all FAIL items are resolved.

### If index rebuild fails

1. Check that Python can access the `knowledge-base/` directory.
2. Verify no markdown files have encoding issues (BOM, non-UTF-8).
3. Check that `knowledge-base/indexes/` directory exists and is writable.
4. Delete the existing SQLite index file and retry.

### If search returns no results

1. Confirm the index was rebuilt successfully.
2. Try a broader query (single common word).
3. Check that entity notes have body text, not just frontmatter.
4. Verify the SQLite database file is not locked by another process.
## Mandatory Post-Ingest Validation Gate (Guardrail C)

Validation is NOT optional. After every ingestion:
1. Run `validate-kg.py` (or equivalent schema validator) against the entire `knowledge-base/`.
2. If the script path is unknown, search for it with `Get-ChildItem -Recurse -Filter "validate-kg.py"`.
3. Record the PASS / WARN / FAIL counts in the ingest log.
4. If any FAIL is found: do NOT archive the source. Fix the failures first, then re-run validation.
5. Only after 0 FAIL may the source be archived and the ingestion marked complete.
