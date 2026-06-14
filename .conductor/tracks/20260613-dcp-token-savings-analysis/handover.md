# Handover: DCP Token-Savings Analysis

**Track:** `20260613-dcp-token-savings-analysis`
**Created:** 2026-06-14
**Status:** Report v3.1 delivered — user reviewing
**Hosted report (public):** https://dcp-savings-2026.vercel.app — deployed 2026-06-14 via Vercel (account `davew001`, project `dcp-savings-2026`). **Share ONLY this clean alias** — the auto-generated deployment URL contains the team slug (`pa-projects-0025`). Teardown: `vercel remove dcp-savings-2026 --yes`. Rationale & reusable steps: `docs/decisions/quick-public-static-hosting-2026-06-14.md`.

---

## What This Project Does

Quantifies Dynamic Context Pruning (DCP) token savings across the last 100 OpenCode sessions. Generates a self-contained HTML report with compound savings model (not one-time), per-model breakdown, DCP eligibility analysis, and a Reddit-ready summary card.

**Key insight discovered:** DCP's real value is compound savings (compressed tokens × subsequent requests), not one-time compression. The report shows **66.3M tokens saved (32.8x multiplier)** vs the naive one-time figure of 2.0M.

---

## Current Report Numbers (v3.1, live — will shift slightly with active sessions)

| Metric | Value |
|--------|-------|
| Sessions analyzed | 100 (empty sessions excluded) |
| Tokens used | ~194.1M |
| One-time saved | ~2.0M |
| Compound saved | ~66.3M |
| Multiplier | 32.8x |
| USD saved (@ $3/M) | ~$199 |
| Sessions with DCP | 73 of 100 |
| Sessions missed DCP | 13 (corrected threshold) |
| Sessions too short | 14 |

---

## Architecture & Data Sources

### Data Sources
- **Session/message/part data:** SQLite at `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`
  - Tables: `session` (id, time_updated), `message` (id, session_id, time_created, data JSON), `part` (message_id, data JSON)
  - Token path: `$.tokens.total` in step-finish parts
  - Model path: `$.providerID || '/' || $.modelID` in message data
  - Input tokens: `$.tokens.input`, cache read: `$.tokens.cache.read`
- **DCP savings state:** JSON files at `C:\Users\DaveWitkin\.local\share\opencode\storage\plugin\dcp\ses_*.json`
  - Each file: `stats.totalPruneTokens` (cumulative counter), `prune.messages.blocksById` (active blocks)
  - Block fields: `compressedTokens`, `summaryTokens`, `compressMessageId`, `directMessageIds`, `parentBlockIds`, `topic`
  - ~412 files total, 73 overlap with selected 100 sessions
- **DCP plugin source:** `C:\development\opencode\.conductor\tracks\20260526-opencode-desktop-log-remediation\artifacts\20260526-110855\@tarquinen-backup\opencode-dcp@latest\node_modules\@tarquinen\opencode-dcp\dist\index.js` (276KB bundled JS)

### DCP Configuration & Trigger Logic (from plugin source `defaultConfig`)
```
compress: {
  maxContextLimit: 100,000     // HARD trigger — force compress above this
  minContextLimit: 50,000      // SOFT limit — allow compress above this
  nudgeFrequency: 5            // every 5 turns
  iterationNudgeThreshold: 15  // starts nudging after 15 turns
  nudgeForce: "soft"           // gentle LLM suggestions
  permission: "allow"          // auto-mode
}
```

**Soft-trigger mechanism:** injects suggestion *text* prompting the LLM to call `compress` (not a forced action).
**Priority thresholds:** `MEDIUM_PRIORITY_MIN_TOKENS=500`, `HIGH_PRIORITY_MIN_TOKENS=5000`.

### Session Selection
- Last 100 sessions by `time_updated DESC`
- Empty/abandoned sessions (zero messages) excluded via SQL: `WHERE id IN (SELECT DISTINCT session_id FROM message)`
- 44 of naive last-100 would have been empty sessions (now excluded)
- All 100 selected sessions have real content (min 14,351 tokens)

### Missed DCP Threshold (corrected in v3.1)
- **OLD (wrong):** peak input > 100K → found 0 missed
- **NEW (correct):** ≥10 requests AND ≥10K peak input → finds 13 missed sessions
- Justified by: DCP compressed sessions at 12K peak (25th percentile of active sessions), and turn-based nudges are independent of token count
- All 13 missed sessions occurred June 8-14, 2026 (DCP installed since March 14 — not pre-DCP)

### Compound Savings Calculation
For each DCP block in a session:
1. `saved = compressedTokens - summaryTokens` (one-time)
2. Find position of `compressMessageId` in ordered step-finish messages
3. `remaining_requests = total_requests - position - 1`
4. `compound_saved = saved × remaining_requests`
5. Session compound = sum of all blocks' compound values

---

## Key Files

| File | Path | Size |
|------|------|------|
| **Generator Script** | `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\scripts\generate_report.py` | ~42KB, ~720 lines |
| **HTML Report** | `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\artifacts\dcp-savings-report.html` | ~29KB, self-contained |
| **Aggregate JSON** | `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\artifacts\aggregate.json` | ~88KB |
| **Execution Log** | `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\execution-logs\20260613-1950.md` | ~6KB |
| **Track Plan** | `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\plan.md` | ~28KB |
| **Spec** | `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\spec.md` | ~12KB |
| **Metadata** | `C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\metadata.json` | status: complete |

