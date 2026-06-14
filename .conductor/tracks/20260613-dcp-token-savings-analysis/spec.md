# Spec: DCP Token-Savings Analysis (Last 100 Sessions)

- **Track ID:** `20260613-dcp-token-savings-analysis`
- **Created:** 2026-06-13
- **Owner:** Planner -> Build agent
- **Plan:** see `plan.md` (authoritative source of truth)

---

## Goal / Outcome

Produce a single, self-contained, human-readable **HTML report** that quantifies
how many tokens (and estimated USD) the **Dynamic Context Pruning (DCP)** plugin
has saved across the **last 100 OpenCode sessions**, with a per-model breakdown.

The report must answer three questions:

1. **Overall totals** across the 100 sessions -- total tokens used, total tokens
   saved via DCP (as a number **and** a percentage), and estimated **USD saved**
   using an internet-researched average model input price (with a sensitivity
   range).
2. **Per-model breakdown** -- tokens saved per model, and how often DCP is invoked
   per model (to test the hypothesis that some models call DCP rarely or never).
3. **Total token savings** -- the headline number.

## Current Track Fit Decision

**Decision: Create a NEW track.** No existing track covers DCP savings analysis.
Adjacent completed work (`20260526-system-prompt-token-audit`,
`20260531-prompt-schema-overhead-research`) covers system-prompt and schema
overhead, not DCP pruning savings. Reusing them would conflate concerns.

## Constraints / Non-Goals

- **No external network calls at runtime.** Pricing is grounded by Planner
  research (see `## Cost Grounding` below) and hard-coded into the report; the
  build script must work offline.
- **No third-party Python packages.** Python 3.13 stdlib only (the host has
  Python 3.13.2 installed). Do not `pip install` anything.
- **DCP state files are the ONLY authoritative savings source.** OpenCode part
  storage does NOT persist compression (verified: zero `compress` / DCP markers
  in `part/` storage). Do not attempt to derive savings from opencode parts.
