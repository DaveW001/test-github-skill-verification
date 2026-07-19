#!/usr/bin/env python3
"""Verify DCP modelMaxLimits exact-150K caps (Task 4.1 acceptance).

JSONC-aware: strips // line comments, /* */ block comments (string-aware) and
trailing commas, then parses with strict=False to tolerate control chars.
Semantics: required keys (from inventory) must be a SUBSET of the file's
compress.modelMaxLimits keys; each required key present must equal integer 150000;
extra unrelated keys are allowed.
"""
import argparse
import json
import re
import sys


def parse_jsonc(text):
    out = []
    i, n = 0, len(text)
    in_str = False
    q = ""
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1]); i += 2; continue
            if c == q:
                in_str = False
            i += 1; continue
        if c in ('"', "'"):
            in_str = True; q = c; out.append(c); i += 1; continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2; continue
        out.append(c); i += 1
    s = "".join(out)
    s = re.sub(r",(\s*[}\]])", r"\1", s)
    return json.loads(s, strict=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--expected", type=int, required=True)
    ap.add_argument("--require-required-subset-and-exact-value", action="store_true")
    args = ap.parse_args()

    with open(args.inventory, encoding="utf-8") as f:
        inv = json.load(f)
    required = list(inv.get("required_keys", []))
    with open(args.config, encoding="utf-8") as f:
        cfg = parse_jsonc(f.read())
    limits = (cfg.get("compress") or {}).get("modelMaxLimits") or {}

    missing = [k for k in required if k not in limits]
    wrong = []
    non_integer = []
    for k in required:
        if k in limits:
            v = limits[k]
            if v != args.expected:
                wrong.append((k, v))
            if not (isinstance(v, int) and not isinstance(v, bool)):
                non_integer.append((k, v))
    extras = sorted([k for k in limits if k not in required])

    if missing or wrong or non_integer:
        if missing:
            print("MISSING_KEYS: " + ", ".join(missing), file=sys.stderr)
        if wrong:
            print("WRONG_VALUES: " + ", ".join(f"{k}={v}" for k, v in wrong), file=sys.stderr)
        if non_integer:
            print("NON_INTEGER: " + ", ".join(f"{k}={v!r}" for k, v in non_integer), file=sys.stderr)
        sys.exit(1)
    print(f"PASS dcp-limits (required={len(required)} all=={args.expected}, extras_preserved={len(extras)})")
    sys.exit(0)


if __name__ == "__main__":
    main()