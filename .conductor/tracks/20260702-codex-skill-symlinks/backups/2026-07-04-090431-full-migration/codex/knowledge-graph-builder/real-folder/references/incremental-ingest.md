# Incremental Ingest

This document defines how to handle re-processing of sources that have already been ingested, and how to perform incremental updates without reprocessing the entire corpus.

## When to Use

Use incremental ingest when:
- A source file has been **materially changed** since the last extraction.
- New metadata or corrections need to be applied to existing entities.
- The user explicitly requests re-processing of a previously ingested source.

Do NOT use incremental ingest when:
- This is a **new source** with no existing source node (use full ingestion workflow).
- The source has not changed and no updates are needed (skip entirely).

## Change Detection

Determine whether a source has changed using these methods in priority order:

### 1. Content Hash Comparison
Compare the SHA-256 hash of the first 4096 characters of the file against the `content_hash` stored in the source node.

```powershell
# Compute hash of current file
$hash = Get-FileHash -LiteralPath "C:\path\to\file.docx" -Algorithm SHA256
# Compare with stored hash in source node
Select-String -LiteralPath "C:\development\02-Kx-to-process\knowledge-base\sources\source-slug.md" -Pattern "content_hash"
```

If hashes match: no change detected. Skip processing unless forced.

### 2. Source Node Coverage Check
Review the existing source node's `source_for::` links to see if all entities from the source have been extracted.

```powershell
# Check what entities have been extracted from this source
Select-String -LiteralPath "C:\development\02-Kx-to-process\knowledge-base\sources\source-slug.md" -Pattern "source_for::"
```

### 3. File Modification Date
As a fallback, compare the file's last modified date against the source node's `last_updated` date.

```powershell
$fileDate = (Get-Item "C:\path\to\file.docx").LastWriteTime
# Compare with last_updated in source node
```

### 4. Manual Override
If the user explicitly states the source has changed, proceed with incremental ingest regardless of hash/date comparison.

## Affected Node Update Rules

When a source has materially changed:

1. **Re-read the source** and extract entities using `entity-extraction.md`.
2. **Compare extracted entities** against existing entities linked to this source:
   - **New entities:** Create new notes (standard workflow).
   - **Changed entities:** Update only the fields that differ. Preserve existing relationships from other sources.
   - **Removed entities:** Do NOT delete entity notes. Flag for review if the source no longer supports a relationship.
3. **Update the source node:**
   - Update `content_hash` to the new hash.
   - Update `last_updated` to current date.
   - Update `source_for::` links to reflect current extraction.
4. **Update affected entity notes:**
   - Add new relationships with new provenance.
   - Update changed fields (e.g., rank, title) with new `as_of` date.
   - Do not remove old relationships; add new ones alongside.
5. **Run validation:**
```powershell
python scripts\validate-kg.py
python scripts\build-index.py
```

## Skip Rules

Do NOT reprocess a source if:

1. **Content hash is unchanged** and no manual override was given.
2. **Source node has `extraction_status: complete`** and no changes detected.
3. **The user did not explicitly request re-processing.**
4. **The source file no longer exists** at the recorded path (log as missing, do not delete source node).

When skipping, log the decision:
```
## YYYY-MM-DD - Source Slug - SKIP

- Reason: Content hash unchanged
- Hash: a1b2c3d4...
- Source node: [[source-slug]]
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| Source file not found at recorded path | Log as missing; do not delete source node; flag for maintainer review |
| Content hash mismatch but file appears identical | Check encoding; recompute hash using UTF-8 normalized content |
| Entity note deleted since last extraction | Create a new entity note; do not attempt to restore the old one |
| Validation fails after incremental update | Revert entity note changes (restore from backup); investigate the failure |
| Merge conflict between old and new data | Preserve both versions with different `as_of` dates; flag for review |
| Partial extraction (source too large to fully process) | Set `extraction_status: partial`; log what was completed; continue with available entities |


## Detecting New Sources from External Systems

The change detection methods above assume the source file already exists on disk. For sources that live in external systems (NotebookLM notebooks, Google Drive folders, Outlook mailboxes), use the two-tier strategy in **`references/external-source-delta-detection.md`**:

1. **Tier 1 (quick):** Check notebook/folder-level counts against a baseline.
2. **Tier 2 (full delta):** Enumerate individual sources and diff against a persisted snapshot.
3. **Ingest new sources** using the standard workflow (`ingestion-workflow.md`).

This is the recommended starting point for every ingestion cycle when external sources are involved.

### Recommended Practices

- **Always back up affected entity notes** before modifying them during incremental ingest.
- **Log every incremental action** in the ingest log with an `INCREMENTAL:` prefix.
- **Prefer source node/path/date comparison** over content hashing when hashing is not implemented in existing metadata.
- **Process only new or materially changed sources.** Do not reprocess the entire corpus by default.
