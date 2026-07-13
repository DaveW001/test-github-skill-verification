"""docs-export.py — Export a Google Doc using gws CLI.

Wraps the gws docs documents get command to export a Google Doc as JSON.
Full markdown conversion is a future enhancement (v1 exports raw Docs JSON).

Example:
    python docs-export.py --document-id DOC_ID --output doc.json
"""
import argparse
import json
import shutil
import subprocess
import sys


def find_gws() -> str:
    """Locate the gws executable."""
    gws = shutil.which("gws")
    if gws:
        return gws
    fallback = r"C:\Users\DaveWitkin\.cargo\bin\gws.exe"
    if shutil.which(fallback):
        return fallback
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Export a Google Doc as JSON using gws CLI. "
                    "Note: v1 exports raw Docs JSON; full markdown conversion is a future enhancement."
    )
    parser.add_argument(
        "--document-id", "-d",
        required=True,
        help="Google Docs document ID to export"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (JSON). Prints to stdout if omitted."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the gws command without executing it."
    )
    args = parser.parse_args()

    gws = find_gws()
    if not gws:
        print("Error: gws CLI not found; run Phase 0.2", file=sys.stderr)
        sys.exit(1)

    cmd = [
        gws, "docs", "documents", "get",
        "--params", json.dumps({"documentId": args.document_id}),
        "--format", "json",
    ]

    if args.dry_run:
        print("Dry-run command:")
        print(" ".join(cmd))
        return

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        print(f"Output written to {args.output}")
    else:
        print(result.stdout)


if __name__ == "__main__":
    main()
