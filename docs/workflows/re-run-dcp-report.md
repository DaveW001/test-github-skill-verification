# Workflow: Re-Run the DCP Token-Savings Report

**Purpose:** Periodically regenerate the DCP (Dynamic Context Pruning) token-savings report from your own OpenCode session data.
**Created:** 2026-06-14
**Last verified:** 2026-06-14
**Related:** Track `20260613-dcp-token-savings-analysis` (original build + handover); `docs/decisions/quick-public-static-hosting-2026-06-14.md` (how to re-host).

## What it produces

A self-contained HTML report plus an `aggregate.json` with the raw numbers. The report uses a **compound** savings model (compressed tokens x subsequent requests), not one-time compression - that is where the real savings show up.

| Output | Path |
|---|---|
| HTML report | `.../20260613-dcp-token-savings-analysis/artifacts/dcp-savings-report.html` |
| Aggregate JSON | `.../20260613-dcp-token-savings-analysis/artifacts/aggregate.json` |
| Generator script | `.../20260613-dcp-token-savings-analysis/scripts/generate_report.py` |

Base path: `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\`

## Prerequisites

- **Python 3** (stdlib only - no pip installs).
- **Data sources present (script is read-only on all of them):**
  - `C:\Users\DaveWitkin\.local\share\opencode\opencode.db` (session / message / part tables)
  - `C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp\ses_*.json` (DCP prune state)

## How to run

```powershell
cd C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\scripts

# Full run (aggregate + HTML) - default: last 100 sessions
python generate_report.py

# Analyze a different number of most-recent sessions (e.g., 250)
python generate_report.py --sessions 250

# Aggregate only (no HTML)
python generate_report.py --aggregate-only

# Verify (self-checks; exit code 0 = pass). Works at any --sessions value.
python generate_report.py --verify
python generate_report.py --sessions 250 --verify
```

**The `--sessions N` flag** selects the N most-recent non-empty sessions (default `100`). The verify check compares the analyzed count against whatever N you pass, so it stays correct at any N. If you ever want a different default, change `LAST_N` near the top of the script.

## Notes and gotchas

- **Numbers shift between runs** because the current live OpenCode session is adding data in real time - expect small drift, not a stable snapshot.
- **Empty / abandoned sessions are auto-excluded** (sessions with zero messages are filtered out in SQL).
- **Outputs are overwritten in place** each run. A hosted/deployed report is a separate static snapshot - re-running locally does NOT change any published link until you redeploy.
- **DCP eligibility threshold** (sessions flagged "should have pruned but did not"): >=10 requests AND >=10K peak input. Tune `DCP_ELIGIBLE_MIN_REQUESTS` / `DCP_ELIGIBLE_MIN_PEAK_INPUT` near the top of the script if you want different criteria.
- **Tunables near the top of the script:** `LAST_N` (default session count), `BLENDED_USD_PER_MTOK` (price), `DCP_ELIGIBLE_MIN_REQUESTS`, `DCP_ELIGIBLE_MIN_PEAK_INPUT`, `DCP_HARD_LIMIT`, `DCP_SOFT_LIMIT`.

## Re-hosting the report publicly

See `docs/decisions/quick-public-static-hosting-2026-06-14.md` for the full rationale and steps. Short version: stage the HTML as `index.html` in a throwaway folder, then `vercel deploy --prod --yes`. Share only the clean `*.vercel.app` alias (not the deployment-specific URL, which contains the Vercel team slug).

## Current instance (last run)

| Field | Value |
|---|---|
| Last generated | 2026-06-14 (100 sessions) |
| Key figures | ~66.3M compound tokens saved, ~32.8x multiplier, ~$199 at $3/Mtok, 73 of 100 sessions with DCP |
| Hosted (snapshot) | https://dcp-savings-2026.vercel.app |
