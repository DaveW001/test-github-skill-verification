#!/usr/bin/env python3
"""Append execution evidence and synchronize the exact 17/8/25 counters."""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    ToolchainError,
    canonical,
    fail,
    json_line,
    read_json,
    write_json,
)


EXECUTABLE_TASKS = 17
READINESS_CHECKS = 8
TOTAL_CHECKBOXES = 25
CHECKBOX_RE = re.compile(r"^\s*-\s*\[([ xX~])\]\s*(.+?)\s*$")
RUN_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _clean_label(value: str) -> str:
    value = re.sub(r"\*\*", "", value)
    return value.strip()


def parse_plan_counts(plan_text: str) -> dict[str, Any]:
    """Return task/readiness counts, treating the named checklist separately."""
    in_readiness = False
    tasks: list[dict[str, Any]] = []
    readiness: list[dict[str, Any]] = []
    for line_number, line in enumerate(plan_text.splitlines(), start=1):
        if line.strip().lower() == "## execution readiness checklist":
            in_readiness = True
            continue
        if in_readiness and line.startswith("## ") and line.strip().lower() != "## execution readiness checklist":
            in_readiness = False
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        state, label = match.groups()
        record = {
            "line": line_number,
            "state": "complete" if state.lower() == "x" else "in_progress" if state == "~" else "pending",
            "label": _clean_label(label),
        }
        (readiness if in_readiness else tasks).append(record)
    return {
        "tasks": tasks,
        "readiness": readiness,
        "task_count": len(tasks),
        "readiness_count": len(readiness),
        "checkbox_count": len(tasks) + len(readiness),
        "completed_tasks": sum(item["state"] == "complete" for item in tasks),
        "completed_readiness": sum(
            item["state"] == "complete" for item in readiness
        ),
    }


def require_exact_counts(counts: dict[str, Any]) -> None:
    actual = (
        counts["task_count"],
        counts["readiness_count"],
        counts["checkbox_count"],
    )
    expected = (EXECUTABLE_TASKS, READINESS_CHECKS, TOTAL_CHECKBOXES)
    if actual != expected:
        fail(
            "plan count mismatch: expected "
            f"{EXECUTABLE_TASKS}/{READINESS_CHECKS}/{TOTAL_CHECKBOXES}, "
            f"got {actual[0]}/{actual[1]}/{actual[2]}"
        )


def _evidence_summary(track: Path, execution_log: Path) -> dict[str, Any]:
    artifacts: list[str] = []
    unverified: list[str] = []
    retry_lines: list[str] = []
    deviation_lines: list[str] = []
    for path in sorted(track.rglob("*")):
        if not path.is_file() or path == execution_log:
            continue
        if path.suffix.lower() not in {".json", ".md", ".jsonl"}:
            continue
        artifacts.append(str(path.relative_to(track)))
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            lowered = stripped.lower()
            if "unverified" in lowered and len(unverified) < 100:
                unverified.append(f"{path.name}: {stripped[:300]}")
            if "retry" in lowered and len(retry_lines) < 100:
                retry_lines.append(f"{path.name}: {stripped[:300]}")
            if (
                "deviation" in lowered or "skipped" in lowered
            ) and len(deviation_lines) < 100:
                deviation_lines.append(f"{path.name}: {stripped[:300]}")
    return {
        "artifacts": artifacts,
        "unverified": unverified,
        "retries": retry_lines,
        "deviations_and_skips": deviation_lines,
    }


