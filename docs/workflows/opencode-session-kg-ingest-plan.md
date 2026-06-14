# OpenCode Session KG Ingest Plan (90 Days)

Status: active
Primary Goal: Build a repeatable pipeline that extracts and summarizes the last 90 days of OpenCode session activity for knowledge-graph ingestion.

## Scope

- In scope:
  - Export session metadata from current and backup OpenCode databases.
  - Produce KG-ingest-ready artifacts (`jsonl`, `md`, `stats`).
  - Preserve recovery artifacts and document repeatable run steps.
- Out of scope:
  - Full restoration of Desktop sidebar/pin visual state.
  - Replaying old sessions back into the live Desktop DB.

## Data Sources

- Active DB:
  - `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`
- Rotated pre-recovery DB:
  - `C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-state-backup-20260531-1738\opencode.db`

## Implemented Pipeline

Script:
- `C:\development\opencode\scripts\export_opencode_sessions.py`

Outputs per run:
- `sessions_90d.jsonl`: one normalized record per session
- `sessions_90d_summary.md`: human-readable summary for triage/review
- `sessions_90d_stats.json`: aggregate metrics for trend analysis
- `kg-prep-nodes.json`: session-aware KG node candidates
- `kg-prep-edges.json`: session-aware KG edge candidates
- `kg-prep-summary.json`: transform counts for validation

Optional KG inbox handoff:
- `--kg-inbox-dir "C:\development\02-Kx-to-process\10 inbox"` creates a timestamped packet under the Kx/KG repo's inbox.

## Current Baseline Export

Run label:
- `desktop-recovery-90d`

Artifact directory:
- `C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\session-export-90d-20260531-1755`

Window:
- 90 days before `2026-05-31`

Result snapshot:
- 1,879 sessions
- 11 projects
- 60,689 backup-db messages + 2,399 active-db messages scanned
- 1,827 sessions currently missing from the rebuilt active DB (`sessions_missing_from_active_90d.jsonl`)

Latest KG handoff:
- `C:\development\02-Kx-to-process\10 inbox\opencode-session-export-90d-20260531-222214`
- 1,881 sessions
- 1,827 sessions missing from active DB
- 1,920 prepared nodes
- 4,366 prepared edges

## Operational Steps

1. Re-run 90-day export and KG inbox handoff:

```powershell
$out="C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\session-export-90d-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
python C:\development\opencode\scripts\export_opencode_sessions.py `
  --db C:\Users\DaveWitkin\.local\share\opencode\opencode.db `
  --db C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-recovery-20260531-181148\opencode.db `
  --db C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts\desktop-state-backup-20260531-1738\opencode.db `
  --days 90 `
  --output-dir $out `
  --label desktop-recovery-90d-kg-handoff `
  --kg-inbox-dir "C:\development\02-Kx-to-process\10 inbox"
```

2. Validate export shape:
- Confirm all three output files exist.
- Confirm `sessions_90d_stats.json` has non-zero `session_count`.
- Spot-check `sessions_90d_summary.md` for expected repos/titles.

3. KG ingestion handoff:
- Use `kg-prep-nodes.json` and `kg-prep-edges.json` as the dedicated session-aware KG load inputs.
- Use:
  - `project_worktree`/`directory` -> project/repo edges
  - `model`, `message_providers`, `message_models` -> tooling/model usage edges
  - `time_created_iso`, `time_updated_iso` -> temporal edges
  - `title`, `sample_user_text`, `sample_assistant_text` -> semantic annotations
- Keep the generated packet as a subfolder under `10 inbox`; default `ingest-inbox.py` only scans top-level files, which prevents accidental regex extraction of the full session JSON.

## Hardening Link

If Desktop startup regresses again, run:
- `C:\development\opencode\scripts\Invoke-OpenCodeDesktopSafeRecovery.ps1`

This preserves evidence, reapplies Skillful cache fixes, and resets only known-corrupt state in a controlled order.

## Known Constraints

- Some session/message content payloads are metadata-heavy and may not include full text bodies.
- Sidebar chat/repo visibility in Desktop is UI-state driven and not guaranteed by DB restoration alone.
- Duplicate session IDs across merged DB sources are deduplicated by session ID, preferring latest seen record.
