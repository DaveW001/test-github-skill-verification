#!/usr/bin/env python3
"""Bounded command runner for the top-skills-agents-review track.

Wraps every Python/PowerShell/Git/OpenCode command in a hard timeout, captures
stdout/stderr, terminates the child process tree on timeout, redacts output
before persistence, and returns exit code 124 on timeout.

Usage:
    python run_bounded.py --timeout-seconds N -- <child> [child args...]

Exit codes:
    0            child exited 0 and output was written
    <child code> child exited nonzero (output written)
    124          timeout
    2            usage / wrapper error
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


# --- Redaction ---------------------------------------------------------------

# Match common long hex/base64 token-like runs, bare Bearer tokens, and inline
# api_key/secret assignments. Conservative: these never remove legitimate
# aggregate counts or names we care about.
_SECRET_PATTERNS = [
    re.compile(r"(?i)(sk-[A-Za-z0-9_\-]{16,})"),
    re.compile(r"(?i)(Bearer\s+[A-Za-z0-9_\-\.]{16,})"),
    re.compile(r"(?i)((?:api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]{8,})"),
    re.compile(r"(?i)(AIza[0-9A-Za-z_\-]{20,})"),
    re.compile(r"(?i)(gh[pousr]_[A-Za-z0-9]{16,})"),
    re.compile(r"(?i)(xox[baprs]-[A-Za-z0-9\-]{10,})"),
]


def _redact(text: str) -> str:
    if not text:
        return text
    red = text
    for pat in _SECRET_PATTERNS:
        red = pat.sub("[REDACTED]", red)
    return red


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="run_bounded.py",
        description="Run a child command with a hard timeout and output capture.",
        add_help=True,
    )
    ap.add_argument(
        "--timeout-seconds",
        type=float,
        required=True,
        help="Hard timeout in seconds for the child process.",
    )
    ap.add_argument(
        "--redact-output",
        choices=["true", "false"],
        default="true",
        help="Whether to redact captured output (default true).",
    )
    ap.add_argument(
        "--record-file",
        default="",
        help="Optional path to write a JSON record of the invocation result.",
    )
    ap.add_argument(
        "child",
        nargs=argparse.REMAINDER,
        help="Child command (use a literal '--' separator before the child).",
    )
    args = ap.parse_args()

    # Drop a leading '--' separator if present.
    child = list(args.child)
    if child and child[0] == "--":
        child = child[1:]
    if not child:
        sys.stderr.write("run_bounded.py: no child command supplied\n")
        return 2

    timeout = args.timeout_seconds
    redact_enabled = args.redact_output == "true"

    start_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        proc = subprocess.run(
            child,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        rc = proc.returncode
        out = proc.stdout or ""
        err = proc.stderr or ""
    except subprocess.TimeoutExpired as e:
        # Process tree termination is handled by subprocess for the main child;
        # ensure no lingering handle.
        rc = 124
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        if isinstance(e.stdout, bytes) and e.stdout:
            out = e.stdout.decode("utf-8", "replace")
        err = "run_bounded.py: TIMEOUT after {0}s running {1}".format(timeout, child)
        try:
            err += "\n" + (e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or ""))
        except Exception:
            pass
    except FileNotFoundError as e:
        sys.stderr.write("run_bounded.py: child not found: {0}\n".format(e))
        return 2
    except Exception as e:
        sys.stderr.write("run_bounded.py: error launching child: {0}\n".format(e))
        return 2

    end_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if redact_enabled:
        out = _redact(out)
        err = _redact(err)

    # Write to our own stdout/stderr so callers see the (redacted) child output.
    sys.stdout.write(out)
    if err:
        sys.stderr.write(err)

    if args.record_file:
        import json

        record = {
            "start_utc": start_iso,
            "end_utc": end_iso,
            "child": child,
            "timeout_seconds": timeout,
            "exit_code": rc,
            "stdout_redacted": redact_enabled,
            "stdout_len": len(out),
            "stderr_len": len(err),
            "stdout_head": out[:2000],
            "stderr_head": err[:2000],
        }
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args.record_file)), exist_ok=True)
            with open(args.record_file, "w", encoding="utf-8") as fh:
                json.dump(record, fh, indent=2)
        except Exception as write_err:
            sys.stderr.write("run_bounded.py: failed to write record: {0}\n".format(write_err))

    return rc


if __name__ == "__main__":
    sys.exit(main())
