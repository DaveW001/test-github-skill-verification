"""Find a ClickUp task URL by name within a list.

This script intentionally contains no embedded credentials.

Examples:
  python scripts/find_task_url.py --list-id 3984798 --name "Fix OpenCode Permission Config"
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

import requests

# Add current directory to path so we can import common
sys.path.append(sys.path[0])

from common import setup_path


def _get_api_token() -> str:
    setup_path()
    try:
        from clickup_client import ClickUpClient
    except Exception as e:
        raise SystemExit(f"Error importing ClickUp client: {e}")

    client = ClickUpClient()
    token = getattr(client, "api_token", None)
    if not token or not str(token).strip():
        raise SystemExit("Missing CLICKUP_API_TOKEN (check C:/development/.env.mcp or cursor-clickup-mcp/.env)")
    return str(token)


def find_task_url(list_id: str, name: str) -> Optional[str]:
    token = _get_api_token()
    base = "https://api.clickup.com/api/v2"
    headers = {"Authorization": token}

    url = f"{base}/list/{list_id}/task"
    page = 0
    while True:
        resp = requests.get(url, headers=headers, params={"page": page}, timeout=30)
        if resp.status_code == 401:
            raise SystemExit("401 Unauthorized (token invalid or overridden by shell env var)")
        resp.raise_for_status()
        data = resp.json() or {}
        tasks = data.get("tasks") or []

        for t in tasks:
            if (t.get("name") or "") == name:
                return t.get("url")

        # ClickUp returns an empty list when pagination ends.
        if not tasks:
            return None
        page += 1


def main() -> int:
    p = argparse.ArgumentParser(description="Find ClickUp task URL by name in a list")
    p.add_argument("--list-id", default="3984798", help="ClickUp list ID (default: 3984798)")
    p.add_argument("--name", required=True, help="Exact task name to match")
    args = p.parse_args()

    found = find_task_url(args.list_id, args.name)
    if not found:
        print("Task not found")
        return 2
    print(found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
