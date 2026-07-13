# Provenance Audit

This document defines how to audit source citations and provenance across the knowledge
graph. Provenance tracking ensures that every claim in the graph can be traced back to
an authoritative source.

## Nodes Without Sources

Every entity file must have at least one entry in the `sources` frontmatter field.
Nodes without sources represent unverified claims.

Detection method:
```powershell
# Find files with empty or missing sources field
python scripts\validate-kg.py
# Review output for "missing sources" warnings
```

For each node without sources:
1. Check whether the information came from a source document that was not cited.
2. Search for the entity name in known source documents.
3. If a source is found, add it to the `sources` field.
4. If no source is found, add the node to the review queue as a provenance gap.

## Relationships Without Source References

A relationship described in entity body text (e.g., "Reports to [[person-jane-doe]]")
should be backed by at least one source. Relationships without source references are
unverified.

Detection method:
- For each wikilink in an entity file, check whether the surrounding text or the file's
  `sources` field provides evidence for the relationship.
- Flag relationships that appear to be asserted without any supporting citation.

Resolution:
- If the relationship is documented in a source but not cited, add the citation.
- If the relationship cannot be verified, add to the review queue.

## Time-Sensitive Claims Without as_of Dates

Claims that change over time (budgets, personnel assignments, program statuses,
organizational structures) must include an `as_of` date to indicate when the claim
was last verified.

Detection method:
- Scan entity files for time-sensitive keywords: budget, cost, funding, personnel,
  owner, leader, director, status, active, inactive.
- For each match, check whether an `as_of` date is present in the frontmatter or
  inline with the claim.

For each time-sensitive claim without an `as_of` date:
1. Attempt to determine when the information was last verified from source documents.
2. If the source date can be found, add `as_of: YYYY-MM-DD` to the claim.
3. If no date can be determined, add to the review queue for user clarification.

## Source Nodes Without source_for Links

Source entity files (those in the knowledge base that represent source documents) should
include `source_for` relationships indicating which entities they provide evidence for.

Detection method:
- List all source-type entities.
- For each, check whether the body text includes `source_for` or `Source for` references.
- Source nodes without any `source_for` links may be orphaned or underutilized.

Resolution:
- Search for entities that cite this source in their `sources` field.
- Add bidirectional `source_for` links where appropriate.

## High-Impact Weakly Sourced Claims

High-impact claims are those that could significantly affect decision-making:

- Program ownership or leadership.
- Budget figures or funding status.
- Organizational restructuring.
- Risk severity or likelihood assessments.
- Decision outcomes or action items.

High-impact claims without strong provenance (at least two independent sources with
`high` or `medium` confidence) should become review queue items, not automatic facts.

Detection method:
1. Identify all high-impact claims by keyword scanning.
2. For each, check the number and quality of supporting sources.
3. Flag any high-impact claim with fewer than 2 independent sources.

## Error Recovery

- If a source document referenced in `sources` does not exist in the knowledge base,
  note it as a broken source reference. Do not remove the citation; add to review queue.
- If `validate-kg.py` does not report provenance issues explicitly, use `search.py` to
  manually cross-reference entity content against known source files.
- If the number of provenance gaps exceeds 20 in a single cycle, recommend a dedicated
  provenance repair track rather than inline fixes.
