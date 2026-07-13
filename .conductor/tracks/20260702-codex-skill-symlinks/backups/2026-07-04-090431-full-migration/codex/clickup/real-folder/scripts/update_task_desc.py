"""Compatibility wrapper for updating ClickUp task descriptions.

This script intentionally contains no embedded credentials.

Usage examples:
- python scripts/update_task_desc.py <task_id> --description "..."
- python scripts/update_task_desc.py <task_id> --status done --description "..."

Implementation note:
- Delegates to the canonical update CLI in the external `cursor-clickup-mcp` repo.
"""

import sys

# Add current directory to path so we can import common
sys.path.append(sys.path[0])

from common import setup_path


def _normalize_status_args(argv):
    out = list(argv)
    for i, v in enumerate(out):
        if v == "--status" and i + 1 < len(out):
            sv = (out[i + 1] or "").strip().lower()
            if sv in {"complete", "completed"}:
                out[i + 1] = "done"
    return out


setup_path()
sys.argv = _normalize_status_args(sys.argv)

try:
    from update_task_cli import update_task_cli
except ImportError as e:
    print(f"Error importing from repository: {e}")
    raise SystemExit(1)


if __name__ == "__main__":
    update_task_cli()
