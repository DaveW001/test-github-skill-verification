# Knowledge Graph Query Skill

## When to Use

Use this skill when you need to:
- Look up people, organizations, programs, events, or contacts in the local Knowledge Graph (KG)
- Enrich meeting notes with attendee context from KG
- Verify relationships or organizational hierarchies
- Find the shortest path between entities (e.g., how two people are connected)
- Identify influential entities via PageRank or community clusters via Louvain
- Answer stakeholder, vendor, or team composition questions
- Resolve ambiguous entity references across Army C2/CC2 **and** Packaged Agile business domains

This skill works for both Army C2/CC2 work and Packaged Agile business enrichment. Do not assume KG is only for Army C2; it contains business contacts, vendors, DCSA personnel, and cross-domain relationships.

## Workspace

All commands run from: `C:\development\02-Kx-to-process`

KG database: `C:\development\02-Kx-to-process\knowledge-base\indexes\graph-index.db`

## Primary Commands

### 1. Health Check
```
python scripts/query-graph.py health
```
Returns JSON with `status`, `nodes`, `edges`, `hashes`, and `db_path`. Run this first to confirm the KG is operational.

### 2. Lookup (Name/Type Search)
```
python scripts/query-graph.py lookup --name "<name>" --type Person --top 5
```
- `--name`: CONTAINS match (partial names work)
- `--type`: Entity type label (e.g., `Person`, `Organization`, `Program`, `Event`)
- `--top`: Max results (default: 10)
- `--explain`: Include explanation metadata

Example:
```
python scripts/query-graph.py lookup --name "Jason E. Lenzi" --type Person --top 5
```

### 3. TF-IDF / Vector Search (Fallback)
```
python scripts/search.py "<query>" --top 5
```
- Searches across all KG markdown source files using TF-IDF + FTS5
- Use when GraphQLite lookup returns no results
- Supports natural language queries

Example:
```
python scripts/search.py "DCSA ISR Jason Lenzi" --top 5
```

### 4. Neighbors
```
python scripts/query-graph.py neighbors --id <entity-id> --depth 2 --types Person,Organization
```
- `--id`: Exact entity ID (e.g., `person-keith-register`)
- `--depth`: Traversal depth (default: 1)
- `--types`: Comma-separated type filter
- `--explain`: Include explanation metadata

### 5. Shortest Path
```
python scripts/query-graph.py path --from <entity-id> --to <entity-id> --max-depth 3
```

### 6. Cypher Query (Advanced)
```
python scripts/query-graph.py cypher "MATCH (n:Person) RETURN n.id, n.name LIMIT 5"
```
Use for custom graph traversals not covered by built-in commands.

### 7. PageRank
```
python scripts/query-graph.py pagerank --top 10
```
Returns the most influential entities by PageRank score.

### 8. Louvain Community Detection
```
python scripts/query-graph.py louvain --top 10
```
Returns community clusters detected by the Louvain algorithm.

## Meeting/Contact Enrichment Recipe

Follow this workflow when enriching meeting notes:

1. **Extract attendee names** from raw meeting notes, email headers, or calendar invites.
2. **Look up each attendee in KG** using `query-graph.py lookup --name "<Name>" --type Person --top 5`.
3. **If not found**, fall back to TF-IDF search: `python scripts/search.py "<Name> <Context>" --top 5`.
4. **If still not found**, use grep/glob to search KG markdown source files directly.
5. **Record conflicts** between KG data and live sources (email signatures, calendar entries) — flag these for review rather than silently overwriting.
6. **Check data freshness** — see Data Freshness Rules below.

## Fallback Strategy

When querying the KG, follow this order:

1. **GraphQLite lookup** (`query-graph.py lookup`) — fastest, structured, returns exact entity matches.
2. **TF-IDF search** (`search.py`) — broader, handles natural language, searches all markdown sources.
3. **Targeted markdown read** — use `Read` or `grep` to examine specific KG source files identified from search results.
4. **grep/glob** — last resort for exact filename patterns or when query tools fail.

Always start at step 1 and only fall forward when the current step returns no useful results.

## Data Freshness Rules

- Check `last_updated` fields on Person and Organization entities. If a field is older than **90 days**, treat it as potentially stale.
- **Cross-source verification**: Before relying on contact details (email, phone, role), verify against at least one live source — email signature, calendar invite, or directory lookup.
- **Flag, don't overwrite**: When KG data conflicts with live evidence, record the discrepancy in the execution log or notes. Do not silently update KG without explicit approval.
- **Staleness threshold**: Data older than 90 days should trigger a verification check. Data older than 180 days should be treated as unreliable until confirmed.
- Queue stale entries for review rather than deleting them.

## Examples

### Lookup a person
```powershell
# In C:\development\02-Kx-to-process
python scripts/query-graph.py lookup --name "Keith Register" --type Person --top 5
```
Expected output: JSON array with matching entities containing `id`, `name`, `type`, and properties.

### Search for DCSA contacts
```powershell
python scripts/search.py "DCSA ISR Jason Lenzi" --top 5
```
Expected output: Ranked search results with file paths and relevance scores.

### Find neighbors of an organization
```powershell
python scripts/query-graph.py neighbors --id org-packaged-agile --depth 2 --types Person
```
Expected output: Connected Person entities with relationship types.

### Check KG health
```powershell
python scripts/query-graph.py health
```
Expected output:
```json
{
  "status": "ok",
  "nodes": 15467,
  "edges": 42653,
  "hashes": 18122,
  "db_path": "C:\\development\\02-Kx-to-process\\knowledge-base\\indexes\\graph-index.db"
}
```

### Find path between two people
```powershell
python scripts/query-graph.py path --from person-keith-register --to person-brad-hunter --max-depth 3
```
Expected output: Shortest path with intermediate nodes and edge labels.

### PageRank for key entities
```powershell
python scripts/query-graph.py pagerank --top 10
```
Expected output: Top 10 entities ranked by PageRank score.
