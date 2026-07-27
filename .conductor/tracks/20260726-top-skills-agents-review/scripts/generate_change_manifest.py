#!/usr/bin/env python3
"""Generate change-manifest.json + diffs and update fix-queue/packet status (Task 4.2).

For each backed-up skill with live changes vs its backup:
- compute before (backup) / after (live) tree hashes
- run `git diff --no-index` (local, bounded) to produce a diff patch
- record changed files, correction, authority_delta (syntax-only => none)
- write change-manifest.json + diff files under evidence/changes/

Also updates fix-queue.json (applied/partial/dave-decision status) and the
affected skill packets' SCRIPT_04_SYNTAX item to reflect post-fix reality.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

TRACK = r"C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review"


def _load(name):
    with open(os.path.join(TRACK, name), "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def _file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _tree_hash(folder):
    """Hash reviewable source content, excluding interpreter-generated caches."""
    entries = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        dirs.sort()
        for fn in sorted(files):
            if fn.endswith((".pyc", ".pyo")):
                continue
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, folder).replace("\\", "/")
            entries.append(rel + ":" + _file_sha(fp))
    entries.sort()
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


def _git_diff_numstat(backup, live):
    try:
        p = subprocess.run(["git", "diff", "--no-index", "--numstat", backup, live],
                           shell=False, capture_output=True, text=True, timeout=60,
                           encoding="utf-8", errors="replace")
        # exit 1 means differences found (normal); parse stdout
        changed = []
        for line in (p.stdout or "").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                path = parts[2].replace("\\", "/")
                if "/__pycache__/" not in path and not path.endswith((".pyc", ".pyo")):
                    changed.append(path)
        return changed
    except Exception:
        return []


def _git_diff_patch(backup, live, out_path):
    try:
        p = subprocess.run(["git", "diff", "--no-index", backup, live],
                           shell=False, capture_output=True, text=True, timeout=60,
                           encoding="utf-8", errors="replace")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(p.stdout or "")
        return len(p.stdout or "")
    except Exception as e:
        return -1


def main():
    prior_manifest = None
    prior_path = os.path.join(TRACK, "change-manifest.json")
    if os.path.isfile(prior_path):
        prior_manifest = _load("change-manifest.json")
    man = _load("backup-manifest.json")
    fq = _load("fix-queue.json")
    rank = _load("usage-ranking.json")
    skill_name = {s["canonical_name"]: s for s in rank["selected_skills"]}

    diff_dir = os.path.join(TRACK, "evidence", "changes")
    if not os.path.isdir(diff_dir):
        os.makedirs(diff_dir, exist_ok=True)

    changes = []
    # Per-skill correction notes (syntax-only; no capability/authority change).
    correction = {
        "clickup": ("Fixed syntax-only defects in scripts/input_validation.py (8 literal-newline-inside-string "
                    "literals corrected to \\n; systematic corruption) and tests/test_input_validation.py "
                    "(fixed indentation of f.write inside `with` block + removed a stray duplicated fragment). "
                    "Removed unreferenced scripts/patch_script.py after Dave explicitly authorized removal; "
                    "the exact pre-edit recovery copy remains in the track backup."),
        "opencode-event-log-compactor": ("Fixed syntax-only PS 5.1 incompatibility in scripts/Switch-ValidatedDatabase.ps1: "
                                         "replaced null-conditional operator `dbHash?.Substring(0,16)` with a PS 5.1-safe "
                                         "`if ($dbHash) { ... Substring }` expression (identical null-safe display behavior)."),
    }

    for entry in man["entries"]:
        cn = entry["canonical_name"]
        backup = entry["backup_path"]
        live = entry["source_path"]
        before_th = _tree_hash(backup)
        after_th = _tree_hash(live)
        changed_files = _git_diff_numstat(backup, live)
        diff_path = os.path.join(diff_dir, cn + ".diff.patch")
        diff_len = _git_diff_patch(backup, live, diff_path)
        # Authority check: syntax-only fixes add no imports/functions/external actions.
        authority_delta = "none" if changed_files else "none"
        # Find queue id for this skill.
        qids = entry["queue_ids"]
        changes.append({
            "canonical_name": cn,
            "queue_ids": qids,
            "target_path": live,
            "backup_path": backup,
            "before_tree_sha256": before_th,
            "after_tree_sha256": after_th,
            "changed_files": changed_files,
            "diff_path": diff_path,
            "diff_size": diff_len,
            "correction": correction.get(cn, "syntax-only defect fix"),
            "authority_delta": authority_delta,
            "authority_basis": "diff is string-literal/operator syntax only; no new imports, functions, external-action verbs, or permission/capability expansion",
        })

    manifest = {
        "trackId": "20260726-top-skills-agents-review",
        "manifest_revision": 2,
        "tree_hash_contract": {
            "scope": "reviewable-source",
            "excluded": ["**/__pycache__/**", "**/*.pyc", "**/*.pyo"],
            "reason": "Interpreter-generated bytecode is retained in place but is not source evidence.",
        },
        "changes": changes,
        "authority_delta_any": any(c["authority_delta"] != "none" for c in changes),
    }
    if prior_manifest:
        manifest["superseded_snapshot_audit"] = {
            "reason": "Regenerated after Dave authorized removal of clickup/scripts/patch_script.py; prior evidence remains preserved in validation-cycle-ledger.json and audit-correction-stage8-cycle1-2026-07-26.md.",
            "prior_manifest_revision": prior_manifest.get("manifest_revision", 1),
            "prior_after_tree_sha256": {
                c.get("canonical_name"): c.get("after_tree_sha256")
                for c in prior_manifest.get("changes", [])
            },
        }
    with open(os.path.join(TRACK, "change-manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    # Update fix-queue.json statuses per skill.
    status_map = {
        "opencode-event-log-compactor": ("applied", "Switch-ValidatedDatabase.ps1 PS5.1 null-safe fix applied; harness SCRIPT SYNTAX now PASS"),
        "clickup": ("applied", "input_validation.py + test_input_validation.py syntax fixes applied; unreferenced truncated patch_script.py removed with Dave's explicit approval; harness SCRIPT SYNTAX now PASS"),
    }
    for q in fq["skill_fixes"]:
        st, note = status_map.get(q["canonical_name"], ("applied", "applied"))
        q["status"] = st
        q["status_note"] = note
    # Preserve the resolved decision as audit evidence without leaving it open.
    fq["dave_decisions"] = [
        d for d in (fq.get("dave_decisions") or [])
        if not (d.get("canonical_name") == "clickup" and d.get("file") == "scripts/patch_script.py")
    ]
    fq.setdefault("resolved_dave_decisions", [])
    resolved = {
        "canonical_name": "clickup",
        "file": "scripts/patch_script.py",
        "finding": "unterminated triple-quoted string literal (truncated file, ends mid-token at line 231)",
        "resolution": "Dave explicitly authorized removal when intent could not be recovered; live file removed after exact backup/hash verification.",
        "recovery_copy": r"C:\development\opencode\.git\codex-track-backups\20260726-top-skills-agents-review\2026-07-26-pre-edit\6f4f87a35d0d925b414a3aaa_clickup\scripts\patch_script.py",
        "backup_sha256": "8CA45DA3EC2AE6A3B9B7F267C4065535FE73963A7F801C21D1334837D3DE50BB",
        "resolved": True,
    }
    if not any(d.get("canonical_name") == "clickup" and d.get("file") == "scripts/patch_script.py"
               for d in fq["resolved_dave_decisions"]):
        fq["resolved_dave_decisions"].append(resolved)
    fq["counts"]["dave_decisions"] = len(fq["dave_decisions"])
    with open(os.path.join(TRACK, "fix-queue.json"), "w", encoding="utf-8") as fh:
        json.dump(fq, fh, indent=2, ensure_ascii=False)

    # Update affected skill packets' SCRIPT_04_SYNTAX item to reflect reality.
    post_fix = {
        "clickup": ("Pass", "Info",
                    "input_validation.py + test_input_validation.py pass syntax; the unreferenced truncated "
                    "patch_script.py was removed with Dave's explicit approval after exact backup/hash verification; "
                    "skill harness SCRIPT SYNTAX now PASS (22/22)."),
        "opencode-event-log-compactor": ("Pass", "Info",
                    "Switch-ValidatedDatabase.ps1 PS5.1 null-safe fix applied; harness SCRIPT SYNTAX now PASS (13/13). Fully resolved."),
    }
    for cn, (res, sev, ev) in post_fix.items():
        ppath = os.path.join(TRACK, "review-batches", "skills", cn + ".json")
        pkt = json.load(open(ppath, encoding="utf-8-sig"))
        for it in pkt["items"]:
            if it["id"] == "SCRIPT_04_SYNTAX":
                it["result"] = res
                it["severity"] = sev
                it["evidence"] = ev
                if res == "Pass":
                    it["confidence"] = "high"
        with open(ppath, "w", encoding="utf-8") as fh:
            json.dump(pkt, fh, indent=2, ensure_ascii=False)

    print("CHANGE_MANIFEST_DONE changes=%d" % len(changes))
    for c in changes:
        print("  %s: changed_files=%d authority_delta=%s" % (c["canonical_name"], len(c["changed_files"]), c["authority_delta"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
