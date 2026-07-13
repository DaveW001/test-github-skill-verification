# Entity Extraction

This document defines supported entity types, extraction rules, relationship rules, confidence levels, and examples for the knowledge graph builder.

## Supported Entity Types

The knowledge graph currently supports 11 entity types, each stored in a dedicated folder:

| Type | Folder | Key Fields | Description |
|------|--------|------------|-------------|
| person | `people/` | name, rank_or_title, primary_org | Individuals mentioned in sources |
| organization | `organizations/` | parent_orgs, org_type | Units, agencies, companies, teams |
| program | `programs/` | status, lead_org | Named programs, projects, initiatives |
| role | `roles/` | held_by, within_org | Formal positions or job functions |
| acronym | `acronyms/` | expansion, context | Abbreviations and their expansions |
| event | `events/` | date, event_type | Meetings, exercises, milestones |
| source | `sources/` | source_path, source_type, extraction_status | Provenance records for ingested documents |
| concept | `concepts/` | domain | Ideas, frameworks, doctrines, technologies |
| decision | `decisions/` | decided_by, date_decided, status | Formal decisions and their outcomes |
| risk | `risks/` | severity, likelihood, mitigation_status | Identified risks and their context |
| action | `actions/` | assignee, due_date, status | Action items and follow-ups |

**Note:** The original schema defined 8 types. The `decision`, `risk`, and `action` types have been added to support the broader knowledge graph. If you encounter a `knowledge-base/` folder for an unlisted type, create entity notes there and flag for schema review.

## Extraction Rules

### General Rules

1. **One entity per note.** Never combine multiple entities in a single file.
2. **Slug format:** `{type}-{descriptive-slug}`. Use lowercase, hyphens for spaces, no special characters.
3. **Filename must match `id` field:** `person-jane-doe.md` has `id: person-jane-doe`.
4. **Default `review_status: needs_review`** for all machine-generated notes.
5. **Every relationship needs a source.** No orphan relationships.
6. **Extract only what the source says.** Do not infer facts not supported by source text.

### Per-Type Extraction Rules

#### Person
- Extract: full name, rank or title, organization affiliation.
- Do NOT extract: email addresses, phone numbers, physical addresses (PII rules).
- If only a last name is given and identity is ambiguous, create a stub note with `confidence: low` and flag for review.

#### Organization
- Extract: official name, abbreviation/acronym, parent organization, type (military, government, contractor, etc.).
- Record alternate names as `aliases`.
- Different sub-units of the same parent are separate entities.

#### Program
- Extract: official name, status (active, planned, completed, cancelled), lead organization.
- Include program acronym as an alias.

#### Role
- Extract: title of the role, who currently holds it, which organization it belongs to.
- A role is distinct from the person who holds it.

#### Acronym
- Extract: the abbreviation and its full expansion.
- Include context (domain or where it is used).
- If an acronym has multiple expansions, create separate entries with disambiguation in the slug.

#### Event
- Extract: event name, date, type (meeting, exercise, ceremony, etc.), location if stated.
- Participants link to person/organization nodes.

#### Decision
- Extract: what was decided, who decided it, when, current status.
- Link to supporting evidence or meeting notes via `source_for::`.

#### Risk
- Extract: risk description, severity (critical/high/medium/low), likelihood, mitigation status.
- Link to the program or organization affected.

#### Action
- Extract: action description, assignee, due date if stated, current status.
- Link to the meeting or source where the action was created.

## Relationship Rules

### Approved Predicates (17)

| Predicate | Meaning | Typical Source -> Target |
|-----------|---------|--------------------------|
| affiliated_with | General affiliation | person -> organization |
| reports_to | Hierarchical reporting | person -> person or role |
| works_with | Collaborative relationship | person -> person |
| member_of | Membership in a group/org | person -> organization |
| has_role | Person holds a role | person -> role |
| stakeholder_for | Interest or investment | person/org -> program |
| owns | Ownership or responsibility | org -> program |
| supports | Provides support to | org/person -> program |
| attended | Presence at event | person -> event |
| interviewed_for | Interview connection | person -> event/program |
| mentioned_in | Referenced in a source | entity -> source |
| source_for | Source documents entity | source -> entity |
| part_of | Subordinate containment | org -> org, event -> event |
| depends_on | Dependency relationship | program -> program |
| related_acronym | Acronym association | acronym -> entity |
| illustrates | Exemplifies a concept | entity -> concept |
| constrains | Imposes a constraint | decision/risk -> entity |

### Relationship Format

Every relationship must include provenance metadata:

```
predicate:: [[target-entity-id]]
- source: [[source-node-id]]
- confidence: high|medium|low
- as_of: YYYY-MM-DD
```

Example:
```
affiliated_with:: [[organization-1st-infantry-division]]
- source: [[source-meeting-notes-2026-05-10]]
- confidence: high
- as_of: 2026-05-10
```

## Confidence Levels

| Level | When to Use |
|-------|-------------|
| **high** | Source explicitly names the entity and relationship. No ambiguity. |
| **medium** | Entity is identifiable but relationship or details are inferred from context. |
| **low** | Entity identity is uncertain (partial name, possible homonym). Flag for review. |

Rules:
- Default to `medium` when unsure between `high` and `medium`.
- Never upgrade confidence without new source evidence.
- Low-confidence entities must have `review_status: needs_review`.

## Examples

### Person Note Example

```
---
id: person-john-smith
type: person
name: John Smith
aliases: [J. Smith, COL Smith]
rank_or_title: Colonel
primary_org: "[[organization-1st-infantry-division]]"
confidence: high
review_status: needs_review
last_updated: 2026-05-10
sources:
  - "[[source-meeting-notes-2026-05-10]]"
---

## Notes

Attendee of the C2 transformation planning session on 2026-05-10.

## Relationships

affiliated_with:: [[organization-1st-infantry-division]]
- source: [[source-meeting-notes-2026-05-10]]
- confidence: high
- as_of: 2026-05-10

stakeholder_for:: [[program-c2-modernization]]
- source: [[source-meeting-notes-2026-05-10]]
- confidence: medium
- as_of: 2026-05-10
```

### Decision Note Example

```
---
id: decision-migrate-to-cloud
type: decision
name: Migrate C2 Systems to Cloud
decided_by: "[[person-jane-commander]]"
date_decided: 2026-04-15
status: approved
confidence: high
review_status: needs_review
last_updated: 2026-05-10
sources:
  - "[[source-decision-memo-2026-04-15]]"
---

## Summary

Decision to migrate legacy C2 systems to cloud infrastructure by Q3 2026.

## Relationships

constrains:: [[program-c2-modernization]]
- source: [[source-decision-memo-2026-04-15]]
- confidence: high
- as_of: 2026-04-15
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| Cannot determine entity type | Use `concept` as default type and flag for review |
| Entity name is ambiguous (common name) | Include context in slug (e.g., person-j-smith-1st-id) and set confidence to low |
| Source contains no extractable entities | Create source node with `extraction_status: complete` and empty `source_for::` list; log as no entities found |
| Relationship predicate does not fit any approved predicate | Use `mentioned_in` as fallback and flag for schema review |
| Duplicate entity created before dedup check | Run `deduplication-and-merge.md` workflow; merge or flag as appropriate |