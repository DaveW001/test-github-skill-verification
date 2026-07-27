#!/usr/bin/env python3
"""Stage 9 dispatch plus orchestrator-owned terminal Phase B closeout."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    ToolchainError,
    canonical,
    fail,
    json_line,
    read_json,
    write_text,
)
from dispatch_stage7 import (
    _append_anomaly,
    run_dispatch_process,
    verify_completion_sync,
)
from sync_execution import EXECUTABLE_TASKS
from sync_ledgers import build_ledger_updates


DOC_AGENT = "conductor-doc-writer"
DOC_MODEL = "opencode-go/deepseek-v4-flash"
DOC_VARIANT = "high"
TERMINAL_MARKER = "<!-- terminal-closeout-phase-b -->"
DOC_EXTENSIONS = {".md", ".markdown", ".rst", ".txt", ".adoc"}
EXCLUDED_DIRS = {
    ".git",
    ".osgrep",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")


def _digest(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _workspace_root(track: Path) -> Path:
    return track.parent.parent.parent


def _inventory_targets(track: Path) -> set[Path]:
    path = track / "scope-inventory.json"
    if not path.is_file():
        return set()
    payload = read_json(path)
    targets = payload.get("targets") if isinstance(payload, dict) else None
    if not isinstance(targets, list):
        fail("scope inventory targets must be an array")
    return {
        canonical(item["path"])
        for item in targets
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def _snapshot(track: Path) -> dict[str, tuple[str, int]]:
    workspace = _workspace_root(track)
    files: set[Path] = set()
    for root, dirnames, filenames in os.walk(workspace):
        dirnames[:] = [
            name for name in dirnames if name.lower() not in EXCLUDED_DIRS
        ]
        directory = Path(root)
        files.update(directory / name for name in filenames)
    files.update(_inventory_targets(track))
    snapshot: dict[str, tuple[str, int]] = {}
    for path in files:
        try:
            if path.is_file() and not path.is_symlink():
                snapshot[os.path.normcase(str(canonical(path)))] = _digest(path)
        except OSError:
            continue
    return snapshot


def _allowed_documentation(path: Path, track: Path) -> bool:
    normalized = os.path.normcase(str(canonical(path)))
    track_normalized = os.path.normcase(str(track))
    if normalized.startswith(track_normalized + os.sep):
        return bool(
            re.fullmatch(
                r"doc-update-log-\d{4}-\d{2}-\d{2}(?:T|-)\d{6}(?:Z)?\.md",
                path.name,
                re.IGNORECASE,
            )
        )
    if path.suffix.lower() not in DOC_EXTENSIONS:
        return False
    workspace = _workspace_root(track)
    try:
        relative = path.relative_to(workspace)
    except ValueError:
        return False
    lowered_parts = [part.lower() for part in relative.parts]
    name = path.name.lower()
    return (
        any(part in {"docs", "doc", "documentation", "adr", "adrs"} for part in lowered_parts[:-1])
        or name.startswith("readme")
        or name.startswith("changelog")
        or name.startswith("history")
        or name.startswith("release-notes")
    )


def _changed_paths(
    before: dict[str, tuple[str, int]], after: dict[str, tuple[str, int]]
) -> set[str]:
    return {
        key
        for key in set(before) | set(after)
        if before.get(key) != after.get(key)
    }


def _anomaly_append_only_ok(
    path: Path, before_bytes: bytes | None
) -> bool:
    if before_bytes is None or not path.is_file():
        return False
    try:
        current = path.read_bytes()
    except OSError:
        return False
    return current.startswith(before_bytes)


def _stage7_report(track: Path) -> Path:
    reports = sorted(
        track.glob("validation-report-*.md"),
        key=lambda path: (path.stat().st_mtime_ns, path.name),
    )
    if not reports:
        fail("Stage 7 ready-to-close report is missing")
    report = reports[-1]
    text = report.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()
    if "not ready to close" in lowered or not re.search(
        r"\bready[_ ]to[_ ]close\b", lowered
    ):
        fail(f"latest Stage 7 report is not ready-to-close: {report}")
    if "required fixes before close" not in lowered:
        fail(f"latest Stage 7 report is malformed: {report}")
    required = lowered.split("required fixes before close", 1)[1]
    if "final recommendation" in required:
        required = required.split("final recommendation", 1)[0]
    if "no fixes required" not in required:
        fail(f"latest Stage 7 report has unresolved fixes: {report}")
    if not any(
        identity in lowered
        for identity in ("conductor-track-validator", "conductor-track-validator-m3")
    ):
        fail(f"latest Stage 7 report lacks validator identity: {report}")
    return report


def _stage9_prompt(track: Path) -> str:
    return (
        "Run Conductor Stage 9 documentation for the track at "
        f"{track}. Agent={DOC_AGENT}; model={DOC_MODEL}; variant={DOC_VARIANT}. "
        "Read spec.md, plan.md, public documentation surfaces, and the latest "
        "ready-to-close Stage 7 report. You have docs-only authority: you may edit "
        "README/usage docs, API docs, changelog, ADRs, and create one "
        "doc-update-log timestamped Markdown artifact inside the track. Do not "
        "modify any AGENTS.md, source, test, build/configuration, plan.md, "
        "metadata.json, tracks.md, or tracks-ledger.md. List every touched path "
        "absolutely and classify each edit as 'non-contractual sync' or "
        "'semantic/contract-affecting'. State whether post-doc validation is "
        "required. If no documentation change is warranted, return an explicit "
        "WAIVED decision with a dated reason. Keep every command bounded and "
        "return promptly on a blocker."
    )


def _default_command(track: Path, prompt: str) -> list[str]:
    executable = shutil.which("opencode") or "opencode"
    return [
        executable,
        "run",
        "--agent",
        DOC_AGENT,
        "--model",
        DOC_MODEL,
        "--variant",
        DOC_VARIANT,
        "--title",
        f"Stage 9 documentation {track.name}",
        "--",
        prompt,
    ]


def _command_from_json(
    raw: str | None, *, track: Path, prompt: str
) -> list[str] | None:
    if raw is None:
        raw = os.environ.get("CONDUCTOR_STAGE9_COMMAND_JSON")
    if raw is None:
        return None
    try:
        command = json.loads(raw)
    except json.JSONDecodeError:
        path = Path(raw)
        if not path.is_file():
            raise
        command = read_json(path)
    if not isinstance(command, list) or not command or not all(
        isinstance(part, str) and part for part in command
    ):
        fail("Stage 9 command override must be a nonempty JSON string array")
    replacements = {
        "{track}": str(track),
        "{agent}": DOC_AGENT,
        "{model}": DOC_MODEL,
        "{variant}": DOC_VARIANT,
        "{prompt}": prompt,
    }
    expanded: list[str] = []
    for part in command:
        value = part
        for marker, replacement in replacements.items():
            value = value.replace(marker, replacement)
        expanded.append(value)
    return expanded


def _parse_stage9_response(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        fail("Stage 9 returned an empty response")
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        if payload.get("agent") != DOC_AGENT or payload.get("model") != DOC_MODEL:
            fail("structured Stage 9 response has the wrong agent/model identity")
        classification = payload.get("classification")
        waiver = payload.get("waiver_reason")
        docs = payload.get("docs_touched", [])
        if not isinstance(docs, list) or not all(
            isinstance(item, str) for item in docs
        ):
            fail("structured Stage 9 docs_touched must be a string array")
        if classification not in {
            "non-contractual sync",
            "semantic/contract-affecting",
            "waived",
        }:
            fail("structured Stage 9 response has an invalid classification")
        if classification == "waived" and not isinstance(waiver, str):
            fail("Stage 9 waiver requires a reason")
        return {
            "raw": stripped,
            "classification": classification,
            "waiver": waiver,
            "docs_touched": docs,
            "post_doc_required": bool(
                payload.get("post_doc_validation_required")
            ),
        }
    lowered = stripped.lower()
    if DOC_AGENT not in lowered or DOC_MODEL not in lowered:
        fail("Stage 9 response does not prove the pinned agent/model identity")
    waiver_match = re.search(r"\bwaived\b", lowered)
    semantic = "semantic/contract-affecting" in lowered
    non_contractual = "non-contractual sync" in lowered
    if not (waiver_match or semantic or non_contractual):
        fail("Stage 9 response lacks a valid documentation classification")
    classification = (
        "waived"
        if waiver_match and not semantic and not non_contractual
        else "semantic/contract-affecting"
        if semantic
        else "non-contractual sync"
    )
    return {
        "raw": stripped,
        "classification": classification,
        "waiver": stripped if classification == "waived" else None,
        "docs_touched": [],
        "post_doc_required": semantic,
    }


def _new_doc_log(track: Path, before_names: set[str]) -> Path | None:
    candidates = [
        path
        for path in track.glob("doc-update-log-*.md")
        if path.name not in before_names
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def _persist_stage9_evidence(
    track: Path,
    parsed: dict[str, Any],
    changed_docs: list[Path],
    existing: Path | None,
) -> Path:
    if existing is not None:
        text = existing.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        if not any(
            marker in lowered
            for marker in (
                "non-contractual sync",
                "semantic/contract-affecting",
                "waived",
            )
        ):
            fail(f"malformed Stage 9 artifact: {existing}")
        for path in changed_docs:
            if str(path) not in text:
                fail(f"Stage 9 artifact omits changed documentation path: {path}")
        return existing
    path = track / f"doc-update-log-{_timestamp_slug()}.md"
    lines = [
        "# Stage 9 Documentation Update Log",
        "",
        f"- Timestamp: `{_utc_now()}`",
        f"- Agent: `{DOC_AGENT}`",
        f"- Model: `{DOC_MODEL}`",
        f"- Variant: `{DOC_VARIANT}`",
        f"- Classification: `{parsed['classification']}`",
        f"- Post-doc validation required: `{str(parsed['post_doc_required']).lower()}`",
        "",
        "## Documentation files touched",
        "",
    ]
    if changed_docs:
        lines.extend(f"- `{path}`" for path in changed_docs)
    else:
        lines.append("- None.")
    if parsed["waiver"]:
        lines.extend(["", "## WAIVED", "", str(parsed["waiver"])])
    lines.extend(["", "## Returned evidence", "", parsed["raw"], ""])
    write_text(path, "\n".join(lines), root=track)
    return path


def _post_doc_phase_b(
    track: Path,
    *,
    stage9_log: Path,
    classification: str,
    changed_docs: list[Path],
) -> Path:
    path = track / f"post-doc-validation-{_timestamp_slug()}.md"
    if classification == "semantic/contract-affecting":
        log_text = stage9_log.read_text(encoding="utf-8", errors="replace")
        missing = [str(item) for item in changed_docs if str(item) not in log_text]
        if missing:
            fail(
                "semantic post-doc validation cannot reconcile changed docs: "
                + ", ".join(missing)
            )
        lines = [
            "# Post-Documentation Validation",
            "",
            "- Status: `PASS`",
            "- Classification: `semantic/contract-affecting`",
            f"- Stage 9 evidence: `{stage9_log}`",
            "- Validator: orchestrator Phase B",
            "- Check: every changed documentation path is listed in the Stage 9 log.",
            "- Check: Stage 9 made no prohibited source/test/config/bookkeeping edit.",
            "- Remaining gaps: none reported.",
            "",
        ]
    else:
        reason = (
            "Stage 9 was explicitly waived with a recorded reason."
            if classification == "waived"
            else "Documentation changes were non-contractual synchronization only."
        )
        lines = [
            "# Post-Documentation Validation",
            "",
            "- Status: `WAIVED`",
            f"- Reason: {reason}",
            f"- Stage 9 evidence: `{stage9_log}`",
            "- Authority: orchestrator Phase B",
            "",
        ]
    write_text(path, "\n".join(lines), root=track)
    return path


def _terminal_plan_text(
    original: str, *, stage7: Path, stage9: Path, post_doc: Path
) -> str:
    block = "\n".join(
        [
            TERMINAL_MARKER,
            "## Terminal Closeout Record",
            "",
            f"- Phase A Stage 7: `ready_to_close` — `{stage7}`",
            f"- Stage 9 evidence: `{stage9}`",
            f"- Orchestrator Phase B: `PASS` — `{post_doc}`",
            "",
        ]
    )
    if TERMINAL_MARKER in original:
        prefix = original.split(TERMINAL_MARKER, 1)[0].rstrip()
        return prefix + "\n\n" + block
    return original.rstrip() + "\n\n" + block


def _atomic_multi_text(replacements: dict[Path, str]) -> None:
    originals = {path: path.read_bytes() for path in replacements}
    temporaries: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, text in replacements.items():
            temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
            temporary.write_text(text, encoding="utf-8", newline="\n")
            temporaries[path] = temporary
        for path in replacements:
            os.replace(temporaries[path], path)
            replaced.append(path)
        for path, text in replacements.items():
            if path.read_text(encoding="utf-8") != text:
                fail(f"Phase B post-write verification failed: {path}")
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


def _restore_bookkeeping(originals: dict[Path, bytes]) -> None:
    for path, original in originals.items():
        try:
            current = path.read_bytes()
        except OSError:
            current = b""
        if current == original:
            continue
        temporary = path.with_name(f".{path.name}.stage9-restore-{os.getpid()}")
        temporary.write_bytes(original)
        os.replace(temporary, path)


def _already_complete(track: Path, metadata: dict[str, Any]) -> dict[str, Any] | None:
    terminal = metadata.get("terminal_closeout")
    if metadata.get("status") != "complete":
        return None
    if not isinstance(terminal, dict) or terminal.get("phase_b") != "PASS":
        fail("metadata is complete without valid orchestrator Phase B evidence")
    for name in ("stage7_report", "stage9_artifact", "post_doc_validation"):
        value = terminal.get(name)
        if not isinstance(value, str) or not Path(value).is_file():
            fail(f"metadata is complete without valid {name} evidence")
    if TERMINAL_MARKER not in (track / "plan.md").read_text(encoding="utf-8"):
        fail("metadata is complete but plan lacks terminal Phase B record")
    return {
        "check": "terminal-closeout-action",
        "status": "PASS",
        "idempotent": True,
        **terminal,
    }


def complete_closeout(
    *,
    track: str | Path,
    tracks: str | Path,
    ledger: str | Path,
    timeout_seconds: int,
    command_json: str | None = None,
) -> dict[str, Any]:
    root = canonical(track)
    tracks_path = canonical(tracks)
    ledger_path = canonical(ledger)
    conductor = root.parent.parent
    if os.path.normcase(str(tracks_path)) != os.path.normcase(
        str(conductor / "tracks.md")
    ) or os.path.normcase(str(ledger_path)) != os.path.normcase(
        str(conductor / "tracks-ledger.md")
    ):
        fail("closeout ledgers must be the track workspace Conductor ledgers")
    if timeout_seconds <= 0:
        fail("timeout-seconds must be positive")
    metadata_path = root / "metadata.json"
    plan_path = root / "plan.md"
    metadata = read_json(metadata_path)
    if not isinstance(metadata, dict):
        fail("metadata.json must be an object")
    existing = _already_complete(root, metadata)
    if existing is not None:
        return existing
    verify_completion_sync(root)
    stage7 = _stage7_report(root)
    if not tracks_path.is_file() or not ledger_path.is_file():
        fail("both Conductor ledgers are required")
    execution_logs = sorted(root.glob("execution-log-*.md"))
    if not execution_logs:
        fail("execution log is required before terminal closeout")
    execution_log = execution_logs[-1]

    bookkeeping_originals = {
        plan_path: plan_path.read_bytes(),
        metadata_path: metadata_path.read_bytes(),
        tracks_path: tracks_path.read_bytes(),
        ledger_path: ledger_path.read_bytes(),
    }
    anomaly_path = conductor / "logs" / "pipeline-anomalies.jsonl"
    anomaly_before = anomaly_path.read_bytes() if anomaly_path.is_file() else None
    before_snapshot = _snapshot(root)
    before_doc_logs = {path.name for path in root.glob("doc-update-log-*.md")}
    prompt = _stage9_prompt(root)
    command = _command_from_json(
        command_json, track=root, prompt=prompt
    ) or _default_command(root, prompt)
    outcome = run_dispatch_process(
        command, cwd=_workspace_root(root), timeout_seconds=timeout_seconds
    )
    after_snapshot = _snapshot(root)
    changed_keys = _changed_paths(before_snapshot, after_snapshot)
    changed_paths = [Path(key) for key in sorted(changed_keys)]
    disallowed: list[Path] = []
    changed_docs: list[Path] = []
    for path in changed_paths:
        if path == anomaly_path and _anomaly_append_only_ok(path, anomaly_before):
            continue
        if _allowed_documentation(path, root):
            changed_docs.append(path)
        else:
            disallowed.append(path)
    if any(path in bookkeeping_originals for path in disallowed):
        _restore_bookkeeping(bookkeeping_originals)
    if disallowed:
        fail(
            "Stage 9 modified prohibited paths: "
            + ", ".join(str(path) for path in disallowed)
        )
    if outcome["status"] != "success":
        fail(
            f"Stage 9 {outcome['status']}: {outcome['reason']}; "
            f"cleanup={outcome['cleanup']}"
        )
    parsed = _parse_stage9_response(outcome["stdout"])
    created_log = _new_doc_log(root, before_doc_logs)
    documentation_changes = [
        path for path in changed_docs if created_log is None or path != created_log
    ]
    stage9_log = _persist_stage9_evidence(
        root, parsed, documentation_changes, created_log
    )
    post_doc = _post_doc_phase_b(
        root,
        stage9_log=stage9_log,
        classification=parsed["classification"],
        changed_docs=documentation_changes,
    )

    # Phase B starts here. The doc-writer has returned and is no longer the
    # actor; only this orchestrator code may synchronize terminal state.
    current_plan = plan_path.read_text(encoding="utf-8")
    current_metadata = read_json(metadata_path)
    if not isinstance(current_metadata, dict):
        fail("metadata changed to a non-object before Phase B")
    current_metadata["status"] = "complete"
    current_metadata["phase"] = "complete"
    current_metadata["completed"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    progress = dict(current_metadata.get("progress") or {})
    progress.update(
        {
            "totalTasks": EXECUTABLE_TASKS,
            "completedTasks": EXECUTABLE_TASKS,
            "percentage": 100,
        }
    )
    current_metadata["progress"] = progress
    current_metadata["terminal_closeout"] = {
        "phase_b": "PASS",
        "timestamp": _utc_now(),
        "stage7_report": str(stage7),
        "stage9_artifact": str(stage9_log),
        "post_doc_validation": str(post_doc),
        "classification": parsed["classification"],
        "orchestrator_owned": True,
    }
    current_tracks = tracks_path.read_text(encoding="utf-8-sig")
    current_ledger = ledger_path.read_text(encoding="utf-8-sig")
    new_tracks, new_ledger = build_ledger_updates(
        track=root,
        tracks_text=current_tracks,
        ledger_text=current_ledger,
        metadata=current_metadata,
    )
    new_plan = _terminal_plan_text(
        current_plan, stage7=stage7, stage9=stage9_log, post_doc=post_doc
    )
    current_log = execution_log.read_text(encoding="utf-8")
    log_append = "\n".join(
        [
            "",
            f"## Terminal Phase B — {_utc_now()}",
            "",
            f"- Stage 7: `ready_to_close` — `{stage7}`",
            f"- Stage 9: `{parsed['classification']}` — `{stage9_log}`",
            f"- Post-doc validation: `{post_doc}`",
            "- Orchestrator Phase B: `PASS`",
            "- Metadata and both ledgers synchronized only after Phase B passed.",
            "",
        ]
    )
    metadata_text = json.dumps(
        current_metadata, indent=2, sort_keys=True, ensure_ascii=False
    ) + "\n"
    _atomic_multi_text(
        {
            plan_path: new_plan,
            metadata_path: metadata_text,
            tracks_path: new_tracks,
            ledger_path: new_ledger,
            execution_log: current_log.rstrip() + "\n" + log_append,
        }
    )
    return {
        "check": "terminal-closeout-action",
        "status": "PASS",
        "phase_b": "PASS",
        "stage7_report": str(stage7),
        "stage9_artifact": str(stage9_log),
        "post_doc_validation": str(post_doc),
        "classification": parsed["classification"],
        "orchestrator_owned": True,
        "metadata_complete_after_phase_b": True,
        "cleanup": outcome["cleanup"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dispatch Stage 9 and perform orchestrator-only terminal Phase B."
    )
    parser.add_argument("--track", required=True)
    parser.add_argument("--tracks", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--timeout-seconds", required=True, type=int)
    parser.add_argument(
        "--command-json",
        help="test-only disposable Stage 9 command override as JSON array or file",
    )
    args = parser.parse_args(argv)
    try:
        result = complete_closeout(
            track=args.track,
            tracks=args.tracks,
            ledger=args.ledger,
            timeout_seconds=args.timeout_seconds,
            command_json=args.command_json,
        )
        print(json_line(result))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        try:
            track_path = canonical(args.track)
            _append_anomaly(
                track_path.parent.parent,
                track=track_path.name,
                subagent=DOC_AGENT,
                detail=str(exc),
            )
        except (OSError, ToolchainError):
            pass
        print(
            json_line(
                {
                    "check": "terminal-closeout-action",
                    "status": "FAIL",
                    "error": str(exc),
                }
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
