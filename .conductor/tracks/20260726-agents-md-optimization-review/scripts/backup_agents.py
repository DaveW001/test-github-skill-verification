#!/usr/bin/env python3
"""Create immutable, verified AGENTS backups without writing any live target."""
from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

from bootstrap_review_toolchain import (
    ToolchainError,
    assert_no_reparse,
    assert_within,
    canonical,
    file_record,
    json_line,
    read_json,
    sha256_file,
    write_json,
)


def backup_destination(root: Path, target: dict[str, Any], index: int) -> Path:
    explicit = target.get("backup_path")
    if explicit:
        proposed = Path(explicit)
        destination = proposed if proposed.is_absolute() else root / proposed
    else:
        digest = str(target.get("sha256", "unknown"))[:16]
        destination = root / "files" / f"{index:03d}-{digest}-AGENTS.md"
    # Path.absolute() retains a lexical parent segment on some platforms, so
    # normalize before the reparse and root-boundary checks.  This is a
    # fail-closed check; a backup destination may never climb out of root.
    normalized_root = Path(os.path.abspath(str(root)))
    normalized_destination = Path(os.path.abspath(str(destination)))
    common = os.path.commonpath((str(normalized_root), str(normalized_destination)))
    if os.path.normcase(common) != os.path.normcase(str(normalized_root)):
        raise ToolchainError(f"backup destination escapes named root: {destination}")
    return assert_within(normalized_destination, normalized_root, label="backup destination")


