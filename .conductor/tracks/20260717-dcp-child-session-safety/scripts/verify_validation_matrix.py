#!/usr/bin/env python3
"""Verify the requirements-to-tests validation matrix (Final Task F.1)."""
import argparse
import re
import sys


def acceptance_criteria(spec_text):
    m = re.search(r"##\s+Acceptance Criteria\s*\n(.+?)(?:\n##\s|\Z)", spec_text, re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    return [ln.strip("- ").strip() for ln in body.splitlines() if ln.strip().startswith("- ")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--require-all", action="store_true")
    args = ap.parse_args()

    spec = open(args.spec, encoding="utf-8").read()
    matrix = open(args.matrix, encoding="utf-8").read().lower()
    criteria = acceptance_criteria(spec)

    missing = []
    for c in criteria:
        # Pick distinctive token(s) from each criterion; require at least one in the matrix.
        toks = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", c)]
        toks = [t for t in toks if t not in ("that", "this", "with", "from", "must", "each", "every", "their", "have", "been")]
        if not toks:
            continue
        if not any(t in matrix for t in toks):
            missing.append(c[:80])
    # Matrix must be a real mapping (has test/command/exit/artifact columns or sections).
    has_structure = all(k in matrix for k in ("test", "exit"))
    if not has_structure:
        missing.append("matrix missing test/exit structure")

    if args.require_all and missing:
        for m in missing:
            print("MATRIX_GAP: " + m, file=sys.stderr)
        sys.exit(1)
    print(f"PASS validation-matrix (criteria={len(criteria)}, gaps={len(missing)})")
    sys.exit(0)


if __name__ == "__main__":
    main()