- **Read-only analysis.** The script MUST NOT write to, delete, or move any file
  under `C:\Users\DaveWitkin\.local\share\opencode\storage\` or the DCP package
  directory. All reads are non-destructive.
- **Single deliverable.** Exactly one HTML file. No CSV shards, no chart servers,
  no external assets (inline any CSS/JS). The HTML must open from disk in a
  browser with no dependencies.
- **Windows + PowerShell execution.** opencode's built-in `read`/`glob`/`grep`
  tools are currently broken ("Bun is not defined"). The build agent MUST drive
  Python via the `bash` tool using PowerShell. Use `Get-Content` / file paths
  only inside the Python script itself.
- **Non-goals:** live monitoring, dashboards, alerting, per-message drill-down,
  comparing against tokenscope's per-session export, fixing the broken
  tokenscope batch export, or modifying DCP configuration.

## Definition of Done

The track is complete when ALL of these hold:

1. The HTML report exists at the exact required path and is openable in a
   browser (no broken links, no external asset 404s).
2. The report contains the three required sections (Overall Totals, Per-Model
   Breakdown, Total Savings) with all required figures.
3. The numbers are reproducible: re-running the generator script on the same
   data yields byte-identical (or within stated sort-stability) figures.
4. A verification command prints a sanity summary to stdout and the planner's
   cross-checks (session count = 100; per-block saved >= 0 for every block;
   total saved matches sum across sessions) pass.
5. `plan.md` every non-deferred checkbox is `[x]`; validation reports 0 FAIL;
   the execution log and ledgers (`tracks.md` + `tracks-ledger.md`) are updated
   and agree.

## In Scope

- Reading the last 100 sessions (selected by `session/<projHash>/ses_<id>.json`
  `time.updated`, descending; take top 100).
- Reading `storage/plugin/dcp/ses_<sessionID>.json` for each of those 100
  sessions to compute per-block savings
  (`= compressedTokens - summaryTokens`).
- Joining DCP block `compressMessageId` -> opencode `message/<sesID>/msg_<id>.json`
  -> `model{providerID, modelID}` for per-model attribution.
- Summing opencode `part/<msgID>/prt_<id>.json` `tokens` (from `step-finish`
  parts) across the 100 sessions for total tokens used.
- Aggregating and emitting one self-contained HTML report.
- A small verification/validate step that sanity-checks the numbers.

## Out of Scope

- Sessions outside the last 100.
- USD precision beyond 2 decimals / speculative fine-grained pricing for
  private models (`zai-coding-plan/glm-5*`) not in public price tables.
- Modifying DCP, opencode, or any storage file.
- Real-time / streaming analysis.
- Chart libraries; use inline CSS bars / tables only.

## Required Artifacts

| Artifact | Path (relative to repo root) | Purpose |
|---|---|---|
| spec.md | `.conductor/tracks/20260613-dcp-token-savings-analysis/spec.md` | This file |
| plan.md | `.conductor/tracks/20260613-dcp-token-savings-analysis/plan.md` | Authoritative task plan |
| metadata.json | `.conductor/tracks/20260613-dcp-token-savings-analysis/metadata.json` | Track metadata |
| generator script | `.conductor/tracks/20260613-dcp-token-savings-analysis/scripts/generate_report.py` | Python stdlib analyzer -> HTML |
| **HTML report (deliverable)** | `.conductor/tracks/20260613-dcp-token-savings-analysis/artifacts/dcp-savings-report.html` | Final self-contained report |
| aggregate JSON | `.conductor/tracks/20260613-dcp-token-savings-analysis/artifacts/aggregate.json` | Machine-readable numbers backing the HTML |
| execution log | `.conductor/tracks/20260613-dcp-token-savings-analysis/execution-logs/<YYYYMMDD-HHMM>.md` | Deviations, counts, validation record |
| ledger updates | `.conductor/tracks.md`, `.conductor/tracks-ledger.md` | Status/date agreement |

## Data Sources (authoritative paths)

```
OpenCode storage root:   C:\Users\DaveWitkin\.local\share\opencode\storage\
  session\<projHash>\ses_<id>.json   -> time.updated (recency), id, title
  message\<sesID>\msg_<id>.json      -> model{providerID, modelID}, role, time
  part\<msgID>\prt_<id>.json         -> type=="step-finish" -> tokens{total,input,output,reasoning,cache{read,write}}
DCP state (SAVINGS SOURCE):
  storage\plugin\dcp\ses_<id>.json   -> prune.messages.blocksById[*]
                                        saved per block = compressedTokens - summaryTokens
                                        (stats.totalPruneTokens is a cumulative cross-check)
