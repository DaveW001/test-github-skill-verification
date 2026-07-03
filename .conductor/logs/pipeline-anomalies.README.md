# Pipeline Anomalies Log

## Purpose
Append-only operational anomaly store for the Conductor pipeline. See `conductor-pipeline/references/anomaly-logging.md` for the full schema and rotation policy.

## File
- Primary store: `pipeline-anomalies.jsonl` (one JSON object per line, UTF-8, no trailing comma, no comments).

## Schema (one line, seven keys)
- `ts` (string, ISO-8601 UTC, e.g. `2026-07-03T14:25:00Z`)
- `track` (string, track id)
- `stage` (string, e.g. `stage-1`, `stage-2`, `stage-4`, `orchestrator`)
- `subagent` (string, e.g. `conductor-track-executor`)
- `type` (string, closed taxonomy)
- `severity` (string, `info` | `warn` | `error`)
- `detail` (string, terse)

## Taxonomy (closed)
`permission-prompt` | `tool-error` | `model-fallback` | `destructive-ask` | `deviation` | `retry` | `other`

## Rotation
- Cap: 5000 lines.
- Action: rename `pipeline-anomalies.jsonl` to `pipeline-anomalies.archive-<ts>.jsonl` and start a new empty `pipeline-anomalies.jsonl`. The previous contents are PRESERVED (FIFO archive, not truncate).

## Rules
- One JSON object per line. Do not modify or delete past lines.
- Never insert comments. JSONL is line-oriented; use a sibling markdown file for prose.
- Never use bare `ConvertFrom-Json` over the whole file - it parses only the FIRST line. Use a per-line parse loop.