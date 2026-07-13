"""gmail-triage.py - Triage Gmail messages using gws CLI.

Wraps the gws gmail +triage command for batch triage operations.

Example:
    python gmail-triage.py --max 20 --output triage.json
    python gmail-triage.py --query "is:unread" --max 10
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
        description="Triage Gmail messages using gws CLI."
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=10,
        help="Maximum number of messages to triage (default: 10)"
    )
    parser.add_argument(
        "--query", "-q",
        default=None,
        help="Gmail search query (e.g. 'is:unread', 'from:boss')"
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

    cmd = [gws, "gmail", "+triage", "--max", str(args.max)]

    if args.query:
        cmd.extend(["--query", args.query])

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
