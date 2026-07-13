"""drive-list.py — List Google Drive files using gws CLI.

Wraps the gws drive files list command for batch operations.

Example:
    python drive-list.py --query "name contains 'report'" --output files.json
    python drive-list.py --page-size 50 --output all-files.json
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
        description="List Google Drive files using gws CLI."
    )
    parser.add_argument(
        "--query", "-q",
        default=None,
        help="Drive query string, e.g. \"name contains 'report'\""
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (JSON). Prints to stdout if omitted."
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=10,
        help="Number of results per page (default: 10)"
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

    params = {"pageSize": args.page_size}
    if args.query:
        params["q"] = args.query

    cmd = [
        gws, "drive", "files", "list",
        "--params", json.dumps(params),
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
