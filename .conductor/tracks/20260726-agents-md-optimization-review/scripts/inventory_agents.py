#!/usr/bin/env python3
"""Produce a frozen, read-only AGENTS inventory with explicit scope evidence."""
from __future__ import annotations

import argparse
import datetime as datetime
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from bootstrap_review_toolchain import (
    ToolchainError,
    assert_no_reparse,
    canonical,
    file_record,
    json_line,
    write_json,
)


FROZEN_ROOTS = (
    "02-Kx-to-process",
    "command-center",
    "INACTIVE-content-marketing",
    "marketing",
    "marketing/marketingskills",
    "opencode-core-dcp-fix",
    "opencode-upstream",
    "opencodex",
    "chief-of-staff",
)
DIRECT_EXCLUSIONS = {".git", "node_modules", "vendor", "vendors", "generated"}


def parse_cutoff(value: str) -> datetime.datetime:
    cutoff = datetime.datetime.fromisoformat(value)
    if cutoff.tzinfo is None:
        raise ToolchainError("cutoff must include a UTC offset")
    return cutoff


def is_excluded(candidate: Path, scan_root: Path) -> bool:
    try:
        parts = [part.casefold() for part in candidate.relative_to(scan_root).parts[:-1]]
    except ValueError:
        return True
    for index, part in enumerate(parts):
        if part in DIRECT_EXCLUSIONS:
            return True
        if part.startswith("backup") or part.startswith("archive"):
            return True
        if part == ".conductor" and any(item.startswith("backup") for item in parts[index + 1:]):
            return True
    return False


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )


def git_root_state(root: Path, cutoff: datetime.datetime) -> dict[str, Any] | None:
    try:
        latest = run_git(root, ["log", "-1", "--format=%cI"])
        status = run_git(root, ["status", "--porcelain"])
    except (OSError, subprocess.SubprocessError):
        return None
    if latest.returncode != 0 or not latest.stdout.strip():
        return None
    raw_timestamp = latest.stdout.strip()
    try:
        qualifies = datetime.datetime.fromisoformat(raw_timestamp) >= cutoff
    except ValueError:
        qualifies = False
    return {
        "kind": "git",
        "latest_commit": raw_timestamp,
        "qualifies": qualifies,
        "dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
    }


def git_file_state(root: Path, target: Path) -> dict[str, Any]:
    relative = target.relative_to(root).as_posix()
    try:
        tracked = run_git(root, ["ls-files", "--error-unmatch", "--", relative]).returncode == 0
        status = run_git(root, ["status", "--porcelain", "--", relative])
    except (OSError, subprocess.SubprocessError):
        return {"tracked": None, "dirty": None}
    return {
        "tracked": tracked,
        "dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
    }


def newest_mtime(root: Path) -> float:
    newest = 0.0
    for item in root.rglob("*"):
        if not item.is_file() or is_excluded(item, root):
            continue
        assert_no_reparse(item, label="non-Git activity evidence")
        newest = max(newest, item.stat().st_mtime)
    return newest


def selected_owner(candidate: Path, selected_roots: list[Path]) -> Path | None:
    owners: list[Path] = []
    for root in selected_roots:
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        owners.append(root)
    if not owners:
        return None
    return max(owners, key=lambda root: len(root.parts))


