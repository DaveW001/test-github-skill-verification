# External Source Delta Detection

This document defines how to detect new and changed sources in external systems that feed the knowledge graph, starting with NotebookLM. Use this **before** ingestion to answer: "What's new since the last time we pulled data?"

## Problem

The knowledge graph ingests content from multiple external sources. These sources change over time -- new documents are added, existing documents are updated, and some are removed. To keep the graph current without reprocessing everything, we need a reliable way to detect what changed since the last ingestion cycle.

NotebookLM is a primary external source for the C2/CC2 portfolio engagement. The same pattern applies to any external system that exposes a source list API or CLI.

## NotebookLM Source Delta Detection

### Current Notebook Inventory

The C2/CC2 engagement uses four NotebookLM notebooks:

| Alias | Notebook ID | Title | Baseline Count |
|-------|-------------|-------|---------------|
| portfolio | `5125c1f1-71b3-4dbe-afc5-d725d1a4db2c` | C2/CC2 Portfolio Engagement Kx | 97 |
| interviews | `a6341a1d-e4d2-4cd1-8cb9-5dfcb0c4cfac` | Interview Notebook | 30 |
| workshop | `093bdb9c-e06a-4117-bdec-7c0f56f5edc1` | Leadership Workshop | 3 |
| solutions | `5a74333c-fdf4-437f-8eff-03d7c455ef72` | Solutions | 2 |

> Baseline counts captured 2026-05-26, updated 2026-05-27 (portfolio 96->97 after source drift detected). Audit-grade snapshots stored under `.conductor/nlm-snapshots/2026-05-27/`. Update this table when you run a delta check.

### Detection Strategy

NotebookLM does **not** expose per-source `created_at` timestamps. The CLI returns source IDs, titles, and types only. The detection strategy works in two tiers:

#### Tier 1: Notebook-Level Growth (Quick Check)

Use `nlm notebook list` to get current `source_count` for each notebook. Compare against the baseline counts above.

```powershell
# Get current notebook state
nlm notebook list --json
```

If `source_count` matches the baseline for all notebooks: nothing new. Stop here.

If any notebook grew: proceed to Tier 2 for that notebook.

#### Tier 2: Source-Level Enumeration (Full Delta)

Use `nlm source list <notebook-id> --json` to get the full source roster for the notebook that changed.

```powershell
# List all sources in a notebook
nlm source list 5125c1f1-71b3-4dbe-afc5-d725d1a4db2c --json
```

Compare the current source list against a **persisted snapshot** (see below) to identify:
- **New sources** -- source IDs not in the snapshot
- **Removed sources** -- snapshot IDs no longer in the live list
- **Changed sources** -- title or type changes for existing IDs (rare but possible)

### Source Recency Heuristic

Most NotebookLM sources in this project have date-stamped titles (e.g., `2026-05-26 Scrum Sync Notes`). For a quick "what's new in the last N days?" check without a persisted snapshot:

1. Run `nlm source list <notebook-id> --json`.
2. Filter source titles matching `2026-MM-DD` patterns.
3. Select titles where the extracted date falls within your time window.

This is a heuristic, not audit-grade. It misses sources without date-stamped titles and may miscategorize sources added late with older content dates.

### Persisted Snapshots (Audit-Grade Detection)

For reliable source-level delta detection across runs:

1. **Create a snapshot** after each ingestion cycle:

```powershell
# Save current source list as a timestamped snapshot
$date = Get-Date -Format "yyyy-MM-dd"
$snapDir = "C:\development\02-Kx-to-process\.conductor\nlm-snapshots\$date"
New-Item -ItemType Directory -Path $snapDir -Force
foreach ($nb in @("5125c1f1-71b3-4dbe-afc5-d725d1a4db2c", "a6341a1d-e4d2-4cd1-8cb9-5dfcb0c4cfac", "093bdb9c-e06a-4117-bdec-7c0f56f5edc1", "5a74333c-fdf4-437f-8eff-03d7c455ef72")) {
  nlm source list $nb --json | Out-File -Encoding utf8 "$snapDir\$nb.json"
}
```

2. **Diff against the previous snapshot** to find new/removed/changed sources:

```powershell
# Compare current vs previous (example)
$prevIds = (Get-Content ".conductor\nlm-snapshots\2026-05-26\5125c1f1*.json" | ConvertFrom-Json).id
$currIds = (nlm source list 5125c1f1-71b3-4dbe-afc5-d725d1a4db2c --json | ConvertFrom-Json).id
$newIds = $currIds | Where-Object { $_ -notin $prevIds }
Write-Host "New sources: $($newIds.Count)"
```

3. **Snapshot storage location:** `.conductor/nlm-snapshots/<YYYY-MM-DD>/`

### After Detection: What to Do with New Sources

Once you have the list of new sources:

1. **Get source content** for each new source:

```powershell
nlm source content <source-id> -o "10 inbox\nlm-<source-id>.md"
```

2. **Ingest using the standard ingestion workflow** (`ingestion-workflow.md`):
   - The extracted content becomes the source file for entity extraction.
   - Create a `source-` node with `source_type: notebooklm` and the NotebookLM source ID.
   - Follow entity extraction, dedup, and validation steps as normal.

3. **Update the baseline counts** in the table above after ingestion completes.

4. **Create a new snapshot** for the next delta cycle.

## General Pattern for Other External Sources

The same two-tier strategy applies to any external system:

| Step | Action |
|------|--------|
| 1 | Get the current source inventory from the external system (API, CLI, or export). |
| 2 | Compare against a persisted snapshot or baseline count. |
| 3 | If changed, enumerate individual sources to find new/removed/changed items. |
| 4 | For each new source, export content and run standard ingestion. |
| 5 | After ingestion, create a new snapshot. |

### Applicable External Sources (Current and Future)

| Source | Detection Method | Status |
|--------|-----------------|--------|
| NotebookLM | `nlm notebook list` + `nlm source list --json` | Documented above |
| Google Drive | `gws` CLI or Google Drive API file list | Not yet documented |
| Outlook email | Microsoft Graph API message list with `$filter` by receivedDateTime | Not yet documented |
| H-drive file share | File system scan with modification date filter | Baseline exists at `.conductor/tracks/c2-h-drive-corpus-expansion/h-drive-raw-inventory.json` |

## Frequency

Run delta detection:
- **Before each ingestion batch** (weekly or as scheduled).
- **On demand** when the user asks "what's new?"
- **After known events** that produce new meeting notes, interviews, or documents.

## CLI Quick Reference

```powershell
# Authenticate
nlm login --check

# Quick notebook-level check
nlm notebook list

# Full source list for a notebook
nlm source list <notebook-id> --json

# Get content of a specific source
nlm source content <source-id>

# Export source content to file
nlm source content <source-id> -o "path/to/output.md"
```

