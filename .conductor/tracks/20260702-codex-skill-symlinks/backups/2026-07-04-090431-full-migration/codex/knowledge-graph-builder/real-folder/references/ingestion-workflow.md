# Ingestion Workflow

This document defines the end-to-end ingestion lifecycle for converting raw source material into knowledge graph entity notes. Follow this workflow in order for every source processed.

## Preconditions

Before starting ingestion, verify:

1. **Repo root exists:** `C:\development\02-Kx-to-process`
2. **Knowledge base root exists:** `C:\development\02-Kx-to-process\knowledge-base`
3. **Source file is accessible** at the provided path (inbox, planning folder, or direct path).
4. **No existing source node** for this file exists in `knowledge-base/sources/`. If one exists with `extraction_status: complete`, see `incremental-ingest.md` before reprocessing.
5. **Python environment** has access to `scripts/` commands.

Verify with:
```powershell
Test-Path -LiteralPath "C:\development\02-Kx-to-process"
Test-Path -LiteralPath "C:\development\02-Kx-to-process\knowledge-base"
```

## Ordered Workflow

### Step 1: Intake Source
- Accept the source file path from the user or inbox scan.
- Record the source type (extension) and confirm readability.
- If the file is not in a readable format, consult `source-conversion.md`.

### Step 2: Convert to Readable Text
- Follow `source-conversion.md` for format-specific conversion.
- Output: plain text or markdown representation of the source content.

### Step 3: Check Source Identity
- Compute a content identifier (SHA-256 of first 4096 characters is the current standard).
- Search existing source nodes for a match on `source_path` or content hash.
- If a match exists with `extraction_status: complete`, skip to `incremental-ingest.md`.

### Step 4: Extract Entities
- Follow `entity-extraction.md` for entity types, rules, and confidence levels.
- Output: a list of candidate entity notes and relationships.

### Step 5: Deduplicate and Merge
- Follow `deduplication-and-merge.md` to compare extracted entities against existing notes.
- Merge only when identity is certain. Flag ambiguous matches for review.

### Step 6: Create or Update Source Node
- Write a source note to `knowledge-base/sources/` with:
  - `id: source-{slug}`
  - `source_path`, `source_type`, `extraction_status: complete`
  - `sensitivity` and `contains_pii` flags
  - `source_for::` links to all extracted entities

### Step 7: Write Entity Notes
- Write one `.md` file per entity in the appropriate `knowledge-base/{type}/` folder.
- Set `review_status: needs_review` on all new notes.
- Include `sources:` referencing the source node in frontmatter.
- Every relationship must include `source:`, `confidence:`, and `as_of:` when time-sensitive.

### Step 8: Validate and Rebuild Index
- Run validation and index rebuild:
```powershell
python scripts\validate-kg.py
python scripts\build-index.py
```
- See `post-ingest-validation.md` for full validation details.

### Step 9: Archive and Log
- Move or record the processed source per folder lifecycle in `archiving-and-logging.md`.
- Append an ingest log entry.

### Step 10: Hand Off Unresolved Items
- If contradictions, gaps, or ambiguous identities remain, create review items for `knowledge-graph-maintainer`.
- See Phase 5 of the builder SKILL.md for handoff criteria.

## Ingestion Decision Tree

```
Source arrives
  |
  Is it readable? -- No --> See source-conversion.md
  |
  Yes
  |
  Does a source node already exist? -- Yes --> See incremental-ingest.md
  |
  No
  |
  Extract entities (entity-extraction.md)
  |
  Deduplicate (deduplication-and-merge.md)
  |
  Write source node + entity notes
  |
  Validate + rebuild index (post-ingest-validation.md)
  |
  Archive + log (archiving-and-logging.md)
  |
  Any contradictions or gaps? -- Yes --> Hand off to knowledge-graph-maintainer
  |
  Done
```

## Handoff to Maintenance

After ingestion, route these items to `knowledge-graph-maintainer`:

- **Contradictory source claims:** Two sources assert different facts about the same entity.
- **Missing canonical entity pages:** Entities referenced but not yet created.
- **Low-confidence identity matches:** Entities that might be duplicates but cannot be confirmed.
- **Orphan nodes:** Nodes with no inbound or outbound relationships not caused by the current source.
- **Review queue aggregation:** Items requiring human review that exceed the builder scope.

