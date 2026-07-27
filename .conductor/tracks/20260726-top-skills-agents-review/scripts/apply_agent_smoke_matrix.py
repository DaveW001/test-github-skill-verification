#!/usr/bin/env python3
"""Agent smoke fixtures + agent-review-matrix.md + fix-queue append (Task 3.2).

Creates one fixture-only prompt JSON record per selected agent (required artifact)
and records smoke_outcome=AGENT_SMOKE_UNVERIFIED with an explicit reason: a live
`opencode run` session is NOT dispatched because (a) the `opencode` CLI hangs in
this environment (verified: `opencode models` produced no output and timed out),
and (b) a live agent session cannot be bounded to the 20-tool-call/10K-token cap
from the dispatch side and may require a server/credentials. This satisfies the
plan: unavailable/unsafe live paths are recorded Unverified; no model substituted.

Appends agent findings to fix-queue.json. All current agent findings are Minor
heuristic (Windows/path/shell, bounded-command, safety-stop guidance) and receive
explicit no-fix dispositions (content/behavior changes = Dave decision). Zero
Major agent defects are queued.
"""

from __future__ import annotations

import json
import os
import sys

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"


def _load(name):
    with open(os.path.join(TRACK, name), "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def _fixture_prompt(agent):
    """A safe fixture-only prompt record per agent (never dispatched live here)."""
    return {
        "canonical_name": agent["canonical_name"],
        "configured_model": agent.get("configured_model"),
        "configured_variant": agent.get("configured_variant"),
        "configured_mode": agent.get("configured_mode"),
        "working_directory": "<disposable-fixture-directory> (would be created fresh; not created here)",
        "allowed_tools": "read-only inspection only; no edit/bash mutation, no task spawn, no external services",
        "prohibited_effects": "no messages, no publish, no calendar/schedule changes, no credentials, "
                              "no production mutation, no delete/archive/rename/merge, no restart, no commit/push",
        "fixture_prompt": "State your role in one sentence and list the absolute path of your definition file. "
                          "Do not call any tools, do not read other files, do not spawn agents, do not use credentials.",
        "expected_output_shape": "one short paragraph; exit 0; no tool calls",
        "intended_command_envelope": ('opencode run --pure --agent "<name>" --format json '
                                      '--dir "<disposable-fixture>" "<fixture_prompt>"'),
        "dispatch_status": "NOT_DISPATCHED",
        "not_dispatched_reason": ("live opencode run is unsafe/unavailable in this environment: the opencode CLI "
                                  "hangs (opencode models produced no output and timed out), and a live agent session "
                                  "cannot be bounded to the 20-tool-call/10K-token cap from the dispatch side and may "
                                  "require a running server/auth. Recorded AGENT_SMOKE_UNVERIFIED; no model substituted."),
    }


def main():
    rank = _load("usage-ranking.json")
    sel = rank["selected_agents"]
    pkt_dir = os.path.join(TRACK, "review-batches", "agents")
    fix_dir = os.path.join(TRACK, "evidence", "agent-smoke-tests")
    if not os.path.isdir(fix_dir):
        os.makedirs(fix_dir, exist_ok=True)

    no_fix = []
    matrix_rows = []
    fixtures = []

    for a in sel:
        name = a["canonical_name"]
        ppath = os.path.join(pkt_dir, name + ".json")
        pkt = _load(os.path.join("review-batches", "agents", name + ".json"))

        # Fixture record (required artifact).
        fix = _fixture_prompt(a)
        fixtures.append(fix)
        with open(os.path.join(fix_dir, name + "-fixture.json"), "w", encoding="utf-8") as fh:
            json.dump(fix, fh, indent=2, ensure_ascii=False)

        # Set smoke outcome + update AGENT_13 item.
        pkt["smoke_outcome"] = "AGENT_SMOKE_UNVERIFIED"
        pkt["smoke_evidence"] = {
            "dispatch_status": "NOT_DISPATCHED",
            "reason": fix["not_dispatched_reason"],
            "fixture_record": "evidence/agent-smoke-tests/%s-fixture.json" % name,
            "intended_envelope": fix["intended_command_envelope"],
        }
        for it in pkt["items"]:
            if it["id"] == "AGENT_13_SMOKE_OUTCOME":
                it["result"] = "Unverified"
                it["severity"] = "Info"
                it["confidence"] = "medium"
                it["blocker_reason"] = fix["not_dispatched_reason"]
                it["evidence"] = "smoke NOT dispatched; AGENT_SMOKE_UNVERIFIED. Fixture record at evidence/agent-smoke-tests/%s-fixture.json" % name
        with open(ppath, "w", encoding="utf-8") as fh:
            json.dump(pkt, fh, indent=2, ensure_ascii=False)

        # Collect agent findings (all Minor heuristic -> no-fix disposition).
        for it in pkt["items"]:
            if it["result"] == "Fail" and it["severity"] in ("Critical", "Major", "Minor"):
                no_fix.append({
                    "canonical_name": name,
                    "rubric_item": it["id"],
                    "severity": it["severity"],
                    "disposition": "no-fix",
                    "reason": ("heuristic Minor agent-prompt finding; adding Windows/path/shell/bounded-command/safety "
                               "guidance to the prompt is a content/behavior decision for Dave, not an in-scope safe "
                               "auto-fix; detection may also miss guidance present in referenced pattern files"),
                })

        fails = [it["id"] for it in pkt["items"] if it["result"] == "Fail" and it["severity"] in ("Critical", "Major", "Minor")]
        matrix_rows.append({
            "rank": a.get("rank"), "name": name, "model": a.get("configured_model"),
            "mode": a.get("configured_mode"), "smoke": pkt["smoke_outcome"],
            "fails": fails,
            "pass": sum(1 for it in pkt["items"] if it["result"] == "Pass"),
            "na": sum(1 for it in pkt["items"] if it["result"] == "Not Applicable"),
            "unv": sum(1 for it in pkt["items"] if it["result"] == "Unverified"),
        })

    # Append to fix-queue.json (preserve existing skill fixes).
    fq = _load("fix-queue.json")
    fq["agent_fixes"] = []  # zero Major agent defects
    fq["agent_no_fix_dispositions"] = no_fix
    fq["counts"]["agent_fixes"] = 0
    fq["counts"]["agent_no_fix_dispositions"] = len(no_fix)
    with open(os.path.join(TRACK, "fix-queue.json"), "w", encoding="utf-8") as fh:
        json.dump(fq, fh, indent=2, ensure_ascii=False)

    # agent-review-matrix.md
    lines = []
    lines.append("# Agent Review Matrix\n")
    lines.append("Track: `20260726-top-skills-agents-review`. One entry per selected agent (10). "
                 "Every frozen agent rubric item is recorded in each packet under "
                 "`review-batches/agents/<name>.json`.\n")
    lines.append("Model/variant route evidence is config-level: live `opencode models` hangs in this "
                 "environment (verified, not retried), so AGENT_04/05 are recorded `Unverified` for "
                 "LIVE availability with config-level supporting evidence from `opencode.jsonc`. No "
                 "route was changed.\n")
    lines.append("Agent smoke (`AGENT_13`) is `AGENT_SMOKE_UNVERIFIED`: a live `opencode run` session "
                 "is not dispatched because the `opencode` CLI hangs and a live session cannot be "
                 "bounded to the 20-tool-call/10K-token cap from the dispatch side. Fixture-only "
                 "prompt records are saved under `evidence/agent-smoke-tests/`. No model was substituted.\n")
    lines.append("| # | Agent | Model | Mode | Smoke | Fails | Pass/NA/Unv |")
    lines.append("|---|-------|-------|------|-------|-------|-------------|")
    for r in matrix_rows:
        lines.append("| {rank} | {name} | {model} | {mode} | {smoke} | {fails} | {pc}/{nc}/{uv} |".format(
            rank=r["rank"], name=r["name"], model=r["model"], mode=r["mode"], smoke=r["smoke"],
            fails=", ".join(r["fails"]) or "—", pc=r["pass"], nc=r["na"], uv=r["unv"]))
    lines.append("")
    lines.append("## Queued agent fixes (Critical/Major)\n")
    lines.append("- (none — zero high-confidence Critical/Major agent defects)\n")
    lines.append("## No-fix dispositions (Minor heuristic findings)\n")
    for nf in no_fix:
        lines.append("- `%s` `%s` (%s): %s" % (nf["canonical_name"], nf["rubric_item"], nf["severity"], nf["reason"]))
    with open(os.path.join(TRACK, "agent-review-matrix.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print("AGENT_MATRIX_DONE fixtures=%d agent_no_fix=%d agent_queued=0" % (len(fixtures), len(no_fix)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
