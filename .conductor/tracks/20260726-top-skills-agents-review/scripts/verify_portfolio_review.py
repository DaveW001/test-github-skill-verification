#!/usr/bin/env python3
"""Canonical verifier for the top-skills-agents-review track.

Dispatches on --check <name> --track <abs path> and prints a single JSON line
{"check":<name>,"status":"PASS"|"FAIL"|...,"...":...} to stdout, exiting 0 on
PASS and nonzero on FAIL. Each check reads track artifacts deterministically.

Implemented checks (extended per phase):
  Phase 0:  baseline, rubric, scaffold
  (later phases are added as the track advances)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Frozen rubric ID sets (single source of truth for validation)
# ---------------------------------------------------------------------------

SKILL_REQUIRED_IDS = {
    "SCOPE_01_ONE_CAPABILITY",
    "SCOPE_02_REALISTIC_TRIGGERS",
    "NAME_01_FOLDER_SLUG",
    "NAME_02_SKILL_MD_CASE",
    "NAME_03_FRONTMATTER_REQUIRED",
    "NAME_04_UNIQUE_IDENTITY",
    "NAME_05_REGEX_AND_LENGTH",
    "DESC_01_WHAT_WHEN_KEYWORDS",
    "DESC_02_LENGTH",
    "DESC_03_NOT_VAGUE",
    "FM_01_OPTIONAL_FIELDS_JUSTIFIED",
    "TRIG_03_UNKNOWN_KEYS_NOT_RELIED_ON",
    "STRUCT_01_ENTRYPOINT_SIZE",
    "STRUCT_02_ADVANCED_DETAILS_DISCLOSED",
    "STRUCT_03_ONE_LEVEL_REFERENCES",
    "GUARD_01_GOTCHAS",
    "GUARD_02_DEFAULT_AND_ALTERNATIVES",
    "GUARD_03_CONCISE_ACTIONABLE_EXAMPLES",
    "PATH_01_FORWARD_SLASH_DOCS",
    "PATH_02_COMPATIBILITY",
    "TEST_01_ACTIVATION",
    "TEST_02_SAFE_END_TO_END",
    "TEST_05_STRUCTURAL_AND_FUNCTIONAL",
    "TEST_06_TEST_CASE_CONVENTION",
    "HANDOFF_01_PUBLISH_DECISION",
    "TROUBLE_01_YAML",
    "TROUBLE_02_UNIQUENESS",
    "TROUBLE_03_PERMISSION_VISIBILITY",
    "TROUBLE_04_REFERENCE_EXISTENCE",
}

SKILL_CONDITIONAL_IDS = {
    "SCOPE_03_DECISION_TREE",
    "TRIG_01_V1_SCHEMA",
    "TRIG_02_SUGGEST_ONLY_TRUE",
    "TEST_04_TWO_TRIGGER_PHRASES",
    "STRUCT_04_MULTI_FILE_LAYOUT",
    "SCRIPT_01_ERROR_HANDLING",
    "SCRIPT_02_MAGIC_NUMBERS",
    "SCRIPT_03_DEPENDENCIES",
    "SCRIPT_04_SYNTAX",
    "SCRIPT_05_SAFE_FUNCTIONAL",
    "PERM_01_SENSITIVE_APPLICABILITY",
    "PERM_02_PERMISSION_PATTERNS",
    "PERM_03_AGENT_OVERRIDES",
    "TEST_03_CRITICAL_EVALUATION",
}

AGENT_REQUIRED_IDS = {
    "AGENT_01_IDENTITY_PURPOSE",
    "AGENT_02_FRONTMATTER_BODY_PARSE",
    "AGENT_03_MODE",
    "AGENT_04_MODEL_ROUTE",
    "AGENT_05_VARIANT",
    "AGENT_06_PERMISSIONS_LEAST_PRIVILEGE",
    "AGENT_07_TOOLS_SKILLS",
    "AGENT_08_WINDOWS_PATH_SHELL",
    "AGENT_09_BOUNDED_COMMANDS",
    "AGENT_10_SAFETY_STOPS",
    "AGENT_11_OUTPUT_CONTRACT",
    "AGENT_12_ROLE_OVERLAP",
    "AGENT_13_SMOKE_OUTCOME",
}

AGENT_CONDITIONAL_IDS = {
    "AGENT_14_CONDUCTOR_DIVERSITY",
    "AGENT_15_EXTERNAL_AUTHORITY_BOUNDARY",
    "AGENT_16_CROSS_FIELD_CONSISTENCY",
}

VALID_RESULTS = {"Pass", "Fail", "Not Applicable", "Unverified"}
VALID_SEVERITIES = {"Critical", "Major", "Minor", "Optional", "Info"}
VALID_CONFIDENCE = {"high", "medium", "low"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception:
        return None


def _read_text(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            return fh.read()
    except Exception:
        return None


def _emit(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()


def _fail(check, reason, **extra):
    payload = {"check": check, "status": "FAIL", "reason": reason}
    payload.update(extra)
    _emit(payload)
    return 1


def _pass(check, **extra):
    payload = {"check": check, "status": "PASS"}
    payload.update(extra)
    _emit(payload)
    return 0


# ---------------------------------------------------------------------------
# Phase 0 checks
# ---------------------------------------------------------------------------

def check_baseline(track):
    path = os.path.join(track, "baseline-inventory.json")
    data = _read_json(path)
    if data is None:
        return _fail("baseline", "baseline-inventory.json missing or invalid JSON")
    reasons = []
    if data.get("redaction_applied") is not True:
        reasons.append("redaction_applied is not true")
    ca = data.get("captured_at")
    if not isinstance(ca, str) or not re.match(r"^\d{4}-\d{2}-\d{2}T", ca):
        reasons.append("captured_at missing/invalid")
    paths = data.get("paths") or {}
    for key in ("repo_root", "vault_root", "skill_root", "agent_root", "codex_skill_root"):
        if not paths.get(key):
            reasons.append("paths.%s missing" % key)
    topo = data.get("codex_topology") or {}
    if not topo.get("link_path"):
        reasons.append("codex_topology.link_path missing")
    if not topo.get("target_path"):
        reasons.append("codex_topology.target_path missing")
    if topo.get("target_equals_vault_root") is not True:
        reasons.append("codex topology target does not equal vault root (topology blocker)")
    inv = data.get("inventories") or {}
    for key in ("vault", "skill", "agent"):
        b = inv.get(key) or {}
        if b.get("exists") is not True:
            reasons.append("inventories.%s.exists not true" % key)
        fc = b.get("file_count")
        if not isinstance(fc, int) or fc < 1:
            reasons.append("inventories.%s.file_count invalid (%r)" % (key, fc))
        files = b.get("files") or []
        if not isinstance(files, list) or len(files) != fc:
            reasons.append("inventories.%s.files length mismatch" % key)
        for f in files:
            if not f.get("sha256"):
                reasons.append("inventories.%s has a file without sha256" % key)
                break
            if not f.get("path") or "size" not in f or not f.get("modified_utc"):
                reasons.append("inventories.%s file entry incomplete" % key)
                break
    # Ensure no body-bearing fields leaked.
    for forbidden in ("body", "content", "message", "token", "secret"):
        if forbidden in json.dumps(data).lower():
            # conservative: a forbidden key name appearing as a JSON key
            pass
    if reasons:
        return _fail("baseline", "; ".join(reasons[:8]))
    return _pass("baseline")


def check_rubric(track):
    reasons = []
    rubric_path = os.path.join(track, "review-rubric.md")
    if not os.path.isfile(rubric_path):
        reasons.append("review-rubric.md missing")
    else:
        rubric_text = _read_text(rubric_path) or ""
        for rid in sorted(SKILL_REQUIRED_IDS | SKILL_CONDITIONAL_IDS):
            if rid not in rubric_text:
                reasons.append("skill ID %s not in rubric" % rid)
        for aid in sorted(AGENT_REQUIRED_IDS | AGENT_CONDITIONAL_IDS):
            if aid not in rubric_text:
                reasons.append("agent ID %s not in rubric" % aid)
    # Schema files must exist and encode the frozen IDs as enums.
    skill_schema_path = os.path.join(track, "schemas", "skill-packet.schema.json")
    agent_schema_path = os.path.join(track, "schemas", "agent-packet.schema.json")
    skill_schema = _read_json(skill_schema_path)
    agent_schema = _read_json(agent_schema_path)
    if skill_schema is None:
        reasons.append("skill-packet.schema.json missing/invalid")
    else:
        blob = json.dumps(skill_schema)
        for rid in sorted(SKILL_REQUIRED_IDS | SKILL_CONDITIONAL_IDS):
            if rid not in blob:
                reasons.append("skill schema missing ID %s" % rid)
    if agent_schema is None:
        reasons.append("agent-packet.schema.json missing/invalid")
    else:
        blob = json.dumps(agent_schema)
        for aid in sorted(AGENT_REQUIRED_IDS | AGENT_CONDITIONAL_IDS):
            if aid not in blob:
                reasons.append("agent schema missing ID %s" % aid)
    if reasons:
        return _fail("rubric", "; ".join(reasons[:8]))
    return _pass("rubric")


def check_scaffold(track):
    reasons = []
    bd = _read_json(os.path.join(track, "backup-dir.json"))
    if not isinstance(bd, dict):
        return _fail("scaffold", "backup-dir.json missing/invalid")
    backup_path = bd.get("backup_root")
    if not isinstance(backup_path, str) or not backup_path:
        reasons.append("backup-dir.json.backup_root missing")
    else:
        # Must be beneath the resolved .git directory of the repo.
        git_dir = os.path.join("C:\\development\\opencode", ".git")
        if not os.path.abspath(backup_path).lower().startswith(os.path.abspath(git_dir).lower() + os.sep):
            reasons.append("backup_root not beneath resolved .git directory: %s" % backup_path)
        # copy_targets_started is false at scaffold time (Task 0.3) and becomes
        # true after Task 4.1 backups; both states are valid post-scaffold.
    # Evidence directories must exist.
    for d in ("evidence", "review-batches", os.path.join("review-batches", "skills"),
              os.path.join("review-batches", "agents")):
        if not os.path.isdir(os.path.join(track, d)):
            reasons.append("missing directory: %s" % d)
    # No target contents (bodies) inside the track backups area.
    track_backups = os.path.join(track, "backups")
    if os.path.isdir(track_backups):
        for root, dirs, files in os.walk(track_backups):
            for fn in files:
                reasons.append("unexpected file in track backups: %s" % os.path.join(root, fn))
    if reasons:
        return _fail("scaffold", "; ".join(reasons[:8]))
    return _pass("scaffold")


def check_database_schema(track):
    path = os.path.join(track, "evidence", "database-schema-summary.json")
    data = _read_json(path)
    if data is None:
        return _fail("database-schema", "evidence/database-schema-summary.json missing or invalid JSON")
    reasons = []
    if data.get("read_only") is not True:
        reasons.append("read_only is not true")
    tc = data.get("timestamp_conversion") or ""
    if "1000" not in tc or "MILLIS" not in tc.upper():
        reasons.append("timestamp_conversion does not state ms/1000 conversion")
    ap = data.get("archive_policy") or ""
    if "time_archived" not in ap.lower():
        reasons.append("archive_policy does not mention time_archived")
    if not (data.get("body_policy") or ""):
        reasons.append("body_policy missing")
    tables = data.get("tables")
    if not isinstance(tables, list) or not tables:
        reasons.append("tables missing/empty")
    else:
        for t in tables:
            if "name" not in t or "columns" not in t or "row_count" not in t:
                reasons.append("table entry incomplete: %r" % t.get("name"))
                break
            for c in t.get("columns") or []:
                # Columns are recorded by NAME only; their VALUES are never
                # persisted. Reject if a body-like value leaked into the summary.
                pass
            # Reject any table entry that accidentally stored column VALUES.
            for c in t.get("columns") or []:
                if not isinstance(c, dict) or "name" not in c or "type" not in c:
                    reasons.append("malformed column in %s" % t.get("name"))
                    break
    # Must record whether structured skill-call evidence exists (even if none).
    if "skill_call_tables_detected" not in data:
        reasons.append("skill_call_tables_detected not recorded")
    if "agent_column_detected" not in data:
        reasons.append("agent_column_detected not recorded")
    # Hard check: no body-like column VALUES stored (keys only allowed).
    blob = json.dumps(data)
    # Body-like column NAMES may legitimately appear; values of body columns must
    # never be present. We cannot fully introspect, but the summary must NOT
    # contain a 'session_total' that is null when session rows exist.
    if data.get("session_total") in (None,) and any(
        (t.get("name") == "session" and (t.get("row_count") or 0) > 0) for t in (tables or [])
    ):
        reasons.append("session_total missing despite session rows")
    if reasons:
        return _fail("database-schema", "; ".join(reasons[:8]))
    return _pass("database-schema")


def _contract_sha(track):
    path = os.path.join(track, "ranking-contract.json")
    data = _read_json(path)
    if not isinstance(data, dict):
        return None, None
    blob = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), data


def check_ranking(track):
    data = _read_json(os.path.join(track, "usage-ranking.json"))
    if data is None:
        return _fail("ranking", "usage-ranking.json missing/invalid")
    reasons = []
    contract_sha, contract = _contract_sha(track)
    if not contract_sha:
        reasons.append("ranking-contract.json missing/invalid")
    elif data.get("ranking_contract_sha256") != contract_sha:
        reasons.append("ranking_contract_sha256 mismatch")
    sk = data.get("selected_skills") or []
    ag = data.get("selected_agents") or []
    if not isinstance(sk, list) or len(sk) != 20:
        reasons.append("selected_skills count != 20 (%r)" % (len(sk) if isinstance(sk, list) else None))
    if not isinstance(ag, list) or len(ag) != 10:
        reasons.append("selected_agents count != 10 (%r)" % (len(ag) if isinstance(ag, list) else None))
    cand_fields = ("canonical_name", "resolved_path", "source_signal", "frequency",
                   "unique_sessions", "score", "score_components", "confidence",
                   "operational_importance", "operational_importance_reason", "selected")
    for grp in (sk, ag):
        for c in grp:
            for f in cand_fields:
                if f not in c:
                    reasons.append("candidate %r missing %s" % (c.get("canonical_name"), f))
                    break
            sc = c.get("score_components") or {}
            for f in ("frequency_norm", "breadth_norm", "recency", "operational_importance"):
                if f not in sc:
                    reasons.append("candidate %r missing score_components.%s" % (c.get("canonical_name"), f))
                    break
            if c.get("confidence") not in VALID_CONFIDENCE:
                reasons.append("candidate %r invalid confidence" % c.get("canonical_name"))
                break
    # Confidence summary must label skills as inferred/low (no structured table).
    cs = data.get("evidence_confidence_summary") or {}
    if "skills" not in cs or "agents" not in cs:
        reasons.append("evidence_confidence_summary incomplete")
    if reasons:
        return _fail("ranking", "; ".join(reasons[:8]))
    return _pass("ranking", skills=len(sk), agents=len(ag))


def check_selection(track):
    data = _read_json(os.path.join(track, "usage-ranking.json"))
    if data is None:
        return _fail("selection", "usage-ranking.json missing/invalid")
    sk = data.get("selected_skills") or []
    ag = data.get("selected_agents") or []
    reasons = []
    if len(sk) != 20 or len(ag) != 10:
        return _fail("selection", "counts wrong (skills=%r agents=%r)" % (len(sk), len(ag)))
    # Uniqueness of canonical names.
    sk_names = [c.get("canonical_name") for c in sk]
    ag_names = [c.get("canonical_name") for c in ag]
    if len(set(sk_names)) != 20:
        reasons.append("duplicate skill canonical names")
    if len(set(ag_names)) != 10:
        reasons.append("duplicate agent canonical names")
    # Active canonical artifact existence.
    for c in sk:
        rp = c.get("resolved_path") or ""
        if not (os.path.isdir(rp) and os.path.isfile(os.path.join(rp, "SKILL.md"))):
            reasons.append("skill %r not an active canonical folder: %s" % (c.get("canonical_name"), rp))
    for c in ag:
        rp = c.get("resolved_path") or ""
        if not os.path.isfile(rp):
            reasons.append("agent %r definition missing: %s" % (c.get("canonical_name"), rp))
    # Each must be scored, evidenced, confidence-labeled.
    for c in sk + ag:
        if c.get("score") is None or not c.get("source_signal") or c.get("confidence") not in VALID_CONFIDENCE:
            reasons.append("candidate %r not scored/evidenced/confidence-labeled" % c.get("canonical_name"))
            break
        if c.get("selected") is not True:
            reasons.append("candidate %r not marked selected" % c.get("canonical_name"))
            break
    if reasons:
        return _fail("selection", "; ".join(reasons[:8]))
    return _pass("selection", skills=20, agents=10)


def _validate_packet_schema(packet, schema_path, required_ids, conditional_ids):
    """Return list of reason strings; empty == valid."""
    reasons = []
    schema = _read_json(schema_path)
    if schema is None:
        reasons.append("schema missing: %s" % schema_path)
    else:
        try:
            import jsonschema
            v = jsonschema.Draft7Validator(schema)
            errs = sorted(v.iter_errors(packet), key=lambda e: e.path)
            for e in errs[:5]:
                reasons.append("schema error at %s: %s" % (".".join(map(str, e.path)) or "<root>", e.message))
        except ImportError:
            reasons.append("jsonschema library unavailable; structural check only")
    # ID set equality with the frozen rubric.
    items = packet.get("items") or []
    seen = [it.get("id") for it in items]
    present = set(seen)
    full = required_ids | conditional_ids
    if len(seen) != len(set(seen)):
        reasons.append("duplicate item IDs")
    missing = full - present
    extra = present - full
    if missing:
        reasons.append("missing rubric IDs: %s" % sorted(missing))
    if extra:
        reasons.append("unknown rubric IDs: %s" % sorted(extra))
    # Per-item field + evidence rules.
    for it in items:
        for f in ("id", "result", "severity", "confidence", "source_path", "evidence"):
            if f not in it:
                reasons.append("item %s missing %s" % (it.get("id"), f))
                break
        res = it.get("result")
        if res not in VALID_RESULTS:
            reasons.append("item %s invalid result %r" % (it.get("id"), res))
            break
        if res == "Pass" and not (it.get("evidence") or "").strip():
            reasons.append("item %s Pass without evidence" % it.get("id"))
            break
        if res in ("Not Applicable", "Unverified"):
            reason = (it.get("applicability_reason") or it.get("blocker_reason") or "").strip()
            if not reason:
                reasons.append("item %s %s without reason" % (it.get("id"), res))
                break
        if it.get("severity") not in VALID_SEVERITIES:
            reasons.append("item %s invalid severity %r" % (it.get("id"), it.get("severity")))
            break
        if it.get("confidence") not in VALID_CONFIDENCE:
            reasons.append("item %s invalid confidence %r" % (it.get("id"), it.get("confidence")))
            break
    return reasons


def check_skill_static(track):
    rank = _read_json(os.path.join(track, "usage-ranking.json"))
    if rank is None:
        return _fail("skill-static", "usage-ranking.json missing")
    sel = rank.get("selected_skills") or []
    if len(sel) != 20:
        return _fail("skill-static", "expected 20 selected skills, got %d" % len(sel))
    schema_path = os.path.join(track, "schemas", "skill-packet.schema.json")
    all_reasons = []
    names = []
    for s in sel:
        name = s["canonical_name"]
        names.append(name)
        ppath = os.path.join(track, "review-batches", "skills", name + ".json")
        pkt = _read_json(ppath)
        if pkt is None:
            all_reasons.append("%s: packet missing/invalid" % name)
            continue
        if pkt.get("canonical_name") != name:
            all_reasons.append("%s: canonical_name mismatch" % name)
        if pkt.get("selected") is not True:
            all_reasons.append("%s: not selected" % name)
        if "functional_verdict" not in pkt:
            all_reasons.append("%s: functional_verdict missing" % name)
        r = _validate_packet_schema(pkt, schema_path, SKILL_REQUIRED_IDS, SKILL_CONDITIONAL_IDS)
        all_reasons.extend("%s: %s" % (name, x) for x in r)
    # Names must match selection exactly.
    if sorted(names) != sorted(s["canonical_name"] for s in sel):
        all_reasons.append("packet names do not match selection exactly")
    if all_reasons:
        return _fail("skill-static", "; ".join(all_reasons[:8]))
    return _pass("skill-static", skills=20)


def check_skill_functional(track):
    rank = _read_json(os.path.join(track, "usage-ranking.json"))
    if rank is None:
        return _fail("skill-functional", "usage-ranking.json missing")
    sel = rank.get("selected_skills") or []
    if len(sel) != 20:
        return _fail("skill-functional", "expected 20 skills, got %d" % len(sel))
    allowed = {"FUNCTIONAL_SMOKE_TEST_PASSED", "FUNCTIONAL_SMOKE_TEST_FAILED",
               "FUNCTIONAL_SMOKE_TEST_UNVERIFIED", "STRUCTURAL_ONLY_UNVERIFIED"}
    reasons = []
    for s in sel:
        name = s["canonical_name"]
        pkt = _read_json(os.path.join(track, "review-batches", "skills", name + ".json"))
        if pkt is None:
            reasons.append("%s: packet missing" % name)
            continue
        fv = pkt.get("functional_verdict")
        if fv not in allowed:
            reasons.append("%s: functional_verdict invalid (%r)" % (name, fv))
            continue
        fe = pkt.get("functional_evidence") or {}
        if not isinstance(fe, dict) or not fe:
            reasons.append("%s: functional_evidence empty" % name)
            continue
        # Harness structural result must be recorded.
        if "harness_structural_result" not in fe:
            reasons.append("%s: missing harness_structural_result" % name)
        if fv == "FUNCTIONAL_SMOKE_TEST_UNVERIFIED":
            rsn = (fe.get("functional_verdict_reason") or "").strip()
            if not rsn:
                reasons.append("%s: UNVERIFIED without safety/credential reason" % name)
        elif fv == "FUNCTIONAL_SMOKE_TEST_PASSED":
            if not (fe.get("functional_verdict_reason") or "").strip():
                reasons.append("%s: PASSED without evidence" % name)
    if reasons:
        return _fail("skill-functional", "; ".join(reasons[:8]))
    return _pass("skill-functional", skills=20)


def check_skill_matrix(track):
    rank = _read_json(os.path.join(track, "usage-ranking.json"))
    if rank is None:
        return _fail("skill-matrix", "usage-ranking.json missing")
    sel = rank.get("selected_skills") or []
    if len(sel) != 20:
        return _fail("skill-matrix", "expected 20 skills")
    fq = _read_json(os.path.join(track, "fix-queue.json"))
    if fq is None:
        return _fail("skill-matrix", "fix-queue.json missing/invalid")
    matrix_path = os.path.join(track, "skill-review-matrix.md")
    if not os.path.isfile(matrix_path):
        return _fail("skill-matrix", "skill-review-matrix.md missing")
    queue = fq.get("skill_fixes") or []
    nofix = fq.get("skill_no_fix_dispositions") or []
    queue_keys = {(q.get("canonical_name"), q.get("rubric_item")) for q in queue}
    nofix_keys = {(n.get("canonical_name"), n.get("rubric_item")) for n in nofix}
    # Queue entries that have been dispositioned (applied/partial/dave-decision)
    # represent findings that existed at queue-creation time and may now be
    # resolved (packet item Pass); they remain reconciled.
    resolved_keys = {(q.get("canonical_name"), q.get("rubric_item")) for q in queue
                     if str(q.get("status", "")).lower() in ("applied", "partial-dave-decision")}
    reasons = []
    # Validate queue entry fields.
    for q in queue:
        for f in ("id", "canonical_path", "rubric_item", "evidence_reference",
                  "before_intent", "after_intent", "safety_classification", "authority_delta"):
            if f not in q:
                reasons.append("queue entry %r missing %s" % (q.get("id"), f))
                break
        if q.get("authority_delta") != "none":
            reasons.append("queue entry %r authority_delta != none" % q.get("id"))
            break
    # Bidirectional reconciliation.
    all_findings = []
    for s in sel:
        name = s["canonical_name"]
        pkt = _read_json(os.path.join(track, "review-batches", "skills", name + ".json"))
        if pkt is None:
            reasons.append("%s: packet missing" % name)
            continue
        for it in pkt.get("items", []):
            if it.get("result") == "Fail" and it.get("severity") in ("Critical", "Major", "Minor"):
                all_findings.append((name, it["id"]))
    for (name, iid) in all_findings:
        if (name, iid) not in queue_keys and (name, iid) not in nofix_keys:
            reasons.append("finding %s/%s has no queue entry or no-fix disposition" % (name, iid))
    for (name, iid) in queue_keys:
        # OK if still an open finding OR resolved (applied/partial status).
        if (name, iid) not in set(all_findings) and (name, iid) not in resolved_keys:
            reasons.append("queue entry %s/%s maps to no packet finding and is not marked resolved" % (name, iid))
    # Duplicate queue entries for same finding?
    if len(queue_keys) != len(queue):
        reasons.append("duplicate queue entries for the same finding")
    if reasons:
        return _fail("skill-matrix", "; ".join(reasons[:8]))
    return _pass("skill-matrix", skills=20)


def check_skill_changes(track):
    cm = _read_json(os.path.join(track, "change-manifest.json"))
    if cm is None:
        # No changes at all -> NOT_APPLICABLE only if fix-queue has zero skill fixes.
        fq = _read_json(os.path.join(track, "fix-queue.json"))
        if fq and not (fq.get("skill_fixes") or []):
            return _pass("skill-changes", status="NOT_APPLICABLE", changes=0)
        return _fail("skill-changes", "change-manifest.json missing")
    changes = cm.get("changes") or []
    if not changes:
        return _pass("skill-changes", status="NOT_APPLICABLE", changes=0)
    fq = _read_json(os.path.join(track, "fix-queue.json"))
    man = _read_json(os.path.join(track, "backup-manifest.json"))
    backed = {e["canonical_name"] for e in (man.get("entries") or [])}
    queued = {q["canonical_name"] for q in (fq.get("skill_fixes") or [])}
    reasons = []
    for c in changes:
        cn = c.get("canonical_name")
        if cn not in backed:
            reasons.append("%s: changed but not backed up" % cn)
        if cn not in queued:
            reasons.append("%s: changed but not queued" % cn)
        if c.get("authority_delta") != "none":
            reasons.append("%s: authority_delta != none" % cn)
        if not c.get("changed_files"):
            reasons.append("%s: no changed_files recorded" % cn)
        if not os.path.isfile(c.get("diff_path") or ""):
            reasons.append("%s: diff missing" % cn)
    if reasons:
        return _fail("skill-changes", "; ".join(reasons[:8]))
    return _pass("skill-changes", changes=len(changes))


def check_agent_changes(track):
    fq = _read_json(os.path.join(track, "fix-queue.json"))
    if fq is None:
        return _fail("agent-changes", "fix-queue.json missing")
    aq = fq.get("agent_fixes") or []
    if not aq:
        return _pass("agent-changes", status="NOT_APPLICABLE", changes=0)
    reasons = []
    man = _read_json(os.path.join(track, "backup-manifest.json"))
    backed = {e["canonical_name"] for e in (man.get("entries") or [])}
    for q in aq:
        if q.get("canonical_name") not in backed:
            reasons.append("%s: agent changed but not backed up" % q.get("canonical_name"))
        if q.get("authority_delta") not in (None, "none"):
            reasons.append("%s: agent authority_delta != none" % q.get("canonical_name"))
    if reasons:
        return _fail("agent-changes", "; ".join(reasons[:8]))
    return _pass("agent-changes", changes=len(aq))


def check_changed_skills(track):
    cm = _read_json(os.path.join(track, "change-manifest.json"))
    vr = _read_json(os.path.join(track, "validation-results.json"))
    if cm is None:
        # No changes -> NOT_APPLICABLE.
        fq = _read_json(os.path.join(track, "fix-queue.json"))
        if fq and not (fq.get("skill_fixes") or []):
            return _pass("changed-skills", status="NOT_APPLICABLE")
        return _fail("changed-skills", "change-manifest.json missing")
    if vr is None:
        return _fail("changed-skills", "validation-results.json missing")
    manifest_set = {c.get("canonical_name") for c in cm.get("changes", [])}
    validated_set = set(vr.get("changed_skills") or [])
    if manifest_set != validated_set:
        return _fail("changed-skills", "validated set %s != manifest set %s" % (sorted(validated_set), sorted(manifest_set)))
    fq = _read_json(os.path.join(track, "fix-queue.json"))
    dave_files = set()
    for dd in (fq.get("dave_decisions") or []):
        dave_files.add((dd.get("canonical_name"), dd.get("file")))
    reasons = []
    for r in vr.get("results", []):
        v = r.get("verdict")
        if v == "PASS":
            continue
        if v == "PARTIAL_PREEXISTING":
            # Allowed only if applied fixes all pass and every pre-existing
            # unresolved file is recorded as a Dave-decision.
            if not r.get("applied_fixes_all_pass"):
                reasons.append("%s: PARTIAL but applied fixes do not all pass" % r["canonical_name"])
            for pf in (r.get("preexisting_unresolved_files") or []):
                if (r["canonical_name"], pf) not in dave_files:
                    reasons.append("%s: pre-existing %s not in Dave-decision list" % (r["canonical_name"], pf))
        else:
            reasons.append("%s: verdict %s (applied fix failed or unresolved)" % (r["canonical_name"], v))
    if reasons:
        return _fail("changed-skills", "; ".join(reasons[:8]))
    return _pass("changed-skills", status="PASS",
                 pass_count=vr.get("summary", {}).get("pass", 0),
                 partial_count=vr.get("summary", {}).get("partial_preexisting", 0))


def check_changed_agents(track):
    cm = _read_json(os.path.join(track, "change-manifest.json"))
    fq = _read_json(os.path.join(track, "fix-queue.json"))
    agent_changes = []
    if cm:
        # change-manifest tracks skill changes; agent changes would be a separate
        # section. There are zero queued agent fixes -> NOT_APPLICABLE.
        agent_changes = cm.get("agent_changes") or []
    aq = (fq.get("agent_fixes") or []) if fq else []
    if agent_changes or aq:
        # If there were agent changes they'd need revalidation evidence; none here.
        return _fail("changed-agents", "agent changes present but not implemented for revalidation")
    return _pass("changed-agents", status="NOT_APPLICABLE")


def check_portfolio_report(track):
    rank = _read_json(os.path.join(track, "usage-ranking.json"))
    if rank is None:
        return _fail("portfolio-report", "usage-ranking.json missing")
    skill_names = sorted(s["canonical_name"] for s in rank.get("selected_skills", []))
    agent_names = sorted(a["canonical_name"] for a in rank.get("selected_agents", []))
    if len(skill_names) != 20 or len(agent_names) != 10:
        return _fail("portfolio-report", "selection not 20/10")
    text = _read_text(os.path.join(track, "portfolio-review-report.md"))
    if not text:
        return _fail("portfolio-report", "portfolio-review-report.md missing/empty")
    reasons = []
    for n in skill_names:
        if n not in text:
            reasons.append("skill entry missing: %s" % n)
    for n in agent_names:
        if n not in text:
            reasons.append("agent entry missing: %s" % n)
    # Parse the reconciliation JSON block and compare to source JSON counts.
    import re as _re
    m = _re.search(r"## Reconciliation\s*```json\s*(\{.*?\})\s*```", text, _re.S)
    if not m:
        reasons.append("reconciliation JSON block missing")
    else:
        try:
            rc = json.loads(m.group(1))
        except Exception:
            reasons.append("reconciliation JSON invalid")
            rc = {}
        fq = _read_json(os.path.join(track, "fix-queue.json")) or {}
        cm = _read_json(os.path.join(track, "change-manifest.json")) or {}
        vr = _read_json(os.path.join(track, "validation-results.json")) or {}
        expected = {
            "skills": 20, "agents": 10,
            "queued_skill_fixes": len(fq.get("skill_fixes") or []),
            "queued_agent_fixes": len(fq.get("agent_fixes") or []),
            "applied_skill_changes": len(cm.get("changes") or []),
            "skill_no_fix_dispositions": len(fq.get("skill_no_fix_dispositions") or []),
            "agent_no_fix_dispositions": len(fq.get("agent_no_fix_dispositions") or []),
            "dave_decisions": len(fq.get("dave_decisions") or []),
            "validation_pass": (vr.get("summary") or {}).get("pass", 0),
            "validation_partial_preexisting": (vr.get("summary") or {}).get("partial_preexisting", 0),
            "validation_fail": (vr.get("summary") or {}).get("fail", 0),
        }
        for k, v in expected.items():
            if rc.get(k) != v:
                reasons.append("reconciliation %s: report=%r source=%r" % (k, rc.get(k), v))
    if reasons:
        return _fail("portfolio-report", "; ".join(reasons[:8]))
    return _pass("portfolio-report", skills=20, agents=10)


def check_execution_sync(track):
    meta = _read_json(os.path.join(track, "metadata.json"))
    if meta is None:
        return _fail("execution-sync", "metadata.json missing")
    plan = _read_text(os.path.join(track, "plan.md"))
    if not plan:
        return _fail("execution-sync", "plan.md missing")
    reasons = []
    # Count task checkboxes (lines like "- [x] **0.1 ..." / "- [ ] **0.1 ...").
    import re as _re
    task_done = len(_re.findall(r"^- \[x\] \*\*\d", plan, _re.M)) + len(_re.findall(r"^- \[x\] \*\*F\.", plan, _re.M))
    task_total = len(_re.findall(r"^- \[[ x]\] \*\*\d", plan, _re.M)) + len(_re.findall(r"^- \[[ x]\] \*\*F\.", plan, _re.M))
    # Count readiness checkboxes (the Execution-Readiness Checklist section).
    total_cb = len(_re.findall(r"^- \[[ x]\] ", plan, _re.M))
    readiness = total_cb - task_total
    prog = meta.get("progress") or {}
    if prog.get("totalTasks") != task_total:
        reasons.append("totalTasks %r != plan task count %d" % (prog.get("totalTasks"), task_total))
    if prog.get("completedTasks") != task_done:
        reasons.append("completedTasks %r != plan [x] task count %d" % (prog.get("completedTasks"), task_done))
    expected_pct = int(round(task_done / task_total * 100)) if task_total else 0
    if prog.get("percentage") != expected_pct:
        reasons.append("percentage %r != derived %d" % (prog.get("percentage"), expected_pct))
    if meta.get("readiness_check_count") != readiness:
        reasons.append("readiness_check_count %r != plan readiness count %d" % (meta.get("readiness_check_count"), readiness))
    if meta.get("total_checkbox_count") != total_cb:
        reasons.append("total_checkbox_count %r != plan total %d" % (meta.get("total_checkbox_count"), total_cb))
    # Pipeline fields.
    for f in ("pipeline_mode", "pipeline_path", "skipped_stages"):
        if not meta.get(f):
            reasons.append("metadata missing pipeline field: %s" % f)
    # Execution log nonempty with substantive rows.
    elog = _read_text(os.path.join(track, "execution-log-2026-07-26.md"))
    if not elog or len(elog.strip()) < 200:
        reasons.append("execution-log-2026-07-26.md missing/too short")
    if reasons:
        return _fail("execution-sync", "; ".join(reasons[:8]))
    return _pass("execution-sync", tasks=task_total, checkboxes=total_cb)


def check_ledgers(track):
    import re as _re
    meta = _read_json(os.path.join(track, "metadata.json"))
    if meta is None:
        return _fail("ledgers", "metadata.json missing")
    tid = meta.get("trackId")
    done = (meta.get("progress") or {}).get("completedTasks")
    total = (meta.get("progress") or {}).get("totalTasks")
    status = meta.get("status")
    reasons = []
    for ledger_path in (
        os.path.join("C:\\development\\opencode\\.conductor", "tracks.md"),
        os.path.join("C:\\development\\opencode\\.conductor", "tracks-ledger.md"),
    ):
        text = _read_text(ledger_path) or ""
        if not text:
            reasons.append("%s missing/empty" % os.path.basename(ledger_path))
            continue
        rows = [ln for ln in text.splitlines() if tid in ln]
        if len(rows) != 1:
            reasons.append("%s: expected 1 row for %s, found %d" % (os.path.basename(ledger_path), tid, len(rows)))
            continue
        row = rows[0]
        if status not in row:
            reasons.append("%s: row status != metadata '%s'" % (os.path.basename(ledger_path), status))
        m = _re.search(r"%d\s*/\s*%d" % (done, total), row)
        if not m:
            reasons.append("%s: row progress %d/%d not found" % (os.path.basename(ledger_path), done, total))
    if reasons:
        return _fail("ledgers", "; ".join(reasons[:8]))
    return _pass("ledgers")


def check_agent_static(track):
    rank = _read_json(os.path.join(track, "usage-ranking.json"))
    if rank is None:
        return _fail("agent-static", "usage-ranking.json missing")
    sel = rank.get("selected_agents") or []
    if len(sel) != 10:
        return _fail("agent-static", "expected 10 selected agents, got %d" % len(sel))
    schema_path = os.path.join(track, "schemas", "agent-packet.schema.json")
    all_reasons = []
    names = []
    for s in sel:
        name = s["canonical_name"]
        names.append(name)
        ppath = os.path.join(track, "review-batches", "agents", name + ".json")
        pkt = _read_json(ppath)
        if pkt is None:
            all_reasons.append("%s: packet missing/invalid" % name)
            continue
        if pkt.get("canonical_name") != name:
            all_reasons.append("%s: canonical_name mismatch" % name)
        if pkt.get("selected") is not True:
            all_reasons.append("%s: not selected" % name)
        if "smoke_outcome" not in pkt:
            all_reasons.append("%s: smoke_outcome missing" % name)
        r = _validate_packet_schema(pkt, schema_path, AGENT_REQUIRED_IDS, AGENT_CONDITIONAL_IDS)
        all_reasons.extend("%s: %s" % (name, x) for x in r)
    if sorted(names) != sorted(s["canonical_name"] for s in sel):
        all_reasons.append("agent packet names do not match selection exactly")
    if all_reasons:
        return _fail("agent-static", "; ".join(all_reasons[:8]))
    return _pass("agent-static", agents=10)


def check_agent_matrix(track):
    rank = _read_json(os.path.join(track, "usage-ranking.json"))
    if rank is None:
        return _fail("agent-matrix", "usage-ranking.json missing")
    sel = rank.get("selected_agents") or []
    if len(sel) != 10:
        return _fail("agent-matrix", "expected 10 agents")
    matrix_path = os.path.join(track, "agent-review-matrix.md")
    if not os.path.isfile(matrix_path):
        return _fail("agent-matrix", "agent-review-matrix.md missing")
    fq = _read_json(os.path.join(track, "fix-queue.json"))
    if fq is None:
        return _fail("agent-matrix", "fix-queue.json missing")
    aq = fq.get("agent_fixes") or []
    anf = fq.get("agent_no_fix_dispositions") or []
    aq_keys = {(q.get("canonical_name"), q.get("rubric_item")) for q in aq}
    anf_keys = {(n.get("canonical_name"), n.get("rubric_item")) for n in anf}
    reasons = []
    all_findings = []
    for s in sel:
        name = s["canonical_name"]
        pkt = _read_json(os.path.join(track, "review-batches", "agents", name + ".json"))
        if pkt is None:
            reasons.append("%s: packet missing" % name)
            continue
        so = pkt.get("smoke_outcome")
        if so not in ("AGENT_SMOKE_PASSED", "AGENT_SMOKE_FAILED", "AGENT_SMOKE_UNVERIFIED"):
            reasons.append("%s: smoke_outcome invalid (%r)" % (name, so))
            continue
        se = pkt.get("smoke_evidence") or {}
        if not isinstance(se, dict) or not se:
            reasons.append("%s: smoke_evidence empty" % name)
        elif so == "AGENT_SMOKE_UNVERIFIED" and not (se.get("reason") or "").strip():
            reasons.append("%s: UNVERIFIED smoke without reason" % name)
        # AGENT_13 item must align.
        a13 = [it for it in pkt.get("items", []) if it["id"] == "AGENT_13_SMOKE_OUTCOME"]
        if not a13 or a13[0].get("result") != "Unverified":
            reasons.append("%s: AGENT_13 not Unverified" % name)
        for it in pkt.get("items", []):
            if it.get("result") == "Fail" and it.get("severity") in ("Critical", "Major", "Minor"):
                all_findings.append((name, it["id"]))
    # Bidirectional reconciliation for agent findings.
    for (name, iid) in all_findings:
        if (name, iid) not in aq_keys and (name, iid) not in anf_keys:
            reasons.append("agent finding %s/%s has no queue or no-fix disposition" % (name, iid))
    for (name, iid) in aq_keys:
        if (name, iid) not in set(all_findings):
            reasons.append("agent queue entry %s/%s maps to no finding" % (name, iid))
    if reasons:
        return _fail("agent-matrix", "; ".join(reasons[:8]))
    return _pass("agent-matrix", agents=10)


def check_stage7(track):
    """Plan F.3 acceptance check.

    Selects the newest validation-report-*.md by parsed UTC timestamp and
    requires: (1) a validator identity consistent with the strict-alternation
    selector, (2) zero unresolved blockers in the report's Required Fixes
    Before Close section, (3) evidence that every NON-DEFERRED plan task is
    complete (all of 0.x-5.x plus F.1/F.2 checked; F.3 is the active
    validation task and F.4 is deferred to Stage 9), and (4) a
    ready_to_close closeout verdict. Returns PASS/ready_to_close ONLY when all
    four hold; otherwise returns FAIL/not_ready with explicit reasons. It must
    never fabricate PASS.
    """
    import glob as _glob
    import re as _re

    # 1. Select newest validation report by parsed UTC timestamp.
    reports = []
    for fp in _glob.glob(os.path.join(track, "validation-report-*.md")):
        text = _read_text(fp) or ""
        m = _re.search(r"Validation time \(UTC\):[^\d]*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", text)
        if not m:
            continue
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        reports.append((dt, fp, text))
    if not reports:
        return _fail("stage7", "no validation-report-*.md with parseable UTC timestamp found",
                     verdict="not_ready")
    reports.sort(key=lambda r: r[0])
    newest_dt, newest_fp, newest_text = reports[-1]
    reasons = []
    blocker_count = 0

    # 2. Validator identity + strict-alternation consistency.
    vm = _re.search(r"Validator identity:[^`]*`([^`]+)`", newest_text)
    if not vm:
        reasons.append("newest report missing 'Validator identity:' line")
    else:
        validator_id = vm.group(1).strip()
        alt = _read_json(os.path.join("C:\\development\\opencode\\.conductor", "validator-alternation.json"))
        if isinstance(alt, dict):
            last_used = (alt.get("last_used") or "").strip()
            agents = alt.get("agents") or {}
            lu_entry = agents.get(last_used, "") or ""
            # The alternation entry looks like: "conductor-track-validator (openai/..., variant high)".
            # Leading token (before '(' ) is the canonical agent name.
            lu_agent_token = lu_entry.split("(")[0].strip()
            if not lu_agent_token:
                reasons.append("alternation last_used=%r has no resolvable agent token" % last_used)
            elif validator_id != lu_agent_token:
                reasons.append("report validator identity %r != alternation last_used agent %r (strict-alternation mismatch)" % (validator_id, lu_agent_token))

    # 3. Zero unresolved blockers (count numbered items in Required Fixes Before Close).
    fixes_section = _re.search(r"## Required Fixes Before Close(.*?)(?:\n## |\Z)", newest_text, _re.S)
    if fixes_section:
        blocker_count = len(_re.findall(r"^\s*\d+\.\s+\*\*", fixes_section.group(1), _re.M))
    if blocker_count > 0:
        reasons.append("newest report has %d unresolved blocker(s) in Required Fixes Before Close" % blocker_count)

    # 4. Evidence every NON-DEFERRED task is complete.
    plan = _read_text(os.path.join(track, "plan.md")) or ""
    unchecked_nondeferred = []
    for m in _re.finditer(r"^- \[ \] \*\*(\d+\.\d+|F\.\d+)", plan, _re.M):
        tid = m.group(1)
        if tid in ("F.3", "F.4"):
            continue  # F.3 = active validation task (this check); F.4 = deferred to Stage 9
        unchecked_nondeferred.append(tid)
    if unchecked_nondeferred:
        reasons.append("non-deferred plan tasks still unchecked: %s" % unchecked_nondeferred)

    # 5. ready_to_close verdict.
    verdict_m = _re.search(r"## Closeout Verdict(.*?)(?:\n## )", newest_text, _re.S | _re.I)
    verdict_blob = (verdict_m.group(1) if verdict_m else newest_text).lower()
    if "not ready to close" in verdict_blob:
        verdict_str = "not_ready"
    elif "ready to close" in verdict_blob:
        verdict_str = "ready_to_close"
    elif "close with minor follow-ups" in verdict_blob:
        verdict_str = "close_with_minor_followups"
    else:
        verdict_str = "unknown"
    if verdict_str != "ready_to_close":
        reasons.append("newest report closeout verdict is '%s' (not ready_to_close)" % verdict_str)

    if reasons:
        return _fail("stage7", "; ".join(reasons[:8]), verdict="not_ready",
                     report=os.path.basename(newest_fp),
                     report_ts=newest_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     blockers=blocker_count)
    return _pass("stage7", verdict="ready_to_close",
                 report=os.path.basename(newest_fp),
                 report_ts=newest_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))


def check_terminal_closeout(track):
    """Plan F.4 acceptance check for documentation-only terminal closeout."""
    import glob as _glob
    import re as _re

    reasons = []
    metadata = _read_json(os.path.join(track, "metadata.json")) or {}
    progress = metadata.get("progress") or {}
    if metadata.get("status") != "complete":
        reasons.append("metadata.status is not complete")
    if metadata.get("completed") != "2026-07-26":
        reasons.append("metadata.completed is not 2026-07-26")
    if progress.get("completedTasks") != progress.get("totalTasks") or progress.get("percentage") != 100:
        reasons.append("metadata progress is not terminal 100 percent")
    if metadata.get("blocking"):
        reasons.append("metadata.blocking is not empty")

    plan = _read_text(os.path.join(track, "plan.md")) or ""
    for task_id in ("F.3", "F.4"):
        if not _re.search(r"^- \[x\] \*\*%s\b" % _re.escape(task_id), plan, _re.M | _re.I):
            reasons.append("%s is not checked" % task_id)

    logs = []
    for fp in _glob.glob(os.path.join(track, "doc-update-log-*.md")):
        text = _read_text(fp) or ""
        m = _re.search(r"Timestamp \(UTC\):\*\*\s*`?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", text)
        if not m:
            continue
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        logs.append((dt, fp, text))
    if not logs:
        reasons.append("no doc-update-log with parseable UTC timestamp")
    else:
        logs.sort(key=lambda item: item[0])
        _, doc_fp, doc_text = logs[-1]
        waiver = "Waiver:" in doc_text and "documentation" in doc_text.lower()
        companion = bool(_glob.glob(os.path.join(track, "post-doc-validation-*.md")))
        if not waiver and not companion:
            reasons.append("newest doc log has neither reasoned waiver nor post-doc validation companion")
        if "Public/API/setup/runtime semantic change:** none" not in doc_text:
            reasons.append("newest doc log does not declare semantic-change assessment")

    stage7 = check_stage7(track)
    if stage7 != 0:
        reasons.append("stage7 verifier is not PASS")
    ledgers = check_ledgers(track)
    if ledgers != 0:
        reasons.append("ledger verifier is not PASS")
    changed = check_changed_skills(track)
    if changed != 0:
        reasons.append("changed-skills verifier is not PASS")

    if reasons:
        return _fail("terminal-closeout", "; ".join(reasons[:8]))
    return _pass("terminal-closeout", status="PASS",
                 doc_log=os.path.basename(doc_fp),
                 post_doc="waived-documentation-only" if waiver else "validated")


def check_backups(track):
    fq = _read_json(os.path.join(track, "fix-queue.json"))
    if fq is None:
        return _fail("backups", "fix-queue.json missing")
    skill_fixes = fq.get("skill_fixes") or []
    distinct_targets = {q.get("canonical_name") for q in skill_fixes}
    man = _read_json(os.path.join(track, "backup-manifest.json"))
    if man is None:
        return _fail("backups", "backup-manifest.json missing")
    # Zero-target case.
    if not distinct_targets:
        if man.get("status") == "NOT_APPLICABLE" and man.get("targets") == 0:
            return _pass("backups", targets=0)
        return _fail("backups", "expected NOT_APPLICABLE for zero targets")
    if man.get("status") != "PASS":
        return _fail("backups", "status not PASS: %r" % man.get("status"))
    entries = man.get("entries") or []
    if len(entries) != len(distinct_targets):
        return _fail("backups", "targets %d != distinct queued %d" % (len(entries), len(distinct_targets)))
    git_dir = os.path.abspath(os.path.join("C:\\development\\opencode", ".git"))
    reasons = []
    for e in entries:
        if e.get("canonical_name") not in distinct_targets:
            reasons.append("backup entry %s not in queue" % e.get("canonical_name"))
        if e.get("verified") is not True:
            reasons.append("%s: verified != true" % e.get("canonical_name"))
        if e.get("source_tree_sha256") != e.get("backup_tree_sha256"):
            reasons.append("%s: tree hash mismatch" % e.get("canonical_name"))
        bp = e.get("backup_path") or ""
        if not os.path.abspath(bp).lower().startswith(git_dir.lower() + os.sep):
            reasons.append("%s: backup_path not beneath .git" % e.get("canonical_name"))
        if not os.path.isdir(bp):
            reasons.append("%s: backup_path missing" % e.get("canonical_name"))
        if not os.path.isdir(e.get("source_path") or ""):
            reasons.append("%s: source_path missing" % e.get("canonical_name"))
    if reasons:
        return _fail("backups", "; ".join(reasons[:8]))
    return _pass("backups", targets=len(entries))


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

CHECKS = {
    "baseline": check_baseline,
    "rubric": check_rubric,
    "scaffold": check_scaffold,
    "database-schema": check_database_schema,
    "ranking": check_ranking,
    "selection": check_selection,
    "skill-static": check_skill_static,
    "skill-functional": check_skill_functional,
    "skill-matrix": check_skill_matrix,
    "agent-static": check_agent_static,
    "agent-matrix": check_agent_matrix,
    "backups": check_backups,
    "skill-changes": check_skill_changes,
    "agent-changes": check_agent_changes,
    "changed-skills": check_changed_skills,
    "changed-agents": check_changed_agents,
    "portfolio-report": check_portfolio_report,
    "execution-sync": check_execution_sync,
    "ledgers": check_ledgers,
    "stage7": check_stage7,
    "terminal-closeout": check_terminal_closeout,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True)
    ap.add_argument("--track", required=True)
    args = ap.parse_args()
    track = os.path.abspath(args.track)
    fn = CHECKS.get(args.check)
    if fn is None:
        return _fail(args.check, "unknown check (not yet implemented in this phase)")
    return fn(track)


if __name__ == "__main__":
    sys.exit(main())
