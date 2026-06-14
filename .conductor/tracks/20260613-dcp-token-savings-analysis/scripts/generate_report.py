#!/usr/bin/env python3
"""DCP Token-Savings Analysis -- generate self-contained HTML report (v3).

Quantifies Dynamic Context Pruning (DCP) token + USD savings across the last
100 OpenCode sessions. Uses COMPOUND savings model (savings x subsequent requests).

v3 changes: CSS tooltips, "Understanding This Report" section, missed-DCP analysis,
persistent one-time vs compound banner, per-model DCP eligibility indicators.

Python 3 stdlib only. Read-only on all data sources. Zero external dependencies.

Data sources:
  - Session/message/part data: SQLite (opencode.db)
  - DCP savings state: JSON files at storage/plugin/dcp/
"""

import argparse
import json
import glob
import os
import sys
import html
import sqlite3
import datetime
from collections import Counter, defaultdict

STORAGE = r"C:\Users\DaveWitkin\.local\share\opencode\storage"
DCP_DIR = os.path.join(STORAGE, "plugin", "dcp")
DB_PATH = r"C:\Users\DaveWitkin\.local\share\opencode\opencode.db"
LAST_N = 100
BLENDED_USD_PER_MTOK = 3.00
SENSITIVITY_USD = [2.00, 3.00, 5.00]
DCP_ELIGIBLE_MIN_REQUESTS = 10   # sessions with >= this many requests should benefit from DCP
DCP_ELIGIBLE_MIN_PEAK_INPUT = 10_000  # AND peak context >= this (DCP has compressed at 12K)
DCP_HARD_LIMIT = 100_000   # DCP maxContextLimit - force compress above this
DCP_SOFT_LIMIT = 50_000    # DCP minContextLimit - allow compress above this
PRICE_SOURCES = [
    "fungies.io", "awesomeagents.ai", "pecollective.com",
    "stochasticsandbox.com", "tldl.io (2026)",
]
OUT_HTML = os.path.join(os.path.dirname(__file__), "..", "artifacts", "dcp-savings-report.html")
OUT_AGG = os.path.join(os.path.dirname(__file__), "..", "artifacts", "aggregate.json")


# === DATA LAYER ===

def select_last_n_sessions(n=LAST_N, conn=None):
    own_conn = conn is None
    if own_conn:
        conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, time_updated FROM session WHERE id IN (SELECT DISTINCT session_id FROM message) ORDER BY time_updated DESC LIMIT ?",
        (n,),
    )
    rows = cur.fetchall()
    if own_conn:
        conn.close()
    return [(r[1], r[0], {}) for r in rows]


def tokens_used_for(sid, conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(json_extract(p.data, '$.tokens.total')), 0) FROM part p JOIN message m ON p.message_id = m.id WHERE m.session_id = ? AND json_extract(p.data, '$.type') = 'step-finish'",
        (sid,),
    )
    return cur.fetchone()[0] or 0


def max_input_for(sid, conn):
    """Peak single-request input tokens -- proxy for max context size."""
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(json_extract(p.data, '$.tokens.input')) FROM part p JOIN message m ON p.message_id = m.id WHERE m.session_id = ? AND json_extract(p.data, '$.type') = 'step-finish'",
        (sid,),
    )
    return cur.fetchone()[0] or 0


def cache_read_for(sid, conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(json_extract(p.data, '$.tokens.cache.read')), 0) FROM part p JOIN message m ON p.message_id = m.id WHERE m.session_id = ? AND json_extract(p.data, '$.type') = 'step-finish'",
        (sid,),
    )
    return cur.fetchone()[0] or 0


def step_finish_count(sid, conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(DISTINCT m.id) FROM message m JOIN part p ON p.message_id = m.id WHERE m.session_id = ? AND json_extract(p.data, '$.type') = 'step-finish'",
        (sid,),
    )
    return cur.fetchone()[0] or 0


