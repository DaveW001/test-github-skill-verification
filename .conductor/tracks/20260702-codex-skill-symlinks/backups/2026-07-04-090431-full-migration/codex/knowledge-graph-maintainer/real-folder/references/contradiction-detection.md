# Contradiction Detection

This document defines how to detect and catalog conflicting claims in the knowledge graph.

## Claim-Level Comparison

For each entity with multiple sources, compare key claims across those sources:

1. **Factual claims**: names, titles, roles, dates, locations, budgets.
2. **Relational claims**: who reports to whom, which org owns which program.
3. **Status claims**: active, inactive, deprecated, superseded.

Comparison process:
- Extract each distinct claim from every source for the entity.
- Normalize claim text (lowercase, strip whitespace, expand abbreviations).
- Group claims by topic (e.g., "program owner", "start date", "budget amount").
- Flag any group where sources disagree on the factual content.

## Source Recency and Confidence

When two sources disagree, use these rules to assess which is more likely authoritative:

| Factor | More Authoritative | Less Authoritative |
|--------|-------------------|-------------------|
| Date | Newer `as_of` date | Older `as_of` date |
| Source type | Official document, meeting notes | Third-party summary, informal message |
| Confidence | `high` | `medium` or `low` |
| Corroboration | Multiple independent sources agree | Single source |

These factors are **guidelines, not rules**. When in doubt, present both claims to the
user rather than automatically preferring one.

## Relationship Conflicts

A relationship conflict occurs when:

1. Source A says entity X `reports_to` entity Y, but Source B says entity X `reports_to`
   entity Z (where Y and Z are different entities).
2. Source A says entity X `leads` program P, but Source B says entity W `leads` program P.

For each conflict:
- Record both claims with full source citations.
- Assess whether the conflict represents a legitimate change over time (e.g., a
  leadership transition) or a genuine disagreement.
- If it is a time-based change, record both with appropriate `as_of` dates.
- If it is a genuine disagreement, create a contradiction queue item.

## Identity Conflicts

An identity conflict occurs when two entity files might refer to the same real-world
entity but have different names, IDs, or attributes.

Common causes:
- Alternative spellings or transliterations (e.g., "Mueller" vs. "Muller").
- Name changes (e.g., maiden name vs. married name).
- Abbreviations vs. full names (e.g., "DoD" vs. "Department of Defense").
- Organizational renaming (e.g., "ARDEC" vs. "DEVCOM-AC").

Detection method:
- Compare entity names using normalized forms (lowercase, no punctuation, no spaces).
- Check for shared attributes (same role, same org, same dates).
- Use `aliases` frontmatter to identify known alternative names.

Resolution rule: **Ambiguous identity merges require user confirmation or authoritative
source evidence. Never merge automatically based on similarity alone.**

## Contradiction Queue Template

When a contradiction is identified, use this template:

```markdown
## Contradiction: [TOPIC]

- **Claim A:** [Description of claim from source A]
  - Source: [[source-a]]
  - Confidence: [high/medium/low]
  - As-of: YYYY-MM-DD
- **Claim B:** [Description of claim from source B]
  - Source: [[source-b]]
  - Confidence: [high/medium/low]
  - As-of: YYYY-MM-DD
- **Initial assessment:** [Brief analysis of which claim is more likely correct and why]
- **Recommended next step:** [Ask user / Find authoritative source / Record as time-based change]
```

### Example: Program Owner Contradiction

```markdown
## Contradiction: Program Owner for Example Program

- **Claim A:** [[source-a]] says owner is [[person-alpha]], confidence high, as_of 2026-04-01.
- **Claim B:** [[source-b]] says owner is [[person-beta]], confidence medium, as_of 2026-05-01.
- **Initial assessment:** Newer source may supersede older source, but role transition is
  not explicit.
- **Recommended next step:** Ask user or find authoritative source before updating
  canonical owner.
```

## Human Gate Rules

Contradictions must **always** be presented to the user for resolution when:

1. Both claims have `high` confidence from independent sources.
2. The contradiction involves a person's identity, role, or organizational affiliation.
3. The contradiction involves budget figures, program status, or other sensitive data.
4. The contradiction cannot be explained by a legitimate time-based change.
5. The resolution would require deleting or merging entity files.

The maintainer skill may propose a resolution but must not apply it without explicit
user approval.
