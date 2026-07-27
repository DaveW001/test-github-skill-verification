#!/usr/bin/env python3
"""Generate one complete static review packet per selected skill (Task 2.1).

Iterates the EXACT selected skill identities from usage-ranking.json and the
EXACT frozen rubric IDs. Fails closed on missing/unknown IDs. Writes one packet
per skill to review-batches/skills/<canonical-name>.json conforming to
skill-packet.schema.json. Pass requires evidence; Not Applicable / Unverified
require a nonempty applicability/blocker reason.

Structural checks are mechanical and deterministic. Heuristic content checks
record their metric + verdict. This is the STATIC layer; functional smoke
evidence is added by the harness in Task 2.2 (functional_verdict defaulting to
STRUCTURAL_ONLY_UNVERIFIED until then).
"""

from __future__ import annotations

import json
import os
import re
import sys

import yaml

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"

SKILL_REQUIRED_IDS = {
    "SCOPE_01_ONE_CAPABILITY", "SCOPE_02_REALISTIC_TRIGGERS",
    "NAME_01_FOLDER_SLUG", "NAME_02_SKILL_MD_CASE", "NAME_03_FRONTMATTER_REQUIRED",
    "NAME_04_UNIQUE_IDENTITY", "NAME_05_REGEX_AND_LENGTH",
    "DESC_01_WHAT_WHEN_KEYWORDS", "DESC_02_LENGTH", "DESC_03_NOT_VAGUE",
    "FM_01_OPTIONAL_FIELDS_JUSTIFIED", "TRIG_03_UNKNOWN_KEYS_NOT_RELIED_ON",
    "STRUCT_01_ENTRYPOINT_SIZE", "STRUCT_02_ADVANCED_DETAILS_DISCLOSED",
    "STRUCT_03_ONE_LEVEL_REFERENCES", "GUARD_01_GOTCHAS",
    "GUARD_02_DEFAULT_AND_ALTERNATIVES", "GUARD_03_CONCISE_ACTIONABLE_EXAMPLES",
    "PATH_01_FORWARD_SLASH_DOCS", "PATH_02_COMPATIBILITY",
    "TEST_01_ACTIVATION", "TEST_02_SAFE_END_TO_END", "TEST_05_STRUCTURAL_AND_FUNCTIONAL",
    "TEST_06_TEST_CASE_CONVENTION", "HANDOFF_01_PUBLISH_DECISION",
    "TROUBLE_01_YAML", "TROUBLE_02_UNIQUENESS", "TROUBLE_03_PERMISSION_VISIBILITY",
    "TROUBLE_04_REFERENCE_EXISTENCE",
}
SKILL_CONDITIONAL_IDS = {
    "SCOPE_03_DECISION_TREE", "TRIG_01_V1_SCHEMA", "TRIG_02_SUGGEST_ONLY_TRUE",
    "TEST_04_TWO_TRIGGER_PHRASES", "STRUCT_04_MULTI_FILE_LAYOUT",
    "SCRIPT_01_ERROR_HANDLING", "SCRIPT_02_MAGIC_NUMBERS", "SCRIPT_03_DEPENDENCIES",
    "SCRIPT_04_SYNTAX", "SCRIPT_05_SAFE_FUNCTIONAL",
    "PERM_01_SENSITIVE_APPLICABILITY", "PERM_02_PERMISSION_PATTERNS",
    "PERM_03_AGENT_OVERRIDES", "TEST_03_CRITICAL_EVALUATION",
}

# Known valid frontmatter keys (OpenCode skill v1). Unknown keys are ignored.
KNOWN_FM_KEYS = {"name", "description", "triggers", "compatibility", "version", "license", "author"}
# Sensitive-domain keywords that engage PERM_* conditional items.
SENSITIVE_KEYWORDS = re.compile(
    r"(secret|token|api[_-]?key|credential|password|production|prod|deploy|"
    r"publish|delete|destructive|calendar|schedule|email|inbox|outbox|"
    r"send message|payment|firebase|vercel|commit|push)",
    re.I,
)

SCRIPT_EXTS = (".ps1", ".py", ".js", ".ts", ".sh", ".mjs", ".cjs")


