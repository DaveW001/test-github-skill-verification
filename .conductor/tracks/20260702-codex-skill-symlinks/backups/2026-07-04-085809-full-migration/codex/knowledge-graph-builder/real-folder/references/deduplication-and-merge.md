# Deduplication and Merge Rules

This document defines how to detect and handle duplicate entities and sources during ingestion. Deduplication is critical for maintaining a clean, authoritative knowledge graph.

## Source Deduplication

Before processing any source, check whether it has already been ingested:

1. **Check by path:** Search `knowledge-base/sources/` for a source node with a matching `source_path`.
2. **Check by hash:** Compute SHA-256 of the first 4096 characters of the file content. Compare against `content_hash` fields in existing source nodes.
3. **Check by name:** If neither path nor hash matches, check for a source with a similar name.

```powershell
# Check for existing source by path
Get-ChildItem "C:\development\02-Kx-to-process\knowledge-base\sources" -Filter *.md | Select-String -Pattern "source_path.*YOUR_PATH"
```

If a source node exists with `extraction_status: complete`:
- Do NOT re-extract entities by default.
- See `incremental-ingest.md` if the source file has been materially updated.

## Entity Deduplication

After extracting entities from a source, compare each candidate against existing notes:

1. **Exact slug match:** `person-john-smith` already exists. This is a confirmed duplicate.
2. **Alias match:** An existing note has `aliases: [J. Smith, John Q. Smith]` that matches the extracted name.
3. **Fuzzy match:** The extracted name is similar but not identical (e.g., "John Smith" vs "Jon Smith"). This is ambiguous.
4. **Wikilink match:** The source text contains `[[person-john-smith]]` which directly references an existing node.

```powershell
# Check for existing entity by slug pattern
Get-ChildItem "C:\development\02-Kx-to-process\knowledge-base\people" -Filter "person-john-smith.md"
```

## Merge Rules

When a duplicate is confirmed (exact slug or alias match):

1. **Add new relationships only.** Do not overwrite existing frontmatter fields unless the new source provides more specific information.
2. **Append to `sources:` list.** Add the new source node ID to the entity's sources array.
3. **Update `last_updated:`** to the current date.
4. **Preserve existing `aliases`.** Merge alias lists (union, not replace).
5. **Add new relationship lines** with provenance (source, confidence, as_of).
6. **Do not change `review_status`** from `reviewed` or `approved` back to `needs_review` unless the merge introduces conflicting information.

Merge example:
```
# Existing entity has:
affiliated_with:: [[organization-alpha]]
- source: [[source-doc-1]]
- confidence: high
- as_of: 2026-04-01

# New source adds:
affiliated_with:: [[organization-bravo]]
- source: [[source-doc-2]]
- confidence: medium
- as_of: 2026-05-10

# Merged result has both relationships
```

## Do Not Merge Cases

**Never merge ambiguous identities.** The following cases must be flagged for review instead of merged:

1. **Same name, different context:** "John Smith" in a military context and "John Smith" in a contractor context could be different people.
2. **Partial name match:** "Smith" matches existing "John Smith" and "Jane Smith" -- do not merge with either.
3. **Rank/title discrepancy:** A source mentions "COL Smith" but existing note says "LTC Smith." The rank change may be a promotion or a different person.
4. **Organization mismatch:** Same name appears in two unrelated organizations without evidence they are the same person.
5. **Time gap without continuity:** Same name appears in sources 5+ years apart with no linking evidence.

When a merge is ambiguous:
1. Create the new entity as a separate note with `confidence: low`.
2. Add a `## Potential Duplicates` section listing the existing notes that might be the same entity.
3. Set `review_status: needs_review`.
4. **Never merge ambiguous identities** -- create a review item or ask the user.

## Verification Checklist

After deduplication and merge, verify:

- [ ] No duplicate slugs exist in the same entity type folder.
- [ ] All merged entities have updated `last_updated` dates.
- [ ] All merged entities reference the new source in `sources:`.
- [ ] No ambiguous merges were performed (all ambiguous cases flagged).
- [ ] `review_status` was not downgraded unless conflicting information was introduced.
- [ ] New relationships include provenance (source, confidence, as_of).

## Error Recovery

| Error | Recovery |
|-------|----------|
| Cannot determine if entities are duplicates | Create separate notes with low confidence; flag for review |
| Existing entity note is corrupted or empty | Do not merge; create new note and flag old one for maintainer review |
| Slug collision with unrelated entity | Add distinguishing suffix to slug (e.g., person-j-smith-2) and flag both for review |
| Aliases create circular references | Remove the circular alias; keep the canonical name as primary |