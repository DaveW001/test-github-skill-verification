"""drive-download.py — Download a file from Google Drive using gws CLI.

Wraps the gws drive files get command for downloads.

Example:
    python drive-download.py --file-id FILE_ID --output ./downloaded-file
"""
import argparse
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
        description="Download a file from Google Drive using gws CLI."
    )
    parser.add_argument(
        "--file-id", "-i",
        required=True,
        help="Google Drive file ID to download"
    )
    parser.add_argument(
        "--output", "-o",
        default="./downloaded-file",
        help="Local output path (default: ./downloaded-file)"
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

    import json
    cmd = [
        gws, "drive", "files", "get",
        "--params", json.dumps({"fileId": args.file_id}),
        "--output", args.output,
    ]

    if args.dry_run:
        print("Dry-run command:")
        print(" ".join(cmd))
        return

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    print(result.stdout)
    if result.stdout.strip():
        print(f"Downloaded to {args.output}")


if __name__ == "__main__":
    main()
