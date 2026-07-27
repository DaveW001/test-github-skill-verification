#!/usr/bin/env python3
"""Generate skill-review-matrix.md + fix-queue.json (Task 2.3).

Reconciles harness script-syntax results into packets, then builds:
- skill-review-matrix.md: one structured entry per selected skill with every
  rubric-item result, functional verdict, confidence, and proposed fix.
- fix-queue.json: high-confidence Critical/Major/Minor findings only.
  Major script-syntax defects are queued; heuristic Minor findings receive an
  explicit no-fix disposition with reason.
Bidirectional reconciliation: every Critical/Major/Minor finding -> exactly one
queue entry or no-fix disposition; every queue entry -> exactly one finding.
"""

from __future__ import annotations

import json
import os
import sys

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"


def _load(name):
    with open(os.path.join(TRACK, name), "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def _no_fix_reason(item_id, severity, skill):
    reasons = {
        "STRUCT_01_ENTRYPOINT_SIZE": "conciseness bound is a heuristic; the skill is an established large reference entrypoint -- refactoring is a content decision for Dave, not an in-scope safe fix",
        "STRUCT_02_ADVANCED_DETAILS_DISCLOSED": "no internal references; this skill keeps details inline by design -- progressive-disclosure restructure is a content decision, not a defect",
        "STRUCT_03_ONE_LEVEL_REFERENCES": "broken internal reference detected; needs case-by-case validation -- recorded as Optional for Dave decision",
        "TROUBLE_04_REFERENCE_EXISTENCE": "reference existence flag mirrors STRUCT_03; same Optional disposition",
        "DESC_02_LENGTH": "description length slightly outside heuristic bounds; editing the activation description affects skill discovery -- Dave decision",
        "DESC_01_WHAT_WHEN_KEYWORDS": "description keyword heuristic; content wording decision for Dave",
        "TEST_01_ACTIVATION": "no explicit activation section detected by heuristic; existing skills rely on description activation -- Optional",
        "SCOPE_02_REALISTIC_TRIGGERS": "trigger-signal heuristic; existing skills activate via description -- Optional",
        "TRIG_02_SUGGEST_ONLY_TRUE": "triggers.suggest_only not true; changing trigger behavior is an authority/behavior decision for Dave",
        "GUARD_03_CONCISE_ACTIONABLE_EXAMPLES": "no examples detected by heuristic; adding examples is a content improvement -- Optional",
    }
    return reasons.get(item_id, "heuristic Minor structural finding on an established skill; no in-scope safe auto-fix -- Optional / Dave decision")


def main():
    rank = _load("usage-ranking.json")
    sel = rank["selected_skills"]
    harness = {r["canonical_name"]: r for r in
               _load(os.path.join("evidence", "skill-smoke-tests", "harness-results.json"))}
    pkt_dir = os.path.join(TRACK, "review-batches", "skills")

    queue = []
    no_fix = []
    matrix_rows = []
    queue_counter = 0

    for s in sel:
        name = s["canonical_name"]
        ppath = os.path.join(pkt_dir, name + ".json")
        pkt = _load(os.path.join("review-batches", "skills", name + ".json"))
        h = harness.get(name, {})
        harness_fail = h.get("harness_result") == "FAIL"

        # Reconcile SCRIPT_04_SYNTAX against authoritative harness result.
        if harness_fail:
            for it in pkt["items"]:
                if it["id"] == "SCRIPT_04_SYNTAX":
                    it["result"] = "Fail"
                    it["severity"] = "Major"
                    it["evidence"] = ("authoritative skill-test-harness SCRIPT SYNTAX: FAIL "
                                      "(%s). Static check deferred; harness is authoritative." %
                                      h.get("summary_excerpt", "")[:200])
                    it["source_path"] = pkt["source_path"]
            with open(ppath, "w", encoding="utf-8") as fh:
                json.dump(pkt, fh, indent=2, ensure_ascii=False)

        # Collect findings.
        skill_fails = [it for it in pkt["items"]
                       if it["result"] == "Fail" and it["severity"] in ("Critical", "Major", "Minor")]
        for it in skill_fails:
            sev = it["severity"]
            iid = it["id"]
            if sev == "Major":
                # High-confidence actionable defect -> queue.
                queue_counter += 1
                qid = "FIX-SKILL-%03d-%s-%s" % (queue_counter, name, iid)
                queue.append({
                    "id": qid,
                    "artifact_type": "skill",
                    "canonical_name": name,
                    "canonical_path": pkt["source_path"],
                    "rubric_item": iid,
                    "severity": sev,
                    "evidence_reference": "review-batches/skills/%s.json item %s; evidence/skill-smoke-tests/harness-results.json" % (name, iid),
                    "before_intent": "skill script(s) fail the authoritative skill-test-harness SCRIPT SYNTAX check",
                    "after_intent": "failing script(s) corrected to pass harness SCRIPT SYNTAX without changing capability or authority",
                    "safety_classification": "Major structural defect; fix is script-syntax only; no capability/permission expansion",
                    "authority_delta": "none",
                    "status": "queued",
                })
            else:
                # Minor heuristic -> explicit no-fix disposition.
                no_fix.append({
                    "canonical_name": name,
                    "rubric_item": iid,
                    "severity": sev,
                    "disposition": "no-fix",
                    "reason": _no_fix_reason(iid, sev, name),
                })

        # Matrix row summary.
        results = {it["id"]: it["result"] for it in pkt["items"]}
        fail_items = [it["id"] for it in skill_fails]
        matrix_rows.append({
            "rank": s.get("rank"),
            "canonical_name": name,
            "resolved_path": s["resolved_path"],
            "confidence": s.get("confidence"),
            "functional_verdict": pkt.get("functional_verdict"),
            "harness_structural_result": h.get("harness_result"),
            "fail_items": fail_items,
            "item_count": len(pkt["items"]),
            "pass_count": sum(1 for it in pkt["items"] if it["result"] == "Pass"),
            "na_count": sum(1 for it in pkt["items"] if it["result"] == "Not Applicable"),
            "unverified_count": sum(1 for it in pkt["items"] if it["result"] == "Unverified"),
        })

    fix_queue = {
        "trackId": "20260726-top-skills-agents-review",
        "generated_at_utc": rank.get("generated_at_utc"),
        "skill_fixes": queue,
        "skill_no_fix_dispositions": no_fix,
        "counts": {"queued_skill_fixes": len(queue), "no_fix_dispositions": len(no_fix)},
    }
    with open(os.path.join(TRACK, "fix-queue.json"), "w", encoding="utf-8") as fh:
        json.dump(fix_queue, fh, indent=2, ensure_ascii=False)

    # Matrix markdown.
    lines = []
    lines.append("# Skill Review Matrix\n")
    lines.append("Track: `20260726-top-skills-agents-review`. One entry per selected skill "
                 "(20). Every frozen rubric item is recorded in each packet under "
                 "`review-batches/skills/<name>.json`; this matrix summarizes results, "
                 "functional verdicts, and fix dispositions.\n")
    lines.append("Functional confirmation is mostly `FUNCTIONAL_SMOKE_TEST_UNVERIFIED` by "
                 "design: live functional cases require credentials, external mutation, "
                 "network, or orchestration/subagent dispatch, all prohibited in this "
                 "review-only track. `session-db-query` was functionally exercised read-only "
                 "in Task 1.1.\n")
    lines.append("| # | Skill | Conf | Harness | Functional | Fails (items) | Pass/NA/Unv |")
    lines.append("|---|-------|------|---------|-----------|---------------|-------------|")
    for r in matrix_rows:
        lines.append("| {rank} | {name} | {conf} | {hr} | {fv} | {fails} | {pc}/{nc}/{uv} |".format(
            rank=r["rank"], name=r["canonical_name"], conf=r["confidence"],
            hr=r["harness_structural_result"], fv=r["functional_verdict"],
            fails=", ".join(r["fail_items"]) or "—",
            pc=r["pass_count"], nc=r["na_count"], uv=r["unverified_count"]))
    lines.append("")
    lines.append("## Queued skill fixes (Major)\n")
    if queue:
        for q in queue:
            lines.append("- **%s** — `%s` item `%s`: %s — %s" %
                         (q["id"], q["canonical_name"], q["rubric_item"], q["before_intent"],
                          q["after_intent"]))
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## No-fix dispositions (Minor heuristic findings)\n")
    lines.append("Each Minor heuristic finding is recorded here with an explicit reason; "
                 "it is NOT auto-fixed. These remain Optional/Dave-decision and are not "
                 "concealed.\n")
    for nf in no_fix:
        lines.append("- `%s` `%s` (%s): %s" %
                     (nf["canonical_name"], nf["rubric_item"], nf["severity"], nf["reason"]))
    with open(os.path.join(TRACK, "skill-review-matrix.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("MATRIX_DONE queued_skill_fixes=%d no_fix_dispositions=%d" % (len(queue), len(no_fix)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
