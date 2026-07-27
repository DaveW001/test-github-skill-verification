#!/usr/bin/env python3
"""Portfolio ranking tool for the top-skills-agents-review track.

Adapted from session-db-query/scripts/query_sessions.py. Reads the OpenCode
session database in READ-ONLY mode only. NEVER selects, prints, or stores raw
message bodies, secrets, or private prompt content.

Modes:
  --inspect-schema   Emit a database contract summary (tables, columns, counts,
                     ms->UTC conversion note). No message-body columns selected.

A future --rank mode (Task 1.2) will read candidate totals and emit
usage-ranking.json according to the frozen ranking-contract.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

DEFAULT_DB = r"C:\Users\DaveWitkin\.local\share\opencode\opencode.db"
VAULT_ROOT = r"C:\Users\DaveWitkin\.opencode-lazy-vault"
ALWAYS_ON_SKILL_ROOT = r"C:\Users\DaveWitkin\.config\opencode\skill"
AGENT_ROOT = r"C:\Users\DaveWitkin\.config\opencode\agent"

# Operational-importance classification. Reasons are recorded per candidate.
IMPORTANCE_1_0 = {
    # safety/orchestration/validation infrastructure (skills)
    "conductor", "conductor-pipeline", "osgrep", "skill-creator",
    "skill-test-harness", "skill-discovery", "session-db-query",
    "opencode-event-log-compactor", "opencode-go-key-rotation",
    "opencode-scheduler", "scheduled-job-best-practices", "git-push",
    "root-cause-analysis", "retrospective", "thinking-partner",
    # orchestration/validation infrastructure (agents)
    "01-planner", "build", "peer-review", "conductor-pipeline-orchestrator",
    "conductor-plan-creator", "conductor-plan-reviewer",
    "conductor-plan-reviewer-alt", "conductor-doc-writer",
    "conductor-track-executor", "conductor-track-executor-glm51",
    "conductor-track-executor-mimo2.5pro", "conductor-test-writer",
    "conductor-test-runner", "conductor-track-validator",
    "conductor-track-validator-alt", "conductor-track-validator-m3",
}
IMPORTANCE_0_5 = {
    # active cross-client business-workflow infrastructure
    "knowledge-graph-builder", "knowledge-graph-maintainer",
    "knowledge-graph-query", "clickup", "clickup-cli", "email-to-clickup",
    "calendar-schedule", "calendar-today", "google-calendar-schedule",
    "google-calendar-today", "unified-calendar-today",
    "slack-messaging", "slack-send-message", "microsoft-graph",
    "gmail-workspace", "gmail-inbox-triage", "gmail-draft-reply",
    "outlook-inbox-triage", "outlook-email-search",
    "email-routing-config", "email-auto-sorter", "email-attachment-detacher",
    "google-contacts", "google-drive",
}


def _importance(name):
    if name in IMPORTANCE_1_0:
        return 1.0, "safety/orchestration/validation infrastructure"
    if name in IMPORTANCE_0_5:
        return 0.5, "active cross-client business-workflow infrastructure"
    return 0.0, "single-purpose/content skill (no infrastructure role)"

# Columns that are STRICTLY message-body / private content. We never SELECT
# these; the schema inspector only records their NAMES via PRAGMA, never values.
BODY_COLUMN_HINTS = {
    "body", "content", "message", "messages", "text", "prompt", "payload",
    "data", "value", "raw", "blob",
}


def _connect_ro(db_path, timeout_seconds):
    uri = "file:{}?mode=ro".format(str(db_path).replace("\\", "/"))
    conn = sqlite3.connect(uri, uri=True, timeout=max(1.0, float(timeout_seconds or 30)))
    return conn


def _list_tables(cur):
    cur.execute(
        "SELECT name, type FROM sqlite_master "
        "WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    )
    return cur.fetchall()


def _table_info(cur, table):
    cur.execute("PRAGMA table_info({})".format('"' + table.replace('"', '""') + '"'))
    cols = []
    for row in cur.fetchall():
        # row: (cid, name, type, notnull, dflt_value, pk)
        cols.append(
            {
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "pk": bool(row[5]),
            }
        )
    return cols


def _safe_row_count(cur, table):
    """Count rows without selecting any columns."""
    try:
        cur.execute(
            "SELECT COUNT(*) FROM {}".format('"' + table.replace('"', '""') + '"')
        )
        return cur.fetchone()[0]
    except sqlite3.Error:
        return None


def inspect_schema(db_path, output_path, timeout_seconds):
    summary = {
        "db_path": os.path.abspath(str(db_path)),
        "read_only": True,
        "connection_uri": "file:<db>?mode=ro",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "timestamp_conversion": (
            "time_created / time_updated / time_archived are Unix MILLISECONDS. "
            "Always divide by 1000 inside SQLite date functions: "
            "DATETIME(time_created / 1000, 'unixepoch')."
        ),
        "archive_policy": (
            "Do NOT filter on time_archived IS NULL. Archived sessions are "
            "completed work and the primary data source; ~90%+ are archived."
        ),
        "body_policy": (
            "Message-body / private-content columns are recorded by NAME only via "
            "PRAGMA table_info. Their values are NEVER selected, printed, or stored. "
            "Hint columns: " + ", ".join(sorted(BODY_COLUMN_HINTS))
        ),
        "tables": [],
        "skill_call_tables_detected": [],
        "agent_column_detected": False,
        "session_total": None,
    }

    conn = _connect_ro(db_path, timeout_seconds)
    try:
        cur = conn.cursor()
        tables = _list_tables(cur)
        for (tname, ttype) in tables:
            cols = _table_info(cur, tname)
            col_names = [c["name"] for c in cols]
            count = _safe_row_count(cur, tname)
            # Flag likely message-body columns by name (names only, never values).
            body_like = [n for n in col_names if n.lower() in BODY_COLUMN_HINTS]
            summary["tables"].append(
                {
                    "name": tname,
                    "type": ttype,
                    "row_count": count,
                    "columns": cols,
                    "body_like_column_names": body_like,
                }
            )
            # Detect any structured skill-call evidence by table name.
            lt = tname.lower()
            if "skill" in lt:
                summary["skill_call_tables_detected"].append(tname)
            if "agent" in col_names:
                summary["agent_column_detected"] = True
        # Session total for the recovery/diagnostic comparison.
        try:
            cur.execute("SELECT COUNT(*) FROM session")
            summary["session_total"] = cur.fetchone()[0]
        except sqlite3.Error:
            summary["session_total"] = None
    finally:
        conn.close()

    # Write JSON (UTF-8, no BOM).
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    # Console summary (names + counts only).
    print("SCHEMA_INSPECT_DONE")
    print("table_count={}".format(len(summary["tables"])))
    print("session_total={}".format(summary["session_total"]))
    print("skill_call_tables_detected={}".format(summary["skill_call_tables_detected"]))
    print("agent_column_detected={}".format(summary["agent_column_detected"]))
    return 0


def _canonical_skills():
    """Return list of (name, resolved_path) for canonical skills, deduped.

    Always-on skill root wins as the resolved path when a name exists in both,
    because those are the actively-loaded global skills.
    """
    by_name = {}
    for root, kind in ((ALWAYS_ON_SKILL_ROOT, "always-on"), (VAULT_ROOT, "vault")):
        if not os.path.isdir(root):
            continue
        try:
            entries = os.listdir(root)
        except OSError:
            continue
        for entry in entries:
            p = os.path.join(root, entry)
            skill_md = os.path.join(p, "SKILL.md")
            if os.path.isdir(p) and os.path.isfile(skill_md):
                # Always-on takes precedence as the canonical resolved path.
                if entry not in by_name or kind == "always-on":
                    by_name[entry] = {
                        "name": entry,
                        "resolved_path": os.path.abspath(p),
                        "source_root": kind,
                        "also_at": [],
                    }
                else:
                    by_name[entry]["also_at"].append(os.path.abspath(p))
    return list(by_name.values())


def _canonical_agents():
    """Return list of dicts for canonical agent definitions (exclude .bak/.routing)."""
    out = []
    if not os.path.isdir(AGENT_ROOT):
        return out
    for fn in sorted(os.listdir(AGENT_ROOT)):
        if not fn.endswith(".md"):
            continue
        if ".bak" in fn or ".routing" in fn:
            continue
        aid = fn[:-3]
        out.append({
            "name": aid,
            "resolved_path": os.path.abspath(os.path.join(AGENT_ROOT, fn)),
        })
    return out


def _gather_agent_usage(db_path, agent_names, timeout_seconds):
    """Direct evidence: session.agent column (no message bodies)."""
    name_ci = {n.casefold(): n for n in agent_names}
    usage = {n: {"frequency": 0, "unique_sessions": 0, "projects": set(),
                 "last_time_created_ms": 0} for n in agent_names}
    conn = sqlite3.connect("file:{}?mode=ro".format(str(db_path).replace("\\", "/")),
                           uri=True, timeout=max(1.0, float(timeout_seconds or 30)))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(agent,''), COUNT(*), COUNT(DISTINCT project_id), "
            "MAX(time_created) FROM session GROUP BY COALESCE(agent,'')"
        )
        for a, n, b, maxc in cur.fetchall():
            key = name_ci.get((a or "").casefold())
            if key is None:
                continue
            usage[key]["frequency"] = int(n or 0)
            usage[key]["unique_sessions"] = int(n or 0)  # same as freq for agents
            usage[key]["projects"] = int(b or 0)
            usage[key]["last_time_created_ms"] = int(maxc or 0)
    finally:
        conn.close()
    return usage


def _gather_skill_usage(db_path, skill_names, timeout_seconds):
    """Inferred evidence: session.title mentions of skill folder names."""
    usage = {n: {"frequency": 0, "unique_sessions": 0, "projects": 0,
                 "last_time_created_ms": 0} for n in skill_names}
    pats = {n: re.compile(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", re.I)
            for n in skill_names}
    conn = sqlite3.connect("file:{}?mode=ro".format(str(db_path).replace("\\", "/")),
                           uri=True, timeout=max(1.0, float(timeout_seconds or 30)))
    try:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(title,''), project_id, time_created FROM session")
        # Track per-skill project sets for breadth.
        proj_sets = {n: set() for n in skill_names}
        last_ms = {n: 0 for n in skill_names}
        counts = {n: 0 for n in skill_names}
        for title, pid, tc in cur.fetchall():
            t = title or ""
            tlow = t
            for n in skill_names:
                if pats[n].search(tlow):
                    counts[n] += 1
                    if pid:
                        proj_sets[n].add(pid)
                    if (tc or 0) > last_ms[n]:
                        last_ms[n] = int(tc or 0)
        for n in skill_names:
            usage[n]["frequency"] = counts[n]
            usage[n]["unique_sessions"] = counts[n]
            usage[n]["projects"] = len(proj_sets[n])
            usage[n]["last_time_created_ms"] = last_ms[n]
    finally:
        conn.close()
    return usage


def _recency(last_ms, ref_iso):
    if not last_ms:
        return 0.0
    ref = datetime.fromisoformat(ref_iso.replace("Z", "+00:00"))
    last = datetime.fromtimestamp(last_ms / 1000.0, tz=timezone.utc)
    days = max(0.0, (ref - last).total_seconds() / 86400.0)
    return math.exp(-days / 90.0)


def _score_and_sort(candidates, contract):
    w = contract["weights"]
    ref_iso = contract["reference_timestamp_utc"]
    # Normalize within artifact type.
    max_freq = max((c["frequency"] for c in candidates), default=0) or 1
    max_breadth = max((c["unique_sessions"] for c in candidates), default=0) or 1
    # breadth uses unique_sessions count as the breadth proxy (sessions/projects)
    for c in candidates:
        fn = c["frequency"] / max_freq if max_freq else 0.0
        bn = c["unique_sessions"] / max_breadth if max_breadth else 0.0
        rec = _recency(c["last_time_created_ms"], ref_iso)
        imp = c["operational_importance"]
        c["score_components"] = {
            "frequency_norm": round(fn, 6),
            "breadth_norm": round(bn, 6),
            "recency": round(rec, 6),
            "operational_importance": imp,
        }
        score = (w["observed_frequency"] * fn
                 + w["unique_session_breadth"] * bn
                 + w["recency"] * rec
                 + w["operational_importance"] * imp)
        c["score"] = round(score, 6)
    candidates.sort(key=lambda c: (-c["score"], -c["unique_sessions"],
                                   -c["score_components"]["recency"],
                                   c["name"].casefold()))
    return candidates


def _confidence(freq, has_signal):
    if not has_signal:
        return "low"
    if freq > 0:
        return "high"
    return "low"


def rank_portfolio(db_path, output_path, contract_path, timeout_seconds):
    with open(contract_path, "r", encoding="utf-8-sig") as fh:
        contract = json.load(fh)
    contract_sha = hashlib.sha256(
        json.dumps(contract, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    # --- Agents (direct evidence) ---
    agents = _canonical_agents()
    agent_names = [a["name"] for a in agents]
    agent_usage = _gather_agent_usage(db_path, agent_names, timeout_seconds)
    agent_cands = []
    for a in agents:
        u = agent_usage[a["name"]]
        imp, imp_reason = _importance(a["name"])
        agent_cands.append({
            "artifact_type": "agent",
            "name": a["name"],
            "canonical_name": a["name"],
            "resolved_path": a["resolved_path"],
            "source_signal": "session.agent (direct; read-only)",
            "frequency": u["frequency"],
            "unique_sessions": u["unique_sessions"],
            "projects": u["projects"],
            "last_time_created_ms": u["last_time_created_ms"],
            "operational_importance": imp,
            "operational_importance_reason": imp_reason,
            "confidence": "high" if u["frequency"] > 0 else "low",
            "exclusion_or_tiebreak": "",
        })
    agent_cands = _score_and_sort(agent_cands, contract)
    for idx, c in enumerate(agent_cands):
        c["rank"] = idx + 1
    selected_agents = agent_cands[:10]
    for c in selected_agents:
        c["selected"] = True
    for c in agent_cands[10:]:
        c["selected"] = False
        c["exclusion_or_tiebreak"] = "below top-10 cutoff"

    # --- Skills (inferred evidence) ---
    skills = _canonical_skills()
    skill_names = [s["name"] for s in skills]
    skill_usage = _gather_skill_usage(db_path, skill_names, timeout_seconds)
    skill_cands = []
    for s in skills:
        u = skill_usage[s["name"]]
        imp, imp_reason = _importance(s["name"])
        skill_cands.append({
            "artifact_type": "skill",
            "name": s["name"],
            "canonical_name": s["name"],
            "resolved_path": s["resolved_path"],
            "source_root": s["source_root"],
            "also_at": s.get("also_at", []),
            "source_signal": "session.title mention (inferred; no structured skill-call table)",
            "frequency": u["frequency"],
            "unique_sessions": u["unique_sessions"],
            "projects": u["projects"],
            "last_time_created_ms": u["last_time_created_ms"],
            "operational_importance": imp,
            "operational_importance_reason": imp_reason,
            "confidence": "low",  # inferred signal only
            "exclusion_or_tiebreak": "",
        })
    skill_cands = _score_and_sort(skill_cands, contract)
    for idx, c in enumerate(skill_cands):
        c["rank"] = idx + 1
    selected_skills = skill_cands[:20]
    for c in selected_skills:
        c["selected"] = True
    for c in skill_cands[20:]:
        c["selected"] = False
        c["exclusion_or_tiebreak"] = "below top-20 cutoff"

    out = {
        "trackId": "20260726-top-skills-agents-review",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ranking_contract_sha256": contract_sha,
        "ranking_contract_path": os.path.abspath(contract_path),
        "selection_targets": {"skills": 20, "agents": 10},
        "selected_skills_count": len(selected_skills),
        "selected_agents_count": len(selected_agents),
        "evidence_confidence_summary": {
            "agents": "high (direct session.agent evidence)",
            "skills": "low (inferred session.title mentions; no structured skill-call table in opencode.db)",
        },
        "selected_skills": selected_skills,
        "selected_agents": selected_agents,
        "near_cutoff_skills": [c for c in skill_cands[20:25]],
        "near_cutoff_agents": [c for c in agent_cands[10:13]],
        "all_candidates_count": {"skills": len(skill_cands), "agents": len(agent_cands)},
    }

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("RANK_DONE")
    print("selected_skills={}".format(len(selected_skills)))
    print("selected_agents={}".format(len(selected_agents)))
    print("top_agent={} (score={})".format(selected_agents[0]["name"], selected_agents[0]["score"]))
    print("top_skill={} (score={})".format(selected_skills[0]["name"], selected_skills[0]["score"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Portfolio ranking / schema inspector.")
    ap.add_argument("--inspect-schema", action="store_true")
    ap.add_argument("--rank", action="store_true")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--output", default="")
    ap.add_argument("--ranking-contract", default="")
    ap.add_argument("--read-only", action="store_true", default=True)
    ap.add_argument("--timeout-seconds", type=float, default=60.0)
    args = ap.parse_args(argv)

    if not os.path.isfile(args.db):
        print("ERROR: db not found: {}".format(args.db), file=sys.stderr)
        return 1
    if args.inspect_schema:
        if not args.output:
            print("ERROR: --output required for --inspect-schema", file=sys.stderr)
            return 2
        return inspect_schema(args.db, args.output, args.timeout_seconds)
    if args.rank:
        if not args.output:
            print("ERROR: --output required for --rank", file=sys.stderr)
            return 2
        contract_path = args.ranking_contract or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "ranking-contract.json",
        )
        return rank_portfolio(args.db, args.output, contract_path, args.timeout_seconds)
    print("ERROR: no mode selected (use --inspect-schema or --rank)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
