"""calendar-list.py - List Google Calendar events using gws CLI.

Wraps the gws calendar events list command for batch operations.

Example:
    python calendar-list.py --days 7 --output events.json
    python calendar-list.py --calendar-id "primary" --days 30 --output month.json
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone


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
        description="List Google Calendar events using gws CLI."
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=7,
        help="Number of days to look ahead (default: 7)"
    )
    parser.add_argument(
        "--calendar-id",
        default="primary",
        help="Calendar ID (default: primary)"
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

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=args.days)
    time_min = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    time_max = end.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "calendarId": args.calendar_id,
        "timeMin": time_min,
        "timeMax": time_max,
        "singleEvents": True,
        "orderBy": "startTime",
    }

    cmd = [
        gws, "calendar", "events", "list",
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
