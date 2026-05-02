#!/usr/bin/env python3
"""
Maintain huashu-design skill links across OpenCode/Codex/Antigravity.

Why this exists:
- Keep one canonical source folder
- Expose it to each app via Windows junctions
- Avoid self-referencing junction mistakes
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


HOME = Path.home()
CANONICAL = HOME / ".local" / "skills" / "huashu-design"
SKILL_MD = "SKILL.md"
REPO_URL = "https://github.com/alchaincyf/huashu-design.git"

TARGETS = {
    "opencode": HOME / ".config" / "opencode" / "skills" / "huashu-design",
    "antigravity": HOME / ".gemini" / "antigravity" / "skills" / "huashu-design",
    "codex": HOME / ".codex" / "skills" / "huashu-design",
    "codex-docs-path": HOME / ".agents" / "skills" / "huashu-design",
}


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)


def has_skill_md(path: Path) -> bool:
    return (path / SKILL_MD).exists()


def remove_path(path: Path) -> None:
    if not path.exists():
        return

    # Try plain rmdir first (safe for junctions).
    r1 = run(["cmd", "/c", "rmdir", str(path)])
    if not path.exists():
        return

    # Fallback for non-empty real directories.
    r2 = run(["cmd", "/c", "rmdir", "/s", "/q", str(path)])
    if path.exists():
        raise RuntimeError(
            f"Failed removing path: {path}\n"
            f"rmdir: {r1.stderr or r1.stdout}\n"
            f"rmdir /s /q: {r2.stderr or r2.stdout}"
        )


def ensure_canonical(seed_if_missing: bool, pull: bool) -> None:
    CANONICAL.parent.mkdir(parents=True, exist_ok=True)

    if not CANONICAL.exists():
        if not seed_if_missing:
            raise RuntimeError(
                f"Canonical skill path missing: {CANONICAL}\n"
                "Re-run with --seed-if-missing to clone it."
            )
        cp = run(["git", "clone", REPO_URL, str(CANONICAL)])
        if cp.returncode != 0:
            raise RuntimeError(f"git clone failed: {cp.stderr or cp.stdout}")

    if not has_skill_md(CANONICAL):
        raise RuntimeError(f"{CANONICAL} is present but missing {SKILL_MD}")

    if pull:
        git_dir = CANONICAL / ".git"
        if git_dir.exists():
            cp = run(["git", "-C", str(CANONICAL), "pull", "--ff-only"])
            if cp.returncode != 0:
                raise RuntimeError(f"git pull failed: {cp.stderr or cp.stdout}")
        else:
            print(f"[warn] No .git at canonical path, skipping pull: {CANONICAL}")


def create_junction(target: Path, source: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    cp = run(["cmd", "/c", "mklink", "/j", str(target), str(source)])
    if cp.returncode != 0:
        raise RuntimeError(f"mklink failed for {target}: {cp.stderr or cp.stdout}")


def repair_links() -> None:
    for name, target in TARGETS.items():
        if target == CANONICAL:
            raise RuntimeError(f"Refusing self-link target for {name}: {target}")

        remove_path(target)
        create_junction(target, CANONICAL)


def check() -> int:
    ok = True

    canonical_ok = CANONICAL.exists() and has_skill_md(CANONICAL)
    print(f"canonical: {CANONICAL} | SKILL={canonical_ok}")
    if not canonical_ok:
        ok = False

    for name, target in TARGETS.items():
        skill_ok = has_skill_md(target)
        print(f"{name:15} {target} | SKILL={skill_ok}")
        if not skill_ok:
            ok = False

    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync huashu-design skill links")
    parser.add_argument("--check", action="store_true", help="Validate canonical + links")
    parser.add_argument("--repair-links", action="store_true", help="Recreate all junctions")
    parser.add_argument(
        "--seed-if-missing",
        action="store_true",
        help="Clone huashu-design to canonical path if missing",
    )
    parser.add_argument(
        "--pull",
        action="store_true",
        help="git pull in canonical path (if .git exists)",
    )
    args = parser.parse_args()

    if not any([args.check, args.repair_links, args.seed_if_missing, args.pull]):
        parser.print_help()
        return 0

    try:
        ensure_canonical(seed_if_missing=args.seed_if_missing, pull=args.pull)
        if args.repair_links:
            repair_links()
        if args.check:
            return check()
        return 0
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
