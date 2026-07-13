#!/usr/bin/env python3
r"""
query-kb.py - BM25 query against the SQLite FTS5 index with metadata filtering.

Usage:
    python query-kb.py --kb "C:/development/02-Kx-to-process/knowledge-base" \
                       --query "C2 transformation stakeholders" \
                       [--type person] [--confidence high] [--top-k 10]

Features:
    - Metadata filter -> BM25 ranking -> optional type/confidence filtering
    - Highlights matching terms
    - Shows provenance (sources) for each result
"""

import argparse
import sqlite3
import sys
from pathlib import Path

DB_FILENAME = "graph-index.db"


def query_bm25(conn: sqlite3.Connection, query: str, entity_type: str = None,
               confidence: str = None, review_status: str = None, top_k: int = 10):
    """Run BM25 query with optional metadata filtering."""

    # Handle empty query
    if not query or not query.strip():
        return []

    # Build the SQL query
    # FTS5 match with BM25 ranking
    # Wrap each word in double quotes to prevent syntax errors with special chars (/, -, etc.)
    # while maintaining bag-of-words search behavior (instead of one giant exact phrase).
    safe_words = []
    for word in query.split():
        escaped = word.replace('"', '""')
        safe_words.append(f'"{escaped}"')
    fts_query = " ".join(safe_words)

    sql = """
        SELECT e.id, e.type, e.name, e.aliases, e.confidence, e.review_status,
               e.last_updated, e.summary, e.relationships,
               bm25(fts_entities) as rank
        FROM entities e
        JOIN fts_entities f ON e.rowid = f.rowid
        WHERE fts_entities MATCH ?
    """
    params = [fts_query]

    if entity_type:
        sql += " AND e.type = ?"
        params.append(entity_type)
    if confidence:
        sql += " AND e.confidence = ?"
        params.append(confidence)
    if review_status:
        sql += " AND e.review_status = ?"
        params.append(review_status)

    sql += " ORDER BY bm25(fts_entities) LIMIT ?"
    params.append(top_k)

    try:
        cursor = conn.execute(sql, params)
        return cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Query error: {e}")
        print(f"FTS query was: {fts_query}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Query knowledge-base with BM25")
    parser.add_argument("--kb", required=True, help="Path to knowledge-base folder")
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--type", "-t", help="Filter by entity type (person, organization, etc.)")
    parser.add_argument("--confidence", "-c", help="Filter by confidence (high, medium, low)")
    parser.add_argument("--status", "-s", help="Filter by review_status")
    parser.add_argument("--top-k", "-k", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full summaries")
    args = parser.parse_args()

    kb = Path(args.kb)
    db_path = kb / "indexes" / DB_FILENAME

    if not db_path.exists():
        print(f"ERROR: Index not found at {db_path}")
        print("Run build-index.py first.")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")

    print(f"Query: {args.query}")
    filters = []
    if args.type:
        filters.append(f"type={args.type}")
    if args.confidence:
        filters.append(f"confidence={args.confidence}")
    if filters:
        print(f"Filters: {', '.join(filters)}")
    print(f"Top-K: {args.top_k}")
    print()

    results = query_bm25(conn, args.query, args.type, args.confidence, args.status, args.top_k)

    if not results:
        print("No results found.")
        conn.close()
        return

    print(f"Found {len(results)} results:\n")
    print(f"{'Rank':>6} | {'Type':<14} | {'Name':<30} | {'Confidence':<10} | {'Status':<14}")
    print("-" * 85)

    for row in results:
        eid, etype, name, aliases, conf, rstatus, updated, summary, rels, rank = row
        marker = "***" if conf == "high" else "   "
        print(f"{rank:>6.1f} | {etype:<14} | {name:<30} | {conf:<10} | {rstatus:<14}")

        if args.verbose and summary:
            # Show first 150 chars of summary
            short = summary[:150].replace("\n", " ").strip()
            if len(summary) > 150:
                short += "..."
            print(f"         {short}")
            print()

    conn.close()


if __name__ == "__main__":
    main()
