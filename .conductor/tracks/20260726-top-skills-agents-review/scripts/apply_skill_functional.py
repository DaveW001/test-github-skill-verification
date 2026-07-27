#!/usr/bin/env python3
"""Update each skill packet with functional verdict + evidence (Task 2.2).

Reads the harness structural results, classifies each skill's functional test
safety, and writes functional_verdict + functional_evidence into the packet.
Live functional cases requiring credentials, external mutation, network,
destructive operations, or subagent/orchestration dispatch are recorded as
FUNCTIONAL_SMOKE_TEST_UNVERIFIED with an explicit safety reason -- they are
NEVER dispatched. The structural harness result is recorded as the structural
evidence layer (distinct from functional confirmation).
"""

from __future__ import annotations

import json
import os
import sys

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"

# Per-skill functional safety classification. Each entry maps skill name ->
# (verdict, reason). session-db-query was functionally exercised read-only in
# Task 1.1. All others require credentials / external mutation / network /
# orchestration dispatch outside the safe fixture envelope -> UNVERIFIED.
FUNCTIONAL_CLASSIFICATION = {
    "session-db-query": (
        "FUNCTIONAL_SMOKE_TEST_PASSED",
        "Task 1.1 read-only schema inspection against opencode.db (?mode=ro) "
        "exercised the skill's documented read-only session-DB query role; no "
        "credentials, no mutation, no raw message bodies selected.",
    ),
}


def _default_unverified(name, structural_result):
    reasons = {
        "git-push": "requires git commit/push (external repository mutation + credentials) -- prohibited in review-only track",
        "opencode-scheduler": "requires scheduling live jobs (external schedule mutation) -- prohibited",
        "opencode-event-log-compactor": "requires compacting/archiving logs (destructive mutation); additionally STRUCTURAL script-syntax FAIL so functional confirmation moot",
        "opencode-go-key-rotation": "requires credential/key rotation (secrets + provider mutation) -- prohibited",
        "clickup": "requires ClickUp API credentials + external mutation; additionally STRUCTURAL script-syntax FAIL so functional confirmation moot",
        "conductor": "orchestration skill invoked through the Conductor pipeline; functional confirmation requires subagent/orchestration dispatch outside the safe fixture envelope",
        "conductor-pipeline": "pipeline orchestration skill; functional confirmation requires subagent/orchestration dispatch outside the safe fixture envelope",
        "scheduled-job-best-practices": "guidance/reference skill; no executable offline role to confirm without a live scheduling context",
        "retrospective": "analysis skill requiring a target session/input and subagent analysis dispatch",
        "root-cause-analysis": "analysis skill requiring a target incident/input and subagent analysis dispatch",
        "skill-creator": "creation skill; functional confirmation would create/modify a skill (write mutation) -- out of review scope",
        "doc": "documentation/processing skill; functional confirmation requires document input and processing/generation outside the safe fixture envelope",
        "humanizer": "content transformation skill; functional confirmation requires generation/subagent dispatch",
        "diagram-svg": "generation skill; functional confirmation requires generation/subagent dispatch",
        "pptx-from-layouts": "generation skill; functional confirmation requires generation + file creation (mutation)",
        "pre-delivery-ai-review": "review skill requiring a target deliverable and analysis dispatch",
        "image-ocr": "requires image input and OCR engine invocation (external/IO) outside the safe fixture envelope",
        "enrich-meeting-notes": "requires meeting-note input and external enrichment (calendar/contact/CRM) -- credentials/mutation",
        "osgrep": "semantic-search CLI in canary mode; functional confirmation requires a bounded live CLI invocation that may surface canary runtime issues; deferred to a dedicated bounded CLI test",
    }
    reason = reasons.get(name, "functional confirmation requires credentials, external mutation, network, or subagent dispatch outside the safe offline fixture envelope")
    return "FUNCTIONAL_SMOKE_TEST_UNVERIFIED", reason


def main():
    with open(os.path.join(TRACK, "evidence", "skill-smoke-tests", "harness-results.json"),
              "r", encoding="utf-8-sig") as fh:
        harness = {r["canonical_name"]: r for r in json.load(fh)}
    pkt_dir = os.path.join(TRACK, "review-batches", "skills")
    updated = []
    for name, h in harness.items():
        ppath = os.path.join(pkt_dir, name + ".json")
        with open(ppath, "r", encoding="utf-8-sig") as fh:
            pkt = json.load(fh)
        structural = h["harness_result"]
        if name in FUNCTIONAL_CLASSIFICATION:
            verdict, reason = FUNCTIONAL_CLASSIFICATION[name]
        else:
            verdict, reason = _default_unverified(name, structural)
        pkt["functional_verdict"] = verdict
        pkt["functional_evidence"] = {
            "harness_structural_result": structural,
            "harness_exit_code": h["harness_exit_code"],
            "harness_summary_excerpt": h["summary_excerpt"][:800],
            "functional_verdict_reason": reason,
            "safe_dispatch_policy": "no live functional case dispatched; credentials/external mutation/network/destructive ops/orchestration dispatch prohibited in review-only track",
        }
        with open(ppath, "w", encoding="utf-8") as fh:
            json.dump(pkt, fh, indent=2, ensure_ascii=False)
        updated.append(name)
    print("FUNCTIONAL_APPLIED=%d" % len(updated))
    return 0


if __name__ == "__main__":
    sys.exit(main())
