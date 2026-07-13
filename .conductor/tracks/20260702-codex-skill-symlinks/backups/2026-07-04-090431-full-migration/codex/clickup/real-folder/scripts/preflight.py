"""ClickUp skill preflight check.

Goals:
- Fail fast if ClickUp auth is not usable (missing/placeholder token).
- Verify external repo discovery + imports work.

Notes:
- Never print tokens.
"""

import os
import sys
import importlib

# Ensure local skill scripts are importable when run directly.
_SCRIPT_DIR = os.path.dirname(__file__)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

def _is_placeholder_token(token):
    if not token:
        return False
    t = token.strip().lower()
    return t in {"your_token", "<your_token>", "changeme"}


def main() -> int:
    # Capture the raw env var before any dotenv loading.
    raw_env_token = os.environ.get("CLICKUP_API_TOKEN")
    if _is_placeholder_token(raw_env_token):
        print("[WARN] CLICKUP_API_TOKEN is set to a placeholder value in the environment (e.g. 'your_token').")
        print("       The ClickUp scripts will try to load a real token from .env files.")
        # python-dotenv won't override an existing env var by default.
        # Remove placeholder values so .env loading can populate a real token.
        os.environ.pop("CLICKUP_API_TOKEN", None)

    # Ensure external repo is discoverable and on sys.path.
    try:
        common = importlib.import_module("common")
        repo_path = common.setup_path()
        print(f"[OK] External repo found: {repo_path}")
    except Exception as e:
        print("[ERROR] External cursor-clickup-mcp repository not available.")
        print(f"        {e}")
        return 1

    # Import client (loads dotenv), then attempt init.
    try:
        clickup_client = importlib.import_module("clickup_client")
        client = clickup_client.ClickUpClient()
        # Double-check placeholder even if init succeeds (defensive).
        if _is_placeholder_token(getattr(client, "api_token", None)):
            raise ValueError("Resolved CLICKUP_API_TOKEN is a placeholder")
        print("[OK] ClickUp client initialized")
    except Exception as e:
        print("[ERROR] ClickUp client failed to initialize")
        msg = str(e)
        if "CLICKUP_API_TOKEN" in msg or "token" in msg.lower() or "placeholder" in msg.lower():
            print("        Fix: ensure a real token is available via one of:")
            print("          - C:/development/.env.mcp")
            if 'repo_path' in locals() and repo_path:
                print(f"          - {repo_path}/.env")
            else:
                print("          - <external repo>/.env")
            print("        And remove placeholder env overrides if present.")
        else:
            print(f"        {e}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
