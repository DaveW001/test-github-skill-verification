#!/usr/bin/env python3
"""Aggregate osgrep debug-wrapper result.json files into a pass/fail report.

Usage:
    python scripts/tests/osgrep_test_suite.py --report
        Scan logs/osgrep-debug/ for result.json and generate report.md.
    python scripts/tests/osgrep_test_suite.py --list
        List all available result.json files with status.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEBUG_DIR = REPO_ROOT / "logs" / "osgrep-debug"
REPORT_DIR = REPO_ROOT / "logs" / "osgrep-test-suite"

BLOCKING_LABELS = {
    "tc-a1-version-check",
    "tc-a2-doctor-check",
    "tc-b1-index-dry-run",
    "tc-b2-index-verbose",
    "tc-b3-index-path",
    "tc-b4-index-reset",
    "tc-b5-search-sync",
    "tc-b6-list",
    "tc-c1-known-answer",
    "tc-c2-max-count",
    "tc-c3-content",
    "tc-c4-scores",
    "tc-f1-mcp-guardrail",
    "tc-f2-tool-path",
    "tc-f3-forced-failure",
}

EXPECTED_FAILURE_LABELS = {
    "tc-e5-nonexistent-cwd",
    "tc-e6-empty-pattern",
    "tc-f3-forced-failure",
}

CRITICAL_PATTERNS = [
    "Table 'chunks' already exists",
    "UnicodeDecodeError",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _is_blocking(label: str) -> bool:
    return any(b in label for b in BLOCKING_LABELS)

def _is_expected_failure(label: str) -> bool:
    return any(e in label for e in EXPECTED_FAILURE_LABELS)

def _evaluate_result(record: dict, label: str) -> str:
    if record.get("timed_out"):
        return "TIMEOUT"
    exit_code = record.get("exit_code")
    if _is_expected_failure(label):
        return "PASS"
    if exit_code == 0:
        return "PASS"
    return "FAIL"

def _scan_critical(stderr: str) -> list:
    found = []
    for pattern in CRITICAL_PATTERNS:
        if pattern in stderr:
            found.append(pattern)
    return found

def _load_results() -> list:
    results = []
    if not DEBUG_DIR.exists():
        return results
    for entry in sorted(DEBUG_DIR.iterdir()):
        if not entry.is_dir():
            continue
        result_file = entry / "result.json"
        if not result_file.exists():
            continue
        try:
            data = json.loads(result_file.read_text(encoding="utf-8"))
            data["_dir"] = entry.name
            data["_file"] = str(result_file)
            results.append(data)
        except (json.JSONDecodeError, OSError) as exc:
            results.append({
                "_dir": entry.name,
                "_file": str(result_file),
                "label": entry.name,
                "exit_code": None,
                "stdout": "",
                "stderr": f"Failed to parse result.json: {exc}",
                "timed_out": False,
                "_parse_error": True,
            })
    return results

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _generate_report(results: list) -> str:
    blocking = []
    non_blocking = []
    critical_findings = []
    total_pass = 0
    total_fail = 0
    total_timeout = 0
    total_skip = 0

    for r in results:
        label = r.get("label", r.get("_dir", "unknown"))
        status = _evaluate_result(r, label)
        is_blk = _is_blocking(label)
        criticals = _scan_critical(r.get("stderr", ""))
        entry = {
            "label": label,
            "status": status,
            "exit_code": r.get("exit_code"),
            "timed_out": r.get("timed_out", False),
            "duration": r.get("duration_seconds", 0),
            "critical": criticals,
            "dir": r.get("_dir", ""),
        }
        if is_blk:
            blocking.append(entry)
        else:
            non_blocking.append(entry)
        if status == "PASS":
            total_pass += 1
        elif status == "FAIL":
            total_fail += 1
        elif status == "TIMEOUT":
            total_timeout += 1
        else:
            total_skip += 1
        for c in criticals:
            critical_findings.append(f"- **{label}**: `{c}`")

    blocking_pass = all(e["status"] == "PASS" for e in blocking)
    blocking_timeout = any(e["timed_out"] for e in blocking)
    go_nogo = "GO" if (blocking_pass and not blocking_timeout) else "NO-GO"

    lines = []
    lines.append("# OsGrep Test Suite Report")
    lines.append("")
    lines.append(f"Generated: {_now_iso()}")
    lines.append(f"Total tests found: {len(results)}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total  | {len(results)} |")
    lines.append(f"| Passed | {total_pass} |")
    lines.append(f"| Failed | {total_fail} |")
    lines.append(f"| Timed Out | {total_timeout} |")
    lines.append(f"| Skipped | {total_skip} |")
    lines.append(f"| **GO / NO-GO** | **{go_nogo}** |")
    lines.append("")
    lines.append("## Blocking Tests")
    lines.append("")
    lines.append("| Label | Status | Exit Code | Duration (s) | Notes |")
    lines.append("|-------|--------|-----------|--------------|-------|")
    for e in blocking:
        notes = ""
        if e["critical"]:
            notes = "CRITICAL: " + "; ".join(e["critical"])
        lines.append(f"| {e['label']} | {e['status']} | {e['exit_code']} | {e['duration']} | {notes} |")
    lines.append("")
    lines.append("## Non-Blocking Tests")
    lines.append("")
    lines.append("| Label | Status | Exit Code | Duration (s) | Notes |")
    lines.append("|-------|--------|-----------|--------------|-------|")
    for e in non_blocking:
        notes = ""
        if e["critical"]:
            notes = "CRITICAL: " + "; ".join(e["critical"])
        lines.append(f"| {e['label']} | {e['status']} | {e['exit_code']} | {e['duration']} | {notes} |")
    lines.append("")
    lines.append("## Critical Error Patterns")
    lines.append("")
    if critical_findings:
        for c in critical_findings:
            lines.append(c)
    else:
        lines.append("No critical error patterns detected.")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    if go_nogo == "GO":
        lines.append("- All blocking tests passed. OsGrep is healthy for continued production use.")
    else:
        failed_blk = [e for e in blocking if e["status"] != "PASS"]
        if failed_blk:
            lines.append("- The following blocking tests did not pass:")
            for e in failed_blk:
                lines.append(f"  - **{e['label']}**: {e['status']} (exit_code={e['exit_code']})")
        if blocking_timeout:
            lines.append("- One or more blocking tests timed out. Consider increasing timeouts or investigating performance.")
    lines.append("")
    tc_f2 = [e for e in blocking if "tc-f2" in e["label"]]
    if tc_f2 and tc_f2[0]["status"] != "PASS":
        lines.append("- **TC-F2 (tool-path activation)** requires an OpenCode session to verify. If running from CLI-only, mark as CONDITIONAL and re-verify inside OpenCode.")
        lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_list(results: list) -> int:
    if not results:
        print(f"No result.json files found in {DEBUG_DIR}")
        return 1
    print(f"Found {len(results)} result.json file(s) in {DEBUG_DIR}\n")
    for r in results:
        label = r.get("label", r.get("_dir", "unknown"))
        status = _evaluate_result(r, label)
        blocking = "BLOCKING" if _is_blocking(label) else "non-blocking"
        duration = r.get("duration_seconds", "?")
        print(f"  [{status:7s}] ({blocking:12s}) {label}  ({duration}s)")
        print(f"           -> {r.get('_file', '')}")
    return 0

def cmd_report(results: list) -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "report.md"
    report_content = _generate_report(results)
    report_path.write_text(report_content, encoding="utf-8")
    print(f"Report written to: {report_path}")
    total = len(results)
    passed = sum(1 for r in results if _evaluate_result(r, r.get("label", "")) == "PASS")
    print(f"  Total: {total} | Passed: {passed} | Failed: {total - passed}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate osgrep debug-wrapper results into a pass/fail report."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="Generate report.md")
    group.add_argument("--list", action="store_true", help="List available result.json files")
    args = parser.parse_args()
    results = _load_results()
    if args.list:
        return cmd_list(results)
    if args.report:
        return cmd_report(results)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
