# Maintenance Workflow

This document defines the full 8-phase maintenance lifecycle for the knowledge graph.
Follow these phases in order during each maintenance cycle.

## Phase 1: Baseline Health Check

Run the graph validation and indexing tools to establish a health baseline.

```powershell
# Validate graph structure (frontmatter, links, orphans)
python scripts\validate-kg.py

# Build or rebuild the search index
python scripts\build-index.py
```

Review the output for:
- Total entity counts by type (people, organizations, programs, decisions, risks)
- Number of broken wikilinks
- Number of orphan nodes (no incoming or outgoing links)
- Number of nodes missing required frontmatter fields

Record these metrics in the maintenance audit report. Compare against prior cycle
metrics if available to track trends.

Exit criteria: validation script completes without crashes, index build succeeds.

## Phase 2: Provenance Audit

Examine source citations across the graph. See `provenance-audit.md` for full details.

Key actions:
1. Find nodes with empty or missing `sources` frontmatter fields.
2. Find relationships described in the body but not backed by `[[source-...]]` links.
3. Find time-sensitive claims (budgets, personnel, program status) that lack `as_of` dates.
4. Flag high-impact claims with weak or missing provenance for the review queue.

Exit criteria: all nodes have been checked for source citations; weak-provenance items
have been added to the review queue.

## Phase 3: Gap Detection

Identify missing entity pages, missing relationships, and thin nodes.
See `gap-detection.md` for full details.

Key actions:
1. Scan all wikilinks in the graph for targets that do not resolve to files.
2. Check for entity types mentioned in text but not represented as nodes.
3. Identify nodes with fewer than 3 relationships as potentially thin.
4. Generate missing page candidates with evidence from existing references.

Exit criteria: all broken wikilinks cataloged; missing page candidates listed; thin
nodes identified.

## Phase 4: Contradiction Detection

Find conflicting claims across sources and confidence levels.
See `contradiction-detection.md` for full details.

Key actions:
1. For each entity with multiple sources, compare key claims (owner, status, dates).
2. Flag claims where sources disagree on factual content.
3. Check for identity conflicts (same person/org referenced under different names).
4. Generate contradiction queue items with Claim A / Claim B format.

Exit criteria: all multi-source entities checked; contradictions cataloged with evidence.

## Phase 5: Active Synthesis

Propose new wiki pages, concept pages, or domain summaries based on patterns found
in the graph. See `active-synthesis.md` for full details.

Key actions:
1. Identify clusters of entities that share a domain but lack a unifying concept page.
2. Find acronyms or terms referenced by 3+ entities without their own definition page.
3. Suggest merge candidates (duplicate entities) or split candidates (overloaded entities).
4. Draft proposed page outlines with supporting entity links.

Exit criteria: synthesis proposals listed with supporting evidence; no automatic creation.

## Phase 6: Research or Human Escalation

Decide how to resolve each issue found in phases 2-5.
See `human-escalation.md` and `web-research-for-gaps.md` for full details.

Decision tree:
- **Public fact with clear gap** and no sensitive implications: web research allowed.
  Follow citation requirements in `web-research-for-gaps.md`.
- **Internal fact** (personnel, org structure, program details): ask the user.
  Follow question guidelines in `human-escalation.md`.
- **Ambiguous identity**: always ask the user. Never merge without confirmation.
- **Sensitive fact** (budget, restructuring, classified): always defer to user.

Exit criteria: each issue has a resolution path (research, ask user, or defer).

## Phase 7: Proposed Updates

Compile all findings into a proposed patch plan. This is a **read-only output**; the
maintainer skill does not automatically apply changes.

The proposed patch plan should include:
- List of new entity files to create (with frontmatter templates and source evidence).
- List of existing files to edit (with specific field changes and source evidence).
- List of review queue items that require user decisions before any action.
- List of deferred items (insufficient evidence, awaiting external input).

Present the patch plan to the user for review before any changes are applied.

Exit criteria: patch plan compiled and presented to the user.

## Phase 8: Validation After Approved Changes

After the user approves and changes are applied, re-run validation:

```powershell
# Re-validate the graph
python scripts\validate-kg.py

# Rebuild the search index
python scripts\build-index.py
```

Confirm:
- No new broken wikilinks were introduced.
- No new orphan nodes were created.
- All new files pass schema validation.
- The review queue has been updated (resolved items closed, new items added).

Exit criteria: validation passes; maintenance audit report updated with final metrics.

## Error Recovery

- If `validate-kg.py` crashes: check the script output for the failing file, fix the
  malformed markdown or YAML, and re-run.
- If `build-index.py` fails: ensure all markdown files have valid UTF-8 encoding and
  that no files are locked by another process.
- If a phase produces no findings: this is a valid result. Record "no issues found"
  in the audit report and proceed to the next phase.
- If the user cannot answer a question: defer the item to the review queue with a
  `status: deferred` annotation and move on.
