#!/usr/bin/env python3
"""Run the skill-test-harness structural mode on all 20 selected skills (Task 2.2).

For each selected skill, invoke the harness via subprocess with a per-skill hard
timeout, capture STRUCTURE/REFERENCES/SCRIPT SYNTAX summary + RESULT, and write
a redacted evidence record to evidence/skill-smoke-tests/harness-results.json.
Never dispatches a live functional case that requires credentials or external
mutation; functional verdicts are classified by apply_skill_functional.py.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"
HARNESS = r"C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1"


def _selected():
    with open(os.path.join(TRACK, "usage-ranking.json"), "r", encoding="utf-8-sig") as fh:
        return json.load(fh)["selected_skills"]


def _run_harness(skill_path, timeout=45):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
           HARNESS, "-SkillPath", skill_path, "-PrintFunctionalPrompt"]
    try:
        proc = subprocess.run(cmd, shell=False, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8", errors="replace")
        return proc.returncode, (proc.stdout or ""), (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT after %ss" % timeout
    except Exception as e:
        return 2, "", "ERROR: %s" % e


def _summarize(out):
    # Extract key summary lines (STRUCTURE/REFERENCES/SCRIPT SYNTAX/RESULT).
    lines = (out or "").splitlines()
    keep = []
    for ln in lines:
        u = ln.upper()
        if any(k in u for k in ("STRUCTURE:", "REFERENCES:", "SCRIPT SYNTAX:", "RESULT:", "SKILL SMOKE TEST")):
            keep.append(ln.strip())
    return "\n".join(keep[-12:])


def main():
    skills = _selected()
    out_dir = os.path.join(TRACK, "evidence", "skill-smoke-tests")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    results = []
    for s in skills:
        name = s["canonical_name"]
        rc, out, err = _run_harness(s["resolved_path"])
        summary = _summarize(out)
        # Redact any long token-like strings defensively.
        summary = re.sub(r"(?i)(sk-[A-Za-z0-9_\-]{16,})", "[REDACTED]", summary)
        results.append({
            "canonical_name": name,
            "resolved_path": s["resolved_path"],
            "harness_exit_code": rc,
            "harness_result": "PASS" if rc == 0 else ("FAIL" if rc == 1 else ("TIMEOUT" if rc == 124 else "ERROR")),
            "summary_excerpt": summary[:1500],
        })
    out_path = os.path.join(out_dir, "harness-results.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    passed = sum(1 for r in results if r["harness_result"] == "PASS")
    failed = sum(1 for r in results if r["harness_result"] == "FAIL")
    other = len(results) - passed - failed
    print("HARNESS_RUN_DONE skills=%d pass=%d fail=%d other=%d" % (len(results), passed, failed, other))
    return 0


if __name__ == "__main__":
    sys.exit(main())
