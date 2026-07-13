# Graph Health Checklist

This checklist provides the commands and criteria for a baseline graph health assessment.
Run these checks at the start of every maintenance cycle.

## Required Commands

```powershell
# 1. Validate graph structure (frontmatter, links, orphans, predicates)
python scripts\validate-kg.py

# 2. Build or rebuild the search index
python scripts\build-index.py

# 3. Validate vector search index (if applicable)
python scripts\validate-vector-search.py
```

All three commands should complete without errors before proceeding to deeper analysis.

## File and Folder Counts

After running validation, record the following metrics:

| Metric | How to Check | Target |
|--------|-------------|--------|
| Total entity files | Count files in `knowledge-base/people/`, `organizations/`, `programs/`, `decisions/`, `risks/` | Growing or stable |
| Entity files by type | `validate-kg.py` output | All 5 types represented |
| Broken wikilinks | `validate-kg.py` output | Zero (or declining) |
| Orphan nodes | `validate-kg.py` output | Zero (or declining) |
| Missing frontmatter | `validate-kg.py` output | Zero |

Quick count command:

```powershell
$folders = @("people","organizations","programs","decisions","risks")
$base = "C:\development\02-Kx-to-process\knowledge-base"
foreach ($f in $folders) {
    $count = (Get-ChildItem -LiteralPath "$base\$f" -Filter "*.md" -ErrorAction SilentlyContinue).Count
    "$f : $count"
}
```

## Broken Wikilinks

Broken wikilinks are `[[target]]` references that point to files that do not exist in the
knowledge base. These indicate either:

1. A missing entity page that should be created (see `gap-detection.md`).
2. A typo in the wikilink target.
3. A renamed entity where links were not updated.

For each broken wikilink found:
- Record the source file and the broken target.
- Attempt to resolve: does a similarly-named file exist? Was the entity renamed?
- If genuinely missing, add to the gap detection findings.

## Orphan Nodes

Orphan nodes have no incoming or outgoing wikilinks. They are disconnected from the graph
and cannot be discovered through relationship traversal.

For each orphan node:
- Check whether the entity is referenced by name (but not wikilink syntax) in other files.
- If referenced by name, the fix is to add `[[wikilink]]` syntax to the referencing files.
- If truly isolated, determine whether the entity should be connected or archived.

## Low-Confidence Nodes

Nodes with `confidence: low` in their frontmatter represent uncertain or unverified
information. These should be reviewed during each maintenance cycle.

For each low-confidence node:
- Check whether new sources have become available since the last review.
- If new sources confirm the information, update `confidence` to `medium` or `high` and
  add the new source to the `sources` field.
- If no new sources exist, leave the confidence level unchanged and ensure the node is
  in the review queue for user attention.

## Exit Criteria

A baseline health check is complete when:

1. `validate-kg.py` runs without crashes and produces a complete report.
2. `build-index.py` completes successfully.
3. `validate-vector-search.py` completes (or is noted as not yet configured).
4. All broken wikilinks are cataloged with resolution status.
5. All orphan nodes are cataloged with connection assessment.
6. All low-confidence nodes are listed for review.
7. Metrics are recorded for trend comparison with prior cycles.

## Error Recovery

- If `validate-kg.py` reports a YAML parse error: open the failing file, fix the
  frontmatter, and re-run validation.
- If a folder count returns zero unexpectedly: check that the folder exists and contains
  `.md` files. An empty folder is not necessarily an error but should be noted.
- If `validate-vector-search.py` fails: note the failure in the audit report. Vector
  search may not be configured for all repositories.
