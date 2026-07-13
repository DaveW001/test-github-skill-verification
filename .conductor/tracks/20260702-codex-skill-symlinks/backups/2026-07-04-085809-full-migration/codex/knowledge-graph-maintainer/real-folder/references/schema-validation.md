# Schema Validation

This document defines the schema validation rules for knowledge graph entity files.
Every entity file must conform to these rules regardless of entity type.

## Required Frontmatter Checks

Every entity file must include these frontmatter fields:

```yaml
---
id: <type>-<short-name>
type: person | organization | program | decision | risk
title: Human-readable title
confidence: high | medium | low
sources:
  - "[[source-<name>]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Validation checks:
1. `id` must match the filename (without `.md` extension).
2. `type` must be one of the five allowed values.
3. `title` must be non-empty and human-readable.
4. `confidence` must be one of `high`, `medium`, or `low`.
5. `sources` must be a non-empty list with at least one `[[source-...]]` reference.
6. `created` and `updated` must be valid ISO dates (YYYY-MM-DD).

Additional optional fields (not required but validated if present):
- `aliases` - list of alternative names or spellings.
- `status` - current status (active, inactive, deprecated, draft).
- `as_of` - date when time-sensitive information was last verified.
- `review_status` - one of `draft`, `reviewed`, `canon`, `deprecated`.

## ID and Filename Checks

1. Filename must follow the pattern `<type>-<short-name>.md` where `<type>` matches
   the frontmatter `type` field.
2. Filename must be lowercase with hyphens (no spaces, underscores, or mixed case).
3. File must reside in the correct subfolder: `people/`, `organizations/`, `programs/`,
   `decisions/`, or `risks/`.
4. `id` in frontmatter must exactly match the filename stem (without `.md`).

Common violations:
- `id: person-JohnDoe` but filename is `person-john-doe.md` (mismatch).
- File in `people/` but `type: organization` (type-folder mismatch).
- Spaces in filename: `person-John Doe.md` (use hyphens instead).

## Predicate Checks

Relationships in the body text are expressed using wikilinks with descriptive context.
The following predicates (relationship types) are recognized:

| Predicate | Example Usage | Required Context |
|-----------|--------------|-----------------|
| reports_to | `Reports to [[person-jane-doe]]` | Both entities must exist |
| leads | `Leads [[program-example]]` | Both entities must exist |
| owns | `Program owner: [[person-alpha]]` | Both entities must exist |
| member_of | `Member of [[org-example-team]]` | Both entities must exist |
| participates_in | `Participates in [[program-example]]` | Both entities must exist |
| influences | `Influences [[decision-example]]` | Both entities must exist |
| depends_on | `Depends on [[program-example]]` | Both entities must exist |
| mitigates | `Mitigates [[risk-example]]` | Both entities must exist |
| creates | `Creates [[risk-example]]` | Both entities must exist |
| escalates | `Escalates to [[person-alpha]]` | Both entities must exist |
| superseded_by | `Superseded by [[program-new-example]]` | Both entities must exist |
| source_for | `Source for [[decision-example]]` | Source entity must exist |
| related_to | `Related to [[org-example]]` | Both entities must exist |
| located_at | `Located at [[org-example-location]]` | Both entities must exist |

Validation checks:
1. Every `[[wikilink]]` target must resolve to an existing file in the knowledge base.
2. Relationship descriptions should use one of the recognized predicates.
3. Unrecognized predicates should be flagged for review but not cause validation failure.

## Review Status Checks

If `review_status` is present in frontmatter:

1. Must be one of: `draft`, `reviewed`, `canon`, `deprecated`.
2. `canon` status requires `confidence: high` and at least two independent sources.
3. `deprecated` status should include a `superseded_by` reference in the body.
4. `draft` status should be flagged for review during maintenance cycles.

## Failure Recovery

If validation shows new `FAIL` results, do **not** mark the maintenance cycle as complete.
Instead:

1. Record each failure with the file path and specific rule violated.
2. Categorize failures:
   - **Auto-fixable**: typos, missing dates, ID-filename mismatches (propose fix in patch plan).
   - **Needs source**: missing sources, low confidence (add to review queue).
   - **Needs decision**: type conflicts, ambiguous identities (add to review queue).
   - **Infrastructure**: broken script, missing folder (report in audit notes).
3. Add all auto-fixable items to the proposed patch plan for user approval.
4. Add all needs-source and needs-decision items to the review queue.
5. Re-run validation after fixes are applied to confirm all failures are resolved.
