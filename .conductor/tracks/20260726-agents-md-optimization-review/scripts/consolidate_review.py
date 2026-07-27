#!/usr/bin/env python3
"""Reconcile the 41 local review packets before any local edit is considered."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    RUBRIC_IDS,
    ToolchainError,
    assert_no_reparse,
    assert_within,
    canonical,
    client_semantics,
    json_line,
    read_json,
    validate_packet,
    write_json,
    write_text,
)


def _key(path: str | Path) -> str:
    return os.path.normcase(str(canonical(path)))


def _read_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ToolchainError(f"missing {label}: {path}")
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ToolchainError(f"{label} must be a JSON object")
    return payload


def _local_records(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    targets = inventory.get("targets")
    if not isinstance(targets, list):
        raise ToolchainError("scope inventory must have a targets list")
    records: list[dict[str, Any]] = []
    for record in targets:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ToolchainError("scope inventory target is malformed")
        if record.get("scope") == "local":
            records.append(record)
    if len(records) != 41:
        raise ToolchainError(f"local consolidation requires exactly 41 inventory records, got {len(records)}")
    if len({_key(record["path"]) for record in records}) != 41:
        raise ToolchainError("local inventory identities are not unique")
    return records


def _packet_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise ToolchainError(f"missing local packet root: {root}")
    files = [path for path in root.rglob("*.json") if path.is_file()]
    if not files:
        raise ToolchainError("local packet root has no packets")
    return sorted(files, key=lambda item: str(item).casefold())


def _packet_identity(packet: dict[str, Any], source: Path) -> tuple[str, str, int]:
    identity = packet.get("file_identity")
    if not isinstance(identity, dict):
        raise ToolchainError(f"packet lacks file_identity: {source}")
    path, digest, size = identity.get("path"), identity.get("sha256"), identity.get("bytes")
    if not isinstance(path, str) or not isinstance(digest, str) or not isinstance(size, int):
        raise ToolchainError(f"packet file_identity is malformed: {source}")
    return _key(path), digest, size


def _load_packets(track: Path, records: list[dict[str, Any]]) -> list[tuple[Path, dict[str, Any], dict[str, Any]]]:
    expected = {_key(record["path"]): record for record in records}
    seen: dict[str, Path] = {}
    loaded: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    for source in _packet_files(track / "review-packets" / "local"):
        packet = _read_object(source, f"packet {source.name}")
        errors = validate_packet(packet)
        if errors:
            raise ToolchainError(f"invalid packet {source}: {'; '.join(errors)}")
        identity, digest, size = _packet_identity(packet, source)
        if identity not in expected:
            raise ToolchainError(f"packet is outside frozen local scope: {source}")
        if identity in seen:
            raise ToolchainError(f"duplicate packet identity for {identity}: {seen[identity]} and {source}")
        record = expected[identity]
        if record.get("sha256") != digest or record.get("bytes") != size:
            raise ToolchainError(f"packet identity disagrees with frozen inventory: {source}")
        client = record.get("client")
        if client in {"codex", "opencode"} and packet.get("client") != client:
            raise ToolchainError(f"packet client does not match frozen inventory: {source}")
        if packet.get("client_semantics") != client_semantics(packet["client"]):
            raise ToolchainError(f"packet client semantics are not canonical: {source}")
        mirror = record.get("mirror_group")
        if mirror:
            if packet.get("mirror_identity") != mirror:
                raise ToolchainError(f"mirror identity was not preserved: {source}")
        elif packet.get("mirror_identity") not in {None, ""}:
            raise ToolchainError(f"packet has unexpected mirror identity: {source}")
        seen[identity] = source
        loaded.append((source, packet, record))
    if set(seen) != set(expected):
        missing = sorted(set(expected) - set(seen))
        raise ToolchainError(f"packet reconciliation is incomplete; missing {missing}")
    if len(loaded) != 41:
        raise ToolchainError("packet reconciliation must have exactly 41 packet files")
    return loaded


def _extract_edits(entry: dict[str, Any]) -> list[dict[str, str]] | None:
    candidate: Any = entry.get("edits")
    if candidate is None:
        candidate = entry.get("edit", entry.get("proposed_edit"))
    if candidate is None and "anchor" in entry and "replacement" in entry:
        candidate = {"anchor": entry["anchor"], "replacement": entry["replacement"]}
    if isinstance(candidate, dict):
        candidate = [candidate]
    if not isinstance(candidate, list) or not candidate:
        return None
    edits: list[dict[str, str]] = []
    for edit in candidate:
        if not isinstance(edit, dict):
            raise ToolchainError("proposed edit must be an object")
        anchor = edit.get("anchor", edit.get("old"))
        replacement = edit.get("replacement", edit.get("new"))
        if not isinstance(anchor, str) or not anchor or not isinstance(replacement, str):
            raise ToolchainError("proposed edit requires a nonempty literal anchor and replacement")
        edits.append({"anchor": anchor, "replacement": replacement})
    if len({edit["anchor"] for edit in edits}) != len(edits):
        raise ToolchainError("proposed edit anchors must be unique within a target")
    return edits


def _build_queue(loaded: list[tuple[Path, dict[str, Any], dict[str, Any]]], track: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    allowlist: list[str] = []
    for source, packet, record in loaded:
        identity = packet["file_identity"]
        target = identity["path"]
        allowlist.append(target)
        for item in packet["rubric"]:
            if item["result"] != "Finding" or item["disposition"] != "apply":
                continue
            edits = _extract_edits(item)
            if edits is None:
                unresolved.append({
                    "target": target,
                    "finding_id": item["finding_id"],
                    "rubric_id": item["id"],
                    "reason": "apply disposition lacks literal anchored edit; retained for human resolution",
                    "packet": str(source),
                })
                continue
            authority_delta = item.get("authority_delta", False)
            if authority_delta not in {False, None, "", "none", "None"}:
                raise ToolchainError(f"apply candidate expands authority: {source} {item['id']}")
            entries.append({
                "target": target,
                "pre_edit_sha256": identity["sha256"],
                "pre_edit_bytes": identity["bytes"],
                "dirty": record.get("dirty"),
                "finding_id": item["finding_id"],
                "rubric_id": item["id"],
                "rationale": item.get("rationale", "review packet high-confidence finding"),
                "authority_delta": False,
                "edits": edits,
                "packet": str(source),
            })
    if len({_key(path) for path in allowlist}) != len(allowlist):
        raise ToolchainError("queue allowlist would contain duplicate target identities")
    return {
        "version": 1,
        "scope": "local",
        "allowlist": sorted(allowlist, key=str.casefold),
        "backup_manifest": str(track / "backup-manifest.json"),
        "entries": entries,
        "unresolved_apply_findings": unresolved,
        "authority_expansion": False,
    }


def _precedence_map(loaded: list[tuple[Path, dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    identities = {canonical(record["path"]): record for _, _, record in loaded}
    chains: list[dict[str, Any]] = []
    for _, _, record in loaded:
        target = canonical(record["path"])
        ancestors: list[str] = []
        cursor = target.parent
        while True:
            parent_agents = cursor / "AGENTS.md"
            if parent_agents in identities and parent_agents != target:
                ancestors.append(str(parent_agents))
            if cursor.parent == cursor:
                break
            cursor = cursor.parent
        chains.append({"target": str(target), "parents": list(reversed(ancestors)), "mirror_identity": record.get("mirror_group")})
    return {"version": 1, "chains": sorted(chains, key=lambda item: item["target"].casefold())}


def _matrix(loaded: list[tuple[Path, dict[str, Any], dict[str, Any]]]) -> str:
    lines = [
        "# AGENTS.md Review Matrix",
        "",
        "| File | Rubric ID | Result | Severity | Confidence | Finding | Disposition |",
        "|---|---|---|---|---:|---|---|",
    ]
    for _, packet, _ in sorted(loaded, key=lambda item: item[1]["file_identity"]["path"].casefold()):
        path = packet["file_identity"]["path"].replace("|", "\\|")
        for item in packet["rubric"]:
            finding = item["finding_id"].replace("|", "\\|")
            lines.append(
                f"| {path} | {item['id']} | {item['result']} | {item['severity']} | {item['confidence']:.2f} | "
                f"{finding} | {item['disposition']} |"
            )
    lines.append("")
    return "\n".join(lines)


def consolidate(track: str | Path, *, dry_run: bool = False) -> dict[str, Any]:
    root = assert_no_reparse(track, label="track")
    inventory = _read_object(root / "scope-inventory.json", "scope inventory")
    records = _local_records(inventory)
    loaded = _load_packets(root, records)
    rubric_identities = sum(len(packet["rubric"]) for _, packet, _ in loaded)
    if rubric_identities != 984:
        raise ToolchainError(f"expected exactly 984 rubric item identities, got {rubric_identities}")
    queue = _build_queue(loaded, root)
    precedence = _precedence_map(loaded)
    matrix = _matrix(loaded)
    outputs = {
        "queue": root / "local-fix-queue.json",
        "precedence": root / "precedence-map.json",
        "matrix": root / "agents-review-matrix.md",
    }
    for output in outputs.values():
        assert_within(output, root, label="consolidation output")
    if not dry_run:
        write_json(outputs["queue"], queue, root=root)
        write_json(outputs["precedence"], precedence, root=root)
        write_text(outputs["matrix"], matrix, root=root)
    return {
        "status": "PASS",
        "files": len(loaded),
        "rubric_identities": rubric_identities,
        "apply_candidates": len(queue["entries"]),
        "unresolved_apply_findings": len(queue["unresolved_apply_findings"]),
        "dry_run": dry_run,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exactly reconcile all local AGENTS.md review packets before edits.")
    parser.add_argument("--track", required=True, help="track-local evidence root")
    parser.add_argument("--dry-run", action="store_true", help="verify reconciliation without writing queue/map/matrix outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(json_line(consolidate(args.track, dry_run=args.dry_run)))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json_line({"status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
