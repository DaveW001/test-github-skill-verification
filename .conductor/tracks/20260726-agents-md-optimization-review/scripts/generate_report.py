#!/usr/bin/env python3
"""Generate the reconciled, global-first AGENTS portfolio report."""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from bootstrap_review_toolchain import (
    ToolchainError,
    canonical,
    fail,
    json_line,
    read_json,
    validate_packet,
    write_json,
    write_text,
)


EXPECTED_GLOBAL = 2
EXPECTED_LOCAL = 41
EXPECTED_TOTAL = 43
EXPECTED_ROOTS = 9
SEVERITY_ORDER = {"Critical": 0, "Major": 1, "Minor": 2, "None": 3}


def _path_key(value: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(value)))


def _load_inventory(track: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    path = track / "scope-inventory.json"
    if not path.is_file():
        fail(f"missing inventory: {path}")
    payload = read_json(path)
    targets = payload.get("targets") if isinstance(payload, dict) else None
    if not isinstance(targets, list):
        fail("scope inventory targets must be an array")
    by_path: dict[str, dict[str, Any]] = {}
    for index, target in enumerate(targets):
        if not isinstance(target, dict) or not target.get("path"):
            fail(f"inventory target {index} is malformed")
        key = _path_key(target["path"])
        if key in by_path:
            fail(f"duplicate inventory identity: {target['path']}")
        if target.get("scope") not in {"global", "local"}:
            fail(f"inventory identity has invalid scope: {target['path']}")
        if not isinstance(target.get("sha256"), str) or len(target["sha256"]) != 64:
            fail(f"inventory identity has invalid sha256: {target['path']}")
        if not isinstance(target.get("bytes"), int) or target["bytes"] < 0:
            fail(f"inventory identity has invalid byte count: {target['path']}")
        by_path[key] = target
    global_count = sum(item["scope"] == "global" for item in by_path.values())
    local_count = sum(item["scope"] == "local" for item in by_path.values())
    roots = {
        _path_key(item.get("root") or Path(item["path"]).parent)
        for item in by_path.values()
        if item["scope"] == "local"
    }
    counts = payload.get("counts", {})
    expected = {
        "global": EXPECTED_GLOBAL,
        "local": EXPECTED_LOCAL,
        "roots": EXPECTED_ROOTS,
    }
    actual = {"global": global_count, "local": local_count, "roots": len(roots)}
    if actual != expected:
        fail(f"inventory reconciliation mismatch: expected {expected}, got {actual}")
    if len(by_path) != EXPECTED_TOTAL:
        fail(f"inventory must contain exactly {EXPECTED_TOTAL} unique targets")
    if isinstance(counts, dict):
        for name, value in expected.items():
            if counts.get(name) != value:
                fail(
                    f"inventory declared {name}={counts.get(name)!r}; "
                    f"reconciled value is {value}"
                )
    return payload, by_path


def _load_packets(
    track: Path, inventory: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    root = track / "review-packets"
    if not root.is_dir():
        fail(f"missing review packet root: {root}")
    packets: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        payload = read_json(path)
        if not isinstance(payload, dict) or "file_identity" not in payload:
            continue
        errors = validate_packet(payload)
        if errors:
            fail(f"invalid packet {path}: {'; '.join(errors)}")
        identity = payload["file_identity"]
        key = _path_key(identity["path"])
        if key in packets:
            fail(f"duplicate packet identity: {identity['path']}")
        if key not in inventory:
            fail(f"packet identity is outside inventory: {identity['path']}")
        baseline = inventory[key]
        if identity.get("sha256") != baseline["sha256"]:
            fail(f"packet/inventory hash mismatch: {identity['path']}")
        if identity.get("bytes") != baseline["bytes"]:
            fail(f"packet/inventory byte mismatch: {identity['path']}")
        packet_scope = "global" if "global" in path.parts else "local"
        if packet_scope != baseline["scope"]:
            fail(f"packet directory/scope mismatch: {identity['path']}")
        payload["_source"] = str(path)
        packets[key] = payload
    missing = sorted(set(inventory) - set(packets))
    extra = sorted(set(packets) - set(inventory))
    if missing or extra:
        fail(
            "report identity reconciliation mismatch: "
            f"missing_packets={missing}, extra_packets={extra}"
        )
    return packets


def _entry_path(entry: dict[str, Any]) -> str | None:
    for name in ("source", "target", "path", "file"):
        value = entry.get(name)
        if isinstance(value, str) and value:
            return value
    identity = entry.get("file_identity")
    if isinstance(identity, dict) and isinstance(identity.get("path"), str):
        return identity["path"]
    return None


def _manifest_entries(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        fail("change manifest must be an object")
    for name in ("changes", "entries", "files"):
        value = payload.get(name)
        if isinstance(value, list):
            if not all(isinstance(entry, dict) for entry in value):
                fail(f"change manifest {name} must contain objects")
            return list(value)
    # An explicitly empty manifest may use only a count.
    if payload.get("changed") in (0, False) or payload.get("change_count") == 0:
        return []
    fail("change manifest must contain changes, entries, or files")
    return []


def _byte_value(entry: dict[str, Any], prefix: str) -> int | None:
    for key in (f"{prefix}_bytes", f"{prefix}Bytes"):
        value = entry.get(key)
        if isinstance(value, int):
            return value
    nested = entry.get(prefix)
    if isinstance(nested, dict) and isinstance(nested.get("bytes"), int):
        return nested["bytes"]
    return None


def _load_changes(
    track: Path, inventory: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], int, int]:
    combined: list[dict[str, Any]] = []
    by_target: dict[str, dict[str, Any]] = {}
    for scope in ("global", "local"):
        path = track / f"change-manifest-{scope}.json"
        if not path.is_file():
            fail(f"missing {scope} change manifest: {path}")
        for entry in _manifest_entries(read_json(path)):
            target_path = _entry_path(entry)
            if not target_path:
                fail(f"{path} contains a change without a target identity")
            key = _path_key(target_path)
            if key not in inventory:
                fail(f"change target is outside inventory: {target_path}")
            if inventory[key]["scope"] != scope:
                fail(f"change manifest scope mismatch: {target_path}")
            if key in by_target:
                fail(f"duplicate change identity across manifests: {target_path}")
            before = _byte_value(entry, "before")
            after = _byte_value(entry, "after")
            if before is None or after is None or before < 0 or after < 0:
                fail(f"change entry lacks valid before/after byte counts: {target_path}")
            if before != inventory[key]["bytes"]:
                fail(
                    f"change/inventory before-byte mismatch for {target_path}: "
                    f"{before} != {inventory[key]['bytes']}"
                )
            normalized = dict(entry)
            normalized["path"] = inventory[key]["path"]
            normalized["scope"] = scope
            normalized["before_bytes"] = before
            normalized["after_bytes"] = after
            normalized["source_manifest"] = str(path)
            by_target[key] = normalized
            combined.append(normalized)
    before_total = sum(item["bytes"] for item in inventory.values())
    after_total = sum(
        by_target.get(key, {}).get("after_bytes", item["bytes"])
        for key, item in inventory.items()
    )
    return combined, before_total, after_total


def _load_validation(track: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    for scope in ("global", "local"):
        path = track / "evidence" / f"{scope}-validation.json"
        if not path.is_file():
            fail(f"missing {scope} loading evidence: {path}")
        payload = read_json(path)
        if not isinstance(payload, dict) or payload.get("scope") != scope:
            fail(f"malformed {scope} loading evidence: {path}")
        evidence[scope] = payload
    return evidence


def _finding_rows(
    inventory: dict[str, dict[str, Any]], packets: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, packet in packets.items():
        target = inventory[key]
        for item in packet["rubric"]:
            if (
                item["result"] == "Finding"
                or item["result"] == "Unverified"
                or item["disposition"] in {"optional", "defer", "blocked"}
            ):
                rows.append(
                    {
                        "path": target["path"],
                        "scope": target["scope"],
                        "root": target.get("root"),
                        "rubric_id": item["id"],
                        "result": item["result"],
                        "severity": item["severity"],
                        "confidence": item["confidence"],
                        "finding_id": item["finding_id"],
                        "disposition": item["disposition"],
                        "evidence": item["evidence"],
                        "source_packet": packet["_source"],
                    }
                )
    return sorted(
        rows,
        key=lambda row: (
            0 if row["scope"] == "global" else 1,
            SEVERITY_ORDER.get(row["severity"], 99),
            str(row["root"] or ""),
            row["path"].lower(),
            row["rubric_id"],
        ),
    )


def _render_findings(rows: Iterable[dict[str, Any]]) -> list[str]:
    rendered: list[str] = []
    for row in rows:
        finding = row["finding_id"] or "(no finding ID)"
        rendered.append(
            f"- `{row['severity']}` `{row['rubric_id']}` `{row['result']}` "
            f"`{row['disposition']}` — `{row['path']}` — {finding} "
            f"(confidence {row['confidence']:.2f})"
        )
    return rendered or ["- None."]


def generate_report(track: str | Path) -> dict[str, Any]:
    root = canonical(track)
    inventory_payload, inventory = _load_inventory(root)
    packets = _load_packets(root, inventory)
    changes, before_total, after_total = _load_changes(root, inventory)
    validation = _load_validation(root)
    findings = _finding_rows(inventory, packets)

    global_rows = [row for row in findings if row["scope"] == "global"]
    local_by_root: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in findings:
        if row["scope"] == "local":
            local_by_root[str(row["root"] or Path(row["path"]).parent)].append(row)
    all_local_roots = sorted(
        {
            str(item.get("root") or Path(item["path"]).parent)
            for item in inventory.values()
            if item["scope"] == "local"
        },
        key=str.lower,
    )
    unresolved = [
        row
        for row in findings
        if row["result"] == "Unverified"
        or row["disposition"] in {"optional", "defer", "blocked"}
    ]
    authority = [
        {
            "path": change["path"],
            "authority_delta": change.get("authority_delta", "not-recorded"),
            "rationale": change.get("rationale", ""),
        }
        for change in changes
    ]
    recovery = [
        {
            "path": change["path"],
            "backup": change.get("backup"),
            "restore": change.get("restore"),
        }
        for change in changes
    ]

    aggregate_manifest = {
        "version": 1,
        "reconciled_to": str(root / "scope-inventory.json"),
        "counts": {
            "global": EXPECTED_GLOBAL,
            "local": EXPECTED_LOCAL,
            "total": EXPECTED_TOTAL,
            "changed": len(changes),
        },
        "bytes": {
            "before": before_total,
            "after": after_total,
            "delta": after_total - before_total,
        },
        "changes": changes,
        "authority_decisions": authority,
        "recovery_paths": recovery,
    }
    unresolved_payload = {
        "version": 1,
        "count": len(unresolved),
        "decisions": unresolved,
    }

    cutoff = inventory_payload.get("cutoff", "2026-03-28T00:00:00-04:00")
    report: list[str] = [
        "# AGENTS.md Portfolio Review",
        "",
        "## Executive Reconciliation",
        "",
        f"- Scope: {EXPECTED_GLOBAL} global + {EXPECTED_LOCAL} local = {EXPECTED_TOTAL} files across {EXPECTED_ROOTS} local roots.",
        f"- Cutoff: `{cutoff}`.",
        f"- Bytes: {before_total} before; {after_total} after; delta {after_total - before_total}.",
        f"- Applied change records: {len(changes)}.",
        f"- Unresolved/Optional/Unverified decisions: {len(unresolved)}.",
        "",
        "## Methodology",
        "",
        "- Frozen 24-item rubric reconciled one-for-one against every inventory identity.",
        "- Packet path, SHA-256, and byte identity were matched to the frozen inventory.",
        "- Global files were ordered and reported before every local-root result.",
        "- Runtime limitations remain Unverified; no favorable count was substituted for conflicting evidence.",
        "",
        "## Global Findings",
        "",
        *_render_findings(global_rows),
        "",
        "## Local Findings by Root",
        "",
    ]
    for local_root in all_local_roots:
        report.extend(
            [
                f"### {local_root}",
                "",
                *_render_findings(local_by_root.get(local_root, [])),
                "",
            ]
        )
    report.extend(
        [
            "## Changes and Authority Decisions",
            "",
        ]
    )
    if changes:
        for change in changes:
            report.append(
                f"- `{change['path']}`: {change['before_bytes']} -> "
                f"{change['after_bytes']} bytes; authority delta "
                f"`{change.get('authority_delta', 'not-recorded')}`; "
                f"backup `{change.get('backup', 'not-recorded')}`."
            )
    else:
        report.append("- No applied changes were recorded.")
    mirror_groups = inventory_payload.get("mirror_groups", [])
    report.extend(
        [
            "",
            "## Mirror Handling",
            "",
            f"- Reconciled mirror groups: {len(mirror_groups) if isinstance(mirror_groups, list) else 0}.",
            "- Review deduplication never replaced per-file identity, applicability, or validation.",
            "",
            "## Optional Gaps and Unverified Probes",
            "",
            *_render_findings(unresolved),
            "",
            "## Loading Evidence",
            "",
            f"- Global validation: `{validation['global'].get('status', 'Unverified')}`.",
            f"- Local validation: `{validation['local'].get('status', 'Unverified')}`.",
            "",
            "## Recovery Paths",
            "",
        ]
    )
    if recovery:
        for item in recovery:
            report.append(
                f"- `{item['path']}` -> `{item.get('backup') or 'not-recorded'}`."
            )
    else:
        report.append("- No changed target required a recovery path.")
    report.extend(
        [
            "",
            "## Source Reconciliation",
            "",
            f"- Inventory identities: {len(inventory)}.",
            f"- Review packet identities: {len(packets)}.",
            f"- Rubric identities: {sum(len(packet['rubric']) for packet in packets.values())}.",
            "- Identity mismatch count: 0.",
            "",
        ]
    )

    write_text(root / "portfolio-review-report.md", "\n".join(report), root=root)
    write_json(root / "change-manifest.json", aggregate_manifest, root=root)
    write_json(root / "unresolved-decisions.json", unresolved_payload, root=root)
    return {
        "check": "portfolio-report",
        "status": "PASS",
        "global": EXPECTED_GLOBAL,
        "local": EXPECTED_LOCAL,
        "total": EXPECTED_TOTAL,
        "roots": EXPECTED_ROOTS,
        "before_bytes": before_total,
        "after_bytes": after_total,
        "unresolved": len(unresolved),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the reconciled global-first AGENTS portfolio report."
    )
    parser.add_argument("--track", required=True)
    args = parser.parse_args(argv)
    try:
        result = generate_report(args.track)
        print(json_line(result))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json_line(
                {"check": "portfolio-report", "status": "FAIL", "error": str(exc)}
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
