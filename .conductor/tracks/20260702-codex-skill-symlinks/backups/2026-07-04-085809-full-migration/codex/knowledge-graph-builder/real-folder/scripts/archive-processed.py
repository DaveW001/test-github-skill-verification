#!/usr/bin/env python3
r"""
archive-processed.py - Move processed inbox files to a date-stamped archive folder.

Uses the same seen.json registry as ingest-inbox.py to determine which files
have been processed. Moves them into:
    <inbox>/archive/YYYY-MM-DD/<original_relative_path>

Usage:
    python archive-processed.py --inbox "C:/development/02-Kx-to-process/10 inbox" \
                                --kb "C:/development/02-Kx-to-process/knowledge-base" \
                                [--dry-run] [--verbose]
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def load_seen(kb_path: Path) -> dict:
    """Load seen-file registry (file_hash -> relative_path)."""
    seen_path = kb_path / "logs" / "seen.json"
    if seen_path.exists():
        with open(seen_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def archive_processed(inbox: Path, kb: Path, dry_run: bool = False, verbose: bool = False) -> list:
    """Move processed files to archive folder. Returns list of archived paths."""
    seen = load_seen(kb)
    if not seen:
        print("No processed files found in registry.")
        return []

    today = datetime.now().strftime("%Y-%m-%d")
    # Archive is at the pipeline level, not inside inbox
    # Pipeline: 10 inbox → 20 planning → ... → 50 outbox → 60 archive
    pipeline_root = inbox.parent
    archive_dir = pipeline_root / "60 archive" / today

    archived = []
    for file_hash, rel_path in seen.items():
        # Skip entries with non-string values (legacy metadata dicts)
        if not isinstance(rel_path, (str, Path)):
            if verbose:
                print(f"  SKIP (non-path entry): {file_hash[:8]}... -> {type(rel_path).__name__}")
            continue
        src = inbox / rel_path
        if not src.exists():
            if verbose:
                print(f"  SKIP (not in inbox): {rel_path}")
            continue

        dst = archive_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dry_run:
            print(f"  WOULD MOVE: {rel_path} -> archive/{today}/{rel_path}")
        else:
            shutil.move(str(src), str(dst))
            if verbose:
                print(f"  MOVED: {rel_path} -> archive/{today}/{rel_path}")
        archived.append(rel_path)

    # Remove empty subfolders left behind in inbox
    if not dry_run and archived:
        for dirpath in sorted(
            (d for d in inbox.rglob("*") if d.is_dir()), reverse=True
        ):
            try:
                if not any(dirpath.iterdir()):
                    dirpath.rmdir()
                    if verbose:
                        print(f"  REMOVED EMPTY DIR: {dirpath.relative_to(inbox)}")
            except OSError:
                pass

    return archived


def main():
    parser = argparse.ArgumentParser(description="Archive processed inbox files")
    parser.add_argument("--inbox", required=True, help="Path to inbox folder")
    parser.add_argument("--kb", required=True, help="Path to knowledge-base folder")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    inbox = Path(args.inbox)
    kb = Path(args.kb)

    if not inbox.exists():
        print(f"ERROR: Inbox not found: {inbox}")
        return 1

    if not kb.exists():
        print(f"ERROR: Knowledge-base not found: {kb}")
        return 1

    print(f"Inbox: {inbox}")
    print(f"Archive target: {inbox.parent / '60 archive'}")

    archived = archive_processed(inbox, kb, dry_run=args.dry_run, verbose=args.verbose)

    print(f"\n--- Summary ---")
    print(f"Archived: {len(archived)} files")
    if args.dry_run:
        print("(DRY RUN — no files were moved)")

    return 0


if __name__ == "__main__":
    exit(main())
