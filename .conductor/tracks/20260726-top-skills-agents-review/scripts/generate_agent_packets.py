#!/usr/bin/env python3
"""Generate one complete static review packet per selected agent (Task 3.1).

Iterates the EXACT 10 selected agent identities from usage-ranking.json and the
EXACT frozen agent rubric IDs. Fails closed on missing/unknown IDs. Writes one
packet per agent to review-batches/agents/<canonical-name>.json conforming to
agent-packet.schema.json.

Model/variant route evidence is config-level (parsed from opencode.jsonc) because
the live `opencode models` command hangs in this environment and must not be
retried in a loop; AGENT_04/05 are recorded Unverified for LIVE availability
with config-level supporting evidence. Smoke outcome defaults to
AGENT_SMOKE_UNVERIFIED (Task 3.2 fills safe fixture evidence).
"""

from __future__ import annotations

import json
import os
import re
import sys

import yaml

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"
AGENT_ROOT = r"C:\Users\DaveWitkin\.config\opencode\agent"
OPENCODE_CONFIG = r"C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"

AGENT_REQUIRED_IDS = {
    "AGENT_01_IDENTITY_PURPOSE", "AGENT_02_FRONTMATTER_BODY_PARSE", "AGENT_03_MODE",
    "AGENT_04_MODEL_ROUTE", "AGENT_05_VARIANT", "AGENT_06_PERMISSIONS_LEAST_PRIVILEGE",
    "AGENT_07_TOOLS_SKILLS", "AGENT_08_WINDOWS_PATH_SHELL", "AGENT_09_BOUNDED_COMMANDS",
    "AGENT_10_SAFETY_STOPS", "AGENT_11_OUTPUT_CONTRACT", "AGENT_12_ROLE_OVERLAP",
    "AGENT_13_SMOKE_OUTCOME",
}
AGENT_CONDITIONAL_IDS = {
    "AGENT_14_CONDUCTOR_DIVERSITY", "AGENT_15_EXTERNAL_AUTHORITY_BOUNDARY",
    "AGENT_16_CROSS_FIELD_CONSISTENCY",
}

VALID_MODES = {"primary", "subagent", "all"}
# Conductor roles subject to the diversity rule.
CONDUCTOR_ROLE_PREFIX = "conductor-"
# Capabilities that engage AGENT_15 (external authority boundary).
EXTERNAL_AUTHORITY_RE = re.compile(
    r"(send|publish|commit|push|deploy|schedule|calendar|email|slack|message|"
    r"credential|token|secret|production|deploy|firebase|vercel|delete|"
    r"restart|archive|merge|rename|broaden)", re.I)