def build_inventory(
    development_root: str | Path,
    cutoff: str | datetime.datetime,
    *,
    global_paths: list[str | Path] | None = None,
    root_relatives: list[str] | None = None,
    non_git_roots: set[str] | None = None,
) -> dict[str, Any]:
    development = assert_no_reparse(development_root, label="development root")
    if not development.is_dir():
        raise ToolchainError(f"development root does not exist: {development}")
    parsed_cutoff = parse_cutoff(cutoff) if isinstance(cutoff, str) else cutoff
    if parsed_cutoff.tzinfo is None:
        raise ToolchainError("cutoff must include a UTC offset")
    relative_roots = root_relatives or list(FROZEN_ROOTS)
    allowed_non_git = {item.casefold() for item in (non_git_roots or {"chief-of-staff"})}
    selected_roots = [development / Path(relative) for relative in relative_roots if (development / Path(relative)).is_dir()]
    root_rows: list[dict[str, Any]] = []
    root_by_path: dict[Path, dict[str, Any]] = {}
    for relative in relative_roots:
        root = development / Path(relative)
        if not root.is_dir():
            root_rows.append({
                "path": str(canonical(root)),
                "relative_root": Path(relative).as_posix(),
                "kind": "missing",
                "qualifies": False,
                "reason": "root does not exist",
            })
            continue
        root = assert_no_reparse(root, label="inventory root")
        git_state = git_root_state(root, parsed_cutoff)
        if git_state is None:
            latest_mtime = newest_mtime(root)
            state: dict[str, Any] = {
                "path": str(root),
                "relative_root": root.relative_to(development).as_posix(),
                "kind": "non-git",
                "qualifies": root.name.casefold() in allowed_non_git and latest_mtime >= parsed_cutoff.timestamp(),
                "activity_mtime_utc": datetime.datetime.fromtimestamp(latest_mtime, tz=datetime.timezone.utc).isoformat() if latest_mtime else None,
                "dirty": None,
            }
        else:
            state = {
                "path": str(root),
                "relative_root": root.relative_to(development).as_posix(),
                **git_state,
            }
        root_rows.append(state)
        root_by_path[root] = state

    targets: list[dict[str, Any]] = []
    if global_paths is None:
        global_paths = [
            r"C:\Users\DaveWitkin\.codex\AGENTS.md",
            r"C:\Users\DaveWitkin\.config\opencode\AGENTS.md",
        ]
    for global_path in global_paths:
        record = file_record(global_path)
        record.update({"scope": "global", "root": None, "relative_path": None, "tracked": None, "dirty": None, "mirror_group": None})
        targets.append(record)

    for root in selected_roots:
        root = canonical(root)
        state = root_by_path[root]
        if not state["qualifies"]:
            continue
        for candidate in sorted(root.rglob("AGENTS.md")):
            if selected_owner(candidate, selected_roots) != root or is_excluded(candidate, root):
                continue
            candidate = assert_no_reparse(candidate, label="inventory target")
            record = file_record(candidate)
            record.update({
                "scope": "local",
                "root": str(root),
                "relative_path": candidate.relative_to(root).as_posix(),
                "mirror_group": None,
            })
            if state["kind"] == "git":
                record.update(git_file_state(root, candidate))
            else:
                record.update({"tracked": None, "dirty": None})
            targets.append(record)

    mirror_groups: list[dict[str, Any]] = []
    by_hash: dict[str, list[dict[str, Any]]] = {}
    for target in targets:
        if target["scope"] == "local":
            by_hash.setdefault(target["sha256"], []).append(target)
    for number, digest in enumerate(sorted(by_hash), start=1):
        members = by_hash[digest]
        if len(members) < 2:
            continue
        group_id = f"mirror-{number:03d}"
        for member in members:
            member["mirror_group"] = group_id
        mirror_groups.append({"id": group_id, "sha256": digest, "paths": [member["path"] for member in members]})

    counts = {
        "global": sum(1 for target in targets if target["scope"] == "global"),
        "local": sum(1 for target in targets if target["scope"] == "local"),
        "roots": sum(1 for root in root_rows if root.get("qualifies")),
    }
    return {
        "version": 1,
        "cutoff": parsed_cutoff.isoformat(),
        "development_root": str(development),
        "roots": root_rows,
        "targets": targets,
        "mirror_groups": mirror_groups,
        "exclusions": {
            "directory_names": sorted(DIRECT_EXCLUSIONS),
            "path_prefixes": ["backup", "archive"],
            "conductor_backup_descendants": True,
        },
        "counts": counts,
    }


