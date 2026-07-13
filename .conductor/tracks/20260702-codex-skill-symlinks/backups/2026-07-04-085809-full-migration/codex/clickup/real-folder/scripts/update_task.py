import sys

# Add current directory to path so we can import common
sys.path.append(sys.path[0])

from common import setup_path


def _normalize_status_args(argv):
    """Normalize common status aliases to avoid 400 errors.

    ClickUp statuses vary by space; in this workspace, tasks commonly use "done".
    """
    out = list(argv)
    for i, v in enumerate(out):
        if v == "--status" and i + 1 < len(out):
            sv = (out[i + 1] or "").strip().lower()
            if sv in {"complete", "completed"}:
                out[i + 1] = "done"
    return out


# Ensure external repo is discoverable and placeholder env vars are sanitized.
setup_path()

# Normalize status arguments before delegating to external CLI.
sys.argv = _normalize_status_args(sys.argv)

try:
    from update_task_cli import update_task_cli
except ImportError as e:
    print(f"Error importing from repository: {e}")
    sys.exit(1)

if __name__ == "__main__":
    update_task_cli()
