# Gap Detection

This document defines how to detect missing entity pages, missing relationships,
incomplete metadata, and thin nodes in the knowledge graph.

## Missing Entity Pages

A missing entity page is identified when:

1. A `[[wikilink]]` target in the graph does not resolve to an existing file.
2. An entity name is referenced in plain text by 3 or more existing nodes but has no
   dedicated page.
3. An entity type is mentioned in `type:` cross-references but the target file does not
   exist in the expected folder.

Detection method:
```powershell
# Run validation to find broken wikilinks
python scripts\validate-kg.py

# Search for frequently mentioned terms that lack entity pages
python scripts\search.py "term that appears frequently"
```

For each missing entity:
- Record the number of references found.
- Identify the referencing files.
- Determine the entity type (person, org, program, decision, risk).
- Assess whether sufficient source evidence exists to create the page.

## Missing Relationship Coverage

Relationships are the wikilinks between entity files. Gaps exist when:

1. Two entities are clearly related (e.g., a person leads a program) but no wikilink
   connects them.
2. An entity has fewer than 3 relationships, suggesting incomplete coverage.
3. A relationship described in a source document is not reflected in the graph.

Detection method:
- For each entity file, count incoming and outgoing wikilinks.
- Flag entities with fewer than 3 total relationships as potentially under-connected.
- Cross-reference source documents against entity files to find uncaptured relationships.

## Missing Owners, Dates, and Statuses

Certain metadata fields are critical for graph utility:

| Field | When Missing | Impact |
|-------|-------------|--------|
| Program owner | No `leads` or `owns` relationship | Cannot trace accountability |
| `as_of` date on time-sensitive claims | No temporal anchor | Cannot assess recency |
| `status` field | No lifecycle state | Cannot filter active vs. inactive |
| `sources` list | No provenance | Cannot verify claim origin |

Detection method:
- Scan all program files for owner references.
- Scan all files with time-sensitive content (budgets, personnel, dates) for `as_of`.
- Flag any file missing a `sources` field.

## Orphan and Thin Nodes

**Orphan nodes** have zero incoming and zero outgoing wikilinks.
**Thin nodes** have content but fewer than 3 relationships.

For each orphan or thin node:
1. Search for the entity name in other files using `python scripts\search.py "entity name"`.
2. If the name appears in other files, the fix is to add `[[wikilink]]` syntax.
3. If the entity is genuinely isolated, assess whether it should be connected to the
   graph or marked for archival.

## Missing Page Candidate Template

When a missing entity page is identified, use this template to create a candidate:

```markdown
## Missing Page Candidate: [ENTITY NAME]

- **Suggested filename:** `<type>-<short-name>.md`
- **Suggested folder:** `knowledge-base/<type>s/`
- **Evidence:** [Number] existing entities reference this name.
- **Referenced by:** [[source-file-1]], [[source-file-2]], ...
- **Current page status:** No file found at the suggested path.
- **Suggested action:** Create `<type>-<short-name>.md` if source evidence includes
  sufficient detail; otherwise create review queue item for user to provide information.
- **Human gate:** Ask user before creating if sources do not clearly define the entity
  or if the entity type is ambiguous.
```

### Example: Missing Page Candidate for JADC2

```markdown
## Missing Page Candidate: JADC2

- **Suggested filename:** `acronym-jadc2.md` or `concept-jadc2.md`
- **Suggested folder:** `knowledge-base/programs/` (if a program) or a new `concepts/` folder
- **Evidence:** 3 decisions and 2 risks mention `JADC2`.
- **Referenced by:** [[decision-jadc2-integration-01]], [[decision-jadc2-integration-02]],
  [[decision-jadc2-integration-03]], [[risk-jadc2-gap-01]], [[risk-jadc2-gap-02]]
- **Current page status:** No `acronym-jadc2.md` or `concept-jadc2.md` found.
- **Suggested action:** Create `acronym-jadc2.md` if source evidence includes expansion;
  otherwise create review queue item.
- **Human gate:** Ask user before creating if sources do not clearly define expansion.
```

## Error Recovery

- If a wikilink target could refer to multiple entities (e.g., "Smith" could be multiple
  people), do not guess. Add to the review queue with an ambiguity note.
- If an entity appears to be missing but exists under an alternative name or alias, update
  the referencing files to use the canonical wikilink.
- If gap detection finds more than 20 missing pages in a single cycle, note this in the
  audit report and suggest a dedicated ingestion track rather than inline creation.