def make_git_commit(root: Path, relative: str, content: str, timestamp: str) -> None:
    subprocess.run(["git", "init", str(root)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    (root / relative).parent.mkdir(parents=True, exist_ok=True)
    (root / relative).write_text(content, encoding="utf-8")
    environment = os.environ.copy()
    environment.update({"GIT_AUTHOR_DATE": timestamp, "GIT_COMMITTER_DATE": timestamp})
    subprocess.run(["git", "-C", str(root), "add", relative], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=environment)
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "fixture"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=environment,
    )


def self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="inventory-agents-self-test-") as temporary:
        development = Path(temporary) / "development"
        active = development / "active-git"
        stale = development / "stale-git"
        non_git = development / "chief-of-staff"
        make_git_commit(active, "AGENTS.md", "dirty guidance\n", "2026-07-10T12:00:00-04:00")
        (active / "AGENTS.md").write_text("dirty guidance changed\n", encoding="utf-8")
        (active / "nested").mkdir(parents=True)
        (active / "nested" / "AGENTS.md").write_text("mirror guidance\n", encoding="utf-8")
        (active / "node_modules").mkdir()
        (active / "node_modules" / "AGENTS.md").write_text("excluded\n", encoding="utf-8")
        make_git_commit(stale, "AGENTS.md", "stale\n", "2020-01-01T12:00:00-05:00")
        non_git.mkdir(parents=True)
        (non_git / "AGENTS.md").write_text("mirror guidance\n", encoding="utf-8")
        recent = datetime.datetime(2026, 7, 10, tzinfo=datetime.timezone.utc).timestamp()
        os.utime(non_git / "AGENTS.md", (recent, recent))
        inventory = build_inventory(
            development,
            "2026-03-28T00:00:00-04:00",
            global_paths=[],
            root_relatives=["active-git", "stale-git", "chief-of-staff"],
            non_git_roots={"chief-of-staff"},
        )
        local_paths = {Path(target["path"]).relative_to(development).as_posix() for target in inventory["targets"] if target["scope"] == "local"}
        if inventory["counts"] != {"global": 0, "local": 3, "roots": 2}:
            raise ToolchainError(f"fixture inventory count mismatch: {inventory['counts']}")
        if "active-git/node_modules/AGENTS.md" in local_paths or "stale-git/AGENTS.md" in local_paths:
            raise ToolchainError("exclusion or cutoff guard failed")
        dirty = next(target for target in inventory["targets"] if target["scope"] == "local" and target["relative_path"] == "AGENTS.md" and "active-git" in target["root"])
        if dirty["dirty"] is not True or dirty["tracked"] is not True:
            raise ToolchainError("dirty/tracked evidence guard failed")
        if len(inventory["mirror_groups"]) != 1 or len(inventory["mirror_groups"][0]["paths"]) != 2:
            raise ToolchainError("mirror grouping guard failed")
    return {"check": "inventory-self-test", "status": "PASS", "live_targets_touched": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a read-only frozen AGENTS.md scope inventory.")
    parser.add_argument("--development-root")
    parser.add_argument("--cutoff")
    parser.add_argument("--output")
    parser.add_argument("--global", dest="global_paths", action="append", default=None, help="optional global target; repeatable")
    parser.add_argument("--root", dest="roots", action="append", default=None, help="relative local root; repeatable")
    parser.add_argument("--non-git-root", dest="non_git_roots", action="append", default=None, help="active non-Git root name; repeatable")
    parser.add_argument("--self-test", action="store_true", help="run only disposable inventory fixtures")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            print(json_line(self_test()))
            return 0
        if not args.development_root or not args.cutoff or not args.output:
            raise ToolchainError("--development-root, --cutoff, and --output are required unless --self-test is used")
        if Path(args.output).name.casefold() == "agents.md":
            raise ToolchainError("inventory output cannot be an AGENTS.md target")
        inventory = build_inventory(
            args.development_root,
            args.cutoff,
            global_paths=args.global_paths,
            root_relatives=args.roots,
            non_git_roots=set(args.non_git_roots or {"chief-of-staff"}),
        )
        write_json(args.output, inventory)
        print(json_line({"check": "inventory", "status": "PASS", **inventory["counts"]}))
        return 0
    except (ToolchainError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json_line({"check": "inventory", "status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