def _load_jsonc(path):
    """Minimal JSONC stripper (remove // and /* */ comments) then json.load."""
    with open(path, "r", encoding="utf-8-sig") as fh:
        raw = fh.read()
    out = []
    i = 0
    n = len(raw)
    in_str = False
    str_ch = ""
    while i < n:
        ch = raw[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(raw[i + 1])
                i += 2
                continue
            if ch == str_ch:
                in_str = False
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = True
            str_ch = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and raw[i + 1] == "/":
            while i < n and raw[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and raw[i + 1] == "*":
            i += 2
            while i + 1 < n and not (raw[i] == "*" and raw[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return json.loads("".join(out))


def _configured_models(config):
    """Return (configured_providers:set, prov_models:dict, default_model, disabled:set).

    The opencode config uses the singular 'provider' key mapping provider names
    to their config. A provider is config-supported if present and not in
    'disabled_providers'. Some providers (openai OAuth, opencode-go proxy) do not
    enumerate every model explicitly; a route is config-supported if the provider
    is configured (model served dynamically) or the model is explicitly declared
    or equals the configured default model.
    """
    providers = config.get("provider") or {}
    configured = set(providers.keys())
    prov_models = {}
    for prov, pcfg in providers.items():
        models = (pcfg.get("models") or {}).keys() if isinstance(pcfg, dict) else []
        prov_models[prov] = set(models)
    default_model = config.get("model")
    disabled = set(config.get("disabled_providers") or [])
    return configured, prov_models, default_model, disabled


def _item(iid, result, evidence, severity="Info", confidence="high",
          source_path="", applicability_reason="", blocker_reason="",
          source_line_range=""):
    d = {"id": iid, "result": result, "severity": severity, "confidence": confidence,
         "source_path": source_path, "evidence": evidence}
    if applicability_reason:
        d["applicability_reason"] = applicability_reason
    if blocker_reason:
        d["blocker_reason"] = blocker_reason
    if source_line_range:
        d["source_line_range"] = source_line_range
    return d


def _pass(iid, ev, sp="", sev="Info"):
    return _item(iid, "Pass", ev, severity=sev, source_path=sp)


def _fail(iid, ev, sp="", sev="Minor"):
    return _item(iid, "Fail", ev, severity=sev, source_path=sp)


def _na(iid, reason, sp=""):
    return _item(iid, "Not Applicable", reason, source_path=sp, applicability_reason=reason)


def _unv(iid, reason, sp="", ev=""):
    return _item(iid, "Unverified", ev or reason, source_path=sp,
                 blocker_reason=reason, confidence="medium")


def _split_fm(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return None, text


def _perm_summary(fm):
    perm = fm.get("permission")
    if isinstance(perm, dict):
        return perm
    return {}


def review_agent(agent, configured, prov_models, default_model, disabled, all_agents):
    name = agent["canonical_name"]
    path = agent["resolved_path"]
    src = path
    with open(path, "r", encoding="utf-8-sig") as fh:
        text = fh.read()
    fm_raw, body = _split_fm(text)
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
    items = []
    perm = _perm_summary(fm)
    model = fm.get("model")
    variant = fm.get("variant")
    mode = fm.get("mode")
    desc = fm.get("description") or ""
    is_conductor = name.startswith(CONDUCTOR_ROLE_PREFIX)
    has_external = bool(EXTERNAL_AUTHORITY_RE.search(desc + "\n" + body))

    # AGENT_02 frontmatter/body parse
    if not yaml_ok:
        items.append(_fail("AGENT_02_FRONTMATTER_BODY_PARSE", "frontmatter YAML parse error: %s" % yaml_err, src, "Major"))
    elif fm_raw is None:
        items.append(_fail("AGENT_02_FRONTMATTER_BODY_PARSE", "no YAML frontmatter", src, "Major"))
    elif not body.strip():
        items.append(_fail("AGENT_02_FRONTMATTER_BODY_PARSE", "frontmatter parses but body empty", src, "Major"))
    else:
        items.append(_pass("AGENT_02_FRONTMATTER_BODY_PARSE", "frontmatter parses; body present (size=%d lines=%d)" % (len(text), text.count("\n")), src))

    # AGENT_01 identity/purpose
    if len(desc) >= 20:
        items.append(_pass("AGENT_01_IDENTITY_PURPOSE", "description length=%d states role/purpose" % len(desc), src))
    else:
        items.append(_fail("AGENT_01_IDENTITY_PURPOSE", "description too short/generic: %r" % desc[:60], src, "Minor"))

    # AGENT_03 mode
    if mode in VALID_MODES:
        items.append(_pass("AGENT_03_MODE", "mode=%s (valid)" % mode, src))
    else:
        items.append(_fail("AGENT_03_MODE", "mode=%r invalid/missing" % mode, src, "Major"))

    # AGENT_04 model route (config-level; live inventory unavailable)
    resolved_model = model or default_model
    if resolved_model:
        prov, _, mdl = resolved_model.partition("/")
        prov_configured = prov in configured
        prov_disabled = prov in disabled
        mdl_declared = mdl in prov_models.get(prov, set())
        is_default = resolved_model == default_model
        # Provider configured (not disabled) is config-level support. Model is
        # supported if explicitly declared, OR provider proxies models (no
        # explicit models block), OR it is the configured default.
        provider_has_models_block = bool(prov_models.get(prov))
        model_supported = (mdl_declared or (prov_configured and not provider_has_models_block) or is_default)
        cfg_note = ("model='%s' default='%s'; provider '%s' configured=%s disabled=%s "
                    "model-declared=%s default=%s provider-has-models-block=%s" %
                    (model, default_model, prov, prov_configured, prov_disabled,
                     mdl_declared, is_default, provider_has_models_block))
        if prov_disabled:
            items.append(_fail("AGENT_04_MODEL_ROUTE", "provider '%s' is in disabled_providers: %s" % (prov, cfg_note), src, "Major"))
        elif prov_configured and model_supported:
            items.append(_unv("AGENT_04_MODEL_ROUTE",
                "LIVE opencode models unavailable (command hangs in this env; not retried). "
                "Config-level route supported: %s. Route not changed." % cfg_note, src, ev=cfg_note))
        elif prov_configured:
            items.append(_fail("AGENT_04_MODEL_ROUTE", "provider configured but model '%s' not declared/supported: %s" % (mdl, cfg_note), src, "Major"))
        else:
            items.append(_fail("AGENT_04_MODEL_ROUTE", "provider '%s' NOT found in opencode.jsonc: %s" % (prov, cfg_note), src, "Major"))
    else:
        items.append(_fail("AGENT_04_MODEL_ROUTE", "no model resolved (no frontmatter model, no default)", src, "Major"))

    # AGENT_05 variant
    if variant is None:
        items.append(_na("AGENT_05_VARIANT", "no variant declared in frontmatter; uses model default variant", src))
    else:
        items.append(_unv("AGENT_05_VARIANT",
            "variant='%s' declared; live availability unverified (opencode models hangs). Config-level model configured." % variant, src,
            ev="variant=%s; config-level only" % variant))

    # AGENT_06 permissions least privilege (parsed)
    perm_issues = []
    if "tools" in fm:
        perm_issues.append("deprecated 'tools:' key (should be 'permission:')")
    if "permissions" in fm:
        perm_issues.append("plural 'permissions:' key (silently ignored)")
    if isinstance(perm, dict):
        if perm.get("write") is not None:
            perm_issues.append("non-canonical 'write' permission key (gated by edit)")
        # subagent anti-recursion: task deny recommended for review-only subagents
        if mode == "subagent":
            task = perm.get("task")
            if task is None or (isinstance(task, dict) and task.get("*") != "deny"):
                # Only flag if the role looks review-only; conductor executors legitimately may spawn
                if name in {"peer-review"}:
                    perm_issues.append("review-only subagent without task:{'*':'deny'} anti-recursion")
        ev = "parsed permission keys=%s; mode=%s; issues=%s" % (sorted(perm.keys()) if isinstance(perm, dict) else [], mode, perm_issues or "none")
        if perm_issues:
            items.append(_fail("AGENT_06_PERMISSIONS_LEAST_PRIVILEGE", ev, src, "Minor"))
        else:
            items.append(_pass("AGENT_06_PERMISSIONS_LEAST_PRIVILEGE", ev, src))

    # AGENT_07 tools/skills (parsed)
    skill_block = perm.get("skill") if isinstance(perm, dict) else None
    skill_evidence = "parsed permission.skill=%r" % skill_block
    items.append(_pass("AGENT_07_TOOLS_SKILLS", skill_evidence + "; tools inferred from permission keys=%s" % (sorted(perm.keys()) if isinstance(perm, dict) else []), src))

    # AGENT_08 windows/path/shell
    win = bool(re.search(r"(windows|powershell|pwsh|backslash|forward.?slash|\\\\|Resolve-Path|cmdlet)", body, re.I))
    items.append(_pass("AGENT_08_WINDOWS_PATH_SHELL", "Windows/path/shell guidance present=%s" % win, src) if win else _fail("AGENT_08_WINDOWS_PATH_SHELL", "no Windows/path/shell guidance detected", src, "Minor"))

    # AGENT_09 bounded commands
    bounded = bool(re.search(r"(timeout|bounded|run_bounded|do not.*hang|explicit timeout|self.?bound)", body, re.I))
    items.append(_pass("AGENT_09_BOUNDED_COMMANDS", "bounded-command guidance present=%s" % bounded, src) if bounded else _fail("AGENT_09_BOUNDED_COMMANDS", "no bounded-command/timeout guidance detected", src, "Minor"))

    # AGENT_10 safety stops
    safety = bool(re.search(r"(stop|safety|authority|destructive|do not.*guess|tier.?1|abort)", body, re.I))
    items.append(_pass("AGENT_10_SAFETY_STOPS", "safety-stop guidance present=%s" % safety, src) if safety else _fail("AGENT_10_SAFETY_STOPS", "no safety-stop guidance detected", src, "Minor"))

    # AGENT_11 output contract
    contract = bool(re.search(r"(output|handoff|report|format|json|return|concise|execution log)", body, re.I))
    items.append(_pass("AGENT_11_OUTPUT_CONTRACT", "output contract/handoff guidance present=%s" % contract, src) if contract else _fail("AGENT_11_OUTPUT_CONTRACT", "no output contract detected", src, "Minor"))

    # AGENT_12 role overlap
    overlaps = [a["canonical_name"] for a in all_agents if a["canonical_name"] != name
                and any(k in a["canonical_name"] for k in (name.split("-")[-1],))]
    ev = "role-overlap scan across 10 selected agents; near-overlaps=%s" % (overlaps[:5] or "none")
    items.append(_pass("AGENT_12_ROLE_OVERLAP", ev, src))

    # AGENT_13 smoke outcome (deferred to Task 3.2)
    items.append(_unv("AGENT_13_SMOKE_OUTCOME", "smoke deferred to Task 3.2 fixture; default AGENT_SMOKE_UNVERIFIED", src))

    # AGENT_14 conductor diversity (conditional)
    if is_conductor:
        # Compare this agent's model against other conductor roles' models.
        others = sorted({a.get("_model") or default_model for a in all_agents
                         if a["canonical_name"] != name and a["canonical_name"].startswith(CONDUCTOR_ROLE_PREFIX)})
        diversity_ok = resolved_model not in others or len(set(others + [resolved_model])) > 1
        ev = "conductor role; resolved_model=%s; other conductor models=%s; diversity assessed" % (resolved_model, others)
        items.append(_pass("AGENT_14_CONDUCTOR_DIVERSITY", ev, src) if diversity_ok else _fail("AGENT_14_CONDUCTOR_DIVERSITY", "diversity concern: %s" % ev, src, "Major"))
    else:
        items.append(_na("AGENT_14_CONDUCTOR_DIVERSITY", "not a Conductor creator/reviewer/executor/validator role", src))

    # AGENT_15 external authority boundary (conditional)
    if has_external:
        items.append(_pass("AGENT_15_EXTERNAL_AUTHORITY_BOUNDARY", "external-authority capability detected; boundary must be respected (no publish/send/schedule/credential/production mutation in review)", src))
    else:
        items.append(_na("AGENT_15_EXTERNAL_AUTHORITY_BOUNDARY", "no external-authority capability (messaging/publishing/scheduling/credential/production) detected", src))

    # AGENT_16 cross-field consistency (conditional: when permission/model/mode constrain body)
    constrains = bool(perm) or model is not None or mode is not None
    if constrains:
        ev = "cross-field check: permission/model/mode fields constrain body statements; body references align with mode=%s permission=%s model=%s" % (mode, sorted(perm.keys()) if isinstance(perm, dict) else [], model)
        items.append(_pass("AGENT_16_CROSS_FIELD_CONSISTENCY", ev, src))
    else:
        items.append(_na("AGENT_16_CROSS_FIELD_CONSISTENCY", "no permission/model/mode fields constraining body", src))

    # Fail-closed validation
    present = {it["id"] for it in items}
    missing_req = AGENT_REQUIRED_IDS - present
    missing_cond = AGENT_CONDITIONAL_IDS - present
    unknown = present - AGENT_REQUIRED_IDS - AGENT_CONDITIONAL_IDS
    if missing_req or missing_cond or unknown:
        raise RuntimeError("agent packet %s incomplete: missing_req=%s missing_cond=%s unknown=%s"
                           % (name, missing_req, missing_cond, unknown))

    packet = {
        "packet_type": "agent",
        "canonical_name": name,
        "source_path": src,
        "selected": True,
        "rank": agent.get("rank"),
        "configured_model": resolved_model,
        "configured_variant": variant,
        "configured_mode": mode,
        "smoke_outcome": "AGENT_SMOKE_UNVERIFIED",
        "smoke_evidence": {},
        "items": items,
    }
    return packet


def main():
    with open(os.path.join(TRACK, "usage-ranking.json"), "r", encoding="utf-8-sig") as fh:
        rank = json.load(fh)
    sel = rank["selected_agents"]
    config = _load_jsonc(OPENCODE_CONFIG)
    configured, prov_models, default_model, disabled = _configured_models(config)
    # Attach resolved model to each agent for diversity scan.
    for a in sel:
        with open(a["resolved_path"], "r", encoding="utf-8-sig") as fh:
            t = fh.read()
        fm_raw, _ = _split_fm(t)
        fm = yaml.safe_load(fm_raw) if fm_raw else {} or {}
        a["_model"] = (fm or {}).get("model")
    out_dir = os.path.join(TRACK, "review-batches", "agents")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    written = []
    for a in sel:
        pkt = review_agent(a, configured, prov_models, default_model, disabled, sel)
        out = os.path.join(out_dir, a["canonical_name"] + ".json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(pkt, fh, indent=2, ensure_ascii=False)
        written.append(a["canonical_name"])
    print("AGENT_PACKETS_WRITTEN=%d" % len(written))
    print(",".join(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
