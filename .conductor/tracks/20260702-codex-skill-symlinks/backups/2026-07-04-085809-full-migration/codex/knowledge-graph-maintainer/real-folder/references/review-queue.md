# Review Queue

This document defines how to create, prioritize, and manage review queue items for the
knowledge graph. Review queues capture issues that require user attention before the
maintainer can proceed.

## When to Create Review Items

Create a review queue item whenever the maintainer encounters:

1. **Contradictions** between sources that cannot be automatically resolved.
2. **Ambiguous identities** where two entities might be the same but evidence is unclear.
3. **Low-confidence nodes** that need source verification.
4. **Provenance gaps** where important claims lack source citations.
5. **Schema violations** that require human judgment to fix.
6. **Sensitive information** that the user must approve before any change.
7. **Missing entity pages** where source evidence is insufficient to create automatically.

## Priority Rules

| Priority | Criteria | Example |
|----------|----------|---------|
| **high** | Affects multiple entities; involves sensitive data; blocks other maintenance work | Contradiction on program ownership affecting 5+ related entities |
| **medium** | Affects 1-3 entities; involves non-sensitive but unverified information | Missing provenance on a single decision node |
| **low** | Cosmetic or minor issue; no blocking impact; can be addressed in next cycle | Typo in entity title; orphan node with no clear connections |

Priority assignment rules:
- When in doubt, assign a higher priority rather than lower.
- Items involving personnel, organizational structure, or budgets are always at least
  `medium` priority.
- Items involving identity merges are always `high` priority.

## Review Queue Item Template

Each review queue item follows this format:

```markdown
- id: review-YYYY-MM-DD-<short-description>
  type: missing_entity | contradiction | low_confidence | provenance_gap | schema_issue | identity_merge | sensitive_change
  priority: high | medium | low
  affected_nodes:
    - [[entity-reference-1]]
    - [[entity-reference-2]]
  question_for_user: "<clear, specific question>"
  recommended_action: "<what the maintainer suggests doing>"
  evidence:
    - "<supporting evidence or source reference>"
  status: open | in_progress | resolved | deferred
  created: YYYY-MM-DD
```

### Example: Review Queue Item

```markdown
- id: review-2026-05-10-example
  type: contradiction
  priority: high
  affected_nodes:
    - [[program-example-program]]
  question_for_user: "Is Example Office the same organization as EXO?"
  recommended_action: "Do not merge until confirmed by user or authoritative source."
  evidence:
    - "Both names appear in [[source-meeting-notes-2026-04-10]] referring to similar functions"
    - "[[org-example-office]] and [[org-exo]] share 3 common program references"
  status: open
  created: 2026-05-10
```

## User Question Guidelines

When formulating questions for the user:

1. **Be specific.** Ask about one entity or one relationship at a time.
2. **Provide context.** Include the source evidence that created the uncertainty.
3. **Offer options.** When possible, present the user with clear choices rather than
   open-ended questions.
4. **State consequences.** Explain what will happen with each answer choice.
5. **Mark as optional.** If the question can be deferred without blocking other work,
   indicate that the user can skip it.

Example of a well-formed question:
> "Source A says [[person-alpha]] leads [[program-example]], but Source B says
> [[person-beta]] leads it. Both sources are high-confidence. Should we:
> (a) Record both with as_of dates as a leadership transition?
> (b) Keep only the newer source and flag the older one?
> (c) Defer until we find an authoritative confirmation?"

Example of a poorly-formed question:
> "Who is in charge?" (too vague, no context, no options)

## Closing Review Items

A review item can be closed when:

1. **Resolved by user:** The user has provided an answer. Apply the resolution and mark
   as `status: resolved`.
2. **Resolved by source:** A new authoritative source has been found that resolves the
   issue without user input. Document the source and mark as `status: resolved`.
3. **Deferred:** The user has explicitly chosen not to address the item now. Mark as
   `status: deferred` and include a note about when to revisit.
4. **Superseded:** The issue has been made irrelevant by other changes (e.g., a merged
   entity was deleted). Mark as `status: resolved` with a note explaining why.

Closed items should remain in the review queue file for audit trail purposes.

## Error Recovery

- If the review queue grows beyond 30 items in a single cycle, stop creating new items
  and report to the user that the queue is large. Recommend a prioritized subset.
- If a review item references an entity that has been deleted or renamed, update the
  affected_nodes list and reassess priority.
- If the user does not respond to a review item within 2 maintenance cycles, escalate
  the item to `high` priority or defer it with a note.


## Count and Regeneration Script
To count needs_review items and regenerate the status reports, use:
\\ash
python scripts/count-needs-review.py --json-out <json-path> --md-out <md-path>
\\n