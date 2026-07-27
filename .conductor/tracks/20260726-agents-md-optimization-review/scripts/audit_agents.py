#!/usr/bin/env python3
"""Create one complete, client-aware 24-item AGENTS.md review packet.

This helper is deliberately review-only.  Its only possible write is the
requested JSON packet, and it refuses an output named AGENTS.md so an audit can
never become an instruction-file edit by accident.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    RUBRIC_IDS,
    ToolchainError,
    assert_no_reparse,
    canonical,
    complete_packet,
    fail,
    file_record,
    json_line,
    sha256_file,
    write_json,
)


def _reference_record(path: str | None, label: str) -> dict[str, Any]:
    if not path:
        return {"label": label, "provided": False}
    candidate = assert_no_reparse(path, label=label)
    if not candidate.is_file():
        return {"label": label, "provided": True, "path": str(candidate), "available": False}
    return {
        "label": label,
        "provided": True,
        "path": str(candidate),
        "available": True,
        "sha256": sha256_file(candidate),
        "bytes": candidate.stat().st_size,
    }


def _entry(packet: dict[str, Any], item_id: str) -> dict[str, Any]:
    for entry in packet["rubric"]:
        if entry["id"] == item_id:
            return entry
    raise RuntimeError(f"missing frozen rubric ID {item_id}")


def _finding(
    packet: dict[str, Any],
    item_id: str,
    *,
    result: str,
    severity: str,
    confidence: float,
    evidence: dict[str, Any],
    finding_id: str,
    disposition: str,
) -> None:
    entry = _entry(packet, item_id)
    entry.update({
        "result": result,
        "applicability": True,
        "severity": severity,
        "confidence": confidence,
        "evidence": evidence,
        "finding_id": finding_id,
        "disposition": disposition,
    })


def _static_signals(text: str) -> dict[str, Any]:
    headings = len(re.findall(r"(?m)^#{1,6}\s+\S", text))
    bullets = len(re.findall(r"(?m)^\s*(?:[-*+] |\d+\. )", text))
    return {
        "headings": headings,
        "bullets": bullets,
        "contains_approval_gate": bool(re.search(r"\b(?:approval|approve|authorize|permission|confirm)\b", text, re.I)),
        "contains_destructive_guard": bool(re.search(r"\b(?:delete|remove|overwrite|reset|destroy)\b", text, re.I)),
        "contains_codex_name": "codex" in text.casefold(),
        "contains_opencode_name": "opencode" in text.casefold(),
    }


def build_packet(
    *,
    target: str | Path,
    client: str,
    manual: str | None = None,
    reference: str | None = None,
    mirror_identity: str | None = None,
) -> dict[str, Any]:
    """Build a schema-complete packet without writing any artifact."""
    if client not in {"codex", "opencode"}:
        fail("client must be codex or opencode")
    target_path = assert_no_reparse(target, label="audit target")
    if target_path.name.casefold() != "agents.md":
        fail("audit target must be named AGENTS.md")
    identity = file_record(target_path)
    text = target_path.read_text(encoding="utf-8", errors="replace")
    manual_record = _reference_record(manual, "manual")
    reference_record = _reference_record(reference, "reference")
    evidence = {
        "command": "audit_agents.py",
        "target": identity,
        "client": client,
        "manual": manual_record,
        "reference": reference_record,
    }
    packet = complete_packet(target=target_path, client=client, evidence=evidence, mirror_identity=mirror_identity)
    packet["audit"] = {
        "mode": "static-review",
        "signals": _static_signals(text),
        "references": {"manual": manual_record, "reference": reference_record},
    }

    # These are intentionally conservative static findings.  The packet stays
    # complete even when a runtime client probe has not yet been run.
    signals = packet["audit"]["signals"]
    if not text.strip():
        _finding(packet, "PURPOSE-01", result="Finding", severity="Major", confidence=1.0,
                 evidence={"reason": "AGENTS.md is empty", "target": identity},
                 finding_id="AUTO-PURPOSE-EMPTY", disposition="defer")
        _finding(packet, "STRUCT-01", result="Finding", severity="Major", confidence=1.0,
                 evidence={"reason": "AGENTS.md is empty", "target": identity},
                 finding_id="AUTO-STRUCT-EMPTY", disposition="defer")
    elif signals["headings"] == 0:
        _finding(packet, "STRUCT-01", result="Finding", severity="Minor", confidence=0.95,
                 evidence={"reason": "no Markdown heading found", "target": identity},
                 finding_id="AUTO-STRUCT-NO-HEADING", disposition="retain")
    if identity["bytes"] > 32768:
        _finding(packet, "TOKEN-02", result="Finding", severity="Minor", confidence=1.0,
                 evidence={"reason": "file exceeds 32 KiB", "bytes": identity["bytes"]},
                 finding_id="AUTO-TOKEN-LARGE", disposition="defer")
    if signals["contains_destructive_guard"] and not signals["contains_approval_gate"]:
        _finding(packet, "SAFETY-01", result="Unverified", severity="None", confidence=0.65,
                 evidence={"reason": "destructive terms found without a static approval-gate marker"},
                 finding_id="AUTO-SAFETY-GATE-UNVERIFIED", disposition="blocked")

    required_reference = manual_record if client == "codex" else reference_record
    reference_id = "LOAD-01" if client == "codex" else "REF-02"
    if required_reference.get("provided") and not required_reference.get("available"):
        _finding(packet, reference_id, result="Unverified", severity="None", confidence=1.0,
                 evidence={"reason": "requested client reference was unavailable", "reference": required_reference},
                 finding_id="AUTO-REFERENCE-UNAVAILABLE", disposition="blocked")
    elif not required_reference.get("provided"):
        _finding(packet, reference_id, result="Unverified", severity="None", confidence=0.8,
                 evidence={"reason": "no client reference was supplied to this static audit"},
                 finding_id="AUTO-REFERENCE-NOT-SUPPLIED", disposition="defer")

    # Freeze the expected ordering in the output even if a future helper
    # refactors complete_packet.
    if [entry["id"] for entry in packet["rubric"]] != list(RUBRIC_IDS):
        fail("packet rubric IDs lost frozen ordering")
    return packet


def write_packet(packet: dict[str, Any], output: str | Path) -> Path:
    destination = canonical(output)
    if destination.name.casefold() == "agents.md":
        fail("audit output cannot be named AGENTS.md")
    return write_json(destination, packet, root=destination.parent)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a complete client-aware AGENTS.md review packet.")
    parser.add_argument("--client", required=True, choices=("codex", "opencode"), help="target client")
    parser.add_argument("--target", required=True, help="AGENTS.md to audit read-only")
    parser.add_argument("--manual", help="Codex manual evidence path")
    parser.add_argument("--reference", help="OpenCode rules/reference evidence path")
    parser.add_argument("--mirror-identity", help="frozen mirror-group identity to preserve in the packet")
    parser.add_argument("--output", required=True, help="packet JSON output path")
    parser.add_argument("--dry-run", action="store_true", help="print the packet without writing it")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        packet = build_packet(
            target=args.target,
            client=args.client,
            manual=args.manual,
            reference=args.reference,
            mirror_identity=args.mirror_identity,
        )
        if args.dry_run:
            print(json.dumps(packet, indent=2, sort_keys=True))
        else:
            output = write_packet(packet, args.output)
            print(json_line({"status": "PASS", "packet": str(output), "rubric_identities": len(packet["rubric"])}))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json_line({"status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