Document handoff items in the ingest log with a `HANDOFF:` prefix.

## Error Recovery

| Error | Recovery |
|-------|----------|
| Source file not found | Confirm path with user; check `10 inbox` and `20 planning` folders |
| Conversion failure | See `source-conversion.md` failure section; try alternative tool |
| Validation shows FAIL | Fix schema errors before marking ingestion complete; re-run `validate-kg.py` |
| Index build fails | Check script dependencies; ensure Python can access `knowledge-base/` |
| Duplicate slug collision | Follow `deduplication-and-merge.md` merge rules; never overwrite without evidence |
| Permission denied writing notes | Check folder permissions; ensure `knowledge-base/{type}/` directories exist |
| Source node already exists with complete status | See `incremental-ingest.md` for change detection before reprocessing |
## Pre-Ingest File Existence Protocol (Guardrail A)

Before creating ANY new `.md` file in `knowledge-base/`:
1. Check if the target path already exists using `Test-Path` or `os.path.exists`.
2. If the file exists:
   - Read the existing file completely.
   - Compare the entity type, name, and key fields.
   - If the existing file describes the SAME entity (same name, same type, same meaning): MERGE new relationships/fields. Do NOT overwrite.
   - If the existing file describes a DIFFERENT entity with the same slug (homonym): Create a disambiguated filename (e.g., `acronym-sgs-tencap.md` vs `acronym-sgs-titan.md`) and cross-link them.
   - If the existing file describes a DIFFERENT meaning of the SAME acronym (polysemy): Merge BOTH definitions into the same file with clear section headers and distinct provenance.
3. NEVER overwrite an existing file without first backing it up to `60 archive/rollback-<timestamp>/`.

## Rollback Snapshot Creation (Guardrail B)

Immediately after Step 0 (source reading) and BEFORE Step 4 (write entity notes):
1. Create a timestamped rollback directory: `60 archive/rollback-<YYYYmmdd-HHMMSS>/`
2. Copy ALL existing files that might be touched during this ingestion into the rollback directory.
3. Maintain a manifest file inside the rollback dir listing: original path, backup path, action (create/merge/overwrite).

## Inventory Table Extraction Checklist (Guardrail D)

When a source contains inventory tables (programs, events, organizations, etc.):
1. Extract EVERY row as a candidate entity.
2. For each row, check if a dedicated note already exists.
3. If a note exists: append the inventory data (lifecycle stage, CPE assignment, budget, status) to the existing note.
4. If a note does NOT exist: create a new note. Do NOT skip with rationale like "already mentioned elsewhere."
5. Mark each row in a tracking checklist until all rows are accounted for.

## Concept Enrichment Trigger (Guardrail E)

After extracting all explicit entity types (people, orgs, programs, etc.):
1. Scan the source for mentions of concepts already existing in `knowledge-base/concepts/`.
2. For each concept found:
   - Read the existing concept note.
   - Append a new "Source Context" section with the relevant excerpt from the current source.
   - Add the source to the concept's `sources` list.
   - Update `last_updated`.
3. Common concepts to check: governance models, strategic principles, transformation concepts, data architectures.

## Completion Gate: Verify Todo List Empty (Guardrail F)

Before declaring ingestion complete:
1. Review the todo list created at the start of the session.
2. Verify EVERY item is marked `completed` or `cancelled` with a documented reason.
3. If any item is still `pending` or `in_progress`: either complete it, cancel it with justification, or hand it off to the maintainer skill with a `HANDOFF:` prefix in the ingest log.
4. Do NOT report success until this gate passes.

## Archive Destination Validation (Guardrail G)

Before declaring ingestion complete:
1. Verify the processed source was moved to 60 archive/ (repository root), NOT a subfolder inside 10 inbox/.
2. If 10 inbox/archive (or any archive-like subfolder) exists inside a working folder, flag it as an error.
3. Move any mis-archived files to the correct 60 archive/ location and remove the rogue subfolder.
4. Do NOT report success until the archive destination is correct.
