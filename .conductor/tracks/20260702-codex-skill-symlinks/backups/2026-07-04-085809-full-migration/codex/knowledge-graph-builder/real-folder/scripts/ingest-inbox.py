#!/usr/bin/env python3
r"""
ingest-inbox.py - Batch ingestion from inbox folder into knowledge-base.

Usage:
    python ingest-inbox.py --inbox "C:/development/02-Kx-to-process/10 inbox" \
                           --kb "C:/development/02-Kx-to-process/knowledge-base" \
                           [--dry-run] [--verbose]

Features:
    - SHA-256 content hashing for dedup
    - Dead letter queue (DLQ) for failed files
    - Append-only ingest log
    - Idempotent re-runs (skips already-processed files)
    - Routes .pdf files through doc-to-markdown skill (prints instruction)
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
SUPPORTED_EXTENSIONS = {".md", ".txt", ".docx", ".xlsx", ".pptx", ".pdf"}
PDF_EXTENSIONS = {".pdf"}
GOOGLE_NATIVE = {".gdoc", ".gsheet", ".gslide"}
# C2 entity types only — do NOT include packaged-agile-kg (separate KG)
ENTITY_TYPES = ["person", "organization", "program", "role", "acronym", "event", "concept", "source", "decision", "risk", "action"]

# C2 entity folder mapping only — packaged-agile-kg, indexes, logs, summaries are excluded
KB_FOLDERS = {
    "person": "people",
    "organization": "organizations",
    "program": "programs",
    "role": "roles",
    "acronym": "acronyms",
    "event": "events",
    "source": "sources",
    "concept": "concepts",
    "decision": "decisions",
    "risk": "risks",
    "action": "actions",
}


def sha256_hash(content: bytes) -> str:
    """Hash the first 4096 bytes of content."""
    return hashlib.sha256(content[:4096]).hexdigest()


def load_seen(kb_path: Path) -> dict:
    """Load seen-file registry (file_hash -> relative_path)."""
    seen_path = kb_path / "logs" / "seen.json"
    if seen_path.exists():
        with open(seen_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(kb_path: Path, seen: dict):
    """Persist seen-file registry."""
    seen_path = kb_path / "logs" / "seen.json"
    seen_path.parent.mkdir(parents=True, exist_ok=True)
    with open(seen_path, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2, sort_keys=True)


def append_log(kb_path: Path, entry: dict):
    """Append an entry to the ingest log."""
    log_path = kb_path / "logs" / "ingest-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = entry.get("timestamp", datetime.now(timezone.utc).isoformat())
    status = entry.get("status", "unknown")
    file = entry.get("file", "unknown")
    entities = entry.get("entities_created", 0)
    merged = entry.get("entities_merged", 0)
    errors = entry.get("errors", "")
    line = f"| {ts} | {status} | {file} | {entities} | {merged} | {errors} |\n"
    if not log_path.exists() or log_path.stat().st_size == 0:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("# Ingest Log\n\n")
            f.write("| Timestamp | Status | File | Entities Created | Entities Merged | Errors |\n")
            f.write("|---|---|---|---|---|---|\n")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def move_to_dlq(inbox_path: Path, file_path: Path, reason: str):
    """Move a failed file to the dead letter queue."""
    dlq_dir = inbox_path / ".dlq"
    dlq_dir.mkdir(parents=True, exist_ok=True)
    dest = dlq_dir / file_path.name
    if dest.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        dest = dlq_dir / f"{stem}-{datetime.now().strftime('%Y%m%d%H%M%S')}{suffix}"
    try:
        import shutil
        shutil.move(str(file_path), str(dest))
        # Write reason file
        reason_path = dest.with_suffix(dest.suffix + ".reason")
        with open(reason_path, "w", encoding="utf-8") as f:
            f.write(f"DLQ Reason: {reason}\nMoved: {datetime.now(timezone.utc).isoformat()}\n")
    except Exception as e:
        print(f"  ERROR moving to DLQ: {e}")


def scan_inbox(inbox_path: Path, recursive: bool = True) -> list:
    """Scan inbox for processable files."""
    files = []
    pattern = "**/*" if recursive else "*"
    for f in inbox_path.glob(pattern):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(f)
    return sorted(files)


def check_google_native(file_path: Path) -> bool:
    """Check if file is Google-native (cannot be read)."""
    return file_path.suffix.lower() in GOOGLE_NATIVE


def get_existing_slugs(kb_path: Path) -> set:
    """Get all existing entity slugs from knowledge-base."""
    slugs = set()
    for type_folder in KB_FOLDERS.values():
        folder = kb_path / type_folder
        if folder.exists():
            for f in folder.glob("*.md"):
                slugs.add(f.stem)
    return slugs


def main():
    parser = argparse.ArgumentParser(description="Ingest files from inbox into knowledge-base")
    parser.add_argument("--inbox", required=True, help="Path to inbox folder")
    parser.add_argument("--kb", required=True, help="Path to knowledge-base folder")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    inbox = Path(args.inbox)
    kb = Path(args.kb)

    if not inbox.exists():
        print(f"ERROR: Inbox not found: {inbox}")
        sys.exit(1)
    if not kb.exists():
        print(f"ERROR: Knowledge-base not found: {kb}")
        sys.exit(1)

    # Load state
    seen = load_seen(kb)
    existing_slugs = get_existing_slugs(kb)
    files = scan_inbox(inbox)

    print(f"Inbox: {inbox}")
    print(f"Knowledge-base: {kb}")
    print(f"Files found: {len(files)}")
    print(f"Previously seen: {len(seen)}")
    print(f"Existing entity slugs: {len(existing_slugs)}")
    print()

    stats = {"processed": 0, "skipped": 0, "failed": 0, "dlq": 0, "google_blocked": 0}

    for f in files:
        rel = str(f.relative_to(inbox))
        print(f"  {rel} ... ", end="")

        # Check Google-native
        if check_google_native(f):
            print("BLOCKED (Google-native, needs export)")
            stats["google_blocked"] += 1
            append_log(kb, {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "blocked_google_native",
                "file": rel,
                "entities_created": 0,
                "entities_merged": 0,
                "errors": "Google-native file, needs manual export"
            })
            continue

        # Hash for dedup
        try:
            content = f.read_bytes()
        except Exception as e:
            print(f"READ ERROR: {e}")
            stats["failed"] += 1
            move_to_dlq(inbox, f, str(e))
            stats["dlq"] += 1
            continue

        file_hash = sha256_hash(content)

        # Check if already processed
        if file_hash in seen:
            print(f"SKIPPED (already processed as {seen[file_hash]})")
            stats["skipped"] += 1
            continue

        # Route by file type
        ext = f.suffix.lower()

        if ext in PDF_EXTENSIONS:
            print("PDF — requires doc-to-markdown skill, queuing")
            # PDFs need the doc-to-markdown skill first
            # Print instruction for agent to follow up
            if not args.dry_run:
                append_log(kb, {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "queued_pdf",
                    "file": rel,
                    "entities_created": 0,
                    "entities_merged": 0,
                    "errors": "Requires doc-to-markdown skill before entity extraction"
                })
            stats["processed"] += 1
            continue

        # For .md, .txt, .docx, .xlsx, .pptx — the agent should process these
        # This script handles routing and dedup; the actual entity extraction
        # is done by the agent using the knowledge-graph-builder skill
        print(f"READY (hash: {file_hash[:12]}...)")

        if not args.dry_run:
            seen[file_hash] = rel
            append_log(kb, {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "ready_for_extraction",
                "file": rel,
                "entities_created": 0,
                "entities_merged": 0,
                "errors": ""
            })

        stats["processed"] += 1

    # Save state
    if not args.dry_run:
        save_seen(kb, seen)

    print()
    print("--- Summary ---")
    print(f"Processed/Ready: {stats['processed']}")
    print(f"Skipped (dedup): {stats['skipped']}")
    print(f"Failed:          {stats['failed']}")
    print(f"Moved to DLQ:    {stats['dlq']}")
    print(f"Google-blocked:  {stats['google_blocked']}")

    if args.dry_run:
        print("\n(DRY RUN — no files were modified)")


if __name__ == "__main__":
    main()
