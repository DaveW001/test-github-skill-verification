#!/usr/bin/env python3
"""Generate the decision-ready portfolio report (Task 5.3).

Reads immutable source JSON (usage-ranking.json, skill/agent packets,
fix-queue.json, change-manifest.json, validation-results.json) and writes
portfolio-review-report.md with exactly 20 skill entries + 10 agent entries,
methodology/confidence, fixes applied, validation, unresolved findings, Optional
improvements, Unverified items, and Dave decisions. Includes a reconciliation
block whose counts are validated by the verifier against the source JSON.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"


def _load(name):
    with open(os.path.join(TRACK, name), "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def _load_pkt(sub, name):
    p = os.path.join(TRACK, "review-batches", sub, name + ".json")
    with open(p, "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def _findings(pkt):
    out = {"Critical": [], "Major": [], "Minor": [], "Optional": []}
    for it in pkt.get("items", []):
        if it.get("result") == "Fail":
            out.setdefault(it.get("severity", "Minor"), []).append(it["id"])
    return out


def main():
    rank = _load("usage-ranking.json")
    fq = _load("fix-queue.json")
    cm = _load("change-manifest.json")
    vr = _load("validation-results.json")
    rubric_sha = rank.get("ranking_contract_sha256", "")

    skills = rank["selected_skills"]
    agents = rank["selected_agents"]

    skill_fixes = fq.get("skill_fixes") or []
    agent_fixes = fq.get("agent_fixes") or []
    skill_nofix = fq.get("skill_no_fix_dispositions") or []
    agent_nofix = fq.get("agent_no_fix_dispositions") or []
    dave = fq.get("dave_decisions") or []
    changes = cm.get("changes") or []

    L = []
    L.append("# Portfolio Review Report — Top Skills and Agents\n")
    L.append("**Track:** `20260726-top-skills-agents-review`  ")
    L.append("**Generated (UTC):** %s  " % datetime.now(timezone.utc).isoformat(timespec="seconds"))
    L.append("**Pipeline:** bookkeeping, `1 -> 2 -> 5 -> 7 -> 9` (Stage 2 retained for broad unversioned global-artifact risk; Stage 3 conditional re-review consumed; manual plan correction closed RR-B1..B5; Stages 3/4/4b/6/8 skipped per threshold policy).  ")
    L.append("**Executor model:** `zai-coding-plan/glm-5.2` (variant `high`).\n")

    # Methodology
    L.append("## Methodology and confidence\n")
    L.append("- **Agents** ranked from **direct** `session.agent` evidence in `opencode.db` "
             "(read-only, `?mode=ro`, archived sessions included) — **high confidence**.")
    L.append("- **Skills** ranked from **inferred** `session.title` mentions + operational "
             "importance — **low confidence**. There is **no structured skill-call table** in "
             "`opencode.db` (event types are message/session lifecycle only; `session.metadata` empty). "
             "Codex-local `~/.codex/sessions` exists but was NOT parsed (message bodies; would need a "
             "body-redaction contract) — recorded as an evidence gap.")
    L.append("- Weights (frozen in `ranking-contract.json`, SHA-256 `%s`): frequency 0.55, breadth 0.25, "
             "recency 0.15, operational-importance 0.05." % rubric_sha[:12])
    L.append("- Functional confirmation: 1 skill functionally PASSED (`session-db-query`, exercised "
             "read-only in Task 1.1); 19 `FUNCTIONAL_SMOKE_TEST_UNVERIFIED` (credentials/external "
             "mutation/orchestration dispatch prohibited). Agent smoke: `AGENT_SMOKE_UNVERIFIED` "
             "(live `opencode run` not dispatched — the `opencode` CLI hangs; unbounded session risk).\n")

    # Skills
    L.append("## Skills (20)\n")
    L.append("| # | Skill | Conf | Harness | Functional | Major findings | Applied fix |")
    L.append("|---|-------|------|---------|-----------|----------------|-------------|")
    applied_by_skill = {}
    for c in changes:
        applied_by_skill.setdefault(c["canonical_name"], []).append(c)
    for s in skills:
        pkt = _load_pkt("skills", s["canonical_name"])
        f = _findings(pkt)
        major = ", ".join(f.get("Major", [])) or "—"
        applied = "yes (%d file(s))" % len(applied_by_skill.get(s["canonical_name"], [{}])[0].get("changed_files", [])) if s["canonical_name"] in applied_by_skill else "—"
        L.append("| %d | %s | %s | %s | %s | %s | %s |" % (
            s.get("rank"), s["canonical_name"], s.get("confidence"),
            (pkt.get("functional_evidence") or {}).get("harness_structural_result"),
            pkt.get("functional_verdict"), major, applied))
    L.append("")

    # Agents
    L.append("## Agents (10)\n")
    L.append("| # | Agent | Model | Mode | Smoke | Minor findings |")
    L.append("|---|-------|-------|------|-------|----------------|")
    for a in agents:
        pkt = _load_pkt("agents", a["canonical_name"])
        f = _findings(pkt)
        minor = ", ".join(f.get("Minor", [])) or "—"
        L.append("| %d | %s | %s | %s | %s | %s |" % (
            a.get("rank"), a["canonical_name"], pkt.get("configured_model"),
            pkt.get("configured_mode"), pkt.get("smoke_outcome"), minor))
    L.append("")

    # Fixes applied
    L.append("## Fixes applied\n")
    for c in changes:
        L.append("- **%s** (%d file(s) changed, `authority_delta: none`): %s" % (
            c["canonical_name"], len(c["changed_files"]), c["correction"]))
    L.append("- **Agent fixes:** none queued (0).\n")

    # Validation
    L.append("## Validation results\n")
    for r in vr.get("results", []):
        L.append("- **%s** — verdict `%s`: %s" % (r["canonical_name"], r["verdict"], r["verdict_reason"]))
    L.append("- **Changed agents:** none → NOT_APPLICABLE.\n")

    # Unresolved / Dave decisions
    L.append("## Unresolved findings and Dave decisions\n")
    if dave:
        for dd in dave:
            L.append("- **%s / %s** (Dave-decision): %s — %s" % (
                dd["canonical_name"], dd["file"], dd["finding"], dd["reason_not_fixed"]))
    else:
        L.append("- (none)")
    open_major = [q for q in skill_fixes if q.get("status") == "partial-dave-decision"]
    L.append("\n### Unresolved Major skill finding\n")
    if open_major:
        for q in open_major:
            L.append("- **%s** `%s`: unresolved; see `fix-queue.json`." % (
                q["canonical_name"], q["rubric_item"]))
    else:
        L.append("- (none)")
    L.append("")

    # Optional / Unverified
    L.append("## Optional improvements and Unverified items\n")
    L.append("- **Optional (no-fix dispositions):** %d skill Minor heuristic findings and %d agent "
             "Minor heuristic findings received explicit no-fix dispositions (content/behavior "
             "decisions for Dave). See `fix-queue.json`." % (len(skill_nofix), len(agent_nofix)))
    L.append("- **Unverified:** 19 skills `FUNCTIONAL_SMOKE_TEST_UNVERIFIED`; all 10 agents "
             "`AGENT_SMOKE_UNVERIFIED`; agent model routes `AGENT_04/05` Unverified for LIVE "
             "availability (config-level evidence only). These are NOT turned into Pass.\n")
    L.append("- **ClickUp offline diagnostic:** 21/23 unit tests passed. One fixture does not "
             "actually exercise an emoji condition; the prioritization import test also exposes "
             "missing `run_prioritization.py` / `prioritization_helpers` packaging. These are "
             "non-blocking follow-ups for this syntax/removal correction, not a 23/23 pass.\n")

    # Reconciliation block (validated by verifier against source JSON)
    counts = {
        "skills": len(skills), "agents": len(agents),
        "queued_skill_fixes": len(skill_fixes), "queued_agent_fixes": len(agent_fixes),
        "applied_skill_changes": len(changes),
        "skill_no_fix_dispositions": len(skill_nofix),
        "agent_no_fix_dispositions": len(agent_nofix),
        "dave_decisions": len(dave),
        "validation_pass": vr.get("summary", {}).get("pass", 0),
        "validation_partial_preexisting": vr.get("summary", {}).get("partial_preexisting", 0),
        "validation_fail": vr.get("summary", {}).get("fail", 0),
    }
    L.append("## Reconciliation\n")
    L.append("```json")
    L.append(json.dumps(counts, indent=2))
    L.append("```\n")
    L.append("Skill entry names: %s" % ", ".join(sorted(s["canonical_name"] for s in skills)))
    L.append("\nAgent entry names: %s" % ", ".join(sorted(a["canonical_name"] for a in agents)))
    L.append("\n---\n_Report generated from immutable source JSON; counts reconcile to `usage-ranking.json`, "
             "`fix-queue.json`, `change-manifest.json`, and `validation-results.json`._")

    with open(os.path.join(TRACK, "portfolio-review-report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("REPORT_DONE skills=%d agents=%d" % (len(skills), len(agents)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
