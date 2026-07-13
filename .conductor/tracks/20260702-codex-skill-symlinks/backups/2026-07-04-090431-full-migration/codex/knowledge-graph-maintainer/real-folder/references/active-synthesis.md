# Active Knowledge Synthesis

This document defines how the maintainer skill proposes new wiki pages, concept pages,
domain summaries, and merge/split suggestions based on patterns found in the graph.

## New Wiki Page Suggestions

A new wiki page should be suggested when:

1. Multiple entities reference a common concept, term, or domain that has no dedicated page.
2. A topic appears in 3 or more entity files as a wikilink target that does not resolve.
3. A domain cluster is identified (see "Community Detection" in
   `semantic-search-and-community-detection.md`) that would benefit from a unifying page.

Suggestion format:
```markdown
### Proposed Page: [TITLE]

- **Type:** concept | domain-summary | acronym | program-area
- **Suggested filename:** `<type>-<short-name>.md`
- **Evidence:** [List of entities that reference this topic]
- **Proposed content outline:**
  1. Definition or summary
  2. Related entities (wikilinks)
  3. Key decisions and risks
  4. Source citations
- **Source evidence:** [[source-1]], [[source-2]], ...
```

## Concept Page Suggestions

Concept pages serve as hubs for related entities. A concept page should be suggested when:

1. An acronym is used by 3+ entities without a definition page.
2. A technology, framework, or methodology is referenced across multiple programs.
3. A domain area (e.g., "5G integration", "command and control") spans multiple entity
   types (programs, decisions, risks).

Each concept page suggestion should include:
- The canonical term and any known aliases.
- A list of entities that would link to this page.
- An assessment of whether sufficient source evidence exists to write the page.

## Domain Summary Suggestions

Domain summaries provide an overview of a broad topic area. A domain summary should be
suggested when:

1. A domain has 5+ entity files across multiple types (people, orgs, programs, etc.).
2. The entities are interrelated but lack a single entry point for navigation.
3. A new user would benefit from a structured overview to understand the domain.

Domain summary structure:
```markdown
# [Domain Name] Summary

## Overview
[Brief description of the domain]

## Key Organizations
- [[org-1]] - [role in domain]
- [[org-2]] - [role in domain]

## Key Programs
- [[program-1]] - [status and relevance]
- [[program-2]] - [status and relevance]

## Key Decisions
- [[decision-1]] - [outcome]
- [[decision-2]] - [outcome]

## Key Risks
- [[risk-1]] - [severity and mitigation status]

## Open Questions
- [Question 1]
- [Question 2]
```

## Merge or Split Suggestions

**Merge suggestions** should be proposed when:
1. Two entity files refer to the same real-world entity (confirmed by source evidence).
2. An entity has been superseded and both the old and new versions exist as separate files.

**Split suggestions** should be proposed when:
1. A single entity file covers multiple distinct real-world entities.
2. An entity file has grown too large (more than 200 lines of body text) and covers
   distinct topics that should be separate pages.

All merge and split suggestions require user approval before execution.

## Human Approval Rules

The following synthesis actions require **explicit user approval**:

1. Creating any new entity file (the maintainer proposes, the user approves).
2. Merging two entity files (requires confirmation that they represent the same entity).
3. Splitting an entity file (requires confirmation of the split boundaries).
4. Creating domain summary pages that include non-public information.
5. Any action that would change the graph structure (add/remove nodes or relationships).

The following synthesis actions may proceed **without** user approval:
1. Generating proposal documents for user review.
2. Listing evidence for a proposed page.
3. Creating review queue items for uncertain cases.

## Examples

### Example 1: Missing Manager Page

```markdown
### Proposed Page: person-jane-smith

- **Type:** person
- **Evidence:** Referenced as manager in [[org-team-alpha]], [[program-delta]],
  and [[decision-resource-allocation-03]].
- **Sources:** [[source-meeting-notes-2026-04-15]], [[source-email-thread-2026-04-20]]
- **Suggested action:** Create `person-jane-smith.md` with role and org associations.
- **Human gate:** Confirm that "Jane Smith" and "J. Smith" in different sources
  refer to the same person before creating.
```

### Example 2: Missing JADC2/Acronym Page

```markdown
### Proposed Page: acronym-jadc2

- **Type:** acronym
- **Evidence:** Referenced by 3 decisions and 2 risks.
- **Referenced by:** [[decision-jadc2-integration-01]], [[decision-jadc2-integration-02]],
  [[decision-jadc2-integration-03]], [[risk-jadc2-gap-01]], [[risk-jadc2-gap-02]]
- **Sources:** [[source-dod-strategy-2026]], [[source-army-c2-briefing]]
- **Suggested action:** Create `acronym-jadc2.md` if source evidence includes the
  full expansion and definition.
- **Human gate:** Ask user if "JADC2" should be an acronym page or a concept page.
```