def backup_inventory(inventory: dict[str, Any], backup_root: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    root = assert_no_reparse(backup_root, label="backup root")
    root.mkdir(parents=True, exist_ok=True)
    root = assert_no_reparse(root, label="backup root")
    manifest = canonical(manifest_path)
    if manifest.name.casefold() == "agents.md":
        raise ToolchainError("backup manifest must not be an AGENTS.md target")
    entries: list[dict[str, Any]] = []
    source_keys: set[str] = set()
    destination_keys: set[str] = set()
    for index, target in enumerate(inventory.get("targets", []), start=1):
        source = assert_no_reparse(target.get("path", ""), label="backup source")
        if source.name.casefold() != "agents.md":
            raise ToolchainError(f"backup source is not an AGENTS.md target: {source}")
        if not source.is_file():
            raise ToolchainError(f"backup source missing: {source}")
        source_key = str(canonical(source)).casefold()
        if source_key in source_keys:
            raise ToolchainError(f"duplicate source mapping rejected: {source}")
        source_keys.add(source_key)
        before = file_record(source)
        expected_hash = target.get("sha256")
        expected_bytes = target.get("bytes")
        if expected_hash != before["sha256"] or expected_bytes != before["bytes"]:
            raise ToolchainError(f"source hash/length drift rejected before backup: {source}")
        destination = backup_destination(root, target, index)
        destination_key = str(canonical(destination)).casefold()
        if destination_key in destination_keys:
            raise ToolchainError(f"duplicate backup mapping rejected: {destination}")
        destination_keys.add(destination_key)
        if destination.exists():
            raise ToolchainError(f"backup destination already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        after = file_record(source)
        copied = file_record(destination)
        if after["sha256"] != before["sha256"] or after["bytes"] != before["bytes"]:
            raise ToolchainError(f"source changed while copying; backup rejected: {source}")
        if copied["sha256"] != before["sha256"] or copied["bytes"] != before["bytes"]:
            raise ToolchainError(f"backup hash/length mismatch: {source}")
        entries.append({
            "source": before["path"],
            "backup": copied["path"],
            "sha256": before["sha256"],
            "bytes": before["bytes"],
            "scope": target.get("scope"),
            "tracked": target.get("tracked"),
            "dirty": target.get("dirty"),
        })
    restore_simulation(entries)
    result = {
        "version": 1,
        "backup_root": str(root),
        "entries": entries,
        "targets": len(entries),
        "verified": len(entries),
        "restore_simulation": "PASS",
    }
    write_json(manifest, result)
    return result


def restore_simulation(entries: list[dict[str, Any]]) -> None:
    """Copy each backup only to a temporary disposable tree and verify its hash."""
    with tempfile.TemporaryDirectory(prefix="agents-backup-restore-") as temporary:
        root = Path(temporary)
        for index, entry in enumerate(entries, start=1):
            source = assert_no_reparse(entry["backup"], label="backup restore source")
            destination = root / f"{index:03d}-AGENTS.md"
            shutil.copyfile(source, destination)
            if sha256_file(destination) != entry["sha256"] or destination.stat().st_size != entry["bytes"]:
                raise ToolchainError(f"disposable restore hash/length mismatch: {source}")


def verify_manifest(manifest: dict[str, Any]) -> None:
    root = assert_no_reparse(manifest.get("backup_root", ""), label="manifest backup root")
    seen_sources: set[str] = set()
    seen_backups: set[str] = set()
    for entry in manifest.get("entries", []):
        source_key = str(canonical(entry.get("source", ""))).casefold()
        backup = assert_within(entry.get("backup", ""), root, label="manifest backup")
        backup_key = str(canonical(backup)).casefold()
        if source_key in seen_sources or backup_key in seen_backups:
            raise ToolchainError("manifest duplicate source/backup mapping")
        seen_sources.add(source_key)
        seen_backups.add(backup_key)
        if not backup.is_file() or sha256_file(backup) != entry.get("sha256") or backup.stat().st_size != entry.get("bytes"):
            raise ToolchainError(f"manifest backup verification failed: {backup}")
    restore_simulation(manifest.get("entries", []))


def expect_failure(operation: Any, label: str) -> None:
    try:
        operation()
    except ToolchainError:
        return
    raise ToolchainError(f"self-test expected guard failure: {label}")


def self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="backup-agents-self-test-") as temporary:
        fixture = Path(temporary)
        source = fixture / "fixture" / "AGENTS.md"
        source.parent.mkdir(parents=True)
        source.write_text("fixture safety guidance\n", encoding="utf-8")
        source_record = file_record(source)
        inventory = {
            "targets": [{
                **source_record,
                "scope": "local",
                "tracked": False,
                "dirty": False,
            }]
        }
        backup_root = fixture / "backups"
        manifest_path = fixture / "manifest.json"
        manifest = backup_inventory(inventory, backup_root, manifest_path)
        verify_manifest(manifest)
        if manifest["restore_simulation"] != "PASS":
            raise ToolchainError("restore simulation did not pass")

        escaped = {"targets": [{**inventory["targets"][0], "backup_path": "../escaped/AGENTS.md"}]}
        expect_failure(lambda: backup_inventory(escaped, fixture / "escape-root", fixture / "escape.json"), "path escape")
        duplicated = {"targets": [inventory["targets"][0], dict(inventory["targets"][0])]}
        expect_failure(lambda: backup_inventory(duplicated, fixture / "duplicate-root", fixture / "duplicate.json"), "duplicate map")
        drifted = {"targets": [{**inventory["targets"][0], "sha256": "0" * 64}]}
        expect_failure(lambda: backup_inventory(drifted, fixture / "drift-root", fixture / "drift.json"), "hash drift")

        copied_backup = Path(manifest["entries"][0]["backup"])
        copied_backup.write_text("corrupted backup\n", encoding="utf-8")
        expect_failure(lambda: verify_manifest(manifest), "backup hash corruption")
        junction = fixture / "junction" / "AGENTS.md"
        junction.parent.mkdir()
        junction.write_text("synthetic reparse guard fixture\n", encoding="utf-8")
        junction_record = file_record(junction)
        linked_inventory = {"targets": [{**junction_record, "tracked": False, "dirty": False}]}

        def synthetic_reparse(path: str | Path) -> bool:
            return canonical(path) == canonical(junction)

        # Simulate the platform reparse-point predicate so this proof is
        # deterministic even where symlink creation is privilege-restricted.
        with patch("bootstrap_review_toolchain.is_reparse_point", side_effect=synthetic_reparse):
            expect_failure(lambda: backup_inventory(linked_inventory, fixture / "junction-root", fixture / "junction.json"), "junction")
    return {
        "check": "backup-self-test",
        "status": "PASS",
        "negative_case_count": 5,
        "live_targets_touched": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Back up AGENTS targets with path, junction, hash, and restore guards.")
    parser.add_argument("--inventory")
    parser.add_argument("--backup-root")
    parser.add_argument("--manifest")
    parser.add_argument("--self-test", action="store_true", help="run only disposable backup fixtures")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            print(json_line(self_test()))
            return 0
        if not args.inventory or not args.backup_root or not args.manifest:
            raise ToolchainError("--inventory, --backup-root, and --manifest are required unless --self-test is used")
        result = backup_inventory(read_json(args.inventory), args.backup_root, args.manifest)
        print(json_line({
            "check": "backups",
            "status": "PASS",
            "targets": result["targets"],
            "verified": result["verified"],
            "restore_simulation": result["restore_simulation"],
        }))
        return 0
    except (ToolchainError, OSError, ValueError) as exc:
        print(json_line({"check": "backups", "status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
