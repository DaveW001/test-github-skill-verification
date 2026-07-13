# Edit Safety for Structured Files

This reference documents safety rules for editing knowledge graph artifacts with repeating
structural patterns — review queues, audit reports, indexes, and ledgers.

## The Problem: Pattern Collision in `oldString` Edits

When a file contains multiple items with identical structural endings (e.g., a review queue
with 10 items each ending with `- **status:** open\n- **created:** 2026-05-15`), the
`oldString` parameter in the edit tool matches the **first** occurrence in the file, not
necessarily the intended target. This silently misassigns changes to wrong items.

**Real case (2026-05-17):** The review queue `review-queue-2026-05-15.md` had 10 items.
Edits intended for items #7–#10 were silently applied to items #3–#6 because the pattern
`- **status:** open\n- **created:** 2026-05-15` matched the earliest occurrence in the file.
Result: 6/10 items had wrong resolution texts, 2 resolved items remained `open`, and
2 items were entirely missing. This was only caught during a manual closeout validation.

## Safety Rules

### Rule 1: Unique Anchoring

When editing a file with 3+ items sharing a structural pattern, always use surrounding
context that is **unique to that item**. Do not rely on the item's ending pattern alone.

**Unsafe (shared ending):**
```
oldString: "- **status:** open\n- **created:** 2026-05-15\n\n### review-2026-05-15-next-item"
```
This will match the first occurrence of `status: open` anywhere in the file.

**Safe (unique anchor):**
```
oldString: "### review-2026-05-15-ash-dharia-null-title\n- **type:** schema_issue\n...content..."
```
Anchor on the item's header (`### review-...`) which is guaranteed unique.

### Rule 2: Rewrite for Bulk Status Changes

When changing >25% of items in a structured file (3+ items in a 10-item file), rewrite the
**entire file** from a known-correct template rather than making individual edits. This
eliminates pattern-collision risk entirely.

### Rule 3: Post-Edit Integrity Check

After any bulk edit to review queues, audit reports, or ledgers, run a manual verification:

```powershell
# Check status distribution matches expected
Select-String -Path "review-queue-*.md" -Pattern '^### review|^- \*\*status:\*\*' | ForEach-Object { $_.Line }

# Verify all resolved items have resolution text (not empty/boilerplate)
Select-String -Path "review-queue-*.md" -Pattern 'resolution' | ForEach-Object { $_.Line }

# Verify no orphan resolution texts (same text on different item types)
# Manual: read the file and confirm each resolution matches its item's type
```

### Rule 4: Atomic Item Boundaries

When adding `resolved_date` and `resolution` fields to an item, always place them
immediately after the item's last existing field and **before** the next item's header
(`### review-...`). Never insert fields that could be misread as belonging to the
next item.

## When to Apply

Activate these rules when working with:
- `knowledge-base/review-queue-*.md` (all dated review queues)
- `knowledge-base/maintenance-audit-*.md` (all dated audits)
- `.conductor/tracks.md` and `.conductor/tracks-ledger.md` (ledgers with repeating rows)
- Any file with 3+ items sharing identical structural endings

## Related

- `maintenance-workflow.md` — Phase 8 post-change validation
- `review-queue.md` — Review queue management best practices
- AGENTS.md `## Track Completion Verification` — closeout checklist
