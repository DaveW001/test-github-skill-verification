# Provenance Rules

This document defines how to record provenance for source nodes, entity relationships, time-sensitive claims, and PII. Provenance is the foundation of trust in the knowledge graph.

## Source Notes

Every ingested source must have a source node in `knowledge-base/sources/`. The source node is the primary provenance record.

### Required Frontmatter

```
---
id: source-{slug}
type: source
name: Human-Readable Source Name
source_path: "C:\development\02-Kx-to-process\10 inbox\filename.ext"
source_type: docx|pdf|md|txt|eml|json|other
content_hash: sha256-of-first-4096-chars
extraction_status: complete|partial|failed
sensitivity: internal|confidential|public
contains_pii: true|false
confidence: high|medium|low
review_status: needs_review|reviewed|approved
last_updated: YYYY-MM-DD
sources: []
---
```

### Source Body

The body of the source note should contain:
1. A brief description of the source content.
2. `source_for::` wikilinks to every entity extracted from this source.

Example:
```
source_for:: [[person-john-smith]]
source_for:: [[organization-1st-infantry-division]]
source_for:: [[decision-migrate-to-cloud]]
```

## Relationship Provenance

Every relationship in an entity note must include provenance metadata. A relationship without provenance is invalid.

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `source` | Always | Wikilink to the source node that supports this relationship |
| `confidence` | Always | `high`, `medium`, or `low` |
| `as_of` | When time-sensitive | Date the relationship was recorded or the fact was true |

### Format

```
predicate:: [[target-entity-id]]
- source: [[source-node-id]]
- confidence: high|medium|low
- as_of: YYYY-MM-DD
```

### Examples

Entity relationship with provenance:
```
affiliated_with:: [[organization-1st-infantry-division]]
- source: [[source-meeting-notes-2026-05-10]]
- confidence: high
- as_of: 2026-05-10
```

Source-to-entity link:
```
source_for:: [[person-john-smith]]
```

### Rules

1. **Every relationship must have a `source` field.** No exceptions.
2. **`confidence` reflects the strength of evidence**, not the importance of the entity.
3. **`as_of` is required when:**
   - The relationship might change over time (roles, reporting structures).
   - The fact is time-bounded (event attendance, project status).
4. **`as_of` is optional when:**
   - The relationship is permanent or historical (person attended an event).
5. **Multiple sources for the same relationship:** Add each source as a separate line under the relationship.

## Time-Sensitive Claims

Some facts are true at a point in time but may change. Handle these carefully:

### Types of Time-Sensitive Claims

- **Current role:** "COL Smith is the commander of 1st Brigade" (may change).
- **Program status:** "Project Alpha is in Phase 2" (will progress).
- **Organizational structure:** "Team Beta reports to Division Gamma" (may reorganize).
- **Action items:** "Complete report by June 2026" (has a deadline).

### Handling Rules

1. Always include `as_of` date for time-sensitive claims.
2. When a new source contradicts an existing time-sensitive claim, do NOT overwrite. Instead:
   - Add the new claim with the new `as_of` date.
   - Retain the old claim with its original `as_of` date.
   - Flag the contradiction for `knowledge-graph-maintainer` review.
3. Never assume a time-sensitive claim is still current without a recent source.

## Privacy and PII

### What Constitutes PII

- Email addresses
- Phone numbers
- Physical addresses
- Date of birth
- Social security / ID numbers
- Personal financial information

### Rules

1. **Never copy raw PII** into entity notes. Instead, note that PII exists: `contains_pii: true`.
2. **Mark sensitive sources:** Set `sensitivity: confidential` when the source contains PII or classified information.
3. **Summarize, do not quote:** For sensitive content, write summaries rather than raw excerpts.
4. **Names are not PII** in this context (they are the primary identifiers), but handle them respectfully.
5. **Ask before including:** If uncertain whether information qualifies as PII, set `contains_pii: true` and flag for review.

## Examples

### Source Node Frontmatter

```
---
id: source-meeting-notes-2026-05-10
type: source
name: C2 Transformation Planning Meeting Notes
source_path: "C:\development\02-Kx-to-process\10 inbox\c2-planning-meeting-2026-05-10.docx"
source_type: docx
content_hash: a1b2c3d4e5f6...
extraction_status: complete
sensitivity: internal
contains_pii: false
confidence: high
review_status: needs_review
last_updated: 2026-05-10
sources: []
---
```

### Entity with Provenance

```
---
id: person-jane-doe
type: person
name: Jane Doe
aliases: [J. Doe, LTC Doe]
rank_or_title: Lieutenant Colonel
primary_org: "[[organization-futures-command]]"
confidence: high
review_status: needs_review
last_updated: 2026-05-10
sources:
  - "[[source-meeting-notes-2026-05-10]]"
---

## Relationships

has_role:: [[role-project-lead-c2-mod]]
- source: [[source-meeting-notes-2026-05-10]]
- confidence: high
- as_of: 2026-05-10

stakeholder_for:: [[program-c2-modernization]]
- source: [[source-meeting-notes-2026-05-10]]
- confidence: medium
- as_of: 2026-05-10
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| Source node missing for a relationship | Do not create the relationship; flag the entity for re-extraction from the correct source |
| `as_of` date is unknown | Use the source file date or ingestion date; note uncertainty in the relationship |
| Confidence level is unclear | Default to `medium`; never assume `high` without explicit source evidence |
| PII accidentally included in entity note | Remove the PII immediately; set `contains_pii: true`; log the incident |
| Multiple conflicting `as_of` dates for same fact | Preserve both dates with their respective sources; flag for maintainer contradiction review |