#!/usr/bin/env python3
"""Strict-alternation Stage 7 dispatcher with success-only state mutation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
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
    write_text,
)
from sync_execution import (
    EXECUTABLE_TASKS,
    READINESS_CHECKS,
    TOTAL_CHECKBOXES,
    parse_plan_counts,
    require_exact_counts,
)


VALIDATORS: dict[str, dict[str, str | None]] = {
    "luna": {
        "agent": "conductor-track-validator",
        "model": "openai/gpt-5.6-luna",
        "variant": "high",
        "next": "m3",
    },
    "m3": {
        "agent": "conductor-track-validator-m3",
        "model": "opencode-go/minimax-m3",
        "variant": None,
        "next": "luna",
    },
}
ANOMALY_KEYS = {
    "ts",
    "track",
    "stage",
    "subagent",
    "type",
    "severity",
    "detail",
}
MAX_CORRECTION_CYCLES = 5


class ExclusiveFileLock:
    def __init__(self, target: Path) -> None:
        self.path = target.with_name(f".{target.name}.lock")
        self.fd: int | None = None

    def __enter__(self) -> "ExclusiveFileLock":
        try:
            self.fd = os.open(
                str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY
            )
            os.write(self.fd, f"{os.getpid()}\n".encode("ascii"))
            os.fsync(self.fd)
            return self
        except FileExistsError:
            fail(f"exclusive state lock is already held: {self.path}")
        return self

    def __exit__(self, *_args: object) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%SZ")


def select_validator(alternation: str | Path) -> tuple[str, dict[str, Any] | None]:
    """Select solely from last_used; persisted next is deliberately ignored."""
    path = canonical(alternation)
    if not path.exists():
        return "luna", None
    state = read_json(path)
    if not isinstance(state, dict):
        fail("validator alternation state must be an object")
    last_used = state.get("last_used")
    if last_used == "luna":
        return "m3", state
    if last_used == "m3":
        return "luna", state
    fail(f"unknown validator last_used identity: {last_used!r}")
    return "", state


def _ledger_sync(track: Path, metadata: dict[str, Any]) -> None:
    conductor = track.parent.parent
    tracks_path = conductor / "tracks.md"
    ledger_path = conductor / "tracks-ledger.md"
    if not tracks_path.is_file() or not ledger_path.is_file():
        fail("both Conductor ledgers are required before Stage 7")
    track_id = track.name
    status = metadata.get("status")
    progress = metadata.get("progress")
    if not isinstance(progress, dict):
        fail("metadata progress is missing")
    completed = progress.get("completedTasks")
    total = progress.get("totalTasks")
    if (completed, total) != (EXECUTABLE_TASKS, EXECUTABLE_TASKS):
        fail(
            "Stage 7 requires metadata progress exactly "
            f"{EXECUTABLE_TASKS}/{EXECUTABLE_TASKS}"
        )
    table_lines = [
        line
        for line in tracks_path.read_text(encoding="utf-8-sig").splitlines()
        if re.match(rf"^\|\s*{re.escape(track_id)}\s*\|", line)
    ]
    ledger_lines = [
        line
        for line in ledger_path.read_text(encoding="utf-8-sig").splitlines()
        if re.match(rf"^-\s*\[{re.escape(track_id)}\]\(", line)
    ]
    if len(table_lines) != 1 or len(ledger_lines) != 1:
        fail("Stage 7 requires exactly one entry in each Conductor ledger")
    if f"{EXECUTABLE_TASKS}/{EXECUTABLE_TASKS}" not in table_lines[0]:
        fail("tracks.md progress does not match metadata 17/17")
    if f"{EXECUTABLE_TASKS}/{EXECUTABLE_TASKS}" not in ledger_lines[0]:
        fail("tracks-ledger.md progress does not match metadata 17/17")
    if not isinstance(status, str) or status not in table_lines[0]:
        fail("tracks.md status does not match metadata")
    if f"Phase: {status} " not in ledger_lines[0]:
        fail("tracks-ledger.md status does not match metadata")


def verify_completion_sync(track: str | Path) -> dict[str, Any]:
    root = canonical(track)
    plan_path = root / "plan.md"
    metadata_path = root / "metadata.json"
    if not plan_path.is_file() or not metadata_path.is_file():
        fail("plan.md and metadata.json are required before Stage 7")
    counts = parse_plan_counts(plan_path.read_text(encoding="utf-8"))
    require_exact_counts(counts)
    if counts["completed_tasks"] != EXECUTABLE_TASKS:
        fail(
            f"Stage 7 requires all {EXECUTABLE_TASKS} executable tasks complete; "
            f"found {counts['completed_tasks']}"
        )
    metadata = read_json(metadata_path)
    if not isinstance(metadata, dict):
        fail("metadata.json must be an object")
    sync = metadata.get("execution_sync")
    if not isinstance(sync, dict) or (
        sync.get("tasks"),
        sync.get("readiness"),
        sync.get("checkboxes"),
    ) != (EXECUTABLE_TASKS, READINESS_CHECKS, TOTAL_CHECKBOXES):
        fail("metadata execution_sync does not prove exact 17/8/25 counts")
    _ledger_sync(root, metadata)
    return {
        "tasks": EXECUTABLE_TASKS,
        "completed_tasks": counts["completed_tasks"],
        "readiness": READINESS_CHECKS,
        "checkboxes": TOTAL_CHECKBOXES,
    }


def guard_correction_budget(track: str | Path) -> None:
    """Fail closed on the persisted five-cycle and anti-runaway limits."""
    root = canonical(track)
    candidates = (
        root / "validation-cycle-ledger.json",
        root / "validation-cycles.json",
    )
    ledger = next((path for path in candidates if path.is_file()), None)
    if ledger is None:
        return
    payload = read_json(ledger)
    cycles = payload.get("cycles") if isinstance(payload, dict) else payload
    if not isinstance(cycles, list) or not all(
        isinstance(item, dict) for item in cycles
    ):
        fail(f"malformed validation correction ledger: {ledger}")
    if len(cycles) >= MAX_CORRECTION_CYCLES:
        fail(f"validation correction cap reached ({MAX_CORRECTION_CYCLES})")
    if len(cycles) >= 2:
        previous, current = cycles[-2:]
        previous_signature = previous.get("blocker_signature")
        current_signature = current.get("blocker_signature")
        if (
            isinstance(previous_signature, str)
            and previous_signature
            and previous_signature == current_signature
        ):
            fail("anti-runaway stop: blocker signature repeated consecutively")
        no_progress = 0
        for item in (previous, current):
            resolved = item.get("resolved_blockers", item.get("resolved", []))
            if resolved in ([], 0, None, False):
                no_progress += 1
        if no_progress == 2:
            fail("anti-runaway stop: two consecutive cycles resolved no blocker")


def _terminate_owned(process: subprocess.Popen[str]) -> str:
    try:
        if process.poll() is not None:
            return "already-exited"
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
        else:
            os.killpg(process.pid, signal.SIGKILL)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        return "owned-process-terminated"
    except (OSError, subprocess.SubprocessError):
        try:
            process.kill()
            process.wait(timeout=10)
            return "owned-process-terminated"
        except (OSError, subprocess.SubprocessError):
            return "owned-process-cleanup-failed"


def run_dispatch_process(
    command: list[str], *, cwd: Path, timeout_seconds: int
) -> dict[str, Any]:
    if timeout_seconds <= 0:
        fail("timeout-seconds must be positive")
    if not command or not all(isinstance(part, str) and part for part in command):
        fail("dispatch command must be a nonempty string array")
    kwargs: dict[str, Any] = {
        "cwd": str(cwd),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True
    try:
        process = subprocess.Popen(command, **kwargs)
    except OSError as exc:
        return {
            "status": "failed",
            "reason": f"launch failure: {exc}",
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "cleanup": "not-started",
        }
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        cleanup = _terminate_owned(process)
        stdout, stderr = process.communicate()
        return {
            "status": "timeout",
            "reason": "owned validator dispatch timed out",
            "returncode": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "cleanup": cleanup,
        }
    return {
        "status": "success" if process.returncode == 0 else "failed",
        "reason": "process exited zero"
        if process.returncode == 0
        else "validator dispatch returned nonzero",
        "returncode": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "cleanup": "not-needed",
    }


def _stage7_prompt(track: Path, selected: str) -> str:
    details = VALIDATORS[selected]
    variant = details["variant"] or "default"
    return (
        "Run Conductor Stage 7 Phase A validation for the track at "
        f"{track}. Selected agent={details['agent']}; model={details['model']}; "
        f"variant={variant}. Read spec.md, plan.md, metadata.json, both workspace "
        "ledgers, execution/change logs, inventory, rubric packets, backups, diffs, "
        "loading evidence, and portfolio artifacts. Verify global-first ordering, "
        "17/17 executor tasks, exact 17/8/25 bookkeeping, zero unresolved blockers, "
        "and Stage 9 readiness. Do not require a Stage 9 artifact yet. Do not edit "
        "deliverables or bookkeeping. Return a structured Markdown report with "
        "headings Closeout Verdict, Evidence Checked, Mismatches Found, Required "
        "Fixes Before Close, and Final Recommendation. A ready report must say "
        "'Ready to close' and 'No fixes required.' Keep every command bounded and "
        "return promptly on a blocker."
    )


def _default_command(track: Path, selected: str, prompt: str) -> list[str]:
    executable = shutil.which("opencode")
    if executable is None:
        return ["opencode", "run", prompt]
    details = VALIDATORS[selected]
    command = [
        executable,
        "run",
        "--agent",
        str(details["agent"]),
        "--model",
        str(details["model"]),
    ]
    if details["variant"]:
        command.extend(["--variant", str(details["variant"])])
    command.extend(
        [
            "--title",
            f"Stage 7 validation {track.name}",
            "--",
            prompt,
        ]
    )
    return command


def _command_from_json(
    raw: str | None, *, track: Path, selected: str, prompt: str
) -> list[str] | None:
    if raw is None:
        raw = os.environ.get("CONDUCTOR_STAGE7_COMMAND_JSON")
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
        fail("Stage 7 command override must be a nonempty JSON string array")
    details = VALIDATORS[selected]
    replacements = {
        "{track}": str(track),
        "{agent}": str(details["agent"]),
        "{model}": str(details["model"]),
        "{variant}": str(details["variant"] or ""),
        "{prompt}": prompt,
    }
    expanded: list[str] = []
    for part in command:
        value = part
        for marker, replacement in replacements.items():
            value = value.replace(marker, replacement)
        expanded.append(value)
    return expanded


def _extract_json_report(text: str) -> tuple[str, dict[str, Any] | None]:
    stripped = text.strip()
    if not stripped:
        return "", None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return text, None
    if not isinstance(payload, dict):
        return text, None
    if isinstance(payload.get("report"), str):
        return payload["report"], payload
    return text, payload


def validate_stage7_report(text: str, selected: str) -> dict[str, Any]:
    report, payload = _extract_json_report(text)
    if not report.strip():
        fail("validator returned an empty response")
    details = VALIDATORS[selected]
    lowered = report.lower()
    if payload is not None and payload.get("verdict") == "ready_to_close":
        validator = payload.get("validator")
        blockers = payload.get("blockers", [])
        if validator != details["agent"]:
            fail("structured report validator identity does not match dispatch")
        if blockers not in ([], None, 0):
            fail("structured report contains blockers")
        for field in (
            "evidence_checked",
            "mismatches",
            "required_fixes",
            "final_recommendation",
        ):
            if field not in payload:
                fail(f"structured report is missing {field}")
        return {
            "report": report,
            "verdict": "ready_to_close",
            "validator": details["agent"],
            "model": details["model"],
        }
    if str(details["agent"]).lower() not in lowered:
        fail("validator report does not identify the selected agent")
    required_headings = (
        "closeout verdict",
        "evidence checked",
        "mismatches found",
        "required fixes before close",
        "final recommendation",
    )
    missing = [heading for heading in required_headings if heading not in lowered]
    if missing:
        fail("malformed validator report; missing sections: " + ", ".join(missing))
    if "not ready to close" in lowered or not re.search(
        r"\bready[_ ]to[_ ]close\b", lowered
    ):
        fail("validator report does not contain a ready-to-close verdict")
    required_section = lowered.split("required fixes before close", 1)[1]
    required_section = required_section.split("final recommendation", 1)[0]
    if "no fixes required" not in required_section:
        fail("validator report does not prove zero required fixes")
    return {
        "report": report,
        "verdict": "ready_to_close",
        "validator": details["agent"],
        "model": details["model"],
    }


def _append_anomaly(
    conductor: Path, *, track: str, subagent: str, detail: str
) -> None:
    path = conductor / "logs" / "pipeline-anomalies.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": _utc_now(),
        "track": track,
        "stage": "stage-7",
        "subagent": subagent,
        "type": "tool-error",
        "severity": "error",
        "detail": detail[:500],
    }
    if set(payload) != ANOMALY_KEYS:
        fail("internal anomaly schema violation")
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _write_anomaly_summary(track: Path) -> Path:
    source = track.parent.parent / "logs" / "pipeline-anomalies.jsonl"
    matching: list[dict[str, Any]] = []
    if source.is_file():
        for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and payload.get("track") == track.name:
                matching.append(payload)
    run_date = (
        read_json(track / "metadata.json").get("created")
        if (track / "metadata.json").is_file()
        else None
    ) or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = track / f"anomaly-summary-{run_date}.md"
    lines = [
        "# Pipeline Anomaly Summary",
        "",
        f"- Track: `{track.name}`",
        f"- Source: `{source}`",
        f"- Matching records: {len(matching)}",
        "",
    ]
    for item in matching:
        lines.append(
            f"- `{item.get('ts')}` `{item.get('severity')}` "
            f"`{item.get('type')}` — {item.get('detail')}"
        )
    if not matching:
        lines.append("- No anomalies recorded for this track.")
    write_text(path, "\n".join(lines) + "\n", root=track)
    return path


def _write_blocker(track: Path, *, subagent: str, detail: str) -> Path:
    signature = hashlib.sha256(
        " ".join(detail.lower().split()).encode("utf-8")
    ).hexdigest()[:16]
    path = track / f"validation-blockers-{_timestamp_slug()}.md"
    lines = [
        "# Stage 7 Validation Blocker",
        "",
        f"- Timestamp: `{_utc_now()}`",
        f"- Validator: `{subagent}`",
        f"- Stable blocker signature: `{signature}`",
        f"- Detail: {detail}",
        "- Alternation state: unchanged; dispatch did not reach validated success.",
        "- Resume point: correct the concrete blocker, preserve the cycle budget, and rerun Gate F.3.",
        "",
    ]
    write_text(path, "\n".join(lines), root=track)
    return path


def _persist_success_state(
    path: Path,
    *,
    selected: str,
    original: dict[str, Any] | None,
    track: str,
) -> None:
    state = dict(original or {})
    state.setdefault(
        "purpose",
        "Strict-alternation selector for Stage 7 paired validators.",
    )
    state.setdefault(
        "rule",
        "Read last_used; invoke the other validator; flip only after success.",
    )
    state["last_used"] = selected
    state["next"] = VALIDATORS[selected]["next"]
    state["agents"] = {
        "m3": "conductor-track-validator-m3 (opencode-go/minimax-m3)",
        "luna": "conductor-track-validator (openai/gpt-5.6-luna, variant high)",
    }
    state["last_successful_track"] = track
    state["last_successful_dispatch_utc"] = _utc_now()
    state["state_file"] = str(path)
    write_json(path, state)


def dispatch_stage7(
    *,
    track: str | Path,
    alternation: str | Path,
    timeout_seconds: int,
    command_json: str | None = None,
) -> dict[str, Any]:
    root = canonical(track)
    alternation_path = canonical(alternation)
    if timeout_seconds <= 0:
        fail("timeout-seconds must be positive")
    if alternation_path.parent != root.parent.parent:
        fail("alternation state must be in the track workspace .conductor folder")
    conductor = root.parent.parent
    selected_for_error = "unknown"
    try:
        verify_completion_sync(root)
        guard_correction_budget(root)
        with ExclusiveFileLock(alternation_path):
            selected, original_state = select_validator(alternation_path)
            selected_for_error = str(VALIDATORS[selected]["agent"])
            prompt = _stage7_prompt(root, selected)
            command = _command_from_json(
                command_json, track=root, selected=selected, prompt=prompt
            ) or _default_command(root, selected, prompt)
            outcome = run_dispatch_process(
                command, cwd=root.parent.parent.parent, timeout_seconds=timeout_seconds
            )
            if outcome["status"] != "success":
                fail(
                    f"Stage 7 {outcome['status']}: {outcome['reason']}; "
                    f"cleanup={outcome['cleanup']}"
                )
            if not outcome["stdout"].strip():
                fail("Stage 7 dispatch returned an empty response")
            validated = validate_stage7_report(outcome["stdout"], selected)
            report_path = root / f"validation-report-{_timestamp_slug()}.md"
            normalized = (
                f"**Validator identity:** `{validated['validator']}`\n\n"
                f"**Validator model:** `{validated['model']}`\n\n"
                + validated["report"].strip()
                + "\n"
            )
            write_text(report_path, normalized, root=root)
            _persist_success_state(
                alternation_path,
                selected=selected,
                original=original_state,
                track=root.name,
            )
            summary = _write_anomaly_summary(root)
            return {
                "check": "stage7-dispatch",
                "status": "PASS",
                "verdict": "ready_to_close",
                "validator": validated["validator"],
                "model": validated["model"],
                "alternation": "PASS",
                "state_flipped_after_success": True,
                "report": str(report_path),
                "anomaly_summary": str(summary),
                "cleanup": outcome["cleanup"],
            }
    except (
        ToolchainError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        try:
            _append_anomaly(
                conductor,
                track=root.name,
                subagent=selected_for_error,
                detail=str(exc),
            )
        except (OSError, ToolchainError):
            pass
        try:
            _write_blocker(root, subagent=selected_for_error, detail=str(exc))
        except (OSError, ToolchainError):
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dispatch strict-alternation independent Stage 7 validation."
    )
    parser.add_argument("--track", required=True)
    parser.add_argument("--alternation", required=True)
    parser.add_argument("--timeout-seconds", required=True, type=int)
    parser.add_argument(
        "--command-json",
        help="test-only disposable command override as JSON array or JSON file",
    )
    args = parser.parse_args(argv)
    try:
        result = dispatch_stage7(
            track=args.track,
            alternation=args.alternation,
            timeout_seconds=args.timeout_seconds,
            command_json=args.command_json,
        )
        print(json_line(result))
        return 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json_line(
                {"check": "stage7-dispatch", "status": "FAIL", "error": str(exc)}
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
