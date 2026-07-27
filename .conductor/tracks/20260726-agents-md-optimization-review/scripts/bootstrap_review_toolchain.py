#!/usr/bin/env python3
"""Shared safety contract and bootstrap self-test for the AGENTS review track.

This module deliberately contains only standard-library code so every helper can
run in a disposable fixture.  It is also imported by the other declared helper
scripts; no helper writes an ``AGENTS.md`` except ``apply_agent_fixes.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any, Iterable


TRACK_NAME = "20260726-agents-md-optimization-review"
RUBRIC_IDS = (
    "SCOPE-01", "SCOPE-02", "LOAD-01", "LOAD-02", "PURPOSE-01",
    "STRUCT-01", "STRUCT-02", "TOKEN-01", "TOKEN-02", "CMD-01",
    "CMD-02", "REF-01", "REF-02", "ARCH-01", "CONV-01", "VERIFY-01",
    "SAFETY-01", "SAFETY-02", "GIT-01", "NEST-01", "CLIENT-01",
    "DRIFT-01", "REVIEW-01", "HANDOFF-01",
)
REQUIRED_PACKET_FIELDS = (
    "result", "applicability", "severity", "confidence", "evidence",
    "finding_id", "disposition",
)
CHECK_NAMES = (
    "scope", "rubric", "backups", "global-review", "global-changes",
    "local-review", "local-changes", "portfolio", "execution-sync",
    "ledgers", "stage7", "terminal-closeout",
)
HELPER_NAMES = (
    "inventory_agents.py", "verify_agents_review.py", "backup_agents.py",
    "audit_agents.py", "audit_batch.py", "consolidate_review.py",
    "apply_agent_fixes.py", "validate_instruction_loading.py",
    "generate_report.py", "sync_execution.py", "sync_ledgers.py",
    "dispatch_stage7.py", "complete_closeout.py",
    "bootstrap_review_toolchain.py",
)
ALLOWED_RESULTS = {"Pass", "Finding", "Not Applicable", "Unverified"}
ALLOWED_SEVERITIES = {"Critical", "Major", "Minor", "None"}
ALLOWED_DISPOSITIONS = {"apply", "retain", "defer", "optional", "blocked", "none"}


class ToolchainError(RuntimeError):
    """Raised for a contract violation that must fail closed."""


def fail(message: str) -> None:
    raise ToolchainError(message)


def canonical(path: str | Path) -> Path:
    return Path(path).expanduser().absolute()


def is_reparse_point(path: str | Path) -> bool:
    """Return true for symlinks/junctions without following them."""
    candidate = Path(path)
    try:
        if candidate.is_symlink():
            return True
        stat_result = candidate.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(stat_result, "st_file_attributes", 0)
    reparse = getattr(__import__("stat"), "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse)


def assert_no_reparse(path: str | Path, *, label: str = "path") -> Path:
    candidate = canonical(path)
    cursor = candidate
    while True:
        if cursor.exists() or cursor.is_symlink():
            if is_reparse_point(cursor):
                fail(f"{label} refuses junction/symlink/reparse point: {cursor}")
        parent = cursor.parent
        if parent == cursor:
            break
        cursor = parent
    return candidate


def assert_within(path: str | Path, root: str | Path, *, label: str = "path") -> Path:
    candidate = assert_no_reparse(path, label=label)
    boundary = assert_no_reparse(root, label=f"{label} root")
    try:
        common = os.path.commonpath((str(candidate), str(boundary)))
    except ValueError as exc:
        fail(f"{label} path-drive mismatch: {candidate} / {boundary}")
        raise exc  # pragma: no cover - fail always raises
    if os.path.normcase(common) != os.path.normcase(str(boundary)):
        fail(f"{label} escapes named root: {candidate} not under {boundary}")
    return candidate


def ensure_parent(path: str | Path, *, root: str | Path | None = None) -> Path:
    destination = canonical(path)
    if root is not None:
        assert_within(destination, root, label="output")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: str | Path) -> dict[str, Any]:
    candidate = assert_no_reparse(path, label="file")
    if not candidate.is_file():
        fail(f"expected regular file: {candidate}")
    return {"path": str(candidate), "sha256": sha256_file(candidate), "bytes": candidate.stat().st_size}


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | Path, payload: Any, *, root: str | Path | None = None) -> Path:
    destination = ensure_parent(path, root=root)
    temporary = destination.with_name(f".{destination.name}.tmp-{os.getpid()}")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, destination)
    return destination


def write_text(path: str | Path, text: str, *, root: str | Path | None = None) -> Path:
    destination = ensure_parent(path, root=root)
    temporary = destination.with_name(f".{destination.name}.tmp-{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, destination)
    return destination


def json_line(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def track_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def load_rubric(track: str | Path) -> dict[str, Any]:
    rubric = read_json(Path(track) / "rubric.json")
    errors = validate_rubric(rubric)
    if errors:
        fail("invalid frozen rubric: " + "; ".join(errors))
    return rubric


def validate_rubric(rubric: Any) -> list[str]:
    if not isinstance(rubric, dict):
        return ["rubric must be an object"]
    ids = rubric.get("rubric_ids")
    items = rubric.get("items")
    errors: list[str] = []
    if ids != list(RUBRIC_IDS):
        errors.append("rubric_ids must exactly equal the frozen 24-ID ordered list")
    if not isinstance(items, list) or [item.get("id") if isinstance(item, dict) else None for item in items] != list(RUBRIC_IDS):
        errors.append("items must contain each frozen ID exactly once and in order")
    return errors


def validate_packet(packet: Any, *, rubric_ids: Iterable[str] = RUBRIC_IDS) -> list[str]:
    expected = list(rubric_ids)
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be an object"]
    for key in ("file_identity", "client", "client_semantics", "rubric"):
        if key not in packet:
            errors.append(f"missing packet field: {key}")
    if packet.get("client") not in {"codex", "opencode"}:
        errors.append("client must be codex or opencode")
    semantics = packet.get("client_semantics")
    if not isinstance(semantics, dict) or not semantics.get("precedence") or not semantics.get("reference_loading"):
        errors.append("client_semantics must record precedence and reference_loading")
    entries = packet.get("rubric")
    if not isinstance(entries, list):
        return errors + ["rubric must be a list"]
    seen: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"rubric entry {index} must be an object")
            continue
        item_id = entry.get("id")
        seen.append(item_id)
        for field in REQUIRED_PACKET_FIELDS:
            if field not in entry:
                errors.append(f"{item_id or index}: missing {field}")
        if entry.get("result") not in ALLOWED_RESULTS:
            errors.append(f"{item_id or index}: invalid result")
        if not isinstance(entry.get("applicability"), bool):
            errors.append(f"{item_id or index}: applicability must be boolean")
        if entry.get("severity") not in ALLOWED_SEVERITIES:
            errors.append(f"{item_id or index}: invalid severity")
        if not isinstance(entry.get("confidence"), (int, float)) or not 0 <= entry.get("confidence", -1) <= 1:
            errors.append(f"{item_id or index}: confidence must be 0..1")
        if not isinstance(entry.get("evidence"), dict) or not entry.get("evidence"):
            errors.append(f"{item_id or index}: evidence must be a nonempty object")
        if not isinstance(entry.get("finding_id"), str):
            errors.append(f"{item_id or index}: finding_id must be a string")
        if entry.get("disposition") not in ALLOWED_DISPOSITIONS:
            errors.append(f"{item_id or index}: invalid disposition")
    if seen != expected:
        errors.append("packet rubric IDs must exactly equal frozen rubric IDs (unknown/duplicate/missing rejected)")
    return errors


def client_semantics(client: str) -> dict[str, str]:
    if client == "codex":
        return {
            "precedence": "hierarchical AGENTS discovery; nearer rules may refine parent rules",
            "reference_loading": "explicit references are evidence, not automatically loaded instructions",
        }
    if client == "opencode":
        return {
            "precedence": "first matching configured instruction source is authoritative",
            "reference_loading": "referenced files are not automatically parsed as instructions",
        }
    fail(f"unknown client: {client}")
    return {}  # pragma: no cover


def complete_packet(
    *, target: str | Path, client: str, evidence: dict[str, Any], mirror_identity: str | None = None
) -> dict[str, Any]:
    identity = file_record(target)
    packet: dict[str, Any] = {
        "file_identity": identity,
        "client": client,
        "client_semantics": client_semantics(client),
        "rubric": [],
    }
    if mirror_identity:
        packet["mirror_identity"] = mirror_identity
    for item_id in RUBRIC_IDS:
        packet["rubric"].append({
            "id": item_id,
            "result": "Pass",
            "applicability": True,
            "severity": "None",
            "confidence": 1.0,
            "evidence": dict(evidence),
            "finding_id": "",
            "disposition": "none",
        })
    return packet


def output_root_for_queue(queue: str | Path, explicit: str | Path | None = None) -> Path:
    return canonical(explicit) if explicit else canonical(queue).parent


def looks_like_live_target(path: str | Path) -> bool:
    """Conservative marker used only by the disposable-fixture proof ledger."""
    normal = os.path.normcase(str(canonical(path))).replace("/", "\\")
    return normal.endswith("\\agents.md") and (
        normal.startswith("c:\\development\\")
        or normal.startswith("c:\\users\\davewitkin\\")
    )


def run_owned_process(command: list[str], timeout_seconds: int) -> dict[str, Any]:
    """Run one owned probe with timeout cleanup and a normalized transcript."""
    if timeout_seconds <= 0:
        fail("timeout_seconds must be positive")
    kwargs: dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(command, **kwargs)
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        return {
            "status": "Unverified", "reason": "timeout", "returncode": process.returncode,
            "stdout": stdout, "stderr": stderr, "cleanup": "owned-process-terminated",
        }
    if process.returncode == 0:
        return {
            "status": "Pass", "reason": "probe returned zero", "returncode": process.returncode,
            "stdout": stdout, "stderr": stderr, "cleanup": "not-needed",
        }
    return {
        "status": "Fail", "reason": "probe returned nonzero", "returncode": process.returncode,
        "stdout": stdout, "stderr": stderr, "cleanup": "not-needed",
    }


def required_toolchain_paths(track: str | Path) -> set[Path]:
    root = canonical(track)
    return {
        root / "rubric.json",
        root / "schemas" / "review-packet.schema.json",
        root / "tests" / "test_review_toolchain.py",
        *(root / "scripts" / name for name in HELPER_NAMES),
    }


def self_test(track: str | Path) -> dict[str, Any]:
    root = canonical(track)
    missing = [str(path) for path in sorted(required_toolchain_paths(root)) if not path.is_file()]
    if missing:
        fail("declared toolchain files missing: " + ", ".join(missing))
    load_rubric(root)
    schema = read_json(root / "schemas" / "review-packet.schema.json")
    if not isinstance(schema, dict) or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail("review-packet schema is not valid Draft 2020-12 metadata")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for helper in HELPER_NAMES:
        source = (root / "scripts" / helper).read_text(encoding="utf-8")
        compile(source, str(root / "scripts" / helper), "exec")
        outcome = subprocess.run(
            [sys.executable, "-B", str(root / "scripts" / helper), "--help"],
            cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
        )
        if outcome.returncode != 0:
            fail(f"--help failed for {helper}: {outcome.stderr.strip()}")
    with tempfile.TemporaryDirectory(prefix="agents-review-self-test-") as temp_dir:
        proof_path = Path(temp_dir) / "proof.json"
        env["REVIEW_TOOLCHAIN_TEST_RESULT"] = str(proof_path)
        suite = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_review_toolchain.py"],
            cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180,
        )
        if suite.returncode != 0:
            fail("disposable fixture self-test failed: " + suite.stderr.strip())
        if not proof_path.is_file():
            fail("disposable fixture self-test did not emit its proof record")
        proof = read_json(proof_path)
    if proof.get("negative_cases_passed") is not True or int(proof.get("negative_case_count", 0)) < 15:
        fail("self-test did not prove at least 15 negative cases")
    if proof.get("live_targets_touched") != 0:
        fail("self-test touched a live target")
    return {
        "check": "toolchain-self-test",
        "status": "PASS",
        "helpers": 14,
        "negative_cases_passed": True,
        "negative_case_count": int(proof["negative_case_count"]),
        "live_targets_touched": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap and self-test the track-local AGENTS review toolchain.")
    parser.add_argument("--self-test", action="store_true", help="run the complete disposable-fixture contract")
    parser.add_argument("--track", default=str(track_from_script()), help="track-local toolchain root")
    args = parser.parse_args(argv)
    try:
        if not args.self_test:
            fail("--self-test is required; bootstrap never creates live review artifacts")
        print(json_line(self_test(args.track)))
        return 0
    except (ToolchainError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json_line({"check": "toolchain-self-test", "status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
