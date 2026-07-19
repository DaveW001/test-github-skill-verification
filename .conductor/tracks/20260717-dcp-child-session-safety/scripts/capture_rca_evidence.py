#!/usr/bin/env python3
"""Capture redacted read-only RCA evidence for track 20260717-dcp-child-session-safety.

Reads the OpenCode SQLite DB in read-only mode and emits ONLY aggregate counts and
metadata hashes. It NEVER selects prompt/part/message-body/tool-payload (content)
columns. If a required aggregate cannot be computed without content columns, the
script writes a blocker artifact and exits non-zero instead of fabricating data.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
import datetime

CONTENT_TABLES = {"message", "part"}      # never SELECT * / data from these
CONTENT_COLUMNS = {"data"}                # never select this column


def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"error:{e}"


def list_tables(cur):
    return [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-uri", required=True)
    ap.add_argument("--dcp-state", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    blocker_path = os.path.join(os.path.dirname(os.path.abspath(args.output)),
                                "rca-evidence-blockers-" + datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + ".md")

    con = sqlite3.connect(args.db_uri, uri=True)
    cur = con.cursor()
    tables = list_tables(cur)

    evidence = {
        "track": "20260717-dcp-child-session-safety",
        "db_uri": args.db_uri.replace("mode=ro", "mode=ro"),
        "db_open_mode": "read-only",
        "captured_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "tables": tables,
        "secret_or_content_fields_emitted": 0,
    }

    # --- safe aggregates (metadata/counts only) ---
    evidence["sessions_total"] = cur.execute("SELECT COUNT(*) FROM session").fetchone()[0]
    evidence["child_sessions_parent_id_not_null"] = cur.execute(
        "SELECT COUNT(*) FROM session WHERE parent_id IS NOT NULL").fetchone()[0]
    evidence["task_child_sessions_title_pattern"] = cur.execute(
        "SELECT COUNT(*) FROM session WHERE title LIKE '%(@%subagent)' AND parent_id IS NOT NULL").fetchone()[0]
    evidence["permission_rows"] = cur.execute("SELECT COUNT(*) FROM permission").fetchone()[0]
    # cumulative lifetime token buckets among children (NOT live context size)
    tot = "(tokens_input + tokens_output + tokens_reasoning + tokens_cache_read + tokens_cache_write)"
    buckets = cur.execute(
        f"SELECT CASE WHEN {tot} > 150000 THEN 'cumulative_over_150k' WHEN {tot} > 0 THEN 'cumulative_1_to_150k' ELSE 'zero' END b, COUNT(*) c "
        f"FROM session WHERE parent_id IS NOT NULL GROUP BY b").fetchall()
    evidence["child_cumulative_token_buckets"] = {r[0]: r[1] for r in buckets}

    # SHA-256 of source config/agent files (names + hashes only, not bodies)
    hashes = {}
    for p in ["C:/Users/DaveWitkin/.config/opencode/dcp.jsonc"]:
        if os.path.exists(p):
            hashes[p] = sha256_file(p)
    evidence["source_file_hashes"] = hashes

    con.close()

    # --- DCP state dir counts (filesystem, no content) ---
    state_files = []
    if os.path.isdir(args.dcp_state):
        state_files = [f for f in os.listdir(args.dcp_state)]
    evidence["dcp_state_dir_exists"] = os.path.isdir(args.dcp_state)
    evidence["dcp_state_file_count"] = len(state_files)
    evidence["dcp_state_json_count"] = len([f for f in state_files if f.endswith(".json")])

    # --- required aggregates that CANNOT be computed content-free ---
    # The plan acceptance requires audited_child_sessions==200, children_over_150k==22,
    # child_compress_calls==0. Investigation shows:
    #  - session.tokens_* are CUMULATIVE lifetime totals, not live context-window size.
    #    cumulative >150000 yields 571 children (not 22).
    #  - live context-window size and compress tool-call counts live ONLY in the
    #    content-bearing message/part `data` columns, which the no-content rule forbids.
    required_unresolvable = {
        "audited_child_sessions": "Stage-1 RCA methodology (sampled audit of 200); not a DB-derived count. parent_id IS NOT NULL = 843, task-child title pattern = 843; neither yields 200.",
        "children_over_150k": "Requires live context-window size; session.tokens_* are cumulative lifetime totals (cumulative>150000 = 571 children, not 22). Live size needs message/part `data` content.",
        "child_compress_calls": "Compress tool calls are stored only in part/message `data` (content) columns; no metadata count exists.",
    }
    evidence["required_aggregates_unresolvable_without_content"] = required_unresolvable
    evidence["status"] = "BLOCKED - required aggregates need content columns (forbidden by no-content rule)"

    # Write the honest evidence file (acceptance gate will fail on the absent/unequal keys - intentional).
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    # Write the blocker artifact per plan recovery clause.
    with open(blocker_path, "w", encoding="utf-8") as f:
        f.write("# RCA Evidence Blocker - Task 0.1\n\n")
        f.write(f"**Track:** 20260717-dcp-child-session-safety  \n**Read-only URI:** `{args.db_uri}`  \n")
        f.write(f"**Generated:** {evidence['captured_at_utc']}\n\n")
        f.write("## Required aggregates cannot be computed without selecting content columns\n\n")
        f.write("The plan acceptance requires `audited_child_sessions==200`, `children_over_150k==22`, ")
        f.write("`child_compress_calls==0`. The no-content rule (Global Execution Rule #4) forbids selecting ")
        f.write("prompt/part/message-body/tool-payload columns.\n\n")
        f.write("## Schema discovered (`SELECT name FROM sqlite_master WHERE type='table'`)\n\n")
        f.write("```\n" + ", ".join(tables) + "\n```\n\n")
        f.write("## Safe aggregates actually computed (read-only, no content)\n\n")
        f.write("- sessions_total: %d\n" % evidence["sessions_total"])
        f.write("- child_sessions_parent_id_not_null: %d\n" % evidence["child_sessions_parent_id_not_null"])
        f.write("- task_child_sessions_title_pattern: %d\n" % evidence["task_child_sessions_title_pattern"])
        f.write("- permission_rows: %d\n" % evidence["permission_rows"])
        f.write("- child cumulative token buckets: %s\n" % json.dumps(evidence["child_cumulative_token_buckets"]))
        f.write("- dcp_state_file_count: %d (json: %d)\n\n" % (evidence["dcp_state_file_count"], evidence["dcp_state_json_count"]))
        f.write("## Why each required aggregate is unresolvable content-free\n\n")
        for k, v in required_unresolvable.items():
            f.write(f"- **{k}**: {v}\n")
        f.write("\n## Conclusion\n\nTask 0.1 acceptance gate (`assert audited_child_sessions==200 and children_over_150k==22 and child_compress_calls==0`) ")
        f.write("cannot pass honestly without violating the no-content rule. Task 0.1 left unchecked. ")
        f.write("Honest evidence written to rca-evidence.json with status BLOCKED.\n")

    print(json.dumps({"status": "blocked", "blocker": blocker_path, "output": args.output}, indent=2))
    sys.exit(2)


if __name__ == "__main__":
    main()