```

### Verified DCP per-session schema (excerpt)

```jsonc
{
  "prune": { "messages": {
    "blocksById": {
      "<blockId>": {
        "compressedTokens": 191049,   // ORIGINAL tokens compressed (savings base)
        "summaryTokens":    17798,     // tokens remaining after compression
        "mode": "range",               // "range" | "message"
        "compressMessageId": "msg_...",  // -> opencode message -> model
        "anchorMessageId":   "msg_...",
        "startId": "m0123", "endId": "m0140", "topic": "..."
      }
    }
  }},
  "stats": { "totalPruneTokens": 191284, "pruneTokenCounter": 191284 }
}
```

**Verified example:** one block had sum compressedTokens=191,049, sum
summaryTokens=17,798 -> **saved = 173,251 tokens**; `stats.totalPruneTokens` =
191,284 (~ sum compressedTokens, a cross-check ceiling).

## Cost Grounding (Planner web research, 2026)

DCP prunes the **input** side of the request (obsolete tool outputs are replaced
with summaries before sending to the model), so savings are valued at the
**input** token price. Cached input is ~10% of full input; the report uses a
blended input rate.

| Source (2026) | Representative input $/M-tok |
|---|---|
| Claude Sonnet 4.6 | $3.00 |
| Claude Opus 4.6 | $5.00 |
| GPT-4.1 | $2.00 |
| GPT-5.4 | $2.50 |
| Gemini 2.5 Pro | $1.25 |

- **Blended default = $3.00 / M input tokens** (mid-frontier).
- Report **MUST** also show a sensitivity table at **$2 / $3 / $5 per M**.
- Report **MUST** cite the source list and state the input-vs-output assumption.
- User's actual models (`zai-coding-plan/glm-5`, `glm-5.2`) are not in public
  tables, so the blended default is used and clearly labelled as an estimate.

Sources consulted: fungies.io, awesomeagents.ai, pecollective.com,
stochasticsandbox.com, tldl.io (all 2026).

## Requirements

- [ ] R1. Script selects exactly the **last 100 sessions** by
      `session/.../ses_*.json` `time.updated` descending (fewer only if fewer
      exist, logged as a deviation).
- [ ] R2. For each selected session, total DCP savings = sum over every block in
      `prune.messages.blocksById` of `(compressedTokens - summaryTokens)`. Missing
      DCP file or empty `blocksById` => 0 saved.
- [ ] R3. Total tokens used across the 100 sessions = sum of `tokens.total` over
      all `part/.../prt_*.json` whose `type == "step-finish"` belonging to those
      sessions.
- [ ] R4. Per-model attribution: for each DCP block, resolve
      `compressMessageId` -> message -> `model`; fallback to the session's
      majority model if unresolved. Output tokens saved per model **and** DCP
      call count per model (number of blocks per model).
- [ ] R5. Overall totals section shows: total tokens used, total tokens saved
      (number **and** `saved/used` %), USD saved at blended $3/M, and the
      $2/$3/$5 sensitivity table.
- [ ] R6. Per-model breakdown section shows, per model: DCP calls (blocks),
      tokens saved, % of total savings, and total tokens used (so
      "rarely/never-calls-DCP" models are visible).
- [ ] R7. Total token savings headline is prominent and consistent across all
      sections (no divergent totals).
- [ ] R8. HTML is a single self-contained file (inline CSS; no external
      requests); opens from disk in a browser.
- [ ] R9. Script is Python 3 stdlib only, idempotent (re-run yields same
      figures), and performs **no writes** outside its own artifact dir.
- [ ] R10. A `--verify`/validate mode prints: session count, total used, total
      saved, per-block min saved (must be >= 0), and sum-saved vs
      `stats.totalPruneTokens` cross-check.

## Non-Requirements

- Live pricing fetch or currency conversion.
- Per-message or per-turn drill-down inside the HTML.
- Statistical modeling / confidence intervals.
- Integration with tokenscope.
- Charts via external libraries (inline CSS bars are sufficient and required).

## Acceptance Criteria

1. **A1 -- Deliverable present & valid:** `artifacts/dcp-savings-report.html`
   exists, is non-trivial in size, and a browser open shows all three sections
   with no unrendered placeholders.
2. **A2 -- Counts correct:** the report's session count is 100 (or fewer, with a
   logged deviation); total-saved equals the sum of per-model saved equals the
   sum of per-session saved.
3. **A3 -- Percent present:** overall section shows savings as both an absolute
   number and a percentage of total tokens used.
4. **A4 -- USD + sensitivity present:** overall section shows USD at $3/M and the
   $2/$3/$5 sensitivity table, with source citation and the input-token
   assumption stated.
5. **A5 -- Per-model call counts present:** per-model table includes DCP call
   (block) counts so rarely/never-calling models are identifiable.
6. **A6 -- Reproducible:** a second run produces identical headline numbers
   (modulo deterministic sort tie-breaks).
7. **A7 -- No destructive ops:** a hash snapshot of `storage/plugin/dcp/` before
   and after shows no changes.
8. **A8 -- Conductor gate:** plan all `[x]`, validation 0 FAIL, execution log
   present, ledgers updated & agreeing.