def message_count(sid, conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM message WHERE session_id = ?", (sid,))
    return cur.fetchone()[0] or 0


def majority_model(sid, conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT json_extract(m.data, '$.providerID') || '/' || json_extract(m.data, '$.modelID') as model, COUNT(*) as cnt FROM message m WHERE m.session_id = ? AND json_extract(m.data, '$.role') = 'assistant' AND json_extract(m.data, '$.modelID') IS NOT NULL GROUP BY model ORDER BY cnt DESC LIMIT 1",
        (sid,),
    )
    row = cur.fetchone()
    return row[0] if row else "unknown"


def has_dcp_file(sid):
    return os.path.exists(os.path.join(DCP_DIR, sid + ".json"))


def get_ordered_sf_msgs(sid, conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT m.id FROM message m JOIN part p ON p.message_id = m.id WHERE m.session_id = ? AND json_extract(p.data, '$.type') = 'step-finish' ORDER BY m.time_created ASC",
        (sid,),
    )
    return [r[0] for r in cur.fetchall()]


def compute_session_dcp(sid, conn):
    fpath = os.path.join(DCP_DIR, sid + ".json")
    result = {"has_dcp": False, "one_time_saved": 0, "compound_saved": 0, "stats_total": 0, "blocks": [], "block_count": 0}
    if not os.path.exists(fpath):
        return result
    try:
        d = json.load(open(fpath, encoding="utf-8"))
    except Exception:
        return result
    result["has_dcp"] = True
    result["stats_total"] = d.get("stats", {}).get("totalPruneTokens", 0)
    blocks = d.get("prune", {}).get("messages", {}).get("blocksById", {})
    if not blocks:
        return result
    sf_msgs = get_ordered_sf_msgs(sid, conn)
    sf_index = {mid: i for i, mid in enumerate(sf_msgs)}
    total_requests = len(sf_msgs)
    one_time = 0
    compound = 0
    block_records = []
    for bid, b in sorted(blocks.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        compressed = b.get("compressedTokens", 0)
        summary = b.get("summaryTokens", 0)
        saved = compressed - summary
        one_time += saved
        cm = b.get("compressMessageId")
        remaining = 0
        if cm and cm in sf_index:
            anchor_idx = sf_index[cm]
            remaining = max(0, total_requests - anchor_idx - 1)
        else:
            remaining = int(total_requests * 0.4)
        block_compound = saved * remaining
        compound += block_compound
        block_records.append({"blockId": b.get("blockId"), "saved": saved, "compound_saved": block_compound, "remaining_requests": remaining, "compressedTokens": compressed, "summaryTokens": summary, "compressMessageId": cm, "topic": b.get("topic", "")})
    result["one_time_saved"] = one_time
    result["compound_saved"] = compound
    result["blocks"] = block_records
    result["block_count"] = len(block_records)
    return result

# === AGGREGATION ===

def aggregate(selected, conn):
    sessions_data = []
    total_used = 0; total_cache_read = 0; total_one_time = 0; total_compound = 0
    total_stats = 0; total_requests = 0; total_blocks = 0
    model_used = Counter(); model_one_time = Counter(); model_compound = Counter()
    model_calls = Counter(); model_sessions = Counter(); model_dcp_sessions = Counter()
    model_missed = Counter(); model_max_input = defaultdict(int)
    sessions_with_dcp = 0; sessions_with_savings = 0
    sessions_missed = 0; sessions_short = 0
    missed_sessions_list = []

    for _updated_ms, sid, _extra in selected:
        used = tokens_used_for(sid, conn)
        cache = cache_read_for(sid, conn)
        reqs = step_finish_count(sid, conn)
        msgs = message_count(sid, conn)
        mdl = majority_model(sid, conn)
        max_input = max_input_for(sid, conn)
        dcp = compute_session_dcp(sid, conn)
        total_used += used; total_cache_read += cache; total_requests += reqs
        total_one_time += dcp["one_time_saved"]; total_compound += dcp["compound_saved"]
        total_stats += dcp["stats_total"]; total_blocks += dcp["block_count"]
        model_used[mdl] += used; model_sessions[mdl] += 1
        if max_input > model_max_input[mdl]:
            model_max_input[mdl] = max_input

        if dcp["has_dcp"]:
            model_dcp_sessions[mdl] += 1; sessions_with_dcp += 1
        else:
            # Classify non-DCP sessions
            if reqs >= DCP_ELIGIBLE_MIN_REQUESTS and max_input >= DCP_ELIGIBLE_MIN_PEAK_INPUT:
                sessions_missed += 1
                model_missed[mdl] += 1
                missed_sessions_list.append({
                    "session_id": sid, "model": mdl,
                    "tokens_used": used, "requests": reqs,
                    "max_input": max_input, "messages": msgs,
                })
            else:
                sessions_short += 1

        if dcp["compound_saved"] > 0:
            sessions_with_savings += 1
            model_one_time[mdl] += dcp["one_time_saved"]
            model_compound[mdl] += dcp["compound_saved"]
            model_calls[mdl] += dcp["block_count"]

        sessions_data.append({
            "session_id": sid, "model": mdl, "tokens_used": used,
            "cache_read": cache, "requests": reqs, "messages": msgs,
            "max_input": max_input,
            "has_dcp": dcp["has_dcp"], "one_time_saved": dcp["one_time_saved"],
            "compound_saved": dcp["compound_saved"], "stats_total": dcp["stats_total"],
            "block_count": dcp["block_count"], "blocks": dcp["blocks"],
        })

    pct_ot = round(total_one_time / total_used * 100, 2) if total_used else 0.0
    pct_comp = round(total_compound / total_used * 100, 2) if total_used else 0.0
    mult = round(total_compound / total_one_time, 1) if total_one_time else 0.0
    usd_sens = {}
    for rate in SENSITIVITY_USD:
        usd_sens[str(int(rate))] = round(total_compound / 1_000_000 * rate, 2)

    all_models = set(model_used) | set(model_compound) | set(model_calls)
    per_model = []
    for mdl in all_models:
        mu = model_used.get(mdl, 0); ms_ot = model_one_time.get(mdl, 0)
        ms_comp = model_compound.get(mdl, 0); mc = model_calls.get(mdl, 0)
        m_sess = model_sessions.get(mdl, 0); m_dcp = model_dcp_sessions.get(mdl, 0)
        m_missed = model_missed.get(mdl, 0)
        m_max_in = model_max_input.get(mdl, 0)
        pct = round(ms_comp / total_compound * 100, 2) if total_compound else 0.0
        act = round(m_dcp / m_sess * 100, 1) if m_sess else 0.0
        per_model.append({
            "model": mdl, "sessions": m_sess, "dcp_sessions": m_dcp,
            "missed_sessions": m_missed, "max_input": m_max_in,
            "activation_rate": act, "tokens_used": mu,
            "dcp_calls": mc, "one_time_saved": ms_ot,
            "compound_saved": ms_comp, "pct_of_savings": pct,
        })
    per_model.sort(key=lambda x: (-x["compound_saved"], x["model"]))
    top_sessions = sorted(
        [s for s in sessions_data if s["compound_saved"] > 0],
        key=lambda x: -x["compound_saved"],
    )[:20]

    return {
        "generated_at": datetime.datetime.now().isoformat() + "Z",
        "session_count": len(selected),
        "sessions_with_dcp": sessions_with_dcp,
        "sessions_with_savings": sessions_with_savings,
        "sessions_missed": sessions_missed,
        "sessions_short": sessions_short,
        "missed_sessions_detail": sorted(missed_sessions_list, key=lambda x: -x["tokens_used"]),
        "totals": {
            "tokens_used": total_used, "cache_read": total_cache_read,
            "one_time_saved": total_one_time, "compound_saved": total_compound,
            "stats_totalPruneTokens": total_stats,
            "pct_one_time": pct_ot, "pct_compound": pct_comp,
            "multiplier": mult, "total_requests": total_requests,
            "total_blocks": total_blocks,
            "usd_compound_blended_3": usd_sens.get("3", 0.0),
            "usd_sensitivity": usd_sens,
        },
        "per_model": per_model,
        "top_sessions": [
            {"session_id": s["session_id"], "model": s["model"],
             "tokens_used": s["tokens_used"], "requests": s["requests"],
             "one_time_saved": s["one_time_saved"],
             "compound_saved": s["compound_saved"],
             "block_count": s["block_count"],
             "multiplier": round(s["compound_saved"] / s["one_time_saved"], 1) if s["one_time_saved"] else 0,
             "blocks": s["blocks"][:5]}
            for s in top_sessions
        ],
        "sessions": sessions_data,
    }


# === FORMATTING ===

def fmt_tokens(n):
    if n >= 1_000_000: return "%.1fM" % (n / 1_000_000)
    elif n >= 1_000: return "%.1fK" % (n / 1_000)
    return str(n)

def fmt_usd(n): return "$%.2f" % n
def fmt_pct(n): return "%.1f%%" % n

def model_short(mdl):
    parts = mdl.split("/")
    return parts[-1] if len(parts) >= 2 else mdl

# === HTML BUILDER ===

def tip(label, tip_text):
    """Wrap a label with a CSS tooltip."""
    return '<span class="tip-wrap">%s<span class="tip-i">i</span><span class="tip-body">%s</span></span>' % (label, tip_text)


def build_html(agg):
    t = agg["totals"]
    ts_ot = t["one_time_saved"]; ts_comp = t["compound_saved"]; tu = t["tokens_used"]
    pct_ot = t["pct_one_time"]; pct_comp = t["pct_compound"]; mult = t["multiplier"]
    usd3 = t["usd_compound_blended_3"]; usd_sens = t["usd_sensitivity"]
    sc = agg["session_count"]; sw_dcp = agg["sessions_with_dcp"]; sw_sav = agg["sessions_with_savings"]
    sw_missed = agg.get("sessions_missed", 0); sw_short = agg.get("sessions_short", 0)
    without_dcp = tu + ts_comp
    max_s = max((s["compound_saved"] for s in agg.get("top_sessions", [])), default=1) or 1
    max_m = max((m["compound_saved"] for m in agg.get("per_model", [])), default=1) or 1

    # --- Top sessions bars ---
    session_rows = ""
    for i, s in enumerate(agg.get("top_sessions", [])[:15]):
        bw = int(s["compound_saved"] / max_s * 100)
        otw = int(s["one_time_saved"] / max_s * 100) if max_s else 0
        session_rows += '<div class="bar-row"><div class="bar-label">#%d</div><div class="bar-track"><div class="bar-fill-ot" style="width:%d%%"></div><div class="bar-fill-comp" style="width:%d%%"></div></div><div class="bar-value">%s</div><div class="bar-meta">%d req / %d blk / %.1fx</div></div>' % (i+1, otw, bw, fmt_tokens(s["compound_saved"]), s["requests"], s["block_count"], s["multiplier"])

    # --- Per-model bars with DCP eligibility ---
    model_rows = ""
    for m in agg.get("per_model", []):
        ms = m["compound_saved"]; mc = m["dcp_calls"]
        bw = int(ms / max_m * 100) if max_m else 0
        otw = int(m["one_time_saved"] / max_m * 100) if max_m else 0
        has = ms > 0
        cc = "#4f46e5" if has else "#e5e7eb"
        co = "#c7d2fe" if has else "#f3f4f6"
        # Eligibility indicator
        missed = m.get("missed_sessions", 0)
        max_in = m.get("max_input", 0)
        if missed > 0:
            elig = '<span class="elig-flag missed"> \u26a0 %d missed</span>' % missed
        elif m["sessions"] > 0 and m["dcp_sessions"] == 0:
            elig = '<span class="elig-flag short"> no DCP needed</span>'
        else:
            elig = ""
        model_rows += '<div class="bar-row"><div class="bar-label">%s</div><div class="bar-track"><div class="bar-fill-ot" style="width:%d%%;background:%s"></div><div class="bar-fill-comp" style="width:%d%%;background:%s"></div></div><div class="bar-value">%s</div><div class="bar-meta">%d calls | %d/%d sess | max %s%s</div></div>' % (html.escape(model_short(m["model"])), otw, co, bw, cc, fmt_tokens(ms) if has else "0", mc, m["dcp_sessions"], m["sessions"], fmt_tokens(max_in), elig)

    usd_rows = ""
    for rate in SENSITIVITY_USD:
        key = str(int(rate)); val = usd_sens.get(key, 0.0)
        usd_rows += '<tr><td>$%.0f/M</td><td>$%.2f</td></tr>' % (rate, val)

    pct_ci = int(pct_comp)
    donut_pct = min(pct_comp, 100)
    donut_deg = int(donut_pct * 3.6)

    no_dcp = [m for m in agg["per_model"] if m["dcp_calls"] == 0 and m["sessions"] > 0]
    best = max(agg.get("top_sessions", []), key=lambda x: x["multiplier"]) if agg.get("top_sessions") else None

    # --- Insights ---
    insights = ""
    missed_detail = agg.get("missed_sessions_detail", [])
    if sw_missed == 0:
        insights += "<li><strong>No missed DCP opportunities.</strong> All %d sessions without DCP were too short (under %d requests or %s peak context).</li>" % (sw_short, DCP_ELIGIBLE_MIN_REQUESTS, fmt_tokens(DCP_ELIGIBLE_MIN_PEAK_INPUT))
    else:
        missed_tokens = sum(s["tokens_used"] for s in missed_detail)
        insights += "<li><strong>%d session(s) missed DCP</strong> (\u2265%d requests and \u2265%s peak context, but no compression triggered): %s tokens consumed across these sessions. DCP was installed but its nudge system didn\u2019t fire \u2014 likely because context stayed under the %s hard limit and the soft nudge (every 5 turns after turn 15) didn\u2019t prompt the model to compress.</li>" % (
            sw_missed, DCP_ELIGIBLE_MIN_REQUESTS, fmt_tokens(DCP_ELIGIBLE_MIN_PEAK_INPUT),
            fmt_tokens(missed_tokens), fmt_tokens(DCP_HARD_LIMIT))
    if no_dcp:
        insights += "<li><strong>%d model(s) never triggered DCP:</strong> %s. These were used only on short sessions with small context windows.</li>" % (len(no_dcp), ", ".join(html.escape(model_short(m["model"])) for m in no_dcp[:5]))
    if best:
        insights += "<li><strong>Best compound multiplier:</strong> Session with %d requests achieved <strong>%.1fx</strong> \u2014 %s one-time compression amplified to %s compound savings.</li>" % (best["requests"], best["multiplier"], fmt_tokens(best["one_time_saved"]), fmt_tokens(best["compound_saved"]))
    insights += "<li><strong>DCP activation:</strong> %d of %d sessions (%.0f%%) have DCP data. %d sessions were too short to need it.</li>" % (sw_dcp, sc, sw_dcp / sc * 100 if sc else 0, sw_short + sc - sw_dcp)
    insights += "<li><strong>Compound effect is the story:</strong> One-time compression removed %s tokens. Real API savings: <strong>%s (%.1fx more)</strong>.</li>" % (fmt_tokens(ts_ot), fmt_tokens(ts_comp), mult)
    avg_blk = t["total_blocks"] / sw_dcp if sw_dcp else 0
    insights += "<li><strong>Average DCP blocks per active session:</strong> %.1f blocks across %d sessions.</li>" % (avg_blk, sw_dcp)


    missed_table_rows = ""
    for ms in missed_detail[:15]:
        missed_table_rows += "<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (
            html.escape(ms["session_id"][:24] + "..."),
            html.escape(model_short(ms["model"])),
            ms["requests"],
            fmt_tokens(ms["max_input"]),
            fmt_tokens(ms["tokens_used"]),
        )
    missed_table_html = ""
    if missed_detail:
        missed_tokens_total = sum(s["tokens_used"] for s in missed_detail)
        missed_table_html = """<h2>Missed DCP Opportunities</h2>
<div class="missed-info"><strong>%d sessions</strong> had enough activity for DCP (\u2265%d requests + \u2265%s peak context) but DCP didn\u2019t trigger. These sessions used <strong>%s tokens</strong> collectively. DCP was installed (files date to March 2026) but its soft nudge system (every 5 turns after turn 15) didn\u2019t prompt compression \u2014 likely because context stayed under the %s hard limit.</div>
<table class="missed-table">
<thead><tr><th>Session</th><th>Model</th><th>Requests</th><th>Peak Context</th><th>Tokens Used</th></tr></thead>
<tbody>%s</tbody>
</table>""" % (
            len(missed_detail),
            DCP_ELIGIBLE_MIN_REQUESTS,
            fmt_tokens(DCP_ELIGIBLE_MIN_PEAK_INPUT),
            fmt_tokens(missed_tokens_total),
            fmt_tokens(DCP_HARD_LIMIT),
            missed_table_rows,
        )

    # --- Reddit card ---
    missed_detail_for_card = agg.get("missed_sessions_detail", [])
    missed_tokens_card = sum(s["tokens_used"] for s in missed_detail_for_card)
    reddit = '<div class="reddit-card"><div class="reddit-header">Post-Ready Summary</div><div class="reddit-body"><p><strong>DCP saved %s tokens across %d sessions</strong> \u2014 %s of total usage, or <strong>%s in API costs</strong> at $3/M.</p><p>Without DCP, total cost would be <strong>%s tokens</strong> instead of %s. Compound effect amplifies one-time compression by <strong>%.1fx</strong>.</p><ul><li>%d%% session DCP activation (%d/%d sessions); %d too short, %d missed (%s tokens at risk)</li><li>%d models tracked, %d never triggered DCP</li><li>Top session: %s compound on %s used (%.1fx)</li></ul></div></div>' % (fmt_tokens(ts_comp), sc, fmt_pct(pct_comp), fmt_usd(usd3), fmt_tokens(without_dcp), fmt_tokens(tu), mult, int(sw_dcp/sc*100) if sc else 0, sw_dcp, sc, sw_short, sw_missed, fmt_tokens(missed_tokens_card), len(agg["per_model"]), len(no_dcp), fmt_tokens(agg["top_sessions"][0]["compound_saved"]) if agg.get("top_sessions") else "0", fmt_tokens(agg["top_sessions"][0]["tokens_used"]) if agg.get("top_sessions") else "0", agg["top_sessions"][0]["multiplier"] if agg.get("top_sessions") else 0)
    # --- CSS ---
    css = """
  :root{--bg:#0f172a;--card:#1e293b;--card2:#334155;--accent:#4f46e5;--accent2:#818cf8;--green:#22c55e;--blue:#3b82f6;--orange:#f59e0b;--red:#ef4444;--amber:#fbbf24;--text:#f1f5f9;--text2:#94a3b8;--text3:#64748b;--border:#475569}
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;padding:20px;max-width:1100px;margin:0 auto}
  h1{font-size:1.8rem;font-weight:700;margin-bottom:4px}
  h2{font-size:1.3rem;font-weight:600;color:var(--accent2);margin-top:32px;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--border)}
  h3{font-size:1.05rem;font-weight:600;color:var(--text);margin-bottom:8px}
  .subtitle{color:var(--text2);font-size:.9rem;margin-bottom:24px}
  .note{color:var(--text3);font-size:.85rem}
  .hero{background:linear-gradient(135deg,#1e293b 0%,#312e81 100%);border-radius:16px;padding:36px;text-align:center;margin-bottom:28px;border:1px solid var(--border)}
  .hero-num{font-size:3.5rem;font-weight:800;color:var(--green);letter-spacing:-1px}
  .hero-label{font-size:1.1rem;color:var(--text2);margin-top:8px}
  .hero-sub{margin-top:16px;font-size:1rem;color:var(--text)}
  .hero-sub strong{color:var(--accent2)}
  .hero-badges{display:flex;gap:16px;justify-content:center;margin-top:20px;flex-wrap:wrap}
  .badge{background:rgba(79,70,229,.2);border:1px solid var(--accent);border-radius:8px;padding:8px 16px;font-size:.95rem}
  .badge strong{color:var(--green)}
  .explain-box{background:var(--card);border-radius:12px;padding:20px 24px;border:1px solid var(--border);border-left:4px solid var(--accent2);margin:0 0 28px}
  .explain-box h3{color:var(--accent2);margin-bottom:10px}
  .explain-box p{font-size:.88rem;color:var(--text);margin:6px 0;line-height:1.65}
  .explain-box .example{background:var(--bg);border-radius:8px;padding:12px 16px;margin:10px 0;font-size:.82rem;color:var(--text2);border:1px solid var(--border)}
  .explain-box .example strong{color:var(--green)}
  .ot-comp-banner{background:rgba(79,70,229,.1);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:0 0 16px;font-size:.85rem;color:var(--text2);display:flex;align-items:center;gap:8px;flex-wrap:wrap}
  .ot-comp-banner strong{color:var(--text)}
  .compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:0 0 24px}
  .compare-card{background:var(--card);border-radius:12px;padding:24px;border:1px solid var(--border);text-align:center}
  .compare-card.alt{border-color:var(--accent)}
  .compare-card .label{color:var(--text2);font-size:.8rem;text-transform:uppercase;letter-spacing:.5px}
  .compare-card .num{font-size:2.2rem;font-weight:700;margin:8px 0}
  .compare-card .num.green{color:var(--green)}.compare-card .num.blue{color:var(--accent2)}
  .compare-card .desc{font-size:.82rem;color:var(--text3)}
  .stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin:20px 0}
  .stat-box{background:var(--card);border-radius:10px;padding:14px 12px;border:1px solid var(--border);text-align:center}
  .stat-box .stat-label{color:var(--text2);font-size:.75rem;text-transform:uppercase;letter-spacing:.5px;display:flex;align-items:center;justify-content:center;gap:2px}
  .stat-box .stat-value{font-size:1.5rem;font-weight:700;margin-top:4px}
  .stat-box .stat-value.green{color:var(--green)}.stat-box .stat-value.blue{color:var(--accent2)}.stat-box .stat-value.orange{color:var(--orange)}
  .chart-container{background:var(--card);border-radius:12px;padding:20px;border:1px solid var(--border);margin:16px 0}
  .chart-title{font-size:.95rem;font-weight:600;margin-bottom:12px;color:var(--text)}
  .bar-row{display:flex;align-items:center;gap:8px;margin:6px 0;font-size:.85rem}
  .bar-label{width:100px;text-align:right;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0}
  .bar-track{flex:1;height:22px;background:var(--bg);border-radius:4px;overflow:hidden;display:flex}
  .bar-fill-ot{height:100%;background:#c7d2fe;border-radius:4px 0 0 4px}
  .bar-fill-comp{height:100%;background:var(--accent);border-radius:0 4px 4px 0}
  .bar-value{width:70px;text-align:right;font-weight:600;color:var(--green);flex-shrink:0}
  .bar-meta{width:200px;font-size:.72rem;color:var(--text3);flex-shrink:0}
  .elig-flag{font-size:.7rem;padding:1px 5px;border-radius:3px;margin-left:4px}
  .elig-flag.missed{background:rgba(239,68,68,.15);color:var(--red)}
  .elig-flag.short{background:rgba(100,116,139,.2);color:var(--text3)}
  .missed-table{width:100%;border-collapse:collapse;margin:12px 0;font-size:.85rem}
  .missed-table th{color:var(--text2);font-size:.75rem;text-transform:uppercase;letter-spacing:.5px;padding:8px 12px;border-bottom:1px solid var(--border);text-align:left}
  .missed-table td{padding:8px 12px;border-bottom:1px solid var(--border)}
  .missed-table td:nth-child(4),.missed-table td:nth-child(5){text-align:right}
  .missed-info{background:rgba(245,158,11,.08);border:1px solid var(--border);border-left:4px solid var(--orange);border-radius:8px;padding:12px 16px;margin:12px 0;font-size:.82rem;color:var(--text2)}
  .missed-info strong{color:var(--orange)}
  .legend{display:flex;gap:20px;margin:8px 0 16px;font-size:.8rem;color:var(--text2);flex-wrap:wrap}
  .legend-item{display:flex;align-items:center;gap:6px}
  .legend-dot{width:12px;height:12px;border-radius:3px;flex-shrink:0}
  table{width:100%;border-collapse:collapse;margin:12px 0}
  th,td{padding:10px 16px;text-align:left;border-bottom:1px solid var(--border)}
  th{color:var(--text2);font-size:.8rem;text-transform:uppercase;letter-spacing:.5px}
  td{font-size:.95rem}
  td:last-child{text-align:right;font-weight:600;color:var(--green)}
  .insights{background:var(--card);border-radius:12px;padding:20px;border:1px solid var(--border);border-left:4px solid var(--accent);margin:16px 0}
  .insights ul{padding-left:20px}
  .insights li{margin:10px 0;font-size:.9rem;line-height:1.6}
  .insights strong{color:var(--accent2)}
  .reddit-card{background:linear-gradient(135deg,#1e293b,#0c4a6e);border-radius:12px;padding:24px;margin:24px 0;border:2px solid var(--blue)}
  .reddit-header{font-size:.8rem;text-transform:uppercase;letter-spacing:1px;color:var(--blue);font-weight:700;margin-bottom:12px}
  .reddit-body{font-size:.95rem;line-height:1.7}
  .reddit-body p{margin:8px 0}
  .reddit-body strong{color:var(--accent2)}
  .reddit-body ul{padding-left:20px;margin:8px 0}
  .donut-container{display:flex;align-items:center;justify-content:center;gap:32px;margin:20px 0;flex-wrap:wrap}
  .donut{width:160px;height:160px;border-radius:50%;display:flex;align-items:center;justify-content:center;position:relative;flex-shrink:0}
  .donut-hole{width:110px;height:110px;border-radius:50%;background:var(--card);display:flex;flex-direction:column;align-items:center;justify-content:center}
  .donut-hole .pct{font-size:2rem;font-weight:800;color:var(--green)}
  .donut-hole .lbl{font-size:.75rem;color:var(--text2)}
  .donut-legend{font-size:.9rem;line-height:2}
  .donut-legend strong{color:var(--accent2)}
  .footer{margin-top:32px;padding-top:16px;border-top:1px solid var(--border);color:var(--text3);font-size:.8rem;text-align:center}
  .tip-wrap{position:relative;display:inline-flex;align-items:center;cursor:help}
  .tip-i{display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;background:var(--card2);color:var(--text2);font-size:.6rem;font-weight:700;margin-left:3px;flex-shrink:0}
  .tip-body{visibility:hidden;opacity:0;position:absolute;bottom:130%;left:50%;transform:translateX(-50%);background:#0c0a1e;color:#e2e8f0;padding:10px 14px;border-radius:8px;font-size:.76rem;white-space:normal;width:250px;z-index:300;line-height:1.5;transition:opacity .15s;box-shadow:0 4px 12px rgba(0,0,0,.5);border:1px solid var(--border);text-align:left;pointer-events:none}
  .tip-body::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#0c0a1e}
  .tip-wrap:hover .tip-body{visibility:visible;opacity:1}
  @media(max-width:700px){.bar-meta{width:120px;font-size:.68rem}.bar-label{width:70px}.compare-grid{grid-template-columns:1fr}}
"""
    # --- HTML body ---
    body = """
<h1>DCP Token Savings Report</h1>
<p class="subtitle">Dynamic Context Pruning &mdash; compound savings analysis across __SC__ sessions</p>

<div class="hero">
  <div class="hero-num">__TS__</div>
  <div class="hero-label">tokens saved via compound DCP effect</div>
  <div class="hero-sub">Without DCP you would have used <strong>__WOD__</strong> tokens instead of <strong>__TU__</strong>.</div>
  <div class="hero-badges">
    <div class="badge"><strong>__PCT__</strong> saved &middot; $__USD3__ at $3/M</div>
    <div class="badge"><strong>__MULT__x</strong> compound multiplier <span class="tip-wrap"><span class="tip-i">i</span><span class="tip-body">The multiplier shows how much compound savings exceeds one-time compression. A 31.9x multiplier means each compressed token saves ~32 tokens total across all subsequent requests in that session.</span></span></div>
    <div class="badge"><strong>__SW__/__SC2__</strong> sessions had DCP</div>
  </div>
</div>

<div class="explain-box">
  <h3>Understanding This Report</h3>
  <p><strong>One-Time Savings</strong> measures tokens removed during each compression event &mdash; counted once.
  If DCP compresses 40K tokens into a 1.5K summary, that's 38.5K tokens saved in that single event.</p>
  <p><strong>Compound Savings</strong> recognizes those 38.5K tokens are <em>never re-sent</em> on subsequent
  requests. In a session that continues for 149 more turns, the real savings is 38.5K &times; 149 = <strong>5.7M tokens</strong>.</p>
  <div class="example"><strong>Example:</strong> Session A has 164 requests. DCP compresses 173K tokens into summaries
  across 6 blocks, starting around turn 15. Those 173K tokens are never re-sent on the remaining ~149 requests.
  One-time savings: <strong>173K</strong>. Compound savings: <strong>14.9M</strong> (86x multiplier).</div>
  <p>The <strong>Multiplier</strong> (__MULT_E__x) means that on average, each compressed token saves ~__MULT_R__
  tokens across all future requests in that session.</p>
</div>

<h2>One-Time vs Compound Savings</h2>
<div class="ot-comp-banner">
  <span class="legend-dot" style="background:#c7d2fe"></span>
  <strong>One-Time</strong> = tokens removed during compression (counted once per event)
  &nbsp;&middot;&nbsp;
  <span class="legend-dot" style="background:#4f46e5"></span>
  <strong>Compound</strong> = same tokens &times; every subsequent request that benefits
</div>
<div class="compare-grid">
  <div class="compare-card">
    <div class="label">One-Time Compression <span class="tip-wrap"><span class="tip-i">i</span><span class="tip-body">Sum of (compressedTokens - summaryTokens) across ALL compression events in ALL sessions. This is the traditional metric that only counts tokens removed once.</span></span></div>
    <div class="num blue">__OT__</div>
    <div class="desc">Tokens removed during compression events &mdash; counted once.</div>
  </div>
  <div class="compare-card alt">
    <div class="label">Compound Savings (Real) <span class="tip-wrap"><span class="tip-i">i</span><span class="tip-body">One-time savings multiplied by the number of subsequent requests that benefit from each compression. This reflects the actual reduction in API token consumption.</span></span></div>
    <div class="num green">__TS2__</div>
    <div class="desc">Tokens saved across ALL subsequent requests in each session.</div>
  </div>
</div>

<h2>Key Metrics</h2>
<div class="stat-grid">
  <div class="stat-box"><div class="stat-label">__TL_TU__</div><div class="stat-value blue">__TU2__</div></div>
  <div class="stat-box"><div class="stat-label">__TL_TS__</div><div class="stat-value green">__TS3__</div></div>
  <div class="stat-box"><div class="stat-label">__TL_PCT__</div><div class="stat-value green">__PCT2__</div></div>
  <div class="stat-box"><div class="stat-label">__TL_USD__</div><div class="stat-value green">$__USD32__</div></div>
  <div class="stat-box"><div class="stat-label">__TL_REQ__</div><div class="stat-value orange">__REQ__</div></div>
  <div class="stat-box"><div class="stat-label">__TL_BLK__</div><div class="stat-value orange">__BLK__</div></div>
  <div class="stat-box"><div class="stat-label">__TL_MULT__</div><div class="stat-value blue">__MULT2__x</div></div>
  <div class="stat-box"><div class="stat-label">__TL_DCP__</div><div class="stat-value blue">__SW2__/__SC3__</div></div>
</div>

<h2>Savings Rate</h2>
<div class="donut-container">
  <div class="donut" style="background:conic-gradient(var(--green) 0deg __DD__deg, var(--card2) __DD__deg 360deg)">
    <div class="donut-hole"><div class="pct">__PCT3__</div><div class="lbl">SAVED</div></div>
  </div>
  <div class="donut-legend">
    <p><strong style="color:var(--green)">&bull;</strong> __TS4__ tokens saved by DCP (__PCT4__)</p>
    <p><strong style="color:var(--card2)">&bull;</strong> __TU3__ tokens actually used (__PCT5__)</p>
    <p style="margin-top:8px;color:var(--text2)">Without DCP, total would be <strong>__WOD2__</strong></p>
  </div>
</div>

<h2>Top Sessions by Compound Savings</h2>
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#c7d2fe"></div>One-time savings</div>
  <div class="legend-item"><div class="legend-dot" style="background:#4f46e5"></div>Compound savings</div>
  <div class="legend-item" style="color:var(--text3)">Multiplier = compound &divide; one-time for that session</div>
</div>
<div class="chart-container">
  <div class="chart-title">Sessions ranked by compound token savings</div>
  __SR__
</div>

<h2>Per-Model Breakdown</h2>
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#c7d2fe"></div>One-time</div>
  <div class="legend-item"><div class="legend-dot" style="background:#4f46e5"></div>Compound</div>
  <div class="legend-item"><span class="elig-flag missed"> \u26a0 missed</span> = \u226510 requests + \u226510K peak, no DCP</div>
  <div class="legend-item"><span class="elig-flag short"> no DCP needed</span> = all sessions short</div>
</div>
<div class="chart-container">
  <div class="chart-title">Models ranked by compound savings &middot; bar meta shows DCP calls, session coverage, and peak context size</div>
  __MR__
</div>

<h2>USD Savings Sensitivity</h2>
<table>
  <thead><tr><th>Rate</th><th>Estimated USD Saved (Compound)</th></tr></thead>
  <tbody>__UR__</tbody>
</table>
<p class="note">Blended input-token pricing from __PS__.</p>

__MISSED__
<h2>Insights</h2>
<div class="insights"><ul>__INS__</ul></div>

__RDT__

<div class="footer">Generated __GEN__ &middot; DCP v3 compound model &middot; Python 3 stdlib only &middot; Read-only analysis</div>
"""
    # --- Build tooltip-wrapped labels for stat boxes ---
    tl_tu = tip("Tokens Used", "Total tokens (input + output + reasoning) consumed across all %d sessions. This is what was actually sent/received after DCP compression." % sc)
    tl_ts = tip("Tokens Saved", "Compound savings: one-time compressed tokens multiplied by subsequent requests that benefit. This is the real reduction in API consumption.")
    tl_pct = tip("Savings Rate", "Compound tokens saved divided by tokens used. Without DCP, you would have used %s tokens total." % fmt_tokens(without_dcp))
    tl_usd = tip("USD Saved ($3/M)", "Estimated cost savings at a blended rate of $3.00 per million input tokens. See sensitivity table below for other rates.")
    tl_req = tip("Total Requests", "Number of model inference calls (step-finish events) across all sessions. Each request benefits from prior DCP compressions.")
    tl_blk = tip("DCP Blocks", "Total compression events across all sessions. Each block compresses a range of conversation messages into a summary.")
    tl_mult = tip("Multiplier", "Compound savings divided by one-time savings. A %.1fx multiplier means each compressed token saves ~%d tokens on average across all subsequent requests." % (mult, int(mult)))
    tl_dcp = tip("Sessions w/ DCP", "%d of %d sessions have DCP state files. Of the remaining %d: %d were too short for DCP, %d had enough activity (\u2265%d requests + \u2265%s peak context) that DCP should have triggered but didn\u2019t. DCP activates via a hard limit at %s tokens or a soft nudge every 5 turns after turn 15." % (sw_dcp, sc, sc - sw_dcp, sw_short, sw_missed, DCP_ELIGIBLE_MIN_REQUESTS, fmt_tokens(DCP_ELIGIBLE_MIN_PEAK_INPUT), fmt_tokens(DCP_HARD_LIMIT)))

    # --- Replacements ---
    replacements = {
        "__SC__": str(sc),
        "__TS__": fmt_tokens(ts_comp),
        "__WOD__": fmt_tokens(without_dcp),
        "__TU__": fmt_tokens(tu),
        "__PCT__": fmt_pct(pct_comp),
        "__USD3__": "%.2f" % usd3,
        "__MULT__": "%.1f" % mult,
        "__SW__": str(sw_dcp),
        "__SC2__": str(sc),
        "__MULT_E__": "%.1f" % mult,
        "__MULT_R__": str(int(mult)),
        "__OT__": fmt_tokens(ts_ot),
        "__TS2__": fmt_tokens(ts_comp),
        "__TL_TU__": tl_tu,
        "__TL_TS__": tl_ts,
        "__TL_PCT__": tl_pct,
        "__TL_USD__": tl_usd,
        "__TL_REQ__": tl_req,
        "__TL_BLK__": tl_blk,
        "__TL_MULT__": tl_mult,
        "__TL_DCP__": tl_dcp,
        "__TU2__": fmt_tokens(tu),
        "__TS3__": fmt_tokens(ts_comp),
        "__PCT2__": fmt_pct(pct_comp),
        "__USD32__": "%.2f" % usd3,
        "__REQ__": str(t["total_requests"]),
        "__BLK__": str(t["total_blocks"]),
        "__MULT2__": "%.1f" % mult,
        "__SW2__": str(sw_dcp),
        "__SC3__": str(sc),
        "__DD__": str(donut_deg),
        "__PCT3__": fmt_pct(pct_comp),
        "__TS4__": fmt_tokens(ts_comp),
        "__PCT4__": fmt_pct(pct_comp),
        "__TU3__": fmt_tokens(tu),
        "__PCT5__": fmt_pct(100 - pct_comp) if pct_comp < 100 else "0%",
        "__WOD2__": fmt_tokens(without_dcp),
        "__SR__": session_rows,
        "__MR__": model_rows,
        "__UR__": usd_rows,
        "__PS__": ", ".join(PRICE_SOURCES),
        "__INS__": insights,
        "__MISSED__": missed_table_html,
        "__RDT__": reddit,
        "__GEN__": agg["generated_at"][:19].replace("T", " "),
    }

    for key, val in replacements.items():
        body = body.replace(key, val)

    return "<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='utf-8'>\n<meta name='viewport' content='width=device-width, initial-scale=1'>\n<title>DCP Token Savings Report</title>\n<style>" + css + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>"


# === VERIFY ===

def verify(agg, expected_n=LAST_N):
    results = []
    t = agg["totals"]
    sc = agg["session_count"]
    ts_comp = t["compound_saved"]; ts_ot = t["one_time_saved"]; tu = t["tokens_used"]
    crosscheck = t["stats_totalPruneTokens"]
    ok = sc == expected_n
    results.append(("session_count", ok, "session_count=%d (expected %d)" % (sc, expected_n)))
    ok = tu > 0
    results.append(("tokens_used_gt_0", ok, "tokens_used=%d" % tu))
    ok = ts_comp > 0
    results.append(("compound_saved_gt_0", ok, "compound_saved=%d" % ts_comp))
    ok = ts_comp >= ts_ot
    results.append(("compound_ge_one_time", ok, "compound=%d >= one_time=%d" % (ts_comp, ts_ot)))
    sum_pm = sum(m.get("compound_saved", 0) for m in agg.get("per_model", []))
    ok = sum_pm == ts_comp
    results.append(("sum_per_model_equals_total", ok, "sum(per_model.compound)=%d, total=%d" % (sum_pm, ts_comp)))
    ok = ts_ot <= crosscheck if crosscheck > 0 else True
    results.append(("one_time_le_crosscheck", ok, "one_time=%d <= crosscheck=%d" % (ts_ot, crosscheck)))
    mult = t["multiplier"]
    ok = mult >= 1.0
    results.append(("multiplier_ge_1", ok, "multiplier=%.1f" % mult))
    return results


# === MAIN ===

def main():
    ap = argparse.ArgumentParser(description="DCP Token-Savings Report v3")
    ap.add_argument("--aggregate-only", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--sessions", type=int, default=LAST_N, help="number of most-recent sessions to analyze (default %(default)s)")
    args = ap.parse_args()
    conn = sqlite3.connect(DB_PATH)
    selected = select_last_n_sessions(n=args.sessions, conn=conn)
    print("Selected %d sessions" % len(selected))
    agg = aggregate(selected, conn)
    conn.close()
    os.makedirs(os.path.dirname(OUT_AGG), exist_ok=True)
    json.dump(agg, open(OUT_AGG, "w", encoding="utf-8"), indent=2)
    print("Wrote %s (%d bytes)" % (OUT_AGG, os.path.getsize(OUT_AGG)))
    if args.verify:
        print("\n=== DCP Savings v3 --verify ===")
        results = verify(agg, args.sessions)
        all_pass = True
        for name, ok, detail in results:
            status = "PASS" if ok else "FAIL"
            if not ok: all_pass = False
            print("  [%s] %s -- %s" % (status, name, detail))
        print("=== session_count=%d tokens_used=%d compound_saved=%d one_time=%d multiplier=%.1f ===" % (agg["session_count"], agg["totals"]["tokens_used"], agg["totals"]["compound_saved"], agg["totals"]["one_time_saved"], agg["totals"]["multiplier"]))
        sys.exit(0 if all_pass else 1)
    if args.aggregate_only:
        return
    os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
    html_str = build_html(agg)
    open(OUT_HTML, "w", encoding="utf-8").write(html_str)
    print("Wrote %s (%d bytes)" % (OUT_HTML, os.path.getsize(OUT_HTML)))


if __name__ == "__main__":
    main()

