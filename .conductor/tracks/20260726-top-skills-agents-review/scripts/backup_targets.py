#!/usr/bin/env python3
"""Back up every distinct queued skill target (Task 4.1).

Reads fix-queue.json skill_fixes, resolves each to its canonical skill FOLDER
(from usage-ranking.json), and copies the folder tree to the safe backup root
beneath the resolved .git directory. Destination names are collision-proof
(lowercase SHA-256 of the canonical source path + sanitized leaf). Writes
backup-manifest.json with source/backup tree hashes, target type, queue IDs,
preexistence marker, and exact restore command. Flips backup-dir.json
copy_targets_started to true.

Tree hash = SHA-256 of the concatenation of (relpath + ':' + file_sha256) over
the sorted file list. This is a stable, content-addressed fingerprint.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
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
    entries = []
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for fn in sorted(files):
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, folder).replace("\\", "/")
            entries.append(rel + ":" + _file_sha(fp))
    entries.sort()
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest(), entries


def _dest_name(src_path, leaf):
    digest = hashlib.sha256(src_path.encode("utf-8")).hexdigest()
    safe_leaf = "".join(c if c.isalnum() or c in "-_" else "_" for c in leaf)
    return digest[:24] + "_" + safe_leaf


def main():
    fq = _load("fix-queue.json")
    bd = _load("backup-dir.json")
    rank = _load("usage-ranking.json")
    skill_folder = {s["canonical_name"]: s["resolved_path"] for s in rank["selected_skills"]}
    backup_root = bd["backup_root"]

    skill_fixes = fq.get("skill_fixes") or []
    # Distinct target folders keyed by canonical_name.
    targets = {}
    for q in skill_fixes:
        cn = q["canonical_name"]
        folder = skill_folder.get(cn)
        if not folder or not os.path.isdir(folder):
            print("ERROR: target folder missing for %s: %s" % (cn, folder), file=sys.stderr)
            return 1
        if cn not in targets:
            targets[cn] = {"folder": folder, "queue_ids": []}
        targets[cn]["queue_ids"].append(q["id"])

    if not targets:
        manifest = {"status": "NOT_APPLICABLE", "targets": 0, "entries": []}
        with open(os.path.join(TRACK, "backup-manifest.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
        print("BACKUPS_NOT_APPLICABLE targets=0")
        return 0

    if not os.path.isdir(backup_root):
        os.makedirs(backup_root, exist_ok=True)

    manifest_entries = []
    for cn, info in targets.items():
        src = info["folder"]
        leaf = os.path.basename(src.rstrip("\\/"))
        dest_name = _dest_name(src, leaf)
        dest = os.path.join(backup_root, dest_name)
        preexist = os.path.exists(dest)
        if preexist:
            # Collision check: refuse non-empty preexisting destinations.
            if os.listdir(dest):
                print("ERROR: backup destination collision (non-empty): %s" % dest, file=sys.stderr)
                return 1
        if os.path.exists(dest):
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest)
        src_th, src_entries = _tree_hash(src)
        bak_th, bak_entries = _tree_hash(dest)
        if src_th != bak_th:
            print("ERROR: backup tree hash mismatch for %s" % cn, file=sys.stderr)
            return 1
        restore_cmd = ('powershell -NoProfile -Command "Remove-Item -LiteralPath \\"%s\\" -Recurse -Force; '
                       'Copy-Item -LiteralPath \\"%s\\" -Destination \\"%s\\" -Recurse -Force"' % (src, dest, os.path.dirname(src)))
        manifest_entries.append({
            "canonical_name": cn,
            "source_path": src,
            "backup_path": dest,
            "destination_name": dest_name,
            "target_type": "directory",
            "queue_ids": info["queue_ids"],
            "preexistence_marker": preexist,
            "source_tree_sha256": src_th,
            "backup_tree_sha256": bak_th,
            "file_count": len(src_entries),
            "restore_command": restore_cmd,
            "verified": src_th == bak_th,
        })

    manifest = {
        "trackId": "20260726-top-skills-agents-review",
        "status": "PASS",
        "targets": len(manifest_entries),
        "backup_root": backup_root,
        "entries": manifest_entries,
    }
    with open(os.path.join(TRACK, "backup-manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    # Flip copy_targets_started.
    bd["copy_targets_started"] = True
    bd["targets_backed_up"] = len(manifest_entries)
    bd["backup_manifest_path"] = os.path.join(TRACK, "backup-manifest.json")
    with open(os.path.join(TRACK, "backup-dir.json"), "w", encoding="utf-8") as fh:
        json.dump(bd, fh, indent=2, ensure_ascii=False)

    print("BACKUPS_DONE targets=%d" % len(manifest_entries))
    for e in manifest_entries:
        print("  %s -> %s (verified=%s)" % (e["canonical_name"], e["destination_name"], e["verified"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
