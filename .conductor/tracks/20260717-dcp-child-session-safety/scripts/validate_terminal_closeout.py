#!/usr/bin/env python3
"""Terminal Phase-B closeout gate for a completed Conductor track.

This gate runs after Stage 9.  It deliberately treats explicitly deferred
tasks as acceptable, but requires every non-deferred task, required artifact,
ledger row, and final metadata field to agree before printing READY_TO_CLOSE.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TRACK_ID = "20260717-dcp-child-session-safety"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        fail(errors, f"missing: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track-root", required=True)
    args = parser.parse_args()

    track_root = Path(args.track_root).resolve()
    errors: list[str] = []
    if track_root.name != TRACK_ID:
        fail(errors, f"unexpected track id: {track_root.name}")

    workspace_root = track_root.parent.parent.parent
    metadata_path = track_root / "metadata.json"
    plan_path = track_root / "plan.md"
    tracks_path = workspace_root / ".conductor" / "tracks.md"
    ledger_path = workspace_root / ".conductor" / "tracks-ledger.md"

    metadata_text = read_text(metadata_path, errors)
    plan_text = read_text(plan_path, errors)
    tracks_text = read_text(tracks_path, errors)
    ledger_text = read_text(ledger_path, errors)

    metadata: dict = {}
    if metadata_text:
        try:
            metadata = json.loads(metadata_text)
        except json.JSONDecodeError as exc:
            fail(errors, f"metadata.json is invalid JSON: {exc}")

    task_states = re.findall(r"^\s*- \[([x~ ])\] \*\*", plan_text, re.MULTILINE)
    counts = {"x": task_states.count("x"), "~": task_states.count("~"), " ": task_states.count(" ")}
    if counts != {"x": 27, "~": 2, " ": 0}:
        fail(errors, f"plan task counts are {counts}, want x=27, ~=2, open=0")
    if re.search(r"^\s*- \[~\] \*\*F\.4", plan_text, re.MULTILINE):
        fail(errors, "F.4 is still pending")
    if "[PENDING STAGE 9]" in plan_text:
        fail(errors, "plan still contains a Stage 9 pending marker")
    for task in ("0.1", "5.2"):
        if not re.search(rf"\*\*{re.escape(task)}[^\n]*\[DEFERRED", plan_text):
            fail(errors, f"explicit deferral for {task} is missing")

    progress = metadata.get("progress", {})
    expected_progress = {
        "totalTasks": 29,
        "completedTasks": 27,
        "percentage": 93,
        "deferredTasks": 2,
        "pendingTasks": 0,
        "nonDeferred": 27,
    }
    for key, expected in expected_progress.items():
        if progress.get(key) != expected:
            fail(errors, f"metadata.progress.{key}={progress.get(key)!r}, want {expected!r}")
    if metadata.get("status") != "complete":
        fail(errors, f"metadata.status={metadata.get('status')!r}, want 'complete'")
    if not metadata.get("completed"):
        fail(errors, "metadata.completed is empty")
    if metadata.get("phase") != "terminal closeout complete":
        fail(errors, f"metadata.phase={metadata.get('phase')!r}, want terminal closeout complete")

    if len(re.findall(r"^\|\s*" + re.escape(TRACK_ID) + r"\s", tracks_text, re.MULTILINE)) != 1:
        fail(errors, "tracks.md does not contain exactly one canonical row")
    if len(re.findall(r"^-\s*\[" + re.escape(TRACK_ID) + r"\]", ledger_text, re.MULTILINE)) != 1:
        fail(errors, "tracks-ledger.md does not contain exactly one canonical bullet")
    for label, text in (("tracks.md", tracks_text), ("tracks-ledger.md", ledger_text)):
        row = next((line for line in text.splitlines() if TRACK_ID in line), "")
        if "complete" not in row.lower() or "27/29" not in row:
            fail(errors, f"{label} row is not synchronized to complete 27/29 state")

    doc_logs = sorted(track_root.glob("doc-update-log-*.md"))
    if not doc_logs:
        fail(errors, "Stage 9 doc-update-log-*.md is missing")
    post_doc = sorted(track_root.glob("post-doc-validation-*.md"))
    if not post_doc:
        fail(errors, "mandatory post-doc-validation-*.md is missing")
    else:
        post_doc_text = post_doc[-1].read_text(encoding="utf-8").lower()
        if not re.search(r"status\W+pass", post_doc_text) or "contract-affecting" not in post_doc_text:
            fail(errors, "latest post-doc validation is not a PASS contract-affecting report")

    required_files = ("handover.md", "validation-matrix.md")
    for name in required_files:
        read_text(track_root / name, errors)
    execution_logs = sorted(track_root.glob("execution-log-*.md"))
    if not execution_logs:
        fail(errors, "execution-log-*.md is missing")
    elif "terminal closeout" not in execution_logs[-1].read_text(encoding="utf-8").lower():
        fail(errors, "latest execution log does not record terminal closeout")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"TERMINAL_CLOSEOUT_BLOCKED ({len(errors)} failure(s))")
        return 1

    print("READY_TO_CLOSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
