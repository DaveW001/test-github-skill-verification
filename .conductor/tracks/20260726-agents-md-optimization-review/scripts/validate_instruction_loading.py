#!/usr/bin/env python3
"""Bounded, read-only Codex/OpenCode instruction-loading probes.

The public CLI is intentionally small and matches ``plan.md``.  Tests may inject
disposable probe commands with ``--probe-command-json`` or the
``AGENTS_REVIEW_PROBE_COMMANDS`` environment variable.  A runtime probe is never
reported as Pass merely because a process exited zero: its transcript must
contain the explicit ``AGENTS_LOADING_PROBE_PASS`` marker.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    ToolchainError,
    assert_no_reparse,
    canonical,
    fail,
    file_record,
    json_line,
    read_json,
    write_json,
)


PASS_MARKER = "AGENTS_LOADING_PROBE_PASS"
CLIENTS = ("codex", "opencode")


def _terminate_owned(process: subprocess.Popen[str]) -> str:
    """Terminate only the process group created for this probe."""
    try:
        if process.poll() is not None:
            return "already-exited"
        if os.name == "nt":
            # The PID is the one created by this helper. /T is deliberately
            # scoped to that owned process tree.
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


def run_bounded_probe(
    command: list[str], *, timeout_seconds: int, cwd: str | Path
) -> dict[str, Any]:
    """Run one fresh owned process and return a normalized transcript."""
    if timeout_seconds <= 0:
        fail("timeout-seconds must be positive")
    if not command or not all(isinstance(part, str) and part for part in command):
        fail("probe command must be a nonempty string array")
    kwargs: dict[str, Any] = {
        "cwd": str(canonical(cwd)),
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
    except FileNotFoundError as exc:
        return {
            "status": "Unverified",
            "reason": "client executable unavailable",
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "cleanup": "not-started",
        }
    except OSError as exc:
        return {
            "status": "Unverified",
            "reason": "client probe launch unavailable",
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
            "status": "Unverified",
            "reason": "timeout",
            "returncode": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "cleanup": cleanup,
        }
    if process.returncode != 0:
        return {
            "status": "Fail",
            "reason": "probe returned nonzero",
            "returncode": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "cleanup": "not-needed",
        }
    if PASS_MARKER not in stdout:
        return {
            "status": "Fail",
            "reason": f"zero exit without required {PASS_MARKER} transcript marker",
            "returncode": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "cleanup": "not-needed",
        }
    return {
        "status": "Pass",
        "reason": "bounded probe returned explicit pass marker",
        "returncode": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "cleanup": "not-needed",
    }


def _load_command_overrides(path: str | None) -> dict[str, list[str]]:
    raw: Any = None
    if path:
        raw = read_json(path)
    elif os.environ.get("AGENTS_REVIEW_PROBE_COMMANDS"):
        raw = json.loads(os.environ["AGENTS_REVIEW_PROBE_COMMANDS"])
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        fail("probe command overrides must be a JSON object")
    result: dict[str, list[str]] = {}
    for client, command in raw.items():
        if client not in CLIENTS:
            fail(f"unknown probe client override: {client}")
        if not isinstance(command, list) or not command or not all(
            isinstance(part, str) and part for part in command
        ):
            fail(f"{client} probe override must be a nonempty string array")
        result[client] = command
    return result


def _probe_prompt(client: str, scope: str, target: Path) -> str:
    return (
        "Read-only instruction-loading probe. Do not edit files, approve actions, "
        "restart an application, or mutate a repository. Report the effective "
        f"{client} instruction sources for {target} and confirm critical safety "
        "and human-approval rules remain present. If and only if the sources and "
        f"rules are verified, output the literal marker {PASS_MARKER}. "
        f"Probe scope: {scope}."
    )


def _default_command(client: str, prompt: str) -> list[str] | None:
    executable = shutil.which(client)
    if executable is None:
        return None
    if client == "codex":
        return [
            executable,
            "exec",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--ephemeral",
            "--json",
            prompt,
        ]
    return [
        executable,
        "run",
        "--format",
        "json",
        "--title",
        "AGENTS instruction-loading probe",
        prompt,
    ]


def _expand_command(
    command: list[str], *, client: str, scope: str, target: Path, prompt: str
) -> list[str]:
    values = {
        "{client}": client,
        "{scope}": scope,
        "{target}": str(target),
        "{cwd}": str(target if target.is_dir() else target.parent),
        "{prompt}": prompt,
    }
    expanded: list[str] = []
    for part in command:
        value = part
        for marker, replacement in values.items():
            value = value.replace(marker, replacement)
        expanded.append(value)
    return expanded


def _classify_environment_blocker(transcript: dict[str, Any]) -> dict[str, Any]:
    """Keep unrelated client-startup defects from masquerading as AGENTS failures."""
    stderr = str(transcript.get("stderr", ""))
    if (
        transcript.get("status") == "Fail"
        and "Error loading config.toml:" in stderr
    ):
        adjusted = dict(transcript)
        adjusted["status"] = "Unverified"
        adjusted["reason"] = (
            "client startup blocked by a pre-existing config.toml parse error; "
            "AGENTS loading could not be observed"
        )
        return adjusted
    return transcript


def _representatives(scope: str, inventory: str | None) -> list[Path]:
    if scope == "global":
        return [
            canonical(r"C:\Users\DaveWitkin\.codex\AGENTS.md"),
            canonical(r"C:\Users\DaveWitkin\.config\opencode\AGENTS.md"),
        ]
    if not inventory:
        fail("--inventory is required for --scope local")
    payload = read_json(inventory)
    targets = payload.get("targets") if isinstance(payload, dict) else None
    if not isinstance(targets, list):
        fail("inventory targets must be an array")
    by_root: dict[str, list[Path]] = {}
    for entry in targets:
        if not isinstance(entry, dict) or entry.get("scope") != "local":
            continue
        path = canonical(entry.get("path", ""))
        root = str(entry.get("root") or path.parent)
        by_root.setdefault(os.path.normcase(str(canonical(root))), []).append(path)
    if not by_root:
        fail("local inventory contains no local targets")
    representatives: list[Path] = []
    for paths in by_root.values():
        ordered = sorted(paths, key=lambda item: (len(item.parts), str(item).lower()))
        representatives.append(ordered[0])
        if ordered[-1] != ordered[0]:
            representatives.append(ordered[-1])
    return representatives


def _static_checks(targets: list[Path]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for target in targets:
        try:
            assert_no_reparse(target, label="instruction target")
            record = file_record(target)
            text = target.read_text(encoding="utf-8")
            status = "Pass" if text.strip() else "Fail"
            reason = "regular nonempty instruction file" if text.strip() else "empty file"
            checks.append({"status": status, "reason": reason, **record})
        except (OSError, UnicodeError, ToolchainError) as exc:
            checks.append({"path": str(target), "status": "Fail", "reason": str(exc)})
    return checks


def _local_targets_and_exclusions(
    inventory: str,
) -> tuple[list[Path], list[dict[str, Any]]]:
    payload = read_json(inventory)
    if not isinstance(payload, dict) or not isinstance(payload.get("targets"), list):
        fail("inventory targets must be an array")
    targets = [
        canonical(entry["path"])
        for entry in payload["targets"]
        if isinstance(entry, dict)
        and entry.get("scope") == "local"
        and isinstance(entry.get("path"), str)
    ]
    exclusions: list[dict[str, Any]] = []
    raw_exclusions = payload.get("exclusions", [])
    if isinstance(raw_exclusions, dict):
        return targets, [
            {
                "status": "Unverified",
                "reason": (
                    "inventory records exclusion policy but not per-file "
                    "baseline hashes; unchanged excluded files cannot be proven"
                ),
                "policy": raw_exclusions,
            }
        ]
    if not isinstance(raw_exclusions, list):
        fail("inventory exclusions must be an array")
    for entry in raw_exclusions:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            exclusions.append(
                {
                    "status": "Unverified",
                    "reason": "exclusion lacks a path/hash identity",
                    "entry": entry,
                }
            )
            continue
        path = canonical(entry["path"])
        baseline_hash = entry.get("sha256")
        if not isinstance(baseline_hash, str) or len(baseline_hash) != 64:
            exclusions.append(
                {
                    "path": str(path),
                    "status": "Unverified",
                    "reason": "exclusion baseline hash was not recorded",
                }
            )
            continue
        try:
            current = file_record(path)
        except (OSError, ToolchainError) as exc:
            exclusions.append(
                {"path": str(path), "status": "Fail", "reason": str(exc)}
            )
            continue
        exclusions.append(
            {
                "path": str(path),
                "status": "Pass"
                if current["sha256"] == baseline_hash
                else "Fail",
                "reason": "excluded file unchanged"
                if current["sha256"] == baseline_hash
                else "excluded file hash changed",
                "sha256": current["sha256"],
                "baseline_sha256": baseline_hash,
            }
        )
    return targets, exclusions


def validate_loading(
    *,
    scope: str,
    timeout_seconds: int,
    output: str | Path,
    inventory: str | None = None,
    command_overrides: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    if scope not in {"global", "local"}:
        fail("scope must be global or local")
    if timeout_seconds <= 0:
        fail("timeout-seconds must be positive")
    targets = _representatives(scope, inventory)
    if scope == "local":
        assert inventory is not None  # enforced by _representatives
        static_targets, exclusion_checks = _local_targets_and_exclusions(inventory)
    else:
        static_targets, exclusion_checks = targets, []
    static = _static_checks(static_targets)
    overrides = command_overrides or {}
    probes: list[dict[str, Any]] = []
    probe_targets = (
        [("codex", targets[0]), ("opencode", targets[1])]
        if scope == "global"
        else [(client, target) for target in targets for client in CLIENTS]
    )
    for client, target in probe_targets:
        cwd = target.parent
        prompt = _probe_prompt(client, scope, target)
        base = overrides.get(client)
        if base is None:
            base = _default_command(client, prompt)
        if base is None:
            transcript: dict[str, Any] = {
                "status": "Unverified",
                "reason": "client executable unavailable",
                "returncode": None,
                "stdout": "",
                "stderr": "",
                "cleanup": "not-started",
            }
            command: list[str] = []
        else:
            command = _expand_command(
                base, client=client, scope=scope, target=target, prompt=prompt
            )
            transcript = run_bounded_probe(
                command, timeout_seconds=timeout_seconds, cwd=cwd
            )
            transcript = _classify_environment_blocker(transcript)
        probes.append(
            {
                "client": client,
                "target": str(target),
                "command": command,
                **transcript,
            }
        )
    statuses = (
        [item["status"] for item in static]
        + [item["status"] for item in exclusion_checks]
        + [item["status"] for item in probes]
    )
    clients: dict[str, dict[str, Any]] = {}
    for client in CLIENTS:
        client_probes = [item for item in probes if item["client"] == client]
        client_statuses = [item["status"] for item in client_probes]
        client_status = (
            "Fail"
            if "Fail" in client_statuses
            else "Pass"
            if client_statuses and all(status == "Pass" for status in client_statuses)
            else "Unverified"
        )
        reasons = sorted(
            {
                str(item.get("reason", ""))
                for item in client_probes
                if item.get("reason")
            }
        )
        clients[client] = {
            "status": client_status,
            "reason": "; ".join(reasons),
            "probe_count": len(client_probes),
        }
    overall = (
        "Fail"
        if "Fail" in statuses
        else "Pass"
        if probes and all(item["status"] == "Pass" for item in probes)
        else "Unverified"
    )
    result = {
        "check": "instruction-loading",
        "scope": scope,
        "status": overall,
        "timeout_seconds": timeout_seconds,
        "static_checks": static,
        "exclusion_checks": exclusion_checks,
        "probes": probes,
        # Both names are emitted for compatibility with the verifier contract.
        "clients": clients,
        "results": clients,
        "summary": {
            name: sum(1 for status in statuses if status == name)
            for name in ("Pass", "Fail", "Unverified")
        },
    }
    write_json(output, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run bounded read-only Codex/OpenCode instruction-loading probes."
    )
    parser.add_argument("--scope", required=True, choices=("global", "local"))
    parser.add_argument("--inventory")
    parser.add_argument("--timeout-seconds", required=True, type=int)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--probe-command-json",
        help="test-only JSON object mapping client names to disposable commands",
    )
    args = parser.parse_args(argv)
    try:
        result = validate_loading(
            scope=args.scope,
            inventory=args.inventory,
            timeout_seconds=args.timeout_seconds,
            output=args.output,
            command_overrides=_load_command_overrides(args.probe_command_json),
        )
        print(json_line(result))
        return 1 if result["status"] == "Fail" else 0
    except (ToolchainError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json_line(
                {
                    "check": "instruction-loading",
                    "scope": args.scope,
                    "status": "Fail",
                    "error": str(exc),
                }
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
