#!/usr/bin/env python3
"""Run osgrep with structured logging and optional stale-process cleanup."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(command: list[str], timeout: int | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def cleanup_stale_windows() -> dict[str, object]:
    result: dict[str, object] = {"attempted": False, "killed": False, "details": "not-windows"}
    if os.name != "nt":
        return result

    result["attempted"] = True
    cmd = ["taskkill", "/F", "/T", "/IM", "osgrep-nodejs-helper.exe"]
    code, out, err = run_cmd(cmd)
    result["killed"] = code == 0
    result["details"] = (out or err).strip()
    result["exit_code"] = code
    return result


def snapshot_windows(label: str, output_dir: Path, cwd: str) -> None:
    if os.name != "nt":
        return
    script = Path("scripts/utils/osgrep_process_snapshot.ps1")
    if not script.exists():
        return
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-Label",
            label,
            "-OutputDir",
            str(output_dir),
            "-TargetCwd",
            cwd,
        ],
        capture_output=True,
        text=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run osgrep with reproducible logs.")
    parser.add_argument("--cwd", default=os.getcwd(), help="Working directory to run osgrep from")
    parser.add_argument("--label", default="run", help="Label for output folder")
    parser.add_argument("--timeout", type=int, default=20, help="Timeout in seconds")
    parser.add_argument("--cleanup-stale", action="store_true", help="Kill stale osgrep helper workers before launch")
    parser.add_argument("--", dest="sep", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command passed to osgrep")
    args = parser.parse_args()

    command_args = args.command
    if command_args and command_args[0] == "--":
        command_args = command_args[1:]

    if not command_args:
        command_args = ["--help"]

    out_root = Path("logs/osgrep-debug")
    out_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = out_root / f"{stamp}-{args.label}"
    out_dir.mkdir(parents=True, exist_ok=True)

    record: dict[str, object] = {
        "label": args.label,
        "started": now_iso(),
        "cwd": args.cwd,
        "command": ["osgrep", *command_args],
        "timeout_seconds": args.timeout,
        "platform": os.name,
        "cleanup": {},
    }

    if args.cleanup_stale:
        record["cleanup"] = cleanup_stale_windows()

    osgrep_exe = shutil.which("osgrep") or shutil.which("osgrep.cmd") or "osgrep"
    if not Path(args.cwd).exists():
        record["exit_code"] = None
        record["stdout"] = ""
        record["stderr"] = f"Working directory does not exist: {args.cwd}"
        record["timed_out"] = False
        record["duration_seconds"] = 0
        record["finished"] = now_iso()
        record["command_text"] = shlex.join([osgrep_exe, *command_args])
        out_path = out_dir / "result.json"
        out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(f"Saved debug log: {out_path}")
        return 2

    run_start = time.time()
    try:
        proc = subprocess.run(
            [osgrep_exe, *command_args],
            cwd=args.cwd,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
        record["exit_code"] = proc.returncode
        record["stdout"] = proc.stdout
        record["stderr"] = proc.stderr
        record["timed_out"] = False
    except subprocess.TimeoutExpired as exc:
        record["exit_code"] = None
        record["stdout"] = exc.stdout or ""
        record["stderr"] = exc.stderr or ""
        record["timed_out"] = True
        snapshot_windows(args.label, out_dir, args.cwd)

    record["duration_seconds"] = round(time.time() - run_start, 3)
    record["finished"] = now_iso()
    record["command_text"] = shlex.join([osgrep_exe, *command_args])

    out_path = out_dir / "result.json"
    out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    print(f"Saved debug log: {out_path}")
    if record.get("timed_out"):
        return 124
    exit_code = record.get("exit_code")
    if isinstance(exit_code, int):
        return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
