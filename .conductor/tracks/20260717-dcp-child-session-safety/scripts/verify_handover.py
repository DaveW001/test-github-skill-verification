#!/usr/bin/env python3
"""Verify the deployment handover document (Final Task F.2)."""
import argparse
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--require", action="append", default=[])
    args = ap.parse_args()
    text = open(args.path, encoding="utf-8").read()
    missing = [r for r in args.require if r.lower() not in text.lower()]
    if missing:
        for m in missing:
            print("HANDOVER_MISSING: " + m, file=sys.stderr)
        sys.exit(1)
    print(f"PASS handover (required_phrases={len(args.require)})")
    sys.exit(0)


if __name__ == "__main__":
    main()