# Human Escalation

This document defines when and how the maintainer skill should escalate issues to the
user for resolution. Human escalation is the default for uncertain, sensitive, or
ambiguous situations.

## When to Ask the User

The maintainer **must** ask the user when:

1. **Identity ambiguity.** Two entity files might refer to the same person or organization
   but evidence is not conclusive.
2. **Contradiction resolution.** Two high-confidence sources disagree on a factual claim.
3. **Sensitive information.** The proposed change involves personnel, budgets, org charts,
   or other sensitive data.
4. **Insufficient evidence.** The maintainer cannot find enough source evidence to make
   a confident recommendation.
5. **Confidentiality concerns.** The information may be classified, FOUO, or otherwise
   restricted.
6. **Major structural changes.** The proposed change would create, delete, merge, or
   split entity files.
7. **User-specific knowledge required.** The question can only be answered by someone
   with direct knowledge of the situation (e.g., meeting participants, project leads).

The maintainer **should not** ask the user when:
1. The issue is cosmetic (typo, formatting).
2. The fix is clearly correct and well-sourced.
3. The information is publicly available and non-sensitive.
4. The user has previously answered the same question (check review queue history).

## How to Ask Targeted Questions

### Question Format

Each question should follow this structure:

1. **Context:** What entity or relationship is involved.
2. **Evidence:** What the sources say (with citations).
3. **Conflict or gap:** What is uncertain or missing.
4. **Options:** What the user can choose to do.
5. **Consequences:** What happens with each option.

### Example Questions

**Good question (specific, contextual, actionable):**
> The graph currently shows [[person-alpha]] as the owner of [[program-example]]
> (source: [[source-a]], as_of 2026-04-01). However, [[source-b]] (as_of 2026-05-01)
> lists [[person-beta]] as the owner. Should I:
> (a) Record a leadership transition with both dates?
> (b) Update to the newer source and note the change?
> (c) Leave unchanged until you confirm?

**Bad question (vague, no context, no options):**
> Who owns Example Program?

### Batch Questions

When multiple questions arise during a maintenance cycle, batch them into a structured
question list rather than asking one at a time:

```markdown
## Maintenance Questions - YYYY-MM-DD

### 1. Identity: Example Office vs. EXO
- **Type:** identity_merge
- **Priority:** high
- **Question:** Are "Example Office" and "EXO" the same organization?
- **Evidence:** Both share 3 program references and appear in [[source-meeting-2026-04-10]].

### 2. Provenance: Program Delta Budget
- **Type:** provenance_gap
- **Priority:** medium
- **Question:** Can you confirm the FY2026 budget figure for [[program-delta]]?
- **Evidence:** Currently cited from [[source-informal-email]] with low confidence.
```

## Sensitive Information Rules

When handling potentially sensitive information:

1. **Do not include sensitive details in review queue items** that might be shared or
   exported. Use generic descriptions instead.
2. **Do not search public web sources** for sensitive internal information.
3. **Do not automatically record sensitive claims** even if found in internal sources.
   Add to the review queue for user approval.
4. **Redact when escalating.** If a question involves specific names, amounts, or details
   that should not be in writing, ask the user verbally or in a secure channel.

## Deferral Rules

The user may choose to defer a question. When this happens:

1. Mark the review item as `status: deferred`.
2. Record the deferral reason if the user provides one.
3. Set a revisit date: defer for at most 2 maintenance cycles.
4. After 2 cycles, escalate the item to `high` priority or close it if no longer relevant.

Items that **cannot** be deferred:
- Identity merges affecting multiple entities.
- Contradictions on high-impact claims.
- Schema violations that cause validation failures.

## Examples

### Example 1: Ambiguous Identity Merge

```markdown
## Escalation: Identity Merge Required

- **Entity A:** [[org-example-office]] - "Example Office", 4 programs, 2 sources
- **Entity B:** [[org-exo]] - "EXO", 3 programs, 2 sources
- **Shared programs:** [[program-alpha]], [[program-beta]], [[program-gamma]]
- **Assessment:** Likely the same organization. "EXO" appears to be an abbreviation.
- **Risk of wrong merge:** Medium - could be distinct sub-organizations.
- **Rule:** Ambiguous identity merges require user confirmation or authoritative source
  evidence.
- **Question to user:** Are "Example Office" and "EXO" the same organization? If so,
  should we merge under the full name?
```

### Example 2: Missing Sensitive Information

```markdown
## Escalation: Sensitive Information Gap

- **Entity:** [[program-delta]]
- **Missing field:** Program owner
- **Assessment:** Source documents mention the program but do not clearly state ownership.
- **Sensitivity:** High - program ownership is an organizational decision.
- **Rule:** Do not automatically assign ownership from informal sources.
- **Question to user:** Who is the designated owner of Program Delta? Is this information
  appropriate to record in the knowledge base?
```
