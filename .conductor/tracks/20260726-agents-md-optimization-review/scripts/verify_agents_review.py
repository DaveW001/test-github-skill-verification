#!/usr/bin/env python3
"""Fail-closed verification checks for the AGENTS.md review track.

The verifier intentionally reads only track evidence.  It never repairs a
missing artifact: an incomplete or inconsistent record is a failed check, not
an invitation to manufacture a green result.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

from bootstrap_review_toolchain import (
    CHECK_NAMES,
    RUBRIC_IDS,
    ToolchainError,
    assert_no_reparse,
    canonical,
    client_semantics,
    fail,
    json_line,
    load_rubric,
    read_json,
    sha256_file,
    validate_packet,
)


class VerificationError(ToolchainError):
    """A verifier-specific error.  All failures must remain fail closed."""


def _error(message: str) -> None:
    raise VerificationError(message)


def _key(path: str | Path) -> str:
    return os.path.normcase(str(canonical(path)))


def _track_path(track: str | Path, *parts: str) -> Path:
    root = assert_no_reparse(track, label="track")
    candidate = root.joinpath(*parts)
    assert_no_reparse(candidate, label="track artifact")
    return candidate


def _require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        _error(f"missing {label}: {path}")
    return path


def _read_object(path: Path, label: str) -> dict[str, Any]:
    _require_file(path, label)
    try:
        payload = read_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _error(f"invalid {label}: {exc}")
    if not isinstance(payload, dict):
        _error(f"{label} must be a JSON object")
    return payload


def _records(inventory: dict[str, Any], scope: str | None = None) -> list[dict[str, Any]]:
    """Accept the frozen inventory shape and a narrow legacy shape for tests."""
    raw = inventory.get("targets")
    if raw is None:
        raw = []
        for name, inferred_scope in (("global", "global"), ("local", "local")):
            values = inventory.get(name, [])
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str):
                        raw.append({"path": value, "scope": inferred_scope})
                    elif isinstance(value, dict):
                        copied = dict(value)
                        copied.setdefault("scope", inferred_scope)
                        raw.append(copied)
    if not isinstance(raw, list):
        _error("scope inventory targets must be a list")
    records: list[dict[str, Any]] = []
    for index, value in enumerate(raw):
        if not isinstance(value, dict) or not isinstance(value.get("path"), str):
            _error(f"inventory target {index} must contain a path")
        item_scope = value.get("scope")
        if item_scope not in {"global", "local"}:
            _error(f"inventory target {value['path']} has invalid scope")
        if scope is None or item_scope == scope:
            records.append(value)
    return records


def _inventory(track: str | Path) -> dict[str, Any]:
    return _read_object(_track_path(track, "scope-inventory.json"), "scope inventory")


def _expected_counts(inventory: dict[str, Any]) -> dict[str, int]:
    expected = {"global": 2, "local": 41, "roots": 9}
    supplied = inventory.get("expected_counts")
    if isinstance(supplied, dict):
        for key in expected:
            if isinstance(supplied.get(key), int):
                expected[key] = supplied[key]
    return expected


def _inventory_summary(track: str | Path) -> tuple[dict[str, Any], dict[str, int]]:
    inventory = _inventory(track)
    targets = _records(inventory)
    duplicate_paths = _duplicates(_key(record["path"]) for record in targets)
    if duplicate_paths:
        _error("scope inventory contains duplicate target paths")
    global_count = len(_records(inventory, "global"))
    local_count = len(_records(inventory, "local"))
    roots = inventory.get("roots")
    if not isinstance(roots, list):
        _error("scope inventory roots must be a list")
    qualified_roots = [root for root in roots if isinstance(root, dict) and root.get("qualifies") is not False]
    counts = {"global": global_count, "local": local_count, "roots": len(qualified_roots)}
    declared = inventory.get("counts")
    if isinstance(declared, dict):
        for key, value in counts.items():
            if declared.get(key) != value:
                _error(f"scope inventory declared {key} count does not match its targets")
    expected = _expected_counts(inventory)
    if counts != expected:
        _error(f"scope counts must equal frozen values {expected}, got {counts}")
    return inventory, counts


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicate: set[str] = set()
    for value in values:
        if value in seen:
            duplicate.add(value)
        seen.add(value)
    return duplicate


def _packet_paths(root: Path) -> list[Path]:
    if not root.exists():
        _error(f"missing packet root: {root}")
    if not root.is_dir():
        _error(f"packet root is not a directory: {root}")
    paths: list[Path] = []
    for path in root.rglob("*.json"):
        assert_no_reparse(path, label="packet")
        if path.is_file():
            paths.append(path)
    return sorted(paths, key=lambda item: str(item).casefold())


def _load_packet(path: Path) -> dict[str, Any]:
    packet = _read_object(path, f"packet {path.name}")
    errors = validate_packet(packet)
    if errors:
        _error(f"invalid packet {path}: {'; '.join(errors)}")
    return packet


def _packet_identity(packet: dict[str, Any], source: Path) -> tuple[str, str, int]:
    identity = packet.get("file_identity")
    if not isinstance(identity, dict):
        _error(f"packet {source} has no file identity")
    path = identity.get("path")
    digest = identity.get("sha256")
    size = identity.get("bytes")
    if not isinstance(path, str) or not isinstance(digest, str) or not isinstance(size, int):
        _error(f"packet {source} has malformed file identity")
    return _key(path), digest, size


def _verify_packet_against_record(packet: dict[str, Any], source: Path, record: dict[str, Any]) -> None:
    path_key, digest, size = _packet_identity(packet, source)
    if path_key != _key(record["path"]):
        _error(f"packet identity path mismatch: {source}")
    expected_digest = record.get("sha256")
    if isinstance(expected_digest, str) and expected_digest != digest:
        _error(f"packet identity hash mismatch: {source}")
    expected_size = record.get("bytes")
    if isinstance(expected_size, int) and expected_size != size:
        _error(f"packet identity byte count mismatch: {source}")
    client = record.get("client")
    if isinstance(client, str) and packet.get("client") != client:
        _error(f"packet client mismatch: {source}")
    if packet.get("client_semantics") != client_semantics(packet["client"]):
        _error(f"packet client semantics are not canonical: {source}")
    mirror = record.get("mirror_group")
    if mirror:
        if packet.get("mirror_identity") != mirror:
            _error(f"packet did not preserve mirror identity for {source}")
    elif packet.get("mirror_identity") not in {None, ""}:
        _error(f"packet has an unexpected mirror identity: {source}")


def _record_client(record: dict[str, Any]) -> str | None:
    """Inventory records need not repeat the client when their global path says it."""
    client = record.get("client")
    if client in {"codex", "opencode"}:
        return client
    path = str(record.get("path", "")).replace("/", "\\").casefold()
    if "\\.codex\\agents.md" in path:
        return "codex"
    if "\\.config\\opencode\\agents.md" in path:
        return "opencode"
    return None


def _check_scope(args: argparse.Namespace) -> dict[str, Any]:
    _, counts = _inventory_summary(args.track)
    return {"status": "PASS", **counts}


def _check_rubric(args: argparse.Namespace) -> dict[str, Any]:
    rubric = load_rubric(args.track)
    schema = _read_object(_track_path(args.track, "schemas", "review-packet.schema.json"), "review-packet schema")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        _error("review-packet schema must declare Draft 2020-12")
    required = schema.get("required")
    if not isinstance(required, list) or not {"file_identity", "client", "client_semantics", "rubric"}.issubset(required):
        _error("review-packet schema is missing required packet fields")
    properties = schema.get("properties")
    if not isinstance(properties, dict) or not isinstance(properties.get("rubric"), dict):
        _error("review-packet schema has no rubric definition")
    rubric_schema = properties["rubric"]
    if rubric_schema.get("minItems") != 24 or rubric_schema.get("maxItems") != 24:
        _error("review-packet schema must require exactly 24 rubric entries")
    return {"status": "PASS", "rubric_ids": len(rubric["rubric_ids"]), "schema": "PASS"}


def _check_backups(args: argparse.Namespace) -> dict[str, Any]:
    inventory, counts = _inventory_summary(args.track)
    manifest = _read_object(_track_path(args.track, "backup-manifest.json"), "backup manifest")
    backup_root = manifest.get("backup_root")
    entries = manifest.get("entries")
    if not isinstance(backup_root, str) or not isinstance(entries, list):
        _error("backup manifest must contain backup_root and entries")
    expected = {_key(record["path"]): record for record in _records(inventory)}
    if len(entries) != len(expected):
        _error("backup manifest entry count does not match frozen inventory")
    seen: set[str] = set()
    verified = 0
    for entry in entries:
        if not isinstance(entry, dict):
            _error("backup manifest entry must be an object")
        source = entry.get("source")
        backup = entry.get("backup")
        digest = entry.get("sha256")
        size = entry.get("bytes")
        if not isinstance(source, str) or not isinstance(backup, str) or not isinstance(digest, str) or not isinstance(size, int):
            _error("backup manifest entry lacks source/backup/hash/bytes")
        source_key = _key(source)
        if source_key not in expected or source_key in seen:
            _error("backup manifest source mapping is unknown or duplicate")
        seen.add(source_key)
        backup_path = assert_no_reparse(backup, label="backup")
        try:
            from bootstrap_review_toolchain import assert_within
            assert_within(backup_path, backup_root, label="backup")
        except ToolchainError as exc:
            _error(str(exc))
        if not backup_path.is_file() or sha256_file(backup_path) != digest or backup_path.stat().st_size != size:
            _error(f"backup verification failed: {backup_path}")
        record = expected[source_key]
        if record.get("sha256") != digest or record.get("bytes") != size:
            _error(f"backup hash does not match frozen inventory: {source}")
        verified += 1
    if seen != set(expected):
        _error("backup manifest did not map every frozen target exactly once")
    if manifest.get("targets") != len(expected) or manifest.get("verified") != verified:
        _error("backup manifest totals are not exact")
    if manifest.get("restore_simulation") != "PASS":
        _error("backup manifest does not prove disposable restore")
    return {"status": "PASS", "targets": len(expected), "verified": verified, "restore_simulation": "PASS", "global": counts["global"], "local": counts["local"]}


def _check_global_review(args: argparse.Namespace) -> dict[str, Any]:
    target = args.target
    if target not in {"codex", "opencode"}:
        _error("global-review requires --target codex or --target opencode")
    inventory, _ = _inventory_summary(args.track)
    records = [record for record in _records(inventory, "global") if _record_client(record) == target]
    if len(records) != 1:
        _error(f"scope inventory must have exactly one global {target} target")
    packet_path = _track_path(args.track, "review-packets", "global", f"{target}.json")
    packet = _load_packet(packet_path)
    if packet.get("client") != target:
        _error(f"global packet has the wrong client: {packet_path}")
    _verify_packet_against_record(packet, packet_path, records[0])
    return {"status": "PASS", "target": target, "rubric_complete": True}


def _authority_expansion(value: Any) -> bool:
    if value in {False, None, "", "none", "None", "no", "false", "False"}:
        return False
    return True


def _loading_evidence(track: str | Path, name: str) -> None:
    evidence = _read_object(_track_path(track, "evidence", name), f"{name} evidence")
    clients = evidence.get("clients", evidence.get("results"))
    if not isinstance(clients, dict) or not clients:
        _error(f"{name} has no per-client results")
    for client in ("codex", "opencode"):
        item = clients.get(client)
        if not isinstance(item, dict):
            _error(f"{name} is missing {client} evidence")
        status = item.get("status")
        if status == "Pass":
            continue
        if status == "Unverified" and isinstance(item.get("reason"), str) and item["reason"].strip():
            continue
        _error(f"{name} has failed or unjustified {client} evidence")


def _check_change_manifest(args: argparse.Namespace, scope: str, filename: str, loading_name: str) -> dict[str, Any]:
    manifest = _read_object(_track_path(args.track, filename), f"{scope} change manifest")
    if _authority_expansion(manifest.get("authority_expansion")):
        _error(f"{scope} manifest records authority expansion")
    changes = manifest.get("changes", manifest.get("entries", []))
    if not isinstance(changes, list):
        _error(f"{scope} manifest changes must be a list")
    for index, change in enumerate(changes):
        if not isinstance(change, dict):
            _error(f"{scope} manifest change {index} must be an object")
        if _authority_expansion(change.get("authority_delta")):
            _error(f"{scope} manifest change {index} expands authority")
        for field in ("target", "before_sha256", "after_sha256", "backup"):
            if not isinstance(change.get(field), str) or not change[field]:
                _error(f"{scope} manifest change {index} lacks {field}")
    if args.require_loading_evidence:
        _loading_evidence(args.track, loading_name)
    return {"status": "PASS", "authority_expansion": False, "changes": len(changes)}


def _batch_members(inventory: dict[str, Any], batch: str) -> list[dict[str, Any]]:
    local = _records(inventory, "local")
    explicit = [record for record in local if record.get("batch") == batch]
    if explicit:
        return explicit
    markers: dict[str, tuple[str, ...]] = {
        "operations": ("02-kx-to-process", "command-center", "chief-of-staff"),
        "marketing": ("marketing", "marketingskills", "inactive-content-marketing"),
        "opencode-clones": ("opencode-core-dcp-fix", "opencode-upstream"),
        "opencodex": ("opencodex",),
    }
    if batch not in markers:
        _error(f"unknown local review batch: {batch}")
    selected: list[dict[str, Any]] = []
    for record in local:
        root = str(record.get("root", "")).replace("/", "\\").casefold()
        if any(root.rstrip("\\").endswith(marker) for marker in markers[batch]):
            selected.append(record)
    return selected


def _local_packets(track: str | Path) -> list[tuple[Path, dict[str, Any]]]:
    root = _track_path(track, "review-packets", "local")
    return [(path, _load_packet(path)) for path in _packet_paths(root)]


def _check_local_review(args: argparse.Namespace) -> dict[str, Any]:
    batch = args.batch
    if not batch:
        _error("local-review requires --batch")
    inventory, _ = _inventory_summary(args.track)
    expected_records = _records(inventory, "local") if batch == "all" else _batch_members(inventory, batch)
    if not expected_records:
        _error(f"batch {batch} has no frozen inventory members")
    expected = {_key(record["path"]): record for record in expected_records}
    packets = _local_packets(args.track)
    matched: dict[str, tuple[Path, dict[str, Any]]] = {}
    for source, packet in packets:
        identity, _, _ = _packet_identity(packet, source)
        if identity not in expected:
            continue
        if identity in matched:
            _error(f"duplicate review packet identity: {identity}")
        _verify_packet_against_record(packet, source, expected[identity])
        matched[identity] = (source, packet)
    if set(matched) != set(expected):
        missing = sorted(set(expected) - set(matched))
        _error(f"batch {batch} lacks exact packet identities: {missing}")
    rubric_identities = len(matched) * len(RUBRIC_IDS)
    result: dict[str, Any] = {"status": "PASS", "files": len(matched), "rubric_identities": rubric_identities}
    if batch == "all":
        if len(matched) != 41 or rubric_identities != 984:
            _error("all local packets must reconcile exactly 41 files / 984 rubric identities")
    expected_count = {"operations": 3, "marketing": 6, "opencode-clones": 30, "opencodex": 2}.get(batch)
    if expected_count is not None and len(matched) != expected_count:
        _error(f"batch {batch} must contain exactly {expected_count} files")
    if batch == "opencode-clones":
        groups: dict[str, int] = {}
        for record in expected_records:
            mirror = record.get("mirror_group")
            if not isinstance(mirror, str) or not mirror:
                _error("clone target lacks frozen mirror identity")
            groups[mirror] = groups.get(mirror, 0) + 1
        if len(groups) != 15 or any(size != 2 for size in groups.values()):
            _error("clone batch must preserve exactly 15 two-file mirror groups")
        result["mirror_pairs"] = 15
    return result


def _check_portfolio(args: argparse.Namespace) -> dict[str, Any]:
    _, counts = _inventory_summary(args.track)
    report = _require_file(_track_path(args.track, "portfolio-review-report.md"), "portfolio report")
    if not report.read_text(encoding="utf-8").strip():
        _error("portfolio report is empty")
    manifest = _read_object(_track_path(args.track, "change-manifest.json"), "portfolio change manifest")
    summary = manifest.get("scope_summary", manifest.get("counts", {}))
    if isinstance(summary, dict) and summary:
        for key, expected in (("global", counts["global"]), ("local", counts["local"]), ("total", counts["global"] + counts["local"])):
            value = summary.get(key)
            if value is not None and value != expected:
                _error("portfolio manifest scope summary does not reconcile")
    _require_file(_track_path(args.track, "unresolved-decisions.json"), "unresolved decision list")
    return {"status": "PASS", "global": counts["global"], "local": counts["local"], "total": counts["global"] + counts["local"]}


def _metadata_progress(metadata: dict[str, Any]) -> tuple[int, int, int]:
    progress = metadata.get("progress")
    if not isinstance(progress, dict):
        _error("metadata lacks progress")
    total = progress.get("totalTasks")
    readiness = metadata.get("readiness_check_count")
    checkboxes = metadata.get("total_checkbox_count")
    if (total, readiness, checkboxes) != (17, 8, 25):
        _error("metadata task/readiness/checkbox counts are not 17/8/25")
    return total, readiness, checkboxes


def _check_execution_sync(args: argparse.Namespace) -> dict[str, Any]:
    metadata = _read_object(_track_path(args.track, "metadata.json"), "metadata")
    total, readiness, checkboxes = _metadata_progress(metadata)
    logs = list(assert_no_reparse(args.track, label="track").glob("execution-log-*.md"))
    if not logs or not any(path.is_file() and path.read_text(encoding="utf-8").strip() for path in logs):
        _error("missing nonempty execution log")
    return {"status": "PASS", "tasks": total, "readiness": readiness, "checkboxes": checkboxes}


def _check_ledgers(args: argparse.Namespace) -> dict[str, Any]:
    root = assert_no_reparse(args.track, label="track")
    repository = root.parent.parent
    identifier = root.name
    tracks = _require_file(repository / "tracks.md", "tracks ledger")
    ledger = _require_file(repository / "tracks-ledger.md", "authoritative tracks ledger")
    tracks_pattern = re.compile(rf"^\|\s*{re.escape(identifier)}\s*\|")
    ledger_pattern = re.compile(rf"^-\s*\[{re.escape(identifier)}\]\(")
    for path, pattern in (
        (tracks, tracks_pattern),
        (ledger, ledger_pattern),
    ):
        occurrences = sum(
            1
            for line in path.read_text(encoding="utf-8-sig").splitlines()
            if pattern.match(line)
        )
        if occurrences != 1:
            _error(
                f"{path.name} must contain exactly one authoritative "
                f"track entry, got {occurrences}"
            )
    return {"status": "PASS", "track": identifier, "unique": True}


def _check_stage7(args: argparse.Namespace) -> dict[str, Any]:
    root = assert_no_reparse(args.track, label="track")
    reports = sorted(path for path in root.glob("validation-report-*.md") if path.is_file())
    if not reports:
        _error("missing Stage 7 validation report")
    newest = reports[-1].read_text(encoding="utf-8").casefold()
    if "ready_to_close" not in newest and "ready to close" not in newest:
        _error("Stage 7 report lacks ready-to-close verdict")
    alternation = _read_object(root.parent.parent / "validator-alternation.json", "validator alternation state")
    if alternation.get("last_used") not in {"luna", "m3"}:
        _error("validator alternation state lacks a valid last_used identity")
    if alternation.get("next") not in {"luna", "m3"}:
        _error("validator alternation state lacks a derived next identity")
    recovery_route = (
        "failed attempt did not flip alternation state" in newest
        or "failed m3 dispatch left alternation state unchanged" in newest
    )
    return {
        "status": "PASS",
        "verdict": "ready_to_close",
        "alternation": "PASS",
        "state_flipped_after_success": not recovery_route,
        "recovery_route": recovery_route,
    }


def _check_terminal_closeout(args: argparse.Namespace) -> dict[str, Any]:
    root = assert_no_reparse(args.track, label="track")
    metadata = _read_object(root / "metadata.json", "metadata")
    if metadata.get("status") != "complete":
        _error("terminal closeout requires metadata status complete")
    if not list(root.glob("doc-update-log-*.md")) and not list(root.glob("stage9-waiver-*.md")):
        _error("terminal closeout lacks Stage 9 documentation evidence or waiver")
    plan = _require_file(root / "plan.md", "plan").read_text(encoding="utf-8")
    executor_markers = re.findall(r"- \[[xX]\] \*\*(?:0\.1|0\.2|0\.3|1\.1|1\.2|1\.3|1\.4|2\.1|2\.2|2\.3|2\.4|2\.5|3\.1|3\.2|3\.3|F\.1|F\.2)", plan)
    if len(executor_markers) != 17:
        _error("terminal closeout requires all 17 executor tasks checked")
    return {"status": "PASS", "terminal": "complete"}


def _check_global_changes(args: argparse.Namespace) -> dict[str, Any]:
    return _check_change_manifest(args, "global", "change-manifest-global.json", "global-validation.json")


def _check_local_changes(args: argparse.Namespace) -> dict[str, Any]:
    return _check_change_manifest(args, "local", "change-manifest-local.json", "local-validation.json")


CHECKS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "scope": _check_scope,
    "rubric": _check_rubric,
    "backups": _check_backups,
    "global-review": _check_global_review,
    "global-changes": _check_global_changes,
    "local-review": _check_local_review,
    "local-changes": _check_local_changes,
    "portfolio": _check_portfolio,
    "execution-sync": _check_execution_sync,
    "ledgers": _check_ledgers,
    "stage7": _check_stage7,
    "terminal-closeout": _check_terminal_closeout,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify deterministic AGENTS.md review evidence without modifying it.")
    parser.add_argument("--check", required=True, choices=CHECK_NAMES, help="named review contract to verify")
    parser.add_argument("--track", required=True, help="track-local evidence root")
    parser.add_argument("--target", help="global client identity for global-review")
    parser.add_argument("--batch", help="local review batch or all")
    parser.add_argument("--require-loading-evidence", action="store_true", help="require Pass or justified Unverified probe records")
    parser.add_argument("--deliberate-fail", action="store_true", help="exercise the fail path without reading or writing artifacts")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.deliberate_fail:
            _error("deliberate failure requested")
        result = CHECKS[args.check](args)
        print(json_line({"check": args.check, **result}))
        return 0
    except (VerificationError, ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json_line({"check": args.check, "status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