---

## HTML Report Sections (v3.1)

1. **Hero** — 66.3M compound tokens saved, multiplier badge, DCP coverage badge
2. **Understanding This Report** — explains one-time vs compound with concrete example (session with 164 requests, 173K compressed → 14.9M compound)
3. **One-Time vs Compound** — side-by-side comparison cards + persistent colored banner
4. **Key Metrics** — 8 stat boxes with tooltips (tokens used, saved, %, USD, requests, blocks, multiplier, DCP coverage)
5. **Savings Rate** — CSS conic-gradient donut chart
6. **Top Sessions** — bar chart, 15 sessions ranked by compound savings
7. **Per-Model Breakdown** — bar chart with DCP eligibility flags (⚠ missed / no DCP needed)
8. **Missed DCP Opportunities** — info box + table of 13 sessions that should have had DCP
9. **USD Sensitivity** — table at $2/$3/$5 per Mtok
10. **Insights** — 5-6 bullet points including missed DCP analysis
11. **Reddit-Ready Summary** — copy-paste card with headline stats

### CSS Tooltips
11 hover-based tooltips (no JS) on metric labels, each explaining the concept and how it's calculated.

---

## How to Run

```powershell
# From the scripts directory
cd C:\development\opencode\.conductor\tracks\20260613-dcp-token-savings-analysis\scripts

# Full run (aggregate + HTML)
python generate_report.py

# Aggregate only (no HTML)
python generate_report.py --aggregate-only

# Verify (7 checks, exit 0 = pass)
python generate_report.py --verify

# Analyze a different number of most-recent sessions (re-runnable; default 100)
python generate_report.py --sessions 250
python generate_report.py --sessions 250 --verify
```

**Requirements:** Python 3 stdlib only. No pip installs. Read-only on all data sources.

**Re-running for future analysis:** add `--sessions N` (default 100) to analyze a different number of most-recent sessions. Full runbook: `docs/workflows/re-run-dcp-report.md`.

**IMPORTANT:** File tools (Read/Write/Edit/Glob/Grep) are BROKEN in this environment ("Bun is not defined"). All file I/O must use the `bash` tool → PowerShell → Python temp-file pattern. See `~/.config/opencode/docs/troubleshooting/tool-failure-bun-undefined.md`.

---

## What's Been Done (Chronological)

1. **Phase 0-4 (original plan):** Built v1 report with one-time savings model. All 26 tasks complete.
2. **User audit request:** "Is there a chance you are not matching up the DCP calls?" — Full audit found session matching was correct but savings model was wrong (one-time vs compound).
3. **Report v2:** Rewrote with compound savings model. 62.4M tokens saved, 31.9x multiplier.
4. **Report v3:** Added CSS tooltips, "Understanding This Report" section, persistent OT vs compound banner, DCP eligibility analysis. Initially used 100K threshold → found 0 missed sessions.
5. **Threshold correction:** user challenged the 100K threshold → revised missed-DCP criteria to **≥10 requests AND ≥10K peak input**, finding **13 missed sessions**. Full rationale in the *Missed DCP Threshold* section above.
6. **Report v3.1:** Added missed DCP opportunities table, updated insights/tooltips with DCP config details, updated per-model eligibility flags, updated Reddit card.

---

## Pending / Next Steps

### Immediate (user may request)
- **User review of v3.1 report** — user was about to open the HTML and review
- **Possible threshold tuning** — user may want to adjust the ≥10 requests / ≥10K peak criteria
- **Possible visual tweaks** — user may want styling changes after reviewing

### Potential Enhancements
1. **Time-series chart** — show DCP savings over time (by date) to show improvement trend
2. **Model comparison table** — full table (not just bar chart) with all metrics per model
3. **DCP block detail view** — expandable sections showing what was compressed in top sessions
4. **Estimated missed savings** — calculate potential compound savings for the 13 missed sessions (estimate: ~1-1.5M tokens based on average multiplier)
5. **Config recommendation** — based on the 13 missed sessions, suggest DCP config changes (e.g., lower `iterationNudgeThreshold` from 15 to 10, or lower `minContextLimit` from 50K to 20K)

### Track Ledger Updates
- `metadata.json` keyOutcomes may need updating with v3.1 numbers (compound 66.3M, 32.8x, 13 missed)
- `plan.md` deviations section should note the threshold correction
- Execution log should get a v3.1 entry

### Known Minor Issues
- `model_usage` entries in aggregate.json may show `sessions=0` for some models (cosmetic, doesn't affect HTML rendering)
- Numbers shift slightly between runs because the current live session is adding data in real-time
- `opencode/north-mini-code-free` model has a DCP file with 172.5K peak input but 0 blocks — DCP initialized but never compressed (edge case, correctly shown in report)

---

## Environment Notes

- **OS:** Windows (win32)
- **Shell:** PowerShell 7+ via bash tool
- **Python:** 3.13.2
- **OpenCode storage:** `C:\Users\DaveWitkin\.local\share\opencode\`
- **DCP plugin:** `@tarquinen/opencode-dcp` (installed via npm)
- **Temp work dir:** `C:\Users\DaveWi~1\AppData\Local\Temp\opencode`
