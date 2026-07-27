#!/usr/bin/env python3
"""Emit disjoint local AGENTS.md review batches from the frozen inventory."""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from audit_agents import build_packet, write_packet
from bootstrap_review_toolchain import (
    ToolchainError,
    assert_no_reparse,
    assert_within,
    canonical,
    file_record,
    json_line,
    read_json,
)


BATCHES = ("operations", "marketing", "opencode-clones", "opencodex")


def _key(path: str | Path) -> str:
    return os.path.normcase(str(canonical(path)))


def _inventory(path: str | Path) -> dict[str, Any]:
    candidate = assert_no_reparse(path, label="inventory")
    if not candidate.is_file():
        raise ToolchainError(f"missing inventory: {candidate}")
    payload = read_json(candidate)
    if not isinstance(payload, dict) or not isinstance(payload.get("targets"), list):
        raise ToolchainError("inventory must contain a targets list")
    return payload


def _local_records(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, record in enumerate(inventory["targets"]):
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ToolchainError(f"inventory target {index} is malformed")
        if record.get("scope") == "local":
            records.append(record)
    return records


def _normal_root(record: dict[str, Any]) -> str:
    root = record.get("root")
    if not isinstance(root, str) or not root:
        raise ToolchainError(f"local inventory target lacks root: {record.get('path')}")
    return root.replace("/", "\\").rstrip("\\").casefold()


def _batch_for_record(record: dict[str, Any]) -> str:
    explicit = record.get("batch")
    if explicit in BATCHES:
        return explicit
    root = _normal_root(record)
    # Test the nested marketing repository before its parent root.  Equality,
    # rather than a broad substring, avoids accidental scope expansion.
    endings = (
        ("marketingskills", "marketing"),
        ("inactive-content-marketing", "marketing"),
        ("opencode-core-dcp-fix", "opencode-clones"),
        ("opencode-upstream", "opencode-clones"),
        ("02-kx-to-process", "operations"),
        ("command-center", "operations"),
        ("chief-of-staff", "operations"),
        ("opencodex", "opencodex"),
        ("marketing", "marketing"),
    )
    for ending, batch in endings:
        if root.endswith("\\" + ending) or root == ending:
            return batch
    raise ToolchainError(f"local target has no approved batch: {record['path']}")


def partition_records(inventory: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return a strict partition; one target may never belong to two batches."""
    groups = {batch: [] for batch in BATCHES}
    identities: set[str] = set()
    for record in _local_records(inventory):
        identity = _key(record["path"])
        if identity in identities:
            raise ToolchainError(f"duplicate local inventory target: {record['path']}")
        identities.add(identity)
        groups[_batch_for_record(record)].append(record)
    union = [record for records in groups.values() for record in records]
    if len(union) != len(identities):
        raise ToolchainError("local batch partition is not disjoint")
    return groups


def _infer_client(record: dict[str, Any]) -> str:
    client = record.get("client")
    if client in {"codex", "opencode"}:
        return client
    path = str(record["path"]).replace("/", "\\").casefold()
    if "\\opencodex\\" in path or path.endswith("\\opencodex\\agents.md"):
        return "codex"
    return "opencode"


def _packet_filename(record: dict[str, Any]) -> str:
    relative = record.get("relative_path") or Path(record["path"]).name
    root = Path(str(record.get("root") or "root").replace("\\", "/")).name or "root"
    combined = f"{root}__{relative}"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "__", str(combined).replace("/", "__").replace("\\", "__")).strip("._")
    if not safe:
        safe = "agents"
    return f"{safe}-{str(record.get('sha256', 'unknown'))[:12]}.json"


def _assert_frozen_identity(record: dict[str, Any]) -> None:
    identity = file_record(record["path"])
    for field in ("sha256", "bytes"):
        expected = record.get(field)
        if expected is not None and identity[field] != expected:
            raise ToolchainError(f"frozen inventory identity changed before audit: {record['path']}")


def _existing_packet_identities(local_root: Path) -> dict[str, Path]:
    existing: dict[str, Path] = {}
    if not local_root.exists():
        return existing
    for path in local_root.rglob("*.json"):
        if not path.is_file():
            continue
        payload = read_json(path)
        if not isinstance(payload, dict):
            continue
        identity = payload.get("file_identity")
        if isinstance(identity, dict) and isinstance(identity.get("path"), str):
            existing[_key(identity["path"])] = path
    return existing


def _reuse_packet(base: dict[str, Any], record: dict[str, Any], mirror_identity: str) -> dict[str, Any]:
    """Preserve per-file identity while proving the content analysis was reused."""
    target_identity = file_record(record["path"])
    packet = copy.deepcopy(base)
    packet["file_identity"] = target_identity
    packet["mirror_identity"] = mirror_identity
    for entry in packet["rubric"]:
        evidence = entry.get("evidence")
        if isinstance(evidence, dict):
            evidence["target"] = target_identity
    audit = packet.get("audit")
    if isinstance(audit, dict):
        audit["analysis_reused_from"] = base["file_identity"]["path"]
    return packet


def build_batch_packets(
    *, inventory_path: str | Path,
    batch: str,
    dedupe_identical: bool = False,
) -> tuple[Path, list[tuple[dict[str, Any], dict[str, Any]]], int]:
    if batch not in BATCHES:
        raise ToolchainError(f"unknown batch: {batch}")
    inventory_file = assert_no_reparse(inventory_path, label="inventory")
    inventory = _inventory(inventory_file)
    groups = partition_records(inventory)
    selected = groups[batch]
    if not selected:
        raise ToolchainError(f"batch {batch} has no targets")
    track = inventory_file.parent
    output_root = track / "review-packets" / "local" / batch
    assert_within(output_root, track, label="packet output")
    all_packet_root = track / "review-packets" / "local"
    existing = _existing_packet_identities(all_packet_root)
    selected_keys = {_key(record["path"]) for record in selected}
    for identity, existing_path in existing.items():
        if identity in selected_keys and output_root not in existing_path.parents:
            raise ToolchainError(f"disjoint batch collision for {identity}: {existing_path}")

    packet_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    analyzed: dict[str, dict[str, Any]] = {}
    mirror_pairs = 0
    mirror_sizes: dict[str, int] = {}
    for record in selected:
        _assert_frozen_identity(record)
        mirror = record.get("mirror_group")
        if mirror is not None and (not isinstance(mirror, str) or not mirror):
            raise ToolchainError(f"invalid mirror identity for {record['path']}")
        if isinstance(mirror, str):
            mirror_sizes[mirror] = mirror_sizes.get(mirror, 0) + 1
        reusable = dedupe_identical and isinstance(mirror, str) and mirror in analyzed
        if reusable:
            base = analyzed[mirror]
            if base["file_identity"]["sha256"] != record.get("sha256"):
                raise ToolchainError(f"mirror identity diverged; cannot dedupe: {mirror}")
            packet = _reuse_packet(base, record, mirror)
        else:
            packet = build_packet(
                target=record["path"],
                client=_infer_client(record),
                mirror_identity=mirror if isinstance(mirror, str) else None,
            )
            if dedupe_identical and isinstance(mirror, str):
                analyzed[mirror] = packet
        packet_pairs.append((record, packet))
    if batch == "opencode-clones" and dedupe_identical:
        if len(mirror_sizes) != 15 or any(size != 2 for size in mirror_sizes.values()):
            raise ToolchainError("deduplicated clone batch requires 15 exact mirror pairs")
        mirror_pairs = 15
    return output_root, packet_pairs, mirror_pairs


def write_batch_packets(
    *, inventory_path: str | Path,
    batch: str,
    dedupe_identical: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    output_root, packet_pairs, mirror_pairs = build_batch_packets(
        inventory_path=inventory_path, batch=batch, dedupe_identical=dedupe_identical
    )
    outputs: list[str] = []
    if not dry_run:
        for record, packet in packet_pairs:
            output = output_root / _packet_filename(record)
            outputs.append(str(write_packet(packet, output)))
    return {
        "status": "PASS",
        "batch": batch,
        "files": len(packet_pairs),
        "mirror_pairs": mirror_pairs,
        "packets": outputs,
        "dry_run": dry_run,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit one disjoint local AGENTS.md batch from the frozen inventory.")
    parser.add_argument("--batch", required=True, choices=BATCHES, help="approved disjoint review batch")
    parser.add_argument("--inventory", required=True, help="frozen scope inventory JSON")
    parser.add_argument("--dedupe-identical", action="store_true", help="reuse analysis only for exact mirror hashes while preserving every identity")
    parser.add_argument("--dry-run", action="store_true", help="validate and build packets in memory without writing them")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(json_line(write_batch_packets(
            inventory_path=args.inventory,
            batch=args.batch,
            dedupe_identical=args.dedupe_identical,
            dry_run=args.dry_run,
        )))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json_line({"status": "FAIL", "batch": args.batch, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
