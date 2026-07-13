---
name: knowledge-graph-maintainer
description: "Audit and maintain the local markdown knowledge graph: health, gaps, review queues."
triggers:
  user_phrases:
    - audit knowledge graph
    - find contradictions in knowledge graph
    - check graph health
    - knowledge graph gaps
    - review queue
    - maintain knowledge graph
    - detect contradictions
---

# Knowledge Graph Maintainer

This skill owns **graph-to-insight maintenance** for the markdown-native knowledge graph
stored in `C:\development\02-Kx-to-process\knowledge-base\`.

It does **not** own raw source extraction, mailbox export, OCR/transcription, or bulk
source-to-graph ingestion. Route those tasks to `knowledge-graph-builder`.

## When to Use

Activate this skill when the user asks to:

- **Audit the knowledge graph** - run a health check across all entity types.
- **Find contradictions** - detect conflicting claims across sources and confidence levels.
- **Find gaps** - identify missing entity pages, missing relationships, or thin nodes.
- **Suggest new wiki pages** - propose synthesis pages, concept pages, or domain summaries.
- **Find orphan nodes** - detect entities with no incoming or outgoing wikilinks.
- **Review queue** - generate or process a queue of items needing user attention.
- **Missing provenance** - audit nodes and relationships that lack source citations.
- **Graph health** - run the full maintenance lifecycle from baseline check to proposed updates.
- **Schema validation** - verify frontmatter, IDs, predicates, and review statuses.
- **Provenance audit** - check that high-impact claims have adequate source backing.
- **Active synthesis** - propose new pages that connect existing entities.
- **Community detection** - find clusters of related but unlinked nodes.
- **Web research for gaps** - search public sources to fill identified knowledge gaps.

## Skill Boundary

This skill owns **graph-to-insight maintenance**. It does **not** own:

- Raw source conversion (email-to-markdown, PDF extraction, OCR).
- Mailbox export or batch ingestion pipelines.
- Bulk source-to-graph ingestion.
- Creating new validation scripts or MCP server infrastructure.

Route ingestion and source conversion tasks to `knowledge-graph-builder` or a dedicated
ingestion Conductor track.

## Reference Workflow

The maintainer skill follows an 8-phase maintenance lifecycle. Each phase has a dedicated
reference file with commands, templates, and escalation rules.

| Phase | Reference | Purpose |
|-------|-----------|---------|
| 1 | `references/maintenance-workflow.md` | Full maintenance lifecycle overview |
| 1 | `references/graph-health-checklist.md` | Baseline health check commands and exit criteria |
| 2 | `references/schema-validation.md` | Frontmatter, ID, predicate, and review status validation |
| 2 | `references/provenance-audit.md` | Source citation audit and weak provenance detection |
| 3 | `references/gap-detection.md` | Missing entity pages, relationships, and coverage gaps |
| 4 | `references/contradiction-detection.md` | Claim comparison, source recency, and identity conflicts |
| 5 | `references/active-synthesis.md` | New wiki page and concept page proposals |
| 5 | `references/semantic-search-and-community-detection.md` | Keyword/vector search and related-node discovery |
| 6 | `references/review-queue.md` | Priority-based review queue management |
| 6 | `references/web-research-for-gaps.md` | Targeted public research for knowledge gaps |
| 6 | `references/human-escalation.md` | When and how to ask the user for clarification |

## Outputs This Skill Produces

When this skill runs a maintenance cycle, it produces one or more of the following:

1. **Maintenance audit report** - a structured summary of graph health, issues found, and actions taken.
2. **Review queue markdown file** - a dated list of items requiring user attention (contradictions, low-confidence nodes, provenance gaps, etc.).
3. **Proposed patch plan** - a list of specific edits to entity files, with source evidence for each change.
4. **Human question list** - targeted questions for the user about ambiguous identities, sensitive facts, or missing context.
5. **New Conductor track recommendation** - if the maintenance cycle reveals work too large for inline fixes (e.g., a major corpus expansion or a new extraction pipeline), propose a new Conductor track.

## Do Not Automatically Write

This skill must **never** automatically perform any of the following actions without
explicit user approval:

- **Do not automatically resolve contradictions.** Present both claims with source evidence and ask the user which is canonical.
- **Do not automatically merge ambiguous identities.** If two person or org nodes might refer to the same entity but evidence is unclear, create a review queue item instead.
- **Do not automatically create public-research-based facts without citations.** Any fact added from web research must include a verifiable source URL and a `confidence` field.
- **Do not automatically change sensitive or internal facts without user approval.** This includes organizational restructuring, personnel changes, program status changes, and budget figures.
- **Do not automatically delete nodes.** If a node appears obsolete, add it to the review queue with evidence rather than removing it.
- **Do not modify the knowledge base during skill creation.** This track creates the skill documentation only.

## Quick Start

To run a full maintenance cycle:

```powershell
# 1. Validate the graph
python scripts\validate-kg.py

# 2. Build the search index
python scripts\build-index.py

# 3. Run the maintainer skill lifecycle
# Follow references/maintenance-workflow.md phases 1-8
```



## Graph Health Audit via GraphQLite

Use scripts/query-graph.py for structured graph health analysis:

```bash
# Check graph availability and counts
python scripts/query-graph.py health

# Find most central entities (PageRank)
python scripts/query-graph.py pagerank --top 10

# Check community structure (Louvain)
python scripts/query-graph.py louvain --top 10

# Investigate orphans - check if an entity has neighbors
python scripts/query-graph.py neighbors --id "<orphan_id>" --depth 1 --types Person,Organization,Program

# Count generic references edges (weak links)
python scripts/query-graph.py cypher "MATCH (a)-[r]->(b) RETURN type(r) as rel_type, count(r) as cnt"

# Find entities with no edges
python scripts/query-graph.py cypher "MATCH (n) WHERE NOT (n)--() RETURN n.id, n.name LIMIT 20"
```

> **Note:** All node paths are stored in the `n.file_path` property. If a lookup returns `None` for path, the graph database is out of sync with the markdown files. Run `python scripts/validate-kg.py --kb ... --scope c2` and check CK-15/CK-16.

**Interpretation:**
- Giant community (1,700+ nodes) + many singletons = sparse graph (expected)
- High PageRank acronyms = cross-referenced hubs (normal)
- Orphan nodes = need relationship fixes
- Generic 
eferences edges = should be typed predicates (future improvement)

Keep alidate-kg.py as the formal validation gate. query-graph.py complements it with relationship-level analysis.
## Related Skills

- **`knowledge-graph-builder`** - source-to-graph ingestion pipeline.
  Use the builder to extract entities from raw documents, then use this maintainer
  skill to audit and improve the resulting graph.
