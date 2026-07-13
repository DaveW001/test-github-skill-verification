#!/usr/bin/env python3
r"""
build-index.py - Build/rebuild SQLite FTS5 index from knowledge-base markdown notes.

Usage:
    python build-index.py --kb "C:/development/02-Kx-to-process/knowledge-base"

Features:
    - SQLite WAL mode for safe concurrent reads
    - FTS5 with porter tokenizer (stemming) for acronym-heavy military content
    - Indexes: entity name, aliases, summary text, relationship predicates
    - Metadata table: type, confidence, review_status, last_updated
    - Idempotent: drops and recreates FTS tables on each run
"""

import argparse
import re
import sys
from pathlib import Path

import sqlite3

# --- Config ---
# Explicit C2 entity folders ONLY — do NOT add packaged-agile-kg, indexes, logs, summaries.
# The PA KG is a separate knowledge base with its own index structure.
KB_FOLDERS = {
    "people": "person",
    "organizations": "organization",
    "programs": "program",
    "roles": "role",
    "acronyms": "acronym",
    "events": "event",
    "sources": "source",
    "concepts": "concept",
    "decisions": "decision",
    "risks": "risk",
    "actions": "action",
}

DB_FILENAME = "graph-index.db"


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from markdown text."""
    fm = {}
    if not text.startswith("---"):
        return fm
    parts = text.split("---", 2)
    if len(parts) < 3:
        return fm
    yaml_text = parts[1].strip()
    for line in yaml_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("-"):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.startswith("["):
                # Simple list parsing
                val = [v.strip().strip('"').strip("'") for v in val.strip("[]").split(",") if v.strip()]
            fm[key] = val
    return fm


def extract_body_sections(text: str) -> dict:
    """Extract ## Summary and ## Relationships sections from body."""
    sections = {"summary": "", "relationships": ""}
    # Remove frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
        else:
            body = text
    else:
        body = text

    current = None
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## Summary"):
            current = "summary"
            continue
        elif stripped.startswith("## Relationships"):
            current = "relationships"
            continue
        elif stripped.startswith("## ") or stripped.startswith("# "):
            current = None
            continue
        if current and current in sections:
            sections[current] += line + "\n"
    return sections


def extract_aliases_value(fm: dict) -> str:
    """Extract aliases as a space-separated string for indexing."""
    aliases = fm.get("aliases", [])
    if isinstance(aliases, list):
        return " ".join(str(a) for a in aliases)
    return str(aliases)


def index_folder(kb_path: Path, folder_name: str, entity_type: str, conn: sqlite3.Connection):
    """Index all .md files in a folder."""
    folder = kb_path / folder_name
    if not folder.exists():
        return 0

    count = 0
    for f in folder.glob("*.md"):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  WARNING: Could not read {f}: {e}")
            continue

        fm = parse_frontmatter(text)
        sections = extract_body_sections(text)

        entity_id = fm.get("id", f.stem)
        name = fm.get("name", f.stem)
        aliases = extract_aliases_value(fm)
        confidence = fm.get("confidence", "unknown")
        review_status = fm.get("review_status", "unknown")
        last_updated = fm.get("last_updated", "")
        sources = str(fm.get("sources", ""))

        # Insert into entities table
        conn.execute(
            """INSERT OR REPLACE INTO entities
               (id, type, name, aliases, confidence, review_status, last_updated, sources, summary, relationships, file_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (entity_id, entity_type, name, aliases, confidence, review_status,
             last_updated, sources, sections["summary"].strip(), sections["relationships"].strip(), str(f))
        )

        # Insert into FTS5
        # If it's a source note, index the entire text. Otherwise, just summary + relationships.
        if entity_type == "source":
            fts_content = f"{name} {aliases} {sections['summary']} {sections['relationships']} {text}"
        else:
            fts_content = f"{name} {aliases} {sections['summary']} {sections['relationships']}"
            
        conn.execute(
            "INSERT INTO fts_entities(rowid, content) VALUES ((SELECT rowid FROM entities WHERE id = ?), ?)",
            (entity_id, fts_content)
        )

        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="Build SQLite FTS5 index from knowledge-base")
    parser.add_argument("--kb", required=True, help="Path to knowledge-base folder")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    kb = Path(args.kb)
    if not kb.exists():
        print(f"ERROR: Knowledge-base not found: {kb}")
        sys.exit(1)

    db_path = kb / "indexes" / DB_FILENAME
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Building index: {db_path}")
    print(f"Knowledge-base: {kb}")

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")

    # Create tables
    conn.execute("DROP TABLE IF EXISTS fts_entities")
    conn.execute("DROP TABLE IF EXISTS entities")

    conn.execute("""
        CREATE TABLE entities (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            aliases TEXT DEFAULT '',
            confidence TEXT DEFAULT 'unknown',
            review_status TEXT DEFAULT 'needs_review',
            last_updated TEXT DEFAULT '',
            sources TEXT DEFAULT '',
            summary TEXT DEFAULT '',
            relationships TEXT DEFAULT '',
            file_path TEXT DEFAULT ''
        )
    """)

    # FTS5 with porter tokenizer for stemming (helps with military acronyms)
    conn.execute("""
        CREATE VIRTUAL TABLE fts_entities USING fts5(
            content,
            tokenize='porter unicode61'
        )
    """)

    total = 0
    for folder_name, entity_type in KB_FOLDERS.items():
        count = index_folder(kb, folder_name, entity_type, conn)
        if count > 0:
            print(f"  {folder_name}/: {count} notes indexed")
        total += count

    conn.commit()
    conn.close()

    print(f"\nTotal entities indexed: {total}")
    print(f"Database: {db_path}")


if __name__ == "__main__":
    main()
