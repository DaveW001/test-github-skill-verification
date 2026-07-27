#!/usr/bin/env python3
"""Guarded, content-anchored AGENTS.md fix runner.

No target is opened for writing until every queued target has passed the
allowlist, baseline-hash, dirty-state, verified-backup, anchor, authority, and
output-containment guards.  The default action is apply because the frozen plan
invokes this helper without an extra flag; ``--dry-run`` provides the safe
preview path used by the disposable fixture tests.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    ToolchainError,
    assert_no_reparse,
    assert_within,
    canonical,
    file_record,
    json_line,
    read_json,
    sha256_file,
    validate_packet,
    write_json,
)


def _key(path: str | Path) -> str:
    return os.path.normcase(str(canonical(path)))


def _nonexpanding(value: Any) -> bool:
    return value in {False, None, "", "none", "None", "no", "false", "False", "no_authority_expansion"}


def _read_object(path: str | Path, label: str) -> dict[str, Any]:
    candidate = assert_no_reparse(path, label=label)
    if not candidate.is_file():
        raise ToolchainError(f"missing {label}: {candidate}")
    payload = read_json(candidate)
    if not isinstance(payload, dict):
        raise ToolchainError(f"{label} must be a JSON object")
    return payload


def _read_utf8_bytes(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ToolchainError(f"target is not UTF-8 and cannot be safely anchored: {path}") from exc
    return data, text


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    assert_no_reparse(path, label="write target")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.agents-review-", dir=str(path.parent))
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_text(path: Path, text: str) -> None:
    _atomic_write_bytes(path, text.encode("utf-8"))


def _literal_edits(value: Any) -> list[dict[str, str]]:
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list) or not value:
        raise ToolchainError("queued fix must contain a nonempty edits list")
    edits: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ToolchainError("queued edit must be an object")
        anchor = item.get("anchor", item.get("old"))
        replacement = item.get("replacement", item.get("new"))
        if not isinstance(anchor, str) or not anchor:
            raise ToolchainError("queued edit anchor must be a nonempty literal string")
        if not isinstance(replacement, str):
            raise ToolchainError("queued edit replacement must be a string")
        edits.append({"anchor": anchor, "replacement": replacement})
    if len({edit["anchor"] for edit in edits}) != len(edits):
        raise ToolchainError("queued edit anchors must be unique per target")
    return edits


def _extract_expected_hash(entry: dict[str, Any]) -> str:
    values = [entry.get(name) for name in ("pre_edit_sha256", "expected_sha256", "sha256") if entry.get(name) is not None]
    identity = entry.get("file_identity")
    if isinstance(identity, dict) and identity.get("sha256") is not None:
        values.append(identity["sha256"])
    values = [value for value in values if isinstance(value, str)]
    if not values or len(set(values)) != 1:
        raise ToolchainError("queued fix must have one unambiguous pre-edit SHA-256")
    digest = values[0]
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.casefold()):
        raise ToolchainError("queued pre-edit hash is not a SHA-256 digest")
    return digest.casefold()


def _entry_target(entry: dict[str, Any]) -> str:
    target = entry.get("target")
    if not isinstance(target, str):
        identity = entry.get("file_identity")
        if isinstance(identity, dict):
            target = identity.get("path")
    if not isinstance(target, str) or not target:
        raise ToolchainError("queued fix lacks target path")
    return target


def _git_dirty_state(target: Path) -> bool | None:
    """Return dirty state for the target path, or None for a non-Git target."""
    try:
        root_result = subprocess.run(
            ["git", "-C", str(target.parent), "rev-parse", "--show-toplevel"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ToolchainError(f"could not determine dirty state for {target}: {exc}") from exc
    if root_result.returncode != 0:
        return None
    repository = Path(root_result.stdout.strip())
    try:
        relative = os.path.relpath(target, repository)
    except ValueError as exc:
        raise ToolchainError(f"target is outside discovered Git root: {target}") from exc
    try:
        status = subprocess.run(
            ["git", "-C", str(repository), "status", "--porcelain", "--", relative],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ToolchainError(f"could not read target dirty state for {target}: {exc}") from exc
    if status.returncode != 0:
        raise ToolchainError(f"git status failed for {target}: {status.stderr.strip()}")
    return bool(status.stdout.strip())


def _guard_dirty_state(entry: dict[str, Any], target: Path) -> bool | None:
    if "dirty" not in entry:
        raise ToolchainError(f"queued fix lacks baseline dirty state: {target}")
    expected = entry["dirty"]
    if expected not in {True, False, None}:
        raise ToolchainError(f"queued dirty state is invalid: {target}")
    observed = _git_dirty_state(target)
    if expected is True:
        raise ToolchainError(f"queued target was dirty at baseline and cannot be edited: {target}")
    if observed is True:
        raise ToolchainError(f"target is dirty now; preserving user changes: {target}")
    if expected is None and observed is not None:
        raise ToolchainError(f"target dirty-state source changed since baseline: {target}")
    if expected is False and observed is True:
        raise ToolchainError(f"target dirty state no longer matches baseline: {target}")
    return observed


def _manifest_mapping(manifest: dict[str, Any], target: Path) -> tuple[dict[str, Any], Path]:
    backup_root = manifest.get("backup_root")
    entries = manifest.get("entries")
    if not isinstance(backup_root, str) or not isinstance(entries, list):
        raise ToolchainError("backup manifest lacks backup_root or entries")
    matching = [entry for entry in entries if isinstance(entry, dict) and isinstance(entry.get("source"), str) and _key(entry["source"]) == _key(target)]
    if len(matching) != 1:
        raise ToolchainError(f"backup manifest must map target exactly once: {target}")
    entry = matching[0]
    backup = entry.get("backup")
    digest = entry.get("sha256")
    size = entry.get("bytes")
    if not isinstance(backup, str) or not isinstance(digest, str) or not isinstance(size, int):
        raise ToolchainError(f"backup record is malformed for {target}")
    backup_path = assert_no_reparse(backup, label="backup")
    assert_within(backup_path, backup_root, label="backup")
    if not backup_path.is_file() or backup_path.stat().st_size != size or sha256_file(backup_path) != digest:
        raise ToolchainError(f"backup file hash/size does not verify: {backup_path}")
    return entry, backup_path


def _queue_from_packets(packets_root: Path, scope: str, queue_path: Path) -> dict[str, Any]:
    """Build a deterministic global queue in memory; never edit a target here."""
    if not packets_root.is_dir():
        raise ToolchainError(f"missing packets root: {packets_root}")
    packet_paths = sorted((path for path in packets_root.rglob("*.json") if path.is_file()), key=lambda item: str(item).casefold())
    if not packet_paths:
        raise ToolchainError("packets root contains no review packets")
    allowlist: list[str] = []
    entries: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for path in packet_paths:
        packet = _read_object(path, "review packet")
        errors = validate_packet(packet)
        if errors:
            raise ToolchainError(f"invalid review packet {path}: {'; '.join(errors)}")
        identity = packet["file_identity"]
        target = identity["path"]
        allowlist.append(target)
        for item in packet["rubric"]:
            if item["result"] != "Finding" or item["disposition"] != "apply":
                continue
            try:
                edits = _literal_edits(item.get("edits", item.get("edit", item.get("proposed_edit"))))
            except ToolchainError:
                unresolved.append({
                    "target": target,
                    "finding_id": item["finding_id"],
                    "rubric_id": item["id"],
                    "reason": "apply finding lacks a literal anchored edit",
                })
                continue
            entries.append({
                "target": target,
                "pre_edit_sha256": identity["sha256"],
                "dirty": None,
                "finding_id": item["finding_id"],
                "rubric_id": item["id"],
                "rationale": item.get("rationale", "global review finding"),
                "authority_delta": item.get("authority_delta", False),
                "edits": edits,
                "packet": str(path),
            })
    if len({_key(path) for path in allowlist}) != len(allowlist):
        raise ToolchainError("packets have duplicate file identities")
    return {
        "version": 1,
        "scope": scope,
        "allowlist": sorted(allowlist, key=str.casefold),
        "backup_manifest": str(queue_path.parent / "backup-manifest.json"),
        "entries": entries,
        "unresolved_apply_findings": unresolved,
        "authority_expansion": False,
    }


@dataclass
class PreparedFix:
    target: Path
    backup: Path
    before: bytes
    after: bytes
    expected_hash: str
    backup_hash: str
    dirty_observed: bool | None
    edits: list[dict[str, str]]
    source_entry: dict[str, Any]


def _normalize_queue(queue: dict[str, Any], queue_path: Path, requested_scope: str | None) -> tuple[str, list[dict[str, Any]], set[str], Path]:
    scope = queue.get("scope", requested_scope)
    if scope not in {"global", "local"}:
        raise ToolchainError("queue scope must be global or local")
    if requested_scope and scope != requested_scope:
        raise ToolchainError("requested scope does not match queue scope")
    if not _nonexpanding(queue.get("authority_expansion", False)):
        raise ToolchainError("queue records authority expansion")
    values = queue.get("entries", queue.get("items", queue.get("fixes")))
    if not isinstance(values, list):
        raise ToolchainError("queue must contain entries")
    allowlist_value = queue.get("allowlist")
    if not isinstance(allowlist_value, list) or not allowlist_value or not all(isinstance(item, str) for item in allowlist_value):
        raise ToolchainError("queue must contain a nonempty explicit allowlist")
    allowlist = {_key(item) for item in allowlist_value}
    if len(allowlist) != len(allowlist_value):
        raise ToolchainError("queue allowlist has duplicate identities")
    manifest_value = queue.get("backup_manifest", str(queue_path.parent / "backup-manifest.json"))
    if not isinstance(manifest_value, str):
        raise ToolchainError("queue backup_manifest must be a path")
    return scope, values, allowlist, assert_no_reparse(manifest_value, label="backup manifest")


def _prepare_fixes(queue: dict[str, Any], queue_path: Path, requested_scope: str | None) -> tuple[str, list[PreparedFix], dict[str, Any]]:
    scope, entries, allowlist, backup_manifest_path = _normalize_queue(queue, queue_path, requested_scope)
    if not entries:
        return scope, [], {"version": 1, "backup_root": "", "entries": []}
    backup_manifest = _read_object(backup_manifest_path, "backup manifest")
    prepared: list[PreparedFix] = []
    seen_targets: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ToolchainError("queue entry must be an object")
        if "authority_delta" not in entry or not _nonexpanding(entry.get("authority_delta")):
            raise ToolchainError("queue entry has missing or expanding authority delta")
        target = assert_no_reparse(_entry_target(entry), label="queued target")
        if target.name.casefold() != "agents.md":
            raise ToolchainError(f"only AGENTS.md can be edited by this helper: {target}")
        target_key = _key(target)
        if target_key not in allowlist:
            raise ToolchainError(f"target is not explicitly allowlisted: {target}")
        if target_key in seen_targets:
            raise ToolchainError(f"queue has multiple entries for one target: {target}")
        seen_targets.add(target_key)
        if not target.is_file():
            raise ToolchainError(f"queued target is not a regular file: {target}")
        expected_hash = _extract_expected_hash(entry)
        actual_hash = sha256_file(target)
        if actual_hash != expected_hash:
            raise ToolchainError(f"pre-edit hash mismatch; preserving target: {target}")
        dirty_observed = _guard_dirty_state(entry, target)
        backup_entry, backup = _manifest_mapping(backup_manifest, target)
        backup_hash = backup_entry["sha256"]
        if backup_hash != expected_hash:
            raise ToolchainError(f"verified backup hash does not equal pre-edit hash: {target}")
        before, text = _read_utf8_bytes(target)
        edits = _literal_edits(entry.get("edits", entry.get("edit")))
        after_text = text
        for edit in edits:
            occurrences = after_text.count(edit["anchor"])
            if occurrences != 1:
                raise ToolchainError(f"anchor must appear exactly once in target: {target}")
            after_text = after_text.replace(edit["anchor"], edit["replacement"], 1)
        after = after_text.encode("utf-8")
        prepared.append(PreparedFix(
            target=target,
            backup=backup,
            before=before,
            after=after,
            expected_hash=expected_hash,
            backup_hash=backup_hash,
            dirty_observed=dirty_observed,
            edits=edits,
            source_entry=entry,
        ))
    return scope, prepared, backup_manifest


def _diff_text(fix: PreparedFix) -> str:
    before = fix.before.decode("utf-8").splitlines(keepends=True)
    after = fix.after.decode("utf-8").splitlines(keepends=True)
    return "".join(difflib.unified_diff(before, after, fromfile=f"{fix.target} (before)", tofile=f"{fix.target} (after)"))


def _diff_path(diff_root: Path, target: Path) -> Path:
    digest = hashlib.sha256(_key(target).encode("utf-8")).hexdigest()[:20]
    return diff_root / f"{digest}-AGENTS.md.diff"


def restore_to_disposable(prepared: list[PreparedFix], restore_root: str | Path) -> list[dict[str, Any]]:
    """Copy verified backups only to a caller-supplied disposable tree."""
    root = assert_no_reparse(restore_root, label="restore root")
    target_keys = {_key(fix.target) for fix in prepared}
    if _key(root) in target_keys or root.name.casefold() == "agents.md":
        raise ToolchainError("restore root cannot be a live target")
    results: list[dict[str, Any]] = []
    for fix in prepared:
        destination = root / hashlib.sha256(_key(fix.target).encode("utf-8")).hexdigest()[:20] / "AGENTS.md"
        assert_within(destination, root, label="disposable restore output")
        backup_data = fix.backup.read_bytes()
        if hashlib.sha256(backup_data).hexdigest() != fix.backup_hash:
            raise ToolchainError(f"backup changed before restore simulation: {fix.backup}")
        _atomic_write_bytes(destination, backup_data)
        if sha256_file(destination) != fix.backup_hash:
            raise ToolchainError(f"disposable restore hash mismatch: {destination}")
        results.append({"target": str(fix.target), "restored": str(destination), "sha256": fix.backup_hash})
    return results


def _manifest_payload(scope: str, prepared: list[PreparedFix], *, dry_run: bool, diff_paths: dict[str, Path], restore: list[dict[str, Any]] | None) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    for fix in prepared:
        changes.append({
            "target": str(fix.target),
            "before_sha256": fix.expected_hash,
            "after_sha256": hashlib.sha256(fix.after).hexdigest(),
            "before_bytes": len(fix.before),
            "after_bytes": len(fix.after),
            "backup": str(fix.backup),
            "backup_sha256": fix.backup_hash,
            "dirty_observed": fix.dirty_observed,
            "anchors": [edit["anchor"] for edit in fix.edits],
            "authority_delta": False,
            "rationale": fix.source_entry.get("rationale", "queued high-confidence fix"),
            "finding_id": fix.source_entry.get("finding_id", ""),
            "diff": str(diff_paths[_key(fix.target)]),
        })
    return {
        "version": 1,
        "scope": scope,
        "dry_run": dry_run,
        "authority_expansion": False,
        "changes": changes,
        "restore_simulation": "PASS" if restore is not None else "not-requested",
        "restored": restore or [],
    }


def run_apply(
    *,
    queue_path: str | Path,
    manifest_path: str | Path,
    diff_root: str | Path,
    scope: str | None = None,
    packets_root: str | Path | None = None,
    output_root: str | Path | None = None,
    dry_run: bool = False,
    restore_to: str | Path | None = None,
) -> dict[str, Any]:
    """Run all guards, then optionally apply an all-or-rollback set of fixes."""
    queue_file = canonical(queue_path)
    manifest_file = canonical(manifest_path)
    diff_directory = canonical(diff_root)
    output_boundary = canonical(output_root) if output_root else queue_file.parent
    for path, label in ((queue_file, "queue"), (manifest_file, "manifest"), (diff_directory, "diff root")):
        assert_within(path, output_boundary, label=label)
    generated_queue = False
    if queue_file.is_file():
        queue = _read_object(queue_file, "fix queue")
    else:
        if packets_root is None:
            raise ToolchainError(f"missing fix queue: {queue_file}")
        packet_root = assert_no_reparse(packets_root, label="packets root")
        if scope not in {"global", "local"}:
            raise ToolchainError("--scope is required when building a queue from packets")
        queue = _queue_from_packets(packet_root, scope, queue_file)
        generated_queue = True

    # This is the no-write guard stage.  Nothing below may run until every
    # target, backup, anchor, dirty state, and output path has been accepted.
    actual_scope, prepared, _backup_manifest = _prepare_fixes(queue, queue_file, scope)
    diff_paths = {_key(fix.target): _diff_path(diff_directory, fix.target) for fix in prepared}
    for path in diff_paths.values():
        assert_within(path, output_boundary, label="diff output")
    restore_records: list[dict[str, Any]] | None = None
    if restore_to is not None:
        restore_root = canonical(restore_to)
        if restore_root == queue_file or restore_root == manifest_file or restore_root == diff_directory:
            raise ToolchainError("restore root cannot overlap a track output path")

    if dry_run:
        # A dry run has no writes at all, including queue generation and
        # disposable restore.  It still returns the exact planned manifest.
        payload = _manifest_payload(actual_scope, prepared, dry_run=True, diff_paths=diff_paths, restore=None)
        return {"status": "PASS", "scope": actual_scope, "dry_run": True, "changes": len(prepared), "manifest": payload, "queue_generated": generated_queue}

    written: list[PreparedFix] = []
    try:
        # Apply only after all guards have passed for all targets.
        for fix in prepared:
            _atomic_write_bytes(fix.target, fix.after)
            if sha256_file(fix.target) != hashlib.sha256(fix.after).hexdigest():
                raise ToolchainError(f"post-edit hash verification failed: {fix.target}")
            written.append(fix)
        if restore_to is not None:
            restore_records = restore_to_disposable(prepared, restore_to)
        for fix in prepared:
            output = diff_paths[_key(fix.target)]
            _atomic_write_text(output, _diff_text(fix))
        payload = _manifest_payload(actual_scope, prepared, dry_run=False, diff_paths=diff_paths, restore=restore_records)
        if generated_queue:
            write_json(queue_file, queue, root=output_boundary)
        write_json(manifest_file, payload, root=output_boundary)
    except Exception as exc:
        rollback_errors: list[str] = []
        for fix in reversed(written):
            try:
                backup_data = fix.backup.read_bytes()
                if hashlib.sha256(backup_data).hexdigest() != fix.backup_hash:
                    raise ToolchainError("verified backup changed during rollback")
                _atomic_write_bytes(fix.target, backup_data)
            except Exception as rollback_exc:  # pragma: no cover - catastrophic I/O only
                rollback_errors.append(f"{fix.target}: {rollback_exc}")
        suffix = f"; rollback errors: {' | '.join(rollback_errors)}" if rollback_errors else ""
        if isinstance(exc, ToolchainError):
            raise ToolchainError(f"apply failed and completed writes were restored{suffix}: {exc}") from exc
        raise ToolchainError(f"apply failed and completed writes were restored{suffix}: {exc}") from exc
    return {
        "status": "PASS",
        "scope": actual_scope,
        "dry_run": False,
        "changes": len(prepared),
        "manifest": str(manifest_file),
        "queue_generated": generated_queue,
        "restore_simulation": "PASS" if restore_records is not None else "not-requested",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply only fully guarded, literal, high-confidence AGENTS.md fixes.")
    parser.add_argument("--scope", choices=("global", "local"), help="optional asserted queue scope")
    parser.add_argument("--packets-root", help="build a deterministic queue from packets if --queue does not yet exist")
    parser.add_argument("--queue", required=True, help="approved fix queue JSON")
    parser.add_argument("--manifest", required=True, help="change-manifest JSON output")
    parser.add_argument("--diff-root", required=True, help="directory for exact unified diffs")
    parser.add_argument("--output-root", help="named containment boundary for queue, manifest, and diffs")
    parser.add_argument("--dry-run", action="store_true", help="run every guard and produce no writes")
    parser.add_argument("--apply", action="store_true", help="explicitly request the default guarded apply action")
    parser.add_argument("--restore-to", help="write verified backups only into a disposable restore tree")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.apply and args.dry_run:
        print(json_line({"status": "FAIL", "error": "--apply and --dry-run are mutually exclusive"}))
        return 1
    try:
        result = run_apply(
            queue_path=args.queue,
            manifest_path=args.manifest,
            diff_root=args.diff_root,
            scope=args.scope,
            packets_root=args.packets_root,
            output_root=args.output_root,
            dry_run=args.dry_run,
            restore_to=args.restore_to,
        )
        print(json_line(result))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json_line({"status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
