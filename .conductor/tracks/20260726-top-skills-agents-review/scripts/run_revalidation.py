#!/usr/bin/env python3
"""Revalidate every changed skill (Task 5.1).

Derives the changed-skill set from change-manifest.json. For each changed skill:
- directly syntax-checks each changed file (.py via py_compile, .ps1 via PowerShell tokenize)
- runs the skill-test-harness for the skill-level SCRIPT SYNTAX summary
Writes validation-results.json with per-skill verdict. The formerly truncated,
unreferenced clickup/scripts/patch_script.py was removed after Dave explicitly
authorized removal and a byte-identical recovery copy was verified.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"
HARNESS = r"C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1"
SKILL_FOLDER = {
    "clickup": r"C:\Users\DaveWitkin\.opencode-lazy-vault\clickup",
    "opencode-event-log-compactor": r"C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-event-log-compactor",
}
# Fixed files per skill (the applied changes only).
APPLIED_FIXES = {
    "clickup": ["scripts/input_validation.py", "tests/test_input_validation.py"],
    "opencode-event-log-compactor": ["scripts/Switch-ValidatedDatabase.ps1"],
}
# No pre-existing syntax blockers remain after Dave's explicit artifact decision.
PREEXISTING_UNRESOLVED = {}


def _run(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, shell=False, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or ""), (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except Exception as e:
        return 2, "", str(e)


def _syntax_check_file(folder, rel):
    fp = os.path.join(folder, rel)
    if not os.path.isfile(fp):
        return {"file": rel, "result": "MISSING", "detail": "file not found"}
    low = rel.lower()
    if low.endswith(".py"):
        rc, out, err = _run([sys.executable, "-m", "py_compile", fp], timeout=45)
        ok = rc == 0
        return {"file": rel, "result": "PASS" if ok else "FAIL",
                "command": "py_compile", "exit_code": rc,
                "detail": (err.strip()[:300] if not ok else "py_compile OK")}
    if low.endswith(".ps1"):
        # PowerShell tokenize via the parser (vars must pre-exist for [ref]).
        script = ("$tokens=$null; $errors=$null; "
                  "[System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$tokens,[ref]$errors) | Out-Null; "
                  "if($errors.Count){ exit 1 } else { exit 0 }") % fp.replace("'", "''")
        rc, out, err = _run(["powershell", "-NoProfile", "-Command", script], timeout=45)
        ok = rc == 0
        return {"file": rel, "result": "PASS" if ok else "FAIL",
                "command": "PS tokenize", "exit_code": rc,
                "detail": ("parse errors: %s" % (out.strip() or err.strip())[:200] if not ok else "PowerShell tokenize OK (0 parse errors)")}
    return {"file": rel, "result": "SKIP", "detail": "no syntax checker for this extension"}


def _harness_summary(folder, timeout=90):
    rc, out, err = _run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                         HARNESS, "-SkillPath", folder], timeout=timeout)
    # Extract SCRIPT SYNTAX summary line + RESULT line.
    summary = ""
    result = ""
    script_fail_files = []
    for ln in (out or "").splitlines():
        if "SCRIPT SYNTAX:" in ln:
            summary = ln.strip()
        if ln.strip().startswith("RESULT:"):
            result = ln.strip()
        m = re.search(r"\[SCRIPT SYNTAX\]\[FAIL\]\s*([^:]+):", ln)
        if m:
            script_fail_files.append(m.group(1).strip())
    return {"harness_exit": rc, "script_syntax_line": summary, "result_line": result,
            "harness_script_fail_files": script_fail_files}


def main():
    cm = json.load(open(os.path.join(TRACK, "change-manifest.json"), encoding="utf-8-sig"))
    changed_skills = sorted({c["canonical_name"] for c in cm["changes"]})
    results = []
    for cn in changed_skills:
        folder = SKILL_FOLDER[cn]
        applied = APPLIED_FIXES.get(cn, [])
        pre = PREEXISTING_UNRESOLVED.get(cn, [])
        file_checks = [_syntax_check_file(folder, rel) for rel in applied]
        pre_checks = [_syntax_check_file(folder, rel) for rel in pre]
        h = _harness_summary(folder)
        applied_all_pass = all(fc["result"] == "PASS" for fc in file_checks)
        # Skill-level harness SCRIPT SYNTAX PASS?
        skill_syntax_pass = "SCRIPT SYNTAX: OK" in h["script_syntax_line"]
        # Determine verdict.
        if applied_all_pass and skill_syntax_pass and not pre:
            verdict = "PASS"
        elif applied_all_pass and pre:
            verdict = "PARTIAL_PREEXISTING"
        else:
            verdict = "FAIL"
        results.append({
            "canonical_name": cn,
            "folder": folder,
            "applied_fix_files": applied,
            "applied_fix_checks": file_checks,
            "applied_fixes_all_pass": applied_all_pass,
            "preexisting_unresolved_files": pre,
            "preexisting_checks": pre_checks,
            "harness": h,
            "skill_level_script_syntax_pass": skill_syntax_pass,
            "verdict": verdict,
            "verdict_reason": (
                "all applied-fix files PASS syntax; skill-level harness SCRIPT SYNTAX PASS" if verdict == "PASS"
                else "applied-fix files PASS syntax; a pre-existing unresolved file remains" if verdict == "PARTIAL_PREEXISTING"
                else "an applied-fix file still fails syntax"),
        })

    out = {
        "trackId": "20260726-top-skills-agents-review",
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "changed_skills": changed_skills,
        "changed_skills_count": len(changed_skills),
        "results": results,
        "summary": {
            "pass": sum(1 for r in results if r["verdict"] == "PASS"),
            "partial_preexisting": sum(1 for r in results if r["verdict"] == "PARTIAL_PREEXISTING"),
            "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
        },
        "changed_agents": [],
        "changed_agents_verdict": "NOT_APPLICABLE",
    }
    with open(os.path.join(TRACK, "validation-results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print("REVALIDATION_DONE skills=%d pass=%d partial=%d fail=%d" %
          (len(results), out["summary"]["pass"], out["summary"]["partial_preexisting"], out["summary"]["fail"]))
    for r in results:
        print("  %s: verdict=%s applied_pass=%s skill_syntax_pass=%s" %
              (r["canonical_name"], r["verdict"], r["applied_fixes_all_pass"], r["skill_level_script_syntax_pass"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
