#!/usr/bin/env python3
"""Completion-hygiene gate (Final Task F.3). Verifies bookkeeping consistency:
plan/metadata/ledgers/execution-log agree and each ledger has exactly one
canonical row. Open/blocked tasks are reported as OPEN (transparency), not FAIL."""
import argparse
import json
import re
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track-root", required=True)
    ap.add_argument("--tracks", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--require-zero-fail", action="store_true")
    args = ap.parse_args()
    import os
    tid = os.path.basename(os.path.normpath(args.track_root))
    fails = []
    opens = []

    md_path = os.path.join(args.track_root, "metadata.json")
    plan_path = os.path.join(args.track_root, "plan.md")
    if not os.path.exists(md_path):
        fails.append("metadata.json missing")
    if not os.path.exists(plan_path):
        fails.append("plan.md missing")
    # execution log (any date)
    el = [f for f in os.listdir(args.track_root) if f.startswith("execution-log-") and f.endswith(".md")]
    if not el:
        fails.append("execution-log-*.md missing")

    # one canonical row each
    for label, path in (("tracks.md", args.tracks), ("tracks-ledger.md", args.ledger)):
        text = open(path, encoding="utf-8").read()
        rows = len(re.findall(re.escape(tid), text))
        if rows != 1:
            fails.append(f"{label} has {rows} references to {tid} (want 1)")

    # metadata parseable + plan/metadata agreement
    if not fails:
        meta = json.load(open(md_path, encoding="utf-8"))
        plan = open(plan_path, encoding="utf-8").read()
        x = len(re.findall(r"- \[x\] \*\*", plan))
        tilde = len(re.findall(r"- \[~\] \*\*", plan))
        opencount = len(re.findall(r"- \[ \] \*\*", plan))
        if meta.get("progress", {}).get("completedTasks") != x:
            fails.append(f"metadata.completedTasks={meta.get('progress', {}).get('completedTasks')} != plan [x]={x}")
        opens.append(f"plan: [x]={x} [~]={tilde} [ ]={opencount}; metadata.status={meta.get('status')}")

    for f in fails:
        print("FAIL: " + f, file=sys.stderr)
    for o in opens:
        print("INFO " + o)
    print(f"{len(fails)} FAIL")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()