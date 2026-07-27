#!/usr/bin/env python3
"""Duplicate-safe upsert for both Conductor ledgers."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    ToolchainError,
    canonical,
    fail,
    json_line,
    read_json,
)


def _same_path(left: str | Path, right: str | Path) -> bool:
    return os.path.normcase(str(canonical(left))) == os.path.normcase(
        str(canonical(right))
    )


def _safe_cell(value: Any) -> str:
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def _progress(metadata: dict[str, Any]) -> tuple[int, int]:
    progress = metadata.get("progress")
    if isinstance(progress, dict):
        completed = progress.get("completedTasks")
        total = progress.get("totalTasks")
    else:
        completed = metadata.get("completed_tasks")
        total = metadata.get("total_tasks")
    if not isinstance(completed, int) or not isinstance(total, int):
        fail("metadata progress must contain integer completedTasks and totalTasks")
    if completed < 0 or total <= 0 or completed > total:
        fail("metadata progress is out of range")
    return completed, total


def _metadata_fields(
    track: Path, metadata: dict[str, Any]
) -> tuple[str, str, str, str, int, int]:
    track_id = metadata.get("trackId") or metadata.get("track_id") or track.name
    if track_id != track.name:
        fail("metadata track identity does not match track folder")
    title = metadata.get("title")
    status = metadata.get("status")
    created = metadata.get("created") or metadata.get("created_at")
    completed_date = metadata.get("completed") or metadata.get("completed_at")
    if not isinstance(title, str) or not title.strip():
        fail("metadata title is required")
    if not isinstance(status, str) or not status.strip():
        fail("metadata status is required")
    if not isinstance(created, str) or not created.strip():
        fail("metadata created date is required")
    date = completed_date if isinstance(completed_date, str) and completed_date else created
    completed, total = _progress(metadata)
    return track_id, title, status, date, completed, total


def build_tracks_row(track: Path, metadata: dict[str, Any]) -> str:
    track_id, title, status, date, completed, total = _metadata_fields(
        track, metadata
    )
    completed_field = (
        f"{date} ({completed}/{total})"
        if metadata.get("completed") or metadata.get("completed_at")
        else f"{completed}/{total}"
    )
    return (
        f"| {_safe_cell(track_id)} | {_safe_cell(title)} | {_safe_cell(status)} | "
        f"{_safe_cell(completed_field)} | {_safe_cell(track)} |"
    )


def build_ledger_entry(track: Path, metadata: dict[str, Any]) -> str:
    track_id, _title, status, date, completed, total = _metadata_fields(
        track, metadata
    )
    summary = metadata.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        fail("metadata summary is required")
    return (
        f"- [{track_id}](./tracks/{track_id}/spec.md): "
        f"{summary.strip()} (Phase: {status} {date}, {completed}/{total} tasks)"
    )


def _upsert_tracks_text(text: str, track_id: str, row: str) -> str:
    lines = text.splitlines()
    pattern = re.compile(rf"^\|\s*{re.escape(track_id)}\s*\|")
    matches = [index for index, line in enumerate(lines) if pattern.match(line)]
    if len(matches) > 1:
        fail(f"ambiguous duplicate rows in tracks.md for {track_id}")
    if matches:
        lines[matches[0]] = row
    else:
        header = next(
            (
                index
                for index, line in enumerate(lines)
                if re.match(r"^\|\s*Track ID\s*\|", line, re.IGNORECASE)
            ),
            None,
        )
        if header is None:
            fail("tracks.md table header was not found")
        insertion = header + 1
        if insertion < len(lines) and re.match(
            r"^\|\s*:?-+", lines[insertion]
        ):
            insertion += 1
        lines.insert(insertion, row)
    result = "\n".join(lines) + "\n"
    if sum(1 for line in result.splitlines() if pattern.match(line)) != 1:
        fail("tracks.md upsert did not produce exactly one row")
    return result


def _upsert_ledger_text(text: str, track_id: str, entry: str) -> str:
    lines = text.splitlines()
    pattern = re.compile(rf"^-\s*\[{re.escape(track_id)}\]\(")
    matches = [index for index, line in enumerate(lines) if pattern.match(line)]
    if len(matches) > 1:
        fail(f"ambiguous duplicate entries in tracks-ledger.md for {track_id}")
    if matches:
        lines[matches[0]] = entry
    else:
        active = next(
            (
                index
                for index, line in enumerate(lines)
                if line.strip().lower() == "## active tracks"
            ),
            None,
        )
        if active is None:
            fail("tracks-ledger.md Active Tracks section was not found")
        lines.insert(active + 1, entry)
    result = "\n".join(lines) + "\n"
    if sum(1 for line in result.splitlines() if pattern.match(line)) != 1:
        fail("tracks-ledger.md upsert did not produce exactly one entry")
    return result


def build_ledger_updates(
    *,
    track: str | Path,
    tracks_text: str,
    ledger_text: str,
    metadata: dict[str, Any],
) -> tuple[str, str]:
    root = canonical(track)
    track_id = metadata.get("trackId") or metadata.get("track_id") or root.name
    return (
        _upsert_tracks_text(tracks_text, track_id, build_tracks_row(root, metadata)),
        _upsert_ledger_text(
            ledger_text, track_id, build_ledger_entry(root, metadata)
        ),
    )


def _atomic_pair(
    first_path: Path, first_text: str, second_path: Path, second_text: str
) -> None:
    originals = {
        first_path: first_path.read_bytes(),
        second_path: second_path.read_bytes(),
    }
    replacements = {first_path: first_text, second_path: second_text}
    temporaries: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, text in replacements.items():
            temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
            temporary.write_text(text, encoding="utf-8", newline="\n")
            temporaries[path] = temporary
        for path in (first_path, second_path):
            os.replace(temporaries[path], path)
            replaced.append(path)
        if first_path.read_text(encoding="utf-8") != first_text:
            fail("tracks.md post-write verification failed")
        if second_path.read_text(encoding="utf-8") != second_text:
            fail("tracks-ledger.md post-write verification failed")
    except BaseException:
        for path in reversed(replaced):
            recovery = path.with_name(f".{path.name}.rollback-{os.getpid()}")
            recovery.write_bytes(originals[path])
            os.replace(recovery, path)
        raise
    finally:
        for temporary in temporaries.values():
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def sync_ledgers(
    *, track: str | Path, tracks: str | Path, ledger: str | Path
) -> dict[str, Any]:
    root = canonical(track)
    tracks_path = canonical(tracks)
    ledger_path = canonical(ledger)
    conductor = root.parent.parent
    if not _same_path(tracks_path, conductor / "tracks.md"):
        fail("--tracks must name the workspace .conductor/tracks.md")
    if not _same_path(ledger_path, conductor / "tracks-ledger.md"):
        fail("--ledger must name the workspace .conductor/tracks-ledger.md")
    if not tracks_path.is_file() or not ledger_path.is_file():
        fail("both Conductor ledger files must already exist")
    metadata = read_json(root / "metadata.json")
    if not isinstance(metadata, dict):
        fail("metadata.json must be an object")
    original_tracks = tracks_path.read_text(encoding="utf-8-sig")
    original_ledger = ledger_path.read_text(encoding="utf-8-sig")
    updated_tracks, updated_ledger = build_ledger_updates(
        track=root,
        tracks_text=original_tracks,
        ledger_text=original_ledger,
        metadata=metadata,
    )
    _atomic_pair(tracks_path, updated_tracks, ledger_path, updated_ledger)
    completed, total = _progress(metadata)
    return {
        "check": "ledgers",
        "status": "PASS",
        "track": root.name,
        "metadata_status": metadata["status"],
        "progress": f"{completed}/{total}",
        "tracks_rows": 1,
        "ledger_entries": 1,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Duplicate-safe upsert of both Conductor ledgers."
    )
    parser.add_argument("--track", required=True)
    parser.add_argument("--tracks", required=True)
    parser.add_argument("--ledger", required=True)
    args = parser.parse_args(argv)
    try:
        result = sync_ledgers(
            track=args.track, tracks=args.tracks, ledger=args.ledger
        )
        print(json_line(result))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json_line({"check": "ledgers", "status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