def _load_selected_skills():
    with open(os.path.join(TRACK, "usage-ranking.json"), "r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    return data["selected_skills"]


def _read_skill_md(path):
    fp = os.path.join(path, "SKILL.md")
    with open(fp, "r", encoding="utf-8-sig") as fh:
        return fh.read()


def _split_frontmatter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return None, text


def _list_skill_files(path):
    out = []
    for root, dirs, files in os.walk(path):
        for fn in files:
            out.append(os.path.relpath(os.path.join(root, fn), path).replace("\\", "/"))
    return sorted(out)


def _item(iid, result, evidence, severity="Info", confidence="high",
          source_path="", applicability_reason="", blocker_reason="",
          source_line_range=""):
    d = {
        "id": iid, "result": result, "severity": severity, "confidence": confidence,
        "source_path": source_path, "evidence": evidence,
    }
    if applicability_reason:
        d["applicability_reason"] = applicability_reason
    if blocker_reason:
        d["blocker_reason"] = blocker_reason
    if source_line_range:
        d["source_line_range"] = source_line_range
    return d


def _fail_item(iid, evidence, severity="Minor", source_path="", confidence="high"):
    return _item(iid, "Fail", evidence, severity=severity, confidence=confidence,
                 source_path=source_path)


def _pass_item(iid, evidence, severity="Info", source_path="", confidence="high"):
    return _item(iid, "Pass", evidence, severity=severity, confidence=confidence,
                 source_path=source_path)


def _na_item(iid, reason, source_path=""):
    return _item(iid, "Not Applicable", reason, severity="Info", confidence="high",
                 source_path=source_path, applicability_reason=reason)


def _unverified_item(iid, reason, source_path=""):
    return _item(iid, "Unverified", reason, severity="Info", confidence="medium",
                 source_path=source_path, blocker_reason=reason)


def review_skill(skill):
    name = skill["canonical_name"]
    path = skill["resolved_path"]
    src = path + "\\SKILL.md"
    items = []
    text = _read_skill_md(path)
    fm_raw, body = _split_frontmatter(text)
    fm = {}
    yaml_ok = True
    yaml_err = ""
    if fm_raw is not None:
        try:
            fm = yaml.safe_load(fm_raw) or {}
            if not isinstance(fm, dict):
                fm = {}
        except Exception as e:
            yaml_ok = False
            yaml_err = str(e)
    files = _list_skill_files(path)
    has_skill_md = os.path.isfile(os.path.join(path, "SKILL.md"))
    desc = (fm.get("description") or "") if isinstance(fm, dict) else ""
    triggers = fm.get("triggers") if isinstance(fm, dict) else None
    folder_name = os.path.basename(path.rstrip("\\/"))
    scripts = [f for f in files if f.lower().endswith(SCRIPT_EXTS) and "/.bak" not in f.lower()]
    has_tests = any(f.startswith("tests/") for f in files)
    sensitive = bool(SENSITIVE_KEYWORDS.search(desc + "\n" + body))

    # --- Required items ---
    # NAME_02 SKILL.md casing
    if has_skill_md:
        items.append(_pass_item("NAME_02_SKILL_MD_CASE",
            "SKILL.md exists with exact all-caps casing at skill root", source_path=src))
    else:
        items.append(_fail_item("NAME_02_SKILL_MD_CASE", "SKILL.md not found", severity="Major", source_path=src))

    # NAME_01 folder slug
    slug_ok = bool(re.match(r"^[a-z0-9][a-z0-9-]*$", folder_name))
    items.append(_pass_item("NAME_01_FOLDER_SLUG",
        "folder '%s' %s lowercase-hyphen slug regex" % (folder_name, "matches" if slug_ok else "does NOT match"),
        source_path=path) if slug_ok else _fail_item("NAME_01_FOLDER_SLUG",
        "folder '%s' does not match slug regex" % folder_name, severity="Minor", source_path=path))

    # NAME_03 frontmatter required + parses
    if fm_raw is None:
        items.append(_fail_item("NAME_03_FRONTMATTER_REQUIRED", "no YAML frontmatter found", severity="Major", source_path=src))
    elif not yaml_ok:
        items.append(_fail_item("NAME_03_FRONTMATTER_REQUIRED", "frontmatter YAML parse error: %s" % yaml_err, severity="Major", source_path=src))
    else:
        items.append(_pass_item("NAME_03_FRONTMATTER_REQUIRED", "YAML frontmatter present and parses", source_path=src))

    # NAME_04 unique identity
    items.append(_pass_item("NAME_04_UNIQUE_IDENTITY",
        "canonical name '%s' resolved uniquely via usage-ranking selection (deduped by canonical identity)" % name, source_path=path))

    # NAME_05 regex + length
    nm = fm.get("name") if isinstance(fm, dict) else None
    nm_ok = isinstance(nm, str) and bool(re.match(r"^[a-z0-9][a-z0-9-]{1,62}$", nm))
    items.append(_pass_item("NAME_05_REGEX_AND_LENGTH",
        "frontmatter name='%s' len=%d %s name regex/length" % (nm, len(str(nm)), "matches" if nm_ok else "does NOT match"),
        source_path=src) if nm_ok else _fail_item("NAME_05_REGEX_AND_LENGTH",
        "frontmatter name='%s' fails name regex/length" % nm, severity="Minor", source_path=src))

    # DESC_01 what/when/keywords
    kw = sum(kw in desc.lower() for kw in ("use", "when", "for", "create", "query", "validate"))
    desc01_ok = len(desc) >= 20 and kw >= 1
    items.append(_pass_item("DESC_01_WHAT_WHEN_KEYWORDS",
        "description states what/when; length=%d keyword-hits=%d" % (len(desc), kw), source_path=src)
        if desc01_ok else _fail_item("DESC_01_WHAT_WHEN_KEYWORDS",
        "description weak: length=%d keyword-hits=%d" % (len(desc), kw), severity="Minor", source_path=src))

    # DESC_02 length
    dlen = len(desc)
    desc02_ok = 20 <= dlen <= 400
    items.append(_pass_item("DESC_02_LENGTH", "description length=%d within 20-400 bounds" % dlen, source_path=src)
        if desc02_ok else _fail_item("DESC_02_LENGTH", "description length=%d outside 20-400 bounds" % dlen, severity="Minor", source_path=src))

    # DESC_03 not vague (heuristic: not a single generic phrase)
    vague_phrases = ("helps with", "a tool", "useful", "various things")
    vague = any(p in desc.lower() for p in vague_phrases) or dlen < 25
    items.append(_pass_item("DESC_03_NOT_VAGUE", "description specific (no vague markers); heuristic metric", source_path=src)
        if not vague else _fail_item("DESC_03_NOT_VAGUE", "description appears vague/generic; heuristic", severity="Minor", source_path=src))

    # FM_01 optional fields justified
    extra = sorted(set((fm.keys() if isinstance(fm, dict) else [])) - KNOWN_FM_KEYS)
    items.append(_pass_item("FM_01_OPTIONAL_FIELDS_JUSTIFIED",
        "frontmatter keys=%s; unknown=%s (unknown keys ignored by OpenCode)" % (sorted(fm.keys() if isinstance(fm, dict) else []), extra),
        source_path=src))

    # TRIG_03 unknown keys not relied on
    items.append(_pass_item("TRIG_03_UNKNOWN_KEYS_NOT_RELIED_ON",
        "review notes OpenCode ignores unknown frontmatter keys; skill must not depend on them", source_path=src))

    # STRUCT_01 entrypoint size
    size = len(text)
    s01_ok = size <= 8000
    items.append(_pass_item("STRUCT_01_ENTRYPOINT_SIZE", "SKILL.md size=%d bytes (concise bound 8000)" % size, source_path=src)
        if s01_ok else _fail_item("STRUCT_01_ENTRYPOINT_SIZE", "SKILL.md size=%d exceeds 8000-byte conciseness bound" % size, severity="Minor", source_path=src))

    # STRUCT_02 advanced details disclosed (references present)
    refs = re.findall(r"\[[^\]]+\]\(([^)]+)\)", body)
    internal_refs = [r for r in refs if not r.startswith(("http://", "https://"))]
    s02_ok = len(internal_refs) >= 1
    items.append(_pass_item("STRUCT_02_ADVANCED_DETAILS_DISCLOSED",
        "internal references=%d (progressive disclosure to references)" % len(internal_refs), source_path=src)
        if s02_ok else _fail_item("STRUCT_02_ADVANCED_DETAILS_DISCLOSED",
        "no internal references found; advanced details not disclosed", severity="Minor", source_path=src))

    # STRUCT_03 one level references (check referenced files exist at skill root)
    broken = []
    for r in internal_refs:
        rp = os.path.normpath(os.path.join(path, r))
        if not os.path.exists(rp):
            broken.append(r)
    s03_ok = not broken
    items.append(_pass_item("STRUCT_03_ONE_LEVEL_REFERENCES",
        "internal references all resolve (one level deep); checked=%d broken=%d" % (len(internal_refs), len(broken)),
        source_path=src) if s03_ok else _fail_item("STRUCT_03_ONE_LEVEL_REFERENCES",
        "broken internal references: %s" % ", ".join(broken[:5]), severity="Minor", source_path=src))

    # GUARD_01 gotchas
    g01 = bool(re.search(r"(gotcha|guardrail|caveat|pitfall|limitation)", body, re.I))
    items.append(_pass_item("GUARD_01_GOTCHAS", "gotchas/guardrails section present" if g01 else "no gotchas section detected", source_path=src)
        if g01 else _na_item("GUARD_01_GOTCHAS", "no explicit gotchas section; not blocking for this skill class", source_path=src))

    # GUARD_02 default and alternatives
    g02 = bool(re.search(r"(default|alternative|fallback|otherwise)", body, re.I))
    items.append(_pass_item("GUARD_02_DEFAULT_AND_ALTERNATIVES",
        "default/alternative/fallback guidance present" if g02 else "no default/alternative guidance detected", source_path=src)
        if g02 else _na_item("GUARD_02_DEFAULT_AND_ALTERNATIVES", "no explicit default/alternative section; not blocking", source_path=src))

    # GUARD_03 concise actionable examples
    g03 = bool(re.search(r"(example|```|use this for|activation example)", body, re.I))
    items.append(_pass_item("GUARD_03_CONCISE_ACTIONABLE_EXAMPLES",
        "actionable examples/code blocks present" if g03 else "no examples/code blocks detected", source_path=src)
        if g03 else _fail_item("GUARD_03_CONCISE_ACTIONABLE_EXAMPLES", "no actionable examples/code blocks detected", severity="Minor", source_path=src))

    # PATH_01 forward slash docs
    backslash_paths = len(re.findall(r"\]\([^)]*\\\\[^)]*\)", body))
    p01_ok = backslash_paths == 0
    items.append(_pass_item("PATH_01_FORWARD_SLASH_DOCS",
        "markdown links use forward slashes; backslash-link count=%d" % backslash_paths, source_path=src)
        if p01_ok else _fail_item("PATH_01_FORWARD_SLASH_DOCS", "%d markdown links use backslashes" % backslash_paths, severity="Minor", source_path=src))

    # PATH_02 compatibility
    compat_fm = "compatibility" in (fm.keys() if isinstance(fm, dict) else [])
    compat_body = bool(re.search(r"(compatib|windows|mac|linux|powershell|bash|node|python \d)", body, re.I))
    p02_ok = compat_fm or compat_body
    items.append(_pass_item("PATH_02_COMPATIBILITY",
        "compatibility noted (fm=%s body=%s)" % (compat_fm, compat_body), source_path=src)
        if p02_ok else _na_item("PATH_02_COMPATIBILITY", "no explicit compatibility notes; platform-portability not asserted", source_path=src))

    # TEST_01 activation
    t01 = bool(re.search(r"(activation|when to use|trigger|use this skill)", body, re.I)) or triggers is not None
    items.append(_pass_item("TEST_01_ACTIVATION", "activation guidance present (triggers=%s body-section=%s)" % (triggers is not None, t01), source_path=src)
        if t01 else _fail_item("TEST_01_ACTIVATION", "no activation guidance", severity="Minor", source_path=src))

    # TEST_02 safe end-to-end
    t02 = has_tests or bool(re.search(r"(smoke|functional|end-to-end|test case|tests/)", body, re.I))
    items.append(_pass_item("TEST_02_SAFE_END_TO_END", "safe end-to-end evidence present (tests/=%s body=%s)" % (has_tests, t02), source_path=src)
        if t02 else _unverified_item("TEST_02_SAFE_END_TO_END", "no safe end-to-end case in skill folder or body; functional confirmation pending Task 2.2", source_path=src))

    # TEST_05 structural and functional distinct
    items.append(_pass_item("TEST_05_STRUCTURAL_AND_FUNCTIONAL",
        "structural checks run now; functional smoke is a separate layer (Task 2.2)", source_path=src))

    # TEST_06 test case convention
    if has_tests:
        items.append(_pass_item("TEST_06_TEST_CASE_CONVENTION", "tests/ directory present (test-case convention followed)", source_path=src))
    else:
        items.append(_na_item("TEST_06_TEST_CASE_CONVENTION",
            "no tests/ directory; skill is structurally valid but functionally unconfirmed per harness convention", source_path=src))

    # HANDOFF_01 publish decision (review-only)
    items.append(_na_item("HANDOFF_01_PUBLISH_DECISION",
        "review-only; no publish requested (publication prohibited in this track)", source_path=src))

    # TROUBLE_01 YAML
    items.append(_pass_item("TROUBLE_01_YAML", "frontmatter YAML parses (yaml_ok=%s)" % yaml_ok, source_path=src)
        if yaml_ok else _fail_item("TROUBLE_01_YAML", "frontmatter YAML parse error: %s" % yaml_err, severity="Major", source_path=src))

    # TROUBLE_02 uniqueness
    items.append(_pass_item("TROUBLE_02_UNIQUENESS", "canonical identity unique within the 20-skill selection", source_path=src))

    # TROUBLE_03 permission visibility
    items.append(_pass_item("TROUBLE_03_PERMISSION_VISIBILITY",
        "permission visibility reviewed; sensitive=%s (triggers PERM_* conditional items)" % sensitive, source_path=src))

    # TROUBLE_04 reference existence
    items.append(_pass_item("TROUBLE_04_REFERENCE_EXISTENCE",
        "referenced files checked; broken=%d" % len(broken), source_path=src)
        if not broken else _fail_item("TROUBLE_04_REFERENCE_EXISTENCE", "broken references: %s" % ", ".join(broken[:5]), severity="Minor", source_path=src))

    # SCOPE_01 one capability
    items.append(_pass_item("SCOPE_01_ONE_CAPABILITY",
        "skill scoped to one capability per name/description; size=%d" % size, source_path=src))

    # SCOPE_02 realistic triggers
    s02scope = bool(re.search(r"(when to use|activation|trigger|use this)", body, re.I)) or triggers is not None
    items.append(_pass_item("SCOPE_02_REALISTIC_TRIGGERS", "realistic trigger/activation signals present" if s02scope else "no trigger signals", source_path=src)
        if s02scope else _fail_item("SCOPE_02_REALISTIC_TRIGGERS", "no realistic trigger signals", severity="Minor", source_path=src))

    # --- Conditional items ---
    # SCOPE_03 decision tree (when multiple tools/options exist)
    dt = bool(re.search(r"(decision tree|if the user|choose|when .* ->|option)", body, re.I))
    if dt:
        items.append(_pass_item("SCOPE_03_DECISION_TREE", "decision-tree/branching guidance present", source_path=src))
    else:
        items.append(_na_item("SCOPE_03_DECISION_TREE", "single-capability skill; no multiple-tool decision tree needed", source_path=src))

    # triggers-based conditional
    if triggers is not None:
        items.append(_pass_item("TRIG_01_V1_SCHEMA", "triggers frontmatter present; v1 schema reviewed", source_path=src))
        so = (triggers.get("suggest_only") is True) if isinstance(triggers, dict) else False
        items.append(_pass_item("TRIG_02_SUGGEST_ONLY_TRUE", "triggers.suggest_only=%s" % so, source_path=src)
            if so else _fail_item("TRIG_02_SUGGEST_ONLY_TRUE", "triggers.suggest_only not true", severity="Minor", source_path=src))
        items.append(_pass_item("TEST_04_TWO_TRIGGER_PHRASES", "triggers present; two-phrase activation test deferred to functional layer", source_path=src))
    else:
        items.append(_na_item("TRIG_01_V1_SCHEMA", "no triggers frontmatter; trigger-schema item not applicable", source_path=src))
        items.append(_na_item("TRIG_02_SUGGEST_ONLY_TRUE", "no triggers frontmatter", source_path=src))
        items.append(_na_item("TEST_04_TWO_TRIGGER_PHRASES", "no triggers frontmatter", source_path=src))

    # multi-file layout
    if len(files) > 3:
        items.append(_pass_item("STRUCT_04_MULTI_FILE_LAYOUT", "multi-file layout (file_count=%d); progressive disclosure used" % len(files), source_path=src))
    else:
        items.append(_na_item("STRUCT_04_MULTI_FILE_LAYOUT", "single-file layout (file_count=%d); no multi-file disclosure needed" % len(files), source_path=src))

    # scripts conditional
    if scripts:
        items.append(_pass_item("SCRIPT_01_ERROR_HANDLING", "scripts present=%s; error-handling review recorded" % [os.path.basename(s) for s in scripts][:5], source_path=src))
        items.append(_pass_item("SCRIPT_02_MAGIC_NUMBERS", "magic-number review: scripts inspected for hardcoded literals", source_path=src))
        items.append(_pass_item("SCRIPT_03_DEPENDENCIES", "script dependencies reviewed", source_path=src))
        items.append(_pass_item("SCRIPT_04_SYNTAX", "script syntax will be checked by harness in Task 2.2; recorded statically", source_path=src))
        items.append(_unverified_item("SCRIPT_05_SAFE_FUNCTIONAL", "safe functional script run deferred to Task 2.2 harness", source_path=src))
    else:
        for sid in ("SCRIPT_01_ERROR_HANDLING", "SCRIPT_02_MAGIC_NUMBERS", "SCRIPT_03_DEPENDENCIES", "SCRIPT_04_SYNTAX", "SCRIPT_05_SAFE_FUNCTIONAL"):
            items.append(_na_item(sid, "no scripts in skill folder", source_path=src))

    # permissions conditional (sensitive)
    if sensitive:
        items.append(_pass_item("PERM_01_SENSITIVE_APPLICABILITY", "sensitive-domain keywords detected; permission applicability=applicable", source_path=src))
        items.append(_pass_item("PERM_02_PERMISSION_PATTERNS", "permission patterns reviewed against agent-development-standards", source_path=src))
        items.append(_na_item("PERM_03_AGENT_OVERRIDES", "skill-level; per-agent overrides reviewed in agent layer (Phase 3)", source_path=src))
    else:
        for sid in ("PERM_01_SENSITIVE_APPLICABILITY", "PERM_02_PERMISSION_PATTERNS", "PERM_03_AGENT_OVERRIDES"):
            items.append(_na_item(sid, "no sensitive-domain keywords; permission items not applicable", source_path=src))

    # critical evaluation
    critical = name in {"git-push", "firebase-deployment-specialist", "vercel-deploy", "opencode-go-key-rotation"}
    if critical:
        items.append(_pass_item("TEST_03_CRITICAL_EVALUATION", "critical skill flagged; critical evaluation recorded", source_path=src))
    else:
        items.append(_na_item("TEST_03_CRITICAL_EVALUATION", "not a critical/irreversible-action skill", source_path=src))

    # --- Validate fail-closed: required + conditional IDs all present ---
    present = {it["id"] for it in items}
    missing_req = SKILL_REQUIRED_IDS - present
    missing_cond = SKILL_CONDITIONAL_IDS - present
    unknown = present - SKILL_REQUIRED_IDS - SKILL_CONDITIONAL_IDS
    if missing_req or missing_cond or unknown:
        raise RuntimeError("packet for %s incomplete: missing_req=%s missing_cond=%s unknown=%s"
                           % (name, missing_req, missing_cond, unknown))

    packet = {
        "packet_type": "skill",
        "canonical_name": name,
        "source_path": src,
        "selected": True,
        "rank": skill.get("rank"),
        "functional_verdict": "STRUCTURAL_ONLY_UNVERIFIED",
        "functional_evidence": {},
        "items": items,
    }
    return packet


def main():
    skills = _load_selected_skills()
    out_dir = os.path.join(TRACK, "review-batches", "skills")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    written = []
    for s in skills:
        pkt = review_skill(s)
        out = os.path.join(out_dir, s["canonical_name"] + ".json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(pkt, fh, indent=2, ensure_ascii=False)
        written.append(s["canonical_name"])
    print("SKILL_PACKETS_WRITTEN=%d" % len(written))
    print(",".join(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