def _append_only(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(f".{path.name}.append.lock")
    descriptor: int | None = None
    try:
        descriptor = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(descriptor)
        descriptor = None
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        fail(f"execution log append lock is already held: {lock}")
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def sync_execution(track: str | Path, run_date: str) -> dict[str, Any]:
    if not RUN_DATE_RE.fullmatch(run_date):
        fail("run-date must use YYYY-MM-DD")
    # Validate the date, not merely the shape.
    datetime.strptime(run_date, "%Y-%m-%d")
    root = canonical(track)
    plan_path = root / "plan.md"
    metadata_path = root / "metadata.json"
    if not plan_path.is_file() or not metadata_path.is_file():
        fail("plan.md and metadata.json are required")
    plan_text = plan_path.read_text(encoding="utf-8")
    counts = parse_plan_counts(plan_text)
    require_exact_counts(counts)
    metadata = read_json(metadata_path)
    if not isinstance(metadata, dict):
        fail("metadata.json must be an object")
    if metadata.get("trackId") not in {None, root.name} and metadata.get(
        "track_id"
    ) not in {None, root.name}:
        fail("metadata track identity does not match track folder")

    log_path = root / f"execution-log-{run_date}.md"
    evidence = _evidence_summary(root, log_path)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    model = (
        metadata.get("execution_model")
        or metadata.get("executor_model")
        or metadata.get("assignedTo")
        or "not-recorded"
    )
    lines = [
        "",
        f"## Execution synchronization — {timestamp}",
        "",
        f"- Track: `{root.name}`",
        f"- Run date: `{run_date}`",
        f"- Executor/model evidence: `{model}`",
        f"- Executable tasks: {counts['completed_tasks']}/{EXECUTABLE_TASKS}",
        f"- Readiness checks: {counts['completed_readiness']}/{READINESS_CHECKS}",
        f"- Total checkboxes: {TOTAL_CHECKBOXES}",
        f"- Pipeline decision: `{metadata.get('pipeline_mode', 'not-recorded')}` / `{metadata.get('pipeline_path', 'not-recorded')}`",
        "- External/destructive actions: none recorded in the inspected track evidence.",
        "",
        "### Task results",
        "",
    ]
    for task in counts["tasks"]:
        lines.append(
            f"- Line {task['line']}: `{task['state']}` — {task['label']}"
        )
    lines.extend(["", "### Evidence inventory", ""])
    for artifact in evidence["artifacts"]:
        lines.append(f"- `{artifact}`")
    if not evidence["artifacts"]:
        lines.append("- None recorded.")
    lines.extend(["", "### Deviations, skips, and retries", ""])
    combined = evidence["deviations_and_skips"] + evidence["retries"]
    lines.extend(f"- {item}" for item in combined)
    if not combined:
        lines.append("- None recorded.")
    lines.extend(["", "### Unverified items", ""])
    lines.extend(f"- {item}" for item in evidence["unverified"])
    if not evidence["unverified"]:
        lines.append("- None recorded.")
    lines.extend(["", "### Backups and edits", ""])
    backup_artifacts = [
        item
        for item in evidence["artifacts"]
        if "backup" in item.lower() or "change-manifest" in item.lower()
    ]
    lines.extend(f"- `{item}`" for item in backup_artifacts)
    if not backup_artifacts:
        lines.append("- No backup/change artifact was present at synchronization.")
    lines.append("")
    _append_only(log_path, "\n".join(lines))

    completed = counts["completed_tasks"]
    progress = dict(metadata.get("progress") or {})
    progress.update(
        {
            "totalTasks": EXECUTABLE_TASKS,
            "completedTasks": completed,
            "percentage": int((completed * 100) / EXECUTABLE_TASKS),
        }
    )
    metadata["progress"] = progress
    metadata["readiness_check_count"] = READINESS_CHECKS
    metadata["total_checkbox_count"] = TOTAL_CHECKBOXES
    metadata["execution_sync"] = {
        "timestamp": timestamp,
        "run_date": run_date,
        "tasks": EXECUTABLE_TASKS,
        "completed_tasks": completed,
        "readiness": READINESS_CHECKS,
        "completed_readiness": counts["completed_readiness"],
        "checkboxes": TOTAL_CHECKBOXES,
        "log": str(log_path),
        "append_only": True,
    }
    write_json(metadata_path, metadata, root=root)
    return {
        "check": "execution-sync",
        "status": "PASS",
        "tasks": EXECUTABLE_TASKS,
        "completed_tasks": completed,
        "readiness": READINESS_CHECKS,
        "checkboxes": TOTAL_CHECKBOXES,
        "append_only": True,
        "log": str(log_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Append execution evidence and synchronize exact task counts."
    )
    parser.add_argument("--track", required=True)
    parser.add_argument("--run-date", required=True)
    args = parser.parse_args(argv)
    try:
        result = sync_execution(args.track, args.run_date)
        print(json_line(result))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json_line(
                {"check": "execution-sync", "status": "FAIL", "error": str(exc)}
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
