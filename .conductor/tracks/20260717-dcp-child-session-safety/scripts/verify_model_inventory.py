#!/usr/bin/env python3
"""Verify the active-model inventory (Task 0.3 acceptance)."""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--require-agent", action="append", default=[])
    ap.add_argument("--require-display", action="append", default=[])
    ap.add_argument("--fail-on-unresolved", action="store_true")
    args = ap.parse_args()

    with open(args.inventory, encoding="utf-8") as f:
        inv = json.load(f)
    d2r = inv.get("display_to_runtime", {}) or {}
    agents = inv.get("agents", {}) or {}
    unresolved = inv.get("unresolved", []) or []

    errors = []
    for a in args.require_agent:
        if a not in agents:
            errors.append(f"missing agent: {a}")
    for d in args.require_display:
        if d not in d2r:
            errors.append(f"missing display_to_runtime entry for: {d}")
        elif not d2r[d]:
            errors.append(f"unresolved display_to_runtime value for: {d}")
    if len(d2r) < 6:
        errors.append(f"display_to_runtime has {len(d2r)} entries, need >= 6")
    if args.fail_on_unresolved and unresolved:
        errors.append(f"unresolved entries present: {unresolved}")

    if errors:
        for e in errors:
            print("FAIL: " + e, file=sys.stderr)
        sys.exit(1)
    print("PASS model-inventory")
    sys.exit(0)


if __name__ == "__main__":
    main()