
### Archive Destination Rule

**NEVER** create an archive subfolder inside 10 inbox, 20 planning, or any other working folder. The ONLY valid archive destination is 60 archive/ at the repository root.

If you find 10 inbox\archive (or any archive-like subfolder inside a working folder), it was created in error. Move its contents to 60 archive/ and delete the rogue subfolder.
# Archiving and Logging

This document defines the folder lifecycle for processed sources, archive rules, ingest log format, and handoff notes for the knowledge graph builder.

## Folder Lifecycle

The repository uses a numbered folder structure to track processing status. The active lifecycle is:

```
10 inbox     -> Source files awaiting processing
20 planning  -> Sources queued for specific extraction runs
60 archive   -> Sources that have been fully processed and logged
knowledge-base -> Entity notes (permanent storage)
```

**Important:** The folders `30 processing`, `40 validating`, and `50 outbox` are **inactive** (legacy). Do not use them. Sources move directly from `20 planning` to `60 archive` after successful validation.

### Folder Details

| Folder | Purpose | When to Use |
|--------|---------|-------------|
| `10 inbox` | Landing zone for new source files | User drops files here for ingestion |
| `20 planning` | Staging for planned extraction | Agent or user moves files here before processing |
| `60 archive` | Completed source storage | After validation passes and ingest log is written |
| `knowledge-base` | Entity notes, source nodes, indexes, logs | Permanent; never move files out without archiving |

## Archive Rules

### When to Archive

Archive a source file to `60 archive` when ALL of the following are true:

1. Source node created in `knowledge-base/sources/` with `extraction_status: complete`.
2. All entity notes written and validated.
3. `validate-kg.py` returns 0 FAIL.
4. Index rebuilt with `build-index.py`.
5. Ingest log entry written.

### Archive Process

```powershell
# Move the source file to archive
Move-Item -LiteralPath "C:\development\02-Kx-to-process\10 inbox\filename.docx" -Destination "C:\development\02-Kx-to-process\60 archive\filename.docx" -Force
```

### When NOT to Archive

Do NOT archive if:
- Validation shows any FAIL results.
- Extraction was partial (`extraction_status: partial`).
- The user requests the file remain in place.
- The source file is still being referenced by an active extraction run.

## Ingest Log Template

Every ingestion run must append an entry to the ingest log. The log is stored at:

`C:\development\02-Kx-to-process\knowledge-base\logs\ingest-log.md`

### Log Entry Format

```
## YYYY-MM-DD - Source Name

- Source: `10 inbox/filename.docx`
- Source node: [[source-slug]]
- Entities created: N
- Entities updated: N
- Entities skipped: N
- Validation: PASS, N FAIL
- Index rebuilt: yes|no
- Open review items: N
- HANDOFF: [description of items handed to maintainer, if any]
```

### Example Entry

```
## 2026-05-10 - C2 Planning Meeting Notes

- Source: `10 inbox/c2-planning-meeting-2026-05-10.docx`
- Source node: [[source-c2-planning-meeting-2026-05-10]]
- Entities created: 5
- Entities updated: 3
- Entities skipped: 2
- Validation: PASS, 0 FAIL
- Index rebuilt: yes
- Open review items: 1
- HANDOFF: person-j-smith ambiguous identity -- may be same as person-john-smith or separate individual
```

## Handoff Notes

When unresolved issues remain after ingestion, document them as handoff notes:

### Handoff Format

Use the `HANDOFF:` prefix in the ingest log entry, and optionally create a separate note in the entity file:

```
## Potential Duplicates
- [[person-j-smith]] may be the same as [[person-john-smith]]. Source mentions "J. Smith" in military context. Existing note for John Smith is COL rank. New source does not specify rank.
```

### Items That Require Handoff

- Contradictory source claims about the same entity.
- Low-confidence identity matches.
- Missing canonical pages for referenced entities.
- Orphan nodes with no relationships.
- Review queue items that exceed builder scope.

These items should be routed to `knowledge-graph-maintainer` for resolution.

## Error Recovery

| Error | Recovery |
|-------|----------|
| Archive folder does not exist | Create it: `New-Item -ItemType Directory -Path "60 archive" -Force` |
| Source file locked by another process | Wait and retry; if persistent, note in log and skip archival |
| Ingest log file does not exist | Create it with a header: `# Ingest Log` |
| Cannot write to ingest log | Check permissions on `knowledge-base/logs/` directory |
| Source file disappeared before archival | Log as missing; do not delete source node; flag for review |
| Accidental archive of unvalidated source | Move back to `10 inbox` or `20 planning`; re-validate |
